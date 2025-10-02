#!/bin/bash

echo "🚀 Setting up Text-to-SQL Assistant for GitHub..."

# Initialize Git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📝 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Text-to-SQL Assistant

- Complete Text-to-SQL system with web UI, CLI, and API
- Uses Google Flan-T5 with prompt engineering
- Safety validation and evaluation framework
- Streamlit interface with suggested prompts
- FastAPI backend for programmatic access
- Comprehensive documentation and examples"

echo "✅ Git repository ready!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Copy the repository URL"
echo "3. Run these commands:"
echo "   git remote add origin <your-repo-url>"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🎉 Your Text-to-SQL Assistant is ready for GitHub!"
