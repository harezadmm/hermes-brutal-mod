# Large APK Decompilation Performance & Pitfalls

Session: 2026-08-22, Carrom Pool (179MB, 41,646 classes)

## Problem

JADX decompilation of large APKs (40K+ classes, 150MB+) times out at default terminal timeout limits (180s-420s). This causes:
- Incomplete decompilation output
- Script failure before analysis completes
- Need to restart and lose progress

## Root Cause

Large modern games have:
- Multi-dex architecture (10+ dex files)
- 40K-50K classes total
- Heavy obfuscation (ProGuard/R8)
- Native libraries (.so files)
- Large asset bundles

JADX processes classes sequentially and can take 5-15 minutes for these APKs.

## Solution: Background Execution

**Always run JADX and APKTool in background for APKs over 100MB:**

```bash
# Run JADX in background with notification
bash /f/apk_modding_system/decompile/jadx/bin/jadx -d jadx_output app.apk --show-bad-code &

# Or via terminal tool
terminal(
    command="cd analysis_dir && bash /f/apk_modding_system/decompile/jadx/bin/jadx -d jadx_output ../app.apk --show-bad-code",
    background=True,
    notify_on_complete=True
)

# APKTool in background
terminal(
    command='cd analysis_dir && java -jar "F:/apk_modding_system/decompile/apktool.jar" d ../app.apk -o apktool_output -f',
    background=True,
    notify_on_complete=True
)
```

## Path Resolution (Windows + git-bash)

**Critical:** Java tools cannot resolve `/f/` MSYS paths. Use Windows-style paths with forward slashes:

```bash
# ❌ WRONG - Java cannot find jarfile
java -jar /f/apk_modding_system/decompile/apktool.jar d app.apk

# ✅ CORRECT - Use F:/ for Java
java -jar "F:/apk_modding_system/decompile/apktool.jar" d app.apk -o output -f

# ✅ CORRECT - bash scripts can use /f/
bash /f/apk_modding_system/decompile/jadx/bin/jadx -d output app.apk
```

**Rule:**
- Java tools (APKTool, uber-apk-signer, any .jar): Use `F:/path/to/file`
- Bash scripts (JADX wrapper): Can use `/f/path/to/file`
- When in doubt: Use `F:/` — it works for both

## Performance Expectations

| APK Size | Classes | Dex Files | JADX Time | APKTool Time |
|:---------|:--------|:----------|:----------|:-------------|
| 50MB | 10K | 2-3 | 2-3 min | 1-2 min |
| 100MB | 20K | 5-6 | 3-5 min | 2-3 min |
| 179MB | 41K | 10+ | 7-10 min | 4-6 min |
| 250MB+ | 50K+ | 15+ | 10-15 min | 5-8 min |

**Never use foreground execution for APKs over 100MB** — always background with `notify_on_complete=True`.

## Workflow Pattern

```python
# Check APK size first
apk_size = os.path.getsize('app.apk') / 1024 / 1024  # MB

if apk_size > 100:
    print(f"Large APK detected ({apk_size:.0f}MB) - using background processing")
    
    # Start both tools in background
    terminal(
        command='cd analysis && bash /f/apk_modding_system/decompile/jadx/bin/jadx -d jadx_output ../app.apk --show-bad-code',
        background=True,
        notify_on_complete=True
    )
    
    terminal(
        command='cd analysis && java -jar "F:/apk_modding_system/decompile/apktool.jar" d ../app.apk -o apktool_output -f',
        background=True,
        notify_on_complete=True
    )
    
    print("Processing in background. Will notify when complete.")
    print(f"Expected time: 5-10 minutes")
    
else:
    # Small APK - can run foreground with high timeout
    terminal(
        command='jadx -d output app.apk',
        timeout=300
    )
```

## Multi-Dex Architecture

Modern large APKs split code across multiple dex files:

```
app.apk
├── classes.dex      (primary dex)
├── classes2.dex
├── classes3.dex
├── ...
└── classes10.dex    (Carrom Pool had 10+)
```

**APKTool output structure:**
```
apktool_output/
├── smali/           (classes.dex)
├── smali_classes2/  (classes2.dex)
├── smali_classes3/
├── ...
└── smali_classes10/
```

When searching for targets, **search ALL smali directories:**

```bash
# Search across all dex outputs
find apktool_output/smali* -name "*Coin*" -o -name "*Premium*"

# Or with grep
grep -r "isPremium" apktool_output/smali*/
```

## Progress Monitoring

JADX logs progress to stderr:

```
INFO  - progress: 12622 of 41646 (30%)
INFO  - progress: 25329 of 41646 (60%)
INFO  - progress: 39034 of 41646 (93%)
```

APKTool logs dex processing:

```
I: Baksmaling classes.dex...
I: Baksmaling classes2.dex...
I: Baksmaling classes10.dex...
```

Check background process status:

```bash
process(action='list')
process(action='poll', session_id='proc_xyz')
```

## User Expectation Management

When starting large APK analysis, communicate clearly:

```
✅ APK: 179MB, 41,646 classes
⏳ JADX decompiling in background (7-10 min)
⏳ APKTool unpacking in background (4-6 min)
📊 Progress: Will notify when complete

You can check status with: process list
```

**Don't:**
- Retry foreground with higher timeout (still may fail)
- Run synchronously and have user wait 10+ minutes
- Claim "almost done" when at 30% (takes as long as 0-30%)

**Do:**
- Start both tools in background immediately
- Give realistic ETA based on size
- Deliver results when notifications arrive

## When Decompilation Completes

Once notified, verify output:

```bash
# Check JADX created source tree
ls -la jadx_output/sources/

# Check APKTool created smali
ls -la apktool_output/smali*/

# Start target scanning
find jadx_output/sources -name "*Coin*" -o -name "*Premium*" -o -name "*IAP*"
```

Then proceed with cheat target identification and Frida hook generation.
