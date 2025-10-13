import socket


def get_ip(dns_name: str) -> str:
    ip_addr = ''
    try:
        ip_addr = socket.gethostbyname(dns_name)
    except socket.gaierror as e:
        ip_addr = F'ERROR resolving {dns_name}: {e}'
    return ip_addr
