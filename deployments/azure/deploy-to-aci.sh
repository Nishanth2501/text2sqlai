#!/bin/bash
set -e

# Azure Container Instances Deployment Script
# This script deploys your Docker container to Azure and gives you a public URL

echo "🚀 Deploying Text-to-SQL Assistant to Azure Container Instances..."

# Configuration
RESOURCE_GROUP="text2sql-demo-rg"
REGISTRY_NAME="text2sqldemoregistry"
CONTAINER_NAME="text2sql-demo-app"
DNS_LABEL="text2sql-demo-app"
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

print_status "Starting deployment process..."

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

# Step 5: Deploy to Container Instances
print_status "Deploying to Azure Container Instances..."

# Check if container already exists
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME &> /dev/null; then
    print_warning "Container already exists. Updating..."
    az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes
fi

# Deploy the container
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $REGISTRY_NAME.azurecr.io/text2sql:latest \
  --dns-name-label $DNS_LABEL \
  --ports 8501 \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    APP_NAME="Text-to-SQL Assistant" \
    DATABASE_URL="sqlite:///data/demo.sqlite" \
    MODEL_NAME="google/flan-t5-base" \
    MAX_TOKENS="128" \
    NUM_BEAMS="4" \
    ENABLE_MODEL_CACHING="true" \
    LOG_LEVEL="INFO" \
    STREAMLIT_SERVER_PORT="8501" \
    STREAMLIT_SERVER_ADDRESS="0.0.0.0" \
    STREAMLIT_THEME_BASE="light"

print_success "Container deployed successfully!"

# Step 6: Get the public URL
print_status "Getting public URL..."
PUBLIC_URL=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.fqdn --output tsv)

if [ -n "$PUBLIC_URL" ]; then
    print_success "🎉 Deployment complete!"
    echo ""
    echo "🌐 Your Text-to-SQL Assistant is now live at:"
    echo "   http://$PUBLIC_URL:8501"
    echo ""
    echo "📊 Health check:"
    echo "   http://$PUBLIC_URL:8501/_stcore/health"
    echo ""
    echo "🔧 Management commands:"
    echo "   View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
    echo "   Stop app:  az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"
    echo "   Scale up:  az container create --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --image $REGISTRY_NAME.azurecr.io/text2sql:latest --cpu 2 --memory 4 --dns-name-label $DNS_LABEL --ports 8501"
else
    print_error "Failed to get public URL. Check the deployment status:"
    az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME
fi
