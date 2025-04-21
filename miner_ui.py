import subprocess
import re
import time
from datetime import datetime

# ANSI สีตัวอักษรเท่านั้น (ไม่มีพื้นหลัง)
Style = {
    "reset": "\033[0m",
    "date": "\033[96m",
    "status": "\033[94m",
    "speed": "\033[92m",
    "share": "\033[93m",
    "reject": "\033[91m",
    "highlight": "\033[93m",  # สำหรับคำว่า "different"
}

def format_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_line(tag, content, color):
    print(f"{color}{tag:<10} {content}{Style['reset']}")

def run_monitor():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    try:
        for line in process.stdout:
            line = line.strip()

            if re.search(r"(temp|temperature)", line, re.IGNORECASE):
                continue  # ข้ามบรรทัดที่ไม่ต้องการ

            # แสดงเวลา
            print_line("[DATE]", format_time(), Style["date"])

            # คำว่า different
            if "different" in line.lower():
                # ไฮไลต์เฉพาะคำว่า different
                line = re.sub(r"(different)", f"{Style['highlight']}\\1{Style['reset']}", line, flags=re.IGNORECASE)
                print_line("[NOTICE]", line, Style["highlight"])
            
            # share accepted
            elif "accepted" in line.lower():
                print_line("[SHARE]", line, Style["share"])

            # rejected share
            elif "rejected" in line.lower():
                print_line("[REJECT]", line, Style["reject"])

            # speed line
            elif "mh/s" in line.lower():
                print_line("[SPEED]", line, Style["speed"])

            # stratum หรือสถานะ
            elif "stratum" in line.lower() or "new job" in line.lower():
                print_line("[STATUS]", line, Style["status"])

            # บรรทัดใหม่คั่น
            print()

            time.sleep(0.2)

    except KeyboardInterrupt:
        process.terminate()
        print("\n\033[93mยกเลิกการขุดแล้ว ขอบคุณที่ใช้งานครับ!\033[0m")
    except Exception as e:
        process.terminate()
        print(f"\033[91mเกิดข้อผิดพลาด: {e}\033[0m")

if __name__ == "__main__":
    run_monitor()
