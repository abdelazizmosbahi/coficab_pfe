# 🚀 Quick Reference - Docker + GitHub Actions

**Copy-Paste Commands for Fast Deployment**

---

## 📋 One-Time Setup (DevOps)

```bash
# 1. Create GitHub PAT
# → https://github.com/settings/tokens
# → Generate new classic token
# → Scopes: read:packages, write:packages
# → Copy the token

# 2. Add secret to repository
# → Repository Settings → Secrets and variables → Actions
# → New secret: GHCR_TOKEN = [your-token]

# 3. Push to main (triggers workflow)
git add .
git commit -m "Add Docker + GitHub Actions pipeline"
git push origin main

# 4. Verify workflow
# → https://github.com/yourusername/coficab_ai_agent/actions
```

---

## 🐳 Local Development

```bash
# First time
cp .env.example .env
# Edit .env with database credentials

# Start application
docker-compose up -d

# View logs
docker-compose logs -f cable-ai

# Stop
docker-compose down
```

---

## 📦 Production Deployment

```bash
# Pull latest image from GHCR
docker-compose pull

# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f cable-ai

# Verify health
docker-compose ps
curl http://localhost:8501
```

---

## 🔧 Troubleshooting

```bash
# Check status
docker-compose ps
docker-compose logs cable-ai

# Restart container
docker-compose restart cable-ai

# Full restart
docker-compose down
docker-compose up -d

# Test database connection
docker-compose exec cable-ai \
  python -c "import pyodbc; print('OK')"

# View container resource usage
docker stats cable-ai

# Remove everything and restart fresh
docker-compose down -v
docker-compose up -d
```

---

## 🔑 Environment Variables

```env
DB_HOST=your-sql-server.database.windows.net
DB_PORT=1433
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=cable_manufacturing
MISTRAL_API_KEY=your-mistral-key
```

---

## 📊 Verify Setup

```bash
# Linux/macOS
bash verify-setup.sh

# Windows PowerShell
.\verify-setup.ps1
```

---

## 🐳 Manual Docker Commands

```bash
# Login to GHCR
docker login ghcr.io
# Username: your-github-username
# Password: [your-PAT]

# Pull image
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest

# Run with environment file
docker run -d \
  --name cable-ai \
  -p 8501:8501 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/yourusername/cable-maintenance-ai:latest

# View logs
docker logs -f cable-ai

# Stop and remove
docker stop cable-ai
docker rm cable-ai
```

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `cable_maintenance_ai/Dockerfile` | Container definition |
| `docker-compose.yml` | Local & prod orchestration |
| `.env.example` | Config template |
| `.env` | Your secrets (never commit!) |
| `.github/workflows/docker-build-push.yml` | CI/CD workflow |
| `DEPLOYMENT.md` | Full deployment guide |
| `GITHUB_ACTIONS_SETUP.md` | GitHub setup guide |
| `verify-setup.sh` | Verify setup (Linux/macOS) |
| `verify-setup.ps1` | Verify setup (Windows) |

---

## 🔗 Image Tags

```bash
# Pull by tag
docker pull ghcr.io/yourusername/cable-maintenance-ai:latest
docker pull ghcr.io/yourusername/cable-maintenance-ai:main-abc123def
docker pull ghcr.io/yourusername/cable-maintenance-ai:main
```

---

## ⏱️ Common Task Times

| Task | Time |
|------|------|
| First build (no cache) | 2-5 min |
| Subsequent builds | 30 sec - 2 min |
| Docker pull | 1-2 min |
| docker-compose up | 10-30 sec |
| Health check pass | 15-40 sec |

---

## 📚 Full Guides

- **DEPLOYMENT.md** - Complete supervisor guide (50+ steps)
- **GITHUB_ACTIONS_SETUP.md** - GitHub CI/CD setup (8 steps)
- **DOCKER_GITHUB_ACTIONS_SUMMARY.md** - Architecture overview

---

## ✅ Checklist Before Going Live

- [ ] GitHub PAT created
- [ ] GHCR_TOKEN secret added
- [ ] Changes pushed to main
- [ ] Workflow completes successfully
- [ ] Image appears in GHCR
- [ ] Local test: `docker-compose up -d` works
- [ ] Local test: App accessible at http://localhost:8501
- [ ] Database connection verified
- [ ] Health check passes
- [ ] `.env` file properly configured
- [ ] `.env` file in `.gitignore`

---

## 🎯 Quick Links

- 🔗 [GitHub Container Registry](https://github.com/yourusername/coficab_ai_agent/pkgs/container/cable-maintenance-ai)
- 🔗 [GitHub Actions Workflow](https://github.com/yourusername/coficab_ai_agent/actions)
- 🔗 [Repository Settings](https://github.com/yourusername/coficab_ai_agent/settings/secrets/actions)
- 🔗 [Docker Hub](https://hub.docker.com/)

---

## 💡 Pro Tips

```bash
# Check image size
docker images ghcr.io/yourusername/cable-maintenance-ai

# Export container state
docker-compose exec cable-ai ls -la /app

# Run one-off command in container
docker-compose exec cable-ai python -c "print('Hello')"

# View container IP
docker-compose exec cable-ai hostname -I

# Pin to specific commit
IMAGE_TAG=main-abc123def docker-compose up -d
```

---

**Questions?** Check the full guides above.  
**Last Updated**: May 19, 2026
