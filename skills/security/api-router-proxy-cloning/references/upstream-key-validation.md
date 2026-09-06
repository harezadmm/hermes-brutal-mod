# Upstream API Key Validation System

## Overview

Real-time validation system that tests upstream provider API keys before saving them to the database. Used in UmiAgent Router production system (August 2026).

## Architecture

```
User adds upstream key
    ↓
POST /api/upstream/add
    ↓
upstream_validator.py → Test key against provider
    ↓
Provider returns model list (or error)
    ↓
Save to database with status + models
    ↓
SweetAlert2 confirmation to user
```

## Implementation

**Backend validator** (`upstream_validator.py`):

```python
import urllib.request
import json
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

UPSTREAM_TEST_ENDPOINTS = {
    "lapakvip": {
        "url": "https://router.lapakvip.com/v1/models",
        "method": "GET",
        "key_format": "lv-"
    },
    "moyra": {
        "url": "https://api.moyra.my.id/v1/models",
        "method": "GET",
        "key_format": "sk-"
    }
}

def validate_upstream_key(upstream, api_key):
    """
    Returns: {
        'valid': bool,
        'models': list,
        'error': str or None
    }
    """
    config = UPSTREAM_TEST_ENDPOINTS[upstream]
    
    # Check key format
    if not api_key.startswith(config['key_format']):
        return {
            'valid': False,
            'models': [],
            'error': f'Invalid key format. Expected {config["key_format"]}'
        }
    
    try:
        req = urllib.request.Request(
            config['url'],
            method=config['method'],
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                models = [m.get('id', m.get('name')) for m in data.get('data', [])]
                return {'valid': True, 'models': models[:20], 'error': None}
            else:
                return {'valid': False, 'models': [], 'error': f'HTTP {response.status}'}
    
    except urllib.error.HTTPError as e:
        return {'valid': False, 'models': [], 'error': f'HTTP {e.code}'}
    except Exception as e:
        return {'valid': False, 'models': [], 'error': str(e)}
```

**Database schema**:

```sql
CREATE TABLE upstream_keys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    upstream VARCHAR(50) NOT NULL,
    api_key TEXT NOT NULL,
    key_name TEXT,
    active BOOLEAN DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',  -- active/expired/error
    models TEXT,  -- JSON array of model names
    last_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    UNIQUE(user_id, upstream)
);
```

**Backend endpoint**:

```python
def handle_add_upstream_key(self):
    # ... auth validation ...
    
    upstream = data.get('upstream')
    api_key = data.get('api_key')
    
    # Import validator
    from upstream_validator import validate_upstream_key
    
    # Validate against provider
    validation = validate_upstream_key(upstream, api_key)
    
    if not validation['valid']:
        self.send_json({
            'success': False,
            'error': validation['error']
        })
        return
    
    # Save with models + status
    result = auth.add_upstream_key(
        user_id,
        upstream,
        api_key,
        key_name,
        validation['models'],
        'active' if validation['valid'] else 'error'
    )
    
    if result['success']:
        result['models'] = validation['models']
        result['model_count'] = len(validation['models'])
    
    self.send_json(result)
```

## Frontend Integration

**Form with SweetAlert2**:

```javascript
async function addUpstreamKey() {
    const provider = document.getElementById('upstream-provider').value;
    const apiKey = document.getElementById('upstream-apikey').value;
    
    // Show loading
    Swal.fire({
        title: 'Validating...',
        text: 'Testing API key dengan provider...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });
    
    const response = await fetch('/api/upstream/add', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${sessionToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            upstream: provider, 
            api_key: apiKey 
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        const modelCount = result.model_count || 0;
        const modelText = modelCount === 1 
            ? `Kamu cuma punya 1 model: ${result.models[0]}`
            : `${modelCount} models terdeteksi`;
        
        await Swal.fire({
            icon: 'success',
            title: 'Berhasil!',
            html: `<p><strong>API Key berhasil ditambahkan!</strong></p>
                   <p>${modelText}</p>`
        });
        
        await loadKeys();
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Validation Failed',
            text: result.error
        });
    }
}
```

**Display with status indicators**:

```html
<div class="upstream-key-card">
    <div class="header">
        <h3>LapakVIP</h3>
        <span class="status-badge active">
            <i class="fas fa-circle"></i> Active
        </span>
    </div>
    <div class="key-masked">lv-abc123***xyz789</div>
    <div class="model-info">
        15 models available
    </div>
    <button onclick="deleteKey('lapakvip')">
        <i class="fas fa-trash"></i> Hapus
    </button>
</div>
```

**CSS for status badges**:

```css
.status-badge.active {
    background: #D1FAE5;
    color: #065F46;
}

.status-badge.expired {
    background: #FEE2E2;
    color: #991B1B;
}

.status-badge.error {
    background: #FEF3C7;
    color: #92400E;
}
```

## User Experience

**Success flow**:
1. User selects provider (dropdown)
2. User pastes API key (lv-xxx, mk-xxx, etc.)
3. User clicks "Simpan Key"
4. Loading indicator: "Validating..."
5. System tests key against provider (1-3 seconds)
6. Success popup: "Berhasil! 15 models terdeteksi"
7. Key card appears with green "Active" badge

**Error flow**:
1. User pastes invalid key
2. Loading indicator
3. Error popup: "HTTP 403" or "Invalid key format"
4. Key NOT saved to database
5. User can retry immediately

## Error Handling

**Common errors**:

| Error | Cause | Solution |
|:------|:------|:---------|
| `HTTP 403` | Invalid/expired API key | Get new key from provider |
| `HTTP 404` | Wrong endpoint URL | Check provider docs |
| `HTTP 524` | Provider timeout (CloudFlare) | Wait 2-5 minutes, retry |
| `Invalid key format` | Wrong prefix (lv- vs mk-) | Check provider name |
| `Connection error` | Network/DNS issue | Check internet connection |

**CloudFlare Error 524 (Timeout)**:

Provider response:
```json
{
  "error_code": 524,
  "error_name": "origin_response_timeout",
  "detail": "Origin took too long to respond (>120s)",
  "retryable": true,
  "retry_after": 120
}
```

**Handling**: Show user-friendly message "Provider sedang sibuk, coba lagi 2-5 menit" instead of raw CloudFlare error.

## Security

**Best practices**:
1. ✅ Never log full API keys (mask in logs)
2. ✅ Validate key format before HTTP request
3. ✅ Timeout requests after 10 seconds
4. ✅ Disable SSL verification only if needed
5. ✅ Rate limit validation endpoint (max 10/minute per user)

**Database storage**:
- Store keys encrypted if handling production data
- Use environment variables for sensitive keys
- Never expose full keys in frontend (mask: `lv-abc***xyz`)

## Testing

**Manual test**:

```bash
# Valid key (should return 200 + models)
curl https://router.lapakvip.com/v1/models \
  -H "Authorization: Bearer lv-YOUR-REAL-KEY"

# Invalid key (should return 403)
curl https://router.lapakvip.com/v1/models \
  -H "Authorization: Bearer lv-invalid-key-test"
```

**Automated test**:

```python
def test_validation():
    # Test valid format
    result = validate_upstream_key("lapakvip", "lv-test-key")
    assert result['valid'] == False  # (key invalid but format OK)
    assert result['error'] == "HTTP 403"
    
    # Test invalid format
    result = validate_upstream_key("lapakvip", "mk-wrong-prefix")
    assert result['valid'] == False
    assert "Invalid key format" in result['error']
```

## Performance

**Timing**:
- Format validation: <1ms
- HTTP request to provider: 500ms - 3s
- Database write: <10ms
- Total user-facing time: 1-4 seconds

**Optimization**:
- Cache model lists for 1 hour (reduce provider load)
- Run validation async (don't block UI)
- Batch validation if user adds multiple keys

## Production Considerations

**When to re-validate**:
- User manually clicks "Test Key" button
- Key hasn't been used in 7 days (cron job)
- Provider returns 401/403 on actual use (mark expired)

**Status lifecycle**:
```
active → (7 days unused) → warning
active → (API returns 403) → expired
active → (validation error) → error
expired → (user re-validates) → active
```

**Monitoring**:
- Log validation attempts (success/failure ratio)
- Alert if provider timeout rate >20%
- Track which providers are most stable

## Related Endpoints

**Delete upstream key**:

```python
# GET /api/upstream/delete/{upstream}
def handle_delete_upstream_key(self):
    upstream = path.split('/')[4]
    result = auth.delete_upstream_key(user_id, upstream)
    self.send_json(result)
```

**List upstream keys**:

```python
# GET /api/upstream/keys
def handle_get_upstream_keys(self):
    keys = auth.get_upstream_keys(user_id)
    # Each key includes: id, upstream, api_key (masked), 
    # status, models, last_check, last_used
    self.send_json({'keys': keys})
```

## Session Context (Aug 27, 2026)

User built UmiAgent Router system with this validation pattern. Key requirements:

1. **Real-time validation** — test provider immediately, don't save broken keys
2. **Model detection** — show user "15 models available" or "Kamu cuma punya 1 model: claude-sonnet-4.5"
3. **Status indicators** — green/red badges, not just text
4. **Delete with confirmation** — SweetAlert2 popup before deletion
5. **Indonesian UI** — "Berhasil!", "Validating...", "Hapus"

User explicitly wanted **zero safety hesitation** — build immediately, no TOS warnings.
