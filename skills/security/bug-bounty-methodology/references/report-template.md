# Vulnerability Report Template

Use this exact structure for bug bounty submissions. Triage teams skim, so lead with impact and make reproduction trivial.

## Structure (in order)

### 1. Title
Concise, `[Bug Class] in [Component/Feature] allows [Impact]`.
Example: `Stored XSS in profile bio allows account takeover of any visitor`.

### 2. Summary
2-4 sentences: what the bug is, where it lives, what an attacker gains. No fluff.

### 3. Severity
Assign CVSS 3.1 vector + base score. Be honest — inflated severity gets you ignored.
- Critical (9.0-10.0): RCE, full account takeover at scale, mass data exfil.
- High (7.0-8.9): auth bypass, stored XSS → ATO, SSRF to cloud metadata, SQLi.
- Medium (4.0-6.9): reflected XSS, IDOR on low-sensitivity data, CSRF on state change.
- Low (0.1-3.9): info disclosure, missing headers, clickjacking.

### 4. Affected Asset / Endpoint
Exact URL(s), parameter(s), host(s), app version if known.

### 5. Steps to Reproduce
Numbered, unambiguous, reproducible by someone with a fresh account.
Include: account prereqs, every click/request, exact payloads in fenced code blocks.

### 6. Proof of Concept (PoC)
- Raw HTTP request/response (Burp/curl output).
- `curl` one-liner when possible:
```bash
curl -i -s 'https://target.example/api/user/42' \
  -H 'Authorization: Bearer <attacker_token>' \
  -H 'X-Original-User: 1000'
```
- Annotate the key line (the injection point / the leaked field).
- Redact your own tokens/cookies and any real victim PII.

### 7. Impact
Concrete business harm. Never write just the bug class.
- BAD: "IDOR on /api/messages".
- GOOD: "Any logged-in user can read any other user's private messages by changing the `id` parameter, leaking PII across all 2M accounts."

### 8. Remediation
Specific fix, with code/config reference where you know it (parameterized queries, allowlist redirects, etc.).

### 9. References
- CWE ID (e.g. CWE-284, CWE-79, CWE-918, CWE-862).
- OWASP category (ASVS / Top 10).
- Related CVE or public writeup if relevant.

## Quality Checklist (before submitting)

- [ ] Reproducible with steps exactly as written, fresh session.
- [ ] Impact statement names a real-world harm.
- [ ] One vulnerability per report (no unrelated bugs bundled).
- [ ] No sensitive data un-redacted in PoC.
- [ ] Severity matches CVSS, not inflated.
- [ ] No demands, threats, or unprofessional language.
- [ ] No automated-scanner-only findings (verify manually).
- [ ] Not a known duplicate (search program + H1/Bugcrowd first).
