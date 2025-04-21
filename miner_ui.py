import subprocess
import re

# สีสำหรับตกแต่งข้อความ (ANSI Escape Codes)
class Style:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

def format_line(line):
    # ลบ newline ทิ้งก่อน
    line = line.strip()

    # ถ้ามีคำว่า "accepted"
    if "accepted" in line.lower():
        return f"{Style.GREEN}{Style.BOLD}[✓] {line}{Style.RESET}"

    # ถ้ามีคำว่า "MH/s"
    elif "mh/s" in line.lower():
        return f"{Style.CYAN}{Style.BOLD}[Speed] {line}{Style.RESET}"

    # การเชื่อมต่อหรือสถานะ
    elif "stratum" in line.lower() or "starting" in line.lower():
        return f"{Style.YELLOW}[Status] {line}{Style.RESET}"

    # ค่าอื่น ๆ
    return f"{Style.DIM}{line}{Style.RESET}"

def run_ccminer():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    print(f"{Style.BOLD}{Style.CYAN}เริ่มต้นการขุด VRSC...{Style.RESET}\n")

    try:
        for line in process.stdout:
            # ข้ามบรรทัดที่มี temp หรือ temperature
            if re.search(r"(temp|temperature)", line, re.IGNORECASE):
                continue

            formatted = format_line(line)
            print(formatted)
    except KeyboardInterrupt:
        process.terminate()
        print(f"\n{Style.RED}หยุดการขุดแล้ว โดยผู้ใช้กด Ctrl+C{Style.RESET}")
    except Exception as e:
        print(f"{Style.RED}เกิดข้อผิดพลาด: {e}{Style.RESET}")
        process.terminate()

if __name__ == "__main__":
    run_ccminer()
