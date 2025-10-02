# Docker Configuration

This folder contains Docker configuration files for local development and deployment.

## Files:
- `Dockerfile` - Multi-stage Docker image definition
- `docker-compose.yml` - Complete development and production setup
- `docker-entrypoint.sh` - Container startup script with initialization
- `deploy.sh` - Deployment management script

## Quick Start:

### Using Docker Compose (Recommended):
```bash
# Start the application
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the application
docker-compose -f docker/docker-compose.yml down
```

### Using the Deployment Script:
```bash
# Start the application
./docker/deploy.sh start

# Check status
./docker/deploy.sh status

# View logs
./docker/deploy.sh logs

# Stop the application
./docker/deploy.sh stop
```

## Access:
- **Application**: http://localhost:8501
- **Health Check**: http://localhost:8501/_stcore/health

## Features:
- ✅ Multi-stage build for optimized image size
- ✅ Health checks for container monitoring
- ✅ Persistent volumes for data and models
- ✅ Resource limits and restart policies
- ✅ Environment variable configuration
- ✅ Automatic database initialization
- ✅ Language model pre-loading
