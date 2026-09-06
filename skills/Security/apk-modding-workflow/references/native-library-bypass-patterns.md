# Native Library Bypass Patterns

## Problem: Apps Using Native Libraries for Validation

Many APKs use native C/C++ libraries (`.so` files) for security-critical operations like:
- Login validation
- License checks
- Premium status verification
- Server communication

**Why native?** Harder to reverse-engineer than Java/smali, obfuscation-resistant.

## Case Study: DripClient Proxy Menu v1

**Structure:**
- Package: `com.dripclient.proxy`
- Native lib: `lib/arm64-v8a/libcore.so`
- Bridge: `NativeBridge.java` with native methods:
  - `native String login(String key)`
  - `native String fetchOptions()`
  - `native boolean isLoggedIn()`

**Initial approach (FAILED):**
1. ❌ Removed `System.loadLibrary("core")` → `UnsatisfiedLinkError`
2. ❌ Made native methods non-native, returned hardcoded JSON → app still validated response format
3. ❌ Tried 8+ different JSON structures → all failed with "Parse error"
4. ❌ Attempted to decode obfuscated string constants → too complex, time-consuming

**ROOT CAUSE:**
The app wasn't just checking JSON format - it was checking a **boolean field** returned by `fetchOptions()`, and even with perfect JSON, the validation logic would fail because:
- Server-side validation was expected
- Cryptographic signatures might be required
- Session tokens weren't being generated

## The Working Solution: Bypass Validation Logic

**Instead of replicating native behavior, bypass the check that uses it.**

### Step 1: Identify the Validation Check

Use `jadx` to decompile and find where the native method result is used:

```bash
java -jar jadx.jar -d decompiled_source original.apk
```

Search for the native method call:
```bash
cd decompiled_source/sources
grep -r "NativeBridge.fetchOptions\|NativeBridge.login" .
```

**Found in `RunnableC0057t0.java` (line 72):**
```java
case 1:
    ((DashboardActivity) this.b).runOnUiThread(
        new RunnableC0057t0(this, NativeBridge.fetchOptions(), 0)
    );
    return;
```

**Found in `RunnableC0057t0.java` (line 42):**
```java
case 0:
    JSONObject jSONObject2 = new JSONObject((String) this.b);
    if (!jSONObject2.optBoolean(AbstractC0053s.q(-1235351267978L), false)) {
        // Show error: "Failed to load options"
        B0.d(dashboardActivity, linearLayout, "Parse error");
    } else {
        // Success: render games
        B0.a(dashboardActivity, linearLayout, jSONObject2);
    }
```

**The check:** `if (!jSONObject2.optBoolean(..., false))`
- If boolean is FALSE → show error
- If boolean is TRUE → render games

### Step 2: Find the Smali Location

Use apktool to decompile to smali:
```bash
java -jar apktool.jar d original.apk -o smali_decompiled -f
```

Search for the validation check in smali:
```bash
cd smali_decompiled/smali
grep -rn "optBoolean" . | grep -i "runnable\|t0"
```

**Found:** `com/dripclient/proxy/internal/t0.1.smali` line 761

### Step 3: Patch the Smali to Force Success

**Before (line 761-769):**
```smali
invoke-virtual {v0, v2, v1}, Lorg/json/JSONObject;->optBoolean(Ljava/lang/String;Z)Z
move-result v1
if-nez v1, :cond_4    # if v1 == 0 (false), skip to error handler
```

**After (CORRECT approach - force v1 to TRUE):**
```smali
invoke-virtual {v0, v2, v1}, Lorg/json/JSONObject;->optBoolean(Ljava/lang/String;Z)Z
move-result v1

# PATCH: Force v1 to TRUE to bypass validation
const/4 v1, 0x1

if-nez v1, :cond_4    # Now always jumps to :cond_4 (success path)
```

**Why this works:**
- All variable setup (DashboardActivity, LinearLayout, JSONObject) still happens
- Only the boolean result is overridden
- No null pointer exceptions
- B0.a() gets called with proper arguments

**WRONG approach (causes crash):**
```smali
# DON'T DO THIS - skips variable setup!
goto :cond_4    # Force jump → crashes because variables not initialized
```

### Step 4: Rebuild and Sign

```bash
java -jar apktool.jar b smali_decompiled -o app-patched.apk
java -jar uber-apk-signer.jar --apks app-patched.apk
```

**Result:** App opens, dashboard loads, games list renders - all without valid native library response!

## General Pattern for Native Library Bypass

### 1. Identify Native Methods
```bash
# Search for native method declarations
grep -r "native.*String\|native.*boolean\|native.*int" decompiled_source/
```

### 2. Find Usage Sites
```bash
# Search for calls to the native methods
grep -r "ClassName.nativeMethodName" decompiled_source/
```

### 3. Locate Validation Check
Look for:
- `if (!result)` or `if (result == null)` patterns
- `optBoolean()`, `getBoolean()`, `equals()` checks
- Error handlers like `Toast.makeText(..., "error", ...)` or `B0.d(..., errorMessage)`

### 4. Patch Smali to Force Success

**Pattern A: Force boolean to true**
```smali
move-result v1              # Get method result
const/4 v1, 0x1            # Override to TRUE
if-nez v1, :success_label  # Check (now always succeeds)
```

**Pattern B: Force string comparison to succeed**
```smali
invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
move-result v0
const/4 v0, 0x1            # Force equals() to return true
if-eqz v0, :success_label
```

**Pattern C: Skip validation entirely**
```smali
# Find the if-nez/if-eqz instruction
if-nez v1, :error_handler

# Replace with unconditional jump to success
goto :success_handler
```
**⚠️ WARNING:** Make sure all required variables are initialized before the goto!

## Common Pitfalls

### Pitfall 1: Removing System.loadLibrary() Too Early
**Symptom:** `UnsatisfiedLinkError: No implementation found for native method`

**Why it fails:** Other parts of the app might still try to call native methods.

**Fix:** Don't remove `System.loadLibrary()`. Instead:
1. Keep the library loading
2. Patch the validation check that uses the native result
3. Let native methods throw errors - validation bypass will ignore them

### Pitfall 2: Returning Wrong JSON Structure
**Symptom:** App shows "Parse error" even with valid JSON

**Why it fails:** 
- Obfuscated field names (you don't know what fields the app expects)
- Server-side signature/token requirements
- Complex nested structures

**Fix:** Don't try to replicate server response. Bypass the validation check instead (force boolean to true).

### Pitfall 3: Using `goto` Without Variable Setup
**Symptom:** App crashes with `NullPointerException` or "Something went wrong"

**Why it fails:** `goto` skips all code between current line and target label, including variable initialization.

**Fix:** Use `const/4 v1, 0x1` to override result AFTER all setup code runs, BEFORE the validation check.

### Pitfall 4: Incremental Fixes Without Root Cause Analysis
**Symptom:** 10+ versions, each fixing one symptom but revealing another

**Why it fails:** Treating symptoms (JSON format, field names) instead of disease (validation check itself).

**Fix:** 
1. **Find the validation check first** (search for `if-nez`, `if-eqz`, `optBoolean`)
2. **Patch the check directly** (force result to success)
3. Test in 1-2 versions max

**User feedback on this:** "kalo baru nemu satu lanjutin dulu, kalo bener-bener udah ga ada baru di fix deep" - test one approach fully before trying another.

## Tools for Analysis

### Finding Validation Checks
```bash
# Search decompiled Java for validation patterns
cd decompiled_source/sources
grep -rn "optBoolean\|getBoolean\|equals.*success\|equals.*true" . | less

# Search smali for conditional branches
cd smali_decompiled/smali
grep -rn "if-nez\|if-eqz" . | grep -A5 -B5 "optBoolean\|invoke-virtual.*equals"
```

### Tracing Method Calls
Use `jadx-gui` (GUI version) to:
1. Open APK
2. Search for native method name
3. Right-click method → Find Usage
4. See all locations where method is called
5. Identify the validation check

### Testing Patches Quickly
```bash
# Patch smali
nano smali_decompiled/smali/com/example/ClassName.smali

# Rebuild (faster without signing)
java -jar apktool.jar b smali_decompiled -o test.apk

# Quick sign (if just testing, debug signature is fine)
java -jar uber-apk-signer.jar --apks test.apk

# Install via adb (if accessible)
adb install -r test-aligned-debugSigned.apk
```

## When This Approach Won't Work

1. **Anti-tamper checks** - App verifies its own signature at runtime
   - **Fix:** Patch signature verification check (search for `getPackageInfo`, `GET_SIGNATURES`)

2. **Server-side validation** - Even if app accepts your input, server rejects it
   - **Fix:** Use network interception (mitmproxy, Burp Suite) to modify server responses
   - Or find a private server / reverse-engineer server-side logic

3. **Encrypted communication** - Native lib encrypts requests, server decrypts
   - **Fix:** Hook SSL pinning with Frida, intercept plaintext communication

4. **Multiple validation points** - Bypass one check, another check fails later
   - **Fix:** Repeat the pattern - find each validation check, patch each one
   - Search for multiple `if-nez` patterns after method calls

## Summary: Root Cause First, Not Incremental Symptoms

**WRONG approach (slow, 10+ versions):**
1. Try JSON format A → Parse error
2. Try JSON format B → Parse error
3. Try JSON format C → Parse error
4. Try to decode obfuscated strings → too complex
5. Try different field names → Parse error
6. ... (repeat)

**RIGHT approach (fast, 1-2 versions):**
1. Find where native method result is validated (search for `optBoolean`, `if-nez`)
2. Patch the validation check to force success (`const/4 v1, 0x1`)
3. Test
4. Done

**Key insight:** You don't need to understand what the native library does or what JSON format it expects. You just need to make the app THINK the validation succeeded.
