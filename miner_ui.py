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

            # Speed line (MH/s)
            if "mh/s" in line.lower():
                output = f"🕒 {now}   ⚡ {color_text(line, Style.CYAN)}"

            # Accepted share
            elif "accepted" in line.lower():
                output = f"🕒 {now}   ✅ {color_text(line, Style.GREEN)}"

            # Rejected share
            elif "rejected" in line.lower():
                output = f"🕒 {now}   ❌ {color_text(line, Style.RED)}"

            # Difficulty change or 'different'
            elif "different" in line.lower() or "diff" in line.lower():
                output = f"🕒 {now}   ⚠️  {color_text(line, Style.YELLOW)}"

            # Other stratum / new job
            elif "stratum" in line.lower() or "new job" in line.lower():
                output = f"🕒 {now}   ℹ️  {line}"

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
