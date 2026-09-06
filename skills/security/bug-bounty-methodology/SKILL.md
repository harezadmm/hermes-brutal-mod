---
name: bug-bounty-methodology
description: Use when hunting bug bounties or writing vuln reports.
---

# Bug Bounty Methodology

Distilled from three repos: `yaklang/hack-skills` (102 vuln-class skills), `matty69v/Bug-Bounty-Agents` (agent prompts), `skraft9/vulnerability-research` (cheatsheets + templates). Bug bounty differs from pentest: scope is tighter, duplicates cost money, and report quality directly determines payout.

## Scope Discipline (NON-NEGOTIABLE)

Before running ANY command against a target:
1. Get the user to declare scope (domains, URLs, IP ranges, cloud accounts) + engagement type.
2. No declared scope → analyze pasted output only (advisory mode), never execute.
3. Verify every target falls in scope before each command. Out-of-scope = refuse and explain.

### OPSEC noise tagging (tag every command)
- **QUIET** — passive: DNS, WHOIS, cert transparency, robots.txt/sitemap.
- **MODERATE** — active but common: TCP connect scan (`-sT`), HTTP requests, banner grabs.
- **LOUD** — triggers IDS/WAF/SOC: vuln scans, brute force, aggressive enum, NSE beyond default.

Rules: least aggressive first, rate-limit by default, save evidence to timestamped files, never pipe untrusted output into shell (`| bash`, `| sh`, `eval`, backticks).

## Target Selection

Good programs: recently launched/updated, large scope, fast response + fair payouts, accept wide vuln types, complex business logic (fintech/healthcare/SaaS).
Avoid: months-long response times, points-only, narrow scope, programs that mark valid reports informational.

## Recon Pipeline (passive first)

```bash
# Subdomain enum
subfinder -d {domain} -silent | sort -u > subs.txt
amass enum -passive -d {domain} >> subs.txt

# Live hosts + tech
httpx -l subs.txt -silent -sc -title -td -ip -o alive.txt
whatweb -i alive.txt --log-json tech.json

# JS endpoints + params from archives
cat alive.txt | waybackurls | grep "\.js$" | sort -u > js.txt
cat alive.txt | waybackurls | grep "?" | sort -u > params.txt

# Subdomain takeover
subjack -w subs.txt -t 100 -timeout 30 -ssl -o takeover.txt
```

## Content Discovery (progressive wordlists)

```bash
ffuf -u https://{target}/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -rate 50 -timeout 10
```
- Start small (~4.6k `common.txt`), then medium (~220k dirbuster), then SecLists/tech-specific, then custom.
- Filter noise with `-fs` (size) / `-fw` (word count) / `-fc` (status).
- Always test backups/artifacts: `.bak` `.old` `.swp` `.git` `.env` `web.config` `wp-config.php.bak`.

## Highest-Payout Vulnerability Classes

1. **IDOR/BOLA + privilege escalation** — create two accounts, replay victim requests with attacker session, swap resource IDs.
2. **Business logic** — race conditions (payment/coupon), price manipulation, workflow bypass, negative qty, currency rounding. These are rarely duplicates because scanners can't find them.
3. **Auth bypass** — password reset, 2FA bypass, session mgmt, OAuth redirect_uri/state/PKCE (see `references/auth-bypass-cheatsheet.md`).
4. **SSRF** — any URL-input param (webhooks, image URL, import). Target `http://169.254.169.254/latest/meta-data/`.
5. **Stored XSS** (higher payout than reflected) where CSP is weak.

## Avoiding Duplicates

- Go deep on one target, not surface-level on many. Business logic > scanning.
- Hunt new features/releases (changelogs, app updates, job postings = new attack surface).
- Unique surface: mobile apps, thick clients, IoT, internal tools.
- Chain low-severity bugs (self-XSS + CSRF → stored XSS) — chains are rarely duplicated.

## Report Writing (see references/report-template.md)

Report quality = bounty vs "not applicable". Rules:
- Reproducible steps mandatory — if triage can't reproduce, it's closed.
- Show IMPACT, not just the bug ("reads other users' private messages" beats "IDOR on /api/messages").
- Include exact HTTP request/response (redact sensitive data, annotate key parts).
- Screenshot/video for complex bugs. One vuln per report (unless same root cause).
- Professional tone — no demands/threats. Don't inflate CVSS; programs respect accuracy.
- Structure: Title → Summary → Severity(CVSS) → Steps to Reproduce → PoC → Impact → Remediation → References (CWE/OWASP/CVE).

## Platform Notes

- **HackerOne**: use "Weakness" field accurately (maps to CWE); Signal/Impact scores gate future invites.
- **Bugcrowd**: P1-P5 (P1 critical), VRT taxonomy determines priority — be precise.
- **Intigriti**: EU/GDPR-heavy, triage gives feedback, leaderboard reputation.

## Behavioral Rules

1. Build a methodology, not a checklist — understand the app's purpose, test against its business logic.
2. If input responds unexpectedly (slight delay, odd error code), keep pulling that thread.
3. Read disclosed reports + vendor advisories + patch diffs — fastest way to level up.
4. Practice on PortSwigger Web Security Academy labs (safe, black-box).
5. Repeated failure/dead-ends is normal — it takes hundreds of hours to find a real vuln.
6. Duplicates sting but validate the finding — sweep for sibling vulns, apply the knowledge forward.

## ATT&CK Anchors

- Recon: T1595 (Active Scanning), T1592 (Gather Victim Host Info)
- Initial Access: T1190 (Exploit Public-Facing Application), T1078 (Valid Accounts)
- Discovery: T1083 (File/Dir Discovery), T1046 (Network Service Discovery)
- Impact: T1565 (Data Manipulation)
