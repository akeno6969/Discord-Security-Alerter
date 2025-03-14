# (optional not needed) this automatically blocks a specific ip from attacking u again (maybe it works depenrs on ur protection)

def block_ip_automatically(ip):
    os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
    logging.info(f"Automatically blocked IP: {ip}")
    return f"🚫 **Blocked IP:** `{ip}`"