#!/usr/bin/env python3
import subprocess
import sys

def get_windowed_applications():
    try:
        # Get list of windowed applications using wmctrl
        output = subprocess.check_output(["wmctrl", "-lp"], universal_newlines=True)
    except FileNotFoundError:
        print("wmctrl not found. Please install wmctrl (e.g., sudo apt-get install wmctrl).")
        sys.exit(1)
    windows = []
    for line in output.strip().splitlines():
        # Expected format: window_id desktop pid hostname title
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        window_id, desktop, pid, hostname, title = parts
        try:
            # Retrieve the command for the process using ps
            command = subprocess.check_output(["ps", "-p", pid, "-o", "cmd="], universal_newlines=True).strip()
        except subprocess.CalledProcessError:
            command = "N/A"
        windows.append({
            "window_id": window_id,
            "desktop": desktop,
            "pid": pid,
            "hostname": hostname,
            "title": title,
            "command": command
        })
    return windows

def main():
    apps = get_windowed_applications()
    if not apps:
        print("No windowed applications found.")
    else:
        for app in apps:
            print(f"Window ID: {app['window_id']}")
            print(f"Desktop: {app['desktop']}")
            print(f"PID: {app['pid']}")
            print(f"Host: {app['hostname']}")
            print(f"Title: {app['title']}")
            print(f"Command: {app['command']}")
            print("-" * 40)

if __name__ == "__main__":
    main()