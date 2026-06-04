# ✅ GitHub Actions Setup - Complete Checklist

**Step-by-step commands to enable Docker builds and pushes to GHCR**

---

## 🔐 Step 1: Create GitHub Personal Access Token (PAT)

### Why?
GitHub Actions needs credentials to push images to GitHub Container Registry (GHCR).

### Steps:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new classic token"**
3. Set the following:
   - **Token name**: `GHCR_PAT` (or any name you prefer)
   - **Expiration**: 90 days (or longer based on your policy)
   - **Scopes**: Check ONLY:
     - ✅ `read:packages` (to pull images)
     - ✅ `write:packages` (to push images)
     - ✅ `delete:packages` (optional, for cleanup)
4. Click **"Generate token"**
5. **Copy the token** (you won't see it again!)

```bash
# Example token (NEVER share this):
# ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Verify Token Works (Optional)

```bash
# Login to GHCR with your PAT
docker login ghcr.io
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Test push (you can delete this later)
docker pull alpine:latest
docker tag alpine:latest ghcr.io/your-username/test:latest
docker push ghcr.io/your-username/test:latest
```

---

## 🔑 Step 2: Add GitHub Actions Secret

### Why?
Store the PAT securely so the workflow can authenticate without exposing credentials.

### Method 1: Via GitHub Web UI (Recommended)

1. Go to your repository: https://github.com/yourusername/coficab_ai_agent
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Fill in:
   - **Name**: `GHCR_TOKEN`
   - **Value**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (paste your PAT)
5. Click **"Add secret"**

### Method 2: Via GitHub CLI

```bash
# Install GitHub CLI: https://cli.github.com

# Login (if not already)
gh auth login

# Add the secret
gh secret set GHCR_TOKEN --body "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  --repo yourusername/coficab_ai_agent
```

### Verify Secret Added

```bash
# List all secrets
gh secret list --repo yourusername/coficab_ai_agent
```

---

## 📁 Step 3: Prepare Repository Structure

The workflow file is already in place, but verify:

```bash
# Check if files exist
ls -la .github/workflows/docker-build-push.yml
ls -la docker-compose.yml
ls -la cable_maintenance_ai/Dockerfile
ls -la .env.example

# Expected output: All 4 files should exist
```

---

## 🚀 Step 4: Update Workflow File (Update Image Name)

### Edit `.github/workflows/docker-build-push.yml`

Find this line:
```yaml
IMAGE_NAME: ${{ github.repository }}/cable-maintenance-ai
```

**This automatically expands to:** `ghcr.io/your-username/coficab_ai_agent/cable-maintenance-ai`

If you want a shorter name, edit the workflow:

```yaml
# Option 1: Keep auto-generated name
IMAGE_NAME: ${{ github.repository }}/cable-maintenance-ai
# Result: ghcr.io/your-username/coficab_ai_agent/cable-maintenance-ai

# Option 2: Shorter name
IMAGE_NAME: cable-maintenance-ai
# Result: ghcr.io/your-username/cable-maintenance-ai

# Option 3: Custom organization name
IMAGE_NAME: your-org/cable-maintenance-ai
# Result: ghcr.io/your-username/your-org/cable-maintenance-ai
```

**Recommended**: Use Option 1 (automatic) - it's cleaner.

---

## 💾 Step 5: Commit & Push Changes

```bash
# Navigate to repository
cd /path/to/coficab_ai_agent

# Add all new files
git add .
git status  # Verify what will be committed

# Commit changes
git commit -m "feat: Add Docker + GitHub Actions CI/CD pipeline

- Improved Dockerfile with ODBC Driver 18 and security best practices
- Production-ready docker-compose.yml with resource limits
- GitHub Actions workflow for automated builds and GHCR pushes
- Comprehensive deployment documentation
- Environment configuration template"

# Push to main branch (this triggers the workflow!)
git push origin main
```

---

## ✅ Step 6: Verify Workflow Execution

### Option 1: GitHub Web UI

1. Go to your repository: https://github.com/yourusername/coficab_ai_agent
2. Click **Actions** tab
3. You should see the workflow: **"Build and Push Docker Image to GHCR"**
4. Click on the latest run to see logs

### Option 2: GitHub CLI

```bash
# Watch workflow execution live
gh run watch --repo yourusername/coficab_ai_agent

# View latest run status
gh run list --repo yourusername/coficab_ai_agent --limit 5

# View detailed logs of latest run
gh run view --repo yourusername/coficab_ai_agent --log
```

---

## 🎯 Step 7: Manual Workflow Trigger (Optional)

If you want to trigger the build without pushing code:

### Via GitHub Web UI

1. Go to **Actions** tab
2. Click the workflow: **"Build and Push Docker Image to GHCR"**
3. Click **"Run workflow"** → **"Run workflow"**

### Via GitHub CLI

```bash
gh workflow run docker-build-push.yml --repo yourusername/coficab_ai_agent
```

---

## 📦 Step 8: Pull Image & Deploy

Once the workflow completes successfully:

```bash
# Login to GHCR
docker login ghcr.io
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (your PAT)

# Pull the image
docker pull ghcr.io/your-username/cable-maintenance-ai:latest

# Or use docker-compose
cd /path/to/coficab_ai_agent
cp .env.example .env
# Edit .env with your database credentials

docker-compose up -d
docker-compose logs -f cable-ai
```

---

## 🐛 Troubleshooting

### Problem: Workflow fails with "authentication failed"

**Solution**: Verify `GHCR_TOKEN` secret is set correctly:

```bash
# Check if secret exists
gh secret list --repo yourusername/coficab_ai_agent | grep GHCR_TOKEN

# If not present, add it again:
gh secret set GHCR_TOKEN --body "your-pat-token" --repo yourusername/coficab_ai_agent
```

### Problem: "Image not found" when pulling

**Solution**: Ensure workflow completed successfully:

```bash
# Check workflow logs
gh run list --repo yourusername/coficab_ai_agent

# View build log details
gh run view <run-id> --log --repo yourusername/coficab_ai_agent
```

### Problem: "Docker image size too large"

**Solution**: The image is optimized but you can further reduce size:

```dockerfile
# In Dockerfile, use multi-stage build (optional):
FROM python:3.11-slim AS builder
# ... install and build ...

FROM python:3.11-slim
# ... copy only needed files ...
```

### Problem: Build times are slow

**Solution**: The workflow uses GitHub Actions cache automatically. Subsequent builds should be faster:

```bash
# Check cache usage in workflow logs
# Look for: "type=gha,mode=max" lines showing cache hits
```

---

## 📊 Workflow Output Summary

When the workflow runs successfully, you'll see:

```
✅ Checkout repository
✅ Set up Docker Buildx
✅ Log in to GitHub Container Registry
✅ Extract metadata for Docker
✅ Build and push Docker image
✅ Image digest: sha256:abc123...
✅ Run security scan with Trivy
✅ Upload Trivy results to GitHub Security tab
```

---

## 🔗 Image Tags Explained

The workflow creates images with multiple tags:

```bash
# Latest commit on main branch
ghcr.io/your-username/cable-maintenance-ai:latest

# Git commit SHA for pinned deployments
ghcr.io/your-username/cable-maintenance-ai:main-abc123def

# Branch name
ghcr.io/your-username/cable-maintenance-ai:main
```

### Example: Pin to specific commit

```bash
# Update docker-compose.yml
image: ghcr.io/your-username/cable-maintenance-ai:main-abc123def

# Or set environment variable
IMAGE_TAG=main-abc123def docker-compose up -d
```

---

## 🎬 Quick Reference - Common Commands

```bash
# ===== INITIAL SETUP =====
# Create PAT at: https://github.com/settings/tokens
# Add secret "GHCR_TOKEN" in repo settings

# ===== DEPLOYMENT =====
git add .
git commit -m "Deploy Docker image"
git push origin main

# ===== VERIFY =====
gh run list --repo yourusername/coficab_ai_agent

# ===== PULL & RUN =====
docker login ghcr.io
docker pull ghcr.io/your-username/cable-maintenance-ai:latest
docker-compose up -d

# ===== MONITOR =====
docker-compose logs -f cable-ai
docker stats cable-ai
```

---

## ✨ Security Best Practices

1. **Rotate PAT regularly** (every 90 days recommended)
2. **Use separate tokens** for different purposes
3. **Revoke old tokens**: https://github.com/settings/tokens
4. **Never commit `.env` file** (it's in `.gitignore`)
5. **Enable branch protection** rules on `main`
6. **Monitor image security** via Trivy scans (automatic in workflow)

---

## 📚 Additional Resources

- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Trivy Security Scanner](https://aquasecurity.github.io/trivy/)

---

**✅ Setup Complete!** Your CI/CD pipeline is now ready for production.

Questions? Check `DEPLOYMENT.md` for runtime instructions.

---

**Last Updated**: May 19, 2026
