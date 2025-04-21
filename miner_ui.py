import subprocess

def run_ccminer():
    process = subprocess.Popen(
        ['./start.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    try:
        for line in process.stdout:
            # ข้ามบรรทัดที่มีคำว่า temperature หรือ temp
            if any(word in line.lower() for word in ['temperature', 'temp']):
                continue
            print(line, end='')
    except KeyboardInterrupt:
        process.terminate()
        print("\nหยุดการขุดเรียบร้อยแล้ว")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        process.terminate()

if __name__ == "__main__":
    run_ccminer()
