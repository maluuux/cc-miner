import subprocess
import re
import os
import time

# Custom styles for background color and text
Style = {
    "reset": "\033[0m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "purple": "\033[95m",
    "bg_black": "\033[48;5;235m",
    "bg_green": "\033[48;5;22m",
    "bg_cyan": "\033[48;5;38m",
    "bg_yellow": "\033[48;5;220m",
    "bg_red": "\033[48;5;196m",
    "bold": "\033[1m"
}

shares = []
speeds = []
status_lines = []

def clear():
    os.system('clear')

# Function to highlight the word "different" in yellow
def highlight_different(text):
    return re.sub(r"\bdifferent\b", f"{Style['yellow']}{Style['bg_yellow']}different{Style['reset']}", text)

def print_ui():
    clear()
    print(f"{Style['bg_purple']} {Style['bold']}Date: {time.strftime('%Y-%m-%d %H:%M:%S')} {Style['reset']}")
    print(f"{Style['bg_cyan']}━━━━━━━━━━━━━━━━━━━━━━━{Style['reset']}")
    print("  VRSC Miner - Live Status")
    print(f"{Style['bg_cyan']}━━━━━━━━━━━━━━━━━━━━━━━{Style['reset']}")

    # Print last 5 share accepted logs
    for s in shares[-5:]:
        print(f"{Style['bg_green']} {Style['green']}[✓] {highlight_different(s)} {Style['reset']}")

    # Print the latest speed logs with cyan background
    if speeds:
        print(f"\n{Style['bg_cyan']}[Speed]{Style['reset']}")
        for sp in speeds[-3:]:
            print(f"{Style['bg_cyan']}  {highlight_different(sp)} {Style['reset']}")

    # Print the status messages with yellow background
    if status_lines:
        print(f"\n{Style['bg_yellow']}[Status]{Style['reset']}")
        for line in status_lines[-3:]:
            print(f"{Style['bg_yellow']}  {highlight_different(line)} {Style['reset']}")

    print(f"{Style['bg_cyan']}━━━━━━━━━━━━━━━━━━━━━━━")
    print(" Press Ctrl+C to stop mining")
    print(f"{Style['bg_cyan']}━━━━━━━━━━━━━━━━━━━━━━━{Style['reset']}")

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
            time.sleep(0.05)  # Update every 50ms

    except KeyboardInterrupt:
        process.terminate()
        print(f"{Style['yellow']}หยุดการขุดแล้ว ขอบคุณที่ใช้งานครับ{Style['reset']}")
    except Exception as e:
        process.terminate()
        print(f"{Style['red']}เกิดข้อผิดพลาด: {e}{Style['reset']}")

if __name__ == "__main__":
    run_monitor()
