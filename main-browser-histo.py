#!/usr/bin/env python3
import os
import sqlite3
import shutil
import tempfile
import datetime
import configparser
import glob

def copy_history_file(src_path):
    """Copy the history file to a temporary location to avoid locking issues."""
    if not os.path.exists(src_path):
        return None
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        shutil.copy2(src_path, temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Error copying {src_path}: {e}")
        return None

def get_chrome_edge_history(db_path, browser_name):
    print(f"{browser_name} History (last minute):")
    temp_path = copy_history_file(db_path)
    if not temp_path:
        print(f"{browser_name} history file not found or could not be copied.")
        return

    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    try:
        # Compute threshold: Chrome/Edge timestamp (microseconds since Jan 1, 1601)
        now = datetime.datetime.now()
        epoch = datetime.datetime(1601, 1, 1)
        threshold = int((now - datetime.timedelta(minutes=1) - epoch).total_seconds() * 1e6)

        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls WHERE last_visit_time > ? ORDER BY last_visit_time DESC",
            (threshold,)
        )
        results = cursor.fetchall()
        if results:
            for url, title, last_visit_time in results:
                dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=last_visit_time)
                print(f"{dt}: {title} - {url}")
        else:
            print("No history entries in the last minute.")
    except Exception as e:
        print(f"Error reading {browser_name} history: {e}")
    finally:
        conn.close()
        os.unlink(temp_path)
    print("-" * 40)

def get_firefox_profile_path():
    profiles_ini = os.path.expanduser("~/.mozilla/firefox/profiles.ini")
    if not os.path.exists(profiles_ini):
        return None

    config = configparser.ConfigParser()
    config.read(profiles_ini)
    for section in config.sections():
        if config.has_option(section, "Default") and config.get(section, "Default") == "1":
            path = config.get(section, "Path")
            is_relative = config.get(section, "IsRelative", fallback="1")
            if is_relative == "1":
                return os.path.join(os.path.expanduser("~/.mozilla/firefox"), path)
            else:
                return path
    # Fallback: pick the first profile ending with .default-release
    candidates = glob.glob(os.path.expanduser("~/.mozilla/firefox/*.default-release"))
    return candidates[0] if candidates else None

def get_firefox_history():
    print("Firefox History (last minute):")
    profile_path = get_firefox_profile_path()
    if not profile_path:
        print("Firefox profile not found.")
        return

    history_path = os.path.join(profile_path, "places.sqlite")
    temp_path = copy_history_file(history_path)
    if not temp_path:
        print("Firefox history file not found or could not be copied.")
        return

    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    try:
        # Compute threshold: Firefox timestamp (microseconds since Jan 1, 1970)
        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)
        threshold = int((now - datetime.timedelta(minutes=1) - epoch).total_seconds() * 1e6)

        cursor.execute(
            "SELECT url, title, last_visit_date FROM moz_places WHERE last_visit_date > ? ORDER BY last_visit_date DESC",
            (threshold,)
        )
        results = cursor.fetchall()
        if results:
            for url, title, last_visit_date in results:
                if last_visit_date:
                    dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=last_visit_date)
                else:
                    dt = "N/A"
                print(f"{dt}: {title} - {url}")
        else:
            print("No history entries in the last minute.")
    except Exception as e:
        print(f"Error reading Firefox history: {e}")
    finally:
        conn.close()
        os.unlink(temp_path)
    print("-" * 40)

def main():
    chrome_history_path = os.path.expanduser("~/.config/google-chrome/Default/History")
    edge_history_path = os.path.expanduser("~/.config/microsoft-edge/Default/History")

    get_chrome_edge_history(chrome_history_path, "Chrome")
    get_chrome_edge_history(edge_history_path, "Edge")
    get_firefox_history()

if __name__ == "__main__":
    main()
