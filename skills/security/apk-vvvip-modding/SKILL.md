---
name: apk-vvvip-modding
description: Mod APKs for Android 16 with anti-detect and SSL bypass.
tags: [android, apk, reverse-engineering, anti-detection, modding, frida]
---

# APK VVVIP Modding System

## Trigger
Use ketika modding APK untuk bypass detection, hardware spoof, SSL pinning bypass, atau signature scheme Android 16+ (v3.1).

## System Location
**Base:** `/f/apk_modding_system/` (3.3GB)
- `tools/` - APKTool 3.0.3, Uber APK Signer, keystore
- `modules/` - Hardware spoof, SSL bypass modules
- `scripts/` - Auto-injection Python scripts
- `output/` - Decompiled & modded APKs

## Tools Stack (Android 16 Compatible)
- **APKTool 3.0.3+** - Signature scheme v3.1 support
- **Uber APK Signer 1.3.0** - RSA 4096-bit custom keystore
- **JADX 1.5.0+** - Java decompilation
- **Frida 17.17.0** - Runtime hooking (SSL bypass)
- **Custom Keystore** - CN=Google LLC spoof (bypass Play Protect)

## Workflow Steps

### 1. Decompile APK
```bash
apktool d target.apk -o /f/apk_modding_system/output/decompiled -f
```

### 2. Inject Hardware Spoof Module
**Auto-inject:**
```bash
python3 /f/apk_modding_system/scripts/inject_spoof.py /f/apk_modding_system/output/decompiled
```

**Manual (jika perlu custom):**
- Copy `hardware_spoof.smali` ke `smali/com/vvvip/spoof/`
- Hook di `MainActivity.smali`:
```smali
invoke-static {}, Lcom/vvvip/spoof/HardwareSpoof;->getDeviceID()Ljava/lang/String;
move-result-object v0
```

### 3. SSL Pinning Bypass (Runtime)
**Frida script:**
```bash
frida -U -f com.target.app -l /f/reverse_engineering_toolkit/frida_scripts/ssl_bypass.js --no-pause
```

**Patch langsung di APK (persistent):**
Edit `res/xml/network_security_config.xml`:
```xml
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

### 4. Recompile APK
```bash
apktool b /f/apk_modding_system/output/decompiled -o /f/apk_modding_system/output/modded.apk
```

### 5. Sign dengan Signature Scheme v3.1
```bash
java -jar /f/apk_modding_system/tools/uber-apk-signer.jar \
  --apks /f/apk_modding_system/output/modded.apk \
  --ks /f/apk_modding_system/tools/custom.keystore \
  --ksAlias vvvip_key \
  --ksPass vvvip2026 \
  --ksKeyPass vvvip2026 \
  --allowResign
```

**Output:** `modded-aligned-signed.apk`

### 6. Install ke Device
```bash
adb install -r /f/apk_modding_system/output/modded-aligned-signed.apk
```

## Automation Script
**One-command modding:**
```bash
/f/apk_modding_system/auto_mod_apk.sh target.apk
```

Script auto execute steps 1-6, output final APK di `output/`.

## Hardware Spoof Components
**Module injected:**
- Fake Android ID: `8e4a2c91f7b3d5e6`
- Spoofed Device Model: `SM-G998B` (Samsung S21 Ultra)
- Random MAC Address: `02:00:00:00:00:00`
- IMEI randomization (jika root available)

## Anti-Detection Checklist
- ✅ Signature scheme v3.1 (Android 16+ compatible)
- ✅ Hardware fingerprint spoof
- ✅ SSL pinning bypass (runtime + persistent)
- ✅ Custom keystore (Google LLC CN spoof)
- ✅ Play Protect evasion layer
- ✅ Certificate trust injection

## Pitfalls
1. **APKTool < 3.0.3** - Tidak support signature scheme v3.1, APK crash di Android 16
2. **Lupa inject network_security_config** - SSL bypass tidak persistent, butuh Frida setiap run
3. **Keystore password exposed** - Jangan commit keystore ke git, taruh di F:\ only
4. **ADB unauthorized** - Run `adb kill-server && adb start-server`, allow USB debugging di device
5. **ColorOS SafetyDetect** - Disable "App Verification" di Settings > Security sebelum install

## Verification
**Check signature scheme:**
```bash
apksigner verify --verbose modded-aligned-signed.apk | grep "v3.1"
```

**Runtime test:**
```bash
adb logcat | grep -i "vvvip\|spoof\|ssl"
```

## Related Skills
- `android-apk-builder` - Build APK from scratch
- `reverse-engineering-gokil` - Deep analysis sebelum mod
- `frida-runtime-hooking` - Advanced runtime bypass techniques