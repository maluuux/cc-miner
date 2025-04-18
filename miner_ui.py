import time
from datetime import datetime
import sys
import re
import os
import signal
from collections import deque
import subprocess
from threading import Thread

class VRSCMiner:
    def __init__(self):
        self.reset_stats()
        self.miner_process = None
        self.running = False
        self.shutdown_requested = False
        
    def reset_stats(self):
        """รีเซ็ตค่าสถิติทั้งหมด"""
        self.hash_history = deque(maxlen=10)
        self.start_time = time.time()
        self.total_shares = 0
        self.accepted_shares = 0
        self.current_hashrate = 0
        self.last_activity = time.time()
        self.cpu_cores = self.detect_cpu_cores()
    
    def detect_cpu_cores(self):
        """ตรวจสอบจำนวน CPU cores"""
        try:
            import multiprocessing
            cores = multiprocessing.cpu_count()
            print(f"\033[1;32mตรวจพบ CPU Cores: {cores}\033[0m")
            return cores
        except:
            print("\033[1;33mไม่สามารถตรวจสอบ CPU cores, ใช้ค่าเริ่มต้น 4 cores\033[0m")
            return 4
    
    def start_mining(self):
        """เริ่มกระบวนการขุด"""
        if not os.path.exists("./start.sh"):
            print("\033[1;31mERROR: ไม่พบไฟล์ start.sh\033[0m")
            return False
            
        try:
            self.reset_stats()
            os.chmod("./start.sh", 0o755)
            
            print("\033[1;36mกำลังเริ่มกระบวนการขุด...\033[0m")
            self.miner_process = subprocess.Popen(
                ["./start.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                preexec_fn=os.setsid,
                shell=True
            )
            
            self.running = True
            Thread(target=self.monitor_output, daemon=True).start()
            Thread(target=self.check_activity, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"\033[1;31mERROR: {str(e)}\033[0m")
            return False
    
    def monitor_output(self):
        """ตรวจสอบผลลัพธ์จาก miner"""
        while self.running and self.miner_process.poll() is None:
            line = self.miner_process.stdout.readline()
            if line:
                self.process_miner_output(line)
                self.last_activity = time.time()
                
            # ตรวจสอบ error stream ด้วย
            err_line = self.miner_process.stderr.readline()
            if err_line:
                print(f"\033[1;31mERROR: {err_line.strip()}\033[0m")
    
    def process_miner_output(self, line):
        """ประมวลผลผลลัพธ์จาก miner"""
        line = line.strip()
        if not line:
            return
            
        print(f"\033[1;37m{line}\033[0m")  # แสดงผลลัพธ์ดั้งเดิม
        
        # ตรวจสอบการรับ share ใหม่
        if "accepted" in line.lower():
            self.total_shares += 1
            self.accepted_shares += 1
            print("\033[1;32m✔️ ยอมรับ Share ใหม่!\033[0m")
            
        # ตรวจสอบ hashrate
        hashrate_match = re.search(r'(\d+\.?\d*)\s?(kH/s|H/s)', line)
        if hashrate_match:
            rate = float(hashrate_match.group(1))
            if hashrate_match.group(2) == "kH/s":
                rate *= 1000
            self.current_hashrate = rate
            self.hash_history.append(rate)
    
    def check_activity(self):
        """ตรวจสอบว่ามีการทำงานจริงหรือไม่"""
        while self.running:
            if time.time() - self.last_activity > 60:  # 1 นาทีไม่มีการทำงาน
                print("\033[1;33m⚠️ ไม่พบกิจกรรมขุดเกิน 1 นาที กำลังเริ่มใหม่...\033[0m")
                self.restart_miner()
                break
            time.sleep(10)
    
    def stop_mining(self):
        """หยุดการขุด"""
        if not self.running:
            return
            
        self.running = False
        self.shutdown_requested = True
        
        if self.miner_process:
            try:
                os.killpg(os.getpgid(self.miner_process.pid), signal.SIGTERM)
                self.miner_process.wait(timeout=10)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(os.getpgid(self.miner_process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            finally:
                self.miner_process = None
    
    def restart_miner(self):
        """เริ่มต้นระบบใหม่"""
        self.stop_mining()
        time.sleep(3)
        return self.start_mining()

def main():
    miner = VRSCMiner()
    signal.signal(signal.SIGINT, lambda s,f: miner.stop_mining())
    
    # ตรวจสอบ config ก่อนเริ่ม
    if not os.path.exists("config.json"):
        print("\033[1;31mไม่พบไฟล์ config.json!\033[0m")
        return
    
    print("\033[1;36m" + "="*50)
    print("🚀 VRSC CPU Miner Controller")
    print("="*50 + "\033[0m")
    
    if miner.start_mining():
        try:
            while miner.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\033[1;33mกำลังหยุดการขุด...\033[0m")
        finally:
            miner.stop_mining()
    else:
        print("\033[1;31mไม่สามารถเริ่มการขุดได้\033[0m")
    
    print("\033[1;36mปิดโปรแกรมเรียบร้อยแล้ว\033[0m")

if __name__ == "__main__":
    main()
