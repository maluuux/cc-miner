#!/data/data/com.termux/files/usr/bin/python3

import os
import time
import subprocess
import sys
import select
from datetime import datetime

# Configuration
LOG_FILE = os.path.expanduser("~/miner.log")
UPDATE_INTERVAL = 3  # seconds

class RealTimeMinerUI:
    def __init__(self):
        self.reset_stats()
        self.start_time = time.time()
        
    def reset_stats(self):
        self.stats = {
            'hashrate': "0 kN/s",
            'temperature': 0,
            'accepted': 0,
            'rejected': 0,
            'stale': 0,
            'threads': {},
            'difficulty': "N/A",
            'latency': "0ms",
            'efficiency': "0%"
        }
        
    def clear_screen(self):
        os.system('clear')
    
    def get_cpu_temp(self):
        """อ่านอุณหภูมิ CPU จากหลาย path ที่เป็นไปได้"""
        temp_paths = [
            '/sys/class/thermal/thermal_zone0/temp',
            '/sys/class/hwmon/hwmon0/temp1_input',
            '/sys/devices/virtual/thermal/thermal_zone0/temp'
        ]
        for path in temp_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return int(f.read().strip()) / 1000
                except:
                    continue
        return 0
    
    def parse_realtime_logs(self):
        """อ่าน log แบบ real-time ด้วย tail -f"""
        try:
            process = subprocess.Popen(
                ['tail', '-n', '50', '-f', LOG_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # ปรับตรงนี้ให้ตรงกับ format log จริงของคุณ
                if 'accepted' in line:
                    self.stats['accepted'] += 1
                elif 'rejected' in line:
                    self.stats['rejected'] += 1
                elif 'stale' in line.lower():
                    self.stats['stale'] += 1
                    
                # อ่าน hashrate (ตัวอย่าง: "5002.12 kN/s yes!")
                if 'kN/s' in line and 'yes!' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'kN/s' and i > 0:
                            self.stats['hashrate'] = f"{parts[i-1]} kN/s"
                
                # อ่าน difficulty (ตัวอย่าง: "diff 419437")
                if 'diff' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'diff' and i+1 < len(parts):
                            self.stats['difficulty'] = parts[i+1].replace(',', '')
                
                # อ่านประสิทธิภาพเธรด (ตัวอย่าง: "CPU T1: 720.75 kN/s")
                if 'CPU T' in line and 'kN/s' in line:
                    thread_part = line.split(':')[0].strip()
                    thread_num = thread_part.split('T')[1]
                    hashrate = line.split('kN/s')[0].split()[-1]
                    self.stats['threads'][f"T{thread_num}"] = f"{hashrate} kN/s"
                    
        except Exception as e:
            print(f"Error reading logs: {e}")

    def draw_progress(self, percent):
        """สร้าง progress bar แบบเรียบง่าย"""
        filled = '▰' * int(percent / 10)
        empty = '▱' * (10 - len(filled))
        return f"{filled}{empty} {percent}%"
    
    def get_uptime(self):
        """คำนวณเวลาการทำงาน"""
        sec = int(time.time() - self.start_time)
        return f"{sec//3600}h {(sec%3600)//60}m"
    
    def display_ui(self):
        """แสดงผล UI"""
        self.clear_screen()
        
        # Header
        print("🚀 VRSC MINER - REAL-TIME MONITOR")
        print("━" * 40)
        
        # Main Stats
        print(f"⛏️  HASH: {self.stats['hashrate']}")
        print(f"🌡️  TEMP: {self.stats['temperature']}°C")
        print(f"🔄 SHARES: {self.stats['accepted']}A/{self.stats['rejected']}R (Stale: {self.stats['stale']})")
        print(f"⚡ DIFF: {self.stats['difficulty']} | LATENCY: {self.stats['latency']}\n")
        
        # Thread Performance
        print("THREADS:")
        for i in range(1, 9):
            thread_id = f"T{i}"
            hashrate = self.stats['threads'].get(thread_id, "0 kN/s")
            print(f"{thread_id}: {hashrate.ljust(10)} {self.draw_progress(70 + i*2)}")
        
        # Footer
        print(f"\n⏱️  UPTIME: {self.get_uptime()}")
        print("━" * 40)
        print("[Q] Quit  [R] Refresh  [S] Stats")

    def run(self):
        """เริ่มการทำงานหลัก"""
        try:
            # สร้าง thread สำหรับอ่าน log แบบ real-time
            import threading
            log_thread = threading.Thread(target=self.parse_realtime_logs, daemon=True)
            log_thread.start()
            
            while True:
                # อัปเดตอุณหภูมิ CPU
                self.stats['temperature'] = self.get_cpu_temp()
                
                # แสดง UI
                self.display_ui()
                
                # ตรวจสอบการกดปุ่ม
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'q':
                        break
                    elif key == 'r':
                        self.reset_stats()
                    elif key == 's':
                        self.show_advanced_stats()
                
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nปิดโปรแกรม...")
    
    def show_advanced_stats(self):
        """แสดงสถิติเพิ่มเติม"""
        self.clear_screen()
        print("📊 ADVANCED STATISTICS")
        print("━" * 40)
        print(f"Pool: sg.vipor.net:5040")
        print(f"Efficiency: {self.stats['efficiency']}")
        print(f"Avg Hashrate: {self.stats['hashrate']}")
        print(f"Last Share: {datetime.now().strftime('%H:%M:%S')}")
        print("\nPress Enter to return...")
        input()

if __name__ == "__main__":
    # ตรวจสอบว่าไฟล์ log มีอยู่
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file not found at {LOG_FILE}")
        print("Please run the miner first!")
        sys.exit(1)
    
    # เริ่ม UI
    ui = RealTimeMinerUI()
    ui.run()
