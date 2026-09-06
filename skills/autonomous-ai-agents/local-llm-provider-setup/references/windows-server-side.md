# Windows Server-Side Recipe (Ollama + OpenSSH)

Run these ON the user's Windows machine (they paste the commands; send cmd-compatible versions first, PowerShell only if they confirm a PS prompt).

## 1. OpenSSH Server

```cmd
DISM /Online /Add-Capability /CapabilityName:OpenSSH.Server~~~~0.0.1.0
net start sshd
sc config sshd start=auto
netsh advfirewall firewall add rule name="SSH Server" dir=in action=allow protocol=TCP localport=22
```

DISM shows no progress bar while downloading — check state with `powershell -command "Get-WindowsCapability -Online -Name OpenSSH*"`; if `Staged`, re-run the DISM command to finish to `Installed`.

## 2. Key auth (admin account)

```cmd
mkdir C:\Users\<user>\.ssh
echo ssh-ed25519 AAAA... hermes-agent> C:\Users\<user>\.ssh\authorized_keys
echo ssh-ed25519 AAAA... hermes-agent> C:\ProgramData\ssh\administrators_authorized_keys
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "SYSTEM:F" /grant "BUILTIN\Administrators:F"
net stop sshd && net start sshd
```

Test from the agent side: `ssh user@<tailscale-ip> "hostname && whoami"`.

## 3. Ollama exposure

```cmd
setx OLLAMA_HOST 0.0.0.0
setx OLLAMA_CONTEXT_LENGTH 65536
taskkill /f /im "ollama app.exe" & taskkill /f /im ollama.exe
schtasks /create /tn OllamaServe /tr "C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe serve" /sc onlogon /rl highest /f
schtasks /run /tn OllamaServe
```

Verify on the box: `netstat -ano | findstr 11434` must show `0.0.0.0:11434`.

## 4. Model pull

Find the exact registry name first (vendor prefixes differ from HF names — e.g. `huihui_ai/qwen3-abliterated:8b`); confirm the manifest URL returns 200 before pulling, then `ollama pull <name>` and smoke-test generate speed.
