import subprocess
import re

cmd = ["bash", "start.sh"]

def extract_info(line):
    if "Connected to" in line:
        return "[เชื่อมต่อพูล] " + line.strip()
    elif "New job" in line:
        return "[งานใหม่] มีงานขุดใหม่"
    elif "Accepted" in line:
        return "[ขุดสำเร็จ] ยืนยันผลลัพธ์"
    elif "Hashrate:" in line:
        match = re.search(r"Hashrate:\s+([\d.]+)\s*H/s", line)
        if match:
            return f"[ความเร็วรวม] {match.group(1)} H/s"
    elif re.search(r"T\d+:", line):
        match = re.search(r"(T\d+):\s*([\d.]+)\s*H/s", line)
        if match:
            thread = match.group(1)
            speed = match.group(2)
            return f"[{thread}] ความเร็ว {speed} H/s"
    return None

with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as process:
    try:
        for line in process.stdout:
            output = extract_info(line)
            if output:
                print(output)
    except KeyboardInterrupt:
        print("\n[ระบบ] หยุดการขุดแล้ว")
        process.terminate()
