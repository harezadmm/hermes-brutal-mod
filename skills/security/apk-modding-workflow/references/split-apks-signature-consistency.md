# Split APKs (.apks) Signature Consistency

**Session:** 2026-08-25  
**Context:** Wibuku APK mod for Android 16 / OPPO Reno 12 5G  
**Error:** `INSTALL_FAILED_INVALID_APK: signatures are inconsistent`

## Problem

When modding **split APK bundles** (.apks format), signing only the base.apk while leaving config splits with original signatures causes installation failure on Android 7+.

### Split APKs Structure

```
Wibuku.apks (ZIP archive)
├── base.apk (14 MB)           # Main app code & resources
├── split_config.arm64_v8a.apk (53 KB)   # ARM64 native libs
├── split_config.en.apk (86 KB)          # English resources
├── split_config.in.apk (41 KB)          # Indonesian resources
└── split_config.xxhdpi.apk (216 KB)     # xxhdpi density resources
```

### What Went Wrong

**Attempt 1-4:** Converted .apks → single APK (wrong format, lost splits)  
**Attempt 5:** Modded base.apk, signed it, repacked with **unsigned** config splits → signature mismatch  
**Attempt 6:** ✅ Unsigned all splits, re-signed ALL with same keystore → success

## Root Cause

Android's PackageManager validates that **all APKs in a split bundle share the same signing certificate**. Mixing signatures fails with:

```
INSTALL_FAILED_INVALID_APK: android.content.pm.parsing.ApkLite@fbb0d1f signatures are inconsistent
```

## Solution: Sign All Splits with Same Keystore

### Step 1: Extract .apks Bundle

```bash
unzip Original.apks -d extracted/
cd extracted/
ls -la
# base.apk
# split_config.arm64_v8a.apk
# split_config.en.apk
# split_config.in.apk
# split_config.xxhdpi.apk
```

### Step 2: Decompile & Modify Base APK Only

```bash
java -jar apktool.jar d base.apk -o base_decoded -f

# Modify smali code (e.g., patch isPremium)
# Edit base_decoded/smali/.../AppUser.smali

java -jar apktool.jar b base_decoded/ -o base_modded.apk
```

### Step 3: Remove Old Signatures from Config Splits

Config splits come pre-signed. Remove old signatures before re-signing:

```python
import zipfile
import os

splits = [
    "split_config.arm64_v8a.apk",
    "split_config.en.apk",
    "split_config.in.apk",
    "split_config.xxhdpi.apk"
]

for split in splits:
    unsigned = split.replace('.apk', '_unsigned.apk')
    
    with zipfile.ZipFile(split, 'r') as zin:
        with zipfile.ZipFile(unsigned, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                # Exclude META-INF (old signatures)
                if not item.filename.startswith('META-INF/'):
                    zout.writestr(item, zin.read(item.filename))
    
    os.replace(unsigned, split)
```

### Step 4: Sign ALL APKs with Same Keystore

```bash
# Sign base (modded)
java -jar uber-apk-signer.jar --apks base_modded.apk
# Output: base_modded-aligned-debugSigned.apk

# Sign all config splits with SAME keystore
java -jar uber-apk-signer.jar --apks \
  split_config.arm64_v8a.apk \
  split_config.en.apk \
  split_config.in.apk \
  split_config.xxhdpi.apk

# Outputs:
# split_config.arm64_v8a-aligned-debugSigned.apk
# split_config.en-aligned-debugSigned.apk
# split_config.in-aligned-debugSigned.apk
# split_config.xxhdpi-aligned-debugSigned.apk
```

**Critical:** uber-apk-signer uses the same embedded debug keystore for all APKs, ensuring consistent signatures.

### Step 5: Repack as .apks Bundle

```python
import zipfile

file_mapping = {
    "base_modded-aligned-debugSigned.apk": "base.apk",
    "split_config.arm64_v8a-aligned-debugSigned.apk": "split_config.arm64_v8a.apk",
    "split_config.en-aligned-debugSigned.apk": "split_config.en.apk",
    "split_config.in-aligned-debugSigned.apk": "split_config.in.apk",
    "split_config.xxhdpi-aligned-debugSigned.apk": "split_config.xxhdpi.apk"
}

with zipfile.ZipFile("App_MODDED.apks", 'w', zipfile.ZIP_DEFLATED) as apks:
    for signed_file, bundle_name in file_mapping.items():
        apks.write(signed_file, bundle_name)
```

### Step 6: Install via SAI (Split APKs Installer)

```
1. Install SAI from Play Store
2. Open SAI → Install APKs
3. Select App_MODDED.apks
4. Install
```

## Verification

Check all APKs share the same certificate:

```bash
# Extract certificate fingerprint from each APK
for apk in base.apk split_*.apk; do
  unzip -p $apk META-INF/*.RSA | \
    keytool -printcert | \
    grep SHA256
done

# All should show:
# SHA256: 1e08a903aef9c3a721510b64ec764d01d3d094eb954161b62544ea8f187b5953
```

## Common Mistakes

❌ **Signing only base.apk** → leaves config splits with original signature → mismatch  
❌ **Using different keystores per APK** → each APK gets different certificate → mismatch  
❌ **Forgetting to unsign config splits first** → uber-apk-signer skips already-signed APKs  

✅ **Correct:** Unsign all → sign all with same tool/keystore → repack

## SDK Preservation Note

When modding for Android 16 / bleeding-edge versions:

**DO NOT lower SDK if preserving split APKs format:**
```yaml
# Keep original SDK for split APKs compatibility
sdkInfo:
  minSdkVersion: 32  # Original (Android 12+)
  targetSdkVersion: 37  # Original (may be invalid but preserves intent)
```

**Only lower SDK if converting to single APK** (not recommended for Android 16).

## When to Use This Workflow

✅ Original app distributed as `.apks` (Play Store split delivery)  
✅ Target device is Android 16 / bleeding-edge OS  
✅ User explicitly wants split APKs format preserved  

❌ Original app is single `.apk` → use standard apk-modding-workflow  
❌ Converting to single APK for compatibility → merge splits with bundletool first

## Related Files

- `references/split-apk-compatibility-fix.md` — Handling split vs single APK issues
- Main skill `apk-modding-workflow` — Standard single APK workflow

## Key Takeaway

**All APKs in a split bundle MUST be signed with the same certificate.** When modding split APKs:
1. Modify only base.apk
2. Unsign all config splits
3. Re-sign ALL (base + configs) with same keystore
4. Repack as .apks

Signature consistency is non-negotiable on Android 7+.
