#!/bin/python3
import queue
import re
import signal
import subprocess
import threading
import time
from typing import IO

import box
import yaml

import tools.update_pizza_redirect as pizza

CONFIG = None

REGEX_MATCH_URL = 'https://[0-9a-zA-Z-]*.trycloudflare.com'
TUNNEL_COMMAND = None


def read_config():
    global CONFIG, TUNNEL_COMMAND
    with open('config/config.yaml', encoding='utf-8') as file:
        CONFIG = box.Box(yaml.safe_load(file))
        TUNNEL_COMMAND = \
            ['cloudflared', 'tunnel', '--url', F'{CONFIG.local_host}:{CONFIG.local_port}']


class TunnelMonitor():
    def __init__(self, tunnel_command, url_regex_match):
        self._tunnel_command = tunnel_command
        self._url_regex_match = url_regex_match
        self.url = None
        self.url_changed = False
        self._process = None
        self._stderr_watch_thread = None
        self._run = True
        self.pizza_id = None
        self._out_queue = queue.Queue()

    def _watch_stderr(pipe: IO[str], queue: queue) -> None:
        print('stderr watch started')
        for line in iter(pipe.readline, ''):
            queue.put(line)
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
                self._process.stderr, self._out_queue,
            ), daemon=True,
        )
        self._stderr_watch_thread.start()
        self._run = True
        print('started tunnel')

    def process_is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    def _stop(self) -> None:
        if self._process is not None:
            self._process.terminate()
            returncode = self._process.wait(timeout=2)
            self._process.kill()
            print(F'process terminated with returncode: {returncode}')

        if self._stderr_watch_thread is not None:
            self._stderr_watch_thread.join()

        self._out_queue.empty()
        self._process = None
        self._stderr_watch_thread = None
        self._run = False
        print('stopped tunnel')

    def _restart(self) -> None:
        print('restarting tunnel')
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
                print(F'found new url: {self.url}')

    def _get_url(self) -> str:
        self.url_changed = False
        return self.url

    def _change_url(self, new_url):
        if self.pizza_id is None:
            success = False
            while not success:
                (success, pizza_id) = pizza.create_redirect(
                    CONFIG.pizza_api_key,
                    CONFIG.duckdns_domain, new_url, notes='home_lab_expose',
                )
                if not success:
                    print(F'trying to delete remaining redirect with id: {pizza_id}')
                    pizza.delete_redirect(CONFIG.pizza_api_key, pizza_id)
                time.sleep(0.5)
            self.pizza_id = pizza_id
        else:
            while not pizza.update_redirect(
                CONFIG.pizza_api_key, self.pizza_id,
                CONFIG.duckdns_domain, new_url, notes='home_lab_expose',
            ):
                time.sleep(1)

    def run_blocking(self):
        self._start()

        try:
            while self._run:
                if not self.process_is_running():
                    print('not running - restarting')
                    self._restart()

                output = self._read_stderr()
                if output is not None:
                    self._handle_stderr(output)

                if self.url_changed:
                    print('updateing redirect to new url: ', end='')
                    self._change_url(self._get_url())

                time.sleep(1)
        finally:
            self._stop()

    def shutdown(self):
        """
            delete all redirect urls
            stop all threads.
        """
        print('shutting down...')
        if self.pizza_id is not None:
            print(F'deleting pizza : {self.pizza_id}')
            if pizza.delete_redirect(CONFIG.pizza_api_key, self.pizza_id):
                print(F'success deleting pizza: {self.pizza_id}')
            self.pizza_id = None
        self._stop()
        print('byyye...')


if __name__ == '__main__':
    read_config()
    tunnel = TunnelMonitor(TUNNEL_COMMAND, REGEX_MATCH_URL)

    def shutdown_gracefully(signum, frame):
        tunnel.shutdown()

    signal.signal(signal.SIGTERM, shutdown_gracefully)
    signal.signal(signal.SIGINT, shutdown_gracefully)

    tunnel.run_blocking()
