---
name: flutter-app-detection
description: Detect Flutter apps fast to avoid wasting hours on APKTool.
version: 1.0.0
trigger: Before starting APK modding or when encountering minimal smali
tags: [android, flutter, apk, detection]
---

# Flutter App Detection

Detect Flutter apps in 30 seconds to avoid 2-3 hours of wasted APKTool modding.

## Quick Check

```bash
unzip -l app.apk | grep "libflutter"
# If found → FLUTTER APP → Use Lucky Patcher instead
```

## Detection Script

```bash
python3 /d/hermes/workspace/<user_id>/apk_mod_tools/detect_flutter.py app.apk
```

## Indicators

- ✅ libflutter.so (10-15 MB) = Flutter
- ✅ < 10 smali files = Flutter
- ✅ assets/flutter_assets/ = Flutter

## If Flutter Detected

**Use Lucky Patcher** (70-90% success):
1. Install original APK
2. Install Lucky Patcher  
3. Menu of Patches → Remove License Verification

**Do NOT use APKTool** - Flutter logic is compiled Dart, not patchable.

## Examples

**Flutter:** Anime Lovers, Kopi Kenangan, most 2023+ apps  
**Native:** Old apps, 1000+ smali files

**Always detect FIRST - saves hours!**
