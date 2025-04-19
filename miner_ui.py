#!/data/data/com.termux/files/usr/bin/python3
import os
import sys
import time
from collections import deque

# ตั้งค่าคำที่ต้องการตรวจจับ (คุณสามารถเพิ่ม/แก้ไขได้)
KEYWORDS = {
    'diff': 'ระดับความยาก:',
    'accepted': '✅ ยอมรับแล้ว:',
    'rejected': '❌ ถูกปฏิเสธ:',
    'stale': '🕒 ล้าสมัย:',
    'hashrate': '⚡ อัตราการขุด:',
    'CPU': '🌡️ อุณหภูมิ CPU:'
}

# ตั้งค่าการแสดงผล
MAX_LINES = 10  # จำนวนบรรทัดสูงสุดที่แสดง
LOG_FILE = os.path.expanduser("~/miner.log")  # ไฟล์ log ของ CCminer

def clear_screen():
    os.system('clear')

def display_header():
    print("🛠️ VRSC MINER LOG PROCESSOR")
    print("━" * 40)
    print("คำอธิบายที่กำหนด:")
    for k, v in KEYWORDS.items():
        print(f"{k} → {v}...")
    print("━" * 40)
    print()

def process_line(line):
    """ประมวลผลแต่ละบรรทัดและแทนที่คำหลัก"""
    processed = line
    for keyword, replacement in KEYWORDS.items():
        if keyword in line:
            processed = processed.replace(keyword, replacement)
    return processed.strip()

def tail_file(filename, n=10):
    """อ่านไฟล์แบบ real-time"""
    try:
        with open(filename, 'r') as f:
            # ย้ายไปยังจุดสิ้นสุดของไฟล์
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line
    except FileNotFoundError:
        print(f"❌ ผิดพลาด: ไม่พบไฟล์ {filename}")
        sys.exit(1)

def main():
    clear_screen()
    display_header()
    
    # เก็บประวัติการแสดงผล
    log_history = deque(maxlen=MAX_LINES)
    
    try:
        print(f"กำลังตรวจสอบไฟล์: {LOG_FILE}\n")
        print("━" * 40)
        
        for line in tail_file(LOG_FILE):
            processed_line = process_line(line)
            
            # เพิ่มบรรทัดใหม่และรักษาจำนวนบรรทัดให้คงที่
            log_history.append(processed_line)
            clear_screen()
            display_header()
            
            # แสดงประวัติล่าสุด
            for log_line in log_history:
                print(log_line)
                
            print("\n━" * 40)
            print("กด Ctrl+C เพื่อหยุด")
            
    except KeyboardInterrupt:
        print("\n❌ หยุดการทำงาน")
    except Exception as e:
        print(f"\n⚠️ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    main()
