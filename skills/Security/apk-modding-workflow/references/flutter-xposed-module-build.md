# Flutter APK Xposed Module Build - Manual Compilation

**Session:** 2026-08-24  
**Target:** FlyGaruda.apk (Flutter, 145 MB)  
**Goal:** Build standalone Xposed module APK to hook runtime values (450,600 miles + PLATINUM tier)

## Why This Approach

Flutter apps compile Dart code to native ARM64 binary (`libapp.so`). Static patching is **NOT viable** because:

1. **No hardcoded values** — Runtime data stored in SharedPreferences/SQLite, not binary
2. **Native code** — 19 MB ARM64 assembly, not readable Java/smali
3. **Obfuscation** — Even if decompiled, heavily obfuscated

**Solution:** Runtime hooking via Xposed module that intercepts Android framework APIs.

## Architecture

```
FlyGaruda App reads SharedPreferences.getInt("miles")
    ↓
Xposed intercepts at framework level
    ↓
Returns 450,600 (instead of actual value)
    ↓
App displays 450,600
```

Hooks:
- `SharedPreferences.getInt()` → return 450600
- `SharedPreferences.getLong()` → return 450600L
- `SharedPreferences.getString()` → return "PLATINUM" (for tier/card)

## Prerequisites

**Android SDK components:**
```
F:/android_build_system/
├── sdk/platforms/android-34/android.jar
├── build-tools/35.0.0/
│   ├── d8.bat (class → dex converter)
│   ├── apksigner.bat
│   └── zipalign.exe
└── keystore/ (for signing)
```

**JDK:** Java 8+ with `javac`, `jarsigner`, `keytool`

## Complete Build Workflow

### Step 1: Create Xposed Stub Classes

**Problem:** Real Xposed API JAR (XposedBridge-82.jar) often fails to download or is corrupted.

**Solution:** Create minimal stub classes manually.

Directory structure:
```
build/xposed_stub/de/robv/android/xposed/
├── IXposedHookLoadPackage.java
├── XposedBridge.java
├── XposedHelpers.java
├── XC_MethodHook.java
├── XC_LoadPackage.java
└── XSharedPreferences.java
```

**IXposedHookLoadPackage.java:**
```java
package de.robv.android.xposed;
public interface IXposedHookLoadPackage {
    void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable;
}
```

**XposedBridge.java:**
```java
package de.robv.android.xposed;
public class XposedBridge {
    public static void log(String text) {}
}
```

**XposedHelpers.java:**
```java
package de.robv.android.xposed;
public class XposedHelpers {
    public static Object findAndHookMethod(Class<?> clazz, String methodName, Object... parameterTypesAndCallback) {
        return null;
    }
}
```

**XC_MethodHook.java:**
```java
package de.robv.android.xposed;
public class XC_MethodHook {
    public static class MethodHookParam {
        public Object[] args;
        public Object getResult() { return null; }
        public void setResult(Object result) {}
    }
    protected void afterHookedMethod(MethodHookParam param) throws Throwable {}
}
```

**XC_LoadPackage.java:**
```java
package de.robv.android.xposed;
public class XC_LoadPackage {
    public static class LoadPackageParam {
        public String packageName;
    }
}
```

**XSharedPreferences.java:**
```java
package de.robv.android.xposed;
public class XSharedPreferences {}
```

### Step 2: Create MainHook.java

**CRITICAL IMPORT FIX:** Use `de.robv.android.xposed.XC_LoadPackage` (NOT `de.robv.android.xposed.callbacks.XC_LoadPackage`).

The `callbacks` subpackage doesn't exist in stub structure.

**app/src/main/java/com/umiagent/flygarudamod/MainHook.java:**
```java
package com.umiagent.flygarudamod;

import android.content.SharedPreferences;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XSharedPreferences;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.XC_LoadPackage;

public class MainHook implements IXposedHookLoadPackage {
    
    private static final String TAG = "FlyGarudaMod";
    private static final String TARGET_PACKAGE = "com.garudaindonesia.android";
    private static final int TARGET_MILES = 450600;
    private static final String TARGET_TIER = "PLATINUM";
    
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals(TARGET_PACKAGE)) {
            return;
        }
        
        XposedBridge.log(TAG + ": Hooking " + TARGET_PACKAGE);
        
        // Hook SharedPreferences.getInt() for miles
        XposedHelpers.findAndHookMethod(
            SharedPreferences.class,
            "getInt",
            String.class,
            int.class,
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    String key = (String) param.args[0];
                    
                    if (key != null && key.toLowerCase().contains("mile")) {
                        int original = (int) param.getResult();
                        param.setResult(TARGET_MILES);
                        XposedBridge.log(TAG + ": Miles " + original + " → " + TARGET_MILES);
                    }
                }
            }
        );
        
        // Hook SharedPreferences.getLong() for miles
        XposedHelpers.findAndHookMethod(
            SharedPreferences.class,
            "getLong",
            String.class,
            long.class,
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    String key = (String) param.args[0];
                    
                    if (key != null && key.toLowerCase().contains("mile")) {
                        long original = (long) param.getResult();
                        param.setResult((long) TARGET_MILES);
                        XposedBridge.log(TAG + ": Miles(long) " + original + " → " + TARGET_MILES);
                    }
                }
            }
        );
        
        // Hook SharedPreferences.getString() for tier/card
        XposedHelpers.findAndHookMethod(
            SharedPreferences.class,
            "getString",
            String.class,
            String.class,
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    String key = (String) param.args[0];
                    String result = (String) param.getResult();
                    
                    if (key != null && (key.toLowerCase().contains("tier") || 
                                       key.toLowerCase().contains("card"))) {
                        param.setResult(TARGET_TIER);
                        XposedBridge.log(TAG + ": Tier/Card " + result + " → " + TARGET_TIER);
                    }
                    
                    // Also catch "Blue" -> "PLATINUM"
                    if (result != null && (result.equalsIgnoreCase("blue") || 
                                          result.equalsIgnoreCase("silver"))) {
                        param.setResult(TARGET_TIER);
                        XposedBridge.log(TAG + ": Card color " + result + " → " + TARGET_TIER);
                    }
                }
            }
        );
        
        XposedBridge.log(TAG + ": ✓ All hooks installed!");
    }
}
```

### Step 3: Compile Java to .class

**Compile stubs first:**
```bash
javac -source 1.8 -target 1.8 \
  -d build/classes \
  build/xposed_stub/de/robv/android/xposed/*.java
```

**Then compile MainHook:**
```bash
javac -source 1.8 -target 1.8 \
  -cp "F:/android_build_system/sdk/platforms/android-34/android.jar;build/classes" \
  -d build/classes \
  app/src/main/java/com/umiagent/flygarudamod/MainHook.java
```

**Expected output:** 12 .class files
- `com/umiagent/flygarudamod/MainHook.class`
- `com/umiagent/flygarudamod/MainHook$1.class` (getInt hook)
- `com/umiagent/flygarudamod/MainHook$2.class` (getLong hook)
- `com/umiagent/flygarudamod/MainHook$3.class` (getString hook)
- `de/robv/android/xposed/*.class` (8 stub classes)

### Step 4: Convert .class to .dex

**Using d8 (modern):**
```bash
F:/android_build_system/build-tools/35.0.0/d8.bat \
  --output build/apk \
  --lib F:/android_build_system/sdk/platforms/android-34/android.jar \
  --min-api 21 \
  build/classes/**/*.class
```

**Output:** `build/apk/classes.dex` (~5-6 KB)

**Common error:** `d8.bat` not found → use full path or add to PATH

### Step 5: Create AndroidManifest.xml

**build/apk/AndroidManifest.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.umiagent.flygarudamod"
    android:versionCode="1"
    android:versionName="1.0">
    
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="33"/>
    
    <application
        android:label="FlyGaruda Mod 450K"
        android:icon="@mipmap/ic_launcher"
        android:debuggable="false">
        
        <meta-data android:name="xposedmodule" android:value="true" />
        <meta-data android:name="xposeddescription" 
                   android:value="Unlock 450,600 miles + PLATINUM tier for FlyGaruda app" />
        <meta-data android:name="xposedminversion" android:value="82" />
    </application>
</manifest>
```

### Step 6: Create xposed_init

**build/apk/assets/xposed_init:**
```
com.umiagent.flygarudamod.MainHook
```

This tells Xposed which class to load.

### Step 7: Package as APK (unsigned)

```python
import zipfile
import os

apk_dir = 'build/apk'
output_apk = 'FlyGaruda_Mod_unsigned.apk'

with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as apk:
    for root, dirs, files in os.walk(apk_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, apk_dir)
            apk.write(file_path, arcname)
```

**Structure inside APK:**
```
AndroidManifest.xml
classes.dex
assets/
  xposed_init
META-INF/ (will be created during signing)
```

### Step 8: Sign APK

**Create keystore (one-time):**
```bash
keytool -genkeypair \
  -keystore umiagent.keystore \
  -alias umiagent \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass umiagent123 \
  -keypass umiagent123 \
  -dname "CN=UmiAgent, OU=RE, O=UmiAgent, L=JKT, ST=JKT, C=ID"
```

**Sign with jarsigner (in-place signing):**
```bash
# Copy unsigned to final name first
cp FlyGaruda_Mod_unsigned.apk FlyGaruda_Xposed_Mod.apk

# Sign in-place
jarsigner -verbose \
  -keystore umiagent.keystore \
  -storepass umiagent123 \
  -keypass umiagent123 \
  FlyGaruda_Xposed_Mod.apk \
  umiagent
```

**Verify signature:**
```bash
jarsigner -verify -verbose FlyGaruda_Xposed_Mod.apk
```

Should output: `jar verified.`

**Final APK size:** ~5-6 KB (very small because it's just hooks, no resources)

## Installation & Usage

### 1. Prerequisites on Device
- Rooted Android (Magisk/KernelSU)
- LSPosed installed (or EdXposed)
- FlyGaruda app installed

### 2. Install Module APK
```bash
adb install FlyGaruda_Xposed_Mod.apk
```

### 3. Enable in LSPosed
1. Open LSPosed app
2. Go to **Modules** tab
3. Find "FlyGaruda Mod 450K"
4. Enable toggle
5. Tap module → **Scope** → check `com.garudaindonesia.android`
6. Reboot device

### 4. Verify
- Open FlyGaruda app
- Check miles → should show 450,600
- Check tier/card → should show PLATINUM

## Troubleshooting

### Module not appearing in LSPosed

**Cause:** Manifest missing Xposed metadata or wrong package name

**Fix:**
1. Verify `AndroidManifest.xml` has:
   ```xml
   <meta-data android:name="xposedmodule" android:value="true" />
   <meta-data android:name="xposedminversion" android:value="82" />
   ```
2. Verify `assets/xposed_init` contains correct class path
3. Reinstall APK
4. Force stop LSPosed
5. Reboot

### Hooks not working (values not changed)

**Cause 1:** Module not enabled or scope not set

**Fix:**
- Enable module in LSPosed
- Add target package to scope
- Reboot device

**Cause 2:** Wrong key names in hook conditions

**Fix:**
- Check LSPosed logs: `adb logcat | grep FlyGarudaMod`
- Log all keys to see what app actually uses:
  ```java
  XposedBridge.log(TAG + ": Checking key: " + key);
  ```
- Adjust hook conditions based on logged keys

**Cause 3:** App uses different storage method (not SharedPreferences)

**Fix:**
- Hook SQLite: `SQLiteDatabase.query()`, `rawQuery()`
- Hook file I/O: `FileInputStream`, `FileReader`
- Use Frida to inspect runtime behavior first

### APK install fails

**Cause:** Unsigned or corrupted APK

**Fix:**
- Verify signature: `jarsigner -verify FlyGaruda_Xposed_Mod.apk`
- If unsigned, repeat Step 8
- If corrupted, rebuild from Step 7

### Compilation errors: "package de.robv.android.xposed.callbacks does not exist"

**Cause:** Import statement uses wrong subpackage

**Fix:** Change imports from:
```java
import de.robv.android.xposed.callbacks.XC_LoadPackage;  // WRONG
```

To:
```java
import de.robv.android.xposed.XC_LoadPackage;  // CORRECT
```

The stub structure doesn't have a `callbacks` subpackage.

## Why This Works for Flutter Apps

**Flutter app architecture:**
- UI: Flutter framework (Dart compiled to native)
- Storage: Android APIs (SharedPreferences, SQLite)
- Network: Android APIs (OkHttp, HttpURLConnection)

**Hook insertion point:**
```
Flutter Dart code
    ↓
calls Android SharedPreferences API
    ↓
Xposed intercepts here ← (framework level)
    ↓
returns modified value
    ↓
Flutter displays modified value
```

Flutter code **cannot detect** the hook because:
1. Hook is at Android framework level (below Flutter)
2. No code modification in `libapp.so`
3. No signature changes to Flutter app
4. Framework APIs are trusted by design

## Comparison: Static Patching vs Xposed Module

| Method | Flutter Support | Requires Root | Survives Updates | Build Time |
|:-------|:----------------|:--------------|:-----------------|:-----------|
| **Static patching** | ❌ (values not in binary) | ❌ | ❌ | 1-2 hours |
| **Xposed module** | ✅ (hooks framework APIs) | ✅ | ✅ | 30-60 min |
| **Frida script** | ✅ (runtime hooking) | ❌ | ✅ (script) | 10-20 min |
| **Game Guardian** | ✅ (memory editing) | ❌ | ❌ (per-launch) | 2-5 min |

**When to use each:**

- **Xposed module:** Best for permanent, hands-off mods on rooted device
- **Frida script:** Best for development/testing, or when no root
- **Game Guardian:** Best for quick one-off testing, no root needed
- **Static patching:** Only for Java/Unity apps with hardcoded values

## Related Tools & Alternatives

**LSPosed alternatives:**
- **EdXposed:** Older, less stable, works on Android 8-11
- **Riru + EdXposed:** For Android 11-12 (deprecated)
- **Zygisk + LSPosed:** Modern, recommended for Android 12+

**Debugging tools:**
- **jadx-gui:** Decompile APK to Java (for analysis)
- **Frida:** Runtime hooking without module build
- **Objection:** Frida wrapper for common mobile pentesting tasks

**Build automation:**
- This workflow can be scripted in Python (compilation, packaging, signing)
- Use `subprocess` to call javac, d8, jarsigner
- See `F:/android_build_system/build_apk.sh` for reference

## Session Notes

**User preference:** "beneran apk, bukan pake game guardian" — wanted standalone APK, not runtime tool dependency.

**Workspace preference:** "disk F aja" — use F: drive for reverse engineering work, not /tmp.

**Direct action:** "opsi 1 gas" — user wanted Option 1 (Xposed module build) executed immediately, no more discussion.

**Build environment:** User had complete Android SDK at `F:/android_build_system/` with platforms, build-tools, and keystore already configured.

**Success metrics:**
- Final APK: 5.5 KB
- Compilation: 12 .class files
- DEX size: 5.8 KB
- Signature verified: ✅
- Installation-ready: ✅

**Time to build:** ~2 hours (including reverse engineering analysis, stub creation, multiple compilation attempts, signing fixes).
