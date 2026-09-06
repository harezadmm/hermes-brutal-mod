---
name: local-llm-provider-setup
description: Use when pointing Hermes at a local or remote Ollama.
---

# Connecting Hermes to a Local/Remote LLM Backend

Goal: make a self-hosted model (e.g. Ollama on the user's own PC) usable as a Hermes model alias. The full chain is: server listens → network path → Hermes provider config → context-length alignment. Debug in that order.

## Procedure

1. **Verify the backend serves and knows its model.**
   - `curl http://<host>:11434/api/version` and `/api/tags`.
   - Ollama registry names have vendor prefixes that differ from HF repo names — query the registry manifest (HTTP 200 check) before pulling; e.g. abliterated models live under `huihui_ai/`, not the HF-style org name. A 404 on pull is almost always the name, not the network.
2. **Establish the network path.**
   - Hermes refuses plaintext HTTP to any non-loopback host (loopback-only guard). A remote LAN/Tailscale backend therefore needs an SSH tunnel: `ssh -N -L 11434:127.0.0.1:11434 user@host` in the background, then point Hermes at `http://127.0.0.1:11434/v1`.
   - Tunnel lifetime = session lifetime. Tell the user the alias silently dies when the tunnel does; re-establish on 'model not reachable' reports rather than re-debugging config.
   - Do NOT trust `setx OLLAMA_HOST 0.0.0.0` alone — confirm with `netstat`/`ss` on the server that it actually listens on the new interface; the running process must be restarted to pick up env changes.
3. **Configure Hermes via `custom_providers`, not a bare model_alias.**
   - Add a `custom_providers` entry: `name`, `base_url` (loopback URL from step 2), dummy `api_key` (local servers still want a non-empty bearer), and a `models` map with per-model `context_length`.
   - Then create the alias pointing at that provider/model. A per-model `context_length` inside `custom_providers` is the ONLY path that reliably reaches the runtime — a global `model.context_length` gets scoped to the default cloud model and is ignored for the alias.
4. **Align context length on both sides.**
   - Hermes enforces a ~64K minimum context floor (config values below it are rejected unless the provider is `lmstudio`/`custom`). For an 8B-class model that supports 128K, just set both sides to 65536 and move on.
   - Ollama truncates silently at ITS OWN default num_ctx (often 2K–32K) regardless of what the client requests. Set the server side to match: `OLLAMA_CONTEXT_LENGTH=65536` env for the serve process, or pass `num_ctx` in the API call.
5. **End-to-end test with a deterministic prompt.**
   - `hermes chat -q "Balas PERSIS satu kata: AKTIF" --model <alias>`.
   - Success proof: the reply plus visible model-specific reasoning style (e.g. Qwen3's reasoning block) confirms the request hit the local model, not a fallback. If output still smells like the default cloud model, the route didn't resolve — re-check which provider the alias resolved to before touching anything else.
   - Thinking-mode models can burn the whole budget on reasoning in short tests; use a bigger token budget or a no-think flag for real tests.

## Pitfalls

- Debug the ROUTE first, the CONTENT second: 'requests still go to the cloud provider' is a route-resolution problem; do not chase it by editing prompts or keys.
- When guided setup happens on the user's own Windows PC, prefer cmd-compatible one-liners (DISM, sc, netsh, schtasks) over PowerShell cmdlets — users pasting from a plain cmd prompt get 'not recognized' errors on PowerShell-only commands, and elevation errors mean they opened a non-admin terminal, not that the command is wrong.
- Windows autostart for Ollama: the GUI tray app fails in non-interactive/scheduled contexts; register the CLI `ollama.exe serve` via `schtasks /create /sc onlogon /rl highest` instead.
- SSH key auth to Windows OpenSSH: admin accounts validate keys against `C:\ProgramData\ssh\administrators_authorized_keys` (not the user profile file), and that file needs `icacls /inheritance:r /grant SYSTEM:F /grant "BUILTIN\Administrators:F"` or sshd silently ignores it.

## References

- `references/windows-server-side.md` — full Windows-side recipe: OpenSSH Server install, key auth, Ollama exposure + autostart (for when the user runs commands on their machine).
