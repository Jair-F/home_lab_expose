#!/bin/python3
import requests
import argparse
import json
import sys

"""
https://redirect.pizza/docs
https://redirect.pizza/api/v1
"""

tk = "rpa_dtylgrntvszoba9so5joeeyenut1gjkwcmfgk1wm2ilndagvm5huihf6h58ugxrl"

# REQUEST_URL = "https://duckdns.org/update/{domain}/{token}[/{ip_addr}]"

def list_redirects(header, entries=100) -> int:
    REQUEST_URL = F"https://redirect.pizza/api/v1/redirects?page=1&per_page={entries}"
    response = requests.get(REQUEST_URL, headers=header)
    return_code = response.status_code
    if return_code == 200:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            pretty_response = json.dumps(response, indent=2)
            print(pretty_response)
    else:
        print(F"ERROR CODE: {response.status_code}")
        print(response.text)
    return return_code

def create_redirect(header, src_url, dest_url, notes="", tag="") -> int:
    REQUEST_URL = "https://redirect.pizza/api/v1/redirects"
    data = F"""{{
        "sources": [
            "{src_url}"
        ],
        "destination": "{dest_url}",
        "redirect_type": "permanent",
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
    response = requests.post(REQUEST_URL, headers=header, data=data)
    return_code = response.status_code
    created_pipe_id = None
    if return_code == 201:
        if 'application/json' in response.headers.get('Content-Type', ''):
            answer = response.json()
            pretty_response = json.dumps(answer, indent=2)
            print(pretty_response)
            created_pipe_id = answer["data"]['id']
            print(F"created redirect with id: {created_pipe_id}")
    else:
        print(F"ERROR CODE: {return_code}")
        print(response.text)
    
    return return_code, created_pipe_id

def update_redirect(header, id, src_url, dest_url, notes="", tag="") -> int:
    REQUEST_URL = F"https://redirect.pizza/api/v1/redirects/{id}"
    data = """{{
        "sources": [
            "{src_url}"
        ],
        "destination": "{dest_url}",
        "redirect_type": "permanent",
        "uri_forwarding": true,
        "keep_query_string": true,
        "tracking": true,
        "tags": [
            "{tag}"
        ],
        "notes": "{notes}"
    }}"""
    data = data.format(src_url=src_url, dest_url=dest_url, notes=notes, tag=tag)
    response = requests.put(REQUEST_URL, headers=header, data=data)
    return_code = response.status_code
    if return_code == 200:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(response)
    else:
        print(F"ERROR CODE: {return_code}")
        print(response.text)
    return return_code

def delete_redirect(header, id) -> int:
    REQUEST_URL = F"https://redirect.pizza/api/v1/redirects/{id}"
    
    response = requests.delete(REQUEST_URL, headers=header)
    return_code = response.status_code
    if return_code == 204:
        if 'application/json' in response.headers.get('Content-Type', ''):
            response = response.json()
            print(response)
    else:
        print(F"ERROR CODE: {return_code}")
        print(response.text)
    
    return return_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update pizza redirect")

    # parser.add_argument("--domain", type=str, help="Domain to change")
    # parser.add_argument("--ip", type=str, help="new ip to update domain")
    parser.add_argument("token", type=str, help="Bearer token for auth")
    parser.add_argument("-l", "--list", action='store_true', help="list redirects")
    parser.add_argument("-u", "--update", action='store_true', help="update a redirect")
    parser.add_argument("-c", "--create", action='store_true', help="create a redirect")
    parser.add_argument("-d", "--delete", action='store_true', help="delete a redirect")
    
    parser.add_argument("-i", "--id", type=str, help="redirect id to work with")
    parser.add_argument("--dest_url", type=str, help="destination url of redirect")
    parser.add_argument("--src_url", type=str, help="source url of redirect")
    parser.add_argument("--tag", default='', type=str, help="tag redirect")
    parser.add_argument("--notes", default='', type=str, help="notes of redirect")    

    args = parser.parse_args()

    REQUEST_HEADERS = {
        "Authorization": F"Bearer {args.token}",
        "Content-Type": "application/json"
    }
    if args.list:
        list_redirects(REQUEST_HEADERS)
    elif args.update:
        update_redirect(REQUEST_HEADERS, args.id, args.src_url,
                        args.dest_url, args.notes, args.tag)
    elif args.create:
        create_redirect(REQUEST_HEADERS, args.src_url, args.dest_url, args.notes, args.tag)
    elif args.delete:
        delete_redirect(REQUEST_HEADERS, args.id)


"""
laern.duckdns.org
dest: google.com
id: 1572326897
ip: 89.106.200.1
"""