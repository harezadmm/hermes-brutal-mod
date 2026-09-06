// TWN Authentication Bypass DLL
// Runtime memory patcher - patches validation checks in RAM

#include <windows.h>
#include <psapi.h>
#include <stdio.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        
        // Create console for debugging
        AllocConsole();
        FILE* f;
        freopen_s(&f, "CONOUT$", "w", stdout);
        
        printf("═══════════════════════════════════════\n");
        printf("  AUTH BYPASS DLL v1.0\n");
        printf("  Runtime Memory Patcher\n");
        printf("═══════════════════════════════════════\n\n");
        
        // Get base address and size of main module
        HMODULE hMain = GetModuleHandle(NULL);
        MODULEINFO modInfo;
        GetModuleInformation(GetCurrentProcess(), hMain, &modInfo, sizeof(modInfo));
        
        BYTE* base = (BYTE*)hMain;
        SIZE_T size = modInfo.SizeOfImage;
        
        printf("[+] Main module: 0x%p\n", hMain);
        printf("[+] Module size: 0x%zX bytes\n", size);
        printf("[*] Scanning for validation patterns...\n\n");
        
        int patches = 0;
        
        // Pattern 1: TEST EAX, EAX; JE (85 C0 74 XX) → JMP (force pass)
        for (SIZE_T i = 0; i < size - 4; i++) {
            if (base[i] == 0x85 && base[i+1] == 0xC0 && base[i+2] == 0x74) {
                DWORD oldProtect;
                if (VirtualProtect(&base[i+2], 2, PAGE_EXECUTE_READWRITE, &oldProtect)) {
                    base[i+2] = 0xEB; // Change JE to JMP
                    VirtualProtect(&base[i+2], 2, oldProtect, &oldProtect);
                    patches++;
                    if (patches <= 5) {
                        printf("  [PATCH] TEST+JE → JMP @ 0x%p\n", base + i);
                    }
                }
            }
        }
        
        // Pattern 2: CMP EAX, 0; JNE (83 F8 00 75 XX) → NOP
        for (SIZE_T i = 0; i < size - 5; i++) {
            if (base[i] == 0x83 && base[i+1] == 0xF8 && 
                base[i+2] == 0x00 && base[i+3] == 0x75) {
                DWORD oldProtect;
                if (VirtualProtect(&base[i+3], 2, PAGE_EXECUTE_READWRITE, &oldProtect)) {
                    base[i+3] = 0x90; // NOP
                    base[i+4] = 0x90; // NOP
                    VirtualProtect(&base[i+3], 2, oldProtect, &oldProtect);
                    patches++;
                    if (patches <= 10) {
                        printf("  [PATCH] CMP+JNE → NOP @ 0x%p\n", base + i);
                    }
                }
            }
        }
        
        // Pattern 3: XOR EAX, EAX (33 C0) → MOV EAX, 1 (force success)
        // Only patch in validation context (followed by TEST/CMP within 10 bytes)
        for (SIZE_T i = 0; i < size - 12; i++) {
            if (base[i] == 0x33 && base[i+1] == 0xC0) {
                BOOL isValidation = FALSE;
                for (int j = 2; j < 12 && i+j < size; j++) {
                    if (base[i+j] == 0x85 || base[i+j] == 0x3B) {
                        isValidation = TRUE;
                        break;
                    }
                }
                
                if (isValidation) {
                    DWORD oldProtect;
                    if (VirtualProtect(&base[i], 5, PAGE_EXECUTE_READWRITE, &oldProtect)) {
                        base[i] = 0xB8;   // MOV EAX,
                        base[i+1] = 0x01; // 1
                        base[i+2] = 0x00;
                        base[i+3] = 0x00;
                        base[i+4] = 0x00;
                        VirtualProtect(&base[i], 5, oldProtect, &oldProtect);
                        patches++;
                        if (patches <= 15) {
                            printf("  [PATCH] XOR EAX → MOV EAX,1 @ 0x%p\n", base + i);
                        }
                    }
                }
            }
        }
        
        printf("\n[+] Applied %d patches\n", patches);
        printf("[+] Authentication should bypass!\n");
        printf("[!] Keep this console open for debugging\n");
        printf("═══════════════════════════════════════\n\n");
    }
    
    return TRUE;
}
