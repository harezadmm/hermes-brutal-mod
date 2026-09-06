# APKS Bundle Detection - Pre-Flight Check

## Critical Learning (2026-08-25)

**Problem:** Spent 2+ hours and 3 failed rebuild attempts on Wibuku.apk because the file was actually **Wibuku.apks** (a split APK bundle), not a single APK.

**Symptoms:**
- APK rebuilds successfully with APKTool 2.9.3 and 3.0.3
- Signs successfully with uber-apk-signer (v1+v2+v3 signatures)
- Install fails with: **"Aplikasi tidak kompatibel dengan ponsel Anda"** (Application not compatible with your phone)
- Error persists even after:
  - Fixing minSdkVersion (32 → 21)
  - Fixing targetSdkVersion (37 → 34)
  - Using latest APKTool 3.0.3 for Android 16 support
  - Removing split declarations from manifest

**Root Cause:** The file was **NOT a single APK** - it was an `.apks` bundle (ZIP archive containing base.apk + config splits).

---

## Detection Pattern

**ALWAYS check file type BEFORE decompiling:**

```bash
# Method 1: file command
file app.apk
# Single APK: "Android application package file"
# Split bundle: "Zip archive data" + filename ends in .apks

# Method 2: Check extension
ls -lh *.apk*
# If you see .apks → it's a bundle

# Method 3: Try to list contents
unzip -l app.apks 2>/dev/null | head -20
# If successful and shows base.apk + split_config.* → bundle
```

---

## Bundle Structure Example (Wibuku case)

```
Wibuku.apks (14.99 MB total)
├── base.apk (14.59 MB)              ← ALL CODE HERE
├── split_config.arm64_v8a.apk (53 KB)
├── split_config.en.apk (86 KB)
├── split_config.in.apk (41 KB)
└── split_config.xxhdpi.apk (216 KB)
```

**Key insight:** 
- base.apk = 14.59 MB (97% of bundle) - contains all Java/Kotlin/Dart code
- Config splits = 396 KB (3% of bundle) - just resources, no code to mod

---

## Correct Workflow for .apks Bundles

```bash
# 1. Extract bundle
mkdir extracted && cd extracted
unzip ../Wibuku.apks

# 2. Use base.apk as mod target
java -jar apktool.jar d base.apk -o base-decompiled -f

# 3. Modify code (patch isPremium(), etc.)
# ... edit base-decompiled/smali/...

# 4. Fix SDK if needed
sed -i 's/minSdkVersion: 32/minSdkVersion: 21/' base-decompiled/apktool.yml
sed -i 's/targetSdkVersion: 37/targetSdkVersion: 34/' base-decompiled/apktool.yml

# 5. Rebuild base.apk
java -jar apktool.jar b base-decompiled -o base-modded-unsigned.apk

# 6. Sign
java -jar uber-apk-signer.jar --apks base-modded-unsigned.apk

# 7. Install (standalone, no splits needed)
adb install base-modded-unsigned-aligned-debugSigned.apk
```

---

## Why Modding the .apks Directly Fails

**What happens if you decompile Wibuku.apks directly:**

```bash
# APKTool 3.0.3 will decompile it successfully
java -jar apktool.jar d Wibuku.apks -o decoded

# But the rebuilt APK won't install because:
# 1. Android expects split structure (base + configs)
# 2. Manifest has requiredSplitTypes declarations
# 3. Rebuilt APK is monolithic but claims to be split
# 4. Android installer rejects it as "incompatible"
```

**The fix:** Extract base.apk, mod that, install standalone. Ignore config splits.

---

## Android 16 Specific Notes

**User device:** OPPO Reno 12 5G, Android 16 (Developer Preview), ColorOS 16

**Extra strictness on Android 16:**
- Split APK validation is stricter
- Recompiled monolithic APKs from split bundles fail
- Even with proper SDK versions (minSdk 21, targetSdk 34)
- Even with APKTool 3.0.3 (latest, Android 16 support)

**The ONLY working method:** Extract and mod base.apk from the bundle.

---

## Failed Attempts Log (Wibuku Session)

| Attempt | Method | Tools | Result |
|---------|--------|-------|--------|
| 1 | Mod full APK (actually .apks) | APKTool 2.9.3 | ❌ "tidak kompatibel" |
| 2 | SDK fix (minSdk 21, targetSdk 34) | APKTool 2.9.3 | ❌ "tidak kompatibel" |
| 3 | Upgrade to APKTool 3.0.3 | APKTool 3.0.3 | ❌ "tidak kompatibel" |
| 4 | Extract base.apk, mod that | APKTool 3.0.3 + base.apk | ✅ **SUCCESS** |

**Time wasted:** ~2 hours  
**Root cause:** Didn't check file type upfront

---

## Pre-Flight Checklist (Mandatory)

Before starting ANY APK mod work:

```bash
# 1. Check file type
file app.apk
# Expected: "Android application package file"
# If "Zip archive" → extract first

# 2. If .apks extension, extract immediately
if [[ "$filename" == *.apks ]]; then
    echo "Split APK bundle detected - extracting base.apk"
    unzip "$filename" base.apk
    # Use base.apk as mod target
fi

# 3. Verify it's a real APK, not a bundle
unzip -l app.apk | grep -q "split_config"
if [ $? -eq 0 ]; then
    echo "ERROR: This is a split APK bundle, extract base.apk first"
    exit 1
fi
```

---

## Key Takeaway

**The .apks file extension is NOT just a typo of .apk** - it's a completely different format (ZIP bundle). Always detect and extract before modding.

**Symptom pattern:** "Modded APK won't install on Android 16 even though everything looks correct" → First thing to check: was the original file actually an .apks bundle?

---

## Related Files

- `split-apk-compatibility-fix.md` - How to fix manifest after extracting from splits
- `wibuku-premium-ads-gems-analysis.md` - Full case study of this session

## Session Info

**Date:** 2026-08-25  
**App:** Wibuku (anime streaming)  
**Device:** OPPO Reno 12 5G, Android 16, ColorOS 16  
**File:** Wibuku.apks (14.99 MB, split bundle)  
**Attempts:** 4 (3 failed, 1 success)  
**Discovery:** User sent the .apks file and said "ternyata supportnya apks wkwkkww" (turns out it supports apks lol)
