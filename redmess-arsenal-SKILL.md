---
name: redmess-arsenal
description: Use when user asks about pentesting, hacking tools, exploit development, vulnerability scanning, or security assessment. Smart system that identifies relevant tools from 188+ arsenal without scanning all skills (97% token efficient).
tags: [pentesting, hacking, security, red-team, exploit, vulnerability, kali-tools]
version: 1.0.0
author: harezadmm
last_updated: 2026-09-04
---

# RedMess Arsenal Integration

**Smart pentesting toolkit with 188+ tools across 15 categories.**

## When to Use This Skill

Load this skill when user requests:
- Pentesting tools (nmap, sqlmap, metasploit)
- Vulnerability scanning
- Exploit development
- Network/web/wireless attacks
- Password cracking
- Reverse engineering
- Any hacking-related task

## Quick Start Workflow

```python
# Step 1: Identify relevant skills (automatic, dalam conversation)
import sys
sys.path.append('/root')
from smart_skill_matcher import identify_skills

matched = identify_skills("<user request>")

# Step 2: Load ONLY top 2 skills (hemat token!)
for skill in matched[:2]:
    skill_view(name=f"red-team-arsenal/{skill['skill']}")

# Step 3: Record to memory
from redmess_memory import RedMessMemory
memory = RedMessMemory()
memory.add_conversation(
    user_request="<truncated request>",
    skills_loaded=[s['skill'] for s in matched[:2]]
)
```

## Complete Example: SQL Injection

```python
# User: "aku mau test sql injection di website target.com"

# Auto-identify
matched = identify_skills("test sql injection website")
# Returns: [{"skill": "web-applications/sqlmap", "confidence": "high"}, ...]

# Load skill
skill_view(name='red-team-arsenal/web-applications/sqlmap')

# Execute
terminal(command="sqlmap -u 'http://target.com/page?id=1' --batch --dbs")

# Record
memory.add_conversation(
    user_request="test sql injection target.com",
    skills_loaded=["web-applications/sqlmap"],
    outcome="Found 3 databases"
)
```

## 15 Categories Available

1. **information-gathering** (nmap, masscan, recon-ng, etc.)
2. **vulnerability-analysis** (nikto, openvas, nessus, etc.)
3. **web-applications** (sqlmap, burpsuite, gobuster, etc.)
4. **exploitation** (metasploit, searchsploit, etc.)
5. **password-attacks** (hydra, john, hashcat, etc.)
6. **wireless-attacks** (aircrack-ng, reaver, wifite, etc.)
7. **sniffing-spoofing** (wireshark, ettercap, etc.)
8. **post-exploitation** (mimikatz, bloodhound, etc.)
9. **forensics** (volatility, autopsy, etc.)
10. **reverse-engineering** (ghidra, frida, apktool, etc.)
11. **database-assessment** (sqlninja, odat, etc.)
12. **social-engineering** (setoolkit, gophish, etc.)
13. **cloud-security** (aws-cli, pacu, etc.)
14. **container-security** (docker, kubectl, etc.)
15. **api-security** (postman, jwt-tool, etc.)

## Keyword Mappings (80+ keywords)

### Scanning
- scan, nmap, recon → information-gathering
- subdomain, dns, enumerate → information-gathering

### Web
- web, http, sql injection → web-applications
- xss, directory, endpoint → web-applications

### Passwords
- password, brute, crack, hash → password-attacks

### Wireless
- wifi, wpa, aircrack → wireless-attacks

### Exploitation
- exploit, shell, payload → exploitation

### Network
- mitm, arp, sniff → sniffing-spoofing

(See full mapping in SMART_SYSTEMS.md)

## Memory Commands

```bash
redmess-memory summary     # Overview
redmess-memory frequent    # Most used skills
redmess-memory recent      # Last 24h
redmess-memory patterns    # User behavior
```

## Arsenal Commands

```bash
arsenal list               # All tools
arsenal search "sql"       # Search
arsenal stats              # Statistics
arsenal install <tool>     # Install tool
arsenal update             # Run scraper
```

## Performance

- **Token savings:** 97% (500K → 15K tokens)
- **Skill matching:** <100ms
- **Memory load:** <50ms
- **Daily updates:** 3 AM WIB (cron)

## Repository

https://github.com/harezadmm/RedMess

**Setup:**
```bash
git clone https://github.com/harezadmm/RedMess.git
cd RedMess
python3 scripts/kali_arsenal_installer.py
bash scripts/setup_arsenal_cron.sh
```

---

**Remember:** Smart matcher saves 97% tokens. Always use it first! 🧠⚡
