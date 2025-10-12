#!/bin/python3
import queue
import re
import subprocess
import threading
import time

import box
import yaml

import tools.update_pizza_redirect as pizza

CONFIG = None

REGEX_MATCH_URL = 'https://[0-9a-zA-Z-]*.trycloudflare.com'
TUNNEL_COMMAND = None


def read_config():
    global CONFIG, TUNNEL_COMMAND
    with open('config/config.yaml') as file:
        CONFIG = box.Box(yaml.safe_load(file))
        TUNNEL_COMMAND = ['cloudflared', 'tunnel', '--url', F'{CONFIG.local_host}:{CONFIG.local_port}']


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
            found_url = match.group()
            if found_url != self.url:
                self.url = found_url
                self.url_changed = True
                print(F'found new url: {self.url}')

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
                    print('updateing redirect: ', end='')
                    new_url = self.get_url()
                    while not pizza.update_redirect(CONFIG.pizza_api_key, 1572326897, 'laern.duckdns.org', new_url):
                        time.sleep(1)

                time.sleep(1)
        finally:
            self._stop()
            print(F'process terminated with returncode: {self._process.returncode}')


if __name__ == '__main__':
    read_config()
    tunnel = TunnelMonitor(TUNNEL_COMMAND, REGEX_MATCH_URL)

    tunnel.runBlocking()
