import subprocess
import re
import time

# ANSI สีข้อความ
class Style:
    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"

def highlight_keywords(line):
    # ALARM
    if "alarm" in line.lower():
        line = f"{Style.RED}⚠️ {line.strip()}{Style.RESET}"
    # Difficulty
    line = re.sub(r'(diff(?:iculty)?(?: changed)?(?: to)?\s*[0-9.]+)',
                  lambda m: f"{Style.YELLOW}{m.group(1)}{Style.RESET}", line, flags=re.IGNORECASE)
    # accepted
    line = re.sub(r'(accepted)', f"{Style.YELLOW}✅ \\1{Style.RESET}", line, flags=re.IGNORECASE)
    # rejected
    line = re.sub(r'(rejected)', f"{Style.RED}❌ \\1{Style.RESET}", line, flags=re.IGNORECASE)
    # new job
    line = re.sub(r'(new job)', f"{Style.YELLOW}📥 \\1{Style.RESET}", line, flags=re.IGNORECASE)
    # stratum
    line = re.sub(r'(stratum)', f"{Style.YELLOW}🔌 \\1{Style.RESET}", line, flags=re.IGNORECASE)
    # speed (เฉพาะ > 2.0 MH/s)
    mh_match = re.search(r'([0-9.]+)\s*mH/s', line, re.IGNORECASE)
    if mh_match:
        mh_val = float(mh_match.group(1))
        if mh_val >= 2.0:
            line = re.sub(r'([0-9.]+\s*mH/s)', f"{Style.CYAN}⚡ \\1{Style.RESET}", line, flags=re.IGNORECASE)
    return line

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
            if not line:
                continue
            # ไม่ต้องกรอง temp แต่สามารถกรองได้ถ้าต้องการ
            # if 'temp' in line.lower(): continue
            highlighted = highlight_keywords(line)
            print(highlighted)
            time.sleep(0.01)
    except KeyboardInterrupt:
        process.terminate()
        print("\n⛔ ยกเลิกการขุดแล้ว")
    except Exception as e:
        process.terminate()
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    run_monitor()
