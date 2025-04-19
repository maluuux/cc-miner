import os
import subprocess
import json
import time
import re

def clear_screen():
    os.system('clear')

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ไม่พบไฟล์ config.json กรุณาตรวจสอบ")
        return None
    except json.JSONDecodeError:
        print("ไฟล์ config.json มีรูปแบบไม่ถูกต้อง")
        return None

def filter_miner_output(line):
    # กรองข้อความที่ไม่ต้องการแสดง
    patterns_to_filter = [
        r'temperature',
        r'temp',
        r'℃',
        r'°C',
        r'hashrate',
        r'accept',
        r'reject',
        r'GPU',
        r'CPU'
    ]
    
    for pattern in patterns_to_filter:
        if re.search(pattern, line, re.IGNORECASE):
            return False
    
    return True

def run_miner():
    config = load_config()
    if not config:
        return
    
    # ตรวจสอบว่าไฟล์ start.sh มีอยู่
    if not os.path.exists('start.sh'):
        print("ไม่พบไฟล์ start.sh กรุณาตรวจสอบ")
        return
    
    # เปลี่ยน permission ให้ไฟล์ start.sh สามารถรันได้
    os.chmod('start.sh', 0o755)
    
    clear_screen()
    print("กำลังเริ่มต้นขุดเหรียญ VRSC...")
    print("ใช้โทรศัพท์มือถือในการขุดด้วย CPU")
    print("กำลังซ่อนข้อมูลอุณหภูมิและข้อมูลที่ไม่จำเป็น...")
    print("\nพิมพ์ 'stop' เพื่อหยุดการขุด\n")
    
    # รัน miner ผ่าน start.sh
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    try:
        while True:
            # ตรวจสอบว่ายังมี process ทำงานอยู่หรือไม่
            if process.poll() is not None:
                print("\nMiner หยุดทำงานแล้ว")
                break
            
            # อ่าน output จาก miner
            line = process.stdout.readline()
            if not line:
                continue
            
            # กรองและแสดงเฉพาะข้อความที่ต้องการ
            if filter_miner_output(line):
                print(line.strip())
            
            # ตรวจสอบคำสั่งหยุดจากผู้ใช้
            user_input = input_non_blocking()
            if user_input and user_input.lower() == 'stop':
                print("\nกำลังหยุดการขุด...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                break
                
    except KeyboardInterrupt:
        print("\nกำลังหยุดการขุด...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    print("การขุดหยุดทำงานแล้ว")

def input_non_blocking():
    """ฟังก์ชันสำหรับรับ input โดยไม่บล็อกการทำงานหลัก"""
    import sys
    import select
    
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None

if __name__ == "__main__":
    run_miner()
