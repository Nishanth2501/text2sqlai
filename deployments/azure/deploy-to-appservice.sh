#!/bin/bash
set -e

# Azure App Service Deployment Script
# This script deploys your Docker container to Azure App Service and gives you a public URL

echo "🚀 Deploying Text-to-SQL Assistant to Azure App Service..."

# Configuration
RESOURCE_GROUP="text2sql-rg"
REGISTRY_NAME="text2sqlregistry"
APP_NAME="text2sql-app"
PLAN_NAME="text2sql-plan"
LOCATION="eastus"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first:"
    echo "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Please login:"
    az login
fi

print_status "Starting Azure App Service deployment..."

# Step 1: Create resource group
print_status "Creating resource group: $RESOURCE_GROUP"
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    print_warning "Resource group already exists"
else
    az group create --name $RESOURCE_GROUP --location $LOCATION
    print_success "Resource group created"
fi

# Step 2: Create container registry
print_status "Creating container registry: $REGISTRY_NAME"
if az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "Container registry already exists"
else
    az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic
    print_success "Container registry created"
fi

# Step 3: Login to registry
print_status "Logging in to container registry..."
az acr login --name $REGISTRY_NAME

# Step 4: Build and push Docker image
print_status "Building and pushing Docker image..."
az acr build --registry $REGISTRY_NAME --image text2sql:latest --file docker/Dockerfile .

print_success "Docker image built and pushed successfully"

# Step 5: Create App Service plan
print_status "Creating App Service plan: $PLAN_NAME"
if az appservice plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "App Service plan already exists"
else
    az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux
    print_success "App Service plan created"
fi

# Step 6: Create web app
print_status "Creating web app: $APP_NAME"
if az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "Web app already exists. Updating..."
    az webapp delete --name $APP_NAME --resource-group $RESOURCE_GROUP --yes
fi

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --deployment-container-image-name $REGISTRY_NAME.azurecr.io/text2sql:latest

print_success "Web app created successfully!"

# Step 7: Configure app settings
print_status "Configuring app settings..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    APP_NAME="Text-to-SQL Assistant" \
    DATABASE_URL="sqlite:///data/demo.sqlite" \
    MODEL_NAME="google/flan-t5-base" \
    MAX_TOKENS="128" \
    NUM_BEAMS="4" \
    ENABLE_MODEL_CACHING="true" \
    LOG_LEVEL="INFO" \
    STREAMLIT_SERVER_PORT="8501" \
    STREAMLIT_SERVER_ADDRESS="0.0.0.0" \
    STREAMLIT_THEME_BASE="light" \
    WEBSITES_PORT="8501" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="true"

print_success "App settings configured!"

# Step 8: Enable continuous deployment
print_status "Enabling continuous deployment..."
az webapp deployment container config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --enable-cd true

# Step 9: Get the public URL
print_status "Getting public URL..."
PUBLIC_URL=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName --output tsv)

if [ -n "$PUBLIC_URL" ]; then
    print_success "🎉 Deployment complete!"
    echo ""
    echo "🌐 Your Text-to-SQL Assistant is now live at:"
    echo "   https://$PUBLIC_URL"
    echo ""
    echo "📊 Health check:"
    echo "   https://$PUBLIC_URL/_stcore/health"
    echo ""
    echo "🔧 Management commands:"
    echo "   View logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
    echo "   Stop app:  az webapp stop --resource-group $RESOURCE_GROUP --name $APP_NAME"
    echo "   Scale up:  az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku P1V2"
    echo "   Restart:   az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME"
else
    print_error "Failed to get public URL. Check the deployment status:"
    az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP
fi

print_status "Deployment process completed!"
