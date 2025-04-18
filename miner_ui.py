#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import signal
import subprocess
from threading import Thread, Lock
from datetime import datetime, timedelta
import re
import json

class VRSCMinerController:
    def __init__(self):
        self.miner_process = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 5
        self.last_activity = time.time()
        self.lock = Lock()
        self.stats = {
            'shares': {'accepted': 0, 'rejected': 0},
            'hashrate': {'current': 0, 'average': 0, 'max': 0},
            'uptime': 0,
            'start_time': datetime.now()
        }
        self.hash_history = []
        self.check_config()

    def check_config(self):
        """ตรวจสอบการตั้งค่าและ dependencies"""
        # ตรวจสอบไฟล์ที่จำเป็น
        required_files = ['start.sh', 'ccminer', 'config.json']
        for f in required_files:
            if not os.path.exists(f):
                print(f"\033[1;31m❌ ไม่พบไฟล์: {f}\033[0m")
                sys.exit(1)

        # ตรวจสอบ library
        lib_path = f"{os.environ['PREFIX']}/lib"
        required_libs = ['libjansson.so', 'libssl.so', 'libcrypto.so']
        for lib in required_libs:
            if not os.path.exists(f"{lib_path}/{lib}"):
                print(f"\033[1;31m❌ ไม่พบ library: {lib}\033[0m")
                print(f"ติดตั้งด้วยคำสั่ง: pkg install {lib.split('.')[0][3:]}")
                sys.exit(1)

        # อ่าน config
        try:
            with open('config.json') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"\033[1;31m❌ ข้อผิดพลาด config.json: {e}\033[0m")
            sys.exit(1)

    def setup_environment(self):
        """ตั้งค่า environment ที่จำเป็น"""
        os.environ['LD_LIBRARY_PATH'] = f"{os.environ.get('LD_LIBRARY_PATH', '')}:{os.environ['PREFIX']}/lib"
        os.chmod('start.sh', 0o755)
        os.chmod('ccminer', 0o755)

    def start_miner(self):
        """เริ่มกระบวนการขุด"""
        with self.lock:
            if self.running:
                return True

            try:
                self.setup_environment()
                
                print("\033[1;36m🚀 กำลังเริ่มกระบวนการขุด...\033[0m")
                self.miner_process = subprocess.Popen(
                    ['./start.sh'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                    preexec_fn=os.setsid,
                    shell=True,
                    env=os.environ
                )

                self.running = True
                self.last_activity = time.time()
                
                # สร้าง threads สำหรับ monitoring
                Thread(target=self.monitor_stdout, daemon=True).start()
                Thread(target=self.monitor_stderr, daemon=True).start()
                Thread(target=self.health_check, daemon=True).start()
                
                return True

            except Exception as e:
                print(f"\033[1;31m❌ เริ่ม miner ไม่สำเร็จ: {e}\033[0m")
                return False

    def monitor_stdout(self):
        """ตรวจสอบ stdout จาก miner"""
        while self.running and self.miner_process.poll() is None:
            line = self.miner_process.stdout.readline()
            if line:
                self.process_output(line.strip())

    def monitor_stderr(self):
        """ตรวจสอบ stderr จาก miner"""
        while self.running and self.miner_process.poll() is None:
            line = self.miner_process.stderr.readline()
            if line:
                print(f"\033[1;31m[ERROR] {line.strip()}\033[0m")

    def process_output(self, line):
        """ประมวลผล output จาก miner"""
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\033[1;37m[{now}] {line}\033[0m")
        self.last_activity = time.time()

        # อัพเดทสถิติ
        self.update_stats(line)

    def update_stats(self, line):
        """อัพเดทสถิติจาก output"""
        # ตรวจสอบ accepted shares
        if 'accepted' in line.lower():
            if 'rejected' in line.lower():
                self.stats['shares']['rejected'] += 1
            else:
                self.stats['shares']['accepted'] += 1

        # ตรวจสอบ hashrate
        hashrate_match = re.search(r'(\d+\.?\d*)\s?(kH/s|H/s)', line)
        if hashrate_match:
            rate = float(hashrate_match.group(1))
            if hashrate_match.group(2) == 'kH/s':
                rate *= 1000
            
            self.stats['hashrate']['current'] = rate
            self.hash_history.append(rate)
            
            # คำนวณค่าเฉลี่ยและค่าสูงสุด
            if self.hash_history:
                self.stats['hashrate']['average'] = sum(self.hash_history) / len(self.hash_history)
                self.stats['hashrate']['max'] = max(self.hash_history)

        # อัพเดทเวลาทำงาน
        self.stats['uptime'] = str(datetime.now() - self.stats['start_time']).split('.')[0]

    def health_check(self):
        """ตรวจสอบสุขภาพ miner"""
        while self.running:
            time.sleep(15)
            
            # ตรวจสอบว่า miner ยังทำงานอยู่หรือไม่
            if self.miner_process.poll() is not None:
                print("\033[1;33m⚠️ โปรแกรมขุดหยุดทำงาน\033[0m")
                self.running = False
                self.restart_miner()
                break
                
            # ตรวจสอบกิจกรรมล่าสุด
            if time.time() - self.last_activity > 60:
                print("\033[1;33m⚠️ ไม่พบกิจกรรมขุดเกิน 1 นาที\033[0m")
                self.restart_miner()
                break

    def restart_miner(self):
        """รีสตาร์ท miner"""
        with self.lock:
            if self.restart_count >= self.max_restarts:
                print("\033[1;31m❌ รีสตาร์ทเกินจำนวนครั้งที่กำหนด กำลังหยุด...\033[0m")
                self.stop_miner()
                return False

            self.restart_count += 1
            print(f"\033[1;36m♻️ กำลังรีสตาร์ท... (ครั้งที่ {self.restart_count}/{self.max_restarts})\033[0m")
            
            self.stop_miner()
            time.sleep(3)
            return self.start_miner()

    def stop_miner(self):
        """หยุด miner"""
        with self.lock:
            if not self.running:
                return

            print("\033[1;36m🛑 กำลังหยุดกระบวนการขุด...\033[0m")
            self.running = False

            try:
                if self.miner_process:
                    os.killpg(os.getpgid(self.miner_process.pid), signal.SIGTERM)
                    self.miner_process.wait(timeout=10)
            except Exception as e:
                print(f"\033[1;33m⚠️ ข้อผิดพลาดขณะหยุดกระบวนการ: {e}\033[0m")
                try:
                    os.killpg(os.getpgid(self.miner_process.pid), signal.SIGKILL)
                except:
                    pass
            finally:
                self.miner_process = None

    def display_stats(self):
        """แสดงสถิติการทำงาน"""
        while self.running:
            time.sleep(5)
            self.clear_screen()
            
            print("\033[1;36m" + "═" * 50)
            print("📊 VRSC MINER STATISTICS")
            print("═" * 50 + "\033[0m")
            
            print(f"\033[1;33m⏱️ เวลาทำงาน: {self.stats['uptime']}")
            print(f"✅ ยอมรับแล้ว: {self.stats['shares']['accepted']} | ❌ ถูกปฏิเสธ: {self.stats['shares']['rejected']}")
            print(f"⚡ แฮชเรท: {self.stats['hashrate']['current']/1000:.2f} kH/s (เฉลี่ย: {self.stats['hashrate']['average']/1000:.2f} kH/s)")
            print(f"📈 สูงสุด: {self.stats['hashrate']['max']/1000:.2f} kH/s | ♻️ รีสตาร์ท: {self.restart_count}/{self.max_restarts}")
            print("\033[1;36m" + "═" * 50 + "\033[0m")
            print("\033[1;32mกำลังทำงาน... กด Ctrl+C เพื่อหยุด\033[0m")

    def clear_screen(self):
        """ล้างหน้าจอ"""
        os.system('clear' if os.name == 'posix' else 'cls')

def main():
    # ตั้งค่าสัญญาณ
    controller = VRSCMinerController()
    signal.signal(signal.SIGINT, lambda s, f: controller.stop_miner())

    # เริ่มการทำงาน
    if controller.start_miner():
        try:
            # แสดงสถิติ
            Thread(target=controller.display_stats, daemon=True).start()
            
            # รอจนกว่าจะหยุด
            while controller.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\033[1;33m🛑 ได้รับสัญญาณหยุดจากผู้ใช้\033[0m")
        finally:
            controller.stop_miner()
    else:
        print("\033[1;31m❌ ไม่สามารถเริ่มการขุดได้\033[0m")

    print("\033[1;36m✅ จบการทำงาน\033[0m")

if __name__ == "__main__":
    main()
