# Split APK Compatibility Fix

## Problem

APK installs fail with error: **"Aplikasi tidak kompatibel dengan ponsel Anda"** / **"Application not compatible with your phone"**

Even though:
- APK is properly decompiled with apktool
- APK is signed correctly with uber-apk-signer or jarsigner
- APK signature verifies successfully
- APK size is reasonable
- Target device meets Android version requirements

## Root Cause

**Split APK architecture mismatch.** The original APK was distributed by Play Store as a **split APK bundle**:
- Base APK (main app code)
- Config APKs (architecture-specific: arm64-v8a, armeabi-v7a, x86)
- Config APKs (density-specific: xhdpi, xxhdpi, xxxhdpi)

The AndroidManifest.xml declares this split architecture:
```xml
<manifest
    android:requiredSplitTypes="base__abi,base__density"
    android:splitTypes=""
    ...>
```

When you decompile and repack **only the base APK**, the manifest still contains `android:requiredSplitTypes`, which tells Android installer: *"This app requires additional config APKs to function."*

Since those config APKs are missing, install fails with compatibility error.

## Solution

**Remove split declarations from AndroidManifest.xml before rebuild:**

```bash
cd app-decompiled

# Remove split requirements
sed -i 's/android:requiredSplitTypes="[^"]*"//g' AndroidManifest.xml
sed -i 's/android:splitTypes="[^"]*"//g' AndroidManifest.xml

# Verify removal
grep -E "splitTypes" AndroidManifest.xml
# Should return nothing

# Rebuild
cd ..
java -jar apktool.jar b app-decompiled -o app-unsigned.apk

# Sign
java -jar uber-apk-signer.jar --apks app-unsigned.apk --allowResign

# Install should now work
adb install app-aligned-debugSigned.apk
```

## How to Identify Split APK Issues

**Before decompiling, check if source APK is split:**

```bash
unzip -l original.apk | grep "split_config"
# If you see split_config.arm64_v8a.apk, split_config.xxhdpi.apk etc
# → It's a split APK bundle, not a standalone APK
```

**After decompiling, check manifest:**

```bash
grep "splitTypes" app-decompiled/AndroidManifest.xml
```

If present → Apply the fix above.

## Alternative: Download Standalone APK

If possible, obtain a **standalone (universal) APK** instead of split APK:
- APKMirror often has both split and standalone versions
- APKPure usually distributes standalone APKs
- Use `bundletool` to build universal APK from AAB:

```bash
# If you have the .aab bundle file
java -jar bundletool.jar build-apks \
  --bundle=app.aab \
  --output=app.apks \
  --mode=universal

unzip app.apks
# Extract universal.apk
```

## Technical Details

### Split APK Types

| Split Type | Contains | Example Filename |
|:-----------|:---------|:-----------------|
| **base** | Main app code, resources | base.apk |
| **config.arm64_v8a** | Native libs for ARM64 | split_config.arm64_v8a.apk |
| **config.armeabi_v7a** | Native libs for ARMv7 | split_config.armeabi_v7a.apk |
| **config.x86_64** | Native libs for x86-64 | split_config.x86_64.apk |
| **config.xxhdpi** | Density-specific resources | split_config.xxhdpi.apk |
| **config.en** | Language pack (English) | split_config.en.apk |

### Why Play Store Uses Split APKs

**Smaller downloads:** User only downloads the config APK matching their device:
- ARM64 user: base + arm64_v8a + xxhdpi (saves ~10-30MB vs universal)
- x86 emulator: base + x86 + mdpi

**Our modded APK:** Standalone with all architectures/densities embedded → larger file size but universal compatibility.

## Verification

After applying fix and rebuilding:

```bash
# Check manifest in final APK
unzip -p app-aligned-debugSigned.apk AndroidManifest.xml | grep -a "splitTypes"
# Should return nothing (binary XML, but string should not appear)

# Or decompile final APK and verify
java -jar apktool.jar d app-aligned-debugSigned.apk -o verify
grep "splitTypes" verify/AndroidManifest.xml
# Should be clean
```

## Related Errors

This fix also resolves:
- "Aplikasi tidak terpasang" (App not installed - Indonesian)
- "Package parsing failed"
- "Installation failed with message INSTALL_PARSE_FAILED_MANIFEST_MALFORMED"

## When This Fix is NOT Needed

- Standalone APK from APKPure → Already universal, no split declarations
- APK extracted from device with `adb pull` → Merged APK, no splits
- Custom-built APK from source → No split architecture unless explicitly configured

## References

- Android Split APK documentation: https://developer.android.com/guide/app-bundle
- APKTool split APK handling: https://github.com/iBotPeaches/Apktool/issues/1626
- Bundletool: https://developer.android.com/tools/bundletool

## Session Discovery

**Date:** 2026-08-22  
**App:** Kopi Kenangan (com.kopikenangan)  
**Original Size:** 31 MB (split)  
**Modded Size:** 26 MB (standalone)  
**Error:** "Aplikasi tidak kompatibel dengan ponsel Anda"  
**Fix Applied:** Removed `android:requiredSplitTypes="base__abi,base__density"` and `android:splitTypes=""` from manifest  
**Result:** ✅ Install successful after rebuild
