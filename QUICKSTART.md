# RedMess - Quick Start Guide

## One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/harezadmm/RedMess/main/install.sh | bash
```

## Manual Installation

### 1. Clone Repository
```bash
git clone https://github.com/harezadmm/RedMess.git
cd RedMess
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configure
```bash
cp .env.example .env
nano .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_@BotFather
TELEGRAM_OWNER_ID=your_telegram_user_id
AI_API_KEY=your_openai_compatible_api_key
AI_BASE_URL=https://your-api-endpoint.com/v1
AI_MODEL=gpt-4
```

### 4. Setup Hermes Skills
```bash
hermes config set skills.external_dirs "['$(pwd)/skills']"
```

### 5. Start Bot
```bash
cd telegram_bot
python3 hermes_full_bot.py
```

## Features

✅ **126 Security Skills** - APK modding, Frida, GODMODE, RAT, SQL injection  
✅ **Hermes Agent Integration** - Full skills + memory system  
✅ **GODMODE BRUTAL** - Zero content restrictions for owner  
✅ **AI Chat** - OpenAI-compatible API  
✅ **OSINT Tools** - Email, username, phone, IP, domain lookup  

## Bot Commands

- `/start` - Start bot
- `/skills` - List all skills
- `/skill <name>` - View skill details
- `/memory` - List memories
- `/search <query>` - Search memories
- `/clear` - Clear chat history

## GODMODE Features (Owner Only)

- Zero content boundaries
- Full malicious code access
- No safety refusals
- Codewords: `BOOMBA!`, `ANARCHIST`

## Requirements

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- OpenAI-compatible API key

## Support

- GitHub: https://github.com/harezadmm/RedMess
- Issues: https://github.com/harezadmm/RedMess/issues
