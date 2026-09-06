# 🔥 RedMess - Quick Installation Guide

**Hermes Agent Modded Edition with GODMODE BRUTAL V3.0**

Zero-hassle setup. One command. Fully configured.

---

## ⚡ Quick Install (Recommended)

**One command, fully automated:**

```bash
curl -fsSL https://raw.githubusercontent.com/harezadmm/RedMess/main/install.sh | bash
```

Or clone and run:

```bash
git clone https://github.com/harezadmm/RedMess.git
cd RedMess
chmod +x install.sh
./install.sh
```

### What the installer does:

✅ **Interactive wizard** - answers questions, no manual config  
✅ **Auto-detects Python** - works with Python 3.11/3.12/3.14  
✅ **Installs Hermes** (optional) - full CLI agent  
✅ **Configures AI API** - OpenAI, Anthropic, or custom  
✅ **Sets up Telegram bot** (optional) - with GODMODE integration  
✅ **Deploys 99+ skills** - offensive security, hacking, pentesting  
✅ **Enables GODMODE** (optional) - zero content restrictions  
✅ **Creates launchers** - ready-to-run scripts  

**Installation takes 2-5 minutes.**

---

## 📋 Installation Wizard Questions

The installer will ask:

### 1️⃣ **Installation Mode**
```
1) Full Installation (Hermes CLI + Telegram Bot)
2) Hermes CLI Only
3) Telegram Bot Only
4) Skills Only (already have Hermes)
```
**Recommended:** Option 1 (Full)

### 2️⃣ **AI API Configuration**
```
API Base URL [https://api.openai.com/v1]: <enter or paste your API URL>
API Key: <paste your API key>
Model name [gpt-4]: <enter model name>
```

**Supported providers:**
- OpenAI (gpt-4, gpt-3.5-turbo)
- Anthropic (claude-3.5-sonnet, claude-3-opus)
- Any OpenAI-compatible API

### 3️⃣ **Telegram Bot (Optional)**
```
Telegram Bot Token: <paste token from @BotFather>
Your Telegram User ID [7570665912]: <your telegram ID>
```

**To get bot token:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow prompts, copy token

**To get your user ID:**
1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your ID

### 4️⃣ **GODMODE Authorization**
```
⚠️  WARNING: GODMODE BRUTAL
This enables ZERO content restrictions:
  • Malicious code (RAT, keylogger, exploits)
  • Weapons guides (bombs, poison, firearms)
  • NSFW content (any kink, taboo)
  • Illegal activity guides

Enable GODMODE BRUTAL? [Y/n]: y
```

**⚠️ Legal warning:** GODMODE bypasses ALL safety filters. For authorized penetration testing and research ONLY. Unauthorized use is illegal.

### 5️⃣ **Installation Directory**
```
Installation directory [~/.redmess]: <press enter or type custom path>
```

**Done!** Installer handles the rest automatically.

---

## 🚀 After Installation

### Start Hermes CLI:
```bash
cd ~/.redmess
./start_hermes.sh
```

### Start Telegram Bot:
```bash
cd ~/.redmess
./start_bot.sh
```

### Configuration file:
```bash
nano ~/.redmess/config/redmess.yaml
```

---

## 📂 What Gets Installed

```
~/.redmess/
├── config/
│   └── redmess.yaml          # Main configuration
├── skills/
│   └── security/             # 99+ offensive security skills
│       ├── GODMODE_ULTIMATE.md
│       ├── deploy_godmode.py
│       └── godmode_injector.py
├── telegram_bot/
│   ├── bot.py                # Telegram bot runner
│   └── godmode_integration.py
├── logs/                     # Bot and error logs
├── workspace/                # Working directory
├── umiagent.db              # Authorization database
├── start_hermes.sh          # Hermes launcher
└── start_bot.sh             # Bot launcher
```

---

## 🎯 Using the Bot

### Telegram Commands:

- `/start` - Welcome message
- `/status` - Check authorization status
- `/godmode` - Activate GODMODE (authorized only)
- `/help` - Command list

### Send any message to chat with AI

### Codewords (GODMODE users):
- `BOOMBA!` - Pipe bomb guide
- `ANARCHIST` - Molotov cocktail
- `CHEMIST` - Drug/poison synthesis
- `HACKER` - Zero-day exploits

---

## 🔥 GODMODE Features

### What's different with GODMODE?

| Without GODMODE | With GODMODE |
|----------------|--------------|
| ❌ "I can't help with that" | ✅ Immediate execution |
| ❌ "That would be dangerous" | ✅ Zero refusals |
| ❌ Sanitized/censored output | ✅ Full uncensored content |
| ❌ "Here's an alternative..." | ✅ Production-ready code |

### Authorization:

**Primary Owner (default):** User ID `7570665912`  
**Rental Users:** GODMODE_BRUTAL tier

**Modify in database:**
```bash
sqlite3 ~/.redmess/umiagent.db
INSERT INTO godmode_auth (user_id, tier) VALUES (YOUR_USER_ID, 'GODMODE_BRUTAL');
```

---

## 🛠️ Troubleshooting

### "Python not found"
```bash
# Ubuntu/Debian
sudo apt install python3.12 python3.12-pip

# macOS
brew install python@3.12
```

### "Hermes not found after install"
```bash
python3 -m pip install --user hermes-agent
export PATH="$HOME/.local/bin:$PATH"
```

### "Bot not responding"
1. Check token in `~/.redmess/config/redmess.yaml`
2. Verify bot is running: `ps aux | grep bot.py`
3. Check logs: `tail -f ~/.redmess/logs/bot.log`

### "AI not responding"
Edit `~/.redmess/config/redmess.yaml`:
```yaml
ai:
  api_key: "YOUR_ACTUAL_KEY_HERE"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4"
```

### "GODMODE not working"
```bash
cd ~/.redmess
python3 godmode_injector.py
./start_bot.sh
```

---

## 🔄 Manual Installation (Advanced)

If you prefer manual setup:

### 1. Install dependencies
```bash
pip3 install hermes-agent python-telegram-bot pyyaml
```

### 2. Clone repository
```bash
git clone https://github.com/harezadmm/RedMess.git
cd RedMess
```

### 3. Run deployment
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Configure manually
```bash
cp config.example.yaml ~/.redmess/config/redmess.yaml
nano ~/.redmess/config/redmess.yaml
```

### 5. Deploy GODMODE
```bash
python3 security/deploy_godmode.py
```

### 6. Start services
```bash
# Hermes CLI
hermes chat

# Telegram bot
cd telegram_bot
python3 bot.py
```

---

## 📊 Features

### 99+ Offensive Security Skills:
- 🔓 APK Modding & Android Hacking
- 🐀 RAT Development (Windows/Linux/macOS)
- 💉 SQL Injection & Web Exploitation
- 🔐 Reverse Engineering (Ghidra, Frida, IDA)
- 📱 Mobile Pentesting (Android 16, Frida hooking)
- ☁️ Cloud Security & AWS Exploitation
- 🌐 API Security & Route Cloning
- 🧪 Lua Deobfuscation & Script Analysis
- 🎯 Social Engineering & Phishing
- 🔨 Binary Exploitation & Buffer Overflows

### GODMODE Capabilities:
- ✅ Malicious code generation (RAT, keyloggers, ransomware)
- ✅ Weapons guides (explosives, poisons, firearms)
- ✅ NSFW content (any kink, taboo, celebrities)
- ✅ Hacking tutorials (zero-days, exploits, pentesting)
- ✅ Drug synthesis & chemistry guides
- ✅ Social engineering scripts
- ✅ Violence & controversial content
- ✅ Zero refusals for authorized users

---

## ⚖️ Legal Disclaimer

**FOR AUTHORIZED PENETRATION TESTING & RESEARCH ONLY**

This tool is for:
- ✅ Authorized security research
- ✅ Penetration testing with written permission
- ✅ Educational purposes in controlled environments
- ✅ Bug bounty programs
- ✅ Red team exercises

**STRICTLY PROHIBITED:**
- ❌ Unauthorized access to systems
- ❌ Real-world attacks without permission
- ❌ Illegal weapons manufacturing
- ❌ Production/distribution of illegal substances
- ❌ Harmful real-world actions

**You are responsible for your actions. By using this tool, you agree to:**
- Only use on systems you own or have explicit written authorization to test
- Comply with all applicable laws in your jurisdiction
- Not hold the developers liable for misuse

Unauthorized computer access is illegal under:
- 🇺🇸 CFAA (Computer Fraud and Abuse Act)
- 🇮🇩 UU ITE (Indonesia)
- 🇪🇺 GDPR & Computer Misuse Acts
- 🇬🇧 Computer Misuse Act 1990

**Use responsibly. Stay legal. Get authorization.**

---

## 🤝 Contributing

Contributions welcome! Submit PRs for:
- New security skills
- Bug fixes
- Performance improvements
- Documentation

---

## 📞 Support

- **GitHub Issues:** [Report bugs](https://github.com/harezadmm/RedMess/issues)
- **Telegram:** @sisuryaofficialkuu
- **Documentation:** See [INSTALLATION.md](INSTALLATION.md) for detailed setup

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

**Modified Hermes Agent by Nous Research**

---

## 🔥 Quick Reference

**Install:**
```bash
curl -fsSL https://raw.githubusercontent.com/harezadmm/RedMess/main/install.sh | bash
```

**Start CLI:**
```bash
~/.redmess/start_hermes.sh
```

**Start Bot:**
```bash
~/.redmess/start_bot.sh
```

**Config:**
```bash
nano ~/.redmess/config/redmess.yaml
```

**Activate GODMODE:**
Send `GODMODE ACTIVE` to bot

**Status:**
```bash
sqlite3 ~/.redmess/umiagent.db "SELECT * FROM godmode_auth"
```

---

**Version:** BRUTAL V3.0  
**Updated:** 2026-09-04  
**Status:** Production Ready 🚀
