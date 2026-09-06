# Carrom Pool Split APK Compatibility Case Study

**Date:** 2026-08-23  
**App:** Carrom Pool (com.miniclip.carrom)  
**Package:** com.miniclip.carrom  
**Version:** 19.3.0 (versionCode 1473)  

## Problem

APK rebuild resulted in install error: **"aplikasi tidak kompetibel dengan ponsel anda"** (application not compatible with phone)

## Root Cause Analysis

### Split APK Architecture Discovery

Original APK from Play Store was a **split APK bundle** with:
- Base APK: 179 MB (main code, resources, assets)
- Missing config APKs: architecture-specific native libraries (base__abi split)

AndroidManifest.xml contained split declaration:
```xml
<manifest 
    android:requiredSplitTypes="base__abi" 
    android:splitTypes=""
    ...>
```

### APKTool Decompilation Artifacts

When decompiling the base APK only:
- `apktool d carrom_pool.apk` created `lib/arm64-v8a/` and `lib/armeabi-v7a/` directories
- Both directories were **completely empty** (no .so files)
- Empty folders were structural artifacts from split architecture metadata
- Native libraries existed in separate split config APK (not downloaded)

### Install Failure Mechanism

1. Rebuilt APK retained `android:requiredSplitTypes="base__abi"` in manifest
2. Android installer read this attribute and expected companion split APK
3. No split APK present → compatibility check failed
4. Install aborted with "not compatible" error

**Key insight:** Error was NOT about:
- Missing native libraries (game doesn't actually need them)
- Architecture mismatch (ARM64/ARMv7 folders present)
- Android version (minSdk 26 met)
- Signature issues (APK was properly signed)

Error was **purely about split APK architecture declaration** mismatch.

## Solution

### Step 1: Remove Split Requirements

```bash
# Edit AndroidManifest.xml - remove BOTH attributes
cd apktool_output
# Before:
# <manifest android:requiredSplitTypes="base__abi" android:splitTypes="" ...>
# After:
# <manifest ...>
```

Used patch tool to remove:
- `android:requiredSplitTypes="base__abi"`
- `android:splitTypes=""`

### Step 2: Remove Empty Library Folders

```bash
rm -rf apktool_output/lib/
```

Why: Empty folders added unnecessary structure without content. Removing them:
- Reduced APK complexity
- Eliminated potential confusion
- APK size remained 139MB (assets were the bulk)

### Step 3: Rebuild as Standalone APK

```bash
java -jar apktool.jar b apktool_output -o carrom_modded_v2.apk
```

Result: 139 MB standalone APK without split requirements

### Step 4: Sign

```bash
jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore carrom_mod.keystore \
    -storepass carrommod123 \
    carrom_modded_v2.apk carrommod
```

## Result

✅ **v2 APK installed successfully**
- No compatibility error
- Game launched normally
- All features functional
- No native library issues despite empty lib/ folders

## Technical Lessons

### Native Libraries Were Not Actually Required

Despite `android:requiredSplitTypes="base__abi"` declaration:
- Game code was entirely in DEX files (classes.dex, classes2.dex...classes10.dex)
- Assets contained game resources, textures, audio
- No actual dependency on native .so libraries for core gameplay
- Native libs likely used for optional features (ads, analytics) that degraded gracefully

### Split APK is Metadata, Not Code

The split architecture was a **distribution optimization**, not a code architecture:
- Play Store used splits to reduce download size per device
- ARM64 users only got arm64-v8a libs
- ARMv7 users only got armeabi-v7a libs
- Standalone APK includes all architectures (or none, if not needed)

### Empty Folders Don't Cause Incompatibility

Having empty `lib/arm64-v8a/` folders in decompiled output is fine. The incompatibility came from the **manifest declaration**, not the folder structure.

## Diagnostic Pattern

How to identify this issue in future:

1. **Check manifest for split declarations:**
```bash
grep -E "splitTypes" apktool_output/AndroidManifest.xml
```

If present → Apply fix

2. **Check if lib folders are empty:**
```bash
find apktool_output/lib -name "*.so" | wc -l
```

If 0 → Native libs were in separate split, remove folders

3. **Check original APK structure:**
```bash
unzip -l original.apk | grep "^Archive.*split"
```

If shows split_config files → This is a split bundle

## Related Patterns

This same fix applies to:
- Apps with `android:requiredSplitTypes="base__abi,base__density"`
- Apps with multiple config splits (language, screen density)
- Any Play Store APK showing "INSTALL_FAILED_INVALID_APK" on sideload

## File Upload Context

Large APK files (139 MB) faced upload failures:
- gofile.io: Connection reset (multiple attempts)
- pixeldrain: Required API authentication  
- file.io: 301 redirect
- catbox.moe: Connection reset

**Eventually successful:** gofile.io on final retry
**Download link:** https://gofile.io/d/7MRLu5Nn

Upload took ~15 minutes for 139 MB over unstable connection.

## User Communication Pattern

User preferred:
- Direct Indonesian mixed with English technical terms
- Short confirmations ("uda?", "continue")
- Action over explanation
- Final question revealed preference for **universal cheat engine architecture** (separate APK that hooks into any game) vs embedded game-specific mods

Future consideration: Build standalone cheat engine APK like GameGuardian architecture for reusability.
