#!/bin/bash
set -e

# Quick Azure Deployment Script
# Choose your deployment method and get a public URL in minutes!

echo "🚀 Quick Azure Deployment for Text-to-SQL Assistant"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Choose your deployment method:${NC}"
echo ""
echo "1) Azure Container Instances (Recommended)"
echo "   - Fastest deployment (5-10 minutes)"
echo "   - Pay-per-use pricing"
echo "   - URL: http://your-app.eastus.azurecontainer.io:8501"
echo ""
echo "2) Azure App Service"
echo "   - Production-ready"
echo "   - Free tier available"
echo "   - URL: https://your-app.azurewebsites.net"
echo ""
echo "3) Show deployment options"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Deploying to Azure Container Instances...${NC}"
        ./deploy-to-aci.sh
        ;;
    2)
        echo -e "${GREEN}🚀 Deploying to Azure App Service...${NC}"
        ./deploy-to-appservice.sh
        ;;
    3)
        echo ""
        echo -e "${YELLOW}📋 Deployment Options Summary:${NC}"
        echo ""
        echo "Azure Container Instances:"
        echo "  ✅ Fastest setup (5-10 minutes)"
        echo "  ✅ Pay-per-use (very cost-effective)"
        echo "  ✅ Perfect for demos and testing"
        echo "  🌐 URL: http://your-app.eastus.azurecontainer.io:8501"
        echo ""
        echo "Azure App Service:"
        echo "  ✅ Production-ready platform"
        echo "  ✅ Free tier available"
        echo "  ✅ Built-in CI/CD support"
        echo "  🌐 URL: https://your-app.azurewebsites.net"
        echo ""
        echo "GitHub Actions (Automated):"
        echo "  ✅ Automatic deployment on git push"
        echo "  ✅ No manual intervention needed"
        echo "  ✅ Use azure-deploy.yml workflow"
        echo ""
        echo "Prerequisites:"
        echo "  • Azure CLI installed"
        echo "  • Azure account with active subscription"
        echo "  • Docker Desktop running (required for builds)"
        echo ""
        ;;
    4)
        echo "Goodbye! 👋"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac
