import subprocess
import re
import time
import os

class Style:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = f"""
{Style.CYAN}{Style.BOLD}
   __      ______  _____  _____   _____  __  __ _____  ____  
   \ \    / / __ \|  __ \|  __ \ / ____||  \/  |  __ \|  _ \ 
    \ \  / / |  | | |__) | |__) | (___  | \  / | |__) | | | |
     \ \/ /| |  | |  _  /|  ___/ \___ \ | |\/| |  _  /| | | |
      \  / | |__| | | \ \| |     ____) || |  | | | \ \| |_| |
       \/   \____/|_|  \_\_|    |_____/ |_|  |_|_|  \_\____/ 
{Style.RESET}
    Monitoring ccminer | VRSC | Clean & Cool Output
    Press Ctrl+C to stop.
    -------------------------------------------------------
"""
    print(banner)

def format_line(line):
    line = line.strip()

    if "accepted" in line.lower():
        return f"{Style.GREEN}[✓] {line}{Style.RESET}"
    elif "mh/s" in line.lower():
        return f"{Style.CYAN}[Speed] {line}{Style.RESET}"
    elif "stratum" in line.lower() or "starting" in line.lower():
        return f"{Style.YELLOW}[Status] {line}{Style.RESET}"
    return f"{Style.DIM}{line}{Style.RESET}"

def run_ccminer():
    clear_screen()
    print_banner()

    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    try:
        for line in process.stdout:
            if re.search(r"(temp|temperature)", line, re.IGNORECASE):
                continue
            print(format_line(line))
    except KeyboardInterrupt:
        process.terminate()
        print(f"\n{Style.RED}คุณได้หยุดการขุดแล้ว ขอบคุณที่ใช้งาน!{Style.RESET}")
    except Exception as e:
        print(f"{Style.RED}เกิดข้อผิดพลาด: {e}{Style.RESET}")
        process.terminate()

if __name__ == "__main__":
    run_ccminer()
