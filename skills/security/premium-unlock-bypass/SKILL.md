---
name: premium-unlock-bypass
description: Bypass premium features and subscription locks in apps.
tags: [premium-unlock, in-app-purchase, subscription-bypass, cracking]
version: 1.0
author: RedMess
license: MIT
---

# Premium Unlock & Bypass

## When to Use
Use when unlocking premium features, bypassing in-app purchases, subscription checks, or paywalls in mobile/desktop apps.

## Android Premium Bypass

### Method 1: Lucky Patcher
```bash
# Install Lucky Patcher
adb install LuckyPatcher.apk

# Root required for full functionality
adb shell
su

# Auto-patch app
# 1. Open Lucky Patcher
# 2. Select target app
# 3. Menu of Patches → Create Modified APK
# 4. Select: "APK rebuilt for InApp and LVL emulation"
# 5. Install patched APK
```

### Method 2: Frida In-App Purchase Bypass
```javascript
// iap_bypass.js - Universal IAP bypass
Java.perform(function() {
    console.log("[*] Starting IAP bypass...");
    
    // Google Play Billing v5+
    try {
        var BillingResult = Java.use("com.android.billingclient.api.BillingResult");
        var Purchase = Java.use("com.android.billingclient.api.Purchase");
        var PurchasesList = Java.use("java.util.ArrayList");
        
        var BillingClient = Java.use("com.android.billingclient.api.BillingClient");
        BillingClient.queryPurchasesAsync.overload("com.android.billingclient.api.QueryPurchasesParams", "com.android.billingclient.api.PurchasesResponseListener").implementation = function(params, listener) {
            console.log("[+] queryPurchasesAsync hooked");
            
            var billingResult = BillingResult.newBuilder()
                .setResponseCode(0) // OK
                .build();
            
            var fakePurchasesList = PurchasesList.$new();
            listener.onQueryPurchasesResponse(billingResult, fakePurchasesList);
        };
    } catch(e) {
        console.log("[-] Play Billing v5 not found: " + e);
    }
    
    // Legacy IAB Helper
    try {
        var IabHelper = Java.use("com.android.vending.billing.IInAppBillingService$Stub$Proxy");
        IabHelper.isBillingSupported.implementation = function() {
            console.log("[+] isBillingSupported bypassed");
            return 0; // BILLING_RESPONSE_RESULT_OK
        };
        
        IabHelper.getPurchases.implementation = function(apiVersion, packageName, type, continuationToken) {
            console.log("[+] getPurchases hooked - returning fake purchases");
            var Bundle = Java.use("android.os.Bundle");
            var bundle = Bundle.$new();
            bundle.putInt("RESPONSE_CODE", 0);
            
            var purchaseDataList = Java.use("java.util.ArrayList").$new();
            purchaseDataList.add('{"productId":"premium","purchaseToken":"fake_token","purchaseState":0}');
            bundle.putStringArrayList("INAPP_PURCHASE_DATA_LIST", purchaseDataList);
            
            return bundle;
        };
    } catch(e) {
        console.log("[-] IAB Helper not found: " + e);
    }
    
    // Common premium checks
    try {
        var SharedPreferences = Java.use("android.app.SharedPreferencesImpl");
        SharedPreferences.getBoolean.overload("java.lang.String", "boolean").implementation = function(key, defValue) {
            if (key.toLowerCase().includes("premium") || 
                key.toLowerCase().includes("pro") || 
                key.toLowerCase().includes("paid") ||
                key.toLowerCase().includes("subscribed")) {
                console.log("[+] Premium check bypassed for key: " + key);
                return true;
            }
            return this.getBoolean(key, defValue);
        };
        
        SharedPreferences.getLong.overload("java.lang.String", "long").implementation = function(key, defValue) {
            if (key.toLowerCase().includes("expiry") || 
                key.toLowerCase().includes("expire") ||
                key.toLowerCase().includes("trial")) {
                console.log("[+] Expiry check bypassed for key: " + key);
                return 9999999999999; // Far future timestamp
            }
            return this.getLong(key, defValue);
        };
    } catch(e) {
        console.log("[-] SharedPreferences hook failed: " + e);
    }
    
    console.log("[*] IAP bypass ready");
});
```

**Run Frida:**
```bash
frida -U -f com.example.app -l iap_bypass.js --no-pause
```

### Method 3: Manual Smali Patching
```bash
# Decompile APK
apktool d app.apk

# Find premium check
cd app
grep -r "isPremium\|hasPremium\|isSubscribed" --include="*.smali"

# Example result: com/example/app/PremiumManager.smali
```

**Edit Smali:**
```smali
# Original method
.method public isPremiumUser()Z
    .locals 2
    invoke-direct {p0}, Lcom/example/app/PremiumManager;->checkSubscription()Z
    move-result v0
    return v0
.end method

# Patched - always return true
.method public isPremiumUser()Z
    .locals 1
    const/4 v0, 0x1    # true
    return v0
.end method
```

**Recompile:**
```bash
apktool b app -o app_premium.apk
java -jar uber-apk-signer.jar -a app_premium.apk
adb install app_premium-aligned-signed.apk
```

### Method 4: Local Database Modification
```bash
# Find app's database
adb shell
su
cd /data/data/com.example.app/databases/

# List databases
ls -la

# Pull database
exit
adb pull /data/data/com.example.app/databases/app.db

# Modify with SQLite
sqlite3 app.db
SELECT * FROM users;
UPDATE users SET is_premium=1, subscription_end='2099-12-31';
.quit

# Push back
adb push app.db /data/data/com.example.app/databases/
adb shell
su
chmod 660 /data/data/com.example.app/databases/app.db
chown u0_a123:u0_a123 /data/data/com.example.app/databases/app.db
```

## iOS Premium Bypass

### Method 1: Frida iOS IAP Bypass
```javascript
// ios_iap_bypass.js
if (ObjC.available) {
    console.log("[*] iOS IAP bypass starting...");
    
    // Hook SKPaymentQueue to fake purchases
    var SKPaymentQueue = ObjC.classes.SKPaymentQueue;
    var originalFinish = SKPaymentQueue['- finishTransaction:'];
    
    Interceptor.attach(originalFinish.implementation, {
        onEnter: function(args) {
            var transaction = new ObjC.Object(args[2]);
            console.log("[+] Transaction finished: " + transaction.toString());
        }
    });
    
    // Hook receipt validation
    var NSBundle = ObjC.classes.NSBundle;
    var appStoreReceiptURL = NSBundle['- appStoreReceiptURL'];
    
    Interceptor.attach(appStoreReceiptURL.implementation, {
        onLeave: function(retval) {
            console.log("[+] Receipt URL requested - spoofing valid receipt");
            // Point to fake receipt or return valid URL
        }
    });
    
    // Hook premium checks (common patterns)
    var viewController = ObjC.classes.ViewController;
    if (viewController) {
        var isPremium = viewController['- isPremiumUser'];
        if (isPremium) {
            Interceptor.attach(isPremium.implementation, {
                onLeave: function(retval) {
                    console.log("[+] isPremiumUser hooked - returning YES");
                    retval.replace(ptr('0x1'));
                }
            });
        }
    }
    
    console.log("[*] iOS IAP bypass ready");
}
```

**Run:**
```bash
frida -U -f com.example.app -l ios_iap_bypass.js
```

### Method 2: Modify App Plist
```bash
# SSH to jailbroken iPhone
ssh root@192.168.1.100

# Find app bundle
cd /var/containers/Bundle/Application/

# Find app
find . -name "*.app" | grep -i appname

# Edit Info.plist
cd <app-guid>/App.app/
plutil -convert xml1 Info.plist
nano Info.plist

# Add keys to fake premium
<key>PremiumUnlocked</key>
<true/>
<key>SubscriptionActive</key>
<true/>

# Convert back
plutil -convert binary1 Info.plist

# Kill and restart app
killall App
```

### Method 3: iGameGod / iAP Cracker
```bash
# Install iGameGod (jailbreak required)
# Cydia → Add Source → http://iosgods.com/repo
# Search: iGameGod
# Install

# In-app:
# 1. Open iGameGod overlay in app
# 2. Select "iAP Cracker"
# 3. Enable "Free In-App Purchases"
# 4. Attempt purchase in app → will succeed without payment
```

## Web App Premium Bypass

### Method 1: LocalStorage/Cookie Manipulation
```javascript
// Open browser console (F12)

// Check localStorage for premium flags
console.log(localStorage);

// Set premium flags
localStorage.setItem('isPremium', 'true');
localStorage.setItem('subscriptionStatus', 'active');
localStorage.setItem('userTier', 'premium');
localStorage.setItem('expiryDate', '9999999999999');

// Check cookies
document.cookie.split(';').forEach(c => console.log(c));

// Set premium cookie
document.cookie = "premium=true; path=/";
document.cookie = "subscription=active; path=/";

// Reload page
location.reload();
```

### Method 2: JavaScript Hook Injection
```javascript
// Tampermonkey/Greasemonkey script
// ==UserScript==
// @name         Premium Unlocker
// @match        https://example.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    // Hook API calls
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            if (args[0].includes('/api/user/status')) {
                return response.json().then(data => {
                    data.isPremium = true;
                    data.subscription = 'active';
                    return new Response(JSON.stringify(data), response);
                });
            }
            return response;
        });
    };
    
    // Override premium check functions
    window.checkPremium = function() { return true; };
    window.isPremiumUser = function() { return true; };
})();
```

### Method 3: MITM Proxy Modification
```python
# mitmproxy_premium.py
from mitmproxy import http
import json

def response(flow: http.HTTPFlow) -> None:
    # Hook subscription API
    if "api.example.com/user/subscription" in flow.request.url:
        data = {
            "status": "active",
            "tier": "premium",
            "expires": "2099-12-31T23:59:59Z"
        }
        flow.response = http.Response.make(
            200,
            json.dumps(data).encode(),
            {"Content-Type": "application/json"}
        )
    
    # Unlock premium features
    if "api.example.com/features" in flow.request.url:
        try:
            content = json.loads(flow.response.content)
            for feature in content.get('features', []):
                feature['locked'] = False
                feature['premium'] = False
            flow.response.content = json.dumps(content).encode()
        except:
            pass
```

**Run:**
```bash
mitmproxy -s mitmproxy_premium.py
# Configure app to use proxy: 127.0.0.1:8080
```

## Desktop App Premium Bypass

### Method 1: Registry Modification (Windows)
```batch
REM Find app's registry keys
reg query HKCU\Software /s | findstr /i "AppName"

REM Modify premium flags
reg add "HKCU\Software\AppName" /v IsPremium /t REG_DWORD /d 1 /f
reg add "HKCU\Software\AppName" /v LicenseKey /t REG_SZ /d "PREMIUM-LICENSE-KEY" /f
reg add "HKCU\Software\AppName" /v ExpiryDate /t REG_SZ /d "2099-12-31" /f
```

### Method 2: Config File Patching
```bash
# Find config file
find ~/ -name "*appname*" -type f 2>/dev/null

# Common locations:
# Windows: %APPDATA%\AppName\config.json
# Linux: ~/.config/appname/settings.json
# macOS: ~/Library/Application Support/AppName/config.plist

# Modify JSON config
cat > config.json << EOF
{
  "premium": true,
  "license": {
    "type": "lifetime",
    "status": "active"
  },
  "features": {
    "pro_mode": true,
    "export_hd": true
  }
}
EOF
```

### Method 3: DLL/Dylib Injection
```cpp
// premium_unlock.cpp
#include <Windows.h>

BOOL WINAPI DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        // Find and patch premium check
        HMODULE hApp = GetModuleHandle(NULL);
        DWORD_PTR baseAddr = (DWORD_PTR)hApp;
        
        // Patch isPremium function to always return true
        BYTE* checkAddr = (BYTE*)(baseAddr + 0x12340); // Offset from IDA
        
        DWORD oldProtect;
        VirtualProtect(checkAddr, 2, PAGE_EXECUTE_READWRITE, &oldProtect);
        checkAddr[0] = 0xB0; // MOV AL, 1
        checkAddr[1] = 0x01;
        checkAddr[2] = 0xC3; // RET
        VirtualProtect(checkAddr, 2, oldProtect, &oldProtect);
    }
    return TRUE;
}
```

## Subscription Bypass Patterns

### Common Checks to Bypass
```python
# Pattern 1: Expiry date check
def is_subscribed():
    expiry = get_expiry_date()
    return datetime.now() < expiry
# Bypass: Set expiry to far future

# Pattern 2: Server validation
def validate_subscription():
    response = api.check_subscription(user_id)
    return response.status == "active"
# Bypass: MITM fake response or patch function

# Pattern 3: Receipt validation
def verify_receipt(receipt):
    return apple.verify(receipt) or google.verify(receipt)
# Bypass: Return true or provide fake receipt

# Pattern 4: Feature flag
def can_use_premium_feature():
    return user.tier == "premium"
# Bypass: Set tier to premium in storage
```

## Automated Premium Unlocker
```python
# auto_premium_unlock.py
import frida
import sys

# Frida script
js_code = """
Java.perform(function() {
    // Hook all boolean methods containing "premium/pro/subscription"
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            try {
                var clazz = Java.use(className);
                var methods = clazz.class.getDeclaredMethods();
                methods.forEach(function(method) {
                    var methodName = method.getName();
                    if ((methodName.toLowerCase().includes('premium') ||
                         methodName.toLowerCase().includes('pro') ||
                         methodName.toLowerCase().includes('subscri')) &&
                        method.getReturnType().getName() == 'boolean') {
                        
                        var impl = clazz[methodName];
                        if (impl) {
                            impl.implementation = function() {
                                console.log('[+] Hooked: ' + className + '.' + methodName);
                                return true;
                            };
                        }
                    }
                });
            } catch(e) {}
        },
        onComplete: function() {}
    });
});
"""

# Attach to app
device = frida.get_usb_device()
pid = device.spawn(["com.example.app"])
session = device.attach(pid)
script = session.create_script(js_code)
script.load()
device.resume(pid)

sys.stdin.read()
```

## Pitfalls
1. **Server-side validation** - Can't fully bypass server checks
2. **Certificate pinning** - MITM requires pinning bypass
3. **Root/jailbreak detection** - Hide root before bypass
4. **Obfuscation** - Hard to find premium checks in obfuscated code
5. **Online-only features** - Require valid subscription token

## Verification
```bash
# Android
adb shell
dumpsys package com.example.app | grep -i premium

# iOS
ssh root@iphone
cat /var/mobile/Containers/Data/Application/<guid>/Library/Preferences/com.example.app.plist

# Check if premium features accessible
```

## Related Skills
- mobile-app-cracking
- frida-runtime-hooking
- desktop-app-cracking
- network-sniffing-mitm