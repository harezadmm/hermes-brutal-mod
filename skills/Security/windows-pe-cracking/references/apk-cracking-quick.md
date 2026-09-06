# APK Cracking Quick Reference

When user provides an APK instead of Windows exe, use these approaches.

## Quick Analysis

```bash
# Extract APK
unzip app.apk -d app_unpacked

# Check if obfuscated
cd app_unpacked
find . -name "*.dex" -exec ls -lh {} \;

# Decompile with apktool
apktool d app.apk -o app_decompiled
cd app_decompiled
ls -la  # Check for smali/ directory
```

## Heavily Obfuscated Apps

**Symptoms:**
- Class names are unicode symbols (ۥۡ.smali, ۦۣ.smali)
- Custom obfuscator in manifest (RizalProtection, RizalObfuscator)
- Method names are garbled (nQqQXﹶˉᵎᐧᴵﾞᴵˈﹳיˊˉˏˈˈⁱˈsgDBj)

**Quick bypass without reverse engineering:**

```python
# Remove custom Application class from manifest
import re

with open('AndroidManifest.xml', 'r') as f:
    manifest = f.read()

# Disable protection by removing custom Application
manifest = re.sub(r'android:name="[^"]*Protection[^"]*"', '', manifest)
manifest = re.sub(r'android:name="[^"]*Obfuscator[^"]*"', '', manifest)

with open('AndroidManifest.xml', 'w') as f:
    f.write(manifest)

print("✓ Protection disabled - app will use default Application class")
```

## Recompile Issues

**Resource naming errors ($m3_avd files):**
```bash
cd app_decompiled/res/drawable
for f in \$*.xml; do 
    mv "$f" "$(echo $f | sed 's/\$/m3_/')"
done
```

**"First type is not attr" error:**
- Resource corruption during decompile
- Solution: Skip resource rebuild, modify DEX directly

## Direct DEX Manipulation (Advanced)

When apktool fails to recompile, work directly with classes.dex:

```bash
# Install dex2jar
apt-get install dex2jar

# Convert to JAR
d2j-dex2jar app.apk -o app.jar

# Decompile JAR with JD-GUI or jadx
jadx -d app_jadx app.apk

# Make changes in Java
# Recompile with dx tool
dx --dex --output=classes.dex app_jadx/
```

## Universal APK Bypass Pattern

For license/premium checks when code is too obfuscated to understand:

```python
# Patch all boolean return false → return true
import re
import os

for root, dirs, files in os.walk('smali'):
    for file in files:
        if file.endswith('.smali'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            # Pattern: const/4 v0, 0x0; return v0 → const/4 v0, 0x1; return v0
            modified = re.sub(
                r'const/4 v(\d+), 0x0\s+return v\1',
                r'const/4 v\1, 0x1\n    return v\1',
                content
            )
            
            if modified != content:
                with open(path, 'w') as f:
                    f.write(modified)
                print(f"Patched: {path}")
```

## Signing Patched APK

```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore release.keystore -alias app -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
apksigner sign --ks release.keystore --out app_signed.apk app_patched.apk

# Verify
apksigner verify app_signed.apk
```

## When APK Cracking is Easier Than EXE

APK is preferable when:
- Windows exe has strong anti-tamper
- File is self-extracting archive
- Static patches cause crashes
- DLL injection blocked by antivirus

Android apps generally have:
- No anti-tamper (most apps)
- Easy decompilation (smali is readable)
- No integrity checks
- No code signing enforcement (user can install unsigned)
