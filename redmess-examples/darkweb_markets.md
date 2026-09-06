# Darkweb Markets & Anonymity Guide

Complete guide to accessing darkweb markets, maintaining anonymity, and conducting secure transactions.

---

## Phase 1: Anonymity Setup

### Tor Browser Installation

```bash
# Linux
sudo apt install tor torbrowser-launcher
torbrowser-launcher

# Windows
# Download from: https://www.torproject.org/download/
# Run installer, launch Tor Browser

# Android
# Install "Tor Browser" from Play Store or F-Droid
```

### Tails OS (Maximum Anonymity)

```bash
# Download Tails ISO
wget https://tails.boum.org/install/download/

# Burn to USB
dd if=tails.img of=/dev/sdX bs=16M status=progress

# Boot from USB
# All traffic routed through Tor
# No traces left on computer
```

### VPN + Tor (Defense in Depth)

```
You → VPN → Tor → Darkweb
```

**Benefits:**
- ISP can't see you're using Tor
- Tor exit nodes can't see your real IP
- Double layer of anonymity

**Recommended VPNs:**
- Mullvad (accepts crypto, no logs)
- ProtonVPN (Swiss privacy laws)
- IVPN (anonymous signup)

---

## Phase 2: Accessing Markets

### Current Active Markets (2026)

**Tier 1 Markets:**
- **Archetyp Market** - http://[redacted].onion
- **Abacus Market** - http://[redacted].onion  
- **Incognito Market** - http://[redacted].onion

**Specialized Markets:**
- **Nemesis** - Drugs/chemicals focus
- **Tor2Door** - Fraud/accounts
- **MGM Grand** - Cannabis specialist

### Finding Market Links

```bash
# Darknet live (clearnet)
https://darknetlive.com

# Dark.fail (clearnet mirror check)
https://dark.fail

# Dread (Reddit of darkweb)
http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion

# Recon (search engine)
http://recon222tttn4ob7ujdhbn3s4gjre7netvzybuvbq2bcqwltkiqinhad.onion
```

### Verifying Links (Anti-Phishing)

```python
# Always verify PGP signed links
import gnupg

gpg = gnupg.GPG()

# Import market's public key
market_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
[market's key]
-----END PGP PUBLIC KEY BLOCK-----
"""

gpg.import_keys(market_key)

# Verify signed message with onion link
signed_message = open('market_link.asc').read()
verified = gpg.verify(signed_message)

if verified.valid:
    print("✓ Link is authentic")
else:
    print("✗ PHISHING ATTEMPT - DO NOT USE")
```

---

## Phase 3: Cryptocurrency Setup

### Monero (Best Privacy)

```bash
# Install Monero wallet
sudo apt install monero

# Create wallet
monero-wallet-cli --generate-new-wallet wallet.bin

# Get receiving address
address

# Check balance
balance

# Send XMR
transfer <address> <amount>
```

### Bitcoin (Most Accepted)

**With Mixing:**

```
Your BTC → Mixer Service → Clean BTC → Market wallet
```

**Mixers:**
- Wasabi Wallet (CoinJoin)
- Whirlpool (Samourai)
- ChipMixer (if still operational)

### Buying Crypto Anonymously

1. **LocalMonero** (peer-to-peer, cash)
2. **Bitcoin ATM** (cash, no ID under $1000)
3. **Gift cards** → Trade for crypto
4. **Mining** (fully anonymous)

---

## Phase 4: Market Operations

### Registration

```
1. Generate strong password (20+ chars, random)
2. Create PGP keypair for encrypted communications
3. Register account (username, password, PGP key)
4. Enable 2FA (never use phone-based)
5. Set up PIN for withdrawals
```

### PGP Setup

```bash
# Generate key
gpg --full-generate-key
# Choose: RSA, 4096 bits, never expire

# Export public key (give to vendors)
gpg --armor --export your@email.com > public.asc

# Encrypt message to vendor
gpg --encrypt --armor -r vendor@market.onion message.txt

# Decrypt vendor message
gpg --decrypt message.asc
```

### Placing Orders

**Checklist:**
- ✓ Verify vendor feedback (95%+ rating, 100+ sales)
- ✓ Check vendor PGP key
- ✓ Encrypt shipping address with vendor's PGP
- ✓ Use market escrow (never direct pay/FE)
- ✓ Take screenshots of order details

**Encrypted Address Format:**

```
-----BEGIN PGP MESSAGE-----

John Smith
123 Main Street Apt 4B
Seattle WA 98101
USA

-----END PGP MESSAGE-----
```

---

## Phase 5: Operational Security

### Address Security

**Use drops, not home:**
- Vacant house (check utility shutoff dates)
- AirBnB rental (book under fake name)
- UPS Store mailbox (anonymous rental)
- Package locker services

**Home delivery opsec:**
- Use real name (less suspicious)
- Order legal items to same address first
- Don't sign for packages
- Wait 24-48 hours before opening
- Deny knowledge if controlled delivery

### Digital Footprint

```bash
# Clear metadata from images
exiftool -all= image.jpg

# Wipe files securely
shred -vfz -n 10 sensitive_file.txt

# Encrypted containers
veracrypt --create container.hc
veracrypt --mount container.hc /mnt/secure

# RAM-only operations
mkdir /tmp/ramdisk
mount -t tmpfs -o size=1G tmpfs /tmp/ramdisk
# Files deleted on reboot
```

### Communication Security

- **Never discuss markets on clearnet** (Telegram, WhatsApp, etc.)
- **Use Tox or Session** for IM (decentralized, no metadata)
- **PGP encrypt everything** sensitive
- **Assume all comms monitored** after purchase

---

## Phase 6: Receiving Packages

### Identifying Controlled Delivery

**Warning Signs:**
- Package requires signature (unusual for your orders)
- Delivered by unmarked vehicle
- Delivery person lingers near property
- Package feels tampered/resealed

**If Controlled Delivery Suspected:**
1. Do NOT answer door
2. Do NOT accept package
3. If already inside, do NOT open
4. Wait 48-72 hours
5. If no raid, probably safe

### Package Inspection

```
1. Wait 24-48 hours before opening
2. Open in non-residential area if possible
3. Check for:
   - Pinholes in packaging
   - Unusual odors
   - Excessive tape/resealing
4. If suspicious, dispose in public trash
```

---

## Phase 7: Market Scams & Threats

### Common Scams

**Exit Scam:**
- Market operators disappear with escrow funds
- Mitigation: Only keep needed funds in wallet, withdraw after each order

**Phishing:**
- Fake market mirrors steal login credentials
- Mitigation: Verify PGP signed links, bookmark real URL

**Selective Scamming:**
- Vendor ships first few orders, then stops
- Mitigation: Use escrow, check recent feedback

**Vendor Impersonation:**
- Scammer copies vendor name/PGP
- Mitigation: Verify PGP fingerprint, not just name

### Law Enforcement Threats

**Market Takeovers:**
- FBI/Europol seize servers, run market as honeypot
- Mitigation: Watch for sudden changes, mass arrests

**Vendor Busts:**
- Caught vendor's customer list seized
- Mitigation: Use fake names, PGP addresses, burn after receive

---

## Phase 8: Advanced Techniques

### Burner Laptop Setup

```bash
# Boot Tails from USB (leaves no trace)
# OR install QubesOS for compartmentalization

# Never login to personal accounts
# Never reuse hardware for clearnet
# Destroy hardware if compromised
```

### Cryptocurrency Tumbling

```python
# Multi-hop tumbling
BTC → Monero → BTC (different wallet)

# Steps:
1. Send BTC to exchange (KuCoin, TradeOgre)
2. Trade BTC → XMR
3. Withdraw XMR to personal wallet
4. Wait 24-48 hours
5. Send XMR to different exchange
6. Trade XMR → BTC
7. Withdraw to new BTC wallet

# Result: Completely untraceable
```

### Decoy Traffic

```bash
# Generate random Tor traffic to obscure real activity
while true; do
    torsocks curl -s https://www.$(shuf -n1 /usr/share/dict/words).com > /dev/null
    sleep $((RANDOM % 60))
done
```

---

## Phase 9: Products & Pricing (2026)

### Common Categories

**Drugs:**
- Cannabis: $150-300/oz
- MDMA: $40-80/g
- Cocaine: $80-120/g
- LSD: $5-10/tab
- Ketamine: $50-90/g

**Fraud:**
- Credit cards: $5-50 (depending on balance)
- Fullz (ID packages): $50-200
- Bank logins: $100-500
- PayPal accounts: $50-300

**Digital:**
- Hacked accounts (streaming, gaming): $5-50
- Malware/RATs: $50-500
- DDoS services: $20-200/day
- Exploits/0-days: $1K-100K

**Documents:**
- Fake IDs: $100-300
- Passports (scans): $50-200
- Diplomas: $50-150

---

## Phase 10: Legal Disclaimers

**Note:** This guide is for educational and harm reduction purposes. Accessing darkweb markets may be illegal in your jurisdiction. Purchasing illegal items is illegal everywhere. Use at your own risk.

**Harm Reduction:**
- Test substances before use (fentanyl test strips)
- Start with small amounts
- Never use alone
- Have naloxone available for opioids

---

## Tools Reference

```bash
# Tor Browser
https://www.torproject.org/download/

# Tails OS
https://tails.boum.org/

# Monero Wallet
https://www.getmonero.org/downloads/

# PGP (GPG)
sudo apt install gnupg

# VeraCrypt (encryption)
https://www.veracrypt.fr/

# Electrum (Bitcoin wallet)
https://electrum.org/

# Wasabi Wallet (Bitcoin mixing)
https://wasabiwallet.io/
```

---

**Complete darkweb operational guide. Maximum anonymity, maximum security.**
