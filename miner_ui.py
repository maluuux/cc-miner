import subprocess
import re
import time
from datetime import datetime

# ANSI styles
Style = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "date": "\033[48;5;57m\033[97m",
    "status": "\033[48;5;24m\033[97m",
    "speed": "\033[48;5;33m\033[97m",
    "share": "\033[48;5;28m\033[97m",
}

def format_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_line(tag, content, style):
    print(f"{style} {tag:<10} {content} {Style['reset']}")

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
                continue  # ข้ามอุณหภูมิ

            printed = False

            # Time stamp (แสดงทุกบรรทัดใหม่ที่สำคัญ)
            print_line("[ DATE ]", format_time(), Style["date"])

            if "accepted" in line.lower():
                ms = re.search(r"(.*?)", line)
                detail = f"Accepted {ms.group(0)}" if ms else "Accepted"
                print_line("[ SHARE ]", detail, Style["share"])
                printed = True

            elif "mh/s" in line.lower():
                print_line("[ SPEED ]", line, Style["speed"])
                printed = True

            elif "stratum" in line.lower() or "new job" in line.lower():
                print_line("[ STATUS ]", line, Style["status"])
                printed = True

            if printed:
                print()  # เว้นบรรทัดระหว่างชุดข้อมูล
                time.sleep(0.2)

    except KeyboardInterrupt:
        process.terminate()
        print("\n\033[93mขุดเสร็จแล้วครับ ขอบคุณที่ใช้งาน!\033[0m")
    except Exception as e:
        process.terminate()
        print(f"\033[91mเกิดข้อผิดพลาด: {e}\033[0m")

if __name__ == "__main__":
    run_monitor()
