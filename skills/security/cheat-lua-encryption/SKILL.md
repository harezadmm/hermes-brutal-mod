---
name: cheat-lua-encryption
description: Encrypt/decrypt game cheats and Lua scripts.
tags: [lua, encryption, obfuscation, game-hacking, protection]
version: 1.0
author: RedMess
license: MIT
---

# Cheat & Lua Encryption/Decryption

## When to Use
Use when encrypting game cheats or Lua scripts to bypass detection, or decrypting obfuscated Lua code.

## Lua Script Encryption

### Simple XOR Encryption
```lua
-- encrypt.lua
function xor_encrypt(data, key)
    local result = {}
    for i = 1, #data do
        local byte = string.byte(data, i)
        local key_byte = string.byte(key, ((i - 1) % #key) + 1)
        table.insert(result, string.char(bit32.bxor(byte, key_byte)))
    end
    return table.concat(result)
end

-- Usage
local script = [[
gg.searchNumber("1000", gg.TYPE_DWORD)
gg.refineNumber("900", gg.TYPE_DWORD)
local r = gg.getResults(10)
for i,v in ipairs(r) do v.value = "999999" end
gg.setValues(r)
]]

local key = "MySecretKey123"
local encrypted = xor_encrypt(script, key)
print("Encrypted:", encrypted)

-- Decrypt and execute
local decrypted = xor_encrypt(encrypted, key) -- XOR is reversible
load(decrypted)()
```

### AES Encryption (Using LuaCrypto)
```lua
-- aes_encrypt.lua
local crypto = require("crypto")

function aes_encrypt(plaintext, key)
    local cipher = crypto.encrypt("aes-256-cbc", plaintext, key, key:sub(1,16))
    return crypto.hex(cipher)
end

function aes_decrypt(ciphertext, key)
    local raw = crypto.unhex(ciphertext)
    return crypto.decrypt("aes-256-cbc", raw, key, key:sub(1,16))
end

-- Usage
local script = "gg.searchNumber('1000', gg.TYPE_DWORD)"
local key = "SuperSecretKey1234567890123456" -- 32 bytes for AES-256
local enc = aes_encrypt(script, key)
print("Encrypted (hex):", enc)

local dec = aes_decrypt(enc, key)
load(dec)()
```

## Lua Bytecode Compilation
```bash
# Compile Lua to bytecode (harder to reverse)
luac -o cheat_encrypted.luac cheat.lua

# Load bytecode in GameGuardian
local chunk = load(io.open("cheat_encrypted.luac", "rb"):read("*a"))
chunk()
```

## Cheat DLL Encryption (Windows)

### RC4 Encrypt C++ Cheat
```cpp
// rc4.cpp
#include <vector>
#include <string>

std::vector<unsigned char> rc4(const std::vector<unsigned char>& data, const std::string& key) {
    std::vector<unsigned char> S(256);
    std::vector<unsigned char> result;
    
    // KSA
    for (int i = 0; i < 256; i++) S[i] = i;
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % key.length()]) % 256;
        std::swap(S[i], S[j]);
    }
    
    // PRGA
    int i = 0; j = 0;
    for (size_t n = 0; n < data.size(); n++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        std::swap(S[i], S[j]);
        result.push_back(data[n] ^ S[(S[i] + S[j]) % 256]);
    }
    return result;
}

// Encrypt cheat function code at runtime
void ExecuteEncryptedCheat() {
    std::string key = "CheatKey2024";
    std::vector<unsigned char> encrypted_code = {/* encrypted shellcode */};
    
    auto decrypted = rc4(encrypted_code, key);
    
    // Allocate executable memory
    LPVOID exec = VirtualAlloc(NULL, decrypted.size(), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(exec, decrypted.data(), decrypted.size());
    
    // Execute
    ((void(*)())exec)();
}
```

## Lua Deobfuscation

### Luraph Deobfuscator
```python
# luraph_decrypt.py
import re

def deobfuscate_luraph(code):
    # Remove junk strings
    code = re.sub(r'local [a-z]+ = ""[^;]+;', '', code)
    
    # Decode string table
    strings = re.findall(r'"([^"]+)"', code)
    for i, s in enumerate(strings):
        code = code.replace(f'_G[{i}]', f'"{s}"')
    
    # Simplify variable names
    vars = {}
    for match in re.finditer(r'local ([a-z_]+) = ', code):
        if match.group(1) not in vars:
            vars[match.group(1)] = f'var{len(vars)}'
    
    for old, new in vars.items():
        code = code.replace(old, new)
    
    return code

# Usage
with open("obfuscated.lua", "r") as f:
    obf_code = f.read()

clean = deobfuscate_luraph(obf_code)
with open("deobfuscated.lua", "w") as f:
    f.write(clean)
```

### Ironbrew Decompiler
```bash
# Clone decompiler
git clone https://github.com/Rerumu/Ironbrew-Deobfuscator
cd Ironbrew-Deobfuscator

# Deobfuscate
lua main.lua input.lua output.lua
```

## Advanced: Polymorphic Lua Loader
```lua
-- polymorphic_loader.lua
function generate_loader(encrypted_script, key)
    local template = [[
local k,e,r="%s","%s",{}
for i=1,#e,2 do 
    local b=tonumber(e:sub(i,i+1),16)
    local kb=k:byte(((i-1)/2%%#k)+1)
    r[#r+1]=string.char(bit32.bxor(b,kb))
end
load(table.concat(r))()
]]
    
    -- Generate random variable names
    local vars = {"k","e","r"}
    for i=1,#vars do
        local new_var = string.char(math.random(97,122))..math.random(100,999)
        template = template:gsub(vars[i], new_var)
    end
    
    return string.format(template, key, encrypted_script)
end

-- Usage: Creates different loader code each time
local enc_script = "48656C6C6F" -- hex encoded
local loader1 = generate_loader(enc_script, "key1")
local loader2 = generate_loader(enc_script, "key1") -- Different code, same result
```

## String Obfuscation for Cheats
```cpp
// obfuscated_strings.h
#define OBFUSCATE(str) []() { \
    constexpr auto encrypted = xor_compile_time(str); \
    return xor_runtime(encrypted); \
}()

// Usage in cheat
const char* cheat_name = OBFUSCATE("MyAwesomeCheat");
const char* proc_name = OBFUSCATE("game.exe");
```

## Pitfalls
1. **XOR detected easily** - Use AES/ChaCha20 for better security
2. **Hardcoded keys** - Store keys remotely or use key derivation
3. **Bytecode still reversible** - Combine with VM protection
4. **Static analysis** - Use runtime decryption only

## Verification
```bash
# Test encryption/decryption
lua encrypt.lua && lua decrypt.lua

# Check if obfuscated Lua runs
lua obfuscated.lua
```

## Related Skills
- lua-deobfuscation
- game-cheat-development
- reverse-engineering-gokil