import socket


def get_ip(dns_name: str) -> str | None:
    if dns_name is None:
        return None
    ip_addr = None
    try:
        ip_addr = socket.gethostbyname(dns_name)
    except socket.gaierror as e:
        print(F'ERROR resolving {dns_name}: {e}')
    return ip_addr
