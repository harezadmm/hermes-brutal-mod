# Mod Menu APK Injection

Complete workflow for injecting a built-in mod menu into an APK — permanent modifications that auto-load on game start without requiring Frida or root.

## Use Case

User wants **built-in mod menu** (not temporary Frida hooks):
- Modded APK with features baked in
- Auto-loads when game starts
- Toggle switches for cheats
- No external tools needed after install

## Architecture

```
Original APK
    ↓
Decompile (apktool)
    ↓
Inject native library (libmod.so)
    ↓
Patch smali to load library in Activity.onCreate()
    ↓
Rebuild & Sign
    ↓
Modded APK (self-contained)
```

## Complete Workflow

### Step 1: Decompile Target APK

```bash
java -jar apktool.jar d original.apk -o apk_decompiled -f
```

**Large APKs (>100MB):**
- Takes 5-10 minutes
- Watch for "Baksmaling classesN.dex" progress
- APKs with 10+ dex files are common (Unity, Flutter)

### Step 2: Create Native Mod Library

**Option A: Simple Stub (Logging Only)**

```cpp
// libmod.cpp
#include <android/log.h>
#define LOG(msg) __android_log_print(ANDROID_LOG_INFO, "ModMenu", msg)

void __attribute__((constructor)) init() {
    LOG("Mod library loaded!");
    LOG("Features: [List your mods here]");
}
```

Compile:
```bash
$NDK/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android21-clang++ \
    -shared -o libmod.so libmod.cpp -llog
```

**Option B: Full Mod with Hooks**

```cpp
// libmod.cpp - Complete mod template
#include <jni.h>
#include <android/log.h>
#include <pthread.h>
#include <unistd.h>
#include <dlfcn.h>

#define LOG_TAG "ModMenu"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// Mod state
static bool initialized = false;

// Initialize hooks
void initHooks() {
    LOGI("Initializing mod hooks...");
    
    // Load game library
    void* game_lib = dlopen("libunity.so", RTLD_NOW);
    if (!game_lib) game_lib = dlopen("libil2cpp.so", RTLD_NOW);
    
    if (game_lib) {
        LOGI("Game library loaded: %p", game_lib);
        
        // Find and hook functions
        // Use Dobby/Substrate for actual hooking
        // This is just the structure
        
    } else {
        LOGE("Failed to load game library: %s", dlerror());
    }
    
    initialized = true;
}

// Background mod thread
void* modThread(void* arg) {
    LOGI("========================================");
    LOGI("MOD MENU STARTED");
    LOGI("Version: 1.0");
    LOGI("========================================");
    
    sleep(3); // Wait for game to load
    
    initHooks();
    
    LOGI("Mod is active!");
    
    while(true) {
        sleep(60);
        if (initialized) {
            LOGI("Mod heartbeat - still active");
        }
    }
    
    return nullptr;
}

// JNI_OnLoad - Auto-called when library loads
JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    LOGI("Mod library loaded via JNI_OnLoad!");
    
    pthread_t thread;
    pthread_create(&thread, nullptr, modThread, nullptr);
    pthread_detach(thread);
    
    return JNI_VERSION_1_6;
}
```

### Step 3: Inject Library into APK

```bash
# Copy to APK lib directories
mkdir -p apk_decompiled/lib/arm64-v8a
mkdir -p apk_decompiled/lib/armeabi-v7a

cp libmod.so apk_decompiled/lib/arm64-v8a/
cp libmod.so apk_decompiled/lib/armeabi-v7a/
```

**CRITICAL:** Include BOTH architectures (64-bit and 32-bit) for compatibility.

### Step 4: Patch Smali to Load Library

Find main activity:
```bash
grep -r "android.app.Activity" apk_decompiled/smali*/com/package/name/*.smali
```

Common patterns:
- `MainActivity.smali`
- `SplashActivity.smali`
- `{GameName}Activity.smali`

Edit the activity's `onCreate` method:

**Before:**
```smali
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1
    
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    
    # Original code continues...
.end method
```

**After:**
```smali
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1
    
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    
    # INJECTED: Load mod library
    const-string v0, "mod"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    
    # Original code continues...
.end method
```

**Library naming:**
- `libmod.so` in filesystem
- `"mod"` in smali (no lib prefix, no .so suffix)

### Step 5: Rebuild APK

```bash
java -jar apktool.jar b apk_decompiled -o modded_unsigned.apk
```

**Expected duration:**
- Small APK (<50MB): 30-60 seconds
- Medium APK (50-150MB): 2-3 minutes
- Large APK (>150MB): 5-10 minutes

**Progress indicators:**
```
I: Smaling smali folder into classes.dex...
I: Smaling smali_classes2 folder into classes2.dex...
I: Smaling smali_classes10 folder into classes10.dex...
I: Building resources...
```

**Last step takes longest:** "Building resources" (aapt2 compile)

### Step 6: Sign APK

```bash
# Create keystore (one time)
keytool -genkey -v \
    -keystore mod.keystore \
    -alias modkey \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass password123 \
    -keypass password123 \
    -dname "CN=ModMenu, OU=Mod, O=Org, L=City, ST=State, C=US"

# Sign with uber-apk-signer (recommended)
java -jar uber-apk-signer.jar --apks modded_unsigned.apk --allowResign

# Or jarsigner (fallback)
jarsigner -verbose \
    -sigalg SHA256withRSA \
    -digestalg SHA-256 \
    -keystore mod.keystore \
    -storepass password123 \
    modded_unsigned.apk \
    modkey
```

Output: `modded_unsigned-aligned-debugSigned.apk`

### Step 7: Install & Verify

```bash
# Uninstall original (signature mismatch)
adb uninstall com.package.name

# Install modded
adb install -r modded-aligned-debugSigned.apk

# Verify mod loaded
adb logcat | grep ModMenu
```

**Expected logcat output:**
```
I ModMenu: Mod library loaded via JNI_OnLoad!
I ModMenu: ========================================
I ModMenu: MOD MENU STARTED
I ModMenu: Version: 1.0
I ModMenu: ========================================
I ModMenu: Initializing mod hooks...
I ModMenu: Game library loaded: 0x7ab4c00000
I ModMenu: Mod is active!
```

## Troubleshooting

### Library Not Loading

**Symptom:** No "ModMenu" logs in logcat

**Check 1:** Library exists in APK
```bash
unzip -l modded.apk | grep libmod.so
# Should show:
# lib/arm64-v8a/libmod.so
# lib/armeabi-v7a/libmod.so
```

**Check 2:** Smali injection present
```bash
grep -A 2 "loadLibrary" apk_decompiled/smali*/com/package/MainActivity.smali
# Should show const-string + invoke-static System.loadLibrary
```

**Check 3:** Library architecture mismatch
```bash
adb shell getprop ro.product.cpu.abi
# If arm64-v8a, needs lib/arm64-v8a/libmod.so
# If armeabi-v7a, needs lib/armeabi-v7a/libmod.so
```

### Crash on Launch

**Symptom:** App crashes immediately after splash screen

**Cause 1:** Missing dependencies in libmod.so
```bash
# Check library dependencies
readelf -d libmod.so | grep NEEDED
```

**Solution:** Link statically or include dependency .so files

**Cause 2:** Wrong Android API level
```bash
# Should target API 21+ (Android 5.0+)
# Check NDK compile command uses -android21 or higher
```

**Cause 3:** Exception in JNI_OnLoad
```bash
adb logcat | grep -E "FATAL|AndroidRuntime"
```

**Solution:** Wrap JNI_OnLoad in try-catch, return JNI_VERSION_1_6 on error

### APK Rebuild Fails

**Error:** `brut.common.BrutException: could not exec`

**Solution:** aapt/aapt2 binary missing
```bash
# Linux/Mac
chmod +x ~/.local/share/apktool/framework/aapt*

# Windows: download aapt.exe and place in apktool dir
```

**Error:** `error: resource X not found`

**Solution:** Framework resource missing
```bash
java -jar apktool.jar empty-framework-dir --force
# Then rebuild
```

## Advanced: ImGui Mod Menu

For visual floating menu (like GameGuardian style):

**1. Add ImGui to library:**
```cpp
#include <imgui.h>
#include <imgui_impl_android.h>

void renderMenu() {
    ImGui::Begin("Mod Menu");
    
    static bool extended_aim = true;
    ImGui::Checkbox("Extended Guideline", &extended_aim);
    
    static bool aimbot = false;
    ImGui::Checkbox("Aimbot", &aimbot);
    
    ImGui::End();
}
```

**2. Hook rendering thread:**
```cpp
// Hook eglSwapBuffers to inject menu
typedef void (*eglSwapBuffers_t)(void*);
eglSwapBuffers_t orig_eglSwapBuffers;

void hooked_eglSwapBuffers(void* display) {
    renderMenu();
    orig_eglSwapBuffers(display);
}
```

**3. Compile with ImGui:**
```bash
clang++ -shared \
    -o libmod.so \
    libmod.cpp imgui/*.cpp \
    -llog -landroid -lEGL -lGLESv2
```

## User Workflow Preference

**Indonesian user pattern (sisuryaofficialkuu):**
- Direct action, no asking for confirmation
- "continue" = keep building, don't stop to ask
- "YAUDA GAUSQ BANYAK NANYA TINGGAL LLAKUIN AJA" = just do it
- Wants complete built APK, not instructions
- Mixed Indonesian/English technical terms

**For this user:**
1. When user asks for "mod menu APK", start building immediately
2. Don't offer options (Option A/B/C) — pick best and execute
3. Build in background, deliver final APK
4. Provide install command, not multi-step manual process

## Build Script Template

```bash
#!/bin/bash
# complete_mod_build.sh

set -e

APK="$1"
MOD_NAME="$2"

echo "Building $MOD_NAME mod for $APK..."

# Decompile
java -jar apktool.jar d "$APK" -o decompiled -f

# Inject library (assumes libmod.so exists)
mkdir -p decompiled/lib/{arm64-v8a,armeabi-v7a}
cp libmod.so decompiled/lib/arm64-v8a/
cp libmod.so decompiled/lib/armeabi-v7a/

# Patch smali (find main activity automatically)
ACTIVITY=$(find decompiled/smali* -name "*Activity.smali" | head -1)
sed -i '/invoke-super.*Activity;->onCreate/a \    const-string v0, "mod"\n    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V' "$ACTIVITY"

# Rebuild
java -jar apktool.jar b decompiled -o "${MOD_NAME}_unsigned.apk"

# Sign
java -jar uber-apk-signer.jar --apks "${MOD_NAME}_unsigned.apk" --allowResign

echo "Done: ${MOD_NAME}_unsigned-aligned-debugSigned.apk"
```

## References

- **APK structure:** https://developer.android.com/guide/components/fundamentals
- **JNI spec:** https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/jniTOC.html
- **Native hooking:** https://github.com/jmpews/Dobby (inline hook framework)
- **ImGui Android:** https://github.com/ocornut/imgui/blob/master/backends/imgui_impl_android.cpp

## Session Context (Aug 2024)

Carrom Pool mod menu build:
- 179 MB APK, 41,646 classes, 10 dex files
- APKTool rebuild took 4+ minutes (expected for large APK)
- User wanted extended guideline + aimbot, NOT coin hack
- Smali injection successful in `CarromActivity.smali` line 116
- Build script created with background execution
