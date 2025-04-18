import time
from datetime import datetime
import sys
import re
import os
import signal
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
        self.shutdown_requested = False
        
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

    def start_miner(self):
        """เริ่มกระบวนการขุดโดยใช้ไฟล์ start.sh"""
        if not os.path.exists("./start.sh"):
            print("\033[1;31mERROR: ไม่พบไฟล์ start.sh ในโฟลเดอร์ปัจจุบัน\033[0m")
            return False
            
        try:
            # รีเซ็ตค่าสถิติเมื่อเริ่มใหม่
            self.__init__()  
            
            # ทำให้ไฟล์ start.sh สามารถรันได้
            os.chmod("./start.sh", 0o755)
            
            self.miner_process = subprocess.Popen(
                ["./start.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                preexec_fn=os.setsid  # สร้าง process group ใหม่
            )
            
            self.running = True
            Thread(target=self.read_output, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"\033[1;31mERROR: ไม่สามารถรันไฟล์ start.sh ได้: {e}\033[0m")
            return False
    
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
        """หยุดกระบวนการขุดอย่างปลอดภัย"""
        if not self.running:
            return
            
        self.running = False
        self.shutdown_requested = True
        
        if self.miner_process:
            try:
                # ส่งสัญญาณ SIGTERM ไปยังทั้ง process group
                os.killpg(os.getpgid(self.miner_process.pid), signal.SIGTERM)
                self.miner_process.wait(timeout=10)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    # ถ้ายังไม่หยุด ส่ง SIGKILL
                    os.killpg(os.getpgid(self.miner_process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            except Exception as e:
                print(f"\033[1;33mWARNING: {e}\033[0m")
            finally:
                self.miner_process = None

    def restart_miner(self):
        """เริ่มต้น miner ใหม่"""
        self.stop_miner()
        time.sleep(2)  # รอให้กระบวนการเก่าหยุดอย่างแน่นอน
        return self.start_miner()

def main():
    display = MobileMinerDisplay()
    
    def signal_handler(sig, frame):
        print("\n\033[1;33mได้รับสัญญาณหยุด...\033[0m")
        display.stop_miner()
        sys.exit(0)
    
    # ตั้งค่าตัวจับสัญญาณ
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("\033[1;36mกำลังเริ่มต้น VRSC Miner...\033[0m")
        if display.start_miner():
            print("\033[1;32mเริ่มต้น miner สำเร็จ! กด Ctrl+C เพื่อหยุด\033[0m")
            
            while display.running:
                # ตัวอย่าง: สามารถเพิ่มเงื่อนไข restart อัตโนมัติที่นี่
                time.sleep(1)
                
    except Exception as e:
        print(f"\033[1;31mเกิดข้อผิดพลาด: {e}\033[0m")
        
    finally:
        if display.running:
            display.stop_miner()
        print("\033[1;36mปิดโปรแกรมเรียบร้อยแล้ว\033[0m")

if __name__ == "__main__":
    main()
