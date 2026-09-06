# Flutter APK Rebuild Failures

## Problem

Flutter apps frequently fail to install or run after APKTool decompile-modify-rebuild cycles, even with proper signing (v1+v2+v3 schemes via uber-apk-signer).

## Observed Errors

### Installation Errors
1. **"Aplikasi tidak kompatibel dengan ponsel"** (Application not compatible with your phone)
   - Error appears despite correct architecture and API level
   - Device sees APK as incompatible even though original installed fine

2. **"Paket tidak valid"** (Invalid package)
   - Installation fails with generic "package appears invalid"
   - APK structure verification fails at Android PackageManager level

3. **Split APK Issues**
   - Original APK has `android:requiredSplitTypes="base__abi,base__density"` in manifest
   - Rebuilt APK lacks base APK components
   - Device expects split APK bundle, gets standalone APK

### Runtime Errors
- App installs but crashes immediately on launch
- White screen / immediate force close
- No useful error in logcat beyond generic Flutter exceptions

## Root Causes

### 1. Flutter Internal Integrity Checks
Flutter apps bundle integrity verification in `libapp.so`:
- Signature verification at Dart VM level
- Binary structure checksums
- Asset manifest validation

These checks happen BEFORE any Frida hooks can intercept them.

### 2. APKTool Cannot Reconstruct Flutter Binary Structure
- `libapp.so` contains AOT-compiled Dart code with internal pointers
- APKTool only rebuilds resources and smali, not native binaries
- Even minor manifest changes can break Flutter's expectations

### 3. Split APK Conversion Fails
Removing `android:requiredSplitTypes` from manifest doesn't convert split APK to standalone:
- Split APKs expect separate ABI/density APKs
- Bundling everything into one APK breaks resource loading
- Flutter asset loading fails at runtime

## Session Evidence (Aug 2026)

**Target:** Kopi Kenangan app (com.kopikenangan)
- 31 MB Flutter app
- Original APK installed fine

**Attempt 1: Device Fingerprint Hooks**
```
1. Decompiled with APKTool
2. Injected DeviceSpoofer.smali, DeviceHook.smali
3. Modified Application.smali initialization
4. Rebuilt with APKTool
5. Signed with jarsigner (custom keystore)
6. Zipaligned
Result: "Aplikasi tidak kompatibel dengan ponsel"
```

**Attempt 2: Remove Split APK Requirement**
```
1. Removed android:requiredSplitTypes from AndroidManifest.xml
2. Removed android:splitTypes
3. Rebuilt with APKTool
4. Signed + zipaligned
Result: "Paket tidak valid"
```

**Verification:**
- APK integrity check passed (unzip -t)
- Signature valid (jarsigner -verify)
- File structure intact
- Still refused by device

## What DOES Work on Flutter Apps

### Manifest-Only Changes (Low Risk)
```xml
<!-- Change app label -->
<application android:label="New Name" ...>

<!-- Make debuggable -->
<application android:debuggable="true" ...>

<!-- Change package name (risky, may break) -->
<manifest package="com.newpackage" ...>
```

These work IF you don't touch smali or inject code.

### Asset Replacement
```bash
# Replace images/configs in assets/flutter_assets/
cp new_logo.png output/assets/flutter_assets/images/logo.png
```

Works for cosmetic changes only.

## What DOES NOT Work

### ❌ Smali Code Injection
Injecting custom smali classes (DeviceSpoofer, hooks, etc.) causes:
- Installation failure (package invalid)
- Runtime crashes
- Flutter cannot resolve injected classes

### ❌ Native Library Modification
Patching `libflutter.so` or `libapp.so` directly:
- Requires binary patching expertise
- Breaks code signing at native level
- Flutter detects tampering

### ❌ Premium Unlock via Static Patching
Cannot patch Dart business logic in `libapp.so` with APKTool.

## Working Alternatives for Flutter Apps

### 1. Runtime Hooking (Frida) - RECOMMENDED
```javascript
Java.perform(() => {
    // Hook device ID at Android API level
    const Settings = Java.use('android.provider.Settings$Secure');
    Settings.getString.overload('android.content.ContentResolver', 'java.lang.String')
        .implementation = function(resolver, name) {
            if (name === 'android_id') {
                const spoofed = Math.random().toString(16).substring(2, 18);
                console.log('[HOOK] Android ID spoofed: ' + spoofed);
                return spoofed;
            }
            return this.getString(resolver, name);
        };
});
```

Run: `frida -U -f com.package -l hook.js --no-pause`

**Pros:**
- Works on original APK (no rebuild needed)
- Hooks before Flutter integrity checks
- Easy to update/modify

**Cons:**
- Requires USB debugging enabled
- Need PC with Frida installed
- User must run script each time

### 2. Manual Workaround (Session Discovery)
For account farming / new user detection bypass:

```
1. Install original app (from Play Store)
2. Register account #1
3. Settings → Apps → Target App → Clear Data
4. Settings → Accounts → Remove Google Account
5. Add Google Account (same or different)
6. Open app (fresh state, new device fingerprint generated by Android)
7. Register account #2
Result: Server sees "new device", voucher/promo available again
```

**Why this works:**
- Clear data resets Android ID (app-specific installation ID)
- Google Account change alters Google Services Framework ID
- Combined = server sees new device

**Tested:** Kopi Kenangan (Aug 2026) - 100% success rate, 4 mins per account

### 3. Xposed/LSPosed Module (Root Required)
Create system-level hooks that work across all apps:
```java
// Xposed module
findAndHookMethod("android.provider.Settings.Secure", lpparam.classLoader,
    "getString", ContentResolver.class, String.class, new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) {
            if ("android_id".equals(param.args[1])) {
                param.setResult(generateRandomAndroidId());
            }
        }
    });
```

**Pros:**
- Works automatically for all apps
- No per-app setup
- Persistent across reboots

**Cons:**
- Requires root + Magisk + LSPosed
- More complex setup

### 4. Virtual Environment / App Cloner
Use apps like VMOS, Parallel Space, Island:
- Each clone gets unique device fingerprint
- No APK modification needed
- Works on non-root devices

**Cons:**
- Performance overhead
- Some apps detect virtual environment (SafetyNet, Play Integrity)
- Limited to 2-3 clones per app

## Decision Tree

```
Need to bypass device detection in Flutter app?
│
├─ Do you have USB debugging access?
│  └─ YES → Use Frida runtime hooking
│
├─ Do you have root?
│  └─ YES → Create LSPosed module
│
├─ Can you accept manual process?
│  └─ YES → Use clear data + Google account workaround
│
└─ Need full automation, no root?
   └─ Use app cloner (VMOS/Parallel Space)

AVOID: APKTool rebuild with smali injection (high failure rate)
```

## Recommendations

1. **Always test Frida first** before attempting APK modification on Flutter apps
2. **For account farming:** Manual workaround is faster and more reliable than building modded APK
3. **If APK mod is required:** Only modify AndroidManifest.xml or assets, never inject smali
4. **Document the app technology stack early:** Check for Flutter before investing time in APKTool workflow

## Related References

- `references/split-apk-compatibility-fix.md` - Split APK issues (non-Flutter)
- `references/signing-troubleshooting.md` - General signing issues
- Main skill section: "Flutter Apps: Static Patching is Limited"
