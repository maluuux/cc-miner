import subprocess
import re
import time

# ANSI สีข้อความ
class Style:
    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"

# กรองและตกแต่งเฉพาะข้อความสำคัญ
def highlight_important(line):
    # ALARM
    if "alarm" in line.lower():
        return f"{Style.RED}⚠️  แจ้งเตือน: {line.strip()}{Style.RESET}"

    # New Job
    if "new job" in line.lower():
        return f"{Style.YELLOW}📥 งานใหม่: {line.strip()}{Style.RESET}"

    # Accepted
    if "accepted" in line.lower():
        return f"{Style.GREEN}✅ แชร์สำเร็จ: {line.strip()}{Style.RESET}"

    # Rejected
    if "rejected" in line.lower():
        return f"{Style.RED}❌ แชร์ถูกปฏิเสธ: {line.strip()}{Style.RESET}"

    # Difficulty
    if "diff" in line.lower():
        return f"{Style.YELLOW}🎯 ความยาก: {line.strip()}{Style.RESET}"

    # ความเร็ว MH/s
    if "mh/s" in line.lower():
        mh_match = re.search(r'([0-9.]+)\s*mH/s', line, re.IGNORECASE)
        if mh_match:
            mh = float(mh_match.group(1))
            if mh >= 2.0:
                return f"{Style.CYAN}⚡ ความเร็ว: {mh_match.group(1)} MH/s{Style.RESET}"

    return None  # ไม่แสดงถ้าไม่ใช่ข้อมูลสำคัญ

def run_clean_monitor():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            highlight = highlight_important(line)
            if highlight:
                print(highlight)
                time.sleep(0.01)
    except KeyboardInterrupt:
        process.terminate()
        print("\n⛔ ยกเลิกการขุดแล้ว")
    except Exception as e:
        process.terminate()
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    run_clean_monitor()
