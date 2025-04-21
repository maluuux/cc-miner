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

# คำที่ต้องการแทนที่ พร้อมข้อความใหม่
custom_keywords = {
    "different": "⚠️ ค่าความยากเปลี่ยนแล้ว!",
    "new job": "📥 งานใหม่เข้ามา",
    "stratum": "🔌 เชื่อมต่อ pool แล้ว",
    "accepted": "✅ แชร์สำเร็จ!",
    "rejected": "❌ แชร์ถูกปฏิเสธ!",
}

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

            # ตรวจสอบคำที่ต้องแทน
            for keyword, replacement in custom_keywords.items():
                if keyword in line.lower():
                    output = f"🕒 {now}   {color_text(replacement, Style.YELLOW)}"
                    break

            # ตรวจจับ speed (mh/s)
            if not output and "mh/s" in line.lower():
                output = f"🕒 {now}   ⚡ {color_text(line, Style.CYAN)}"

            # แสดงผล
            if output:
                print(output)
                time.sleep(0.1)

    except KeyboardInterrupt:
        process.terminate()
        print(color_text("\n⛔ หยุดโปรแกรมโดยผู้ใช้", Style.YELLOW))
    except Exception as e:
        process.terminate()
        print(color_text(f"เกิดข้อผิดพลาด: {e}", Style.RED))

if __name__ == "__main__":
    run_miner_monitor()
