import requests
import threading
import time
import os
import random
import json
from colorama import Fore, Style, init

init(autoreset=True)

# Constants
LOG_FILE = "logs.txt"
PROXY_FILE = "proxies.txt"
LANG_EN_FILE = "lang_en.json"
LANG_TR_FILE = "lang_tr.json"

# Global variables
running = False
success_count = 0
fail_count = 0
bad_proxies = []
channel = ""
post_id = ""
threads = []
proxies = []
use_proxy = True
target_views = 0
lang = {}  # Current language dictionary
current_lang = "tr"  # Default language

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

def load_language(language="tr"):
    """Loads language file"""
    global lang, current_lang
    
    # Select language file based on language code
    lang_file = LANG_TR_FILE if language == "tr" else LANG_EN_FILE
    
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            lang = json.load(f)
        current_lang = language
    except FileNotFoundError:
        # If language file not found, create it with basic values
        if language == "tr":
            # Create Turkish language file with basic values from the code
            lang = {
                "menu_bot_start": "Bot Başlat",
                "menu_proxy_mgmt": "Proxy Yönetimi",
                "menu_logs": "Log Görüntüle",
                "menu_help": "Yardım",
                "menu_exit": "Çıkış"
                # ... More keys will be added in real file
            }
            with open(LANG_TR_FILE, 'w', encoding='utf-8') as f:
                json.dump(lang, f, ensure_ascii=False, indent=4)
        else:
            # Create English language file with basic values
            lang = {
                "menu_bot_start": "Start Bot",
                "menu_proxy_mgmt": "Proxy Management",
                "menu_logs": "View Logs",
                "menu_help": "Help",
                "menu_exit": "Exit"
                # ... More keys will be added in real file
            }
            with open(LANG_EN_FILE, 'w', encoding='utf-8') as f:
                json.dump(lang, f, ensure_ascii=False, indent=4)

def print_banner():
    """Displays the application banner"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{Fore.CYAN}
╔════════════════════════════════════════╗
║                                        ║            
║   ____     ____    _______    _____    ║
║  |  _ \   / __ \  |__   __|  / ____|   ║    
║  | |_) | | |  | |    | |    | (___     ║ 
║  |  _ <  | |  | |    | |     \___ \    ║ 
║  | |_) | | |__| |    | |     ____) |   ║ 
║  |____/   \____/     |_|    |_____/    ║ 
║                                        ║
║                 Telegram View Bot v1.1 ║
║                         Created by ONM ║
╚════════════════════════════════════════╝{Style.RESET_ALL}
""")

def print_menu(menu_items, title="MENU"):
    """Displays a formatted menu"""
    print(f"{Fore.CYAN}╔═════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║ {title.center(39)} ║")
    print(f"{Fore.CYAN}╠═════════════════════════════════════════╣")
    
    for idx, item in enumerate(menu_items, 1):
        color = Fore.GREEN if idx < len(menu_items) else Fore.RED
        print(f"{color}║ {idx}. {item.ljust(36)} ║")
    
    print(f"{Fore.CYAN}╚═════════════════════════════════════════╝")

def log(message):
    """Logs a message to both file and console"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

def load_proxies():
    """Loads proxies from file"""
    global proxies
    if not os.path.exists(PROXY_FILE):
        open(PROXY_FILE, 'w').close()
    with open(PROXY_FILE, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

def save_proxies():
    """Saves proxies to file"""
    with open(PROXY_FILE, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def fetch_data(proxy=None):
    """Fetches necessary data from Telegram"""
    try:
        headers = {
            'user-agent': random.choice(USER_AGENTS)
        }
        if proxy and use_proxy:
            r = requests.get(f'https://t.me/{channel}/{post_id}?embed=1', proxies={'https': f'http://{proxy}'}, headers=headers, timeout=10)
        else:
            r = requests.get(f'https://t.me/{channel}/{post_id}?embed=1', headers=headers, timeout=10)
        cookie = r.headers.get('set-cookie', '').split(';')[0]
        key = r.text.split('data-view="')[1].split('"')[0]
        if 'stel_ssid' not in cookie:
            return None
        return {'key': key, 'cookie': cookie}
    except Exception as e:
        proxy_text = lang["log_fetch_failed"].format(f"Proxy {proxy}" if proxy else "Direct")
        log(f"{Fore.RED}{proxy_text}")
        return None

def add_view(proxy=None, key=None, cookie=None):
    """Adds a view to the Telegram post"""
    global success_count, fail_count
    try:
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            'referer': f'https://t.me/{channel}/{post_id}?embed=1',
            'cookie': cookie,
            'user-agent': random.choice(USER_AGENTS)
        }
        if proxy and use_proxy:
            r = requests.get(f'https://t.me/{channel}/{post_id}?embed=1&view={key}', proxies={'https': f'http://{proxy}'}, headers=headers, timeout=10)
        else:
            r = requests.get(f'https://t.me/{channel}/{post_id}?embed=1&view={key}', headers=headers, timeout=10)
        if r.status_code == 200:
            success_count += 1
            success_text = lang["log_view_added"].format(f"Proxy {proxy}" if proxy else "Direct", success_count)
            log(f"{Fore.GREEN}{success_text}")
        else:
            fail_count += 1
            fail_text = lang["log_view_failed"].format(f"Proxy {proxy}" if proxy else "Direct", r.status_code)
            log(f"{Fore.RED}{fail_text}")
    except Exception as e:
        fail_count += 1
        error_text = lang["log_error"].format(f"Proxy {proxy}" if proxy else "Direct", str(e))
        log(f"{Fore.RED}{error_text}")
        if proxy:
            bad_proxies.append(proxy)

def view_worker(proxy=None):
    """Worker thread for adding views"""
    while running and success_count < target_views:
        data = fetch_data(proxy)
        if data:
            add_view(proxy, data['key'], data['cookie'])
        else:
            fetch_failed_text = lang["log_fetch_failed"].format(f"Proxy {proxy}" if proxy else "Direct")
            log(f"{Fore.RED}{fetch_failed_text}")
            if proxy:
                bad_proxies.append(proxy)
                break  # Exit if proxy fails
        time.sleep(1)

def start_bot():
    """Starts the view bot with user configurations"""
    global running, success_count, fail_count, bad_proxies, threads, use_proxy, target_views
    running = True
    success_count = 0
    fail_count = 0
    bad_proxies = []
    threads = []

    print_banner()
    print_menu([lang["prompt_proxy_use"], lang["prompt_proxy_dont_use"]], lang["title_proxy_choice"])
    proxy_choice = input(f"{Fore.YELLOW}{lang['prompt_selection']}")
    use_proxy = (proxy_choice == "1")

    try:
        print(f"\n{Fore.CYAN}{lang['title_target_views']}")
        print(f"{Fore.CYAN}══════════════════")
        target_views = int(input(f"{Fore.YELLOW}{lang['prompt_view_count']}"))
    except ValueError:
        print(f"{Fore.RED}[-] {lang['msg_invalid_number_input']}")
        input(f"{Fore.CYAN}{lang['prompt_continue']}")
        return

    log_start_text = lang["log_operation_start"].format(channel, post_id, lang["msg_active"] if use_proxy else lang["msg_inactive"], target_views)
    log(f"{Fore.CYAN}[!] {log_start_text}")

    # Progress display
    print(f"\n{Fore.CYAN}{lang['msg_starting']}")
    print(f"{Fore.CYAN}══════════════════")
    print(f"{Fore.YELLOW}{lang['msg_channel']}{channel}")
    print(f"{Fore.YELLOW}{lang['msg_post_id']}{post_id}")
    print(f"{Fore.YELLOW}{lang['msg_proxy']}{lang['msg_active'] if use_proxy else lang['msg_inactive']}")
    print(f"{Fore.YELLOW}{lang['msg_target']}{target_views}{lang['msg_views']}\n")

    if use_proxy:
        if not proxies:
            print(f"{Fore.RED}[-] {lang['msg_proxy_missing']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            return
            
        for proxy in proxies:
            if success_count >= target_views:
                break
            t = threading.Thread(target=view_worker, args=(proxy,))
            threads.append(t)
            t.start()
    else:
        # Create multiple direct threads for better performance
        for _ in range(5):  # Start 5 direct connection threads
            t = threading.Thread(target=view_worker)
            threads.append(t)
            t.start()

    # Progress monitor
    try:
        while running and success_count < target_views:
            print(f"\r{Fore.CYAN}[!] {lang['msg_progress']}{Fore.GREEN}{success_count}/{target_views} {Fore.YELLOW}({(success_count/target_views*100):.1f}%) {Fore.RED}{lang['msg_fail']}{fail_count}", end="")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] {lang['msg_operation_cancel']}")
        running = False

    # Wait for threads to finish
    running = False
    for t in threads:
        t.join(timeout=1)
    
    complete_text = f"{lang['msg_complete']}{lang['msg_success']}{success_count}, {lang['msg_fail']}{fail_count}, {lang['msg_failed_proxies']}{len(bad_proxies)}"
    print(f"\n\n{Fore.YELLOW}[!] {complete_text}")
    
    if use_proxy and bad_proxies:
        cleaning_text = lang["msg_cleaning"].format(len(bad_proxies))
        print(f"{Fore.YELLOW}[!] {cleaning_text}")
        for proxy in bad_proxies:
            if proxy in proxies:
                proxies.remove(proxy)
        save_proxies()
    
    input(f"{Fore.CYAN}{lang['msg_main_menu']}")

def proxy_menu():
    """Proxy management menu"""
    while True:
        print_banner()
        print_menu([
            lang["menu_proxy_add"],
            lang["menu_proxy_remove"],
            lang["menu_proxy_list"],
            lang["menu_proxy_bulk"],
            lang["menu_main"]
        ], lang["title_proxy"])
        
        choice = input(f"{Fore.YELLOW}{lang['prompt_selection']}")

        if choice == "1":
            proxy = input(f"{Fore.CYAN}{lang['prompt_proxy_add']}")
            if proxy and ":" in proxy:
                proxies.append(proxy)
                save_proxies()
                added_text = lang["msg_proxy_added"].format(proxy)
                print(f"{Fore.GREEN}[+] {added_text}")
            else:
                print(f"{Fore.RED}[-] {lang['msg_invalid_proxy']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            
        elif choice == "2":
            if not proxies:
                print(f"{Fore.RED}[-] {lang['msg_proxy_empty']}")
                input(f"{Fore.CYAN}{lang['prompt_continue']}")
                continue
                
            print(f"\n{Fore.CYAN}{lang['menu_proxy_list']}:")
            for i, p in enumerate(proxies, 1):
                print(f"{Fore.YELLOW}{i}. {p}")
            
            try:
                idx = int(input(f"{Fore.CYAN}{lang['prompt_proxy_remove']}"))
                if idx == 0:
                    continue
                if 1 <= idx <= len(proxies):
                    removed = proxies.pop(idx-1)
                    save_proxies()
                    removed_text = lang["msg_proxy_removed"].format(removed)
                    print(f"{Fore.GREEN}[+] {removed_text}")
                else:
                    print(f"{Fore.RED}[-] {lang['msg_invalid_number']}")
            except ValueError:
                print(f"{Fore.RED}[-] {lang['msg_invalid_input']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            
        elif choice == "3":
            if not proxies:
                print(f"{Fore.RED}[-] {lang['msg_proxy_empty']}")
            else:
                count_text = lang["msg_proxy_count"].format(len(proxies))
                print(f"\n{Fore.CYAN}{count_text}")
                for i, p in enumerate(proxies, 1):
                    print(f"{Fore.YELLOW}{i}. {p}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            
        elif choice == "4":
            print(f"{Fore.CYAN}{lang['prompt_bulk_proxy']}")
            print(f"{Fore.CYAN}{lang['prompt_bulk_proxy_end']}")
            
            bulk_proxies = []
            while True:
                line = input()
                if not line:
                    break
                if ":" in line:
                    bulk_proxies.append(line.strip())
            
            if bulk_proxies:
                proxies.extend(bulk_proxies)
                save_proxies()
                added_text = lang["msg_proxies_added"].format(len(bulk_proxies))
                print(f"{Fore.GREEN}[+] {added_text}")
            else:
                print(f"{Fore.YELLOW}[!] {lang['msg_no_proxies_added']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            
        elif choice == "5":
            break
        else:
            print(f"{Fore.RED}[-] {lang['msg_invalid_selection']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")

def view_logs():
    """View log menu"""
    while True:
        print_banner()
        print_menu([
            lang["menu_recent_ops"], 
            lang["menu_successful_ops"], 
            lang["menu_failed_ops"], 
            lang["menu_failed_proxies"],
            lang["menu_all_logs"],
            lang["menu_main"]
        ], lang["title_logs"])
        
        choice = input(f"{Fore.YELLOW}{lang['prompt_selection']}")

        # Check if log file exists
        if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
            print(f"{Fore.RED}[-] {lang['msg_log_missing']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            continue

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
            
        # Keywords based on language
        op_start_keyword = "İzlenme işlemi başladı" if current_lang == "tr" else "View operation started"
        success_keyword = "başarıyla izlenme ekledi" if current_lang == "tr" else "successfully added view"
        fail_keyword = "izlenme ekleyemedi" if current_lang == "tr" else "failed to add view"
        fetch_fail_keyword = "veriyi çekemedi" if current_lang == "tr" else "failed to fetch data"

        if choice == "1":
            keyword = op_start_keyword
            title = lang["menu_recent_ops"].upper()
        elif choice == "2":
            keyword = success_keyword
            title = lang["menu_successful_ops"].upper()
        elif choice == "3":
            keyword = fail_keyword
            title = lang["menu_failed_ops"].upper()
        elif choice == "4":
            keyword = fetch_fail_keyword
            title = lang["menu_failed_proxies"].upper()
        elif choice == "5":
            keyword = ""  # Show all logs
            title = lang["menu_all_logs"].upper()
        elif choice == "6":
            break
        else:
            print(f"{Fore.RED}[-] {lang['msg_invalid_selection']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")
            continue

        print(f"\n{Fore.CYAN}{title}")
        print(f"{Fore.CYAN}{'=' * len(title)}")
        
        found = False
        # Show most recent logs first (up to 20)
        filtered_logs = [log_line for log_line in reversed(logs) if keyword in log_line or not keyword]
        for i, log_line in enumerate(filtered_logs[:20], 1):
            print(f"{Fore.YELLOW}{i}. {log_line.strip()}")
            found = True
            
        if not found:
            print(f"{Fore.RED}[-] {lang['msg_no_logs']}")
            
        input(f"\n{Fore.CYAN}{lang['prompt_continue']}")

def help_menu():
    """Displays help information"""
    print_banner()
    print(f"{Fore.CYAN}{lang['title_help']}")
    print(f"{Fore.CYAN}{'═' * len(lang['title_help'])}")
    
    # Individual help items
    print(f"{Fore.YELLOW}{lang['help_bot_start']}")
    print(f"{Fore.YELLOW}{lang['help_channel']}")
    print(f"{Fore.YELLOW}{lang['help_post_id']}")
    print(f"{Fore.YELLOW}{lang['help_proxy']}")
    print()
    print(f"{Fore.YELLOW}{lang['help_proxy_mgmt']}")
    print(f"{Fore.YELLOW}{lang['help_proxy_format']}")
    print(f"{Fore.YELLOW}{lang['help_proxy_bulk']}")
    print()
    print(f"{Fore.YELLOW}{lang['help_logs']}")
    print(f"{Fore.YELLOW}{lang['help_help']}")
    print(f"{Fore.YELLOW}{lang['help_language']}")
    print()
    print(f"{Fore.RED}{lang['help_note']}")
    print(f"{Fore.RED}{lang['help_warning']}")
    print()
    input(f"{Fore.CYAN}{lang['prompt_continue']}")

def language_menu():
    """Language selection menu"""
    global current_lang
    
    print_banner()
    print_menu([
        lang["menu_lang_tr"],
        lang["menu_lang_en"]
    ], lang["title_language"])
    
    choice = input(f"{Fore.YELLOW}{lang['prompt_selection']}")
    
    if choice == "1":
        load_language("tr")
        print(f"{Fore.GREEN}[+] {lang['msg_language_changed']}{lang['menu_lang_tr']}")
    elif choice == "2":
        load_language("en")
        print(f"{Fore.GREEN}[+] {lang['msg_language_changed']}{lang['menu_lang_en']}")
    else:
        print(f"{Fore.RED}[-] {lang['msg_invalid_selection']}")
    
    input(f"{Fore.CYAN}{lang['prompt_continue']}")

def main_menu():
    """Main application menu"""
    load_proxies()
    load_language(current_lang)  # Load initial language
    
    while True:
        print_banner()
        print_menu([
            lang["menu_bot_start"],
            lang["menu_proxy_mgmt"],
            lang["menu_logs"],
            lang["menu_help"],
            lang["menu_language"],
            lang["menu_exit"]
        ], lang["title_main"])
        
        choice = input(f"{Fore.YELLOW}{lang['prompt_selection']}")

        if choice == "1":
            global channel, post_id
            print_banner()
            print(f"{Fore.CYAN}{lang['title_bot_start']}")
            print(f"{Fore.CYAN}{'═' * len(lang['title_bot_start'])}")
            channel_input = input(f"{Fore.CYAN}{lang['prompt_channel']}").replace("https://t.me/", "").strip()
            
            # Handle channel/post_id from full URL
            if "/" in channel_input:
                parts = channel_input.split("/")
                channel = parts[0]
                if len(parts) > 1 and parts[1].isdigit():
                    post_id = parts[1]
                    post_input = input(f"{Fore.CYAN}{lang['prompt_post_id']}[{post_id}]: ").strip()
                    if post_input:
                        post_id = post_input
                else:
                    post_id = input(f"{Fore.CYAN}{lang['prompt_post_id']}").strip()
            else:
                channel = channel_input
                post_id = input(f"{Fore.CYAN}{lang['prompt_post_id']}").strip()
            
            if channel and post_id:
                start_bot()
            else:
                print(f"{Fore.RED}[-] {lang['msg_invalid_channel']}")
                input(f"{Fore.CYAN}{lang['prompt_continue']}")
        
        elif choice == "2":
            proxy_menu()
        
        elif choice == "3":
            view_logs()
        
        elif choice == "4":
            help_menu()
            
        elif choice == "5":
            language_menu()
        
        elif choice == "6":
            print_banner()
            print(f"{Fore.RED}{lang['prompt_exit_confirm']}")
            confirm = input(f"{Fore.YELLOW}{lang['prompt_yes_no']}")
            if confirm == "1":
                print(f"{Fore.YELLOW}{lang['msg_exiting']}")
                break
        
        else:
            print(f"{Fore.RED}[-] {lang['msg_invalid_selection']}")
            input(f"{Fore.CYAN}{lang['prompt_continue']}")

if __name__ == "__main__":
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] {lang['msg_interrupted']}")
    except Exception as e:
        print(f"\n{Fore.RED}[-] {lang['msg_error']}{str(e)}")
        with open("error.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - HATA: {str(e)}\n")
        print(f"{Fore.YELLOW}[!] {lang['msg_error_logged']}")
