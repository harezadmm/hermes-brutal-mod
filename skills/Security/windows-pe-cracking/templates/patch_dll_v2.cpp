// Advanced DLL injection patch with API hooking + memory patching
// Bypasses anti-tamper by patching RAM only, leaves file untouched

#include <windows.h>
#include <psapi.h>
#include <stdio.h>

// Hook for MessageBoxW - suppress error dialogs
typedef int (WINAPI* MessageBoxW_t)(HWND, LPCWSTR, LPCWSTR, UINT);
MessageBoxW_t OriginalMessageBoxW = NULL;

int WINAPI HookedMessageBoxW(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType) {
    wprintf(L"[HOOK] MessageBoxW intercepted\n");
    wprintf(L"  Caption: %s\n", lpCaption ? lpCaption : L"(null)");
    wprintf(L"  Text: %s\n", lpText ? lpText : L"(null)");
    
    // Block error messages (key not found, invalid, etc)
    if (lpText && (wcsstr(lpText, L"encontrada") || wcsstr(lpText, L"invalid") || 
                   wcsstr(lpText, L"error") || wcsstr(lpText, L"fail"))) {
        printf("  [BYPASS] Error dialog blocked!\n");
        return IDOK;
    }
    
    return OriginalMessageBoxW(hWnd, lpText, lpCaption, uType);
}

// IAT hook installation
BOOL HookFunction(LPCSTR moduleName, LPCSTR functionName, LPVOID hookFunction, LPVOID* originalFunction) {
    HMODULE hModule = GetModuleHandleA(moduleName);
    if (!hModule) return FALSE;
    
    FARPROC targetFunc = GetProcAddress(hModule, functionName);
    if (!targetFunc) return FALSE;
    
    *originalFunction = (LPVOID)targetFunc;
    
    HMODULE hMainModule = GetModuleHandle(NULL);
    MODULEINFO modInfo;
    GetModuleInformation(GetCurrentProcess(), hMainModule, &modInfo, sizeof(modInfo));
    
    PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)hMainModule;
    PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((BYTE*)hMainModule + dosHeader->e_lfanew);
    PIMAGE_IMPORT_DESCRIPTOR importDesc = (PIMAGE_IMPORT_DESCRIPTOR)((BYTE*)hMainModule + 
        ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
    
    while (importDesc->Name) {
        char* dllName = (char*)((BYTE*)hMainModule + importDesc->Name);
        
        if (_stricmp(dllName, moduleName) == 0) {
            PIMAGE_THUNK_DATA thunk = (PIMAGE_THUNK_DATA)((BYTE*)hMainModule + importDesc->FirstThunk);
            
            while (thunk->u1.Function) {
                LPVOID* funcAddr = (LPVOID*)&thunk->u1.Function;
                
                if (*funcAddr == targetFunc) {
                    DWORD oldProtect;
                    VirtualProtect(funcAddr, sizeof(LPVOID), PAGE_READWRITE, &oldProtect);
                    *funcAddr = hookFunction;
                    VirtualProtect(funcAddr, sizeof(LPVOID), oldProtect, &oldProtect);
                    return TRUE;
                }
                thunk++;
            }
        }
        importDesc++;
    }
    
    return FALSE;
}

// Aggressive memory patching - NOP all conditional jumps
void PatchValidationLogic() {
    HMODULE hMainModule = GetModuleHandle(NULL);
    MODULEINFO modInfo;
    GetModuleInformation(GetCurrentProcess(), hMainModule, &modInfo, sizeof(modInfo));
    
    BYTE* baseAddr = (BYTE*)hMainModule;
    SIZE_T moduleSize = modInfo.SizeOfImage;
    
    int patches = 0;
    
    // NOP all JE/JNE (74/75) conditional jumps
    for (SIZE_T i = 0; i < moduleSize - 2; i++) {
        if (baseAddr[i] == 0x74 || baseAddr[i] == 0x75) {
            DWORD oldProtect;
            if (VirtualProtect(&baseAddr[i], 2, PAGE_EXECUTE_READWRITE, &oldProtect)) {
                baseAddr[i] = 0x90;   // NOP
                baseAddr[i+1] = 0x90;
                VirtualProtect(&baseAddr[i], 2, oldProtect, &oldProtect);
                patches++;
            }
        }
    }
    
    printf("[+] Applied %d jump patches\n", patches);
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        
        AllocConsole();
        FILE* f;
        freopen_s(&f, "CONOUT$", "w", stdout);
        
        printf("═══════════════════════════════════════\n");
        printf("  AUTH BYPASS DLL v2.0\n");
        printf("  API Hook + Memory Patch\n");
        printf("═══════════════════════════════════════\n\n");
        
        printf("[*] Installing API hooks...\n");
        if (HookFunction("user32.dll", "MessageBoxW", (LPVOID)HookedMessageBoxW, (LPVOID*)&OriginalMessageBoxW)) {
            printf("[+] MessageBoxW hooked\n");
        }
        
        printf("\n[*] Patching validation logic...\n");
        PatchValidationLogic();
        
        printf("\n[+] All patches applied!\n");
        printf("[!] Try authentication now\n");
        printf("═══════════════════════════════════════\n\n");
    }
    
    return TRUE;
}
