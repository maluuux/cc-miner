#!/data/data/com.termux/files/usr/bin/python3

import subprocess
import re
import time
import sys
from datetime import datetime


def __init__(self):
        self.hashrate_history = []
        self.start_time = time.time()
        self.max_history = 30
        self.config = self.load_config()
        self.last_difficulty = None
        self.last_update_time = None
        self.last_lines = []
        self.max_last_lines = 2
        self.alert_messages = []
        self.running = True
        self.miner_data = {
            'hashrate': 0,
            'difficulty': 0,
            'accepted': 0,
            'rejected': 0,
            'connection': {
                'status': 'กำลังเชื่อมต่อ...',
                'pool': self.config.get('pools', ['ไม่ระบุ'])[0],
                'url': 'ไม่ระบุ'
            },
            'block': 0
        }
def clear_screen():
    print("\033[H\033[J", end="")

def print_header():
    clear_screen()
    print("""
\033[1;36m╔══════════════════════════════════════════════════╗
║ \033[1;33mVRSC CCminer Mobile - Custom Dashboard\033[1;36m           ║
╚══════════════════════════════════════════════════╝\033[0m
""")

def parse_miner_output(line):
    # Regular expressions to extract mining data
    hashrate_pattern = re.compile(r"accepted:.*?([\d,]+)\s*kN/s")
    share_pattern = re.compile(r"accepted:\s*(\d+)/(\d+)")
    difficulty_pattern = re.compile(r"diff\s*(\d+)")
    
    data = {
        'hashrate': "0.00",
        'unit': "kN/s",
        'accepted': 0,
        'total': 0,
        'difficulty': 0,
        'time': datetime.now().strftime("%H:%M:%S")
    }
    
    if hashrate_match := hashrate_pattern.search(line):
        data['hashrate'] = hashrate_match.group(1).replace(",", "")
    
    if share_match := share_pattern.search(line):
        data['accepted'] = int(share_match.group(1))
        data['total'] = int(share_match.group(2))
    
    if difficulty_match := difficulty_pattern.search(line):
        data['difficulty'] = int(difficulty_match.group(1))
    
    return data

def display_stats(data):
    print(f"\033[1;34mTime:\033[0m \033[1;32m{data['time']}\033[0m")
    
    print(f"\033[1;34mHashrate:\033[0m \033[1;33m{float(data['hashrate']):,.2f} {data['unit']}\033[0m")
    
    print(f"\033[1;34mAccepted shares:\033[0m \033[1;32m{data['accepted']}\033[0m/"
          f"\033[1;34mTotal:\033[0m \033[1;35m{data['total']}\033[0m")
    
    print(f"\033[1;34mDifficulty:\033[0m \033[1;36m{data['difficulty']:,}\033[0m")
    
    print("\n\033[1;36m" + "═" * 50 + "\033[0m")

def main():
    # Start mining process
    process = subprocess.Popen(
        ["./start.sh"],
        cwd="/path/to/ccminer",  # Change to your ccminer directory
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
                
            if "accepted:" in line:
                data = parse_miner_output(line)
                print_header()
                display_stats(data)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\033[1;31mStopping miner...\033[0m")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    main()
