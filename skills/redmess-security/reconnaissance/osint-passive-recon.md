---
description: OSINT reconnaissance without touching target infrastructure
category: security/reconnaissance
tags: [osint, recon, passive, information-gathering, no-touching]
platform: [linux, windows]
difficulty: beginner
tools: [google, shodan, wayback-machine, whois, censys]
mitre_attack: [T1592, T1593, T1594]
---

# Passive OSINT Reconnaissance

## When to Use
Use passive OSINT when you need intelligence on target WITHOUT alerting them:
- Identify attack surface (subdomains, IPs, technologies)
- Find employee information (phishing targets)
- Discover leaked credentials
- Map organizational structure
- Identify security weaknesses
- Pre-engagement reconnaissance

"Passive" means: NO direct interaction with target systems. All data from public sources.

## Prerequisites
- Internet connection
- Basic command-line skills
- OSINT mindset (curiosity + patience)
- Note-taking system (CherryTree, Obsidian, Notion)

## OSINT Workflow

```
1. Define Scope
   └─► What are you looking for? (domains, people, tech stack)

2. Gather Public Data
   ├─► Search engines (Google dorking)
   ├─► Public databases (WHOIS, DNS, certs)
   ├─► Social media (LinkedIn, Twitter, GitHub)
   ├─► Leaked data (Have I Been Pwned, Dehashed)
   └─► Archive sites (Wayback Machine)

3. Analyze & Correlate
   └─► Connect the dots, identify patterns

4. Document Findings
   └─► Create attack surface map
```

## Step-by-Step

### 1. Initial Target Profiling

**Domain WHOIS:**
```bash
# Get domain registration info
whois target.com

# Key info to note:
# - Registrant name/email
# - Registration date (how old is org?)
# - Name servers (hosting provider)
# - Registrar (GoDaddy, Namecheap, etc)
```

**IP Address Lookup:**
```bash
# Find IP address of domain
dig target.com +short
nslookup target.com

# Reverse DNS (IP to domain)
dig -x 203.0.113.45 +short

# Find IP range owned by organization
whois 203.0.113.45 | grep -i "netrange\|cidr"
```

**ASN Lookup (Autonomous System):**
```bash
# Find all IPs owned by organization
# Visit: https://bgp.he.net/
# Enter organization name → View ASN → Prefixes
# Lists all IP ranges owned

# Or use CLI
curl -s "https://api.bgpview.io/search?query_term=Tesla" | jq
```

### 2. Subdomain Enumeration (Passive)

**Certificate Transparency Logs:**
```bash
# crt.sh - finds subdomains from SSL certificates
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# Filter wildcard certs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | grep -v '*' | sort -u
```

**DNS Aggregators:**
```bash
# SecurityTrails (requires free API key)
curl -s "https://api.securitytrails.com/v1/domain/target.com/subdomains" \
  -H "APIKEY: YOUR_KEY" | jq -r '.subdomains[]' | sed 's/$/.target.com/'

# Censys (passive cert search)
# Visit: https://search.censys.io/
# Search: parsed.names: target.com

# VirusTotal (passive DNS)
# Visit: https://www.virustotal.com/gui/domain/target.com/relations
```

**Wayback Machine (Historical Subdomains):**
```bash
# Install waybackurls
go install github.com/tomnomnom/waybackurls@latest

# Find all historical URLs
echo "target.com" | waybackurls | unfurl domains | sort -u
```

### 3. Google Dorking

**Find hidden admin panels:**
```
site:target.com inurl:admin
site:target.com intitle:"index of"
site:target.com inurl:login
site:target.com inurl:dashboard
site:target.com filetype:php inurl:admin
```

**Find exposed files:**
```
site:target.com filetype:pdf
site:target.com filetype:xls | filetype:xlsx
site:target.com filetype:doc | filetype:docx
site:target.com filetype:sql
site:target.com filetype:env
site:target.com filetype:log
```

**Find sensitive information:**
```
site:target.com "confidential"
site:target.com "internal use only"
site:target.com "not for distribution"
site:target.com intext:"password" | intext:"username"
site:target.com intext:"api_key" | intext:"apikey"
```

**Find technology stack:**
```
site:target.com "powered by"
site:target.com "built with"
site:target.com inurl:wp-content (WordPress)
site:target.com inurl:/phpmyadmin
```

**GitHub code search:**
```
# Search GitHub for exposed secrets
org:target "api_key"
org:target "password"
org:target "secret"
org:target "credentials"
user:employeename target.com
filename:.env target
```

### 4. Employee Enumeration

**LinkedIn:**
```
# Manual search on LinkedIn:
# - Company page → People
# - Note: job titles, email patterns, technologies mentioned

# Email pattern discovery:
# John Smith → jsmith@target.com
# John Smith → john.smith@target.com
# John Smith → smithj@target.com

# Use Hunter.io or RocketReach to verify patterns
```

**Social Media:**
```
# Twitter
site:twitter.com "target.com"
site:twitter.com "@targetcorp"

# Facebook
site:facebook.com "works at Target Corp"

# GitHub (employees' personal projects)
site:github.com "target.com"
```

**Job Postings:**
```
site:linkedin.com "Target Corp" "seeking"
site:indeed.com "target.com"

# Look for tech stack in job descriptions:
# "Experience with AWS, Docker, PostgreSQL"
# = Target uses AWS, Docker, PostgreSQL
```

### 5. Leaked Credentials

**Have I Been Pwned:**
```bash
# Check if emails leaked in breaches
# Visit: https://haveibeenpwned.com/
# Enter: employee@target.com

# Or use API
curl "https://haveibeenpwned.com/api/v3/breachedaccount/employee@target.com"
```

**Dehashed (requires paid subscription):**
```bash
# Search for leaked credentials
# Visit: https://dehashed.com/
# Search: email:target.com
# Search: domain:target.com

# Returns: email, username, password, hash
```

**Pastebin & Paste Sites:**
```
site:pastebin.com "target.com"
site:pastebin.com "target.com" password
site:ghostbin.com "target.com"
```

### 6. Technology Profiling

**Wappalyzer (Browser Extension):**
```
# Install: https://www.wappalyzer.com/
# Visit target.com
# Extension shows: CMS, frameworks, analytics, CDN, etc
```

**BuiltWith:**
```
# Visit: https://builtwith.com/target.com
# Shows: hosting, CDN, CMS, JavaScript libraries, analytics
```

**Shodan (Passive Mode):**
```bash
# Find internet-facing services WITHOUT scanning
# Visit: https://www.shodan.io/
# Search: hostname:target.com
# Search: org:"Target Corp"

# Shows: open ports, services, versions, vulnerabilities
# All from Shodan's existing scan data (passive)

# CLI (requires API key)
shodan search hostname:target.com
shodan search org:"Target Corp"
```

**Censys:**
```bash
# Similar to Shodan
# Visit: https://search.censys.io/
# Search: target.com
# Search: services.tls.certificates.leaf_data.subject.common_name: target.com

# Shows: certificates, open ports, services
```

### 7. Dark Web & Forums

**Telegram Channels:**
```
# Search for leaked data on Telegram
# Channels often leak databases, credentials
# Search: "target.com" in InfoSec channels
```

**Dark Web Markets:**
```
# Access via Tor
# Markets selling:
# - Database dumps
# - Corporate credentials
# - VPN access
# Search for organization name
```

**Hacker Forums:**
```
# Visit (via Tor or clearnet):
# - RaidForums (seized, but archives exist)
# - Breached.to
# - Nulled.to
# Search for: target company name
```

### 8. Wayback Machine (Historical Analysis)

```bash
# Find old versions of website
# Visit: https://web.archive.org/
# Enter: target.com

# Look for:
# - Old admin panels (removed but still exist)
# - Employee names in old blog posts
# - Old technologies mentioned
# - Deprecated endpoints

# CLI tool
waybackurls target.com | tee wayback_urls.txt

# Find sensitive paths
cat wayback_urls.txt | grep -iE "(admin|login|api|key|token|password)"
```

### 9. Document & Organize

**Create Target Profile:**
```
Target: Target Corp (target.com)
═══════════════════════════════════════

[1] DOMAINS & IPs
Primary: target.com (203.0.113.45)
Subdomains:
  - mail.target.com
  - vpn.target.com
  - dev.target.com
IP Range: 203.0.113.0/24 (AS12345)

[2] TECHNOLOGY STACK
Web Server: Nginx 1.21.0
Framework: React, Node.js
Database: PostgreSQL (from job postings)
Cloud: AWS (S3 buckets, EC2)
CDN: CloudFlare

[3] EMPLOYEES (Sample)
- John Smith (CISO) - jsmith@target.com
- Jane Doe (Dev Manager) - jane.doe@target.com
Email Pattern: firstname.lastname@target.com

[4] LEAKED CREDENTIALS
- 5 employees in LinkedIn breach (2021)
- 1 developer GitHub token exposed (removed)

[5] ATTACK SURFACE
- VPN portal: vpn.target.com (FortiGate SSL VPN)
- Admin panel: admin.target.com (custom CMS)
- API: api.target.com (REST, no auth on /docs)

[6] POTENTIAL VULNERABILITIES
- Old WordPress on blog.target.com (v4.9.8)
- Exposed phpMyAdmin on dev subdomain
- S3 bucket public read: target-backups.s3.amazonaws.com
```

## Automation Tools

**theHarvester:**
```bash
# All-in-one OSINT tool
theHarvester -d target.com -b all

# Specific sources
theHarvester -d target.com -b google,bing,linkedin,twitter
```

**Recon-ng:**
```bash
# Modular OSINT framework
recon-ng
> workspaces create target_corp
> db insert domains target.com
> modules search
> modules load recon/domains-hosts/certificate_transparency
> run
```

**Spiderfoot:**
```bash
# Automated OSINT
spiderfoot -s target.com -m all -o json > output.json
```

**OSINT Framework:**
```
# Comprehensive tool list
# Visit: https://osintframework.com/
# Browse by category (Domain, Username, Email, etc)
```

## Pitfalls & OPSEC

**Common Mistakes:**
- **Clicking links on target site** — Logs your IP, not passive
- **Running Nmap** — Active scanning, will be detected
- **Creating LinkedIn profiles to view employees** — Tracked
- **Directly accessing found admin panels** — Not passive, logs IP

**Staying Passive:**
- ✅ Google search: `site:target.com` (passive)
- ✅ Shodan search: `hostname:target.com` (passive, Shodan's data)
- ✅ WHOIS lookup (passive, public record)
- ❌ Visiting `http://target.com/admin` (active, logs IP)
- ❌ Nmap scan (active, VERY detectable)

**OPSEC Improvements:**
- Use VPN or Tor for all searches
- Don't use personal accounts (LinkedIn, GitHub)
- Separate OSINT infrastructure from personal
- Don't save sensitive findings to cloud (Notion, Google Docs)

## Verification

```bash
# Validate findings
# - Subdomains resolve? dig subdomain.target.com
# - IPs belong to target? whois <IP>
# - Emails valid? theHarvester email validation
# - Leaked creds work? (ONLY IF AUTHORIZED - testing = illegal)
```

## Related Skills
- `google-dorking-advanced` — Deep search operator techniques
- `subdomain-enumeration-active` — Active subdomain discovery
- `employee-phishing-recon` — Targeted phishing research
- `dark-web-monitoring` — Monitor dark web for org mentions

## References
- [OSINT Framework](https://osintframework.com/)
- [Awesome OSINT](https://github.com/jivoi/awesome-osint)
- [OSINT Techniques](https://www.osinttechniques.com/)
- [IntelTechniques](https://inteltechniques.com/menu.html)

---

**LEGAL NOTE:** Passive OSINT is generally legal (public information). However, using discovered information for unauthorized access or attacks is ILLEGAL. Only proceed to active testing with written authorization.
