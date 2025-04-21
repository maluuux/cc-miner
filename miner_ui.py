import subprocess
import re
import time
from datetime import datetime

# ANSI สีข้อความ
class Style:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def color_text(text, color):
    return f"{color}{text}{Style.RESET}"

def run_miner_monitor():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if not line or re.search(r"temp|temperature", line, re.IGNORECASE):
                continue

            now = get_time()
            output = ""

            elif "different" in line.lower() or "diff" in line.lower():
            # แทนที่คำว่า 'different' ด้วยข้อความใหม่
                custom_message = "⚠️ ค่าความยากเปลี่ยนแล้ว!"  # <<== คุณสามารถเปลี่ยนข้อความนี้ได้
                output = f"{color_text(custom_message, Style.YELLOW)}"


            if output:
                print(output)
                time.sleep(0.1)

    except KeyboardInterrupt:
        process.terminate()
        print(color_text("\n⛔ ยกเลิกการขุดแล้ว", Style.YELLOW))
    except Exception as e:
        process.terminate()
        print(color_text(f"เกิดข้อผิดพลาด: {e}", Style.RED))

if __name__ == "__main__":
    run_miner_monitor()
