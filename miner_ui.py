import subprocess
import re
import os
import time

Style = {
    "reset": "\033[0m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "bold": "\033[1m",
    "dim": "\033[2m"
}

shares = []
speeds = []
status_lines = []

def clear():
    os.system('clear')

def print_ui():
    clear()
    print(f"{Style['cyan']}━━━━━━━━━━━━━━━━━━━━━━━")
    print("  VRSC Miner - Live Status")
    print("━━━━━━━━━━━━━━━━━━━━━━━" + Style['reset'])

    for s in shares[-5:]:
        print(f"{Style['green']}[✓] {s}{Style['reset']}")

    if speeds:
        print(f"\n{Style['cyan']}[Speed]{Style['reset']}")
        for sp in speeds[-3:]:
            print(f"  {sp}")

    if status_lines:
        print(f"\n{Style['yellow']}[Status]{Style['reset']}")
        for line in status_lines[-3:]:
            print(f"  {line}")

    print(f"{Style['cyan']}━━━━━━━━━━━━━━━━━━━━━━━")
    print(" Press Ctrl+C to stop mining")
    print("━━━━━━━━━━━━━━━━━━━━━━━" + Style['reset'])

def run_monitor():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    try:
        for line in process.stdout:
            line = line.strip()

            # ข้าม temperature
            if re.search(r"(temp|temperature)", line, re.IGNORECASE):
                continue

            # แยกหมวดหมู่
            if "accepted" in line.lower():
                shares.append(line)
            elif "mh/s" in line.lower():
                speeds.append(line)
            elif "stratum" in line.lower() or "new job" in line.lower():
                status_lines.append(line)

            print_ui()
            time.sleep(0.05)

    except KeyboardInterrupt:
        process.terminate()
        print(f"{Style['yellow']}หยุดการขุดแล้ว ขอบคุณที่ใช้งานครับ{Style['reset']}")
    except Exception as e:
        process.terminate()
        print(f"{Style['red']}เกิดข้อผิดพลาด: {e}{Style['reset']}")

if __name__ == "__main__":
    run_monitor()
