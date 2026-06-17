import os
import requests
from time import sleep
from configparser import ConfigParser
from os import system, name
from threading import Thread, active_count, Event
import csv
import phonenumbers
from phonenumbers import PhoneNumber, PhoneNumberFormat
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
import random
from emailtools import generate
import re
from itertools import cycle
import logging
import json

# ============ TELEGRAM BOT SETUP ============
BOT_TOKEN = "8674884879:AAEGkrEKSnOOLan0cH1MnCjYcUDRDx2m1r0"  # 👈 Apna bot token yahan daalo
ADMIN_USER_ID = 8518042438  # 👈 Apna Telegram user ID yahan daalo (integer)

# ============ CONFIGURATION ============
THREADS = 1200
PROXIES_TYPES = ('http', 'socks4', 'socks5')
time_out = 20
REPORTING = False  # Initially reporting is off
TARGET_USERNAME = ""
REPORT_THREAD = None
STOP_EVENT = Event()

# ============ LOGGING ============
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ USER AGENT SETUP ============
software_names = [
    SoftwareName.CHROME.value, 
    SoftwareName.FIREFOX.value, 
    SoftwareName.EDGE.value, 
    SoftwareName.OPERA.value,
    SoftwareName.SAFARI.value
]

operating_systems = [
    OperatingSystem.WINDOWS.value, 
    OperatingSystem.LINUX.value, 
    OperatingSystem.MAC.value
]

user_agent_rotator = UserAgent(
    software_names=software_names, 
    operating_systems=operating_systems, 
    limit=2000
)

# ============ MOBILE USER AGENTS ============
MOBILE_USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S901E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-F721B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0',
    'Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
    'Mozilla/5.0 (Android 12; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/149.0.0.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/148.0.0.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/147.0.0.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/121.0.6167.180 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/121.0.6167.180 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36 OPR/80.0.4170.73613',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36 OPR/79.0.4143.72758',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/149.0.0.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/148.0.0.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/124.0 Mobile/15E148 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/123.0 Mobile/15E148 Safari/605.1.15'
]

# ============ DIVERSE HEADERS POOL ============
HEADERS_POOL = [
    # Desktop Chrome on Windows
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Desktop Firefox on Windows
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.5',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Desktop Chrome on Mac
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Mobile Chrome on Android
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Mobile Firefox on Android
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.5',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Mobile Safari on iOS
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Mobile Chrome on iOS
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"iOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Samsung Browser on Android
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    },
    # Opera Mobile on Android
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Opera";v="80", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support'
    }
]

# ============ GLOBAL VARIABLES ============
errors = open('errors.txt', 'a+')
success_count = 0
error_count = 0
username = ""

# ============ TELEGRAM BOT FUNCTIONS ============
def send_telegram_message(message):
    """Send message to Telegram admin"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': ADMIN_USER_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def get_updates(offset=None):
    """Get updates from Telegram bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return {'ok': False, 'result': []}

# ============ CORE FUNCTIONS ============
def get_random_user_agent():
    """Get random user agent - mix of desktop and mobile"""
    if random.random() < 0.5:  # 50% chance of mobile
        return random.choice(MOBILE_USER_AGENTS)
    else:
        return user_agent_rotator.get_random_user_agent()

def get_random_headers():
    """Get random headers with mobile/desktop mix"""
    headers = random.choice(HEADERS_POOL).copy()
    headers['user-agent'] = get_random_user_agent()
    
    languages = [
        'en-US,en;q=0.9',
        'en-GB,en;q=0.9,en-US;q=0.8',
        'en-IN,en;q=0.9,en-US;q=0.8',
        'en-CA,en;q=0.9,en-US;q=0.8',
        'en-AU,en;q=0.9,en-US;q=0.8',
        'hi-IN,en;q=0.9,en-US;q=0.8',
        'es-ES,en;q=0.9,en-US;q=0.8',
        'pt-BR,en;q=0.9,en-US;q=0.8',
        'fr-FR,en;q=0.9,en-US;q=0.8',
        'de-DE,en;q=0.9,en-US;q=0.8',
        'ru-RU,en;q=0.9,en-US;q=0.8',
        'ja-JP,en;q=0.9,en-US;q=0.8',
        'ko-KR,en;q=0.9,en-US;q=0.8'
    ]
    headers['accept-language'] = random.choice(languages)
    
    return headers

def generate_random_phone_number():
    while True:
        country_code = random.choice(['+1', '+44', '+91', '+61', '+81', '+49', '+33', '+55', '+86', '+7', '+92', '+20', '+234', '+52', '+63'])
        national_number = str(random.randint(1000000000, 9999999999))[:10]
        phone_number_str = country_code + national_number
        try:
            phone_number = phonenumbers.parse(phone_number_str)
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
        except:
            continue

def get_random_line(filename, username):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            if not lines:
                return f"Please unban {username}"
            line = random.choice(lines).strip()
            return line.replace('{username}', username)
    except FileNotFoundError:
        return f"Please unban {username}"

def extract_csrf_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    token_input = soup.find('input', {'name': 'csrf_token'})
    if token_input:
        return token_input.get('value', '')
    return None

def control(proxy, proxy_type, username):
    global success_count, error_count
    
    try:
        headers = get_random_headers()
        url = 'https://telegram.org/support'
        
        session = requests.Session()
        
        # Random delay to avoid pattern detection
        sleep(random.uniform(0.1, 0.5))
        
        # GET request with random headers
        response = session.get(
            url, 
            proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'}, 
            timeout=time_out, 
            headers=headers
        )
        
        if response.status_code != 200:
            error_count += 1
            return
        
        csrf_token = extract_csrf_token(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', action="/support")
        
        if not form:
            error_count += 1
            return
        
        # Generate random data
        message = get_random_line('message.txt', username)
        email = generate('gmail')
        phone = generate_random_phone_number()
        
        # Build form data
        data = {}
        for input_tag in form.find_all(['input', 'textarea']):
            name = input_tag.get('name')
            if name:
                if name == 'csrf_token' and csrf_token:
                    data[name] = csrf_token
                elif 'email' in name.lower():
                    data[name] = email
                elif 'phone' in name.lower():
                    data[name] = phone
                elif 'problem' in name.lower() or 'message' in name.lower():
                    data[name] = message
                else:
                    data[name] = input_tag.get('value', '')
        
        textarea = form.find('textarea')
        if textarea:
            textarea_name = textarea.get('name')
            if textarea_name:
                data[textarea_name] = message
        
        # POST request with unique headers
        post_headers = headers.copy()
        post_headers['cookie'] = '; '.join([f"{k}={v}" for k, v in session.cookies.items()])
        
        response = session.post(url, data=data, headers=post_headers, timeout=time_out)
        
        if response.status_code == 200:
            success_count += 1
            if success_count % 10 == 0:  # Send status every 10 success
                send_telegram_message(f"✅ <b>Report Status</b>\nSuccess: {success_count}\nFailed: {error_count}")
        else:
            error_count += 1
            
    except:
        error_count += 1

def get_views_from_saved_proxies(proxy_type, proxies, username):
    global REPORTING
    for proxy in proxies:
        if not REPORTING or STOP_EVENT.is_set():
            break
        if proxy.strip():
            control(proxy.strip(), proxy_type, username)

def start_view():
    global REPORTING, REPORT_THREAD, STOP_EVENT
    
    while True:
        if not REPORTING:
            sleep(1)
            continue
        
        if STOP_EVENT.is_set():
            REPORTING = False
            STOP_EVENT.clear()
            send_telegram_message("🛑 <b>Reporting Stopped!</b>")
            break
        
        threads = []
        for proxy_type in PROXIES_TYPES:
            try:
                with open(f"{proxy_type}_proxies.txt", 'r') as file:
                    proxies = [p.strip() for p in file.readlines() if p.strip()]
                
                random.shuffle(proxies)
                
                chunk_size = min(100, len(proxies) // THREADS + 1)
                chunked_proxies = [proxies[i:i + chunk_size] for i in range(0, len(proxies), chunk_size)]
                
                for chunk in chunked_proxies:
                    if not REPORTING or STOP_EVENT.is_set():
                        break
                    thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk, username))
                    threads.append(thread)
                    thread.start()
                    sleep(random.uniform(0.05, 0.15))
                    
            except FileNotFoundError:
                pass
                continue
        
        for t in threads:
            t.join()
        
        sleep(random.randint(5, 15))

# ============ UI COLORS ============
E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'
W = '\033[0m'

def check_views():
    global success_count, error_count
    
    while True:
        if REPORTING:
            os.system('cls' if name == 'nt' else 'clear')
            print(f'''
{G}╔═══════════════════════════════════════════════════╗
{G}║           TELEGRAM REPORT BOT STATUS            ║
{G}╠═══════════════════════════════════════════════════╣
{G}║ {B}Status          {W}: {G}RUNNING{' ' * (19 - len('RUNNING'))}{G}║
{G}║ {B}Target          {W}: {S}{TARGET_USERNAME}{' ' * (20 - len(str(TARGET_USERNAME)))}{G}║
{G}║ {B}Active Threads  {W}: {B}{active_count()}{' ' * (20 - len(str(active_count())))}{G}║
{G}║ {S}Successful      {W}: {S}{success_count}{' ' * (24 - len(str(success_count)))}{G}║
{G}║ {E}Failed          {W}: {E}{error_count}{' ' * (24 - len(str(error_count)))}{G}║
{G}╚═══════════════════════════════════════════════════╝
            ''')
        sleep(5)

# ============ MAIN BOT LOOP ============
def main():
    global REPORTING, TARGET_USERNAME, username, success_count, error_count, REPORT_THREAD, STOP_EVENT
    
    send_telegram_message("🤖 <b>Bot Started!</b>\n\nCommands:\n/start - Show this message\n/report <username> - Start reporting\n/stop - Stop reporting\n/status - Check current status\n/help - Show help")
    
    # Start status display thread
    Thread(target=check_views, daemon=True).start()
    
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(offset=last_update_id + 1)
            
            if updates.get('ok'):
                for update in updates.get('result', []):
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        text = message.get('text', '')
                        
                        # Only respond to admin
                        if chat_id != ADMIN_USER_ID:
                            continue
                        
                        # ===== COMMANDS =====
                        if text == '/start' or text == '/help':
                            response = """🤖 <b>Telegram Report Bot</b>

<b>Commands:</b>
/report &lt;username&gt; - Start reporting a user/channel
/stop - Stop reporting
/status - Check current status
/help - Show this help

<b>Example:</b>
/report @username
/report https://t.me/username
/stop"""
                            send_telegram_message(response)
                        
                        elif text.startswith('/report'):
                            parts = text.split(' ', 1)
                            if len(parts) < 2:
                                send_telegram_message("❌ Please provide username!\nExample: /report @username")
                                continue
                            
                            target = parts[1].strip()
                            
                            # Extract username from link
                            if 't.me/' in target:
                                target = target.split('t.me/')[-1].split('/')[0]
                            if target.startswith('@'):
                                target = target[1:]
                            
                            if REPORTING:
                                send_telegram_message("⚠️ Reporting already running!\nUse /stop first to stop current reporting.")
                                continue
                            
                            TARGET_USERNAME = target
                            username = target
                            success_count = 0
                            error_count = 0
                            STOP_EVENT.clear()
                            REPORTING = True
                            
                            send_telegram_message(f"🚀 <b>Reporting Started!</b>\nTarget: <code>{target}</code>\nThreads: {THREADS}")
                            
                            # Start reporting thread
                            REPORT_THREAD = Thread(target=start_view, daemon=True)
                            REPORT_THREAD.start()
                        
                        elif text == '/stop':
                            if not REPORTING:
                                send_telegram_message("⚠️ No reporting is currently running.")
                                continue
                            
                            STOP_EVENT.set()
                            REPORTING = False
                            send_telegram_message("🛑 <b>Reporting Stopped!</b>")
                            
                            if REPORT_THREAD:
                                REPORT_THREAD.join(timeout=5)
                        
                        elif text == '/status':
                            if REPORTING:
                                response = f"""📊 <b>Report Status</b>
                                
Target: <code>{TARGET_USERNAME}</code>
Status: 🟢 Running
Success: {success_count}
Failed: {error_count}
Active Threads: {active_count()}"""
                            else:
                                response = f"""📊 <b>Report Status</b>

Status: 🔴 Stopped
Target: <code>{TARGET_USERNAME if TARGET_USERNAME else 'None'}</code>
Success: {success_count}
Failed: {error_count}"""
                            send_telegram_message(response)
        
        except Exception as e:
            logger.error(f"Bot error: {e}")
        
        sleep(1)

# ============ RUN ============
if __name__ == "__main__":
    print(f"{G}Starting Telegram Report Bot...{W}")
    print(f"{B}Bot Token: {BOT_TOKEN[:10]}...{W}")
    print(f"{B}Admin ID: {ADMIN_USER_ID}{W}")
    
    main()
