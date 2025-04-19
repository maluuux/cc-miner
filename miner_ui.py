#!/data/data/com.termux/files/usr/bin/python3

import os
import time
import subprocess
import sys
import select  # เพิ่ม import นี้เพื่อแก้ error
from datetime import datetime

# Configuration
MINER_PATH = os.path.expanduser("~/ccminer")
CONFIG_FILE = os.path.expanduser("~/config.json")
LOG_FILE = os.path.expanduser("~/miner.log")
UPDATE_INTERVAL = 5  # seconds

class MinerUI:
    def __init__(self):
        self.accepted_shares = 0
        self.rejected_shares = 0
        self.stale_shares = 0
        self.hashrate = "0 kN/s"
        self.temperature = 0
        self.threads = {f"T{i}": "0 kN/s" for i in range(1, 9)}
        self.start_time = time.time()
        self.last_update = time.time()
        
    def clear_screen(self):
        os.system('clear')
        
    def get_cpu_temp(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000
        except:
            return 0
            
    def parse_logs(self):
        try:
            if not os.path.exists(LOG_FILE):
                return
                
            # Read last 20 lines of log
            result = subprocess.run(['tail', '-n', '20', LOG_FILE], 
                                 capture_output=True, text=True)
            log_lines = result.stdout.split('\n')
            
            # Reset counters
            self.accepted_shares = 0
            self.rejected_shares = 0
            self.stale_shares = 0
            
            for line in log_lines:
                if 'accepted' in line.lower():
                    self.accepted_shares += 1
                elif 'rejected' in line.lower():
                    self.rejected_shares += 1
                elif 'stale' in line.lower():
                    self.stale_shares += 1
                    
                # Parse hashrate
                if 'kN/s' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'kN/s' and i > 0:
                            self.hashrate = f"{parts[i-1]} kN/s"
                            
                # Parse thread performance
                if any(f"T{i}:" in line for i in range(1, 9)) and 'kN/s' in line:
                    thread_part = line.split(':')[0].strip()
                    hashrate = line.split('kN/s')[0].split()[-1]
                    self.threads[thread_part] = f"{hashrate} kN/s"
                        
        except Exception as e:
            print(f"Error parsing logs: {e}")

    def draw_progress_bar(self, percent):
        filled = '█' * int(percent / 10)
        empty = '_' * (10 - len(filled))
        return f"{filled}{empty} {percent}%"
        
    def get_uptime(self):
        uptime_sec = int(time.time() - self.start_time)
        hours = uptime_sec // 3600
        minutes = (uptime_sec % 3600) // 60
        return f"{hours}h {minutes}m"
        
    def display_ui(self):
        self.clear_screen()
        
        # Header
        print("VERUS MINER | POOL: sg.vipor.net")
        print("━" * 40)
        
        # Main stats
        print(f"HASH: {self.hashrate} ▲1.2%")
        print(f"TEMP: {self.temperature}°C {self.draw_progress_bar(72)}")
        print(f"NET: 1.4 KB/s ▲ Latency: 120ms")
        print(f"SHARES: {self.accepted_shares}A/{self.rejected_shares}R (Stale: {self.stale_shares})")
        print(f"EFFICIENCY: 98.5% Diff: 27\n")
        
        # Thread performance
        print("THREAD PERFORMANCE:")
        for i in range(1, 9):
            thread_id = f"T{i}"
            hashrate = self.threads.get(thread_id, "0 kN/s")
            print(f"{thread_id}: {hashrate} {self.draw_progress_bar(80 - i*3)}")
        
        # Footer
        print(f"\nUPTIME: {self.get_uptime()} | Alerts: 0")
        print("━" * 40)
        print("[Q] Quit [L] Logs [P] Pool Stats")

    def run(self):
        try:
            while True:
                self.temperature = self.get_cpu_temp()
                self.parse_logs()
                self.display_ui()
                
                # Check for user input
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'q':
                        break
                    elif key == 'l':
                        os.system(f"less {LOG_FILE}")
                    elif key == 'p':
                        self.show_pool_stats()
                
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nStopping miner UI...")

    def show_pool_stats(self):
        self.clear_screen()
        print("POOL STATISTICS:")
        print("Active Workers: 12")
        print("Pool Hashrate: 1.23 GH/s")
        print("Estimated Earnings: 0.0021 VRSC/hr")
        print("Last Block: 12m ago\n")
        input("Press Enter to return...")

if __name__ == "__main__":
    # Check requirements
    if not os.path.exists(MINER_PATH):
        print("Error: CCminer not found!")
        sys.exit(1)
        
    if not os.path.exists(LOG_FILE):
        print("Warning: Log file not found. Creating empty one...")
        open(LOG_FILE, 'w').close()
    
    # Run UI
    ui = MinerUI()
    ui.run()
