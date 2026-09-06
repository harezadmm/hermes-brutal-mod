#!/bin/bash
# Quick GitHub push script for RedMess BRUTAL MOD

set -e

echo "🔥 RedMess BRUTAL MOD - GitHub Push Script"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ ERROR: Run this from RedMess root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add remote if not exists
if ! git remote | grep -q "origin"; then
    echo "🔗 Adding GitHub remote..."
    read -p "Enter GitHub repo URL (e.g., git@github.com:harezadmm/RedMess.git): " repo_url
    git remote add origin "$repo_url"
fi

# Create .gitignore if doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.env.local

# Hermes
.hermes/conversations/
.hermes/logs/
.hermes/cache/

# Temporary
*.tmp
*.bak
.cache/
EOF
fi

echo ""
echo "📋 Current status:"
git status --short

echo ""
read -p "Commit message (default: 'Update RedMess BRUTAL MOD'): " commit_msg
commit_msg=${commit_msg:-"Update RedMess BRUTAL MOD"}

echo ""
echo "🚀 Staging files..."
git add .

echo "📝 Committing..."
git commit -m "$commit_msg"

echo "⬆️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🔗 View at: https://github.com/harezadmm/RedMess"
echo ""
