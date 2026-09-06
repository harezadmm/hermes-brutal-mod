# Native Library Auto-Injection for Mod Menus

Session: 2026-08-22 (Carrom Pool mod menu build)

## Use Case

Creating modded APKs where a custom native library (`.so`) auto-loads on game start to inject cheats (extended guideline, aimbot, etc.) without requiring external tools like Frida.

## Complete Working Workflow

### 1. Create Native Mod Library

**File:** `libcarrommod.cpp` (or `lib<appname>mod.cpp`)

```cpp
#include <jni.h>
#include <android/log.h>
#include <pthread.h>
#include <unistd.h>
#include <dlfcn.h>

#define LOG_TAG "CarromMod"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// Mod thread - runs in background
void* modThread(void* arg) {
    LOGI("Mod started!");
    sleep(5); // Wait for game to load
    
    // Hook game functions here
    // - Extended guideline hooks
    // - Currency modification
    // - Aimbot features
    
    LOGI("Mod is now active!");
    
    while (true) {
        sleep(60);
        LOGI("Mod heartbeat");
    }
    
    return nullptr;
}

// JNI_OnLoad - Auto-called when library loads
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    LOGI("Mod library loaded!");
    
    pthread_t thread;
    int result = pthread_create(&thread, nullptr, modThread, nullptr);
    
    if (result == 0) {
        pthread_detach(thread);
        LOGI("Mod thread created successfully!");
    }
    
    return JNI_VERSION_1_6;
}
```

### 2. Compile Library (if NDK available)

**With Android NDK:**

```bash
NDK_PATH="/path/to/ndk"
TOOLCHAIN="$NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64"

# ARM64 (modern devices)
$TOOLCHAIN/bin/aarch64-linux-android21-clang++ \
    -shared \
    -o libmod_arm64.so \
    libcarrommod.cpp \
    -llog -landroid -ldl \
    -std=c++17 -O3

# ARM32 (older devices)
$TOOLCHAIN/bin/armv7a-linux-androideabi21-clang++ \
    -shared \
    -o libmod_arm32.so \
    libcarrommod.cpp \
    -llog -landroid -ldl \
    -std=c++17 -O3
```

**Without NDK (stub library for testing):**

Create minimal stub that just logs when loaded. The actual hooking requires proper NDK compilation.

### 3. Decompile APK

```bash
java -jar apktool.jar d original.apk -o app-decompiled -f
```

### 4. Inject Library into APK

```bash
cd app-decompiled

# Create lib directories if don't exist
mkdir -p lib/arm64-v8a
mkdir -p lib/armeabi-v7a

# Copy compiled libraries
cp /path/to/libmod_arm64.so lib/arm64-v8a/libcarrommod.so
cp /path/to/libmod_arm32.so lib/armeabi-v7a/libcarrommod.so
```

**CRITICAL:** Library name must match what you'll load in smali (e.g., `libcarrommod.so` → `System.loadLibrary("carrommod")`).

### 5. Patch Smali to Load Library

**Find main activity:**

```bash
# Search for main activity in AndroidManifest.xml
grep -A 5 "android.intent.action.MAIN" AndroidManifest.xml

# Example output: com.miniclip.carrom.CarromActivity
```

**Locate activity smali file:**

```bash
find . -name "CarromActivity.smali" | grep -v "\$"
# Result: smali_classes8/com/miniclip/carrom/CarromActivity.smali
```

**Find onCreate method:**

```bash
grep -n "\.method.*onCreate" smali_classes8/com/miniclip/carrom/CarromActivity.smali
# Result: 107:.method public onCreate(Landroid/os/Bundle;)V
```

**Inject library loader AFTER super.onCreate():**

```smali
.method public onCreate(Landroid/os/Bundle;)V
    .locals 1
    
    invoke-super {p0, p1}, Lcom/miniclip/nucleus/NucleusActivity;->onCreate(Landroid/os/Bundle;)V
    
    # INJECTED: Load mod library
    const-string v0, "carrommod"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    
    # Continue with original onCreate code...
    invoke-direct {p0}, Lcom/miniclip/carrom/CarromActivity;->setupAudioChangedListener()V
    
    return-void
.end method
```

**Key injection points:**
- ✅ AFTER `invoke-super` in `onCreate()` — library loads once, before other initialization
- ❌ BEFORE `invoke-super` — may crash (parent not initialized)
- ❌ In constructor `<init>` — library loaded multiple times
- ❌ In `onResume` — library reloaded on every resume (memory leak)

### 6. Rebuild APK

```bash
java -jar apktool.jar b app-decompiled -o app-modded-unsigned.apk
```

**Expected output:**
```
I: Using Apktool 2.9.3
I: Checking whether sources has changed...
I: Smaling smali folder into classes.dex...
I: Smaling smali_classes2-10 folders...
I: Building resources...
I: Copying libs... (← confirms .so files copied)
I: Building apk file...
I: Copying unknown files/dir...
```

**Common rebuild errors:**

| Error | Cause | Fix |
|:------|:------|:----|
| `brut.androlib.AndrolibException: brut.directory.PathNotExist: apktool.yml` | Wrong directory | Run from parent of `app-decompiled/` |
| `.so: cannot find` | Library path wrong | Check `lib/arm64-v8a/libcarrommod.so` exists |
| `Smaling failed` | Syntax error in smali | Check inject has proper spacing, no typos |

### 7. Sign APK

```bash
java -jar uber-apk-signer.jar --apks app-modded-unsigned.apk --allowResign
```

Output: `app-modded-aligned-debugSigned.apk`

### 8. Install & Verify

```bash
# Install
adb install -r app-modded-aligned-debugSigned.apk

# Verify mod loads
adb logcat | grep CarromMod
```

**Expected logcat:**
```
I CarromMod: Mod library loaded!
I CarromMod: Mod thread created successfully!
I CarromMod: Mod started!
I CarromMod: Mod is now active!
```

## Troubleshooting

### Library Not Loading (No Logcat Messages)

**Check 1: Library exists in APK**

```bash
unzip -l app-modded-aligned-debugSigned.apk | grep libcarrommod
# Should show: lib/arm64-v8a/libcarrommod.so
```

**Check 2: Library name matches smali call**

Smali: `const-string v0, "carrommod"`  
File: `lib/arm64-v8a/libcarrommod.so`  
Match: YES (`libcarrommod` → `carrommod`)

**Check 3: Smali injection successful**

```bash
grep -A 3 "loadLibrary" app-decompiled/smali*/com/*/CarromActivity.smali
```

Should show your injected code.

**Check 4: Activity actually launched**

```bash
adb logcat | grep "CarromActivity"
```

If no logs, game uses different entry point. Search for `LAUNCHER` activity in manifest.

### Library Loads But Crashes

**Check logcat for crash:**

```bash
adb logcat | grep -E "FATAL|AndroidRuntime"
```

**Common causes:**

1. **Missing symbols:** Library references functions not in `liblog.so` or `libandroid.so`
   - Fix: Recompile with correct `-l` flags
   
2. **ABI mismatch:** Device is ARM32 but only ARM64 library provided
   - Fix: Provide both `lib/armeabi-v7a/` and `lib/arm64-v8a/`

3. **JNI signature wrong:** `JNI_OnLoad` signature doesn't match spec
   - Fix: Use exact signature: `JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved)`

### Hooks Not Working (Library Loads But No Effect)

**Issue:** JNI_OnLoad runs but game functions not hooked.

**Causes:**
1. Game library hasn't loaded yet when hooks attempted
   - Fix: Increase `sleep(5)` to `sleep(10)` in mod thread

2. Function names wrong (obfuscated or different library)
   - Fix: Use Frida to list actual function names first:
   ```javascript
   Process.enumerateModules().forEach(m => console.log(m.name));
   ```

3. Need proper hooking framework (Dobby/Substrate)
   - Fix: For production, use hooking library instead of raw `dlsym`

## Upload Failures for Large APKs

**Session context:** 139 MB modded APK upload repeatedly failed to gofile.io, pixeldrain, file.io, catbox.moe.

**Root causes:**
- Slow/unstable connection (residential)
- Large file size (100+ MB)
- Services timeout on slow uploads (5-15 min limit)

**Working solutions:**

1. **Local install via ADB (fastest):**
   ```bash
   adb install -r /path/to/modded.apk
   ```

2. **Upload from user's machine** (better connection):
   - User uploads to Google Drive / Mega / Telegram
   - Faster than agent-side upload

3. **Split APK approach** (advanced):
   - Use `apktool` to rebuild as split APKs (base + config)
   - Each split < 50 MB uploads reliably
   - Requires Android 5.0+ and proper split configuration

**Don't retry same failing upload service repeatedly.** After 2 failures, switch to local install or user-side upload.

## Size Optimization

Large modded APKs (100+ MB) often result from:

1. **Unused architecture libraries** — if targeting ARM64 only:
   ```bash
   rm -rf app-decompiled/lib/armeabi-v7a
   rm -rf app-decompiled/lib/x86*
   ```

2. **Debug symbols in .so files:**
   ```bash
   # Strip before injecting
   arm-linux-androideabi-strip libmod.so
   ```

3. **Uncompressed assets** — apktool preserves compression, but if manually copied:
   ```bash
   # In apktool.yml, ensure:
   doNotCompress: []  # Don't list .so here
   ```

## Session-Specific Notes

**Carrom Pool (com.miniclip.carrom):**
- 179 MB original APK
- 139 MB modded APK (resources re-compressed by apktool)
- Main activity: `com.miniclip.carrom.CarromActivity`
- Smali location: `smali_classes8/com/miniclip/carrom/CarromActivity.smali`
- Build time: ~4 minutes (APKTool rebuild on Windows, 10 dex files)
- Signing time: ~30 seconds

**Successful injection:**
```smali
# At line 116, after invoke-super:
const-string v0, "carrommod"
invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
```

**Verification command:**
```bash
adb logcat | grep CarromMod
```

## References

- Android JNI Spec: https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/invocation.html
- System.loadLibrary docs: https://developer.android.com/reference/java/lang/System#loadLibrary(java.lang.String)
- Smali reference: https://github.com/JesusFreke/smali/wiki
