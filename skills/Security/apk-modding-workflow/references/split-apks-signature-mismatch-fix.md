# Split APKs Signature Mismatch Fix

## Problem

When modding `.apks` bundles (split APK format used by bundletool/Play Store), you'll encounter:

```
INSTALL_FAILED_INVALID_APK: android.content.pm.parsing.ApkLite@... signatures are inconsistent
```

**Root cause:** You modified and signed `base.apk`, but the config splits (`split_config.arm64_v8a.apk`, etc.) still have the **original signature**. Android validates that ALL APKs in a bundle share the same signature.

## The Working Fix

### Step 1: Identify Split APKs Bundle

```bash
unzip -l app.apks
# Look for:
# base.apk
# split_config.arm64_v8a.apk
# split_config.xxhdpi.apk
# split_config.en.apk
# etc.
```

### Step 2: Extract Bundle

```bash
mkdir app_splits
cd app_splits
unzip ../app.apks
```

### Step 3: Decompile & Modify ONLY base.apk

```bash
java -jar apktool.jar d base.apk -o base_decoded -f
# Modify base_decoded/ (manifest, smali, resources)
java -jar apktool.jar b base_decoded/ -o base_modded.apk
```

**DO NOT modify config splits.** They contain:
- Native libraries (`.so` files)
- Density-specific resources (xxhdpi, xhdpi)
- Language packs (en, in, ms)

These rarely need modification.

### Step 4: Sign base.apk

```bash
java -jar uber-apk-signer.jar --apks base_modded.apk
# Output: base_modded-aligned-debugSigned.apk
```

### Step 5: Remove Old Signatures from Config Splits

Config splits come pre-signed with the **original developer signature**. You must strip these before re-signing with YOUR keystore.

**Python script to unsign:**

```python
import zipfile
import os

splits = [
    "split_config.arm64_v8a.apk",
    "split_config.xxhdpi.apk",
    "split_config.en.apk",
    "split_config.in.apk",
    "split_config.ms.apk"
]

for apk in splits:
    if not os.path.exists(apk):
        continue
    
    temp = apk + ".tmp"
    with zipfile.ZipFile(apk, 'r') as zin:
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                # Skip META-INF (signature files)
                if not item.filename.startswith('META-INF/'):
                    data = zin.read(item.filename)
                    zout.writestr(item, data)
    
    os.replace(temp, apk)
    print(f"✅ Unsigned: {apk}")
```

Run this in the `app_splits/` directory.

### Step 6: Sign ALL Config Splits with SAME Keystore

```bash
java -jar uber-apk-signer.jar --apks split_config.*.apk
```

**Critical:** This MUST use the **same keystore** (or debug keystore) as Step 4. uber-apk-signer uses its embedded debug keystore by default, which is perfect for consistency.

**Verify all have same signature:**

```bash
keytool -printcert -jarfile base_modded-aligned-debugSigned.apk | grep SHA256
keytool -printcert -jarfile split_config.arm64_v8a-aligned-debugSigned.apk | grep SHA256
# SHA256 must match across all APKs
```

### Step 7: Repack as .apks Bundle

**Python script:**

```python
import zipfile
import os

bundle_name = "app_MODDED.apks"

# Map signed files back to original names for bundle
files = {
    "base_modded-aligned-debugSigned.apk": "base.apk",
    "split_config.arm64_v8a-aligned-debugSigned.apk": "split_config.arm64_v8a.apk",
    "split_config.xxhdpi-aligned-debugSigned.apk": "split_config.xxhdpi.apk",
    "split_config.en-aligned-debugSigned.apk": "split_config.en.apk",
    "split_config.in-aligned-debugSigned.apk": "split_config.in.apk",
    "split_config.ms-aligned-debugSigned.apk": "split_config.ms.apk"
}

with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for signed_file, archive_name in files.items():
        if os.path.exists(signed_file):
            bundle.write(signed_file, archive_name)
            print(f"✅ Added {archive_name}")

print(f"\n✅ Bundle created: {bundle_name}")
```

### Step 8: Install via SAI

`.apks` files require **Split APKs Installer (SAI)**:

1. Install SAI from Play Store: https://play.google.com/store/apps/details?id=com.aefyr.sai
2. Open SAI → Install APKs
3. Select `app_MODDED.apks`
4. Install

## Why This Happens

Android validates split APKs as a **cohesive unit**:

```java
// Android's PackageParser.java (simplified)
Signature baseSignature = base.apk.getSignature();
for (split : splits) {
    if (!split.getSignature().equals(baseSignature)) {
        throw INSTALL_FAILED_INVALID_APK;
    }
}
```

If you sign `base.apk` with a debug keystore but leave config splits with the original Play Store signature, validation fails.

## Alternative: Sign with Original Keystore

If you have the **original developer keystore** (extremely rare), you can:

```bash
# Sign base with original key
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore original.keystore -storepass password \
  base_modded.apk myalias

# Config splits already have original signature, no need to re-sign
# Repack directly
```

This preserves the original signature, allowing updates over the original app. But you almost never have the original keystore for someone else's app.

## Common Mistakes

### ❌ Only Signing base.apk

```bash
# WRONG
java -jar uber-apk-signer.jar --apks base_modded.apk
# Then repack with UNSIGNED config splits
# Result: Signature mismatch
```

### ❌ Signing Config Splits Without Unsigning First

```bash
# WRONG
java -jar uber-apk-signer.jar --apks split_config.arm64_v8a.apk
# uber-apk-signer sees existing signature, skips with "already signed"
# Result: Old signature preserved, mismatch with base.apk
```

### ❌ Signing with Different Keystores

```bash
# WRONG
java -jar uber-apk-signer.jar --apks base_modded.apk --ks my.keystore
java -jar uber-apk-signer.jar --apks split_config.*.apk
# Second command uses default debug keystore (different from first)
# Result: Signature mismatch
```

**Always use the SAME keystore** (or let uber-apk-signer use its embedded debug keystore for everything).

## Quick Checklist

- [ ] Extract `.apks` bundle
- [ ] Decompile & modify ONLY `base.apk`
- [ ] Rebuild `base.apk`
- [ ] Sign `base.apk` with uber-apk-signer
- [ ] **Remove META-INF from ALL config splits** (Python script)
- [ ] Sign ALL config splits **with same keystore**
- [ ] Verify SHA256 signatures match across all APKs
- [ ] Repack as `.apks` bundle (Python script)
- [ ] Install via SAI (not `adb install`)

## Session Context

Discovered 2026-08-25 during Wibuku APK modding (Indonesian anime streaming app). Initial attempts failed with "signatures are inconsistent" until config splits were unsigned and re-signed with matching keystore.
