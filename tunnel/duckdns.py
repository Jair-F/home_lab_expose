#!/bin/python3
import argparse
import sys

import requests


# manuals:
# https://www.duckdns.org/spec.jsp
# https://duckdns.org/update/{YOURDOMAIN}/{YOURTOKEN}[/{YOURIPADDRESS}]


REQUEST_URL = 'https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip_addr}'
NOIP_REQUEST_URL = \
    'http://{username}:{password}@dynupdate.no-ip.com/nic/update?hostname={domain}&myip={ip_addr}'
NOIP_REQUEST_URL_FILLED = \
    'http://jaj05798:6qPH0A_THcWSfTZJ@dynupdate.no-ip.com/nic/update?hostname={domain}&myip={ip_addr}'


def update_duckdns_ip(domain: str, auth_token: str, new_ip: str) -> bool:
    filled_url = REQUEST_URL.format(domain=domain, token=auth_token, ip_addr=new_ip)
    print(filled_url)
    response = requests.get(filled_url)

    # noip
    filled_url = NOIP_REQUEST_URL_FILLED.format(domain=domain, ip_addr=new_ip)
    response = requests.get(filled_url)
    print(F'noip: {filled_url}')
    print(F'noip: {response}')

    try:
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        if response.text == 'OK':
            return True
    except requests.exceptions.RequestException as e:
        print(f'error http status code: {e}')

    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update duckdns.org ip for domain')

    parser.add_argument('domain', type=str, help='Domain to change')
    parser.add_argument('ip', type=str, help='new ip to update domain')
    parser.add_argument('token', type=str, help='token for auth')

    args = parser.parse_args()
    SUCCESS = update_duckdns_ip(args.domain, args.token, args.ip)
    if not SUCCESS:
        print('failed to update domain')
        sys.exit(1)
