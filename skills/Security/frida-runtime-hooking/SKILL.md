---
name: frida-runtime-hooking
description: Bypass any app check at runtime using Frida dynamic hooking.
version: 1.0.0
trigger: When static patching fails, need runtime bypass, or hooking required
tags: [android, frida, hooking, runtime, reverse-engineering]
---

# Frida Runtime Hooking - Bypass Anything

Bypass premium checks, root detection, SSL pinning, and more at **runtime** without modifying APK.

## Why Frida

**When static patching (APKTool) fails:**
- ✅ Flutter apps (can't patch libapp.so)
- ✅ Server validation (hook before server call)
- ✅ Obfuscated code (hook by pattern)
- ✅ Root detection (hide root at runtime)
- ✅ SSL pinning (MITM any app)

**Frida = Runtime code injection** - modify behavior while app runs.

---

## Setup (One-Time)

### 1. Install Frida Tools

```bash
pip3 install frida-tools objection --user
```

### 2. Download Frida Server for Android

```bash
# Check device architecture
adb shell getprop ro.product.cpu.abi
# Output: arm64-v8a

# Download matching frida-server
curl -L -o frida-server https://github.com/frida/frida/releases/download/16.5.9/frida-server-16.5.9-android-arm64.xz
unxz frida-server*.xz
```

### 3. Push to Device

```bash
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "su -c '/data/local/tmp/frida-server &'"
```

**Frida server now running on device!**

---

## Basic Hooking Examples

### Hook isPremium() → Always Return True

```javascript
// hook_premium.js
Java.perform(function() {
    var AppUser = Java.use("com.app.model.AppUser");
    
    AppUser.isPremium.implementation = function() {
        console.log("[+] isPremium() called - returning TRUE");
        return true;  // Force premium
    };
    
    console.log("[+] Hooked isPremium()");
});
```

**Run:**
```bash
frida -U -f com.app.package -l hook_premium.js --no-pause
```

---

### Hook Method with Arguments

```javascript
// hook_purchase.js
Java.perform(function() {
    var BillingClient = Java.use("com.android.billingclient.api.BillingClient");
    
    BillingClient.isReady.implementation = function() {
        console.log("[+] BillingClient.isReady() - returning TRUE");
        return true;
    };
    
    // Hook purchase result
    var Purchase = Java.use("com.android.billingclient.api.Purchase");
    Purchase.getPurchaseState.implementation = function() {
        console.log("[+] getPurchaseState() - returning PURCHASED (1)");
        return 1;  // 1 = PURCHASED
    };
});
```

---

### Find and Hook Unknown Method

```javascript
// hook_all_methods.js
Java.perform(function() {
    var targetClass = Java.use("com.app.premium.PremiumManager");
    
    // Hook ALL methods in class
    var methods = targetClass.class.getDeclaredMethods();
    methods.forEach(function(method) {
        var methodName = method.getName();
        
        try {
            targetClass[methodName].implementation = function() {
                console.log("[+] Called: " + methodName);
                var result = this[methodName].apply(this, arguments);
                console.log("    Returned: " + result);
                
                // Force true for boolean methods
                if (methodName.startsWith("is") || methodName.startsWith("check")) {
                    console.log("    [!] Forcing TRUE");
                    return true;
                }
                
                return result;
            };
        } catch(e) {}
    });
});
```

---

## Advanced: SSL Pinning Bypass (MITM Any App)

```javascript
// bypass_ssl_pinning.js
Java.perform(function() {
    console.log("[+] Bypassing SSL Pinning...");
    
    // Hook TrustManagerImpl
    var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
    
    TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
        console.log("[+] SSL verification bypassed for: " + host);
        return untrustedChain;
    };
    
    TrustManagerImpl.checkTrustedRecursive.implementation = function(certs, host, clientAuth, untrustedChain, trustAnchorChain, used) {
        console.log("[+] Certificate check bypassed");
        return Java.use("java.util.ArrayList").$new();
    };
    
    console.log("[+] SSL Pinning bypass active");
});
```

**Now intercept HTTPS traffic with Burp Suite/mitmproxy!**

---

## Root Detection Bypass

```javascript
// bypass_root.js
Java.perform(function() {
    console.log("[+] Hiding root...");
    
    // Hook common root checks
    var File = Java.use("java.io.File");
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        
        // Hide root files
        if (path.indexOf("su") >= 0 || 
            path.indexOf("magisk") >= 0 ||
            path.indexOf("superuser") >= 0) {
            console.log("[+] Hiding: " + path);
            return false;
        }
        
        return this.exists.call(this);
    };
    
    // Hook Runtime.exec (su command)
    var Runtime = Java.use("java.lang.Runtime");
    Runtime.exec.overload("java.lang.String").implementation = function(cmd) {
        if (cmd.indexOf("su") >= 0) {
            console.log("[+] Blocked su command: " + cmd);
            throw new Error("su not found");
        }
        return this.exec.call(this, cmd);
    };
    
    console.log("[+] Root detection bypassed");
});
```

---

## Hook Native Library (C/C++)

```javascript
// hook_native.js
var libnative = Module.findExportByName("libnative.so", "checkLicense");

if (libnative) {
    Interceptor.attach(libnative, {
        onEnter: function(args) {
            console.log("[+] checkLicense() called");
        },
        onLeave: function(retval) {
            console.log("[+] Original return: " + retval);
            retval.replace(1);  // Force return 1 (true)
            console.log("[+] Modified return: " + retval);
        }
    });
    console.log("[+] Hooked native checkLicense()");
}
```

---

## Objection - Quick Pentest Tool

```bash
# Start objection
objection -g com.app.package explore

# Inside objection console:
android hooking list classes              # List all classes
android hooking search methods isPremium  # Find methods
android hooking watch class com.app.User  # Watch class
android ui screenshot /tmp/screen.png     # Take screenshot
android heap search instances com.app.User # Find objects in memory
android root disable                       # Bypass root detection
android sslpinning disable                 # Bypass SSL pinning

# Memory dump
memory dump all /tmp/memory.bin
memory list modules
```

**Objection = Automated Frida scripts!**

---

## Flutter App Hooking

```javascript
// hook_flutter.js
// Flutter uses Dart VM - different approach

// Find Dart methods by pattern
Process.enumerateModules().forEach(function(module) {
    if (module.name === "libapp.so") {
        console.log("[+] Found Flutter libapp.so");
        
        // Hook by address (need to find with reFlutter first)
        var premiumCheck = module.base.add(0x123456);
        
        Interceptor.attach(premiumCheck, {
            onEnter: function(args) {
                console.log("[+] Premium check called");
            },
            onLeave: function(retval) {
                retval.replace(1);  // Force true
            }
        });
    }
});
```

**Note:** Flutter harder to hook - use reFlutter to find methods first.

---

## Complete Workflow

### 1. Identify Target

```bash
# List running apps
frida-ps -U

# Explore app
objection -g com.app.package explore
```

### 2. Find Target Method

```javascript
// search_methods.js
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.indexOf("premium") >= 0 || 
                className.indexOf("billing") >= 0) {
                console.log("[+] Found: " + className);
            }
        },
        onComplete: function() {
            console.log("[+] Search complete");
        }
    });
});
```

### 3. Hook and Test

```bash
frida -U -f com.app.package -l hook.js --no-pause
```

### 4. Make Permanent (Optional)

Use **Frida-Gadget** to inject into APK for permanent hooks.

---

## Pro Tips

**Find obfuscated methods:**
```javascript
// Hook by return type
Java.enumerateLoadedClasses({
    onMatch: function(className) {
        try {
            var clazz = Java.use(className);
            var methods = clazz.class.getDeclaredMethods();
            
            methods.forEach(function(method) {
                var returnType = method.getReturnType().toString();
                
                // Find boolean methods (likely checks)
                if (returnType === "boolean") {
                    console.log(className + "." + method.getName());
                }
            });
        } catch(e) {}
    }
});
```

**Trace all method calls:**
```bash
# Using objection
android hooking watch class_method com.app.User.* --dump-args --dump-return
```

**Universal SSL Pinning Bypass:**
```bash
objection -g com.app.package explore
android sslpinning disable
```

---

## Common Targets

| Target | Hook Point | Force Return |
|--------|-----------|--------------|
| Premium check | isPremium() | true |
| Root detection | File.exists("/su") | false |
| License check | checkLicense() | true/1 |
| Billing | getPurchaseState() | 1 (PURCHASED) |
| SSL Pinning | TrustManager | bypass |
| Trial expired | isTrialExpired() | false |

---

## Troubleshooting

**Error: "Failed to spawn"**
```bash
# Check frida-server running
adb shell "ps | grep frida"

# Restart frida-server
adb shell "su -c 'killall frida-server'"
adb shell "su -c '/data/local/tmp/frida-server &'"
```

**Error: "Class not found"**
- App might not be loaded yet
- Use `Java.choose()` to find existing instances
- Hook later in app lifecycle

**Method has multiple overloads:**
```javascript
AppUser.isPremium.overload().implementation = function() { ... }
AppUser.isPremium.overload('boolean').implementation = function(arg) { ... }
```

---

## Key Advantages Over Static Patching

- ✅ Works on Flutter apps
- ✅ Bypass server validation (hook before send)
- ✅ No APK modification needed
- ✅ Reversible (just restart app)
- ✅ Can intercept network traffic
- ✅ Real-time debugging

**Frida = Hacker-tier modding!**

---

**Version:** 1.0.0  
**Created:** 2026-08-25  
**Requirement:** Rooted device or Frida-Gadget injection
