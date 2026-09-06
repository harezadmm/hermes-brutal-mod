---
name: mobile-hacking
description: Android/iOS pentesting, APK reversing, Frida hooking.
tags: [android, ios, apk, mobile, frida, apktool, objection]
---

# Mobile Hacking

Use when user requests mobile security testing: Android APK analysis, iOS app testing, Frida hooking, or mobile pentesting.

## Trigger Conditions
- Android APK decompilation/analysis
- iOS app security testing
- Mobile app reverse engineering
- Frida dynamic instrumentation
- SSL pinning bypass
- Root/jailbreak detection bypass
- Mobile malware analysis

## Android Pentesting

### APK Analysis Tools

#### APKTool (Decompile/Recompile)
```bash
# Install
apt install apktool

# Decompile APK
apktool d app.apk -o app_decompiled

# Recompile
apktool b app_decompiled -o app_modified.apk

# Sign APK
keytool -genkey -v -keystore my-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-key.keystore app_modified.apk alias_name

# Zipalign
zipalign -v 4 app_modified.apk app_final.apk
```

#### JADX (Decompile to Java)
```bash
# Install
apt install jadx

# Decompile
jadx app.apk -d output_dir

# GUI mode
jadx-gui app.apk

# Export Gradle project
jadx -e app.apk -d gradle_project
```

#### Dex2jar + JD-GUI
```bash
# Convert DEX to JAR
d2j-dex2jar app.apk

# Open JAR in JD-GUI
jd-gui app-dex2jar.jar
```

### Static Analysis

#### Extract APK Contents
```bash
# APK is just a ZIP file
unzip app.apk -d app_extracted

# Important files:
# AndroidManifest.xml - permissions, components
# classes.dex - compiled Java code
# lib/ - native libraries
# res/ - resources
# META-INF/ - signatures
```

#### AndroidManifest.xml Analysis
```bash
# View with apktool
apktool d app.apk

# Check permissions
grep -E 'uses-permission' AndroidManifest.xml

# Exported components (potential attack surface)
grep -E 'exported="true"' AndroidManifest.xml

# Debuggable flag
grep -E 'debuggable="true"' AndroidManifest.xml

# Backup allowed
grep -E 'allowBackup="true"' AndroidManifest.xml
```

#### Search for Secrets
```bash
# API keys, tokens, passwords
grep -r "api_key" app_decompiled/
grep -r "password" app_decompiled/
grep -r "secret" app_decompiled/
grep -r "token" app_decompiled/

# URLs
grep -r "http://" app_decompiled/
grep -r "https://" app_decompiled/

# Hardcoded credentials
grep -r "admin" app_decompiled/

# AWS keys
grep -r "AKIA" app_decompiled/
```

### Dynamic Analysis with Frida

#### Setup Frida
```bash
# Install Frida on host
pip install frida-tools

# Download frida-server for Android
wget https://github.com/frida/frida/releases/latest/download/frida-server-16.0.0-android-arm64.xz
unxz frida-server-16.0.0-android-arm64.xz

# Push to device
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# Verify
frida-ps -U
```

#### SSL Pinning Bypass
```javascript
// ssl_pinning_bypass.js
Java.perform(function() {
    // OkHttp3 SSL Pinning Bypass
    var CertificatePinner = Java.use('okhttp3.CertificatePinner');
    CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {
        console.log('[+] SSL Pinning bypassed!');
        return;
    };
    
    // TrustManager bypass
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    var TrustManager = Java.registerClass({
        name: 'com.sensepost.test.TrustManager',
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    
    var TrustManagers = [TrustManager.$new()];
    var SSLContext_init = SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom');
    SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
        SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
    
    console.log('[+] SSL Pinning bypass installed');
});

// Run script
frida -U -f com.example.app -l ssl_pinning_bypass.js --no-pause
```

#### Root Detection Bypass
```javascript
// root_bypass.js
Java.perform(function() {
    // Common root detection methods
    
    // 1. File existence check
    var File = Java.use('java.io.File');
    File.exists.implementation = function() {
        var name = this.getName();
        if (name == 'su' || name == 'magisk') {
            console.log('[+] Root file check bypassed: ' + name);
            return false;
        }
        return this.exists.call(this);
    };
    
    // 2. Build.TAGS check
    var Build = Java.use('android.os.Build');
    Build.TAGS.value = 'release-keys';
    
    // 3. RootBeer library
    var RootBeer = Java.use('com.scottyab.rootbeer.RootBeer');
    RootBeer.isRooted.implementation = function() {
        console.log('[+] RootBeer bypass');
        return false;
    };
    
    console.log('[+] Root detection bypass installed');
});

// Run
frida -U -f com.example.app -l root_bypass.js --no-pause
```

#### Function Hooking
```javascript
// hook_login.js
Java.perform(function() {
    var Activity = Java.use('com.example.app.LoginActivity');
    
    // Hook login method
    Activity.login.implementation = function(username, password) {
        console.log('[+] Login attempt:');
        console.log('    Username: ' + username);
        console.log('    Password: ' + password);
        
        // Call original method
        return this.login(username, password);
    };
    
    // Hook checkPremium
    Activity.checkPremium.implementation = function() {
        console.log('[+] Premium check bypassed!');
        return true;  // Always return premium
    };
});

// Run
frida -U -f com.example.app -l hook_login.js --no-pause
```

#### Objection (Frida GUI)
```bash
# Install
pip install objection

# Run
objection -g com.example.app explore

# Inside objection shell:
android hooking list classes
android hooking list class_methods com.example.app.MainActivity
android hooking watch class_method com.example.app.MainActivity.login --dump-args --dump-return

# SSL pinning bypass
android sslpinning disable

# Root detection bypass
android root disable

# Dump memory
memory dump all /tmp/dump
```

### ADB (Android Debug Bridge)

#### Basic ADB Commands
```bash
# List devices
adb devices

# Install APK
adb install app.apk

# Uninstall
adb uninstall com.example.app

# Pull file from device
adb pull /data/data/com.example.app/databases/app.db

# Push file to device
adb push file.txt /sdcard/

# Shell access
adb shell

# Logcat (logs)
adb logcat

# Filtered logcat
adb logcat | grep "password"

# Backup app data
adb backup -f backup.ab -apk com.example.app

# Restore
adb restore backup.ab
```

#### Rooted Device Commands
```bash
# Root shell
adb root
adb shell

# Remount /system as writable
adb remount

# Access app private data
adb shell
su
cd /data/data/com.example.app
ls -la

# View databases
sqlite3 /data/data/com.example.app/databases/app.db
.tables
SELECT * FROM users;
```

### Drozer (Android Security Framework)
```bash
# Install
pip install drozer

# Start server on device
adb forward tcp:31415 tcp:31415

# Connect
drozer console connect

# List packages
run app.package.list

# Get package info
run app.package.info -a com.example.app

# Find attack surface
run app.package.attacksurface com.example.app

# Exploit exported activity
run app.activity.start --component com.example.app/.SecretActivity

# Exploit content provider
run app.provider.query content://com.example.app.provider/users

# SQL injection in content provider
run scanner.provider.injection -a com.example.app
```

### Android Malware Analysis

#### Detect Malicious Behavior
```bash
# Check permissions
apktool d malware.apk
grep -E 'SEND_SMS|READ_SMS|CALL_PHONE|READ_CONTACTS|RECORD_AUDIO|CAMERA|LOCATION' AndroidManifest.xml

# Check if obfuscated
jadx malware.apk
# Look for: class a, class b, method a()

# Check native code
unzip malware.apk
file lib/armeabi-v7a/*

# Strings analysis
strings classes.dex | grep -i "http"
strings lib/armeabi-v7a/*.so

# C&C communication
tcpdump -i any -s 0 -w capture.pcap
# Install and run malware
# Analyze capture.pcap in Wireshark
```

## iOS Pentesting

### IPA Analysis

#### Extract IPA
```bash
# IPA is a ZIP file
unzip app.ipa -d app_extracted

# Important files:
# Payload/App.app/Info.plist - app metadata
# Payload/App.app/binary - Mach-O binary
# Payload/App.app/_CodeSignature - signatures
```

#### Static Analysis
```bash
# View Info.plist
plutil -convert xml1 Info.plist
cat Info.plist

# Binary analysis with otool
otool -L binary  # Linked libraries
otool -h binary  # Mach-O header
otool -l binary  # Load commands

# Check for PIE (Position Independent Executable)
otool -hv binary | grep PIE

# Check for stack canaries
otool -Iv binary | grep stack_chk

# Dump class information
class-dump binary > classes.txt

# Strings
strings binary | grep -i "api"
strings binary | grep -i "password"
```

### Jailbroken iOS Testing

#### SSH to Device
```bash
# Default credentials (change immediately!)
ssh root@iphone_ip
# Password: alpine

# Change root password
passwd
```

#### Frida on iOS
```bash
# Install Frida on iOS (via Cydia)
# Add repo: https://build.frida.re

# Connect from host
frida-ps -U

# SSL pinning bypass (iOS)
frida -U -f com.example.app -l ios-ssl-bypass.js --no-pause
```

#### SSL Pinning Bypass (iOS)
```javascript
// ios_ssl_bypass.js
if (ObjC.available) {
    // NSURLSession bypass
    var NSURLSession = ObjC.classes.NSURLSession;
    var URLSession_didReceiveChallenge = NSURLSession['- URLSession:didReceiveChallenge:completionHandler:'];
    
    Interceptor.attach(URLSession_didReceiveChallenge.implementation, {
        onEnter: function(args) {
            var completionHandler = new ObjC.Block(args[4]);
            var originalImpl = completionHandler.implementation;
            
            completionHandler.implementation = function(disposition, credential) {
                // NSURLSessionAuthChallengeDisposition: 0 = UseCredential
                originalImpl(0, ObjC.classes.NSURLCredential.credentialForTrust_(args[3]));
            };
        }
    });
    
    console.log('[+] iOS SSL Pinning bypassed');
}
```

#### Cycript (Runtime Manipulation)
```bash
# Install via Cydia

# Attach to process
cycript -p SpringBoard

# Get all classes
ObjectiveC.classes

# Hook method
var vc = [UIApplication sharedApplication].keyWindow.rootViewController;
vc.view.backgroundColor = [UIColor redColor];

# Call private method
[[UIApplication sharedApplication] suspend];
```

### iOS Binary Patching

#### Decrypt App Binary
```bash
# iOS binaries are encrypted
# Use Clutch or frida-ios-dump

# Clutch
Clutch -i  # List apps
Clutch -d com.example.app  # Decrypt

# frida-ios-dump
git clone https://github.com/AloneMonkey/frida-ios-dump
cd frida-ios-dump
python dump.py com.example.app
```

#### Patch with Hopper/IDA Pro
```
1. Open decrypted binary in Hopper Disassembler
2. Find jailbreak detection function
3. Replace with NOP instructions or always return 0
4. Export patched binary
5. Resign and reinstall
```

#### Resign IPA
```bash
# Extract IPA
unzip app.ipa

# Replace binary
cp patched_binary Payload/App.app/binary

# Sign with your certificate
codesign -f -s "iPhone Developer: Your Name" Payload/App.app

# Repackage
zip -r patched.ipa Payload/

# Install
ideviceinstaller -i patched.ipa
```

## Mobile Traffic Interception

### Burp Suite Setup
```bash
# 1. Configure Burp proxy (127.0.0.1:8080)

# 2. Android: Install Burp CA certificate
# Export cert from Burp
# Push to device
adb push cacert.der /sdcard/
# Install via Settings > Security > Install from storage

# 3. Android: Set proxy
adb shell settings put global http_proxy 192.168.1.100:8080

# 4. iOS: Install Burp CA certificate
# Go to http://burp in Safari
# Download and install certificate
# Trust in Settings > General > About > Certificate Trust Settings

# 5. Set proxy on iOS
# Settings > WiFi > Configure Proxy > Manual
# Server: 192.168.1.100, Port: 8080
```

### mitmproxy
```bash
# Install
pip install mitmproxy

# Run
mitmproxy -p 8080

# Web interface
mitmweb -p 8080

# SSL pinning bypass addon
mitmproxy --set addon_ssl_pinning_disable=true
```

## Pitfalls
- **Certificate pinning**: Harder to bypass on modern apps
- **Root/jailbreak detection**: Multi-layered checks
- **Obfuscation**: Makes static analysis difficult
- **Anti-debug**: Detects Frida, debuggers
- **Legal**: Reverse engineering apps may violate ToS

## Related Skills
- `apk-modding-workflow`: Detailed APK modification
- `frida-runtime-hooking`: Advanced Frida techniques
- `reverse-engineering-gokil`: Binary analysis
- `flutter-app-detection`: Detect Flutter before wasting time
