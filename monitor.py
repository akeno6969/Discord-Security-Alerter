# Simple monitoring script NOT the main script!!

import re
import subprocess
import os
from config import GEOIP_API_URL
import requests

def get_geoip(ip):
    try:
        response = requests.get(GEOIP_API_URL.format(ip=ip))
        data = response.json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country", "Unknown")
        org = data.get("org", "Unknown")
        return f"🌍 **GeoIP Info:** {city}, {region}, {country} (Org: {org})"
    except:
        return "❌ GeoIP lookup failed."

def check_ssh_attacks():
    log_file = "/var/log/auth.log"
    if not os.path.exists(log_file):
        return None
    with open(log_file, "r") as log:
        for line in log.readlines():
            if "Failed password" in line:
                ip_match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    ip = ip_match.group(1)
                    geo = get_geoip(ip)
                    return f"⚠️ **SSH Brute Force Attempt Detected!**\n🔹 Attacker IP: `{ip}`\n{geo}"
    return None

def detect_failed_logins():
    result = subprocess.run(["lastb", "-n", "5"], capture_output=True, text=True)
    if result.stdout:
        ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", result.stdout)
        alerts = []
        for ip in ips:
            geo = get_geoip(ip)
            alerts.append(f"⚠️ **Failed Login Attempt from IP:** `{ip}`\n{geo}")
        return "\n".join(alerts)
    return None