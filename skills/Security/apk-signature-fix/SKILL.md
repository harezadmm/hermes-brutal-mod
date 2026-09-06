---
name: apk-signature-fix
description: Fix split APK signature mismatches to enable installation.
version: 1.0.0
trigger: SAI error ada salah mengurangikan paket or signature mismatch
tags: [android, apk, signature, split-apk]
---

# APK Signature Fix

Fix "ada salah mengurangikan paket" error when installing modded split APKs.

## Problem

Split APKs must have **identical signatures**. If base.apk uses keystore A and splits use keystore B → installation fails.

## Quick Fix

### 1. Unsign Splits

```python
# Save as unsign_splits.py
import zipfile, sys, os
for apk in sys.argv[1:]:
    temp = apk + '.tmp'
    with zipfile.ZipFile(apk) as zin:
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if not item.filename.startswith('META-INF/'):
                    zout.writestr(item, zin.read(item.filename))
    os.replace(temp, apk)
```

```bash
python3 unsign_splits.py split_config.*.apk
```

### 2. Sign ALL Together

```bash
# ONE command = same keystore
java -jar uber-apk-signer.jar --apks base_modded.apk split_config.*.apk
```

### 3. Verify

```bash
for apk in *-debugSigned.apk; do
    unzip -p "$apk" META-INF/CERT.RSA | keytool -printcert | grep SHA256
done
# All should match
```

## Why This Happens

uber-apk-signer creates NEW keystore each run. Signing separately = different keystores = mismatch.

## Key Rules

- ✅ Unsign splits first
- ✅ Sign ALL in ONE command  
- ✅ Verify SHA256 matches
- ❌ Never sign separately
