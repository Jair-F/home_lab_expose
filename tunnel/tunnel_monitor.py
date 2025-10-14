import io
import queue
import re
import subprocess
import threading
import time
from typing import Optional

import tunnel.redirect_pizza as pizza


class TunnelMonitor():
    _tunnel_command: list[str]
    _url_regex_match: str
    url: str | None
    url_changed: bool
    _redirect_domain: str
    _process: subprocess.Popen[str] | None
    _stderr_watch_thread: Optional[threading.Thread] | None
    _run: bool
    pizza_id: int | None
    _pizza_api_key: str
    _out_queue: queue.Queue[str]

    def __init__(
        self, tunnel_command: list[str], url_regex_match: str,
        redirect_domain: str, pizza_api_key: str,
    ):
        self._tunnel_command = tunnel_command
        self._url_regex_match = url_regex_match
        self.url = None
        self.url_changed = False
        self._redirect_domain = redirect_domain
        self._process = None
        self._stderr_watch_thread = None
        self._run = True
        self.pizza_id = None
        self._pizza_api_key = pizza_api_key
        self._out_queue = queue.Queue()

    def _watch_stderr(self, pipe: io.TextIOWrapper, q: queue.Queue[str]) -> None:
        print('stderr watch started')
        for line in iter(pipe.readline, ''):
            q.put(line)
        pipe.close()
        print('stderr watch ended')

    def _start(self) -> None:
        self._process = subprocess.Popen(
            args=self._tunnel_command,
            stderr=subprocess.PIPE,  # stdout=subprocess.PIPE, stdin=subprocess.PIPE,
            text=True,
        )
        self._stderr_watch_thread = threading.Thread(
            target=TunnelMonitor._watch_stderr, args=(
                self, self._process.stderr, self._out_queue,
            ), daemon=True,
        )
        self._stderr_watch_thread.start()
        self._run = True
        print(F'TUNNEL {self._redirect_domain}: started')

    def process_is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    def _stop(self) -> None:
        if self._process is not None:
            self._process.terminate()
            returncode = self._process.wait(timeout=2)
            self._process.kill()
            print(
                F'TUNNEL {self._redirect_domain}: ',
                F'process terminated with returncode: {returncode}',
            )

        if self._stderr_watch_thread is not None:
            self._stderr_watch_thread.join()

        self._out_queue.empty()
        self._process = None
        self._stderr_watch_thread = None
        self._run = False
        print(F'TUNNEL {self._redirect_domain}: stopped')

    def _restart(self) -> None:
        print(F'TUNNEL {self._redirect_domain}: restarting')
        self._stop()
        self._start()

    def _read_stderr(self) -> str | None:
        line = None
        try:
            line = self._out_queue.get_nowait()
        except queue.Empty:
            line = None
        return line

    def _handle_stderr(self, output: str) -> None:
        # print(F"got output: {output}")
        match = re.search(self._url_regex_match, output)
        if match is not None:
            found_url = match.group()
            if found_url != self.url:
                self.url = found_url
                self.url_changed = True
                print(F'TUNNEL {self._redirect_domain}: found new url: {self.url}')

    def _get_url(self) -> str | None:
        self.url_changed = False
        return self.url

    def _change_url(self, new_url: str) -> None:
        if self.pizza_id is None:
            success = False
            while not success:
                (success, pizza_id) = pizza.create_redirect(
                    self._pizza_api_key,
                    self._redirect_domain, new_url, notes='home_lab_expose',
                )
                if not success:
                    print(F'trying to delete remaining redirect with id: {pizza_id}')
                    pizza.delete_redirect(self._pizza_api_key, pizza_id)
                time.sleep(0.5)
            self.pizza_id = pizza_id
        else:
            while not pizza.update_redirect(
                self._pizza_api_key, self.pizza_id,
                self._redirect_domain, new_url, notes='home_lab_expose',
            ):
                time.sleep(1)

    def run_blocking(self) -> None:
        self._start()

        try:
            while self._run:
                if not self.process_is_running():
                    print(F'TUNNEL {self._redirect_domain}: not running - restarting')
                    self._restart()

                output = self._read_stderr()
                if output is not None:
                    self._handle_stderr(output)

                if self.url_changed:
                    print(
                        F'TUNNEL {self._redirect_domain}: ',
                        'updating redirect to new url: ', end='',
                    )
                    self._change_url(self._get_url())

                time.sleep(1)
        finally:
            self._stop()

    def shutdown(self) -> None:
        """
            delete all redirect urls
            stop all threads.
        """
        print('shutting down...')
        if self.pizza_id is not None:
            print(F'TUNNEL {self._redirect_domain}: deleting pizza : {self.pizza_id}')
            if pizza.delete_redirect(self._pizza_api_key, self.pizza_id):
                print(F'TUNNEL {self._redirect_domain}: success deleting pizza: {self.pizza_id}')
            self.pizza_id = None
        self._stop()
        print('byyye...')
