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

# กำหนดคำที่จะใช้แทน พร้อมข้อความที่ต้องการแสดง
custom_keywords = {
    "diff": "⚠️ ค่าความยากเปลี่ยนแล้ว!",
    "new job": "📥 งานใหม่เข้ามา",
    "stratum": "🔌 เชื่อมต่อ pool แล้ว",
    "accepted": "✅ แชร์สำเร็จ!",
    "rejected": "❌ แชร์ถูกปฏิเสธ!",
}

# pattern ตรวจจับค่า speed แบบกว้างขึ้น
speed_patterns = [
    r"speed.*?([0-9.]+)\s*(k|m|g)?h/s",
    r"([0-9.]+)\s*(k|m|g)?h/s",
    r"total:\s*([0-9.]+)\s*(k|m|g)?h/s"
]

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

            # จับคำแทนก่อน
            for keyword, replacement in custom_keywords.items():
                if keyword in line.lower():
                    output = f"🕒 {now}   {color_text(replacement, Style.YELLOW)}"
                    break

            # ตรวจ speed
            if not output:
                for pattern in speed_patterns:
                    match = re.search(pattern, line.lower())
                    if match:
                        speed_val = match.group(1)
                        unit = match.group(2).upper() + "H/s" if match.group(2) else "H/s"
                        speed_text = f"{speed_val} {unit}"
                        output = f"🕒 {now}   ⚡ {color_text(speed_text, Style.CYAN)}"
                        break

            # แสดงผล
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
