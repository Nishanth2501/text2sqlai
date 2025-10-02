# Azure Cloud Deployment Guide

Deploy your Text-to-SQL Assistant to Azure Cloud and get a **public URL**! 🚀

## 🌐 Deployment Options

### Option 1: Azure Container Instances (Recommended - Fastest)
- **Public URL**: `https://your-app-name.eastus.azurecontainer.io`
- **Cost**: Pay-per-use, very cost-effective
- **Setup Time**: 5-10 minutes
- **Best for**: Development, testing, demos

### Option 2: Azure App Service
- **Public URL**: `https://your-app-name.azurewebsites.net`
- **Cost**: Free tier available, then pay-per-use
- **Setup Time**: 10-15 minutes
- **Best for**: Production applications

### Option 3: Azure Container Registry + App Service
- **Public URL**: `https://your-app-name.azurewebsites.net`
- **Cost**: Free tier available
- **Setup Time**: 15-20 minutes
- **Best for**: Production with CI/CD

---

## 🚀 Quick Start (Azure Container Instances)

### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Ensure Docker is running locally
docker --version
```

### Deploy in 3 Steps:

#### Step 1: Build and Push to Azure Container Registry
```bash
# Create resource group
az group create --name text2sql-rg --location eastus

# Create container registry
az acr create --resource-group text2sql-rg --name text2sqlregistry --sku Basic

# Login to registry
az acr login --name text2sqlregistry

# Build and push Docker image
az acr build --registry text2sqlregistry --image text2sql:latest --file docker/Dockerfile .
```

#### Step 2: Deploy to Container Instances
```bash
# Deploy with public URL
az container create \
  --resource-group text2sql-rg \
  --name text2sql-app \
  --image text2sqlregistry.azurecr.io/text2sql:latest \
  --dns-name-label text2sql-app \
  --ports 8501 \
  --environment-variables \
    APP_NAME="Text-to-SQL Assistant" \
    MODEL_NAME="google/flan-t5-base" \
    ENABLE_MODEL_CACHING="true" \
    LOG_LEVEL="INFO"
```

#### Step 3: Get Your Public URL
```bash
# Get the public URL
az container show --resource-group text2sql-rg --name text2sql-app --query ipAddress.fqdn --output tsv
```

**Your app will be available at**: `http://text2sql-app.eastus.azurecontainer.io:8501`

---

## 🌐 Azure App Service Deployment

### Option A: Direct Deployment
```bash
# Create App Service plan
az appservice plan create --name text2sql-plan --resource-group text2sql-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group text2sql-rg --plan text2sql-plan --name text2sql-app --deployment-container-image-name text2sqlregistry.azurecr.io/text2sql:latest

# Configure app settings
az webapp config appsettings set --resource-group text2sql-rg --name text2sql-app --settings \
  APP_NAME="Text-to-SQL Assistant" \
  MODEL_NAME="google/flan-t5-base" \
  ENABLE_MODEL_CACHING="true" \
  WEBSITES_PORT=8501
```

**Your app will be available at**: `https://text2sql-app.azurewebsites.net`

### Option B: GitHub Actions (Automated)
See `azure-deploy.yml` for automated deployment.

---

## 🔧 Environment Variables

Configure your deployment with these environment variables:

```bash
# Application
APP_NAME="Text-to-SQL Assistant"
DATABASE_URL="sqlite:///data/demo.sqlite"
MODEL_NAME="google/flan-t5-base"

# Performance
MAX_TOKENS=128
NUM_BEAMS=4
ENABLE_MODEL_CACHING=true
LOG_LEVEL=INFO

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_THEME_BASE=light
```

---

## 📊 Monitoring & Management

### View Logs
```bash
# Container Instances
az container logs --resource-group text2sql-rg --name text2sql-app

# App Service
az webapp log tail --resource-group text2sql-rg --name text2sql-app
```

### Scale Your Application
```bash
# Container Instances (restart with more resources)
az container create --resource-group text2sql-rg --name text2sql-app --image text2sqlregistry.azurecr.io/text2sql:latest --cpu 2 --memory 4

# App Service (scale up)
az appservice plan update --name text2sql-plan --resource-group text2sql-rg --sku P1V2
```

---

## 💰 Cost Estimation

### Azure Container Instances
- **Free**: 750 hours/month of B1S instances
- **Pay-as-you-go**: ~$0.004/hour for 1 vCPU, 1.5GB RAM
- **Monthly estimate**: $0-10 for light usage

### Azure App Service
- **Free**: F1 tier (shared resources)
- **Basic**: B1 tier ~$13/month
- **Standard**: S1 tier ~$73/month

---

## 🛠️ Troubleshooting

### Common Issues:

1. **Port Configuration**
   ```bash
   # Ensure port 8501 is exposed
   az container show --resource-group text2sql-rg --name text2sql-app --query ipAddress.ports
   ```

2. **Health Check**
   ```bash
   # Check container health
   curl http://your-app-url:8501/_stcore/health
   ```

3. **Logs**
   ```bash
   # View detailed logs
   az container logs --resource-group text2sql-rg --name text2sql-app --follow
   ```

---

## 🎯 Next Steps

1. **Choose your deployment option** above
2. **Follow the quick start** for your chosen method
3. **Get your public URL** and share your app!
4. **Monitor usage** and scale as needed

Your Text-to-SQL Assistant will be **live on the internet** with a public URL! 🌐