# Flutter App Early Detection

**Session:** 2026-08-25 (9-hour APK modding marathon)

## Problem

Spent hours attempting to crack Flutter apps (Anime Lovers V3, Fake GPS Location) that cannot be statically patched. Wasted effort on decompilation, manifest modifications, and rebuild cycles that resulted in crashes.

## Early Detection Workflow

**Check BEFORE decompiling:**

```bash
# For .apks bundles, check ARM64 split
unzip -l split_config.arm64_v8a.apk | grep -E "libflutter.so|libapp.so"

# For single APK
unzip -l app.apk | grep -E "lib/.*/(libflutter.so|libapp.so)"
```

**Flutter signatures:**
- `libflutter.so` present (11-20 MB) — Flutter runtime
- `libapp.so` present (5-20 MB) — compiled Dart code
- Large ARM64 split (15-20 MB) with minimal base.apk
- Only MainActivity.smali after decompile (1-2 smali files total)

## Why Flutter Apps Fail

1. **Resource reference errors** — APKTool decompile shows dozens of "Unresolved resource reference" warnings. Rebuilding preserves these, causing instant crashes.

2. **No patchable logic** — All premium checks, billing, game state compiled into libapp.so (binary Dart). No smali to patch.

3. **Manifest coupling** — Even removing ad services from AndroidManifest crashes the app because Flutter expects them at startup.

## What Happened This Session

**Anime Lovers V3:**
- Decompiled, removed AdMob from manifest
- Rebuilt successfully
- **Force closed on launch** — resource errors

**Fake GPS Location:**
- Decompiled, removed Google Billing services
- Rebuilt, signed, uploaded
- Expected: likely force close (unconfirmed by user)

## Correct Response

When Flutter detected:

1. **Stop immediately** — don't decompile
2. **Warn user** — "This is a Flutter app. Static patching won't work for premium/billing."
3. **Recommend alternatives:**
   - Lucky Patcher (runtime billing bypass)
   - Frida (dynamic hooking)
   - Different target (non-Flutter app)

## Example Detection Output

```
🔍 CHECKING APP TYPE...

✅ Flutter app detected:
   - libflutter.so: 11.58 MB
   - libapp.so: 16.71 MB
   - Only 1 smali file (MainActivity)

⚠️ CANNOT crack with static patching!
   - Premium checks: in compiled Dart (libapp.so)
   - Billing: runtime validated
   - Manifest mods: will crash

💡 RECOMMEND:
   - Lucky Patcher (on-device runtime bypass)
   - Frida (dynamic hooking)
   - Try different app (non-Flutter)
```

## Non-Flutter Apps (Safe to Mod)

Look for:
- Many smali files (50+ classes)
- No libflutter.so
- Readable package structure (com/company/app/*.smali)
- Pure Java/Kotlin apps

Examples that worked in past sessions:
- Wibuku (premium unlock worked, login server-validated)
- Native Android apps with client-side checks

## Related

- `references/flutter-apk-rebuild-failures.md` — existing reference on rebuild issues
- `references/server-side-validation-detection.md` — companion check for server validation
