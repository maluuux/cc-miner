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

# กำหนดคำสำคัญและคำแทน
custom_keywords = {
    "new job": "📥 งานใหม่เข้ามา",
    "stratum": "🔌 เชื่อมต่อ pool แล้ว",
    "accepted": "✅ แชร์สำเร็จ!",
    "rejected": "❌ แชร์ถูกปฏิเสธ!",
}

# pattern ตรวจ speed
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

            # ตรวจจับ ALARM แล้วแสดงข้อความเต็ม พร้อมสีแดง
            if "alarm" in line.lower():
                output = f"🕒 {now}   {color_text('⚠️ แจ้งเตือน: ' + line, Style.RED)}"

            # ตรวจจับ difficulty หรือ different พร้อมค่า
            elif "diff" in line.lower():
                diff_match = re.search(r'diff(?:iculty)?(?: changed)?(?: to)?\s*([0-9.]+)', line.lower())
                if diff_match:
                    diff_value = diff_match.group(1)
                    output = f"🕒 {now}   ⚠️ ค่าความยากถูกปรับเป็น {color_text(diff_value, Style.YELLOW)}"

            # ตรวจจับคำแทนทั่วไป
            elif not output:
                for keyword, replacement in custom_keywords.items():
                    if keyword in line.lower():
                        output = f"🕒 {now}   {color_text(replacement, Style.YELLOW)}"
                        break

            # ตรวจจับ speed ที่มากกว่า 2.0 MH/s
            if not output:
                for pattern in speed_patterns:
                    match = re.search(pattern, line.lower())
                    if match:
                        speed_val = float(match.group(1))
                        unit = match.group(2).upper() if match.group(2) else ""
                        if unit == "M" and speed_val >= 2.0:
                            speed_text = f"{speed_val} MH/s"
                            output = f"🕒 {now}   ⚡ {color_text(speed_text, Style.CYAN)}"
                            break

            if output:
                print(output)
                time.sleep(0.05)

    except KeyboardInterrupt:
        process.terminate()
        print(color_text("\n⛔ ยกเลิกการขุดแล้ว", Style.YELLOW))
    except Exception as e:
        process.terminate()
        print(color_text(f"เกิดข้อผิดพลาด: {e}", Style.RED))

if __name__ == "__main__":
    run_miner_monitor()
