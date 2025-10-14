#!/bin/python3
import signal
import threading
import time
import types

import box
import yaml

import tunnel.tunnel_monitor as tunnel_m
from consts import PIZZA_REDIRECT_DOMAIN
from consts import REGEX_MATCH_URL
from consts import VERSION
from tunnel.domain import update_noip_ip
from tunnel.resolve_dns import get_ip


CONFIG = None

TUNNEL_COMMANDS = []
REDIRECT_DOMAINS = []
RUNNING = True


def read_config() -> None:
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
            REDIRECT_DOMAINS.append(site.redirect_domain)


if __name__ == '__main__':
    print('-------------------------------------------------------')
    print(F'              home lab expose v{VERSION}              ')
    print('-------------------------------------------------------')

    read_config()
    tunnels: list[tunnel_m.TunnelMonitor] = []
    tunnel_threads: list[threading.Thread] = []
    for i, command in enumerate(TUNNEL_COMMANDS, start=0):
        tunnels.append(
            tunnel_m.TunnelMonitor(
                command, REGEX_MATCH_URL,
                REDIRECT_DOMAINS[i], CONFIG.pizza_api_key,
            ),
        )

    def shutdown_gracefully(signum: int, frame: types.FrameType | None) -> None:
        global RUNNING
        for t in tunnels:
            t.shutdown()

        for t in tunnel_threads:
            t.join()
        RUNNING = False
    signal.signal(signal.SIGTERM, shutdown_gracefully)
    signal.signal(signal.SIGINT, shutdown_gracefully)

    def run_tunnel(t: tunnel_m.TunnelMonitor) -> None:
        print('running tunnel blocking')
        t.run_blocking()
    for tunnel in tunnels:
        thread = threading.Thread(target=run_tunnel, args=[tunnel], daemon=True)
        thread.start()
        tunnel_threads.append(thread)

    CLOUDFLARE_TOPDOMAIN_IP = ''
    while RUNNING:
        current_ip = get_ip(PIZZA_REDIRECT_DOMAIN)

        if current_ip is not None and CLOUDFLARE_TOPDOMAIN_IP != current_ip:
            if update_noip_ip(
                CONFIG.noip_domain, CONFIG.noip_username,
                CONFIG.noip_password, current_ip,
            ):
                print(F'NOIP {CONFIG.noip_domain}: updated noip ip to {current_ip}')
                CLOUDFLARE_TOPDOMAIN_IP = current_ip
        time.sleep(10)
