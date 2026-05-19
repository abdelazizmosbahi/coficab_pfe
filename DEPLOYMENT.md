# 📦 Cable Manufacturing AI - Deployment Guide

**For Supervisors & DevOps Teams**

This guide explains how to pull and run the pre-built Docker image for the Cable Manufacturing AI system.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software
- **Docker** (version 20.10 or later) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0 or later) - [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** (for cloning the repository)

### Verify Installation
```bash
docker --version
docker-compose --version
```

### Network Access
- Access to **GitHub Container Registry (ghcr.io)**
- Access to your **SQL Server** database
- Access to **Mistral AI API** (if using AI features)

---

## 🚀 Quick Start

### Option 1: Using docker-compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/coficab_ai_agent.git
cd coficab_ai_agent

# 2. Create environment file
cp .env.example .env
# Edit .env with your database and API credentials

# 3. Start the application
docker-compose up -d

# 4. Check if it's running
docker-compose ps
docker-compose logs -f cable-ai
```

The application will be available at: **http://localhost:8501**

### Option 2: Using Docker directly

```bash
# 1. Log in to GitHub Container Registry (first time only)
docker login ghcr.io
# Enter username and GitHub Personal Access Token

# 2. Pull the latest image
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest

# 3. Run the container
docker run -d \
  --name cable-ai \
  -p 8501:8501 \
  -e DB_HOST=your-server.database.windows.net \
  -e DB_PORT=1433 \
  -e DB_USER=your-username \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=cable_manufacturing \
  -e MISTRAL_API_KEY=your-mistral-key \
  --restart unless-stopped \
  ghcr.io/yourusername/cable-maintenance-ai:latest
```

---

## 🔧 Detailed Setup Instructions

### Step 1: Create Environment File

```bash
cd coficab_ai_agent
cp .env.example .env
```

Edit the `.env` file with your actual values:

```env
# Database Configuration
DB_HOST=your-sql-server.database.windows.net
DB_PORT=1433
DB_USER=your-database-username
DB_PASSWORD=your-database-password
DB_NAME=cable_manufacturing

# AI Service Configuration
MISTRAL_API_KEY=your-mistral-api-key-here
```

### Step 2: GitHub Container Registry Authentication

#### Option A: Using Personal Access Token (Recommended)

```bash
# Generate a token at: https://github.com/settings/tokens
# Scopes needed: read:packages

docker login ghcr.io
# When prompted:
#   Username: your-github-username
#   Password: your-github-personal-access-token
```

#### Option B: Using GitHub Actions (Automatic in CI/CD)

The GitHub Actions workflow automatically handles authentication.

### Step 3: Pull the Image

```bash
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest

# Or pull a specific version (e.g., git commit SHA)
docker pull ghcr.io/yourusername/cable-maintenance-ai:main-abc123def
```

---

## ⚙️ Configuration

### Environment Variables (`.env` file)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | ✅ Yes | - | SQL Server hostname or IP |
| `DB_PORT` | ✅ Yes | 1433 | SQL Server port |
| `DB_USER` | ✅ Yes | - | Database username (SQL authentication) |
| `DB_PASSWORD` | ✅ Yes | - | Database password |
| `DB_NAME` | ✅ Yes | cable_manufacturing | Database name |
| `MISTRAL_API_KEY` | ✅ Yes | - | API key for Mistral AI |

### Streamlit Configuration (automatic)

The following are pre-configured in the Docker image:
- **Server port**: 8501
- **Server address**: 0.0.0.0 (accessible from any interface)
- **Headless mode**: Enabled (no browser auto-open)
- **Toolbar**: Hidden
- **Sidebar**: Collapsed by default

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:
- **Port mapping** (change `8501:8501` if needed)
- **Resource limits** (CPU/memory constraints)
- **Logging options** (log rotation, level)
- **Restart policy** (change `unless-stopped` if needed)

---

## ▶️ Running the Application

### Using docker-compose

```bash
# Start in background
docker-compose up -d

# View live logs
docker-compose logs -f cable-ai

# Stop the application
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Docker directly

```bash
# Run with detached mode
docker run -d \
  --name cable-ai \
  -p 8501:8501 \
  -e DB_HOST=... \
  -e DB_PORT=... \
  -e DB_USER=... \
  -e DB_PASSWORD=... \
  -e DB_NAME=... \
  -e MISTRAL_API_KEY=... \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ghcr.io/yourusername/cable-maintenance-ai:latest

# View logs
docker logs -f cable-ai

# Stop the container
docker stop cable-ai
docker rm cable-ai
```

---

## 📊 Monitoring & Troubleshooting

### Check Application Status

```bash
# Using docker-compose
docker-compose ps

# Using Docker
docker ps | grep cable-ai

# Check health
docker inspect --format="{{.State.Health.Status}}" cable-ai
```

### View Logs

```bash
# Last 100 lines
docker-compose logs -n 100 cable-ai

# Stream logs with timestamps
docker-compose logs -f --timestamps cable-ai

# Filter logs (e.g., errors only)
docker-compose logs cable-ai | grep -i error
```

### Common Issues

#### Issue 1: Connection refused (port 8501)
```bash
# Check if container is running
docker-compose ps

# Check port mapping
docker-compose port cable-ai 8501

# Try rebuilding the image
docker-compose build --no-cache
docker-compose up -d
```

#### Issue 2: Database connection error
```bash
# Verify .env file settings
cat .env

# Test database connectivity from container
docker-compose exec cable-ai \
  python -c "import pyodbc; print('Connection OK')"

# Check if database is accessible from your network
nslookup your-sql-server.database.windows.net
```

#### Issue 3: High memory usage
```bash
# Check container stats
docker stats cable-ai

# Restart container
docker-compose restart cable-ai

# Increase memory limits in docker-compose.yml:
#   deploy:
#     resources:
#       limits:
#         memory: 3G
```

#### Issue 4: Image not found
```bash
# Ensure you're logged in to GHCR
docker login ghcr.io

# Verify image exists
docker image ls | grep cable-maintenance-ai

# Pull the latest image
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest
```

### Restart Strategy

```bash
# Soft restart (keeps data)
docker-compose restart cable-ai

# Hard restart (recreates container)
docker-compose down
docker-compose up -d

# Clean restart (removes all)
docker-compose down -v
docker-compose up -d
```

---

## 🏭 Production Deployment

### Recommended Settings

```yaml
# docker-compose.yml - Production config
services:
  cable-ai:
    image: ghcr.io/yourusername/cable-maintenance-ai:latest
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Deployment Workflow

```bash
# 1. Pull latest code
git pull origin main

# 2. Verify .env file is properly configured
cat .env

# 3. Pull latest image from GHCR
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest

# 4. Create new container (old one stops gracefully)
docker-compose up -d

# 5. Verify deployment
docker-compose ps
curl http://localhost:8501

# 6. Monitor logs
docker-compose logs -f cable-ai
```

### Automated Updates

Set up a cron job to pull and deploy the latest image:

```bash
# Create /home/deploy/update-cable-ai.sh
#!/bin/bash
cd /path/to/coficab_ai_agent
docker-compose pull
docker-compose up -d
docker-compose logs -f cable-ai

# Make executable
chmod +x /home/deploy/update-cable-ai.sh

# Add to crontab (e.g., daily at 2 AM)
0 2 * * * /home/deploy/update-cable-ai.sh >> /var/log/cable-ai-update.log 2>&1
```

### Using Specific Image Versions

```bash
# Pull a specific version by git commit SHA
docker pull ghcr.io/yourusername/cable-maintenance-ai:main-abc123def

# Update docker-compose.yml
image: ghcr.io/yourusername/cable-maintenance-ai:main-abc123def

# Deploy
docker-compose up -d
```

### Backup Before Deployment

```bash
# Export current database state (if needed)
docker-compose exec cable-ai \
  python -c "import backup_module; backup_module.backup_db()"

# Keep previous image
docker tag ghcr.io/yourusername/cable-maintenance-ai:latest \
           ghcr.io/yourusername/cable-maintenance-ai:latest-backup
```

---

## 📝 Useful Commands Reference

```bash
# View image details
docker inspect ghcr.io/yourusername/cable-maintenance-ai:latest

# View image layers and history
docker history ghcr.io/yourusername/cable-maintenance-ai:latest

# Remove old/unused images
docker image prune

# Run container with interactive shell (for debugging)
docker run -it --rm \
  -e DB_HOST=... \
  ghcr.io/yourusername/cable-maintenance-ai:latest \
  /bin/bash

# Check disk usage
docker system df

# Clean up everything
docker system prune -a
```

---

## 📞 Support & Issues

- **GitHub Issues**: [Report a bug](https://github.com/yourusername/coficab_ai_agent/issues)
- **Documentation**: See `README.md` for architecture and features
- **CI/CD Logs**: Check [GitHub Actions](https://github.com/yourusername/coficab_ai_agent/actions) for build status

---

## 📄 License

[Your License Here]

---

**Last Updated**: May 19, 2026
