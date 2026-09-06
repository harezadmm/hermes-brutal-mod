---
name: desktop-app-cracking
description: Crack desktop apps to bypass licensing and trial limits.
tags: [cracking, reverse-engineering, patching, x64dbg, ida]
version: 1.0
author: RedMess
license: MIT
---

# Desktop App Cracking

## When to Use
Use when cracking desktop applications (Windows/Linux/macOS) to bypass trial periods, licensing checks, or premium features.

## Windows App Cracking

### Tools Required
- **x64dbg** - Debugger for Windows apps
- **IDA Pro / Ghidra** - Disassembler and decompiler
- **Detect It Easy (DIE)** - Identify packer/protector
- **UPX** - Unpacker for compressed executables
- **Resource Hacker** - Modify executable resources
- **CFF Explorer** - PE file editor

### Basic Cracking Flow

#### 1. Identify Protection
```bash
# Detect packer/protector
die.exe target.exe

# Common protections:
# - UPX (easy to unpack)
# - Themida/VMProtect (very hard)
# - Enigma Protector (medium)
# - ASPack/PECompact (medium)
```

#### 2. Unpack if Needed
```bash
# UPX unpacking
upx -d target.exe -o unpacked.exe

# Themida/VMProtect requires manual unpacking
# Use x64dbg with ScyllaHide plugin
```

#### 3. Find License Check

**Static Analysis (IDA Pro/Ghidra):**
```c
// Look for common patterns
// Pattern 1: String comparison
if (strcmp(user_serial, valid_serial) == 0) {
    is_licensed = true;
}

// Pattern 2: Registry check
RegOpenKeyEx(HKEY_CURRENT_USER, "Software\\App\\License", ...);
RegQueryValueEx(hKey, "Serial", ...);

// Pattern 3: Trial expiry
if (current_date > install_date + 30) {
    show_trial_expired();
}
```

**Dynamic Analysis (x64dbg):**
```bash
# Load executable in x64dbg
x64dbg.exe target.exe

# Set breakpoints on common functions
bp MessageBoxA
bp GetDlgItemTextA
bp lstrcmpA
bp RegQueryValueExA

# Run and trigger license dialog
# When breakpoint hits, examine stack/registers
```

#### 4. Patch Binary

**Method 1: JMP Patch (Skip License Check)**
```asm
# Original code
00401000: test eax, eax        ; Check if license valid
00401002: jz short 00401020    ; Jump if invalid (show error)
00401004: mov ecx, [ebp+var_4] ; Continue if valid
...
00401020: push offset aTrialExpired ; "Trial expired"
00401025: call MessageBoxA

# Patched code (always jump to valid path)
00401000: test eax, eax
00401002: jmp short 00401004   ; Force jump to valid path (changed jz to jmp)
00401004: mov ecx, [ebp+var_4]
```

**Method 2: NOP Patch (Remove Check)**
```asm
# Original
00401000: call check_license
00401005: test eax, eax
00401007: jz short invalid

# Patched (NOP out the call)
00401000: nop
00401001: nop
00401002: nop
00401003: nop
00401004: nop
00401005: test eax, eax
00401007: jz short invalid
```

**Method 3: Return True Patch**
```asm
# Original check_license function
check_license:
00402000: push ebp
00402001: mov ebp, esp
00402003: ... (complex validation)
00402050: xor eax, eax     ; return false
00402052: pop ebp
00402053: ret

# Patched (always return 1/true)
check_license:
00402000: mov eax, 1       ; return true immediately
00402005: ret
00402006: nop (fill rest)
```

#### 5. Apply Patch Permanently

**Using x64dbg:**
1. Make modifications in x64dbg
2. Right-click instruction → Patches → Patch file
3. Save patched executable

**Using HxD Hex Editor:**
```bash
# Find bytes to patch
# Original: 74 1A (JZ +26)
# Patched:  EB 1A (JMP +26)

# Open in hex editor and replace
hxd.exe target.exe
# Ctrl+F → Find hex: 74 1A
# Replace with: EB 1A
# Save
```

### Keygen Development

#### Create Key Generator
```python
# keygen.py
import hashlib

def generate_serial(username):
    # Reverse-engineered algorithm
    data = f"{username}:SECRET_SALT:2026"
    hash_value = hashlib.md5(data.encode()).hexdigest()
    
    # Format as serial: XXXX-XXXX-XXXX-XXXX
    serial = '-'.join([hash_value[i:i+4].upper() for i in range(0, 16, 4)])
    return serial

if __name__ == "__main__":
    user = input("Enter username: ")
    serial = generate_serial(user)
    print(f"\n[+] Serial: {serial}")
```

**GUI Keygen:**
```python
# keygen_gui.py
import tkinter as tk
import hashlib

def generate():
    username = entry_name.get()
    data = f"{username}:SECRET_SALT:2026"
    serial = hashlib.md5(data.encode()).hexdigest()[:16].upper()
    serial = '-'.join([serial[i:i+4] for i in range(0, 16, 4)])
    entry_serial.delete(0, tk.END)
    entry_serial.insert(0, serial)

root = tk.Tk()
root.title("App Keygen v1.0")
root.geometry("400x200")

tk.Label(root, text="Username:").pack(pady=10)
entry_name = tk.Entry(root, width=30)
entry_name.pack()

tk.Button(root, text="Generate", command=generate).pack(pady=10)

tk.Label(root, text="Serial:").pack()
entry_serial = tk.Entry(root, width=30)
entry_serial.pack()

root.mainloop()
```

### DLL Injection for Runtime Patching
```cpp
// crack.cpp
#include <Windows.h>

DWORD WINAPI MainThread(LPVOID param) {
    // Find license check function
    HMODULE hModule = GetModuleHandle(NULL);
    DWORD_PTR baseAddr = (DWORD_PTR)hModule;
    
    // Patch at offset 0x1000 (license check)
    BYTE* patchAddr = (BYTE*)(baseAddr + 0x1000);
    
    DWORD oldProtect;
    VirtualProtect(patchAddr, 5, PAGE_EXECUTE_READWRITE, &oldProtect);
    
    // Patch: mov eax, 1; ret
    patchAddr[0] = 0xB8; // MOV EAX
    *(DWORD*)(patchAddr + 1) = 1;
    patchAddr[5] = 0xC3; // RET
    
    VirtualProtect(patchAddr, 5, oldProtect, &oldProtect);
    
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        CreateThread(NULL, 0, MainThread, NULL, 0, NULL);
    }
    return TRUE;
}
```

**Compile & Inject:**
```bash
g++ -shared crack.cpp -o crack.dll
# Use any DLL injector
```

## Linux App Cracking

### Tools Required
- **GDB** - GNU Debugger
- **radare2** - Reverse engineering framework
- **patchelf** - Modify ELF executables
- **Ghidra** - Disassembler

### Basic Linux Crack Flow

#### 1. Analyze with radare2
```bash
# Open in radare2
r2 -A target_app

# Analyze all
aaa

# List functions
afl | grep license

# Disassemble license check
pdf @sym.check_license

# Find strings
iz | grep -i trial
iz | grep -i license
```

#### 2. Patch with radare2
```bash
# Open in write mode
r2 -w target_app

# Seek to function
s sym.check_license

# Show assembly
pdf

# Patch instruction (change JE to JMP)
wa jmp 0x401234 @ 0x401230

# Verify patch
pdf

# Save and quit
q
```

#### 3. Patch with GDB
```bash
# Load in GDB
gdb ./target_app

# Set breakpoint at license check
break check_license

# Run
run

# When breakpoint hits, examine
disas

# Patch instruction
set {unsigned char}0x401230 = 0xEB  # JE → JMP

# Continue
continue
```

#### 4. Make Patch Permanent
```bash
# Use xxd to create hex dump
xxd target_app > app.hex

# Edit app.hex (change bytes manually)
# Find: 74 1a (JE)
# Replace: eb 1a (JMP)

# Convert back to binary
xxd -r app.hex > target_app_cracked

# Fix permissions
chmod +x target_app_cracked
```

## macOS App Cracking

### Tools Required
- **Hopper Disassembler** - macOS reverse engineering
- **class-dump** - Extract Objective-C headers
- **lldb** - Debugger
- **optool** - Mach-O binary patching

### Basic macOS Crack Flow

#### 1. Extract Headers
```bash
# Dump Objective-C classes
class-dump -H App.app/Contents/MacOS/App -o headers/

# Find license check methods
grep -r "license\|trial" headers/
```

#### 2. Debug with lldb
```bash
# Load app
lldb App.app/Contents/MacOS/App

# Set breakpoint on license method
br set -n "-[LicenseManager isLicenseValid]"

# Run
run

# When breakpoint hits
disas

# Modify return value (force true)
register write rax 1

# Continue
continue
```

#### 3. Patch Binary
```bash
# Use Hopper to find license check
# Export as assembly, modify, reassemble

# Or use optool to inject dylib
optool install -c load -p "@executable_path/crack.dylib" -t App.app/Contents/MacOS/App

# Sign modified app
codesign -f -s - App.app
```

### Universal Crack: Replace Binary
```bash
# Create wrapper script
cat > App.app/Contents/MacOS/App_original << 'EOF'
#!/bin/bash
# Patch environment to bypass license
export LICENSE_CHECK=0
export TRIAL_DAYS=999
$(dirname "$0")/App_real "$@"
EOF

# Rename original
mv App.app/Contents/MacOS/App App.app/Contents/MacOS/App_real

# Make wrapper executable
chmod +x App.app/Contents/MacOS/App_original
mv App.app/Contents/MacOS/App_original App.app/Contents/MacOS/App
```

## Advanced Techniques

### Anti-Debug Bypass
```cpp
// Detect IsDebuggerPresent check
if (IsDebuggerPresent()) {
    ExitProcess(1);
}

// Patch in x64dbg
// Find call to IsDebuggerPresent
// Set breakpoint after call
// Modify EAX to 0 (no debugger)
// Or patch: MOV EAX, 0; NOP out call
```

### Hardware ID Bypass
```cpp
// App generates HWID from MAC/disk serial
// Hook GetVolumeInformationA
typedef BOOL (WINAPI* pGetVolumeInformationA)(LPCSTR, LPSTR, DWORD, LPDWORD, LPDWORD, LPDWORD, LPSTR, DWORD);
pGetVolumeInformationA oGetVolumeInfo;

BOOL WINAPI hkGetVolumeInformationA(LPCSTR lpRoot, LPSTR lpVolumeName, DWORD nVolumeNameSize, 
                                     LPDWORD lpVolumeSerial, LPDWORD lpMaxComponentLength,
                                     LPDWORD lpFileSystemFlags, LPSTR lpFileSystemName, DWORD nFileSystemNameSize) {
    BOOL ret = oGetVolumeInfo(lpRoot, lpVolumeName, nVolumeNameSize, lpVolumeSerial, 
                               lpMaxComponentLength, lpFileSystemFlags, lpFileSystemName, nFileSystemNameSize);
    
    if (lpVolumeSerial) {
        *lpVolumeSerial = 0x12345678; // Fake serial
    }
    return ret;
}
```

### Time Trial Bypass
```cpp
// Hook GetSystemTime
typedef VOID (WINAPI* pGetSystemTime)(LPSYSTEMTIME);
pGetSystemTime oGetSystemTime;

VOID WINAPI hkGetSystemTime(LPSYSTEMTIME lpSystemTime) {
    oGetSystemTime(lpSystemTime);
    lpSystemTime->wYear = 2025; // Freeze time at 2025
    lpSystemTime->wMonth = 1;
    lpSystemTime->wDay = 1;
}
```

## Pitfalls
1. **Code obfuscation** - Virtualized code (VMProtect) very hard to crack
2. **Online validation** - Server-side checks can't be fully bypassed
3. **Anti-tamper** - Apps check their own integrity
4. **Legal risks** - Cracking commercial software is illegal
5. **Updates break patch** - Need to re-crack after app updates

## Verification
```bash
# Test cracked app
./target_app_cracked

# Check if premium features unlocked
# Check if trial period bypassed
# Test without internet (if online check)
```

## Related Skills
- reverse-engineering-gokil
- frida-runtime-hooking
- apk-vvvip-modding