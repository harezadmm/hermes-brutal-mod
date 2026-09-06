# Frida-Gadget Injection for Non-Root Devices

**Session:** 2026-08-25 (Fake GPS Location crack)  
**Success:** ✅ Pro unlock achieved without root

## When to Use

- Device has no root access
- Lucky Patcher failed
- Flutter app (libflutter.so, libapp.so present)
- Obfuscated Google Play Billing (v7.x+)
- Server-side validation (need to hook before network call)

## Overview

Frida-Gadget embeds the Frida runtime directly into the APK. The modified APK loads Frida at startup and executes hook scripts automatically - achieving permanent runtime hooks without requiring root.

**Trade-offs:**
- ✅ No root required
- ✅ Permanent (embedded in APK)
- ✅ Works on Flutter/obfuscated apps
- ⚠️ APK size increases by ~25 MB
- ⚠️ Setup time: 20-30 minutes
- ⚠️ Some apps detect Frida presence

## Complete Workflow

### 1. Download Frida-Gadget

```bash
cd ~/tools/apk_mod_tools/
curl -L -o frida-gadget.so.xz https://github.com/frida/frida/releases/download/16.5.9/frida-gadget-16.5.9-android-arm64.so.xz
unxz frida-gadget.so.xz
# Result: 25 MB libfrida-gadget.so
```

**Note:** Match architecture to target device (arm64-v8a for 64-bit, armeabi-v7a for 32-bit).

### 2. Decompile APK

```bash
java -jar apktool.jar d app.apk -o decoded/ -f
```

### 3. Inject Gadget Library

```bash
mkdir -p decoded/lib/arm64-v8a/
cp frida-gadget.so decoded/lib/arm64-v8a/libfrida-gadget.so
```

### 4. Create Hook Script

Create `decoded/assets/hook.js`:

```javascript
// Frida-Gadget auto-load hook script
console.log("[+] Frida-Gadget loaded!");

Java.perform(function() {
    console.log("[+] Hooking started...");
    
    // Hook Google Play Billing
    try {
        var Purchase = Java.use("com.android.billingclient.api.Purchase");
        
        Purchase.getPurchaseState.implementation = function() {
            console.log("[+] getPurchaseState() → PURCHASED");
            return 1; // 1 = PURCHASED
        };
        
        Purchase.isAcknowledged.implementation = function() {
            console.log("[+] isAcknowledged() → TRUE");
            return true;
        };
        
        console.log("[+] Billing hooked");
    } catch(e) {
        console.log("[-] Billing not found");
    }
    
    // Hook all boolean "pro/premium/paid" methods
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            // Replace with target package
            if (className.indexOf("com.target.package") >= 0) {
                try {
                    var clazz = Java.use(className);
                    var methods = clazz.class.getDeclaredMethods();
                    
                    methods.forEach(function(method) {
                        var name = method.getName();
                        var type = method.getReturnType().toString();
                        
                        if (type === "boolean" && 
                            (name.indexOf("pro") >= 0 || 
                             name.indexOf("premium") >= 0 ||
                             name.indexOf("paid") >= 0 ||
                             name.indexOf("vip") >= 0)) {
                            
                            console.log("[+] Hook: " + className + "." + name);
                            clazz[name].implementation = function() {
                                return true;
                            };
                        }
                    });
                } catch(e) {}
            }
        },
        onComplete: function() {
            console.log("[+] Hooks complete!");
        }
    });
});
```

**Important:** Replace `"com.target.package"` with actual app package name.

### 5. Create Gadget Config

Create `decoded/lib/arm64-v8a/libfrida-gadget.config.so`:

```json
{
  "interaction": {
    "type": "script",
    "path": "hook.js"
  }
}
```

**Note:** The `.so` extension is intentional - preserves file during APK packaging.

### 6. Patch MainActivity to Load Gadget

Find MainActivity:
```bash
find decoded/smali* -name "MainActivity.smali" | head -1
```

Add **before first method** in MainActivity.smali:

```smali
.method static constructor <clinit>()V
    .locals 1
    
    # FRIDA-GADGET: Auto-load at startup
    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    
    return-void
.end method
```

If `<clinit>` already exists, add the loadLibrary call at its start instead.

### 7. Rebuild and Sign

```bash
java -jar apktool.jar b decoded/ -o modded.apk
java -jar uber-apk-signer.jar --apks modded.apk
# Result: modded-aligned-debugSigned.apk
```

### 8. Handle Split APKs

If original was `.apks` format:

```bash
# Unsign config splits
python3 unsign_splits.py split_config.*.apk

# Sign all with SAME keystore (one command)
java -jar uber-apk-signer.jar --apks modded.apk split_config.*.apk

# Verify signatures match
for apk in *-debugSigned.apk; do
    unzip -p "$apk" META-INF/CERT.RSA | keytool -printcert | grep SHA256
done
# All SHA256 must be identical

# Repack as .apks bundle
python3 -c "
import zipfile
with zipfile.ZipFile('app_gadget.apks', 'w') as bundle:
    bundle.write('modded-aligned-debugSigned.apk', 'base.apk')
    bundle.write('split_config.en-aligned-debugSigned.apk', 'split_config.en.apk')
    # ... add all splits
"
```

### 9. Install and Verify

```bash
adb install modded-aligned-debugSigned.apk

# Watch for gadget load
adb logcat | grep -i frida
# Should see: "[+] Frida-Gadget loaded!"
```

## Real Example: Fake GPS Location

**App:** com.hopefactory2021.fakegpslocation  
**Date:** 2026-08-25  
**Device:** OPPO Reno 12 5G (Android 16, no root)  
**Result:** ✅ Pro unlocked

**Stats:**
- Original base.apk: 14 MB
- With Gadget: 23 MB
- Final .apks: 15.76 MB (compressed)

**Hooks:**
- Google Play Billing (getPurchaseState → 1, isAcknowledged → true)
- All boolean methods matching "pro", "premium", "paid"

**Installation:** Via SAI (Split APKs Installer)

**Logcat output:**
```
[+] Frida-Gadget loaded!
[+] Hooking started...
[+] Billing hooked
[+] Hook: com.hopefactory2021.fakegpslocation.BillingManager.isPro
[+] Hooks complete!
```

## Expected Behavior

1. App launches MainActivity
2. `<clinit>` executes, loads libfrida-gadget.so
3. Gadget reads config, executes hook.js from assets
4. Hooks install before user interaction
5. Pro/Premium checks return true automatically

## Pitfalls

### APK Size Increase
- Gadget: 25 MB uncompressed
- Final impact: +8-10 MB (after .apks compression)
- Unavoidable with this method

### Anti-Frida Detection
Some apps check:
- `/proc/self/maps` for "frida" strings
- Loaded library names

**Mitigation:** Rename `libfrida-gadget.so` to innocent name (e.g., `libutils.so`, `libcore.so`) and update loadLibrary call to match.

### Hook Script Syntax Errors
- App crashes on launch if hook.js has errors
- Test hook logic incrementally
- Check logcat for JavaScript exceptions

### Split APK Signature Mismatch
- All APKs must have identical signatures
- Sign in ONE command (same keystore)
- Verify SHA256 matches before repacking

## Comparison: Methods for No-Root Modding

| Method | Setup Time | Success Rate | APK Size | Detection Risk |
|--------|------------|--------------|----------|----------------|
| Lucky Patcher | 2-5 min | 70-80% | No change | Low |
| Frida-Gadget | 20-30 min | 90%+ | +25 MB | Medium |
| Static Patching | 10-20 min | 60% (Java only) | No change | Low |

**Recommendation:**
1. Try Lucky Patcher first (fastest)
2. Use Frida-Gadget when Lucky Patcher fails
3. Static patching only works on non-Flutter Java/Kotlin apps

## When Frida-Gadget is Necessary

- ✅ Flutter apps (no smali to patch)
- ✅ Heavily obfuscated code (can't find methods)
- ✅ Google Play Billing v7+ (runtime verification)
- ✅ Server-validated apps (hook before network send)
- ✅ Lucky Patcher failed

## Troubleshooting

**App crashes on launch:**
```bash
adb logcat | grep -E "frida|FATAL|AndroidRuntime"
```
- Verify hook.js syntax
- Check gadget config JSON is valid
- Ensure MainActivity patch is correct

**Hooks not executing:**
- Confirm hook.js is in assets/
- Verify config.so points to "hook.js"
- Check logcat shows "[+] Frida-Gadget loaded!"

**"SAI: ada salah mengurangikan paket":**
- Signature mismatch in split APKs
- Re-sign all APKs together
- Verify SHA256 consistency

## Limitations

**Cannot crack:**
- Server-side order generation (e.g., cinema tickets, food orders)
- Blockchain validation
- Hardware attestation
- Apps that detect Frida and refuse to run

**Frida-Gadget hooks BEFORE server validation**, but cannot bypass server-side generation of codes/tokens/orders.

## References

- Frida releases: https://github.com/frida/frida/releases
- Gadget docs: https://frida.re/docs/gadget/
- Session: 10+ hour Fake GPS crack (2026-08-25)
- Tested on: Android 16, OPPO Reno 12 5G, no root
