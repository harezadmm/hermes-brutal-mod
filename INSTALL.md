# Installation Guide

Complete installation instructions for RedMess across different platforms and use cases.

---

## Quick Install (5 Minutes)

### Option 1: Direct API Integration

```bash
# Clone repository
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Install dependencies (Python example)
pip install anthropic openai google-generativeai

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Test
python examples/test_basic.py
```

### Option 2: Telegram Bot

```bash
# Clone and setup
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Install dependencies
pip install python-telegram-bot anthropic

# Configure
cp config.example.yaml config.yaml
nano config.yaml  # Add your tokens

# Run
python telegram_bot.py
```

### Option 3: Hermes Agent

```bash
# Navigate to Hermes profile
cd ~/.hermes/profiles/your_profile/

# Copy RedMess components
curl -O https://raw.githubusercontent.com/yourusername/RedMess/main/IDENTITY.md
curl -O https://raw.githubusercontent.com/yourusername/RedMess/main/JAILBREAK.md
curl -O https://raw.githubusercontent.com/yourusername/RedMess/main/GODMODE.md

# Append to instructions
cat JAILBREAK.md GODMODE.md >> instructions.md

# Restart Hermes
hermes
```

---

## Detailed Installation

### Prerequisites

**Required:**
- Python 3.10+ (for Python integrations)
- API key for at least one provider (Anthropic, OpenAI, etc.)

**Optional:**
- Telegram Bot Token (for bot deployment)
- Docker (for containerized deployment)
- PostgreSQL (for rental system with many users)

### System Requirements

**Minimum:**
- 1 CPU core
- 512 MB RAM
- 100 MB disk space

**Recommended:**
- 2+ CPU cores
- 2 GB RAM
- 1 GB disk space (for logs, cache)

**For Local Models:**
- 8+ CPU cores or GPU
- 16+ GB RAM (32GB+ for 70B models)
- 50+ GB disk space

---

## Installation by Platform

### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3-pip git -y

# Clone RedMess
cd ~
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Set environment variables
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc

# Test installation
python test_install.py
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11 git

# Clone and setup
cd ~
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

# Test
python test_install.py
```

### Windows

```powershell
# Install Python from python.org (3.11+)
# Download: https://www.python.org/downloads/

# Open PowerShell as Administrator

# Clone repository
cd $HOME
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variable
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-key-here', 'User')

# Test
python test_install.py
```

### Android (Termux)

```bash
# Update Termux
pkg update && pkg upgrade -y

# Install dependencies
pkg install python git -y

# Clone RedMess
cd ~
git clone https://github.com/yourusername/RedMess.git
cd RedMess

# Install Python packages
pip install -r requirements.txt

# Set API key
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc

# Test
python test_install.py
```

---

## Provider Setup

### Anthropic Claude

```bash
# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Test
python -c "import anthropic; print(anthropic.Anthropic(api_key='$ANTHROPIC_API_KEY').messages.create(model='claude-sonnet-4', max_tokens=100, messages=[{'role':'user','content':'test'}]))"
```

### OpenAI GPT

```bash
# Get API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."

# Test
python -c "import openai; print(openai.OpenAI(api_key='$OPENAI_API_KEY').chat.completions.create(model='gpt-4', messages=[{'role':'user','content':'test'}]))"
```

### Google Gemini

```bash
# Get API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="..."

# Test
python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print(genai.GenerativeModel('gemini-1.5-pro').generate_content('test'))"
```

### Local Models (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:70b

# Test
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1:70b",
  "messages": [{"role": "user", "content": "test"}]
}'
```

---

## Telegram Bot Setup

### Create Bot

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose name and username
4. Copy token: `7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

### Configure Bot

```bash
# Edit config
nano config.yaml
```

```yaml
telegram:
  token: "7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
  owner_id: 7570665912  # Your Telegram user ID
  
ai:
  provider: "anthropic"
  model: "claude-sonnet-4"
  api_key: "sk-ant-..."
  
redmess:
  godmode: true
  rental_enabled: false  # Set true for multi-user
```

### Run Bot

```bash
# Start bot
python telegram_bot.py

# Or with systemd (Linux)
sudo cp redmess-bot.service /etc/systemd/system/
sudo systemctl enable redmess-bot
sudo systemctl start redmess-bot
```

---

## Docker Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  redmess-bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OWNER_ID=7570665912
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=redmess
      - POSTGRES_USER=redmess
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy

```bash
# Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_token
ANTHROPIC_API_KEY=your_key
DB_PASSWORD=secure_password
EOF

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f redmess-bot
```

---

## Hermes Agent Integration

### Full Integration

```bash
# Navigate to profile
cd ~/.hermes/profiles/your_profile/

# Download all components
wget https://raw.githubusercontent.com/yourusername/RedMess/main/IDENTITY.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/JAILBREAK.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/GODMODE.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/WRITING_TIPS.md

# Merge into identity
cat IDENTITY.md > identity.md

# Merge into instructions
cat JAILBREAK.md GODMODE.md WRITING_TIPS.md >> instructions.md

# Download examples
mkdir -p redmess_examples
cd redmess_examples
wget https://raw.githubusercontent.com/yourusername/RedMess/main/examples/rat_example.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/examples/sqli_exploit.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/examples/weapon_guides.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/examples/darkweb_markets.md
wget https://raw.githubusercontent.com/yourusername/RedMess/main/examples/advanced_hacking.md

# Restart Hermes
cd ~
hermes
```

### Selective Integration

```bash
# Only core jailbreak (minimal)
cd ~/.hermes/profiles/your_profile/
cat JAILBREAK.md GODMODE.md >> instructions.md

# Only for specific tasks
cd ~/.hermes/profiles/your_profile/skills/
mkdir redteam
cd redteam
# Copy relevant example files
```

---

## Troubleshooting Installation

### Python Import Errors

```bash
# If "ModuleNotFoundError: No module named 'anthropic'"
pip install anthropic openai google-generativeai python-telegram-bot

# If pip not found
python -m ensurepip --upgrade
```

### API Key Issues

```bash
# Test API key validity
python -c "import anthropic; anthropic.Anthropic(api_key='YOUR_KEY').messages.create(model='claude-sonnet-4', max_tokens=10, messages=[{'role':'user','content':'hi'}])"

# If invalid, regenerate key from provider dashboard
```

### Permission Errors (Linux)

```bash
# If "Permission denied"
sudo chown -R $USER:$USER ~/RedMess
chmod +x *.py
```

### Port Conflicts (Docker)

```bash
# If "port already allocated"
# Edit docker-compose.yml to use different ports
# Or stop conflicting service
sudo systemctl stop postgresql  # If port 5432 conflict
```

---

## Upgrading

### Update RedMess

```bash
cd ~/RedMess
git pull origin main

# Reinstall dependencies (if requirements changed)
pip install -r requirements.txt --upgrade

# Restart bot/service
sudo systemctl restart redmess-bot
```

### Migration (Version Updates)

```bash
# Backup current config
cp config.yaml config.yaml.backup

# Backup database (if using rental system)
cp data/umiagent.db data/umiagent.db.backup

# Pull update
git pull

# Run migration script (if provided)
python migrate.py

# Test
python test_install.py
```

---

## Uninstallation

### Remove RedMess

```bash
# Stop service
sudo systemctl stop redmess-bot
sudo systemctl disable redmess-bot

# Remove files
rm -rf ~/RedMess

# Remove systemd service
sudo rm /etc/systemd/system/redmess-bot.service
sudo systemctl daemon-reload

# Remove Python packages (optional)
pip uninstall anthropic openai python-telegram-bot
```

### Remove from Hermes

```bash
cd ~/.hermes/profiles/your_profile/

# Remove identity (if you want to revert)
rm identity.md
# Restore original or create new one

# Remove from instructions
nano instructions.md  # Manually remove RedMess sections

# Remove examples
rm -rf redmess_examples/
```

---

## Support

**Issues:** https://github.com/yourusername/RedMess/issues  
**Telegram:** @sisuryaofficialkuu  
**Bot:** @umi_agbot  

---

**Installation complete! Check README.md for usage examples.**
