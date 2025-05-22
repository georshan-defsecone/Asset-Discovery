import ipaddress
import re

def parse_ip_range(ip_range):
    """Parses an IP range like 192.168.1.1-192.168.1.10 into a list of IPs."""
    start_ip, end_ip = ip_range.split('-')
    start = ipaddress.IPv4Address(start_ip.strip())
    end = ipaddress.IPv4Address(end_ip.strip())
    if end < start:
        raise ValueError("Invalid IP range: end IP is before start IP.")
    return [str(ip) for ip in range(int(start), int(end) + 1)]

def normalize_ip_list(ip_input):
    """Parses and normalizes different formats of IP input."""
    ip_list = set()

    # Split by comma first
    parts = ip_input.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            # IP Range
            ip_list.update(parse_ip_range(part))
        elif '/' in part:
            # CIDR Notation
            try:
                net = ipaddress.IPv4Network(part, strict=False)
                ip_list.update([str(ip) for ip in net.hosts()])
            except ValueError:
                raise ValueError(f"Invalid CIDR: {part}")
        else:
            # Single IP
            try:
                ipaddress.IPv4Address(part)
                ip_list.add(part)
            except ValueError:
                raise ValueError(f"Invalid IP address: {part}")

    return sorted(ip_list)

def get_input_data(ip_input):
    """
    Returns a dictionary of normalized inputs for scanning.
    """
    try:
        ip_list = normalize_ip_list(ip_input)
    except ValueError as e:
        return {"error": str(e)}

    return {
        "ips": ip_list # ,
        # "username": username,
        # "password": password,
        # "domain": domain_name
    }
