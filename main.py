# Written by akeno6969 on github
# if you paid for this you were scammed!


import discord # dependency  
import asyncio # dependency
import subprocess # dependency
import re # dependency
import os # dependency
import time # dependency
import requests # dependency
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 


TOKEN = "YOUR_DISCORD_BOT_TOKEN" # replace with ur details
CHANNEL_ID = 1234567890  # replace with ur details


intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)



def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return "Unknown IP ):"



def get_geoip(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
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


def detect_sudo_usage():
    result = subprocess.run(["grep", "COMMAND=", "/var/log/auth.log"], capture_output=True, text=True)
    if result.stdout:
        return f"🚨 **Root Privilege Command Executed!**\n```\n{result.stdout}\n```"
    return None


def detect_usb_insertions():
    result = subprocess.run(["dmesg | grep -i 'usb' | tail -5"], shell=True, capture_output=True, text=True)
    if result.stdout:
        return f"🔌 **New USB Device Inserted!**\n```\n{result.stdout}\n```"
    return None



def detect_network_activity():
    result = subprocess.run(["netstat", "-ant"], capture_output=True, text=True)
    active_connections = result.stdout.count("ESTABLISHED")

    if active_connections > 150:  # Adjust threshold if needed
        return f"🚨 **Unusual Network Activity Detected!**\n🔹 Active Connections: `{active_connections}`"
    
    return None


class SecurityFileMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.startswith("/etc/") or event.src_path.startswith("/var/www/"):
            asyncio.run_coroutine_threadsafe(client.get_channel(CHANNEL_ID).send(
                f"⚠️ **Filesystem Change Detected!**\n🔹 File: `{event.src_path}`"
            ), client.loop)


def block_ip(ip):
    os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
    return f"🚫 **Blocked IP:** `{ip}`"

# 🔹 Security Monitor Function
async def security_monitor():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        alerts = [
            check_ssh_attacks(),
            detect_failed_logins(),
            detect_sudo_usage(),
            detect_network_activity(),
            detect_usb_insertions()
        ]

        for alert in alerts:
            if alert:
                await channel.send(alert)

        await asyncio.sleep(60)  # Check every minute


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!block "):
        ip = message.content.split("!block ")[1]
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):  
            response = block_ip(ip)
            await message.channel.send(response)
        else:
            await message.channel.send("❌ Invalid IP format!")

    if message.content == "!status":
        await message.channel.send("✅ **Security Alert Bot is running!**")

    if message.content == "!check_usb":
        usb_alert = detect_usb_insertions()
        await message.channel.send(usb_alert if usb_alert else "✅ No recent USB activity detected.")

    if message.content == "!check_network":
        net_alert = detect_network_activity()
        await message.channel.send(net_alert if net_alert else "✅ No unusual network activity detected.")


observer = Observer()
observer.schedule(SecurityFileMonitor(), "/etc/", recursive=True)
observer.schedule(SecurityFileMonitor(), "/var/www/", recursive=True)
observer.start()


client.loop.create_task(security_monitor())


client.run(TOKEN)