#!/bin/python3
import argparse
import json

import requests

# manuals:
# https://redirect.pizza/docs
# https://redirect.pizza/api/v1


# REQUEST_URL = "https://duckdns.org/update/{domain}/{token}[/{ip_addr}]"

def build_header(token: str) -> dict[str, str]:
    request_headers = {
        'Authorization': F'Bearer {token}',
        'Content-Type': 'application/json',
    }
    return request_headers


def list_redirects(token: str, entries: int = 100) -> bool:
    request_url = F'https://redirect.pizza/api/v1/redirects?page=1&per_page={entries}'
    response = requests.get(request_url, headers=build_header(token))
    return_code = response.status_code
    if return_code == 200:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(json.dumps(response, indent=2), end='\n\n')
        return True

    print(F'ERROR CODE: {response.status_code}')
    print(response.text)
    return False


def create_redirect(
    token: str, src_url: str,
    dest_url: str, notes: str = '', tag: str = '',
) -> tuple[bool, int | None]:
    request_url = 'https://redirect.pizza/api/v1/redirects'
    data = F"""{{
        "sources": [
            "{src_url}"
        ],
        "destination": "{dest_url}",
        "redirect_type": "temporary",
        "uri_forwarding": true,
        "keep_query_string": true,
        "tracking": true,
        "tags": [
            "{tag}"
        ],
        "notes": "{notes}",
        "merge": true
    }}"""
    # data = data.format(src_url=src_url, dest_url=dest_url, notes=notes, tag=tag)
    # print(data)
    response = requests.post(request_url, headers=build_header(token), data=data)
    return_code = response.status_code
    return_pizza_id = None
    if return_code == 201:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(json.dumps(response, indent=2), end='\n\n')
            return_pizza_id = response['data']['id']
            print(F'created redirect with id: {return_pizza_id}')
            return (True, return_pizza_id)
    else:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(F'ERROR CODE: {return_code}')
            print(json.dumps(response, indent=2), end='\n\n')
            return_pizza_id = response['errors']['redirect_id'][0]

    return (False, return_pizza_id)


def update_redirect(
    token: str, pizza_id: int, src_url: str,
    dest_url: str, notes: str = '', tag: str = '',
) -> bool:
    request_url = F'https://redirect.pizza/api/v1/redirects/{pizza_id}'
    data = """{{
        "sources": [
            "{src_url}"
        ],
        "destination": "{dest_url}",
        "redirect_type": "temporary",
        "uri_forwarding": true,
        "keep_query_string": true,
        "tracking": true,
        "tags": [
            "{tag}"
        ],
        "notes": "{notes}"
    }}"""
    data = data.format(src_url=src_url, dest_url=dest_url, notes=notes, tag=tag)
    response = requests.put(request_url, headers=build_header(token), data=data)
    return_code = response.status_code
    if return_code == 200:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(json.dumps(response, indent=2), end='\n\n')
        return True

    print(F'ERROR CODE: {return_code}')
    print(response.text)
    return False


def delete_redirect(token: str, pizza_id: int) -> bool:
    request_url = F'https://redirect.pizza/api/v1/redirects/{pizza_id}'

    response = requests.delete(request_url, headers=build_header(token))
    return_code = response.status_code
    if return_code == 204:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(json.dumps(response, indent=2), end='\n\n')
        return True

    print(F'ERROR CODE: {return_code}')
    print(response.text)
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update pizza redirect')

    # parser.add_argument("--domain", type=str, help="Domain to change")
    # parser.add_argument("--ip", type=str, help="new ip to update domain")
    parser.add_argument('token', type=str, help='Bearer token for auth')
    parser.add_argument('-l', '--list', action='store_true', help='list redirects')
    parser.add_argument('-u', '--update', action='store_true', help='update a redirect')
    parser.add_argument('-c', '--create', action='store_true', help='create a redirect')
    parser.add_argument('-d', '--delete', action='store_true', help='delete a redirect')

    parser.add_argument('-i', '--id', type=str, help='redirect id to work with')
    parser.add_argument('--dest_url', type=str, help='destination url of redirect')
    parser.add_argument('--src_url', type=str, help='source url of redirect')
    parser.add_argument('--tag', default='', type=str, help='tag redirect')
    parser.add_argument('--notes', default='', type=str, help='notes of redirect')

    args = parser.parse_args()

    if args.list:
        list_redirects(args.token)
    elif args.update:
        update_redirect(
            args.token, args.id, args.src_url,
            args.dest_url, args.notes, args.tag,
        )
    elif args.create:
        create_redirect(args.token, args.src_url, args.dest_url, args.notes, args.tag)
    elif args.delete:
        delete_redirect(args.token, args.id)
