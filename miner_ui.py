import time
from datetime import datetime
import sys
import re
from collections import deque
import subprocess
from threading import Thread

class MobileMinerDisplay:
    def __init__(self):
        self.hash_history = deque(maxlen=10)
        self.start_time = time.time()
        self.total_shares = 0
        self.accepted_shares = 0
        self.current_hashrate = 0
        self.cpu_cores = self.detect_cpu_cores()
        self.miner_process = None
        self.running = False
        
    def detect_cpu_cores(self):
        """ตรวจสอบจำนวน CPU cores โดยอัตโนมัติ"""
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except:
            return 4  # ค่าเริ่มต้นถ้าไม่สามารถตรวจสอบได้
    
    def clear_screen(self):
        """ล้างหน้าจอ"""
        sys.stdout.write("\033[H\033[J")
    
    def display_header(self):
        """แสดงส่วนหัวโปรแกรม"""
        print("\033[1;36m")  # สีฟ้าเข้ม
        print("══════════════════════════════════════")
        print(f"🛠️ VRSC CPU Miner - {self.cpu_cores} Threads 🛠️")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("══════════════════════════════════════\033[0m")
    
    def process_line(self, line):
        """ประมวลผลแต่ละบรรทัดจาก miner"""
        line = line.strip()
        if not line:
            return
            
        if "accepted" in line:
            self.total_shares += 1
            self.accepted_shares += 1
            diff_match = re.search(r'diff (\d+)', line)
            hashrate_match = re.search(r'(\d+\.\d+) kN/s', line)
            
            if hashrate_match:
                self.current_hashrate = float(hashrate_match.group(1))
                self.hash_history.append(self.current_hashrate)
            
            print(f"\033[1;32m✔️ ACCEPTED SHARE #{self.accepted_shares}")
            print(f"  ├─ Difficulty: {int(diff_match.group(1)):,}" if diff_match else "  ├─ Difficulty: N/A")
            print(f"  └─ Hashrate: {self.current_hashrate:,.2f} kN/s\033[0m")
        
        elif "CPU" in line and "Hashing" in line:
            core_match = re.search(r'CPU T(\d+):', line)
            hashrate_match = re.search(r'(\d+\.\d+) kN/s', line)
            
            if hashrate_match:
                self.current_hashrate = float(hashrate_match.group(1))
                self.hash_history.append(self.current_hashrate)
            
            if core_match:
                print(f"\033[1;34m🔧 CORE {core_match.group(1)} ACTIVE")
                print(f"  └─ Speed: {self.current_hashrate:,.2f} kN/s\033[0m")
        
        elif "difficulty" in line:
            diff_match = re.search(r'difficulty set to (\d+)', line)
            if diff_match:
                print(f"\033[1;33m🔄 DIFFICULTY UPDATED: {diff_match.group(1)}\033[0m")
    
    def display_stats(self):
        """แสดงสถิติการทำงาน"""
        avg_hash = sum(self.hash_history)/len(self.hash_history) if self.hash_history else 0
        uptime = int(time.time() - self.start_time)
        
        print("\033[1;36m──────────────────────────────────────\033[0m")
        print(f"\033[1;35m📊 STATS: {self.accepted_shares}/{self.total_shares} Shares")
        print(f"⚡ AVG: {avg_hash/1000:,.2f} kH/s │ CURRENT: {self.current_hashrate/1000:,.2f} kH/s")
        print(f"🕒 UPTIME: {uptime//3600}h {(uptime%3600)//60}m {uptime%60}s\033[0m")
        print("\n")

    def start_miner(self, miner_command):
        """เริ่มกระบวนการขุด"""
        self.running = True
        self.miner_process = subprocess.Popen(
            miner_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True
        )
        
        # Thread สำหรับอ่านผลลัพธ์
        Thread(target=self.read_output, daemon=True).start()
    
    def read_output(self):
        """อ่านผลลัพธ์จาก miner"""
        while self.running and self.miner_process.poll() is None:
            line = self.miner_process.stdout.readline()
            if line:
                self.clear_screen()
                self.display_header()
                self.process_line(line)
                self.display_stats()
        
        self.running = False

    def stop_miner(self):
        """หยุดกระบวนการขุด"""
        self.running = False
        if self.miner_process:
            self.miner_process.terminate()
            self.miner_process.wait()

if __name__ == "__main__":
    display = MobileMinerDisplay()
    
    try:
        # ตัวอย่างคำสั่งเริ่ม miner - แก้ไขตาม config ของคุณ
        miner_cmd = "./staer.sh"
        
        display.start_miner(miner_cmd)
        
        # รอจนกว่าจะหยุดโดยผู้ใช้
        while display.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nกำลังหยุด miner...")
        display.stop_miner()
        print("หยุดการทำงานเรียบร้อยแล้ว")
