#!/bin/bash

# RedMess Project - Final Package Creator
# Creates clean distribution package for GitHub release
# Version: BRUTAL V3.0

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${RED}${BOLD}"
cat << "EOF"
╦═╗┌─┐┌┬┐╔╦╗┌─┐┌─┐┌─┐  ╔═╗┌─┐┌─┐┬┌─┌─┐┌─┐┌─┐┬─┐
╠╦╝├┤  ││║║║├┤ └─┐└─┐  ╠═╝├─┤│  ├┴┐├─┤│ ┬├┤ ├┬┘
╩╚═└─┘─┴┘╩ ╩└─┘└─┘└─┘  ╩  ┴ ┴└─┘┴ ┴┴ ┴└─┘└─┘┴└─
EOF
echo -e "${NC}${CYAN}Clean Package Creator - BRUTAL V3.0${NC}\n"

PACKAGE_DIR="RedMess-Package"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${BLUE}Creating clean distribution package...${NC}\n"

# Remove old package
rm -rf "$PACKAGE_DIR"

# Create package structure
echo -e "${CYAN}[1/5] Creating directory structure${NC}"
mkdir -p "$PACKAGE_DIR"/{security,telegram_bot,docs}

# Copy core files
echo -e "${CYAN}[2/5] Copying core files${NC}"
cp install.sh "$PACKAGE_DIR/"
cp setup.sh "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp config.example.yaml "$PACKAGE_DIR/"
cp .env.example "$PACKAGE_DIR/"
cp .gitignore "$PACKAGE_DIR/"
cp LICENSE "$PACKAGE_DIR/"
cp checklist.sh "$PACKAGE_DIR/"

# Copy documentation
echo -e "${CYAN}[3/5] Copying documentation${NC}"
cp README.md "$PACKAGE_DIR/"
cp QUICK_INSTALL.md "$PACKAGE_DIR/"
cp SUMMARY.md "$PACKAGE_DIR/"

# Copy Python tools
echo -e "${CYAN}[4/5] Copying management tools${NC}"
cp db_manager.py "$PACKAGE_DIR/"
cp backup_manager.py "$PACKAGE_DIR/"

# Copy security & bot files
echo -e "${CYAN}[5/5] Copying GODMODE & bot${NC}"
cp security/GODMODE_ULTIMATE.md "$PACKAGE_DIR/security/"
cp security/godmode_integration.py "$PACKAGE_DIR/security/"
cp security/godmode_injector.py "$PACKAGE_DIR/security/"
cp security/deploy_godmode.py "$PACKAGE_DIR/security/"

cp telegram_bot/bot.py "$PACKAGE_DIR/telegram_bot/"
cp telegram_bot/godmode_integration.py "$PACKAGE_DIR/telegram_bot/"

# Make scripts executable
chmod +x "$PACKAGE_DIR"/*.sh

# Create package info
cat > "$PACKAGE_DIR/PACKAGE_INFO.txt" << EOF
RedMess - GODMODE BRUTAL V3.0
================================

Package Created: $(date)
Version: 3.0.0
Status: Production Ready

Contents:
---------
✓ Interactive installer (install.sh)
✓ Manual setup script (setup.sh)
✓ GODMODE system (4 files)
✓ Telegram bot integration
✓ Database manager
✓ Backup manager
✓ Complete documentation
✓ Configuration templates

Installation:
-------------
1. Extract this package
2. Run: ./install.sh
3. Follow the interactive wizard

Quick Start:
------------
See QUICK_INSTALL.md for detailed instructions

Support:
--------
GitHub: https://github.com/harezadmm/RedMess
Telegram: @sisuryaofficialkuu

Legal:
------
Read LICENSE before use
For authorized penetration testing ONLY
EOF

# Create archive
echo -e "\n${BLUE}Creating archive...${NC}"
tar -czf "RedMess-v3.0-${TIMESTAMP}.tar.gz" "$PACKAGE_DIR"

ARCHIVE_SIZE=$(du -h "RedMess-v3.0-${TIMESTAMP}.tar.gz" | cut -f1)

echo -e "\n${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                                                           ║${NC}"
echo -e "${GREEN}${BOLD}║         ✅  Package Created Successfully! 🔥              ║${NC}"
echo -e "${GREEN}${BOLD}║                                                           ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Package Details:${NC}"
echo -e "  Archive: ${GREEN}RedMess-v3.0-${TIMESTAMP}.tar.gz${NC}"
echo -e "  Size: ${GREEN}${ARCHIVE_SIZE}${NC}"
echo -e "  Directory: ${GREEN}${PACKAGE_DIR}/${NC}"
echo -e ""

echo -e "${CYAN}Contents:${NC}"
find "$PACKAGE_DIR" -type f | wc -l | xargs echo "  Total files:"
echo -e ""

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Test the package: ${BLUE}tar -xzf RedMess-v3.0-${TIMESTAMP}.tar.gz${NC}"
echo -e "  2. Test installation: ${BLUE}cd RedMess-Package && ./install.sh${NC}"
echo -e "  3. Upload to GitHub releases"
echo -e "  4. Update download links in README"
echo -e ""

echo -e "${GREEN}Package ready for distribution! 🚀${NC}\n"
