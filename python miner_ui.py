import json
import time
import random
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

def load_config():
    """โหลดการตั้งค่าจากไฟล์ config.json"""
    try:
        with open('config.json') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(Fore.RED + "Error: config.json not found!")
        exit(1)
    except json.JSONDecodeError:
        print(Fore.RED + "Error: Invalid config.json format!")
        exit(1)

def display_config(config):
    """แสดงการตั้งค่าอย่างสวยงาม"""
    print(Fore.CYAN + "\n╔════════════════════════════════════════════╗")
    print(Fore.CYAN + "║          " + Fore.YELLOW + "VRSC MINER CONFIGURATION" + Fore.CYAN + "          ║")
    print(Fore.CYAN + "╠════════════════════════════════════════════╣")
    
    config_items = [
        ("1. Wallet Address", config.get("user", "Not specified")),
        ("2. Miner Name", config.get("miner-name", "Anonymous")),
        ("3. Password", config.get("pass", "x")),
        ("4. Threads", config.get("threads", "Auto")),
        ("5. Pool URL", config["pools"][0]["url"] if config.get("pools") else "Not specified")
    ]
    
    for item, value in config_items:
        print(Fore.CYAN + f"║ {Fore.GREEN}{item:<18}{Fore.WHITE}: {value:<24} ║")
    
    print(Fore.CYAN + "╚════════════════════════════════════════════╝\n")

def simulate_mining(config):
    """จำลองการขุดเหรียญด้วยการแสดงผลที่สวยงาม"""
    threads = config.get("threads", 4)
    accepted = 0
    
    print(Fore.GREEN + "🚀 Starting VRSC Miner with following parameters:")
    print(Fore.YELLOW + f"• Threads: {threads} | Pool: {config['pools'][0]['url']}")
    print(Fore.CYAN + "="*60)
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        diff = random.randint(150000, 400000)
        accepted += 1
        
        # สร้างสีสันให้แต่ละเธรด
        thread_colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, 
                        Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTRED_EX]
        
        # แสดงผลแบบสวยงาม
        print(Fore.LIGHTBLUE_EX + f"[{timestamp}] " + 
              Fore.LIGHTGREEN_EX + f"✅ Accepted: {accepted} " + 
              Fore.LIGHTYELLOW_EX + f"| Diff: {diff:,}")
        
        total_hash = 0
        for i in range(1, threads+1):
            thread_hash = 400 + random.random() * 600
            total_hash += thread_hash
            print(Fore.LIGHTBLUE_EX + f"[{timestamp}] " + 
                  thread_colors[i%8] + f"⚙️ Thread {i}: " + 
                  Fore.LIGHTCYAN_EX + f"{thread_hash:.2f} kN/s")
        
        print(Fore.LIGHTBLUE_EX + f"[{timestamp}] " + 
              Fore.LIGHTGREEN_EX + "⚡ Total: " + 
              Fore.LIGHTWHITE_EX + f"{total_hash:.2f} kN/s " + 
              Fore.LIGHTYELLOW_EX + "| " + 
              Fore.LIGHTMAGENTA_EX + "Stratum: {config['pools'][0]['name']}")
        
        # แสดงความคืบหน้าแบบกราฟิก
        progress = int((accepted % 20) * 5)
        print(Fore.LIGHTBLUE_EX + "[" + "■"*progress + " "*(100-progress) + "] " +
              f"{progress}%")
        
        time.sleep(random.uniform(0.8, 1.5))

def main():
    """ฟังก์ชันหลัก"""
    config = load_config()
    display_config(config)
    
    print(Fore.YELLOW + "Press any key to start mining..." + Style.RESET_ALL)
    input()
    
    try:
        simulate_mining(config)
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Mining stopped by user. Goodbye!")

if __name__ == "__main__":
    main()
