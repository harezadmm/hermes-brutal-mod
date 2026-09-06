# Platform Verification Patterns

Decision table for account-existence checks. Core rule: a "hit" requires page CONTENT evidence, not just an HTTP status.

## Reliable JSON APIs (no auth, no login wall)

| Platform | Endpoint | Exists when |
|---|---|---|
| GitHub | `https://api.github.com/users/USER` | HTTP 200, JSON has `"login"` |
| GitLab | `https://gitlab.com/api/v4/users?username=USER` | non-empty JSON array; gives id, name, state, avatar_url |

GitLab's `avatar_url` contains `secure.gravatar.com/avatar/<sha256-of-email>` — comparing that hash to the target email's SHA256 proves the account belongs to the email owner.

## HTML platforms — status code is NOT enough

| Platform | Status for missing profile | Verification grep on page content |
|---|---|---|
| Pinterest | 200 (lies) | `<title>` contains the display name |
| Instagram | 200 (lies) | `"username"` appears in page JSON; login wall limits confidence |
| Twitch | 200 (lies) | look for the user's display name in embedded JSON |
| Steam | 200 + "The specified profile could not be found" | profile page contains actual persona name |
| YouTube | 404 for missing @handle | `<title>` is the channel name |
| GitLab HTML | 302 → sign-in for missing | `<title>NAME · GitLab</title>` |
| Facebook | 200 login wall | effectively unverifiable without a session — mark inconclusive |

Generic pattern:

```bash
curl -sL -A "$UA" "https://platform/USER" -o page.html
grep -oE '<title>[^<]*</title>' page.html   # title should name the profile, not "Not Found"/login
```
## Gravatar details

- Hash input is the email **trimmed and lowercased**, MD5 (legacy) or SHA256 (newer).
- `https://gravatar.com/<hash>.json` — 404 means no profile; 200 returns `entry[0].name`, `hash`, `preferredUsername`, thumbnail URLs.
- `https://gravatar.com/<hash>.vcf` — vCard with FN (full name), nickname, URLs, timezone, base64 photo.
- `https://gravatar.com/<hash>` — HTML profile page, also works with the username slug.
- Check BOTH MD5 and SHA256 — some accounts only respond to one.

## Known dead ends (don't retry these without new tooling)

- Reddit `/user/X/about.json` — bot-blocked from server IPs; inconclusive.
- HIBP — 401 without a paid API key.
- Facebook/Instagram full verification — login walls; report as inconclusive unless a browser session is used.
