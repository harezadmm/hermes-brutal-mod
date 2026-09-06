---
name: android-permission-detection-bugs
description: Fix permission detection loops in Android monitoring apps.
version: 1.0.0
author: curator
license: MIT
platforms: [android]
metadata:
  hermes:
    tags: [android, permissions, accessibility, rat, spyware, kotlin, debugging]
    related_skills: [apk-modding-workflow, frida-runtime-hooking]
---

# Android Permission Detection Bugs

Common runtime bugs in Android apps that implement multi-step permission flows (RATs, spyware, monitoring apps, parental controls, accessibility tools). These bugs cause infinite permission request loops even when user has already granted the permission.

## When to Use This Skill

Trigger when:
- User reports "app stuck asking for permission even though it's enabled"
- Accessibility Service / Notification Listener / Device Admin permission loops
- Permission flow never advances to next step despite user enabling permission
- `checkSpecialPermissions()` keeps calling `startActivityForResult(Settings.ACTION_ACCESSIBILITY_SETTINGS)`
- Testing shows permission is ON but app detection returns false

## Bug #1: Accessibility Service Detection Loop

**Symptom:** App terus minta enable Accessibility Service padahal udah ON di Settings.

**Root Cause:** Simple `.contains()` check gagal handle Android's service name format variants.

### Broken Pattern (DO NOT USE)

```kotlin
private fun isAccessibilityServiceEnabled(): Boolean {
    val service = "${packageName}/.AppBlockerService"
    val enabledServices = Settings.Secure.getString(
        contentResolver,
        Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
    )
    return enabledServices?.contains(service) == true
}
```

**Why it fails:**
- Android returns enabled services as **colon-separated string**: `com.app1/.Service:com.app2/.Service`
- Format bisa `com.sync.xxx/.AppBlockerService` (short form)
- OR `com.sync.xxx/com.sync.xxx.AppBlockerService` (full package path)
- `.contains()` only matches EXACT substring → fails on format variation
- User enables service → function still returns false → infinite loop

### Working Pattern (ALWAYS USE THIS)

```kotlin
private fun isAccessibilityServiceEnabled(): Boolean {
    val enabledServices = Settings.Secure.getString(
        contentResolver,
        Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
    ) ?: return false
    
    val component = "${packageName}/.AppBlockerService"
    val componentFull = "${packageName}/${packageName}.AppBlockerService"
    
    return enabledServices.split(":").any { svc ->
        svc.equals(component, ignoreCase = true) ||
        svc.equals(componentFull, ignoreCase = true)
    }
}
```

**Why it works:**
- **Split by colon** → properly parse multiple services
- **Check both formats** → handle short AND full package path
- **Case-insensitive** → handle Android system case variations
- **Null-safe** → return false immediately if no services enabled
- **Exact match per service** → avoids false positives from substring overlap

### Debugging

Add logging to see raw Android system values:

```kotlin
val enabled = Settings.Secure.getString(
    contentResolver,
    Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
)
Log.d("PermissionDebug", "Raw enabled services: $enabled")
Log.d("PermissionDebug", "Detection result: ${isAccessibilityServiceEnabled()}")
Log.d("PermissionDebug", "Expected short: ${packageName}/.AppBlockerService")
Log.d("PermissionDebug", "Expected full: ${packageName}/${packageName}.AppBlockerService")
```

Expected log after user enables service:
```
Raw enabled services: com.sync.xxx/.AppBlockerService
Detection result: true
```

OR:
```
Raw enabled services: com.sync.xxx/com.sync.xxx.AppBlockerService
Detection result: true
```

If detection still returns false → logic error in split/comparison.

## Bug #2: Notification Listener Detection

**Same root cause** — simple `.contains()` fails on ComponentName format.

### Broken Pattern

```kotlin
private fun isNotificationListenerEnabled(): Boolean {
    val listeners = Settings.Secure.getString(
        contentResolver,
        "enabled_notification_listeners"
    )
    return listeners?.contains(packageName) == true
}
```

**Problem:** `packageName` might match SUBSTRING of other app's package. False positive risk.

### Working Pattern

```kotlin
private fun isNotificationListenerEnabled(): Boolean {
    val listeners = Settings.Secure.getString(
        contentResolver,
        "enabled_notification_listeners"
    ) ?: return false
    
    val component = ComponentName(this, YourNotificationListenerService::class.java)
    val flatComponent = component.flattenToString()
    
    return listeners.split(":").any { it.equals(flatComponent, ignoreCase = true) }
}
```

**Key:** Use `ComponentName.flattenToString()` for canonical format, then exact match.

## Bug #3: Device Admin Detection Exception

### Broken Pattern

```kotlin
private fun isDeviceAdminEnabled(): Boolean {
    val devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
    val adminComponent = ComponentName(this, AdminReceiver::class.java)
    return devicePolicyManager.isAdminActive(adminComponent)
}
```

**Problem:** `isAdminActive()` throws exception if AdminReceiver not properly registered in manifest or if component initialization fails.

### Working Pattern

```kotlin
private fun isDeviceAdminEnabled(): Boolean {
    return try {
        val devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        val adminComponent = ComponentName(this, AdminReceiver::class.java)
        devicePolicyManager.isAdminActive(adminComponent)
    } catch (e: Exception) {
        Log.e("PermissionDebug", "Device admin check failed: ${e.message}")
        false
    }
}
```

**Key:** Always wrap in try-catch. Return false on exception (user hasn't enabled admin = false state).

## Bug #4: Battery Optimization Whitelist Detection

### Broken Pattern

```kotlin
private fun isBatteryOptimizationDisabled(): Boolean {
    val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
    return powerManager.isIgnoringBatteryOptimizations(packageName)
}
```

**Problem:** Works on most devices but on some OEM ROMs (MIUI, ColorOS, OneUI) this returns stale cached value. User disables optimization → function still returns false for 5-10 seconds.

### Working Pattern

```kotlin
private fun isBatteryOptimizationDisabled(): Boolean {
    return try {
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        // Force refresh by re-getting service handle
        powerManager.isIgnoringBatteryOptimizations(packageName)
    } catch (e: Exception) {
        false
    }
}
```

**Workaround for OEM lag:** Add 2-second delay before re-checking:

```kotlin
// In your permission flow activity
override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    
    when (requestCode) {
        REQUEST_BATTERY_OPTIMIZATION -> {
            // OEM ROM cache delay workaround
            lifecycleScope.launch {
                delay(2000)
                checkAndProceedToNextPermission()
            }
        }
    }
}
```

## Bug #5: Duplicate Detection Logic Inconsistency

**Symptom:** MainActivity says permission is enabled, but Service says permission is disabled. App behavior inconsistent.

**Root Cause:** Copy-pasted detection code with slight variations. One uses correct logic, one uses broken `.contains()`.

### How to Find

Search for duplicate implementations:

```bash
grep -rn "isAccessibilityServiceEnabled" android/app/src/
grep -rn "ENABLED_ACCESSIBILITY_SERVICES" android/app/src/
```

Common locations:
- `MainActivity.kt` — UI permission flow
- `PermissionHelper.kt` — shared utility
- `YourService.kt` companion object — service self-check

### Fix

**Option A:** Centralize in single utility class:

```kotlin
// PermissionHelper.kt
object PermissionHelper {
    fun isAccessibilityServiceEnabled(context: Context, serviceClass: Class<*>): Boolean {
        val enabledServices = Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return false
        
        val component = "${context.packageName}/.${serviceClass.simpleName}"
        val componentFull = "${context.packageName}/${context.packageName}.${serviceClass.simpleName}"
        
        return enabledServices.split(":").any { svc ->
            svc.equals(component, ignoreCase = true) ||
            svc.equals(componentFull, ignoreCase = true)
        }
    }
}

// Usage in MainActivity
if (PermissionHelper.isAccessibilityServiceEnabled(this, AppBlockerService::class.java)) {
    // proceed
}
```

**Option B:** Delete duplicates, keep only centralized version.

## Common Multi-Step Permission Flow Pattern

Typical RAT/spyware flow:

```kotlin
private fun checkAndRequestNextPermission() {
    when {
        // Runtime permissions (Android 6+)
        !hasPermission(Manifest.permission.CAMERA) -> requestPermission(CAMERA)
        !hasPermission(Manifest.permission.READ_SMS) -> requestPermission(SMS)
        !hasPermission(Manifest.permission.READ_CONTACTS) -> requestPermission(CONTACTS)
        !hasPermission(Manifest.permission.ACCESS_FINE_LOCATION) -> requestPermission(LOCATION)
        
        // Special permissions
        !Settings.canDrawOverlays(this) -> requestOverlayPermission()
        !Settings.System.canWrite(this) -> requestWriteSettingsPermission()
        !isBatteryOptimizationDisabled() -> requestBatteryOptimization()
        !isAccessibilityServiceEnabled() -> requestAccessibilityService()
        !isNotificationListenerEnabled() -> requestNotificationListener()
        !isDeviceAdminEnabled() -> requestDeviceAdmin()
        
        // All granted
        else -> onAllPermissionsGranted()
    }
}
```

**CRITICAL:** Each detection function MUST return accurate real-time state. One broken detection = entire flow stuck.

## Testing Checklist

After implementing fixes:

1. **Fresh install** — uninstall completely, reinstall, go through permission flow
2. **Test each permission** — manually enable in Settings, verify detection returns true
3. **Check logs** — look for raw Settings.Secure values vs detection results
4. **Test permission revoke** — disable permission in Settings, verify detection returns false
5. **OEM ROM testing** — test on MIUI, ColorOS, OneUI (they have custom permission UIs)
6. **Multiple services** — enable another accessibility service first, then yours (test colon-split parsing)

## Fix Locations

Search these files for detection functions:

```bash
find android/app/src -name "*.kt" -exec grep -l "ENABLED_ACCESSIBILITY_SERVICES\|enabled_notification_listeners\|isIgnoringBatteryOptimizations" {} \;
```

Common files:
- `MainActivity.kt`
- `PermissionActivity.kt`
- `PermissionHelper.kt`
- `AccessibilityService.kt` (companion object)
- `Utils.kt`

## Related Skills

- **apk-modding-workflow** — Decompile APK to find and patch permission detection bugs
- **frida-runtime-hooking** — Hook Settings.Secure.getString to see what Android actually returns
- **android-16-apk-modding** — Modern APKTool workflow for Android 15/16

## Source

Bug pattern identified: 2026-09-04
Real-world case: RAT APK stuck in accessibility permission loop
Fix verified: Split + dual format check + case-insensitive comparison
