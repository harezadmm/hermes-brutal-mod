# RedMess Security Skills - Deployment Guide

**Version:** 1.0.0  
**Date:** September 4, 2026  
**Author:** harezadmm

## 📋 Overview

This guide covers deploying RedMess Security Skills repository for:
- Personal penetration testing lab
- Red team operations
- Security research
- Educational environments

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-org/RedMess.git
cd RedMess
```

### 2. Run Setup
```bash
chmod +x setup.sh
sudo ./setup.sh
```

### 3. Verify Installation
```bash
# Check skills count
find skills -name "SKILL.md" | wc -l
# Should output: 100

# List security skills
ls skills/Security/

# Test a skill
cat skills/Security/linux-privilege-escalation/SKILL.md
```

## 🔧 Manual Installation

### System Requirements
- **OS:** Kali Linux 2023+, Ubuntu 22.04+, Debian 11+
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 50GB free space
- **Network:** Internet connection for tool downloads
- **Privileges:** Root/sudo access

### Core Tools Installation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip python3-venv

# Install penetration testing tools
sudo apt-get install -y \
    nmap masscan \
    sqlmap nikto \
    john hashcat \
    metasploit-framework \
    wireshark tcpdump \
    hydra medusa \
    aircrack-ng \
    binwalk foremost \
    radare2 gdb \
    docker.io

# Install Python security libraries
pip3 install \
    requests scapy pwntools \
    impacket frida-tools \
    paramiko cryptography \
    selenium beautifulsoup4
```

## 📁 Workspace Setup

```bash
# Create workspace structure
mkdir -p ~/redmess-workspace/{loot,exploits,payloads,wordlists,tools,logs}
mkdir -p ~/redmess-workspace/targets/{network,web,mobile,cloud}

# Download wordlists
cd ~/redmess-workspace/wordlists

# RockYou
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# SecLists
git clone https://github.com/danielmiessler/SecLists.git

# PayloadsAllTheThings
git clone https://github.com/swisskyrepo/PayloadsAllTheThings.git
```

## 🎯 Skill Usage Workflow

### 1. Select Target

```bash
# Network target
echo "192.168.1.100" > ~/redmess-workspace/targets/network/target.txt

# Web target
echo "https://target-app.com" > ~/redmess-workspace/targets/web/target.txt

# Mobile app
adb pull /data/app/com.example.app/base.apk ~/redmess-workspace/targets/mobile/
```

### 2. Choose Skill

```bash
# Search for relevant skill
grep -r "SQL injection" /tmp/RedMess/skills/

# Read skill
cat /tmp/RedMess/skills/Security/database-hacking-techniques/SKILL.md
```

### 3. Execute Procedure

```bash
# Follow step-by-step
# Example: SQL injection

# Step 1: Test for vulnerability
sqlmap -u "https://target-app.com/product?id=1" --batch

# Step 2: Enumerate databases
sqlmap -u "https://target-app.com/product?id=1" --dbs

# Step 3: Dump data
sqlmap -u "https://target-app.com/product?id=1" -D database_name --dump

# Save loot
mv /root/.local/share/sqlmap/output ~/redmess-workspace/loot/target-app-dump/
```

## ⚖️ Legal Disclaimer

**CRITICAL REMINDER:**

These tools and skills are for **AUTHORIZED TESTING ONLY**.

- ✅ Your own systems
- ✅ Systems you have written permission to test
- ✅ Bug bounty programs (within scope)
- ✅ Penetration testing engagements (with contract)

- ❌ Other people's systems
- ❌ Production systems without authorization
- ❌ Any system you don't own or have permission to test

**Unauthorized access is a crime.** Penalties include:
- Criminal prosecution
- Imprisonment
- Heavy fines
- Civil liability

**Always obtain written permission before testing.**

---

**Happy (legal) hacking! 🔐**
