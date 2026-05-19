#!/bin/bash

# ========================================
# Cable Manufacturing AI - Setup Verification Script
# Ensures all files are in place and properly configured
# ========================================

set -e

echo "=========================================="
echo "🔍 Docker + GitHub Actions Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (NOT FOUND: $file)"
        ((FAILED++))
    fi
}

check_directory() {
    local dir=$1
    local description=$2
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (NOT FOUND: $dir)"
        ((FAILED++))
    fi
}

check_content() {
    local file=$1
    local pattern=$2
    local description=$3
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $description (PATTERN NOT FOUND)"
        ((WARNINGS++))
    fi
}

# ========================================
# Check Files
# ========================================
echo "📁 Checking files..."
echo ""

check_file "cable_maintenance_ai/Dockerfile" "Dockerfile exists"
check_content "cable_maintenance_ai/Dockerfile" "ODBC" "Dockerfile includes ODBC Driver 18"
check_content "cable_maintenance_ai/Dockerfile" "useradd" "Dockerfile includes non-root user"
check_content "cable_maintenance_ai/Dockerfile" "HEALTHCHECK" "Dockerfile includes health check"

check_file "docker-compose.yml" "docker-compose.yml exists"
check_content "docker-compose.yml" "DB_HOST" "docker-compose.yml includes database config"
check_content "docker-compose.yml" "MISTRAL_API_KEY" "docker-compose.yml includes Mistral config"

check_file ".env.example" ".env.example exists"
check_file ".github/workflows/docker-build-push.yml" "GitHub Actions workflow exists"
check_content ".github/workflows/docker-build-push.yml" "REGISTRY: ghcr.io" "Workflow targets GHCR"
check_content ".github/workflows/docker-build-push.yml" "trivy" "Workflow includes Trivy security scan"

check_file "DEPLOYMENT.md" "DEPLOYMENT.md documentation exists"
check_file "GITHUB_ACTIONS_SETUP.md" "GITHUB_ACTIONS_SETUP.md documentation exists"

echo ""

# ========================================
# Check Directories
# ========================================
echo "📂 Checking directories..."
echo ""

check_directory ".github" ".github directory exists"
check_directory ".github/workflows" ".github/workflows directory exists"
check_directory "cable_maintenance_ai" "cable_maintenance_ai directory exists"

echo ""

# ========================================
# Check .gitignore
# ========================================
echo "🔒 Checking security (.gitignore)..."
echo ""

if grep -q "\.env$" ".gitignore" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} .env file is ignored (won't be committed)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} .env might be committed (add to .gitignore)"
    ((WARNINGS++))
fi

if grep -q "\.env\.local" ".gitignore" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} .env.local is ignored"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Consider adding .env.local to .gitignore"
    ((WARNINGS++))
fi

echo ""

# ========================================
# Check Docker/Docker Compose
# ========================================
echo "🐳 Checking Docker installation..."
echo ""

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Docker not installed"
    ((FAILED++))
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose installed: $COMPOSE_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Docker Compose not installed"
    ((FAILED++))
fi

echo ""

# ========================================
# Check Git
# ========================================
echo "📝 Checking Git configuration..."
echo ""

if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git installed: $(git --version)"
    ((PASSED++))
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Git repository initialized"
        ((PASSED++))
        
        REMOTE=$(git config --get remote.origin.url 2>/dev/null || echo "NONE")
        if [ "$REMOTE" != "NONE" ]; then
            echo -e "${GREEN}✓${NC} Git remote configured: $REMOTE"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠${NC} No git remote configured (configure with: git remote add origin <url>)"
            ((WARNINGS++))
        fi
    else
        echo -e "${RED}✗${NC} Not a git repository"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Git not installed"
    ((FAILED++))
fi

echo ""

# ========================================
# Validation Summary
# ========================================
echo "=========================================="
echo "📊 Verification Summary"
echo "=========================================="
echo -e "${GREEN}✓ Passed${NC}: $PASSED"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warnings${NC}: $WARNINGS"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed${NC}: $FAILED"
fi
echo ""

# ========================================
# Next Steps
# ========================================
if [ $FAILED -eq 0 ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1️⃣  GitHub Setup (One-time):"
    echo "   - Follow GITHUB_ACTIONS_SETUP.md"
    echo "   - Create Personal Access Token"
    echo "   - Add GHCR_TOKEN secret"
    echo ""
    echo "2️⃣  Commit and Push:"
    echo "   git add ."
    echo "   git commit -m 'Add Docker + GitHub Actions pipeline'"
    echo "   git push origin main"
    echo ""
    echo "3️⃣  Monitor Workflow:"
    echo "   - Visit: https://github.com/yourusername/coficab_ai_agent/actions"
    echo "   - Verify build completes successfully"
    echo ""
    echo "4️⃣  Deploy (for Supervisor):"
    echo "   cp .env.example .env"
    echo "   # Edit .env with credentials"
    echo "   docker-compose up -d"
    echo ""
    echo "5️⃣  Verify Running:"
    echo "   docker-compose ps"
    echo "   docker-compose logs -f cable-ai"
    echo ""
else
    echo "❌ Some checks failed. Please fix the issues above."
    echo ""
    echo "Common fixes:"
    echo "  - Ensure you're in the project root directory"
    echo "  - Run: git clone <repo> && cd coficab_ai_agent"
    echo "  - Install Docker and Docker Compose"
    echo ""
fi

echo "=========================================="
echo "📚 Documentation:"
echo "  - DEPLOYMENT.md - For supervisors"
echo "  - GITHUB_ACTIONS_SETUP.md - For setup"
echo "  - DOCKER_GITHUB_ACTIONS_SUMMARY.md - Overview"
echo "=========================================="
echo ""

exit $FAILED
