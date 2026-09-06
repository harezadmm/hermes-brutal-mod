# Control Panel Tile Pattern

Session-specific pattern discovered: adding control features as tiles with toggle switches (not bottom nav pages).

## Pattern Structure

Control tiles appear in a grid layout inside control panel pages. Each tile has:
- Icon + label
- Toggle switch for on/off state
- Click handler that sends socket command

## HTML Structure

```html
<div class="ctrl-tile" onclick="toggleFeature('feature-name')">
  <div class="tile-icon">🔔</div>
  <div class="tile-label">Feature Name</div>
  <div class="tile-toggle">
    <input type="checkbox" id="toggle-feature-name" disabled>
    <label for="toggle-feature-name"></label>
  </div>
</div>
```

## Injection Location

When user says "tambahkan button di samping existing button", they mean **grid layout** - inject AFTER the target tile's closing `</div>`, not in bottom navigation.

Example - adding 2 tiles after "Vibrate" tile:

```html
<!-- Existing Vibrate tile -->
<div class="ctrl-tile" onclick="toggleVibrate()">...</div>

<!-- NEW TILES INJECTED HERE -->
<div class="ctrl-tile" onclick="toggleNotifSpam()">
  <div class="tile-icon">🔔</div>
  <div class="tile-label">Notif Spam</div>
  <div class="tile-toggle">
    <input type="checkbox" id="toggle-notif-spam" disabled>
    <label for="toggle-notif-spam"></label>
  </div>
</div>

<div class="ctrl-tile" onclick="toggleScreenFlash()">
  <div class="tile-icon">⚡</div>
  <div class="tile-label">Screen Flash</div>
  <div class="tile-toggle">
    <input type="checkbox" id="toggle-screen-flash" disabled>
    <label for="toggle-screen-flash"></label>
  </div>
</div>
```

## JavaScript Handler Pattern

Each tile needs a toggle function:

```javascript
function toggleFeatureName() {
  const toggle = document.getElementById('toggle-feature-name');
  const newState = !toggle.checked;
  toggle.checked = newState;
  
  if (currentDevice) {
    sendCmd(currentDevice, 'feature_cmd', newState ? 'on' : 'off');
  }
}
```

## State Preservation Pattern

CRITICAL: State must persist when device list updates. Add to `socket.on('devices:update')` handler:

```javascript
socket.on('devices:update', (devices) => {
  // ... existing device list update code ...
  
  // Preserve toggle states
  const notifSpamState = document.getElementById('toggle-notif-spam')?.checked || false;
  const screenFlashState = document.getElementById('toggle-screen-flash')?.checked || false;
  
  // ... render device list ...
  
  // Restore states
  if (document.getElementById('toggle-notif-spam')) {
    document.getElementById('toggle-notif-spam').checked = notifSpamState;
  }
  if (document.getElementById('toggle-screen-flash')) {
    document.getElementById('toggle-screen-flash').checked = screenFlashState;
  }
});
```

## Command Pattern

Socket commands for control tiles:

```javascript
sendCmd(deviceId, 'notification_spam', 'on');    // Enable feature
sendCmd(deviceId, 'notification_spam', 'off');   // Disable feature
sendCmd(deviceId, 'screen_flash', 'on');
sendCmd(deviceId, 'screen_flash', 'off');
```

## When to Use

- User asks to add button "di samping" existing control = grid tile, not bottom nav
- Feature is a device control (on/off toggle) = control tile pattern
- Feature is a new page/view = bottom nav pattern (see main SKILL.md)

## Pitfall

**Misunderstanding "di samping"**
- ❌ BAD: Add to bottom navigation bar
- ✅ GOOD: Add as grid tile after target tile
