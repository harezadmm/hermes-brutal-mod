---
name: mobile-app-cracking
description: Crack mobile apps to bypass premium and licensing checks.
tags: [android, ios, cracking, reverse-engineering, patching]
version: 1.0
author: RedMess
license: MIT
---

# Mobile App Cracking

## When to Use
Use when cracking Android/iOS apps to bypass premium features, licensing, in-app purchases, or subscription checks.

## Android App Cracking

### Tools Required
- **APKTool** - Decompile/recompile APKs
- **JADX** - Java decompiler
- **Lucky Patcher** - Automated patching framework
- **Frida** - Runtime hooking
- **apksigner** - Re-sign modified APKs

### Basic APK Cracking Flow

#### 1. Decompile APK
```bash
# Decompile APK to smali
apktool d app.apk -o app_decompiled

# Decompile to Java (for analysis)
jadx app.apk -d app_java
```

#### 2. Find Premium Check Logic
```bash
# Search for common patterns
cd app_java
grep -r "isPremium" .
grep -r "isSubscribed" .
grep -r "validateLicense" .
grep -r "checkPurchase" .
```

#### 3. Patch Smali Code
```smali
# Original code in MainActivity.smali
.method public isPremium()Z
    .locals 1
    invoke-direct {p0}, Lcom/app/license/LicenseChecker;->checkLicense()Z
    move-result v0
    return v0
.end method

# Patched version - always return true
.method public isPremium()Z
    .locals 1
    const/4 v0, 0x1    # Force return true
    return v0
.end method
```

#### 4. Remove License Check Calls
```smali
# Find and comment out license validation
# Before:
invoke-virtual {p0}, Lcom/app/MainActivity;->validateLicense()V

# After:
# invoke-virtual {p0}, Lcom/app/MainActivity;->validateLicense()V
```

#### 5. Recompile & Sign
```bash
# Recompile APK
apktool b app_decompiled -o app_cracked.apk

# Generate keystore
keytool -genkey -v -keystore my.keystore -alias mykey -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my.keystore app_cracked.apk mykey

# Zipalign
zipalign -v 4 app_cracked.apk app_cracked_aligned.apk

# Install
adb install app_cracked_aligned.apk
```

### Advanced: Frida Runtime Patching
```javascript
// bypass_premium.js
Java.perform(function() {
    // Hook premium check
    var MainActivity = Java.use("com.example.app.MainActivity");
    
    MainActivity.isPremium.implementation = function() {
        console.log("[+] isPremium() called - returning true");
        return true;
    };
    
    // Hook in-app purchase verification
    var IabHelper = Java.use("com.android.billingclient.api.Purchase");
    
    IabHelper.getPurchaseState.implementation = function() {
        console.log("[+] Purchase state bypassed");
        return 1; // PURCHASED
    };
    
    // Hook license validator
    var LicenseValidator = Java.use("com.google.android.vending.licensing.LicenseValidator");
    
    LicenseValidator.verify.overload("com.google.android.vending.licensing.Policy", "com.google.android.vending.licensing.ResponseData").implementation = function(policy, data) {
        console.log("[+] License validation bypassed");
        return 0; // LICENSED
    };
});
```

**Run Frida:**
```bash
frida -U -f com.example.app -l bypass_premium.js --no-pause
```

### Lucky Patcher Automation
```bash
# Install Lucky Patcher
adb install LuckyPatcher.apk

# Patch app via CLI (if rooted)
adb shell
su
pm grant ru.chelpus.luckypatcher android.permission.WRITE_EXTERNAL_STORAGE

# Auto-patch options:
# 1. Remove license verification
# 2. Remove Google Ads
# 3. Mod APK (custom patches)
```

## iOS App Cracking

### Tools Required
- **Clutch** - Decrypt App Store apps (jailbreak required)
- **class-dump** - Extract Objective-C headers
- **Hopper Disassembler** - Reverse engineering
- **Frida** - Runtime hooking
- **iOS App Signer** - Re-sign IPAs

### Decrypt IPA (Jailbroken Device)
```bash
# SSH to iPhone
ssh root@iphone-ip

# List installed apps
Clutch -i

# Decrypt app
Clutch -d com.example.app

# Download decrypted IPA
scp root@iphone-ip:/var/root/Documents/Decrypted/*.ipa .
```

### Find Premium Check (Hopper/IDA)
```bash
# Extract headers
class-dump -H app.app -o headers/

# Search for premium methods
grep -r "premium" headers/
grep -r "isPro" headers/
grep -r "subscription" headers/
```

### Patch with Frida (iOS)
```javascript
// ios_premium_bypass.js
if (ObjC.available) {
    var ViewController = ObjC.classes.ViewController;
    
    // Hook isPremiumUser method
    var isPremium = ViewController['- isPremiumUser'];
    Interceptor.attach(isPremium.implementation, {
        onLeave: function(retval) {
            console.log('[+] isPremiumUser called, forcing YES');
            retval.replace(ptr('0x1')); // Return YES
        }
    });
    
    // Hook purchase validation
    var validatePurchase = ObjC.classes.StoreManager['- validateReceipt:'];
    Interceptor.attach(validatePurchase.implementation, {
        onLeave: function(retval) {
            console.log('[+] Receipt validation bypassed');
            retval.replace(ptr('0x1')); // Valid receipt
        }
    });
}
```

**Run on iOS:**
```bash
frida -U -f com.example.app -l ios_premium_bypass.js
```

### Re-sign IPA
```bash
# Extract IPA
unzip app.ipa

# Modify Info.plist / binary patches
# ...

# Re-sign with personal certificate
codesign -f -s "iPhone Developer: Your Name" Payload/App.app

# Re-package
zip -r app_cracked.ipa Payload/

# Install
ideviceinstaller -i app_cracked.ipa
```

## Bypass Subscription Checks

### Common Patterns to Patch
```java
// Java/Kotlin (Android)
// Pattern 1: Boolean check
if (user.isSubscribed()) { /* premium features */ }
// Patch: Always return true

// Pattern 2: Expiry date
if (subscription.expiryDate > currentDate) { /* ... */ }
// Patch: Set expiryDate to far future

// Pattern 3: Server validation
if (api.validateSubscription(userId)) { /* ... */ }
// Patch: Mock server response or skip call
```

### Server-Side Bypass (MITM)
```python
# mitmproxy script to fake subscription response
from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if "api.example.com/subscription" in flow.request.url:
        flow.response = http.Response.make(
            200,
            b'{"subscribed": true, "premium": true, "expiry": "2099-12-31"}',
            {"Content-Type": "application/json"}
        )
```

**Run:**
```bash
mitmproxy -s fake_subscription.py
# Configure phone to use proxy
```

## Remove Ads from Apps

### Smali Patch (Android)
```smali
# Find AdMob initialization
.method private loadAd()V
    # Comment out ad loading
    # invoke-virtual {v0}, Lcom/google/android/gms/ads/AdView;->loadAd(Lcom/google/android/gms/ads/AdRequest;)V
    return-void
.end method
```

### Frida Ad Blocker
```javascript
Java.perform(function() {
    var AdView = Java.use("com.google.android.gms.ads.AdView");
    AdView.loadAd.implementation = function() {
        console.log("[+] Ad blocked");
        return;
    };
});
```

## Pitfalls
1. **Certificate pinning** - Use Frida SSL bypass or patch out pinning
2. **Root detection** - Hide root with Magisk Hide or patch detection
3. **Obfuscated code** - Use deobfuscators (ProGuard/R8 reversal)
4. **Server-side validation** - MITM or find client-side bypass
5. **Integrity checks** - Patch checksum validation

## Verification
```bash
# Test cracked APK
adb install -r app_cracked.apk
adb logcat | grep -i "premium\|license"

# Verify premium features unlocked
# Open app, test locked features
```

## Related Skills
- apk-vvvip-modding
- frida-runtime-hooking
- android-16-apk-modding
- flutter-app-detection