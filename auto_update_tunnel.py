#!/bin/python3
import signal
import threading
import time

import box
import yaml

import tunnel.tunnelMonitor as tunnelM

CONFIG = None

REGEX_MATCH_URL = 'https://[0-9a-zA-Z-]*.trycloudflare.com'
TUNNEL_COMMANDS = []
DUCKDNS_SUBDOMAINS = []
RUNNING = True


def read_config():
    global CONFIG, TUNNEL_COMMANDS
    with open('config/config.yaml', encoding='utf-8') as file:
        CONFIG = box.Box(yaml.safe_load(file))
        # print(json.dumps(CONFIG, indent=2))
        # print(CONFIG.sites)
        for site in iter(CONFIG.sites):
            site = CONFIG['sites'][site]
            TUNNEL_COMMANDS.append([
                'cloudflared', 'tunnel', '--no-tls-verify',
                '--url', F'{site.local_host}:{site.local_port}',
            ])
            DUCKDNS_SUBDOMAINS.append(site.duckdns_subdomain)
    # print(TUNNEL_COMMANDS)
    # print(DUCKDNS_SUBDOMAINS)


if __name__ == '__main__':
    read_config()
    tunnels = []
    tunnel_threads = []
    for i, command in enumerate(TUNNEL_COMMANDS, start=0):
        tunnels.append(
            tunnelM.TunnelMonitor(
                command, REGEX_MATCH_URL,
                DUCKDNS_SUBDOMAINS[i], CONFIG.pizza_api_key,
            ),
        )

    def shutdown_gracefully(signum, frame):
        global RUNNING
        for t in tunnels:
            t.shutdown()

        for t in tunnel_threads:
            t.join()
        RUNNING = False
    signal.signal(signal.SIGTERM, shutdown_gracefully)
    signal.signal(signal.SIGINT, shutdown_gracefully)

    def run_tunnel(t: tunnelM.TunnelMonitor):
        print('running tunnel blocking')
        t.run_blocking()
    for tunnel in tunnels:
        thread = threading.Thread(target=run_tunnel, args=[tunnel], daemon=True)
        thread.start()
        tunnel_threads.append(thread)

    print(F'duckdns_topdomain: {CONFIG.duckdns_topdomain}')
    while RUNNING:
        # monitor here the duckdns main domain.
        print(F'monitoring duckdns topdomain: {CONFIG.duckdns_topdomain}')
        time.sleep(10)
