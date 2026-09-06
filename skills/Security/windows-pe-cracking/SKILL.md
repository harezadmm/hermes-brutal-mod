---
name: windows-pe-cracking
description: Crack Windows PE to bypass auth or unlock features.
tags: [windows, pe, cracking, reverse-engineering, dll-injection, anti-tamper]
---

# Windows PE Cracking

Reverse engineer and crack Windows PE executables to bypass authentication, remove license checks, or unlock premium features.

## When to Use

- User wants to bypass login/key validation in Windows .exe
- Need to unlock paid features or remove trial limitations
- Static patches cause crashes (anti-tamper protection)
- Need runtime memory patching to bypass integrity checks

## Analysis Phase

### 1. Initial Reconnaissance

```bash
# Check file type and properties
file app.exe
strings app.exe | grep -iE 'license|key|trial|premium'

# PE structure analysis
pip install pefile
python3 << EOF
import pefile
pe = pefile.PE('app.exe')

# Check if packed
for section in pe.sections:
    entropy = section.get_entropy()
    print(f"{section.Name.decode().strip()}: entropy {entropy:.2f}")
    if entropy > 7.0:
        print("  ⚠️ Possibly packed/encrypted")

# Check imports
if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        print(f"\n{entry.dll.decode()}:")
        for imp in entry.imports[:10]:
            if imp.name:
                print(f"  {imp.name.decode()}")
EOF
```

### 2. Identify Protection Type

**Self-extracting archive:**
- High `.rdata` section entropy (>7.5)
- Error strings like "couldn't decode attached data"
- Use binwalk to find embedded payloads
- Extract real executable before patching

**Anti-tamper protection:**
- Checksum validation at startup
- Window creation fails (MainWindowHandle=0) after patch
- Process runs but GUI never appears
- → **Use runtime injection instead of static patching**

**Server-side validation:**
- Error messages in foreign languages ("Chave não encontrada")
- Network traffic during key check
- No hardcoded valid keys in binary
- → **Cannot keygen; must bypass client-side check**

## Cracking Approaches

### Approach 1: Static Patching (Simple Cases)

```python
import pefile

exe_path = "app.exe"
output = "app_cracked.exe"

with open(exe_path, 'rb') as f:
    data = bytearray(f.read())

pe = pefile.PE(exe_path)
text_section = next(s for s in pe.sections if b'.text' in s.Name)
text_start = text_section.PointerToRawData
text_end = text_start + text_section.SizeOfRawData

patches = 0

# Pattern: CMP + JNE → NOP the JNE
for i in range(text_start, text_end - 6):
    if data[i] == 0x3D:  # CMP EAX, imm32
        if data[i+5] in [0x75, 0x0F]:  # JNE
            data[i+5] = 0x90
            data[i+6] = 0x90
            patches += 1

# Fix checksum
pe_new = pefile.PE(data=bytes(data))
pe_new.OPTIONAL_HEADER.CheckSum = pe_new.generate_checksum()

with open(output, 'wb') as f:
    f.write(pe_new.write())

print(f"Applied {patches} patches")
```

**Test:** Check MainWindowHandle with PowerShell:
```powershell
Get-Process | Where {$_.ProcessName -like '*app*'} | Select MainWindowHandle
```
If MainWindowHandle = 0 → GUI init failed, use Approach 3

### Approach 2: Keygen (Offline Validation)

```python
with open('app.exe', 'rb') as f:
    data = f.read()

# Find key patterns
key_patterns = [b'KEY', b'License', b'Serial']
for pattern in key_patterns:
    offset = data.find(pattern)
    if offset != -1:
        context = data[offset-50:offset+100]
        print(f"{pattern} @ {hex(offset)}")

# Generate candidates
import hashlib
seeds = ["AppName", "Version", "Author"]
for seed in seeds:
    key = hashlib.md5(seed.encode()).hexdigest()[:16].upper()
    print(f"{seed} → {key}")
```

**If server-side validation:** Keygen won't work. Use Approach 3.

### Approach 3: Runtime Memory Patching (Anti-tamper Bypass)

**When to use:** Static patches crash or GUI fails to appear.

See `templates/patch.cpp` and `templates/injector.cpp` for complete DLL injection solution.

**Compile:**
```bash
x86_64-w64-mingw32-g++ -shared -o patch.dll patch.cpp -lpsapi -static
x86_64-w64-mingw32-g++ -o injector.exe injector.cpp -static
```

**Use:**
```bash
# Place injector.exe, patch.dll, app.exe in same folder
./injector.exe
```

## Pitfalls

**Self-extracting archives misidentified as standalone apps**
- Symptom: File is 20MB+, high `.rdata` entropy
- Impact: Patching wrapper crashes; real app extracted to temp at runtime
- Fix: Use binwalk to extract, or monitor temp folders during launch
- Check: `7z l app.exe` — if it lists files, it's a wrapper

**Static patches cause GUI failure (MainWindowHandle=0)**
- Symptom: Process in Task Manager but no window
- Root cause: Anti-tamper killed GUI init
- Fix: Use runtime injection — patches RAM only, file stays clean

**Over-patching critical code paths**
- Symptom: Exe crashes or hangs
- Cause: Patched 500+ jumps including critical logic
- Fix: Conservative patching — only CMP+JNE in validation context
- Test incrementally: 10-20 patches, test, repeat

**Keygen with server-side validation**
- Symptom: All keys fail with "Key not found"
- Fix: Cannot keygen; must bypass client check or use injection

**Checksum validation breaks patched exe**
- Fix: Recalculate checksum:
  ```python
  pe.OPTIONAL_HEADER.CheckSum = pe.generate_checksum()
  ```

## Tools

- **pefile** — PE structure analysis
- **binwalk** — Extract embedded files
- **strings** — Quick reconnaissance
- **x86_64-w64-mingw32-g++** — Compile Windows tools from Linux
- **7-Zip** — Check if self-extracting archive
