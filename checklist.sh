#!/bin/bash

# RedMess Project Checklist
# Verify all components are ready before deployment
# Version: BRUTAL V3.0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║         RedMess Deployment Checklist - V3.0              ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"

PASSED=0
FAILED=0
WARNINGS=0

check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description - MISSING: $file"
        ((FAILED++))
        return 1
    fi
}

check_dir() {
    local dir="$1"
    local description="$2"
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description - MISSING: $dir"
        ((FAILED++))
        return 1
    fi
}

warn() {
    local message="$1"
    echo -e "${YELLOW}⚠${NC} $message"
    ((WARNINGS++))
}

# Core Installation Files
echo -e "${BLUE}[1/8] Core Installation Files${NC}"
check_file "install.sh" "Interactive installer"
check_file "setup.sh" "Manual setup script"
check_file "requirements.txt" "Python dependencies"
echo ""

# Configuration
echo -e "${BLUE}[2/8] Configuration Files${NC}"
check_file "config.example.yaml" "Configuration template"
check_file ".env.example" "Environment variables template"
echo ""

# GODMODE System
echo -e "${BLUE}[3/8] GODMODE System${NC}"
check_file "security/GODMODE_ULTIMATE.md" "GODMODE prompt"
check_file "security/godmode_integration.py" "GODMODE integration"
check_file "security/godmode_injector.py" "GODMODE injector"
check_file "security/deploy_godmode.py" "GODMODE deployment"
echo ""

# Security Skills
echo -e "${BLUE}[4/8] Security Skills${NC}"
check_dir "security" "Security skills directory"

if [ -d "security" ]; then
    SKILL_COUNT=$(find security -name "*.md" 2>/dev/null | wc -l)
    if [ $SKILL_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $SKILL_COUNT skill files"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} No skill files found"
        ((FAILED++))
    fi
fi
echo ""

# Telegram Bot
echo -e "${BLUE}[5/8] Telegram Bot${NC}"
check_file "telegram_bot/bot.py" "Bot main script"
check_file "telegram_bot/godmode_integration.py" "Bot GODMODE integration"
echo ""

# Management Tools
echo -e "${BLUE}[6/8] Management Tools${NC}"
check_file "db_manager.py" "Database manager"
check_file "backup_manager.py" "Backup manager"
echo ""

# Documentation
echo -e "${BLUE}[7/8] Documentation${NC}"
check_file "README.md" "Main README"
check_file "QUICK_INSTALL.md" "Installation guide"
check_file "LICENSE" "License file"
echo ""

# Git Configuration
echo -e "${BLUE}[8/8] Git Configuration${NC}"
check_file ".gitignore" "Git ignore rules"

# Check if git repo
if [ -d ".git" ]; then
    echo -e "${GREEN}✓${NC} Git repository initialized"
    ((PASSED++))
else
    warn "Not a git repository (run: git init)"
fi
echo ""

# File Permissions
echo -e "${BLUE}[Bonus] File Permissions${NC}"
for script in install.sh setup.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✓${NC} $script is executable"
            ((PASSED++))
        else
            warn "$script is not executable (run: chmod +x $script)"
        fi
    fi
done
echo ""

# Python Syntax Check
echo -e "${BLUE}[Bonus] Python Syntax${NC}"
PYTHON_FILES=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" 2>/dev/null)
SYNTAX_ERRORS=0

for pyfile in $PYTHON_FILES; do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        :
    else
        echo -e "${RED}✗${NC} Syntax error in $pyfile"
        ((SYNTAX_ERRORS++))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All Python files have valid syntax"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Found $SYNTAX_ERRORS Python files with syntax errors"
    ((FAILED++))
fi
echo ""

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      SUMMARY                              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}\n"
    
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Review configuration files"
    echo -e "  2. Test installation: ${YELLOW}./install.sh${NC}"
    echo -e "  3. Commit to git: ${YELLOW}git add . && git commit -m 'Initial commit'${NC}"
    echo -e "  4. Push to GitHub: ${YELLOW}git push origin main${NC}"
    echo -e "  5. Update repository URL in README.md"
    echo ""
    
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Fix issues before deployment.${NC}\n"
    exit 1
fi
