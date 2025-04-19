#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import re
import time

def clear_screen():
    """ล้างหน้าจอ"""
    os.system('clear')

def load_config():
    """โหลดการตั้งค่าจากไฟล์ config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ ไม่พบไฟล์ config.json กรุณาตรวจสอบอีกครั้ง")
        sys.exit(1)
    except json.JSONDecodeError:
        print("⚠️ ไฟล์ config.json มีรูปแบบไม่ถูกต้อง")
        sys.exit(1)

def modify_config(config):
    """ปรับแต่งการตั้งค่า config.json"""
    print("\n⚙️ การตั้งค่าปัจจุบัน:")
    print(f"Pool: {config['pool']}")
    print(f"Wallet: {config['wallet'][:10]}...{config['wallet'][-5:]}")
    print(f"Worker Name: {config['worker_name']}")
    
    change = input("\nต้องการเปลี่ยนการตั้งค่าไหม? (y/n): ").lower()
    if change == 'y':
        config['pool'] = input("ใส่ที่อยู่ Pool (เช่น stratum+tcp://example.com:port): ")
        config['wallet'] = input("ใส่ที่อยู่ Wallet: ")
        config['worker_name'] = input("ใส่ชื่อ Worker: ")
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("✅ บันทึกการตั้งค่าเรียบร้อยแล้ว")
    else:
        print("🚫 ไม่มีการเปลี่ยนแปลงการตั้งค่า")

def start_mining():
    """เริ่มต้นการขุดโดยซ่อนอุณหภูมิ CPU"""
    print("\n⛏️ กำลังเริ่มการขุด...")
    print("ℹ️ การแสดงอุณหภูมิ CPU จะถูกซ่อนไว้")
    
    try:
        # ใช้คำสั่ง start.sh หรือเรียก ccminer โดยตรง
        if os.path.exists('start.sh'):
            process = subprocess.Popen(['bash', 'start.sh'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
        else:
            config = load_config()
            command = [
                './ccminer',
                '-a', 'verus',
                '-o', config['pool'],
                '-u', config['wallet'],
                '-p', 'x',
                '--cpu-affinity', '1',
                '--background'
            ]
            process = subprocess.Popen(command, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
        
        # กรองและแสดงผลลัพธ์โดยซ่อนอุณหภูมิ
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # กรองบรรทัดที่มีอุณหภูมิออก
                if 'temperature' not in output.lower() and 'temp' not in output.lower():
                    print(output.strip())
        
        print("\n⛏️ การขุดได้หยุดทำงาน")
    except KeyboardInterrupt:
        print("\n🛑 หยุดการขุดโดยผู้ใช้")
        process.terminate()
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {str(e)}")

def main_menu():
    """แสดงเมนูหลัก"""
    clear_screen()
    print("""
    🚀 CCminer Manager สำหรับ Termux 🚀
    ----------------------------------
    1. เริ่มการขุด (ซ่อนอุณหภูมิ)
    2. เปลี่ยนการตั้งค่า
    3. ตรวจสอบสถานะการขุด
    4. หยุดการขุด
    5. ออกจากโปรแกรม
    ----------------------------------
    ℹ️ หมายเหตุ: โปรแกรมนี้สำหรับใช้ CPU เท่านั้น
    """)

def main():
    """ฟังก์ชันหลัก"""
    while True:
        main_menu()
        choice = input("เลือกเมนู (1-5): ")
        
        if choice == '1':
            start_mining()
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == '2':
            config = load_config()
            modify_config(config)
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == '3':
            print("\n🔍 กำลังตรวจสอบสถานะการขุด...")
            # คำสั่งตรวจสอบกระบวนการขุด
            os.system('ps aux | grep ccminer | grep -v grep')
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == '4':
            print("\n🛑 กำลังหยุดกระบวนการขุด...")
            os.system('pkill -f ccminer')
            print("✅ หยุดการขุดเรียบร้อยแล้ว")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == '5':
            print("\n👋 ออกจากโปรแกรม... ขอบคุณที่ใช้บริการ!")
            sys.exit(0)
        else:
            print("\n⚠️ กรุณาเลือกหมายเลขระหว่าง 1-5 เท่านั้น")
            time.sleep(1)

if __name__ == "__main__":
    # ตรวจสอบว่าใช้งานใน Termux หรือไม่
    if not os.path.exists('/data/data/com.termux/files/home'):
        print("⚠️ โปรแกรมนี้ออกแบบมาสำหรับใช้งานใน Termux เท่านั้น")
        sys.exit(1)
    
    # ตรวจสอบว่า ccminer มีอยู่หรือไม่
    if not os.path.exists('ccminer') and not os.path.exists('start.sh'):
        print("⚠️ ไม่พบไฟล์ ccminer หรือ start.sh ในไดเรกทอรีปัจจุบัน")
        sys.exit(1)
    
    main()
