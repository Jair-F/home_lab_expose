#!/bin/python3
import queue
import re
import subprocess
import threading
import time

import tools.update_pizza_redirect as pizza

HOST_URL = 'localhost'
PORT = '80'

regex_match_url = 'https://[0-9a-zA-Z-]*.trycloudflare.com'
tunnel_command = ['cloudflared', 'tunnel', '--url', F'{HOST_URL}:{PORT}']


class TunnelMonitor():
    def __init__(self, tunnel_command, url_regex_match):
        self._tunnel_command = tunnel_command
        self._url_regex_match = url_regex_match
        self.url = None
        self.url_changed = False
        self._process = None
        self._stderr_watch_thread = None
        self._run = True
        self._out_queue = queue.Queue()

    def _watch_stderr(pipe, queue) -> None:
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

    def processIsRunning(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    def _stop(self) -> None:
        if self._process is not None:
            self._process.terminate()
            self._process.wait(timeout=2)
            self._process.kill()

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
            self.url = match.group()
            self.url_changed = True
            print(F'found url: {self.url}')

    def get_url(self) -> str:
        self.url_changed = False
        return self.url

    def runBlocking(self):
        self._start()

        try:
            while self._run:
                if not self.processIsRunning():
                    print('not running - restarting')
                    self._restart()

                output = self._read_stderr()
                if output is not None:
                    self._handle_stderr(output)

                if self.url_changed:
                    print('updateing redirect')
                    temp = self.get_url()
                    tk = 'rpa_dtylgrntvszoba9so5joeeyenut1gjkwcmfgk1wm2ilndagvm5huihf6h58ugxrl'
                    REQUEST_HEADERS = {
                        'Authorization': F'Bearer {tk}',
                        'Content-Type': 'application/json',
                    }
                    pizza.update_redirect(1572326897, REQUEST_HEADERS, 'laern.duckdns.org', temp)

                time.sleep(1)
        finally:
            self._stop()
            print(F'process terminated with returncode: {self._process.returncode}')


if __name__ == '__main__':
    tunnel = TunnelMonitor(tunnel_command, regex_match_url)

    tunnel.runBlocking()
