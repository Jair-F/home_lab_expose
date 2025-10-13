#!/bin/python3
import argparse
import sys

import requests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor if site is up.')

    parser.add_argument('--url', required=True, type=str, help='URL to check')

    args = parser.parse_args()
    try:
        response = requests.get(args.url)
        if response.status_code == 200:
            print('site is up')
            sys.exit(0)
    except requests.exceptions.RequestException:
        pass

    print('site is down')
    sys.exit(1)
