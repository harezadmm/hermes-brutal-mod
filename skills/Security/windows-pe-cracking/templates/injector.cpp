// DLL Injector - Launches target exe and injects patch DLL
// Usage: Place injector.exe, patch.dll, and target.exe in same folder

#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>
#include <string.h>

BOOL InjectDLL(DWORD pid, const char* dllPath) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        printf("[-] Failed to open process (Error: %lu)\n", GetLastError());
        return FALSE;
    }
    
    SIZE_T len = strlen(dllPath) + 1;
    LPVOID mem = VirtualAllocEx(hProcess, NULL, len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
    if (!mem) {
        printf("[-] Failed to allocate memory\n");
        CloseHandle(hProcess);
        return FALSE;
    }
    
    if (!WriteProcessMemory(hProcess, mem, dllPath, len, NULL)) {
        printf("[-] Failed to write DLL path\n");
        VirtualFreeEx(hProcess, mem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }
    
    HMODULE hKernel = GetModuleHandleA("kernel32.dll");
    LPVOID loadLib = GetProcAddress(hKernel, "LoadLibraryA");
    
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, 
        (LPTHREAD_START_ROUTINE)loadLib, mem, 0, NULL);
    
    if (!hThread) {
        printf("[-] Failed to create remote thread (Error: %lu)\n", GetLastError());
        VirtualFreeEx(hProcess, mem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }
    
    WaitForSingleObject(hThread, INFINITE);
    
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, mem, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    
    return TRUE;
}

int main(int argc, char* argv[]) {
    printf("═══════════════════════════════════════════════════\n");
    printf("  DLL INJECTOR v1.0\n");
    printf("  Runtime Authentication Bypass\n");
    printf("═══════════════════════════════════════════════════\n\n");
    
    // Usage: injector.exe <target.exe> or default to app.exe
    const char* targetExe = (argc > 1) ? argv[1] : "app.exe";
    
    // Get full path to DLL
    char dllPath[MAX_PATH];
    GetCurrentDirectoryA(MAX_PATH, dllPath);
    strcat_s(dllPath, MAX_PATH, "\\patch.dll");
    
    // Check if DLL exists
    if (GetFileAttributesA(dllPath) == INVALID_FILE_ATTRIBUTES) {
        printf("[-] Error: patch.dll not found!\n");
        printf("    Make sure patch.dll is in the same folder.\n\n");
        system("pause");
        return 1;
    }
    
    printf("[+] DLL Path: %s\n", dllPath);
    printf("[+] Target: %s\n\n", targetExe);
    
    // Launch target exe suspended
    printf("[*] Launching %s...\n", targetExe);
    
    STARTUPINFOA si = {sizeof(si)};
    PROCESS_INFORMATION pi;
    
    if (!CreateProcessA(
        targetExe,
        NULL, NULL, NULL, FALSE,
        CREATE_SUSPENDED,
        NULL, NULL, &si, &pi
    )) {
        printf("[-] Failed to launch %s\n", targetExe);
        printf("    Make sure the exe is in the same folder!\n\n");
        system("pause");
        return 1;
    }
    
    printf("[+] Process created (PID: %lu)\n", pi.dwProcessId);
    printf("[*] Injecting patch DLL...\n");
    
    // Small delay to ensure process is ready
    Sleep(500);
    
    if (InjectDLL(pi.dwProcessId, dllPath)) {
        printf("[+] DLL injected successfully!\n");
        printf("[*] Resuming process...\n\n");
        
        ResumeThread(pi.hThread);
        
        printf("═══════════════════════════════════════════════════\n");
        printf("  %s is running with authentication bypass!\n", targetExe);
        printf("  Check the console window from patch.dll for details.\n");
        printf("═══════════════════════════════════════════════════\n\n");
    } else {
        printf("[-] Injection failed!\n");
        TerminateProcess(pi.hProcess, 1);
    }
    
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    
    printf("Press any key to exit...\n");
    system("pause > nul");
    
    return 0;
}
