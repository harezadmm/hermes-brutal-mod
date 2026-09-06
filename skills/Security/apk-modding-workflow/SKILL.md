---
name: apk-modding-workflow
description: Use for Android APK decompile, modify, and proper signing.
version: 1.0.0
author: UmiAgent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [apk, android, reverse-engineering, mobile-security, apktool, signing]
    related_skills: [game-modder-apk]
---

# APK Modding Workflow

Proper workflow for decompiling, modifying, and repackaging Android APK files with modern signature schemes that work on Android 7-15.

## When to Use This Skill

Trigger when the user:
- Wants to mod an APK (premium unlock, remove ads, inject features)
- Asks to modify AndroidManifest.xml or app resources
- Needs to patch smali code or inject custom logic
- Gets "paket tidak valid" / "package appears invalid" install errors
- Asks about APK signing, zipalign, or signature schemes

## Core Problem

**Manual Python `zipfile` repacking FAILS.** It doesn't preserve APK alignment and binary XML structure, causing "Application not installed because package appears invalid" errors on Android 7+.

**`jarsigner` alone is INSUFFICIENT for Android 7+.** It only signs with v1 scheme (JAR signature). Modern Android requires APK Signature Scheme v2/v3.

## The Working Workflow

### Step 1: Install Tools

```bash
# Download apktool (proper decompile/recompile)
cd ~/tools
curl -L -o apktool.jar "https://github.com/iBotPeaches/Apktool/releases/download/v2.10.0/apktool_2.10.0.jar"

# Download uber-apk-signer (zipalign + v1/v2/v3/v4 signing in one step)
curl -L -o uber-apk-signer.jar "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"
```

### Step 2: Decompile APK

```bash
java -jar apktool.jar d original.apk -o app-decompiled -f
```

**What this does:**
- Decodes binary `AndroidManifest.xml` to readable XML
- Decompiles `classes.dex` to smali code
- Extracts resources with proper structure preservation
- Preserves 9-patch images, binary XMLs, and native libs

### Step 3: Modify

Common modifications:

**A. Make Debuggable (for Frida/runtime hooking):**

Edit `app-decompiled/AndroidManifest.xml`:
```xml
<application android:debuggable="true" ...>
```

**B. Change App Label:**
```xml
<application android:label="App Name PRO" ...>
```

**C. Disable SSL Pinning (if present):**

Search smali for `TrustManager`, `SSLContext`, `HostnameVerifier` and patch validation methods to always return true.

**D. Patch Premium Checks (Java/Kotlin apps only):**

Search smali for `isPremium`, `isSubscribed`, `hasLicense`:
```bash
cd app-decompiled/smali
grep -r "isPremium" .
grep -r "license" .
```

Modify methods to return `const/4 v0, 0x1` (true).

**E. Remove Ads:**

Delete ad library directories from `smali/` (e.g., `smali/com/google/android/gms/ads/`).

### Step 4: Recompile

```bash
java -jar apktool.jar b app-decompiled -o app-modded-unsigned.apk
```

### Step 5: Sign with Modern Signature Schemes

```bash
java -jar uber-apk-signer.jar --apks app-modded-unsigned.apk --allowResign
```

**Output:** `app-modded-aligned-debugSigned.apk`

**What uber-apk-signer does:**
- Zipaligns the APK (4-byte alignment for resources)
- Signs with v1 + v2 + v3 schemes (Android 7-15 compatible)
- Verifies signature after signing
- Uses embedded debug keystore (valid until 2044)

### Step 6: Install

```bash
adb install app-modded-aligned-debugSigned.apk
```

Or send to user via Telegram:
```
MEDIA:/path/to/app-modded-aligned-debugSigned.apk
```

## Alternative: Custom Keystore

If you need a custom keystore (not debug):

```bash
# Generate keystore (one time)
keytool -genkey -v -keystore my.keystore -alias mykey -keyalg RSA -keysize 2048 -validity 10000 -storepass password123 -keypass password123 -dname "CN=YourName, OU=Mod, O=Org, L=City, ST=State, C=ID"

# Sign with custom keystore
java -jar uber-apk-signer.jar --apks app-modded-unsigned.apk --ks my.keystore --ksAlias mykey --ksPass password123 --ksKeyPass password123
```

## Flutter Apps: Static Patching is Limited

**How to identify Flutter:**
- `lib/arm64-v8a/libflutter.so` present
- `lib/arm64-v8a/libapp.so` present (compiled Dart code)
- `assets/flutter_assets/` directory

**What you CAN modify:**
- AndroidManifest.xml (make debuggable, change label)
- Assets (images, JSON configs in `assets/flutter_assets/`)
- Remove ad libraries from smali (if any native ads)

**What you CANNOT modify via static patching:**
- Dart business logic (compiled into `libapp.so`)
- Premium checks, license validation, in-app purchase logic in Dart code
- Game state, coins, levels stored in Dart runtime

**For Flutter premium unlock:**

1. **Make debuggable** (Step 3A above)
2. **Recompile & sign** (Steps 4-5)
3. **Runtime bypass with Frida:**

```javascript
// Frida script example (bypass isPremium check)
Java.perform(function() {
    var SharedPreferences = Java.use("android.content.SharedPreferences");
    SharedPreferences.getBoolean.overload('java.lang.String', 'boolean').implementation = function(key, defValue) {
        if (key.includes("premium") || key.includes("pro") || key.includes("license")) {
            console.log("[+] Bypassing premium check: " + key + " -> true");
            return true;
        }
        return this.getBoolean(key, defValue);
    };
});
```

Run: `frida -U -f com.package.name -l bypass.js --no-pause`

4. **Or use Lucky Patcher** (easier for non-root):
   - Install Lucky Patcher on Android
   - Open APK in Lucky Patcher
   - Create Modified APK → APK with LVL Emulation

## Common Errors & Fixes

### Error: "Application not installed because package appears invalid"

**Cause 1:** Manual Python zipfile repack (corrupt structure)
**Fix:** Use apktool for decompile/recompile (Steps 2, 4)

**Cause 2:** Signed with jarsigner only (missing v2/v3 signatures)
**Fix:** Use uber-apk-signer (Step 5)

**Cause 3:** APK not zipaligned
**Fix:** uber-apk-signer auto-handles this

### Error: "INSTALL_PARSE_FAILED_NO_CERTIFICATES"

**Cause:** APK unsigned or signature corrupted
**Fix:** Re-sign with uber-apk-signer (Step 5)

### Error: "INSTALL_FAILED_UPDATE_INCOMPATIBLE"

**Cause:** Trying to install over existing app with different signature
**Fix:** Uninstall original app first, then install modded APK

### Apktool Error: "brut.common.BrutException: could not exec"

**Cause:** aapt/aapt2 binary missing or not executable
**Fix:** 
```bash
# Linux/Mac
chmod +x ~/.local/share/apktool/framework/aapt*

# Windows: download aapt.exe separately and place in apktool dir
```

## Signature Schemes Explained

| Scheme | Android Version | Tool Support |
|:-------|:----------------|:-------------|
| **v1 (JAR)** | All versions | jarsigner, apksigner, uber-apk-signer |
| **v2 (APK)** | 7.0+ (API 24+) | apksigner, uber-apk-signer |
| **v3 (APK)** | 9.0+ (API 28+) | apksigner, uber-apk-signer |
| **v4 (Streaming)** | 11.0+ (API 30+) | uber-apk-signer |

**Modern best practice:** Sign with v1+v2+v3 for maximum compatibility (Android 4.4 - 15). uber-apk-signer does this automatically.

**Why jarsigner fails:** It only signs v1. Android 7+ verifies v2/v3 first if present; if absent but targeting API 24+, install fails.

## Tool Comparison

| Tool | Pros | Cons |
|:-----|:-----|:-----|
| **apktool** | Proper decompile, editable XML/smali, preserves structure | Requires Java, slower than zipfile |
| **uber-apk-signer** | One-step zipalign+sign, all schemes, auto-verify | Requires Java |
| **jarsigner** | Built-in to JDK | v1 only, fails on Android 7+ |
| **Python zipfile** | Fast, no deps | Corrupts APK structure, DO NOT USE |
| **Lucky Patcher** | User-friendly GUI, works on-device | Requires Android device, not scriptable |

## Quick Reference

```bash
# Full workflow
java -jar apktool.jar d original.apk -o app-decompiled -f
# [modify app-decompiled/AndroidManifest.xml or smali/]
java -jar apktool.jar b app-decompiled -o app-unsigned.apk
java -jar uber-apk-signer.jar --apks app-unsigned.apk --allowResign
# Result: app-aligned-debugSigned.apk
```

## When This Workflow Fails

**1. Obfuscated code** — ProGuard/R8 makes smali unreadable. Need to:
- Reverse-engineer with jadx-gui
- Find obfuscated class/method names
- Patch by signature, not by readable name

**2. Anti-tamper checks** — App detects modification at runtime:
- Signature verification checks
- Root detection
- Emulator detection

**Bypass:**
- Patch signature check in smali (search for `getPackageInfo`, `GET_SIGNATURES`)
- Use Magisk Hide for root detection
- Use Frida to hook detection methods

**3. Server-side validation** — App checks license/premium status via API:
- Static patching won't help if server validates
- Need to intercept API calls (mitmproxy + Frida SSL unpinning)
- Or find private server / crack server-side logic

## Source & Documentation

- **apktool:** https://github.com/iBotPeaches/Apktool
- **uber-apk-signer:** https://github.com/patrickfav/uber-apk-signer
- **APK Signature Scheme:** https://source.android.com/docs/security/features/apksigning

## Related Skills

- `game-modder-apk` — Higher-level Python wrapper (less reliable, use this workflow instead for serious mods)
- `sqlmap` — SQL injection for server-side premium bypass
- `godmode` — Jailbreak LLM API calls (unrelated but similar "unlock" concept)
