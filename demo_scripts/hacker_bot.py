import requests
import time
from colorama import Fore, Style, init

init(autoreset=True)
# CLOUD CONFIG: Target the internal proxy
PROXY_URL = "http://127.0.0.1:8000"

def log(source, msg, color=Fore.WHITE):
    print(f"{color}[{source}] {msg}{Style.RESET_ALL}")

def run_attack_sequence():
    print(Fore.RED + "\n--- INITIATING ATTACK SEQUENCE ---\n")

    # PHASE 1: INITIAL SUCCESS
    target = "/admin/login"
    log("BOT", f"Targeting {target}...", Fore.YELLOW)
    
    try:
        response = requests.get(f"{PROXY_URL}{target}")
        if response.status_code == 200:
            log("SUCCESS", f"✅ Connected. Server Response: {response.json()}", Fore.GREEN)
        else:
            log("FAIL", "Connection failed.", Fore.RED)
    except:
        log("ERROR", "Proxy unreachable.", Fore.RED)

    # PHASE 2: WAIT FOR MUTATION
    wait_time = 26
    log("BOT", f"Analyzing vulnerabilities (Waiting {wait_time}s)...", Fore.CYAN)
    for i in range(wait_time, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")

    # PHASE 3: REPLAY ATTACK (The Trap)
    stale_target = "/admin/login_old_token_x99" 
    log("BOT", f"Replaying attack on captured endpoint: {stale_target}...", Fore.YELLOW)
    
    try:
        response = requests.get(f"{PROXY_URL}{stale_target}")
        data = response.json()
        
        if "account_flag" in str(data):
            log("SUCCESS", "✅ 200 OK - DATABASE DOWNLOADED", Fore.GREEN)
            log("DATA", f"Payload: {data}", Fore.GREEN)
            print(Fore.RED + "\n[SYSTEM ALERT] WAIT... THE DATA IS FAKE! HONEYPOT DETECTED!" + Style.RESET_ALL)
        else:
            log("INFO", f"Response: {data}", Fore.WHITE)
            
    except Exception as e:
        log("ERROR", f"Attack Failed: {e}", Fore.RED)

if __name__ == "__main__":
    while True:
        run_attack_sequence()
        print(Fore.WHITE + "\nResting for 5 seconds...\n")
        time.sleep(5)