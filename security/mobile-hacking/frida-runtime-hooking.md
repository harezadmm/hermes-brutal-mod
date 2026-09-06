---
description: Bypass app security at runtime using Frida dynamic instrumentation
category: security/mobile-hacking
tags: [frida, android, ios, runtime-hooking, bypass, mobile]
platform: [android, ios]
difficulty: advanced
tools: [frida, adb, objection, python3]
mitre_attack: [T1629]
---

# Frida Runtime Hooking

## When to Use
Use Frida when you need to:
- Bypass SSL pinning in mobile apps
- Bypass root/jailbreak detection
- Modify app behavior at runtime
- Extract encryption keys from memory
- Bypass authentication checks
- Analyze obfuscated code
- Intercept API calls and modify responses

Common scenarios:
- Mobile app penetration testing
- Reverse engineering proprietary protocols
- Bug bounty hunting on mobile apps
- Malware analysis

## Prerequisites
- Frida installed: `pip3 install frida-tools`
- Rooted Android device OR jailbroken iOS device
- USB debugging enabled (Android)
- Target app installed
- Basic JavaScript knowledge

## Architecture

```
PC (Frida Client)          Mobile Device (Frida Server)
┌──────────────────┐       ┌─────────────────────────┐
│  Python Script   │       │    frida-server         │
│  (frida CLI)     │◄─────►│    (running as root)    │
│                  │  USB  │                         │
│  JavaScript      │       │  ┌──────────────────┐   │
│  Hook Code       │       │  │  Target App      │   │
└──────────────────┘       │  │  ┌────────────┐  │   │
                           │  │  │ Hooked     │  │   │
                           │  │  │ Functions  │  │   │
                           │  │  └────────────┘  │   │
                           │  └──────────────────┘   │
                           └─────────────────────────┘
```

## Step-by-Step

### 1. Install Frida Server on Device

**Android:**
```bash
# Download frida-server for device architecture
# Check architecture first
adb shell getprop ro.product.cpu.abi
# Output: arm64-v8a, armeabi-v7a, or x86

# Download matching frida-server
wget https://github.com/frida/frida/releases/download/16.1.4/frida-server-16.1.4-android-arm64.xz

# Extract
unxz frida-server-16.1.4-android-arm64.xz
mv frida-server-16.1.4-android-arm64 frida-server

# Push to device
adb push frida-server /data/local/tmp/

# Make executable and run
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

**iOS (jailbroken):**
```bash
# Add Frida repo to Cydia
# Sources → Edit → Add → https://build.frida.re

# Install "Frida" package from Cydia

# Or via SSH
ssh root@<device-ip>  # Default password: alpine
apt-get install re.frida.server
/usr/sbin/frida-server &
```

### 2. Verify Frida Connection

```bash
# List processes on device
frida-ps -U

# Should show running apps and their PIDs
# If empty, frida-server not running or USB debug off
```

### 3. Bypass SSL Pinning

SSL pinning prevents MITM even with trusted CA cert. Bypass it to intercept HTTPS traffic.

**Universal Android SSL Bypass:**
```javascript
// ssl-bypass.js
Java.perform(function() {
    console.log("[*] Bypassing SSL Pinning...");
    
    // Hook SSLContext.init()
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    SSLContext.init.overload(
        '[Ljavax.net.ssl.KeyManager;',
        '[Ljavax.net.ssl.TrustManager;',
        'java.security.SecureRandom'
    ).implementation = function(keyManager, trustManager, secureRandom) {
        console.log("[+] SSLContext.init() hooked");
        
        // Create custom TrustManager that trusts everything
        var TrustManager = Java.registerClass({
            name: 'custom.TrustManager',
            implements: [Java.use('javax.net.ssl.X509TrustManager')],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });
        
        var TrustManagers = [TrustManager.$new()];
        this.init(keyManager, TrustManagers, secureRandom);
    };
    
    // Hook HostnameVerifier
    var HostnameVerifier = Java.use('javax.net.ssl.HttpsURLConnection');
    HostnameVerifier.setDefaultHostnameVerifier.implementation = function(hostnameVerifier) {
        console.log("[+] HostnameVerifier hooked");
        
        var TrustAll = Java.registerClass({
            name: 'custom.HostnameVerifier',
            implements: [Java.use('javax.net.ssl.HostnameVerifier')],
            methods: {
                verify: function(hostname, session) {
                    return true;  // Trust all hostnames
                }
            }
        });
        
        return this.setDefaultHostnameVerifier(TrustAll.$new());
    };
    
    console.log("[+] SSL Pinning bypassed!");
});
```

**Run the bypass:**
```bash
# Method 1: Attach to running app
frida -U -f com.example.app -l ssl-bypass.js --no-pause

# Method 2: Spawn app with script
frida -U -n "App Name" -l ssl-bypass.js

# Method 3: Use objection (easier)
objection -g com.example.app explore
> android sslpinning disable
```

### 4. Bypass Root Detection

**Common root detection methods:**
- Check for su binary
- Check for Superuser/Magisk apps
- Test for file system write access
- Check build tags (test-keys)

**Bypass script:**
```javascript
// root-bypass.js
Java.perform(function() {
    console.log("[*] Bypassing root detection...");
    
    // Method 1: Hook common root detection libraries
    
    // RootBeer library (popular)
    try {
        var RootBeer = Java.use('com.scottyab.rootbeer.RootBeer');
        RootBeer.isRooted.implementation = function() {
            console.log("[+] RootBeer.isRooted() bypassed");
            return false;
        };
    } catch(err) {}
    
    // Method 2: Hook Runtime.exec() to hide su
    var Runtime = Java.use('java.lang.Runtime');
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        if (cmd.indexOf("su") != -1 || cmd.indexOf("which") != -1) {
            console.log("[!] Blocked command: " + cmd);
            throw "Command not found";
        }
        return this.exec(cmd);
    };
    
    // Method 3: Hook File.exists() for common root files
    var File = Java.use('java.io.File');
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        var rootPaths = [
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        ];
        
        if (rootPaths.indexOf(path) != -1) {
            console.log("[!] Hiding root file: " + path);
            return false;
        }
        return this.exists();
    };
    
    console.log("[+] Root detection bypassed!");
});
```

**Run:**
```bash
frida -U -f com.example.app -l root-bypass.js --no-pause
```

### 5. Intercept & Modify API Calls

**Hook OkHttp (popular Android HTTP library):**
```javascript
// okhttp-intercept.js
Java.perform(function() {
    console.log("[*] Hooking OkHttp...");
    
    // Hook OkHttpClient.newCall()
    var OkHttpClient = Java.use('okhttp3.OkHttpClient');
    OkHttpClient.newCall.implementation = function(request) {
        console.log("\n[+] HTTP Request:");
        console.log("    URL: " + request.url());
        console.log("    Method: " + request.method());
        
        var headers = request.headers();
        for (var i = 0; i < headers.size(); i++) {
            console.log("    Header: " + headers.name(i) + " = " + headers.value(i));
        }
        
        var body = request.body();
        if (body != null) {
            console.log("    Body: " + body.toString());
        }
        
        return this.newCall(request);
    };
    
    // Hook Response to see responses
    var Response = Java.use('okhttp3.Response');
    var ResponseBody = Java.use('okhttp3.ResponseBody');
    
    ResponseBody.string.implementation = function() {
        var responseString = this.string();
        console.log("\n[+] HTTP Response:");
        console.log(responseString);
        return responseString;
    };
    
    console.log("[+] OkHttp hooked!");
});
```

**Modify API responses:**
```javascript
// modify-response.js
Java.perform(function() {
    var ResponseBody = Java.use('okhttp3.ResponseBody');
    
    ResponseBody.string.implementation = function() {
        var response = this.string();
        
        // Modify JSON response
        if (response.indexOf('"premium":false') != -1) {
            console.log("[!] Modifying premium status");
            response = response.replace('"premium":false', '"premium":true');
        }
        
        return response;
    };
});
```

### 6. Extract Encryption Keys

**Find AES keys in memory:**
```javascript
// key-extraction.js
Java.perform(function() {
    var SecretKeySpec = Java.use('javax.crypto.spec.SecretKeySpec');
    
    SecretKeySpec.$init.overload('[B', 'java.lang.String').implementation = function(key, algorithm) {
        console.log("\n[+] AES Key Created:");
        console.log("    Algorithm: " + algorithm);
        console.log("    Key (hex): " + bytesToHex(key));
        console.log("    Key (base64): " + bytesToBase64(key));
        
        return this.$init(key, algorithm);
    };
    
    function bytesToHex(bytes) {
        var hex = "";
        for (var i = 0; i < bytes.length; i++) {
            hex += ("0" + (bytes[i] & 0xFF).toString(16)).slice(-2);
        }
        return hex;
    }
    
    function bytesToBase64(bytes) {
        var Base64 = Java.use('android.util.Base64');
        return Base64.encodeToString(bytes, 0);
    }
});
```

### 7. Bypass Authentication

**Skip login screen:**
```javascript
// bypass-login.js
Java.perform(function() {
    // Find the Login Activity
    var LoginActivity = Java.use('com.example.app.LoginActivity');
    
    // Hook the authentication check method
    LoginActivity.validateCredentials.implementation = function(username, password) {
        console.log("[+] Login bypass activated");
        console.log("    Username: " + username);
        console.log("    Password: " + password);
        
        // Always return true (authenticated)
        return true;
    };
    
    // Or jump directly to main activity
    var Intent = Java.use('android.content.Intent');
    var MainActivity = Java.use('com.example.app.MainActivity');
    
    LoginActivity.onCreate.implementation = function(savedInstanceState) {
        console.log("[+] Skipping login, jumping to MainActivity");
        
        var intent = Intent.$new(this, MainActivity.class);
        this.startActivity(intent);
        this.finish();
    };
});
```

### 8. Frida + Burp Suite for Complete MITM

```bash
# 1. Setup Burp to listen on all interfaces
# Proxy → Options → Proxy Listeners → Add → 0.0.0.0:8080

# 2. Forward device traffic through Burp
adb shell settings put global http_proxy <PC_IP>:8080

# 3. Install Burp CA cert on device
# Export from Burp: Proxy → Options → Import/Export CA Cert
# Push to device and install as user certificate

# 4. Run Frida SSL bypass
frida -U -f com.example.app -l ssl-bypass.js --no-pause

# 5. Intercept and modify in Burp
# Now you see HTTPS traffic in Burp even with SSL pinning
```

## Pitfalls & OPSEC

**Common Failures:**
- **Frida detection** — Apps detect Frida and refuse to run
  - Solution: Rename frida-server, use Magisk Hide, patch detection code
- **App crashes** — Wrong hook implementation crashes app
  - Solution: Use try/catch in hooks, test incrementally
- **Method not found** — Hooked method doesn't exist in this app version
  - Solution: Use `Java.enumerateMethods()` to discover actual methods
- **SELinux blocking** — Frida can't inject on enforcing mode
  - Solution: `setenforce 0` or use Magisk to disable SELinux

**Detection Risks:**
- Frida server creates network ports (27042, 27043)
- Frida libraries injected in app memory
- App can scan for frida-server process
- App can check for Frida-related strings in memory

**OPSEC Improvements:**
- **Rename frida-server** to innocent name (`/system/bin/debuggerd`)
- **Patch detection** — Use Frida to hook detection methods
- **Magisk Hide** — Hide root from target app
- **Use objection** — Higher-level tool, easier to use
- **Dual-boot** — Use second Android install without Frida for sensitive apps

## Advanced Techniques

### Objection (Frida-based toolkit)

```bash
# Install
pip3 install objection

# Explore app
objection -g com.example.app explore

# Inside objection REPL
> android hooking list classes  # List all classes
> android hooking search methods MainActivity  # Find methods
> android hooking watch class com.example.Class  # Watch all methods
> android sslpinning disable  # Quick SSL bypass
> android root disable  # Quick root bypass
> memory list modules  # List loaded libraries
> memory dump all /tmp/dump  # Dump entire memory
```

## Verification

```bash
# Confirm Frida working
frida-ps -U  # Should list processes

# Confirm hooks active
# Check console output for "[+] Hook activated" messages

# Confirm SSL bypass working
# Burp Suite should show HTTPS traffic

# Confirm root bypass working
# App launches without root detection error
```

## Related Skills
- `apk-modding-workflow` — Static modification of APKs
- `android-16-apk-modding` — APK modding for newer Android
- `flutter-app-detection` — Detect Flutter before wasting time
- `reverse-engineering-gokil` — Binary analysis with Ghidra/IDA

## References
- [Frida Documentation](https://frida.re/docs/home/)
- [Frida CodeShare](https://codeshare.frida.re/) — Pre-made scripts
- [Objection GitHub](https://github.com/sensepost/objection)
- [Android App Reverse Engineering 101](https://www.ragingrock.com/AndroidAppRE/)

---

**LEGAL WARNING:** Only test apps you own or have authorization to test. Bypassing security controls on apps you don't own may violate terms of service and laws like DMCA Section 1201.
