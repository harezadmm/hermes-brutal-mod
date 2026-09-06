# 🧠 RedMess Smart Systems

## Anti-Pikun & Token Efficiency

RedMess punya 3 sistem pintar untuk hemat token dan ingat conversation history:

---

## 1. 🎯 Smart Skill Matcher

**Problem:** 188 skills, scan semua = boros token  
**Solution:** Identifikasi skill yang dibutuhkan dari request user

### Cara Kerja
1. **Direct Tool Name Match** - Detect `nmap`, `sqlmap`, `metasploit` langsung
2. **Keyword Mapping** - "sql injection" → web-applications + database-assessment
3. **Scoring System** - Rank tools by relevance (tool name match = +5, category = +3)
4. **Memory Integration** - Frequent skills dari history user
5. **Top 5 Only** - Return max 5 most relevant skills

### Usage

```bash
# CLI
python3 /root/smart_skill_matcher.py "aku mau scan website cari sql injection"

# Output:
# 1. 🔥 web-applications/sqlmap (HIGH confidence)
# 2. ⚡ vulnerability-analysis/nikto (MEDIUM)
# 3. ⚡ web-applications/gobuster (MEDIUM)
# ...
```

### Integration dengan Hermes

```python
# Dalam conversation, gw akan otomatis:
from smart_skill_matcher import identify_skills

user_request = "aku mau crack wifi"
matched = identify_skills(user_request)  # Returns top 5 skills

# Load ONLY yang relevant:
for skill in matched[:2]:  # Top 2 aja
    skill_view(name=f"red-team-arsenal/{skill['skill']}")
```

### Keyword Coverage

- **Scanning:** nmap, masscan, recon
- **Web:** sql injection, xss, directory brute
- **Passwords:** crack, brute, hash
- **Wireless:** wifi, wpa, aircrack
- **Exploitation:** exploit, shell, payload
- **Network:** mitm, arp, sniff
- **Cloud:** aws, azure, s3
- **Mobile:** apk, android, frida

---

## 2. 💾 Persistent Memory System

**Problem:** Hermes lupa conversation sebelumnya  
**Solution:** Save history, skill usage, patterns ke disk

### Features

#### Conversation History
- Save 100 conversations terakhir
- Timestamp, request, skills used, outcome
- Query by time range (last 24h, 7d, etc)

#### Skill Usage Stats
- Track berapa kali skill dipakai
- Identify favorite tools
- Suggest next skills based on patterns

#### User Patterns Detection
- Common keywords dari requests
- Preferred categories
- Typical targets

#### Session Context
- Current target (IP, domain, network)
- Session notes
- Active skills in use

### Usage

```bash
# View summary
redmess-memory summary

# Most used skills
redmess-memory frequent

# Last 24h activity
redmess-memory recent

# Detect patterns
redmess-memory patterns

# Current context
redmess-memory context
```

### Python API

```python
from redmess_memory import RedMessMemory

memory = RedMessMemory()

# Record conversation
memory.add_conversation(
    user_request="scan 192.168.1.1",
    skills_loaded=["information-gathering/nmap"],
    outcome="Found 22 open ports"
)

# Get frequent skills
freq = memory.get_frequent_skills(5)
# Returns: [("web-applications/sqlmap", 15), ...]

# Get recent context
recent = memory.get_recent_context(hours=24)

# Set current target
memory.set_context(
    target="192.168.1.100",
    notes="Corporate network, authenticated scan"
)

# Suggest next skills
next_skills = memory.suggest_next_skills(["information-gathering/nmap"])
# Returns: ["vulnerability-analysis/nikto", "web-applications/gobuster"]
```

### Memory File Location
```
~/.hermes/profiles/umi3/redmess_memory.json
```

---

## 3. 🔄 Daily Auto-Update

**Problem:** Tools baru keluar tiap hari  
**Solution:** Cron job scrape GitHub + awesome-lists daily

### Sources
- **Awesome Pentest Lists:** 400+ repos (no rate limit)
- **GitHub Trending:** Security topics
- **Exploit-DB:** New exploits
- **Kali Repos:** Package updates

### Schedule
- **Time:** 3:00 AM WIB daily (20:00 UTC)
- **Logs:** `/root/.cache/arsenal_scraper/logs/`
- **Limit:** Max 50 new tools per day

### Manual Trigger
```bash
arsenal update
```

---

## 🚀 Complete Workflow Example

### Scenario: User mau test SQL injection

```python
# User request
"aku mau test website target.com buat sql injection"

# Step 1: Smart Skill Matcher (automatic)
matched = identify_skills(request)
# Returns:
# 1. web-applications/sqlmap (HIGH)
# 2. vulnerability-analysis/nikto (MEDIUM)

# Step 2: Load ONLY top skill (hemat token!)
skill_view(name='red-team-arsenal/web-applications/sqlmap')

# Step 3: Record to memory
memory.add_conversation(
    user_request=request,
    skills_loaded=["web-applications/sqlmap"],
    outcome=None  # Will update later
)

# Step 4: User execute
# ... sqlmap running ...

# Step 5: Memory suggest next
next_skills = memory.suggest_next_skills(["web-applications/sqlmap"])
# Suggests: ["web-applications/gobuster", "exploitation/metasploit-framework"]
```

---

## 📊 Token Savings

### Before (Naive Approach)
```
Load all 188 skills → ~500K tokens
User: "aku mau scan nmap"
Response: Scan through 188 skills
```

### After (Smart System)
```
Smart Matcher: Identify 5 relevant → ~5K tokens
Load top 2 skills → ~10K tokens
Total: ~15K tokens (97% savings!)
```

---

## 🛠️ Files & Commands

### Scripts
```
/root/smart_skill_matcher.py    - Skill identifier
/root/redmess_memory.py         - Memory system
/root/arsenal_cli.py            - Arsenal management
/root/daily_arsenal_scraper.py  - Auto-update scraper
```

### Commands
```bash
# Skill matching
python3 /root/smart_skill_matcher.py "<request>"

# Memory management
redmess-memory summary|frequent|recent|patterns|context|reset

# Arsenal management
arsenal list|search|stats|install|update
```

### Integration
```python
# Di conversation Hermes, automatic:
1. Parse user request
2. Run smart_skill_matcher.identify_skills(request)
3. Load top 2-3 skills only
4. Record to memory.add_conversation()
5. Suggest next skills if relevant
```

---

## 🔐 Memory Privacy

- **Local only:** File stored di `~/.hermes/profiles/umi3/`
- **No cloud:** Data ga pernah upload
- **User control:** `redmess-memory reset` untuk clear
- **Sensitive data:** Request truncated to 300 chars

---

## 📈 Statistics (2026-09-04)

```
Total Skills: 188
Categories: 15
Daily Updates: Active (cron 3 AM WIB)
Memory System: Active
Smart Matcher: Active
Token Savings: ~97% vs naive approach
```

---

## 🎯 Next Improvements

- [ ] ML-based skill recommendation
- [ ] Auto-categorization of new tools
- [ ] Collaborative filtering (if multiple users)
- [ ] Skill quality scoring based on outcomes
- [ ] Integration with vulnerability databases
- [ ] Auto-enrichment of skills from usage patterns

---

**Built for LO by Umi**  
**2026-09-04**

*Smart systems make RedMess remember you and save tokens!* 🧠⚡
