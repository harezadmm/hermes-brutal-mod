# Production Auth System for API Router

Complete authentication system with MySQL + SQLite fallback for production API router deployments.

## Architecture

```
User → Login/Register → Session Token (30 days) → API Key (yr-xxx format)
                                ↓
                        Dashboard shows:
                        - Default API key
                        - Base URL (router.umiagent.my.id/api/v1)
                        - Copy buttons
                        - Quick setup for Hermes Agent
```

## Database Schema

### MySQL (Production) / SQLite (Development)

**users table:**
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- SHA256 + salt
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**api_keys table:**
```sql
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    api_key VARCHAR(100) UNIQUE NOT NULL,  -- Format: yr-{timestamp}-{random}
    key_name VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    request_count INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_api_key (api_key),
    INDEX idx_user_id (user_id)
);
```

**sessions table:**
```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(100) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,  -- 30 days from creation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_token (session_token),
    INDEX idx_expires (expires_at)
);
```

**usage_logs table:**
```sql
CREATE TABLE usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    api_key VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    upstream VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    request_size INT,
    response_size INT,
    tokens_used INT,
    status_code INT,
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_created (created_at)
);
```

**router_settings table:**
```sql
CREATE TABLE router_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    active_upstream VARCHAR(50) DEFAULT 'lapakvip',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**user_balance table:**
```sql
CREATE TABLE user_balance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    credits INT DEFAULT 0,
    total_earned INT DEFAULT 0,
    total_spent INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## API Key Format

**Format:** `yr-{timestamp_hex}-{random_hex}`

**Example:** `yr-6a8fb755-c81c7d9547bc9cfb77a399b0e5241ee8`

**Generation:**
```python
import secrets
import time

def generate_api_key():
    timestamp = hex(int(time.time()))[2:]
    random_part = secrets.token_hex(16)
    return f"yr-{timestamp}-{random_part}"
```

**Benefits:**
- Globally unique (timestamp + 128-bit random)
- Chronologically sortable
- Impossible collisions
- Easy to identify (yr- prefix = UmiAgent Router)

## Password Security

**Hash format:** `{salt}${hash}`

**Implementation:**
```python
import hashlib
import secrets

def hash_password(password):
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password, stored_hash):
    salt, pwd_hash = stored_hash.split('$')
    return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
```

## Session Management

**Token format:** URL-safe base64 (32 bytes)

**Generation:**
```python
import secrets
from datetime import datetime, timedelta

session_token = secrets.token_urlsafe(32)
expires_at = datetime.now() + timedelta(days=30)
```

**Validation:**
```python
# Check token + expiry + user active status
SELECT u.id, u.username 
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE s.session_token = %s 
  AND s.expires_at > NOW() 
  AND u.is_active = TRUE
```

## Backend Endpoints

### Auth Endpoints

**POST /api/auth/register**
```json
Request:
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123",
  "full_name": "John Doe"
}

Response:
{
  "success": true,
  "api_key": "yr-6a8fb755-...",
  "session_token": "PGwwX5aQoslYvzy...",
  "user_id": 1
}
```

**POST /api/auth/login**
```json
Request:
{
  "username": "johndoe",  // or email
  "password": "secret123"
}

Response:
{
  "success": true,
  "session_token": "PGwwX5aQoslYvzy...",
  "user_id": 1,
  "default_api_key": "yr-6a8fb755-..."
}
```

**GET /api/auth/me**
```
Headers: Authorization: Bearer {session_token}

Response:
{
  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "keys": [{
    "id": 1,
    "api_key": "yr-6a8fb755-...",
    "key_name": "Default Key",
    "active": true,
    "created_at": "2026-08-27T10:00:00",
    "last_used": "2026-08-27T11:00:00",
    "request_count": 150,
    "total_tokens": 50000
  }],
  "stats": {
    "credits": 10000,
    "total_earned": 10000,
    "total_spent": 0,
    "total_requests": 150,
    "active_keys": 1,
    "requests_24h": 50,
    "tokens_24h": 15000,
    "bytes_24h": 500000
  },
  "active_upstream": "lapakvip"
}
```

### API Key Management

**POST /api/keys/create**
```json
Headers: Authorization: Bearer {session_token}

Request:
{
  "key_name": "Production Key"
}

Response:
{
  "success": true,
  "api_key": "yr-6a8fb9a2-..."
}
```

**GET /api/keys**
```
Headers: Authorization: Bearer {session_token}

Response:
{
  "keys": [...]  // Same format as /api/auth/me
}
```

### Router Management

**POST /api/router/set**
```json
Headers: Authorization: Bearer {session_token}

Request:
{
  "upstream": "moyra"  // lapakvip, moyra, marketku, yogathedev, kaorustore
}

Response:
{
  "success": true
}
```

## Proxy Request Flow

```
1. User sends request to /api/v1/chat/completions
2. Extract API key from Authorization header
3. If yr-xxx key:
   a. Validate key (check active status)
   b. Get user's selected upstream from router_settings
   c. Route to that upstream
4. If non-yr key (lv-, mk-, sk-, etc.):
   a. Auto-detect upstream from prefix
   b. Forward directly
5. Log usage (tokens, response time, status)
6. Update api_keys.request_count and last_used
```

## MySQL to SQLite Fallback

**Auto-detection pattern:**
```python
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        connect_timeout=2
    )
    conn.close()
    import auth_mysql as auth
    AUTH_TYPE = "mysql"
except Exception:
    import auth  # SQLite version
    AUTH_TYPE = "sqlite"
```

**Why fallback matters:**
- Development: SQLite (no server needed)
- Production: MySQL (better concurrency)
- Deployment: Works immediately without MySQL setup

## Login Page Integration

**SweetAlert2 for modern UI:**
```html
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<script>
// Register
const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
});

const data = await response.json();

if (data.success) {
    localStorage.setItem('session_token', data.session_token);
    Swal.fire({
        icon: 'success',
        title: 'Account Created!',
        html: `Your API Key: <code>${data.api_key}</code>`,
        confirmButtonText: 'Go to Dashboard'
    }).then(() => {
        window.location.href = '/';
    });
}
</script>
```

## Dashboard API Key Display

**Auto-load on page load:**
```javascript
async function loadUserData() {
    const sessionToken = localStorage.getItem('session_token');
    if (!sessionToken) {
        window.location.href = '/login.html';
        return;
    }
    
    const response = await fetch('/api/auth/me', {
        headers: { 'Authorization': 'Bearer ' + sessionToken }
    });
    
    const data = await response.json();
    
    // Update dashboard
    document.getElementById('default-api-key').textContent = data.keys[0].api_key;
    document.getElementById('balance').textContent = data.stats.credits.toLocaleString();
    document.getElementById('totalRequests').textContent = data.stats.total_requests.toLocaleString();
}

window.addEventListener('load', loadUserData);
```

**Copy button:**
```javascript
function copyApiKey() {
    const apiKey = document.getElementById('default-api-key').textContent;
    navigator.clipboard.writeText(apiKey).then(() => {
        Swal.fire({
            icon: 'success',
            title: 'Copied!',
            timer: 1500,
            showConfirmButton: false
        });
    });
}
```

## User Requirements: "1000% NO GIMMICK"

**Critical: User demands working code, not demos**

When building auth systems for this user:
- ❌ Don't use placeholder values
- ❌ Don't say "// TODO: implement this"
- ❌ Don't use fake data/mock responses
- ✅ Complete database schema with foreign keys
- ✅ Actual password hashing (not plaintext)
- ✅ Real session tokens (secure random)
- ✅ Working API endpoints (test with curl)
- ✅ Error handling for all edge cases

**User quote:**
> "1000% NO GIMMICK... beneran WORK!"

Translation: "1000% NO GIMMICK... actually WORKS!"

**Test before delivering:**
```bash
# 1. Init database
python auth.py

# 2. Start server
python server.py

# 3. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'

# 4. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 5. Get user info
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {token_from_step_4}"

# All 5 steps must return valid JSON with success:true
```

## Pitfalls

1. **MySQL not installed** → Auto-fallback to SQLite works
2. **Pydantic errors on Python 3.14** → Use stdlib HTTP server (no FastAPI)
3. **Session token in cookie vs header** → Support both (check Cookie header too)
4. **API key format collision** → Timestamp + 128-bit random = impossible
5. **Password stored plaintext** → Always hash with salt
6. **Session never expires** → Set expires_at = NOW() + 30 days
7. **CORS blocked** → Add Access-Control-Allow-Origin: * header
8. **User can't see API key after register** → Show in success popup OR redirect to dashboard

## Production Checklist

- [ ] MySQL server configured and running
- [ ] Database created (`CREATE DATABASE umiagent_router`)
- [ ] All tables indexed (username, email, api_key, session_token)
- [ ] Password min length enforced (6+ chars)
- [ ] Session expiry job (delete expired sessions daily)
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] HTTPS enabled (Let's Encrypt)
- [ ] Domain configured (router.umiagent.my.id)
- [ ] Firewall allows port 443
- [ ] Backup strategy (daily MySQL dumps)
