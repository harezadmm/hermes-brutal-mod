---
name: lua-deobfuscation
description: Deobfuscate commercial Lua obfuscators (MoonVeil, Luraph).
version: 1.0.0
triggers:
  - Lua script obfuscation
  - MoonVeil deobfuscation
  - Encrypted Lua strings
  - Obfuscated Roblox scripts
  - Commercial Lua obfuscators
category: security
tags:
  - lua
  - deobfuscation
  - reverse-engineering
  - moonveil
  - string-decryption
related_skills:
  - reverse-engineering-gokil
---

# Lua Script Deobfuscation

Deobfuscate commercial Lua obfuscators: MoonVeil, Luraph, Ironbrew, PSU (Pro Script Utilities). Common in Roblox exploit scripts and protected Lua codebases.

## When to Use

- User provides obfuscated Lua script (minified single line, random variable names)
- Script contains encrypted string patterns like `Kb('\\206\\186','\\25')`
- References commercial obfuscator (MoonVeil, Luraph, Ironbrew)
- User requests "decode", "deobfuscate", "decrypt", or "unpack" Lua source

## MoonVeil Obfuscator (v1.4+)

### Key Pattern Recognition

```lua
-- Header comment
-- This script was generated using the MoonVeil Obfuscator v1.4.5

-- First line: variable mappings
local xe,Kd,ed,Wc = type,bit32.bxor,getmetatable,pairs

-- String decoder function (name varies: Kb, decode, etc)
Kb = function(Fc,Ed)
  -- XOR decryption logic
end

-- Encrypted strings throughout
local x = Kb('\\206\\186\\25', '\\b\\128')
```

### Critical Discovery: Decimal Byte Escapes

**MoonVeil uses DECIMAL byte values in `\ddd` escapes, NOT octal.**

Standard Lua: `\ddd` is octal (max `\377` = 255 decimal)  
MoonVeil: `\ddd` is decimal (`\186` = byte 186 directly)

This breaks 70%+ of strings if you assume octal parsing. Values like `\186`, `\206`, `\248`, `\255` are DECIMAL.

### Deobfuscation Steps

#### Step 1: Parse Lua String Literals (Decimal Escapes)

```python
def parse_lua_string(code, start):
    """Parse Lua string from position, handling DECIMAL escapes"""
    if code[start] not in ["'", '"']:
        return None, start
    
    quote = code[start]
    result = []
    i = start + 1
    
    while i < len(code):
        if code[i] == quote:
            return bytes(result), i + 1
        
        elif code[i] == '\\' and i + 1 < len(code):
            i += 1
            ch = code[i]
            
            if ch.isdigit():
                # Numeric escape - collect up to 3 digits
                num = ''
                while i < len(code) and code[i].isdigit() and len(num) < 3:
                    num += code[i]
                    i += 1
                
                # DECIMAL not octal
                val = int(num, 10)
                if val <= 255:
                    result.append(val)
                    continue
            
            # Standard escapes
            elif ch == 'n': result.append(ord('\n'))
            elif ch == 't': result.append(ord('\t'))
            elif ch == 'r': result.append(ord('\r'))
            elif ch == '\\': result.append(ord('\\'))
            elif ch in ["'", '"']: result.append(ord(ch))
            else: result.append(ord(ch))
            
            i += 1
        else:
            result.append(ord(code[i]))
            i += 1
    
    return None, start  # Unterminated
```

#### Step 2: Extract Decoder Calls

Character-by-character parsing (regex fails on escape sequences):

```python
def extract_decoder_calls(code, func_name='Kb'):
    """Extract all decoder function calls with positions"""
    calls = []
    i = 0
    
    while i < len(code):
        pos = code.find(f'{func_name}(', i)
        if pos == -1:
            break
        
        start_pos = pos
        i = pos + len(func_name) + 1
        
        # Skip whitespace
        while i < len(code) and code[i] in ' \t\n':
            i += 1
        
        # Parse first string argument
        str1, end1 = parse_lua_string(code, i)
        if str1 is None:
            i = pos + 3
            continue
        
        # Skip comma
        i = end1
        while i < len(code) and code[i] in ' ,\t\n':
            i += 1
        
        # Parse second string argument
        str2, end2 = parse_lua_string(code, i)
        if str2 is None:
            i = pos + 3
            continue
        
        # Check closing paren
        i = end2
        while i < len(code) and code[i] in ' \t\n':
            i += 1
        
        if i < len(code) and code[i] == ')':
            end_pos = i + 1
            calls.append({
                'start': start_pos,
                'end': end_pos,
                'bytes1': str1,
                'bytes2': str2,
                'original': code[start_pos:end_pos]
            })
            i += 1
        else:
            i = pos + 3
    
    return calls
```

#### Step 3: XOR Decode Strings

```python
def xor_decode(bytes1, bytes2):
    """XOR decode with cycling key"""
    if not bytes2:
        return bytes1
    
    result = []
    for i, b in enumerate(bytes1):
        key_byte = bytes2[i % len(bytes2)]
        result.append(b ^ key_byte)
    
    return bytes(result)
```

#### Step 4: Replace in Source

```python
# Decode all calls
decoded_map = []
for call in decoder_calls:
    decoded_bytes = xor_decode(call['bytes1'], call['bytes2'])
    decoded_str = decoded_bytes.decode('utf-8', errors='replace')
    
    # Create Lua string literal
    escaped = decoded_str.replace('\\', '\\\\').replace("'", "\\'")
    replacement = f"'{escaped}'"
    
    decoded_map.append({
        'pos': (call['start'], call['end']),
        'replacement': replacement
    })

# Replace backwards to preserve positions
deobfuscated = code
for item in reversed(decoded_map):
    start, end = item['pos']
    deobfuscated = deobfuscated[:start] + item['replacement'] + deobfuscated[end:]
```

#### Step 5: Variable Renaming

Extract variable mappings from first line:

```python
# Pattern: local a,b,c,d = builtin1,builtin2,builtin3,builtin4
var_map = {
    'xe': 'type',
    'Kd': 'bit32_bxor',
    'ed': 'getmetatable',
    'Wc': 'pairs',
    # Extract more from Ya['module']['func'] patterns
}

# Replace with word boundaries
for old_var in sorted(var_map.keys(), key=len, reverse=True):
    new_var = var_map[old_var]
    pattern = r'\b' + re.escape(old_var) + r'\b'
    deobfuscated = re.sub(pattern, new_var, deobfuscated)
```

## Typical Results

**Input:**
- 194KB minified single-line Lua
- 165 encrypted string calls
- All variables 1-3 chars

**Output:**
- 197KB readable source
- 1700+ formatted lines
- 165/165 strings decoded (100%)
- Builtin functions visible
- Main logic identifiable

**Time:** ~5 minutes (includes parser debugging iterations)

## Other Obfuscators

### Luraph
- Similar XOR pattern
- May use octal escapes (standard Lua)
- Stronger VM obfuscation
- Decoder function name varies

### Ironbrew
- Older, simpler
- Base64 + XOR layers
- Less control flow obfuscation
- Easier to crack

### PSU (Pro Script Utilities)
- Variable obfuscation only
- No string encryption
- Minification focused

## Pitfalls

1. **Assuming Octal:** MoonVeil's decimal escapes will fail 70% of strings. Always try decimal first.

2. **Regex Extraction:** Backslash escapes break regex. Must parse character-by-character.

3. **Control Flow Remains:** String + variable deobfuscation makes code readable, but state machine logic (`lc=P[14840]or S(...)`) stays obfuscated. That's expected - full VM deobfuscation requires bytecode analysis.

4. **Hardcoded XOR Keys:** Decoder functions have session-specific keys (e.g., 63785, 46458). If different keys appear, the pattern still holds - just different constants.

5. **Incomplete Decoding:** Some binary data (like embedded bytecode) won't decode to UTF-8. Mark those as `[binary]` and keep original.

## Success Indicators

- ✅ All decoder calls replaced with string literals
- ✅ Builtin function names visible (`string.char`, `bit32.bxor`, `table.concat`)
- ✅ Valid Lua syntax (`luac -p` passes)
- ✅ Function boundaries identifiable
- ✅ Main execution flow traceable

## Tools Required

- Python 3.11+ (no external deps)
- Optional: Lua interpreter for validation

## Verification

```bash
# Check syntax
luac -p deobfuscated.lua

# Compare structure
wc -l original.lua deobfuscated.lua

# Grep for decoder calls (should be 0)
grep -c 'Kb(' deobfuscated.lua
```

## Next Steps After Deobfuscation

Once strings decoded and variables renamed:
1. **Trace entry point** - find main execution (usually at end)
2. **Identify key functions** - look for game interaction, HTTP calls, crypto
3. **Map control flow** - state machine variables (lc, state, etc)
4. **Extract embedded data** - Base64 blobs, bytecode chunks
5. **Test modifications** - inject logging, change behavior
