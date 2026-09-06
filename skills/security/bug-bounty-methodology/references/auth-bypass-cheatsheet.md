# Auth & Identity Bypass Cheatsheet (JWT, OAuth, SAML, MFA)

Sourced from `skraft9/vulnerability-research` cheatsheets. Enterprise SSO bugs are under-duplicated because scanners can't reach them — high value in bug bounty.

## 1. JWT Attacks

### alg=none bypass
1. Decode header (base64url).
2. Change `"alg": "HS256"` → `"alg": "none"` (also try `None`, `NONE`).
3. Edit payload (e.g. `"role":"admin"`).
4. Strip signature but KEEP the trailing dot: `eyJhbG...uIn0.`

### Key confusion (RS256 → HS256)
1. Get server public key (`/.well-known/jwks.json`).
2. Set header alg to `HS256`.
3. Sign forged token using the PUBLIC KEY STRING as HMAC secret.

### JWK injection
If header accepts a `jwk` param, inject your own RSA public key + sign with your matching private key:
```json
{"alg":"RS256","jwk":{"kty":"RSA","e":"AQAB","n":"<YOUR_MODULUS>"}}
```

### Offline crack (HS256 symmetric)
```bash
hashcat -a 0 -m 16500 jwt.txt rockyou.txt
```

## 2. OAuth 2.0 / OIDC

### Redirect URI manipulation (token theft)
`redirect_uri` not strictly whitelisted → steal authorization code/token:
- `https://client.com.attacker.com` (subdomain)
- `https://client.com/callback?redirect=https://attacker.com` (open redirect chain)
- `https://client.com%2Eattacker.com` (URL encoding)
- `https://client.com@attacker.com` (credentials syntax)

### CSRF via missing `state`
No `state` param (or unvalidated) → attacker captures auth `code`, drops own request, sends callback URL to victim → victim's session ties to attacker's account (login CSRF).

### Pre-account takeover (implicit trust)
App allows email/password + OAuth login but doesn't verify email:
1. Register `victim@company.com` with attacker password.
2. Victim logs in via "Log in with Google".
3. Accounts merge unverified → attacker retains password access.

## 3. SAML

### XML Signature Wrapping (XSW)
1. Intercept + base64-decode SAML Response.
2. Clone `<Assertion>`, modify clone (e.g. `<NameID>` → `admin@corp.com`).
3. Position so signature validation checks the ORIGINAL but app logic reads the FAKE (wrapper element).
- Tool: **SAML Raider** (Burp) automates XSW.

### Signature stripping
If SP only validates signature when present:
1. Delete `<ds:Signature>` block entirely.
2. Modify assertion, forward.

### XML comment injection
Break username string with XML comments to desync extraction vs DB lookup:
`admin@corp.com.evil.com` with comments positioned to truncate to `admin@corp.com`.

## 4. General Auth / MFA Flaws

### MFA response manipulation
If server sends success/fail to client for routing:
```http
HTTP/1.1 401 Unauthorized
{"success": false, "message": "Invalid Code"}
```
→ rewrite to:
```http
HTTP/1.1 200 OK
{"success": true, "message": "Authenticated"}
```

### Password reset host header poisoning
If reset link is built from `Host` header:
```http
POST /api/reset-password HTTP/1.1
Host: evil-server.com
{"email": "admin@target.com"}
```
Victim receives `https://evil-server.com/reset?token=...` → attacker captures token.

## Key Insight (offensive)
Apps trust tokens that LOOK like they came from Google/Okta/Auth0 without verifying. Always test: stripped signature, algorithm swap, missing state/nonce, dynamic `alg` trust, IdP↔SP parser desync. Find the desync, find the bug.

## Key Insight (defensive)
Never roll your own crypto/parser. Reject `none`/unexpected `alg`. Mandate `state` + PKCE. Disable XXE/DTD in XML parsers before signature validation.
