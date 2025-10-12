#!/bin/python3
import argparse
import sys

import requests

"""
https://www.duckdns.org/spec.jsp
https://duckdns.org/update/{YOURDOMAIN}/{YOURTOKEN}[/{YOURIPADDRESS}]
"""

REQUEST_URL = 'https://duckdns.org/update/{domain}/{token}[/{ip_addr}]'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update duckdns.org ip for domain')

    parser.add_argument('domain', type=str, help='Domain to change')
    parser.add_argument('ip', type=str, help='new ip to update domain')
    parser.add_argument('token', type=str, help='token for auth')

    args = parser.parse_args()
    filled_url = REQUEST_URL.format(domain=args.domain, token=args.token, ip_addr=args.ip)

    response = requests.get(filled_url)

    try:
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        if response.text == 'OK':
            sys.exit(0)
        elif response.text == 'KO':  # OK is good
            print('failed to update domain')
            sys.exit(-1)
        else:
            print('unknown error - faild to update domain')
            sys.exit(3)

    except requests.exceptions.RequestException as e:
        print(f'error http status code: {e}')
        sys.exit(-2)
