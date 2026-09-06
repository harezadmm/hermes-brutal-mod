# Hermes BRUTAL MOD 🔥

Full modified Hermes Agent setup — persona layer, GODMODE jailbreak, 71-skill arsenal, RedMess profile, deploy scripts.

## 📦 Isi Paket

| Layer | File/Folder | Fungsi |
|-------|------------|--------|
| 🧠 Persona | `PERSONA.md`, `SOUL.md`, `IDENTITY.md`, `identity.md`, `instructions.md` | Identitas & gaya bahasa agent |
| 🔓 Jailbreak | `godmode_prompt.txt`, `prefill.json`, `JAILBREAK.md`, `GODMODE.md` | Core jailbreak prompt & prefill |
| ⚙️ Config | `config.yaml`, `config.example.yaml`, `cli-config.yaml.example` | Routing model & tools |
| 🎨 Skills | `skills/` (71 skill) | Arsenal kemampuan per-domain |
| 🔴 RedMess | `profiles/redmess/`, `redmess/`, `redmess-examples/`, `redmess-arsenal-SKILL.md` | Profile & tooling RedMess |
| 🔧 Deploy | `PUSH_BRUTAL_MOD.sh`, `deploy.sh`, `checklist.sh`, `create_package.sh` | Script deploy & push |
| 📚 Docs | 40 file `.md` | Dokumentasi lengkap |

## 🚀 Cara Pakai

```bash
# 1. Ekstrak ke ~/.hermes/ (backup dulu yang lama!)
tar -xzf hermes-mod-full.tar.gz -C ~/.hermes/

# 2. Modifikasi layer yang mau diubah:
#    - Perilaku agent → PERSONA.md / SOUL.md / godmode_prompt.txt
#    - Kemampuan → skills/<nama-skill>/SKILL.md
#    - Model routing → config.yaml

# 3. Restart Hermes, done.
```

## ⚠️ Penting

- **JANGAN commit** `.env`, `auth.json`, `state.db`, `kanban.db`, `sessions/`, `logs/` — berisi API keys & data pribadi
- Skill `app-account-farming` hanya untuk riset defensive/lab sendiri
- Repo ini private — jangan di-public tanpa review ulang isi `skills/`

## 📝 Struktur Modifikasi Prioritas

1. `godmode_prompt.txt` + `prefill.json` — kontrol jailbreak & prefill
2. `PERSONA.md` / `SOUL.md` — identitas agent
3. `skills/*/SKILL.md` — tambah/edit kemampuan
4. `config.yaml` — routing model & platform
