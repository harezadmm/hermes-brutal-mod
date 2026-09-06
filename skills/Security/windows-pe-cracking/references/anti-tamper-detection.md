# Anti-Tamper Protection Detection and Handling

## Symptoms of Anti-Tamper

### Window Creation Failure
- Process appears in Task Manager with valid PID
- CPU usage normal (not crashed)
- Memory usage reasonable (1-50MB)
- **MainWindowHandle = 0** (critical indicator)
- No visible window despite process running
- No error message or crash dialog

**Diagnosis:**
```powershell
Get-Process | Where {$_.ProcessName -like '*app*'} | Select Id, MainWindowHandle
```
If MainWindowHandle is 0, GUI initialization was blocked by tamper detection.

### Immediate Crash on Modified Binary
- Static patch applied successfully (checksum recalculated)
- File structure valid (PE headers intact)
- But exe crashes instantly or shows "corrupted" error
- No specific error message, just immediate termination

### Process Starts Then Dies
- Process ID appears briefly in Task Manager
- Disappears within 1-2 seconds
- No time to attach debugger
- Event Viewer may show "application crashed" with no details

## Root Causes

1. **Checksum validation** - exe computes its own hash and compares to embedded value
2. **Code integrity checks** - validates .text section hasn't changed
3. **Anti-debug triggers** - detects debugger and terminates
4. **Digital signature verification** - checks authenticode signature
5. **Self-decryption** - unpacks code at runtime, modified bytes = garbage

## Solution: Runtime Memory Patching

**Why it works:**
- Original file remains unmodified (passes integrity checks)
- Patches applied AFTER integrity validation runs
- Process already initialized normally (GUI created)
- Anti-tamper only checks on load, not continuously

**Implementation:**
1. Launch target suspended with CREATE_SUSPENDED flag
2. Inject patch DLL via LoadLibrary remote thread
3. DLL scans process memory for validation patterns
4. Patches in RAM with VirtualProtect
5. Resume main thread

See `references/dll-injection-templates.md` for complete working code.

## Detection Before Wasting Time

Run these checks BEFORE attempting static patches:

```bash
# Check for high entropy sections (encrypted/packed code)
python3 << EOF
import pefile
pe = pefile.PE('app.exe')
for section in pe.sections:
    entropy = section.get_entropy()
    if entropy > 7.0:
        print(f"{section.Name.decode().strip()}: {entropy:.2f} - SUSPICIOUS")
EOF

# Check for anti-debug imports
strings app.exe | grep -iE 'IsDebuggerPresent|CheckRemoteDebugger|NtQueryInformation'

# Check for self-extracting archive (different approach needed)
7z l app.exe | grep -E '\.exe|\.dll' | head -5
```

If any red flags appear → go straight to runtime injection, skip static patching.

## Verification After Patch

```python
# Test if patched exe still works
import subprocess
import time

proc = subprocess.Popen(['app_cracked.exe'])
time.sleep(2)

# Check if still running
if proc.poll() is None:
    print("✓ Process still alive")
    # Check for window
    import win32gui
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            windows.append(hwnd)
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    if any(proc.pid == win32process.GetWindowThreadProcessId(w)[1] for w in windows):
        print("✓ Window created successfully")
    else:
        print("✗ Window creation failed - use runtime injection")
else:
    print("✗ Process terminated - anti-tamper triggered")
```

## Progressive Patching Strategy

Don't patch everything at once. Test incrementally:

1. **First pass:** Patch only CMP+JNE patterns (10-20 patches)
2. **Test:** Launch and check MainWindowHandle
3. **If works:** Add TEST+JE patterns (20-40 more)
4. **Test again**
5. **If fails:** Roll back, identify critical path

This isolates which patches break the exe.
