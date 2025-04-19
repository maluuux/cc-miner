import subprocess
import json
import os
import re
import time

def clear_screen():
    os.system('clear')

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ ไม่พบไฟล์ config.json กรุณาตรวจสอบ")
        return None
    except json.JSONDecodeError:
        print("⚠️ ไฟล์ config.json มีรูปแบบไม่ถูกต้อง")
        return None

def filter_miner_output(line):
    # กรองข้อมูลที่ไม่ต้องการแสดง
    if 'temperature' in line.lower():
        return False
    if 'temp' in line.lower():
        return False
    if 'cpu' in line.lower() and 'usage' in line.lower():
        return False
    
    # เก็บเฉพาะข้อมูลสำคัญ
    patterns = [
        r'accepted',
        r'shares',
        r'hashrate',
        r'verus',
        r'VRSC',
        r'block',
        r'stratum'
    ]
    
    return any(re.search(p, line, re.IGNORECASE) for p in patterns)

def run_miner():
    config = load_config()
    if not config:
        print("❌ ไม่สามารถเริ่มต้น miner ได้เนื่องจากปัญหากับ config")
        return
    
    if not os.path.exists('start.sh'):
        print("❌ ไม่พบไฟล์ start.sh")
        return
    
    # ตั้งค่าสิทธิ์ให้ไฟล์ start.sh
    os.chmod('start.sh', 0o755)
    
    clear_screen()
    print("🛠️ กำลังเริ่มต้น VerusCoin (VRSC) Miner...")
    print("📌 ใช้โทรศัพท์มือถือในการขุดด้วย CPU")
    print("🔕 ปิดการแสดงอุณหภูมิ CPU")
    print("🔄 กรุณารอสักครู่...\n")
    
    try:
        process = subprocess.Popen(
            ['./start.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ Miner เริ่มทำงานแล้ว!\n")
        print("=== กำลังแสดงผลลัพธ์สำคัญ (กรองอุณหภูมิออกแล้ว) ===\n")
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
                
            if filter_miner_output(line):
                print(line.strip())
                
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n🛑 รับสัญญาณหยุด 작업...")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    finally:
        if 'process' in locals():
            process.terminate()
        print("\n❎ ปิดโปรแกรม Miner แล้ว\n")

if __name__ == "__main__":
    print("\n=== Python Script สำหรับจัดการ CCminer ใน Termux ===")
    print("=== พัฒนาสำหรับขุดเหรียญ VRSC ด้วย CPU โทรศัพท์ ===\n")
    
    run_miner()
    
    print("🙏 ขอบคุณที่ใช้สคริปต์นี้")
    print("⚠️ หมายเหตุ: การขุด cryptocurrency อาจทำให้อุปกรณ์ร้อนได้")
