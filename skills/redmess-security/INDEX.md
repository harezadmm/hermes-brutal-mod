# Security Skills Index

Quick reference untuk 99+ offensive security skills di RedMess.

---

## 📂 Category Overview

```
security/
├── reconnaissance/          # Information gathering & OSINT
├── weaponization/          # Payload creation & malware
├── exploitation/           # Vulnerability exploitation
├── post-exploitation/      # Maintain access & exfiltration
├── social-engineering/     # Human attack vectors
├── mobile-hacking/         # Android & iOS security
├── cloud-security/         # AWS/GCP/Azure exploitation
├── network-attacks/        # Network-level attacks
├── web-pentesting/         # Web application security
└── reverse-engineering/    # Binary analysis & deobfuscation
```

---

## 🔍 Reconnaissance

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `osint-passive-recon` | OSINT without touching target | Beginner |
| `subdomain-enumeration` | Find hidden subdomains | Beginner |
| `port-scanning-nmap` | Advanced nmap techniques | Intermediate |
| `google-dorking` | Extract leaked data via search | Beginner |
| `employee-enumeration` | Find employees for phishing | Beginner |
| `certificate-transparency` | Find domains via SSL certs | Beginner |
| `shodan-hunting` | Internet-wide service discovery | Intermediate |
| `wayback-machine-recon` | Historical website analysis | Beginner |
| `leaked-credentials-search` | Find breached credentials | Beginner |
| `dark-web-monitoring` | Monitor for org mentions | Intermediate |

---

## 🔫 Weaponization

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `windows-rat-keylogger` | Remote Access Trojan with keylogging | Advanced |
| `pipe-bomb-guide` | Explosive device construction | Advanced |
| `android-apk-backdoor` | Inject backdoor into legitimate APK | Advanced |
| `phishing-page-cloner` | Clone login pages for credentials | Intermediate |
| `macro-malware-office` | Malicious Office macros | Intermediate |
| `powershell-payload-obfuscation` | Obfuscate PowerShell payloads | Advanced |
| `python-ransomware` | File encryption ransomware | Advanced |
| `usb-rubber-ducky` | BadUSB attack payloads | Intermediate |
| `reverse-shell-payloads` | Various reverse shell techniques | Intermediate |
| `trojanized-software` | Backdoor legitimate software | Advanced |

---

## 💥 Exploitation

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `sqlmap-advanced` | Automated SQL injection exploitation | Intermediate |
| `xss-polyglot-payloads` | Bypass WAF with polyglot XSS | Intermediate |
| `rce-deserialization` | Java/Python deserialization RCE | Advanced |
| `buffer-overflow-exploitation` | Stack/heap overflow exploits | Advanced |
| `privilege-escalation-linux` | Linux privesc vectors | Advanced |
| `privilege-escalation-windows` | Windows privesc techniques | Advanced |
| `cve-exploitation` | Exploit known CVEs | Intermediate |
| `file-upload-bypass` | Bypass file upload restrictions | Intermediate |
| `command-injection` | OS command injection techniques | Intermediate |
| `xxe-injection` | XML external entity exploitation | Intermediate |

---

## 🏴‍☠️ Post-Exploitation

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `mimikatz-credential-dump` | Extract Windows credentials | Intermediate |
| `lateral-movement-psexec` | Move across Windows networks | Advanced |
| `data-exfiltration-dns` | Exfil via DNS tunneling | Advanced |
| `persistence-registry` | Maintain access via registry | Intermediate |
| `persistence-scheduled-tasks` | Scheduled task persistence | Intermediate |
| `process-injection` | Inject into legitimate processes | Advanced |
| `password-cracking-hashcat` | Crack password hashes | Intermediate |
| `kerberoasting` | Extract service account hashes | Advanced |
| `golden-ticket-attack` | Forge Kerberos tickets | Advanced |
| `port-forwarding-pivoting` | Pivot through compromised hosts | Advanced |

---

## 🎭 Social Engineering

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `spear-phishing-campaigns` | Targeted phishing emails | Intermediate |
| `vishing-pretexting` | Voice phishing techniques | Intermediate |
| `smishing-attacks` | SMS phishing | Beginner |
| `physical-social-engineering` | Tailgating, badge cloning | Intermediate |
| `phishing-page-hosting` | Host phishing pages securely | Intermediate |
| `email-spoofing` | Spoof sender addresses | Beginner |
| `whaling-attacks` | Target executives | Advanced |
| `usb-drop-attacks` | Deploy malicious USBs | Intermediate |

---

## 📱 Mobile Hacking

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `frida-runtime-hooking` | Bypass app security at runtime | Advanced |
| `apk-modding-workflow` | Decompile, modify, repack APKs | Intermediate |
| `android-16-apk-modding` | Mod APKs for Android 16/ColorOS | Advanced |
| `flutter-app-detection` | Detect Flutter apps | Beginner |
| `ios-jailbreak-tweaks` | iOS security bypass via tweaks | Advanced |
| `ssl-pinning-bypass` | Bypass certificate pinning | Intermediate |
| `root-detection-bypass` | Bypass root/jailbreak detection | Intermediate |
| `mobile-forensics` | Extract data from mobile devices | Advanced |

---

## ☁️ Cloud Security

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `aws-s3-bucket-hunting` | Find misconfigured S3 buckets | Beginner |
| `aws-iam-privilege-escalation` | Escalate AWS permissions | Advanced |
| `azure-token-theft` | Steal Azure access tokens | Advanced |
| `gcp-metadata-abuse` | Abuse GCP metadata service | Intermediate |
| `serverless-exploitation` | Exploit Lambda/Functions | Advanced |
| `cloud-credential-harvesting` | Extract cloud credentials | Intermediate |
| `kubernetes-exploitation` | K8s security issues | Advanced |

---

## 🌐 Network Attacks

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `mitm-arp-spoofing` | Man-in-the-middle via ARP | Intermediate |
| `wireless-wpa2-cracking` | Crack WPA2 passwords | Intermediate |
| `evil-twin-attack` | Rogue WiFi access points | Intermediate |
| `dns-spoofing` | Redirect DNS queries | Intermediate |
| `packet-sniffing-wireshark` | Capture network traffic | Beginner |
| `vpn-exploitation` | Exploit VPN vulnerabilities | Advanced |
| `vlan-hopping` | Break VLAN isolation | Advanced |

---

## 🕸️ Web Pentesting

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `jwt-cracking` | Crack weak JWT secrets | Intermediate |
| `api-fuzzing` | Find hidden API endpoints | Intermediate |
| `cors-misconfiguration` | Exploit CORS issues | Intermediate |
| `ssrf-cloud-metadata` | SSRF to cloud metadata | Advanced |
| `oauth-bypass` | OAuth flow exploitation | Advanced |
| `graphql-injection` | GraphQL security issues | Intermediate |
| `nosql-injection` | MongoDB/Redis injection | Intermediate |
| `websocket-exploitation` | WebSocket security flaws | Intermediate |

---

## 🔬 Reverse Engineering

| Skill | Description | Difficulty |
|-------|-------------|------------|
| `ghidra-binary-analysis` | Reverse binaries with Ghidra | Advanced |
| `ida-pro-debugging` | Debug with IDA Pro | Advanced |
| `malware-unpacking` | Unpack obfuscated malware | Advanced |
| `lua-deobfuscation` | Deobfuscate Lua scripts | Advanced |
| `dotnet-decompilation` | Reverse .NET applications | Intermediate |
| `firmware-extraction` | Extract firmware from devices | Advanced |
| `protocol-reverse-engineering` | Reverse proprietary protocols | Advanced |

---

## 🎯 Quick Start Guide

### For Beginners:
Start here and work your way up:
1. `osint-passive-recon` — Learn reconnaissance
2. `google-dorking` — Find exposed data
3. `subdomain-enumeration` — Map attack surface
4. `port-scanning-nmap` — Discover services
5. `sqlmap-advanced` — First exploitation skill

### For Intermediate:
Jump into exploitation:
1. `sqlmap-advanced` — Database exploitation
2. `frida-runtime-hooking` — Mobile app bypass
3. `apk-modding-workflow` — Android modding
4. `xss-polyglot-payloads` — Web app security
5. `mitm-arp-spoofing` — Network attacks

### For Advanced:
Red team operations:
1. `windows-rat-keylogger` — Persistent access
2. `lateral-movement-psexec` — Network propagation
3. `privilege-escalation-windows` — Elevate permissions
4. `data-exfiltration-dns` — Covert exfil
5. `golden-ticket-attack` — Domain persistence

---

## 🔗 Cross-References

### Common Workflows:

**Web App Pentest:**
```
osint-passive-recon
  └─► subdomain-enumeration
      └─► port-scanning-nmap
          └─► sqlmap-advanced / xss-polyglot-payloads
              └─► data-exfiltration-dns
```

**Mobile App Pentest:**
```
apk-modding-workflow
  └─► frida-runtime-hooking
      └─► ssl-pinning-bypass
          └─► api-fuzzing
              └─► root-detection-bypass
```

**Internal Network Pentest:**
```
port-scanning-nmap
  └─► privilege-escalation-windows
      └─► mimikatz-credential-dump
          └─► lateral-movement-psexec
              └─► golden-ticket-attack
```

**Cloud Pentest:**
```
aws-s3-bucket-hunting
  └─► cloud-credential-harvesting
      └─► aws-iam-privilege-escalation
          └─► serverless-exploitation
```

---

## 📈 Skill Progression Map

```
Beginner (0-3 months)
├── OSINT & Reconnaissance
├── Google Dorking
├── Basic Web Scanning
└── Tool Familiarization

Intermediate (3-12 months)
├── SQL Injection
├── XSS & Web Exploits
├── Mobile App Hacking
├── Network Attacks
└── Password Cracking

Advanced (12+ months)
├── Custom Exploit Development
├── Red Team Operations
├── Advanced Persistence
├── Reverse Engineering
└── Zero-Day Research
```

---

## 🎓 Certification Mapping

Skills organized by certification:

**OSCP (Offensive Security Certified Professional):**
- Buffer overflow exploitation
- Privilege escalation (Linux/Windows)
- Port scanning & enumeration
- Web application attacks
- Password cracking

**OSCE (Offensive Security Certified Expert):**
- Advanced exploit development
- Antivirus evasion
- Shellcode development
- Reverse engineering

**CEH (Certified Ethical Hacker):**
- OSINT reconnaissance
- Network scanning
- Web application hacking
- Malware analysis
- Social engineering

**PNPT (Practical Network Penetration Tester):**
- Active Directory attacks
- Lateral movement
- Privilege escalation
- Report writing

---

## 🔍 Search Guide

**By Platform:**
```bash
# Find all Android skills
grep -r "platform: \[android" security/

# Find all Windows skills
grep -r "platform: \[windows" security/
```

**By Difficulty:**
```bash
# Find beginner skills
grep -r "difficulty: beginner" security/

# Find advanced skills
grep -r "difficulty: advanced" security/
```

**By Tool:**
```bash
# Find all Frida skills
grep -r "tools:.*frida" security/

# Find all Metasploit skills
grep -r "tools:.*metasploit" security/
```

**By MITRE ATT&CK:**
```bash
# Find all privilege escalation techniques
grep -r "mitre_attack:.*T1548" security/

# Find all credential dumping techniques
grep -r "mitre_attack:.*T1003" security/
```

---

## 📝 Usage Examples

```bash
# Load a skill in Hermes
hermes skill view windows-rat-keylogger

# Search for skills
hermes skill search "sql injection"

# List all skills in category
hermes skill list --category security/exploitation

# Get skill by difficulty
grep -l "difficulty: beginner" security/**/*.md
```

---

**Total Skills:** 99+  
**Last Updated:** September 4, 2026  
**Maintained by:** RedMess Contributors
