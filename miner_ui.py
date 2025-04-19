#!/data/data/com.termux/files/usr/bin/python3
import os
import time
import subprocess
import json
from threading import Thread
import sys

# Configuration
MINER_PATH = os.path.expanduser("~/ccminer")
CONFIG_FILE = os.path.expanduser("~/config.json")
START_SCRIPT = os.path.expanduser("~/start.sh")
LOG_FILE = os.path.expanduser("~/miner.log")
REFRESH_RATE = 5  # seconds

class MinerMonitor:
    def __init__(self):
        self.running = True
        self.stats = {
            'hashrate': "0 kH/s",
            'accepted': 0,
            'rejected': 0,
            'cpu_temp': 0,
            'threads': {},
            'difficulty': "N/A"
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
    
    def parse_log(self):
        """อ่านและประมวลผล log file"""
        try:
            # ใช้ tail เพื่ออ่านล่าสุด 50 บรรทัด
            result = subprocess.run(['tail', '-n', '50', LOG_FILE], 
                                 capture_output=True, text=True)
            log_lines = result.stdout.split('\n')
            
            # รีเซ็ตค่าทุกครั้งที่อ่าน
            self.stats['accepted'] = 0
            self.stats['rejected'] = 0
            self.stats['threads'] = {}
            
            for line in log_lines:
                # นับ accepted/rejected shares
                if 'Accepted:[' in line:
                    self.stats['accepted'] += 1
                elif 'rejected' in line.lower():
                    self.stats['rejected'] += 1
                
                # อ่าน hashrate
                if 'kH/s yes!' in line:
                    parts = line.split('✅✅')
                    if len(parts) > 1:
                        self.stats['hashrate'] = parts[1].split('kH/s')[0].strip() + " kH/s"
                
                # อ่านประสิทธิภาพเธรด CPU
                if 'CPU T' in line and 'kH/s' in line:
                    thread = line.split('CPU T')[1].split(':')[0]
                    speed = line.split('kH/s')[0].split()[-1]
                    self.stats['threads'][f"T{thread}"] = f"{speed} kH/s"
                
                # อ่าน difficulty
                if 'difficulty set to' in line:
                    self.stats['difficulty'] = line.split('to')[1].strip()
                    
        except Exception as e:
            print(f"Error reading log: {e}")

    def display_ui(self):
        """แสดงผล UI"""
        self.clear_screen()
        
        # Header
        print("⚡ VRSC MINER MONITOR (Termux)")
        print("━" * 50)
        
        # Main Stats
        print(f"⛏️ Hashrate: {self.stats['hashrate']}")
        print(f"🌡️ CPU Temp: {self.stats['cpu_temp']:.1f}°C")
        print(f"📊 Shares: {self.stats['accepted']}A/{self.stats['rejected']}R")
        print(f"📶 Difficulty: {self.stats['difficulty']}")
        print("\nCPU Threads:")
        
        # Display CPU threads
        for i in range(1, 9):  # สำหรับ CPU 8 threads
            thread_id = f"T{i}"
            hashrate = self.stats['threads'].get(thread_id, "0 kH/s")
            print(f"  {thread_id}: {hashrate}")
        
        # Footer
        print("\n━" * 50)
        print("กด Ctrl+C เพื่อหยุด")

    def run(self):
        """เริ่มการตรวจสอบ"""
        try:
            while self.running:
                self.stats['cpu_temp'] = self.get_cpu_temp()
                self.parse_log()
                self.display_ui()
                time.sleep(REFRESH_RATE)
                
        except KeyboardInterrupt:
            print("\nปิดโปรแกรมตรวจสอบ...")
            self.running = False

if __name__ == "__main__":
    # ตรวจสอบไฟล์ที่จำเป็น
    if not all(os.path.exists(f) for f in [MINER_PATH, CONFIG_FILE, START_SCRIPT]):
        print("⚠️ ผิดพลาด: ไม่พบไฟล์ที่จำเป็น (ccminer/config.json/start.sh)")
        sys.exit(1)
        
    if not os.path.exists(LOG_FILE):
        print("⚠️ ข้อควรระวัง: ไม่พบไฟล์ log, จะสร้างใหม่เมื่อรัน miner")
        open(LOG_FILE, 'a').close()
    
    monitor = MinerMonitor()
    monitor.run()
