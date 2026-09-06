# DLL Injection Templates for Anti-Tamper Bypass

Complete working C++ templates for runtime memory patching when static patches fail.

## Patch DLL (twn_patch.cpp)

```cpp
#include <windows.h>
#include <psapi.h>
#include <stdio.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        
        AllocConsole();
        FILE* f;
        freopen_s(&f, "CONOUT$", "w", stdout);
        
        printf("=== AUTH BYPASS DLL ===\n");
        
        HMODULE hMainModule = GetModuleHandle(NULL);
        MODULEINFO modInfo;
        GetModuleInformation(GetCurrentProcess(), hMainModule, &modInfo, sizeof(modInfo));
        
        BYTE* baseAddr = (BYTE*)hMainModule;
        SIZE_T moduleSize = modInfo.SizeOfImage;
        
        int patches = 0;
        
        // Pattern: TEST EAX,EAX; JE → patch JE to JMP
        for (SIZE_T i = 0; i < moduleSize - 4; i++) {
            if (baseAddr[i] == 0x85 && baseAddr[i+1] == 0xC0 && baseAddr[i+2] == 0x74) {
                DWORD oldProtect;
                if (VirtualProtect(&baseAddr[i+2], 2, PAGE_EXECUTE_READWRITE, &oldProtect)) {
                    baseAddr[i+2] = 0xEB; // JE → JMP
                    VirtualProtect(&baseAddr[i+2], 2, oldProtect, &oldProtect);
                    patches++;
                }
            }
        }
        
        printf("[+] Applied %d patches\n", patches);
    }
    return TRUE;
}
```

## Injector (twn_injector.cpp)

```cpp
#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>

BOOL InjectDLL(DWORD processId, const char* dllPath) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
    if (!hProcess) return FALSE;
    
    SIZE_T dllPathLen = strlen(dllPath) + 1;
    LPVOID remoteMem = VirtualAllocEx(hProcess, NULL, dllPathLen, 
                                      MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
    WriteProcessMemory(hProcess, remoteMem, dllPath, dllPathLen, NULL);
    
    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    LPVOID loadLibraryAddr = (LPVOID)GetProcAddress(hKernel32, "LoadLibraryA");
    
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, 
                                       (LPTHREAD_START_ROUTINE)loadLibraryAddr, 
                                       remoteMem, 0, NULL);
    
    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    
    return TRUE;
}

int main() {
    printf("=== INJECTOR ===\n");
    
    char dllPath[MAX_PATH];
    GetCurrentDirectoryA(MAX_PATH, dllPath);
    strcat_s(dllPath, MAX_PATH, "\\patch.dll");
    
    STARTUPINFOA si = {sizeof(si)};
    PROCESS_INFORMATION pi;
    
    if (!CreateProcessA("target.exe", NULL, NULL, NULL, FALSE,
                       CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        printf("[-] Failed to launch\n");
        return 1;
    }
    
    Sleep(500);
    
    if (InjectDLL(pi.dwProcessId, dllPath)) {
        printf("[+] DLL injected\n");
        ResumeThread(pi.hThread);
    }
    
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}
```

## Compile

```bash
x86_64-w64-mingw32-g++ -shared -o patch.dll twn_patch.cpp -lpsapi -static-libgcc -static-libstdc++
x86_64-w64-mingw32-g++ -o injector.exe twn_injector.cpp -static-libgcc -static-libstdc++
```

## Usage

1. Place `injector.exe`, `patch.dll`, `target.exe` in same folder
2. Run `injector.exe`
3. Target launches with patches applied in memory
4. Original exe file remains unmodified
