---
name: network-scanning-recon
description: Nmap, masscan, shodan, network reconnaissance.
tags: [nmap, masscan, shodan, recon, port-scanning, subdomain-enum]
---

# Network Scanning & Reconnaissance

Use when user requests network scanning, port scanning, service enumeration, subdomain discovery, or reconnaissance of network infrastructure.

## Trigger Conditions
- Port scanning
- Service enumeration
- Network mapping
- Subdomain discovery
- Shodan/Censys searches
- OS fingerprinting
- Vulnerability scanning

## Nmap Basics

### Quick Scans
```bash
# Ping sweep (discover live hosts)
nmap -sn 192.168.1.0/24

# Quick port scan (top 1000 ports)
nmap 192.168.1.10

# All ports
nmap -p- 192.168.1.10

# Specific ports
nmap -p 80,443,8080 192.168.1.10

# Fast scan (aggressive timing)
nmap -T4 -F 192.168.1.10
```

### Service Detection
```bash
# Service version detection
nmap -sV 192.168.1.10

# OS detection
nmap -O 192.168.1.10

# Aggressive scan (OS + version + scripts + traceroute)
nmap -A 192.168.1.10

# Banner grabbing
nmap -sV --script=banner 192.168.1.10
```

### Stealth Scans
```bash
# SYN scan (stealth, doesn't complete handshake)
nmap -sS 192.168.1.10

# TCP connect scan (less stealth, completes handshake)
nmap -sT 192.168.1.10

# UDP scan (very slow)
nmap -sU 192.168.1.10

# Null scan (firewall evasion)
nmap -sN 192.168.1.10

# FIN scan
nmap -sF 192.168.1.10

# Xmas scan
nmap -sX 192.168.1.10
```

### Firewall Evasion
```bash
# Fragment packets
nmap -f 192.168.1.10

# Decoy scan (hide your IP among decoys)
nmap -D RND:10 192.168.1.10

# Spoof source port
nmap --source-port 53 192.168.1.10

# Randomize host order
nmap --randomize-hosts 192.168.1.0/24

# Slow scan (avoid IDS)
nmap -T1 192.168.1.10
```

## Nmap Scripting Engine (NSE)

### Vulnerability Scanning
```bash
# Run default scripts
nmap -sC 192.168.1.10

# Run all vuln scripts
nmap --script vuln 192.168.1.10

# Specific vulnerability
nmap --script smb-vuln-ms17-010 192.168.1.10

# SQL injection detection
nmap --script http-sql-injection 192.168.1.10

# Check for common vulns
nmap --script=vulscan/vulscan.nse 192.168.1.10
```

### Service-Specific Scripts
```bash
# HTTP enumeration
nmap --script http-enum 192.168.1.10

# SMB enumeration
nmap --script smb-enum-shares,smb-enum-users 192.168.1.10

# SSH brute force
nmap --script ssh-brute --script-args userdb=users.txt,passdb=passwords.txt 192.168.1.10

# FTP anonymous login
nmap --script ftp-anon 192.168.1.10

# MySQL enumeration
nmap --script mysql-enum 192.168.1.10
```

### Custom NSE Scripts
```lua
-- http-custom-check.nse
description = [[
Custom HTTP endpoint check
]]

categories = {"discovery", "safe"}

portrule = function(host, port)
  return port.number == 80 or port.number == 443
end

action = function(host, port)
  local http = require "http"
  local response = http.get(host, port, "/admin")
  
  if response.status == 200 then
    return "Admin panel found!"
  end
end
```

## Masscan (Fastest Port Scanner)

### Basic Usage
```bash
# Scan entire internet for port 80 (BE CAREFUL!)
masscan 0.0.0.0/0 -p80

# Scan single target, all ports
masscan 192.168.1.10 -p0-65535

# Scan multiple ports
masscan 192.168.1.0/24 -p80,443,8080,8443

# Scan with rate limit (packets/sec)
masscan 192.168.1.0/24 -p80 --rate 1000

# Output to file
masscan 192.168.1.0/24 -p80 -oL results.txt
```

### Advanced Masscan
```bash
# Exclude IPs
masscan 10.0.0.0/8 -p80 --exclude 10.0.0.1-10.0.1.255

# Banner grabbing
masscan 192.168.1.0/24 -p80 --banners

# Specific source IP (if multiple interfaces)
masscan 192.168.1.0/24 -p80 --source-ip 192.168.1.100

# Custom configuration
masscan -c masscan.conf
```

### Masscan → Nmap Pipeline
```bash
# 1. Fast discovery with masscan
masscan 10.0.0.0/8 -p80,443 --rate 10000 -oL found.txt

# 2. Parse results
grep open found.txt | awk '{print $4}' | sort -u > targets.txt

# 3. Detailed scan with nmap
nmap -sV -iL targets.txt -oA detailed_results
```

## Shodan (Internet-Wide Scanning)

### Shodan CLI
```bash
# Install
pip install shodan

# Initialize
shodan init YOUR_API_KEY

# Search
shodan search "apache"
shodan search "port:3389 country:US"
shodan search "webcam"

# Get host info
shodan host 8.8.8.8

# Download search results
shodan download results "port:22" --limit 1000

# Parse downloaded data
shodan parse results.json.gz
```

### Shodan Queries
```bash
# Find specific service
shodan search "product:MySQL"

# Find by country/city
shodan search "port:3306 country:ID city:Jakarta"

# Find default credentials
shodan search "default password"

# Find webcams
shodan search "Server: SQ-WEBCAM"

# Find ICS/SCADA
shodan search "port:502"  # Modbus
shodan search "port:47808"  # BACnet

# Find vulnerable services
shodan search "port:445 ms17-010"

# Find specific software version
shodan search "OpenSSH 7.2"
```

### Shodan Python API
```python
import shodan

api = shodan.Shodan('YOUR_API_KEY')

# Search
results = api.search('apache')

for result in results['matches']:
    print(f"IP: {result['ip_str']}")
    print(f"Port: {result['port']}")
    print(f"Banner: {result['data']}\n")

# Get host details
host = api.host('8.8.8.8')
print(f"OS: {host.get('os', 'n/a')}")
print(f"Organization: {host.get('org', 'n/a')}")
for item in host['data']:
    print(f"Port {item['port']}: {item['product']}")
```

## Subdomain Enumeration

### Subfinder
```bash
# Install
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Basic scan
subfinder -d target.com

# Output to file
subfinder -d target.com -o subdomains.txt

# Use all sources
subfinder -d target.com -all

# Recursive (find subdomains of subdomains)
subfinder -d target.com -recursive
```

### Amass
```bash
# Install
apt install amass

# Passive scan (OSINT only)
amass enum -passive -d target.com

# Active scan (DNS brute force)
amass enum -d target.com

# With DNS brute force wordlist
amass enum -d target.com -brute -w wordlist.txt

# Output formats
amass enum -d target.com -json output.json
```

### DNSRecon
```bash
# Standard enumeration
dnsrecon -d target.com

# Brute force subdomains
dnsrecon -d target.com -D subdomains.txt -t brt

# Zone transfer attempt
dnsrecon -d target.com -t axfr

# Reverse lookup
dnsrecon -r 192.168.1.0/24
```

### Manual Zone Transfer
```bash
# Find nameservers
dig target.com NS

# Attempt zone transfer
dig axfr target.com @ns1.target.com

# If successful, you get all DNS records!
```

## DNS Bruteforcing

### Gobuster DNS Mode
```bash
# Install
apt install gobuster

# DNS bruteforce
gobuster dns -d target.com -w wordlist.txt

# Show CNAMEs
gobuster dns -d target.com -w wordlist.txt -c

# Wildcard handling
gobuster dns -d target.com -w wordlist.txt --wildcard
```

### FFuf DNS Mode
```bash
# DNS fuzzing
ffuf -w wordlist.txt -u https://FUZZ.target.com

# Filter by status code
ffuf -w wordlist.txt -u https://FUZZ.target.com -fc 404

# Match response size
ffuf -w wordlist.txt -u https://FUZZ.target.com -fs 4242
```

## Network Mapping

### Full Network Discovery Pipeline
```bash
#!/bin/bash
TARGET="10.0.0.0/8"

# 1. Ping sweep
echo "[+] Discovering live hosts..."
nmap -sn $TARGET -oG - | awk '/Up$/{print $2}' > live_hosts.txt

# 2. Fast port scan
echo "[+] Port scanning..."
nmap -p- -T4 -iL live_hosts.txt -oA port_scan

# 3. Service detection on open ports
echo "[+] Service detection..."
nmap -sV -iL live_hosts.txt -oA service_scan

# 4. Vulnerability scan
echo "[+] Vulnerability scanning..."
nmap --script vuln -iL live_hosts.txt -oA vuln_scan

# 5. Parse results
echo "[+] Generating report..."
grep -r "open" *.gnmap > open_ports.txt
grep -r "VULNERABLE" *.nmap > vulnerabilities.txt

echo "[+] Scan complete!"
```

## Censys (Alternative to Shodan)

### Censys CLI
```bash
# Install
pip install censys

# Configure
censys config

# Search
censys search "services.port:22"

# Get host
censys view 8.8.8.8
```

### Censys Queries
```
# Find specific TLS certs
services.tls.certificates.leaf_data.subject.common_name:*.target.com

# Find HTTP servers
services.http.response.html_title:"Admin Panel"

# Find by ASN
autonomous_system.asn:15169

# Find by location
location.country:Indonesia
```

## Banner Grabbing

### Netcat
```bash
# HTTP banner
echo "HEAD / HTTP/1.1\r\nHost: target.com\r\n\r\n" | nc target.com 80

# SMTP banner
nc target.com 25

# SSH banner
nc target.com 22

# FTP banner
nc target.com 21
```

### Automated
```bash
# Nmap banners
nmap -sV --script=banner target.com

# dmitry (all-in-one recon)
dmitry -iwnse target.com
```

## OS Fingerprinting

### Passive OS Detection
```bash
# p0f (passive, no packets sent)
p0f -i eth0

# Watches network traffic and guesses OS
```

### Active OS Detection
```bash
# Nmap OS detection
nmap -O target.com

# Aggressive OS detection
nmap -O --osscan-guess target.com

# xprobe2
xprobe2 target.com
```

## ASN Enumeration

### Find IP ranges of organization
```bash
# Method 1: whois
whois -h whois.radb.net target.com

# Method 2: BGP toolkit
curl "https://bgp.he.net/search?search%5Bsearch%5D=target.com"

# Method 3: ASN lookup
curl "https://ipinfo.io/AS15169" | jq .
```

## Reverse IP Lookup

### Find all domains on IP
```bash
# Method 1: Bing API
curl "https://www.bing.com/search?q=ip:192.168.1.1"

# Method 2: ViewDNS
curl "https://viewdns.info/reverseip/?host=192.168.1.1&t=1"

# Method 3: SecurityTrails API
curl "https://api.securitytrails.com/v1/domain/192.168.1.1/reverse" \
  -H "APIKEY: YOUR_KEY"
```

## WHOIS Enumeration

### Basic WHOIS
```bash
# Domain WHOIS
whois target.com

# IP WHOIS
whois 8.8.8.8

# ASN WHOIS
whois -h whois.radb.net AS15169
```

### Parse WHOIS Data
```bash
# Extract emails
whois target.com | grep -i email

# Extract nameservers
whois target.com | grep -i "name server"

# Extract registrar
whois target.com | grep -i registrar
```

## Screenshot Web Services

### Aquatone
```bash
# Install
go install github.com/michenriksen/aquatone@latest

# Take screenshots of all subdomains
cat subdomains.txt | aquatone -out screenshots/

# View report
firefox screenshots/aquatone_report.html
```

### EyeWitness
```bash
# Install
git clone https://github.com/FortyNorthSecurity/EyeWitness
cd EyeWitness/Python/setup
./setup.sh

# Run
./EyeWitness.py -f urls.txt --web
```

## Automation Script

### Full Recon Script
```python
#!/usr/bin/env python3
import subprocess
import sys

def run(cmd):
    print(f"[+] Running: {cmd}")
    subprocess.run(cmd, shell=True)

def recon(target):
    print(f"[*] Starting reconnaissance on {target}")
    
    # Subdomain enumeration
    run(f"subfinder -d {target} -o subdomains.txt")
    run(f"amass enum -passive -d {target} >> subdomains.txt")
    
    # Resolve subdomains
    run(f"cat subdomains.txt | dnsx -silent -o resolved.txt")
    
    # Port scan
    run(f"nmap -iL resolved.txt -T4 -p- -oA port_scan")
    
    # Service detection
    run(f"nmap -iL resolved.txt -sV -oA service_scan")
    
    # Screenshot
    run(f"cat resolved.txt | aquatone -out screenshots/")
    
    # Vulnerability scan
    run(f"nmap --script vuln -iL resolved.txt -oA vuln_scan")
    
    print(f"[+] Reconnaissance complete! Check results.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./recon.py target.com")
        sys.exit(1)
    
    recon(sys.argv[1])
```

## Pitfalls
- **Rate limiting**: Too fast = detection/blocking
- **False positives**: Firewalls can show ports as filtered
- **Legal**: Scanning without permission is illegal
- **Noise**: Aggressive scans trigger IDS/IPS
- **IPv6**: Many tools don't scan IPv6 by default

## Related Skills
- `web-pentesting-tools`: Web application scanning
- `sqlmap`: SQL injection after port discovery
- `advanced-hacking`: Exploitation after reconnaissance
- `social-engineering`: Use recon data for targeted attacks
