import subprocess
import re
import json
import time
import sys

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ไม่พบไฟล์ config.json กรุณาตรวจสอบ")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ไฟล์ config.json มีรูปแบบไม่ถูกต้อง")
        sys.exit(1)

def filter_output(line):
    # กรองข้อความที่ไม่ต้องการแสดง
    filters = [
        'temperature', 'temp=', 'fan=', 'speed=', 
        'GPU', 'CUDA', 'NVML', 'Watt', 'power='
    ]
    
    for f in filters:
        if f.lower() in line.lower():
            return False
    
    # เก็บเฉพาะข้อมูลที่สำคัญ
    important_patterns = [
        r'accepted:\s*\d+/\d+',  # อัตราการรับงาน
        r'hashrate:\s*\d+',      # ความเร็วในการขุด
        r'VRSC',                 # ชื่อเหรียญ
        r'yes!\s*\(\d+\.\d+\s*\)' # ยืนยันการขุดสำเร็จ
    ]
    
    for pattern in important_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    return False

def run_miner():
    config = load_config()
    
    # อ่านคำสั่งจากไฟล์ start.sh
    try:
        with open('start.sh', 'r') as f:
            command = f.read().strip()
    except FileNotFoundError:
        print("ไม่พบไฟล์ start.sh กรุณาตรวจสอบ")
        sys.exit(1)
    
    # เริ่มกระบวนการขุด
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    print("เริ่มการขุดเหรียญ VRSC ด้วย CPU...")
    print("กำลังกรองข้อมูลที่ไม่จำเป็นออก...")
    print("=" * 50)
    
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and filter_output(output):
                # แสดงผลเฉพาะข้อมูลที่สำคัญ
                print(output.strip())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nกำลังหยุดการขุด...")
        process.terminate()
        print("หยุดการขุดเรียบร้อยแล้ว")

if __name__ == "__main__":
    run_miner()
