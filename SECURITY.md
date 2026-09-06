# Security Policy

## Reporting Vulnerabilities in RedMess

If you discover a security vulnerability **in RedMess itself** (not in the tools/exploits it helps create), we want to know about it.

### What Qualifies as a RedMess Vulnerability?

✅ **Report These:**
- Command injection in RedMess code
- Path traversal allowing unauthorized file access
- Privilege escalation in installation scripts
- Code execution via malicious skill files
- Authentication bypass in Telegram gateway
- Memory leaks causing crashes
- Backdoors in the codebase

❌ **Don't Report These:**
- Vulnerabilities in tools RedMess helps create (that's the point)
- "RedMess can generate malware" (intended feature)
- "AI says bad things" (no content filtering by design)
- Exploits discovered using RedMess (disclose to affected vendor)

### How to Report

**Email:** `security@redmess.dev`

Include:
- **Description** - What's the vulnerability?
- **Impact** - What can an attacker do?
- **Reproduction** - Step-by-step POC
- **Affected versions** - Which releases are vulnerable?
- **Suggested fix** - Optional but appreciated

### What to Expect

- **24-hour response** - We'll acknowledge your report
- **7-day initial assessment** - Severity classification
- **30-day fix timeline** - For critical issues
- **90-day disclosure** - Coordinated disclosure after patch

### Bug Bounty

We don't have a formal bug bounty program yet, but:

- **Critical vulnerabilities** - We'll credit you prominently
- **High-severity issues** - Named in security advisory
- **Pull request preferred** - Submit a fix for faster resolution

### Severity Classification

**Critical** (Patch within 7 days)
- Remote code execution
- Authentication bypass
- Arbitrary file write with privilege escalation

**High** (Patch within 30 days)
- Local privilege escalation
- Information disclosure of credentials
- Denial of service

**Medium** (Patch within 90 days)
- XSS in web interface
- Path traversal without privilege escalation
- Memory exhaustion

**Low** (Patch when convenient)
- Information disclosure (non-sensitive)
- Minor bugs with no security impact

---

## Coordinated Disclosure

We follow coordinated disclosure:

1. **Day 0** - You report vulnerability privately
2. **Day 1** - We acknowledge and start investigation
3. **Day 7** - Initial assessment and timeline
4. **Day 30-90** - Patch developed and tested
5. **Day of patch** - Security advisory published, credit given
6. **Day 90** - If no patch, we allow public disclosure

If you want to publish before 90 days, let us know. We prefer coordination but respect researcher choice.

---

## Security Best Practices for Users

### Using RedMess Safely

1. **Isolated Environment**
   - Run in Docker or VM
   - Don't run on your main machine
   - Use separate network for testing

2. **API Key Security**
   - Use separate API keys for RedMess
   - Rotate keys regularly
   - Don't commit keys to version control

3. **Telegram Bot Security**
   - Use strong bot tokens
   - Enable 2FA on Telegram account
   - Restrict bot to authorized users only
   - Set `OWNER_IDS` in config

4. **File System Isolation**
   - RedMess has full file system access
   - Don't run as root unless necessary
   - Use AppArmor/SELinux profiles

5. **Network Isolation**
   - Assume RedMess can exfiltrate data
   - Use network segmentation
   - Monitor outbound traffic

### Threat Model

**What RedMess protects against:**
- ✅ Unauthorized users accessing your instance
- ✅ API key leakage (not stored in plaintext)
- ✅ Command injection (sanitized inputs)

**What RedMess does NOT protect against:**
- ❌ Malicious AI model responses (user responsibility)
- ❌ Exfiltration via AI provider (use local models)
- ❌ Social engineering the AI (GODMODE disables refusals)
- ❌ Forensic analysis of conversation history

### OPSEC for Offensive Use

If using RedMess for red team operations:

1. **Attribution Evasion**
   ```bash
   # Use VPN/Tor
   torsocks redmess
   
   # Clear bash history
   export HISTFILE=/dev/null
   
   # Use burner API keys
   hermes config set openai.api_key $BURNER_KEY
   ```

2. **Conversation Security**
   - Conversations are stored locally in `~/.hermes/`
   - Encrypt home directory
   - Use ephemeral VMs
   - Wipe after operations

3. **C2 Infrastructure**
   - Don't hardcode real C2 servers in prompts
   - Use placeholders in generated malware
   - Manually edit before deployment

4. **Legal Protection**
   - Get written authorization before testing
   - Document scope and timeline
   - Store authorization letters securely

---

## Known Security Considerations

### By Design

These are **intentional** and not vulnerabilities:

1. **No Content Filtering**
   - RedMess will generate malware, exploits, and illegal content
   - This is core functionality, not a bug
   - Users are responsible for legal compliance

2. **Full System Access**
   - RedMess can execute arbitrary commands
   - It can read/write any file
   - Run in isolated environments

3. **Conversation Logging**
   - All conversations stored locally
   - Includes generated exploits and malware
   - Encrypt storage or use ephemeral environments

4. **AI Model Access**
   - Conversations sent to AI provider (Anthropic, OpenAI, etc.)
   - Providers may log requests
   - Use local models for sensitive operations

### Mitigations

1. **Docker Isolation** (Recommended)
   ```bash
   hermes setup terminal
   # Select Docker backend
   # Commands run in container, not host
   ```

2. **User Restrictions**
   ```python
   # In Telegram bot config
   OWNER_IDS = [123456789]  # Only you
   RENTAL_ENABLED = False   # No sharing
   ```

3. **API Key Rotation**
   ```bash
   # Monthly rotation
   hermes config set anthropic.api_key $NEW_KEY
   ```

4. **Audit Logging**
   ```bash
   # Enable detailed logs
   hermes config set logging.level debug
   tail -f ~/.hermes/logs/agent.log
   ```

---

## Incident Response

If you believe your RedMess instance is compromised:

1. **Immediate Actions**
   - Disconnect from network
   - Revoke API keys (Anthropic, OpenAI, etc.)
   - Rotate Telegram bot token if applicable
   - Stop all running processes

2. **Investigation**
   - Check conversation history: `~/.hermes/conversations/`
   - Review command history: `~/.hermes/logs/`
   - Inspect running processes: `ps aux | grep hermes`
   - Check network connections: `netstat -tuln`

3. **Remediation**
   - Wipe conversations: `rm -rf ~/.hermes/conversations/*`
   - Reinstall RedMess: `./install.sh`
   - Change all credentials
   - Review generated code for backdoors

4. **Report to Us**
   - Email: `security@redmess.dev`
   - Include incident timeline
   - Share IOCs if applicable

---

## Supply Chain Security

### How We Protect You

1. **Signed Releases**
   - All releases GPG-signed
   - Verify before installing:
     ```bash
     gpg --verify redmess-v1.0.0.tar.gz.sig
     ```

2. **Dependency Pinning**
   - `requirements.txt` uses exact versions
   - No wildcard version ranges
   - Regular dependency audits

3. **Code Review**
   - All PRs reviewed before merge
   - No force-pushes to main
   - Commit signing required

4. **No Telemetry**
   - RedMess doesn't phone home
   - No usage tracking
   - No crash reporting
   - Audit the code yourself

### How You Can Verify

```bash
# Clone and audit
git clone https://github.com/harezadmm/RedMess.git
cd RedMess

# Check for suspicious network calls
grep -r "requests.post" .
grep -r "urllib" .
grep -r "socket" .

# Review dependencies
cat requirements.txt
pip install pipdeptree
pipdeptree

# Run in isolated environment
docker build -t redmess .
docker run --rm --network none redmess
```

---

## Cryptographic Practices

RedMess uses cryptography for:

1. **API Key Storage**
   - Keys encrypted at rest
   - OS keyring integration (when available)
   - Fallback: XOR obfuscation (not secure, use keyring)

2. **Telegram Bot Tokens**
   - Stored in config file (plaintext)
   - User responsible for file permissions
   - Recommend: `chmod 600 ~/.hermes/config.yaml`

3. **Conversation Encryption** (Optional)
   ```bash
   # Enable encryption
   hermes config set encryption.enabled true
   hermes config set encryption.key $(openssl rand -hex 32)
   ```

---

## Compliance

### GDPR (EU Users)

RedMess processes:
- Conversation history (locally stored)
- User IDs (Telegram, Discord)
- API keys (encrypted)

**Your rights:**
- Access: `cat ~/.hermes/conversations/*`
- Deletion: `rm -rf ~/.hermes/`
- Portability: Copy `~/.hermes/` directory

**No data sent to maintainers** unless you report a bug.

### CCPA (California Users)

Same as GDPR. We don't collect data centrally.

### Export Control (ITAR/EAR)

RedMess may contain:
- Strong cryptography (export-controlled)
- Offensive security tools (export-controlled)

**Users are responsible for compliance with:**
- US Export Administration Regulations (EAR)
- International Traffic in Arms Regulations (ITAR)
- Local export control laws

Do not use RedMess in embargoed countries without proper licenses.

---

## Contact

- **Security Issues:** security@redmess.dev
- **General Questions:** GitHub Discussions
- **Urgent Matters:** Telegram `@harezadmm`

**PGP Key for security@redmess.dev:**
```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[Key would go here in real implementation]
-----END PGP PUBLIC KEY BLOCK-----
```

---

<p align="center">
  <i>Last updated: 2026-09-04</i>
</p>

<p align="center">
  <b>Security is a shared responsibility. Report issues responsibly.</b>
</p>
