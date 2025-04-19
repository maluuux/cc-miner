#!/data/data/com.termux/files/usr/bin/python3
import os
import time
import sys
from collections import deque

# ตั้งค่าการแสดงผล
MAX_LINES = 8
LOG_FILE = os.path.expanduser("~/ccminer/ccminer  -c ~/ccminer/config.json")

def clear_screen():
    os.system('clear')

def display_header():
    print("⚡ VRSC MINER - REAL-TIME MONITOR")
    print("━" * 40)

def process_line(line):
    """ปรับแต่งข้อความให้อ่านง่าย"""
    line = (line.replace("Accepted", "✅ ยอมรับ")
            .replace("diff", "ความยาก")
            .replace("kH/s", "kH/s")
            .replace("CPU", "🌡️ CPU")
            .replace("NET New job", "📶 งานใหม่"))
    return line.strip()

def main():
    log_history = deque(maxlen=MAX_LINES)
    
    try:
        while True:
            clear_screen()
            display_header()
            
            # อ่านไฟล์ล่าสุด (50 บรรทัดสุดท้าย)
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    lines = f.readlines()[-50:]
                
                # กรองและประมวลผลบรรทัดใหม่
                for line in lines:
                    if any(x in line for x in ["Accepted", "CPU", "NET"]):
                        processed = process_line(line)
                        log_history.append(processed)
            
            # แสดงผล
            for line in log_history:
                print(line)
            
            print("\n━" * 40)
            print("กด Ctrl+C เพื่อหยุด")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n❌ หยุดการทำงาน")

if __name__ == "__main__":
    main()
