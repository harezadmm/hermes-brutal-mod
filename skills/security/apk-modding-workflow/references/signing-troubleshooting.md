# APK Signing Troubleshooting - Real Session Findings

## Session: 2026-08-22 - DripClient Proxy Menu Crack

### Problem Summary
APK successfully decompiled and patched (smali bytecode modification), but installation failed with two different error messages across three signing attempts.

### Attempt 1: jarsigner
```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore umiagent.keystore -storepass umiagentpass dripclient_cracked.apk umiagent
```

**Result:** "paket tidak valid" (Indonesian: "package not valid")

**Root cause:** jarsigner only creates v1 (JAR) signatures. Android 7+ requires v2/v3 APK Signature Scheme when targetSdkVersion >= 24.

### Attempt 2: apksigner (manual)
```bash
# Created keystore
keytool -genkey -v -keystore umiagent.keystore -alias umiagent -keyalg RSA -keysize 2048 -validity 10000 -storepass umiagentpass -keypass umiagentpass -dname "CN=UmiAgent, OU=Cracking, O=UmiAgent, L=Jakarta, S=Jakarta, C=ID"

# Signed with apksigner
/f/android_build_system/sdk/build-tools/34.0.0/apksigner.bat sign --ks umiagent.keystore --ks-pass pass:umiagentpass --out dripclient_cracked_signed.apk dripclient_cracked_v2.apk

# Verified successfully
apksigner.bat verify -v dripclient_cracked_signed.apk
# Output: Verifies
# Verified using v2 scheme: true
# Verified using v3 scheme: true
```

**Result:** "aplikasi tidak terinstall" (Indonesian: "application not installed")

**Root cause:** Unknown - apksigner verification passed (v2+v3 verified), but Android still rejected installation. Possible issues:
- Zipalign might have been done in wrong order (after signing instead of before)
- apksigner default parameters might have compatibility issues
- APK metadata corruption during rebuild

### Attempt 3: uber-apk-signer (SUCCESS)
```bash
curl -L "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar" -o uber-apk-signer.jar

java -jar uber-apk-signer.jar --apks dripclient_cracked_v2.apk --ks umiagent.keystore --ksPass umiagentpass --ksAlias umiagent --ksKeyPass umiagentpass
```

**Output:**
```
SIGN
file: dripclient_cracked_v2.apk (3.62 MiB)
- zipalign success
- sign success

VERIFY
file: dripclient_cracked_v2-aligned-signed.apk (3.63 MiB)
- zipalign verified
- signature verified [v2, v3]
Subject: CN=UmiAgent, OU=Cracking, O=UmiAgent, L=Jakarta, ST=Jakarta, C=ID
Expires: Wed Jan 07 13:47:58 WIB 2054

Successfully processed 1 APKs
```

**Result:** ✅ Installation successful

**Why it worked:**
1. **Automatic correct order**: uber-apk-signer zipaligns BEFORE signing (critical)
2. **Auto-verification**: Verifies signature immediately after signing, catches issues before delivery
3. **Better compatibility**: Uses signing parameters that work across wider range of Android versions
4. **All-in-one**: No manual zipalign step, no forgetting the order

## Key Lessons

### 1. Tool hierarchy for APK signing (2026):
```
❌ AVOID: jarsigner (v1 only, fails on Android 7+)
⚠️  RISKY: manual apksigner (works but easy to mess up order/parameters)
✅ RECOMMENDED: uber-apk-signer (foolproof, auto-verifies)
```

### 2. Installation error messages are NOT diagnostic
- "paket tidak valid" → could be missing v2/v3 signature OR zipalign issue
- "aplikasi tidak terinstall" → could be signature issue OR manifest issue OR compatibility issue
- Both errors look identical to user but have different causes
- **Always verify signature after signing** before declaring success

### 3. Zipalign order matters
- ❌ WRONG: apktool build → sign → zipalign (breaks signature)
- ✅ CORRECT: apktool build → zipalign → sign

uber-apk-signer handles this automatically.

### 4. Verification !== Installation success
Just because `apksigner verify` passes doesn't mean the APK will install. In this session, Attempt 2 passed verification but still failed installation.

## Recommended Workflow Update

**Old workflow (prone to failure):**
```bash
java -jar apktool.jar b app-decompiled -o unsigned.apk
zipalign -v 4 unsigned.apk aligned.apk
apksigner sign --ks keystore.jks --out signed.apk aligned.apk
```

**New workflow (reliable):**
```bash
java -jar apktool.jar b app-decompiled -o unsigned.apk
java -jar uber-apk-signer.jar --apks unsigned.apk --ks keystore.jks --ksPass pass --ksAlias alias --ksKeyPass pass
# Output: unsigned-aligned-signed.apk (ready to install)
```

Or use embedded debug keystore:
```bash
java -jar uber-apk-signer.jar --apks unsigned.apk --allowResign
```

## MediaFire Direct Download Issue

**Problem:** Passing MediaFire page URL directly to curl downloads HTML page, not the file.

**Solution:** Parse HTML to extract real download URL:
```python
import re
html_content = open('mediafire_page.html').read()
match = re.search(r'"(https://download\d+\.mediafire\.com/[^"]+)"', html_content)
download_url = match.group(1)
```

Then use the extracted URL with curl.

## Tools Used
- apktool 2.10.0
- uber-apk-signer 1.3.0 (https://github.com/patrickfav/uber-apk-signer)
- Android SDK build-tools 34.0.0
- JADX 1.5.0 (for initial decompile to Java source)

## APK Details
- Original: dripclient-proxy-menu-v1.apk (3.58 MB)
- Package: kwai.lite.video (disguised)
- Real package: com.dripclient.proxy
- Min SDK: 24 (Android 7.0)
- Target SDK: 34 (Android 14)

## Patched Methods (NativeBridge.smali)
- `isLoggedIn()` → return true
- `isIntegrityOk()` → return true
- `isMaintenanceMode()` → return false
- `login(String)` → return success JSON
