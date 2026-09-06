# APK Modding Workflow - References Index

This directory contains session-specific case studies, troubleshooting guides, and condensed knowledge for APK reverse engineering.

## Critical Pre-Flight Check

**⚠️ READ FIRST:** `server-side-validation-detection.md`

Run this 10-minute assessment **before decompiling** to detect impossible cracks:
- Food delivery / cinema / e-commerce apps (95%+ server-validated)
- Flutter apps with ordering features
- Heavy native protection

**Time-saver:** Abort early on server-validated apps instead of wasting 2+ hours on impossible cracks.

## Split APKs & Signatures

- `split-apks-signature-consistency.md` - Signing all splits with same keystore (Wibuku case study)
- `split-apk-compatibility-fix.md` - Handling split vs single APK issues
- `signing-troubleshooting.md` - Common signature errors

## Flutter Apps

- `flutter-apk-rebuild-failures.md` - Flutter app limitations
- `flutter-xposed-module-build.md` - Runtime hooks for Flutter

## Native Library & JNI

- `native-library-bypass-patterns.md` - Bypassing native protection
- `native-library-auto-injection.md` - Injecting custom native libs
- `jni-and-login-bypass-pitfalls.md` - JNI security bypass techniques

## Mod Injection

- `mod-menu-injection.md` - Injecting cheat menus
- `dex-string-scanning-for-mod-targets.md` - Finding patch targets
- `device-fingerprint-spoofing.md` - Anti-ban device spoofing

## Case Studies

- `wibuku-premium-ads-gems-analysis.md` - Premium unlock + ad removal
- `carrom-pool-split-apk-case-study.md` - Split APK modding example

## Troubleshooting

- `large-apk-decompilation.md` - Handling 100+ MB APKs
- `rushed-cracking-pitfalls.md` - Common mistakes under time pressure
- `apks-bundle-detection.md` - Identifying .apks vs .apk format

## Quick Reference

**Before starting any crack:**
1. Check `server-side-validation-detection.md` - saves hours
2. Identify Flutter: `unzip -l app.apk | grep libflutter.so`
3. Check split APKs: `file app.apks` (if ZIP archive)
4. Assess category: food/tickets/banking = likely impossible

**Core workflow:**
```bash
java -jar apktool.jar d app.apk -o decoded/ -f
# [modify decoded/smali/ or AndroidManifest.xml]
java -jar apktool.jar b decoded/ -o modded.apk
java -jar uber-apk-signer.jar --apks modded.apk
```

See main `SKILL.md` for complete workflow.
