import re

def is_valid_ip(ip):
    return bool(re.match(r"^\d+\.\d+\.\d+\.\d+$", ip))

def rate_limit(last_called, threshold=10):
    if time.time() - last_called < threshold:
        return False
    return True