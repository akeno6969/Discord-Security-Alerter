from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
import discord

class FileMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.startswith("/etc/") or event.src_path.startswith("/var/www/"):
            asyncio.run_coroutine_threadsafe(client.get_channel(CHANNEL_ID).send(
                f"⚠️ **Filesystem Change Detected!**\n🔹 File: `{event.src_path}`"
            ), client.loop)

def start_file_monitor():
    observer = Observer()
    observer.schedule(FileMonitor(), "/etc/", recursive=True)
    observer.schedule(FileMonitor(), "/var/www/", recursive=True)
    observer.start()