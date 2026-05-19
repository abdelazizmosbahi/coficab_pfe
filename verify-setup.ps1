# ========================================
# Cable Manufacturing AI - Setup Verification Script (PowerShell)
# Ensures all files are in place and properly configured
# ========================================

$global:PASSED = 0
$global:FAILED = 0
$global:WARNINGS = 0

# Helper functions
function Write-Pass($msg) {
    Write-Host "✓ $msg" -ForegroundColor Green
    $global:PASSED++
}

function Write-Fail($msg) {
    Write-Host "✗ $msg" -ForegroundColor Red
    $global:FAILED++
}

function Write-Warning($msg) {
    Write-Host "⚠ $msg" -ForegroundColor Yellow
    $global:WARNINGS++
}

function Check-File($file, $description) {
    if (Test-Path $file) {
        Write-Pass $description
    } else {
        Write-Fail "$description (NOT FOUND: $file)"
    }
}

function Check-Directory($dir, $description) {
    if (Test-Path $dir -PathType Container) {
        Write-Pass $description
    } else {
        Write-Fail "$description (NOT FOUND: $dir)"
    }
}

function Check-Content($file, $pattern, $description) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match $pattern) {
            Write-Pass $description
        } else {
            Write-Warning "$description (PATTERN NOT FOUND)"
        }
    }
}

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 Docker + GitHub Actions Verification (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# Check Files
# ========================================
Write-Host "📁 Checking files..." -ForegroundColor Magenta
Write-Host ""

Check-File "cable_maintenance_ai/Dockerfile" "Dockerfile exists"
Check-Content "cable_maintenance_ai/Dockerfile" "ODBC" "Dockerfile includes ODBC Driver 18"
Check-Content "cable_maintenance_ai/Dockerfile" "useradd" "Dockerfile includes non-root user"
Check-Content "cable_maintenance_ai/Dockerfile" "HEALTHCHECK" "Dockerfile includes health check"

Check-File "docker-compose.yml" "docker-compose.yml exists"
Check-Content "docker-compose.yml" "DB_HOST" "docker-compose.yml includes database config"
Check-Content "docker-compose.yml" "MISTRAL_API_KEY" "docker-compose.yml includes Mistral config"

Check-File ".env.example" ".env.example exists"
Check-File ".github/workflows/docker-build-push.yml" "GitHub Actions workflow exists"
Check-Content ".github/workflows/docker-build-push.yml" "REGISTRY: ghcr.io" "Workflow targets GHCR"
Check-Content ".github/workflows/docker-build-push.yml" "trivy" "Workflow includes Trivy security scan"

Check-File "DEPLOYMENT.md" "DEPLOYMENT.md documentation exists"
Check-File "GITHUB_ACTIONS_SETUP.md" "GITHUB_ACTIONS_SETUP.md documentation exists"

Write-Host ""

# ========================================
# Check Directories
# ========================================
Write-Host "📂 Checking directories..." -ForegroundColor Magenta
Write-Host ""

Check-Directory ".github" ".github directory exists"
Check-Directory ".github/workflows" ".github/workflows directory exists"
Check-Directory "cable_maintenance_ai" "cable_maintenance_ai directory exists"

Write-Host ""

# ========================================
# Check .gitignore
# ========================================
Write-Host "🔒 Checking security (.gitignore)..." -ForegroundColor Magenta
Write-Host ""

if (Test-Path ".gitignore") {
    $gitignore = Get-Content ".gitignore" -Raw
    if ($gitignore -match "\.env$") {
        Write-Pass ".env file is ignored (won't be committed)"
    } else {
        Write-Warning ".env might be committed (add to .gitignore)"
    }
    
    if ($gitignore -match "\.env\.local") {
        Write-Pass ".env.local is ignored"
    } else {
        Write-Warning "Consider adding .env.local to .gitignore"
    }
} else {
    Write-Fail ".gitignore file not found"
}

Write-Host ""

# ========================================
# Check Docker/Docker Compose
# ========================================
Write-Host "🐳 Checking Docker installation..." -ForegroundColor Magenta
Write-Host ""

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
    $dockerVersion = & docker --version
    Write-Pass "Docker installed: $dockerVersion"
} else {
    Write-Fail "Docker not installed"
}

$compose = Get-Command docker-compose -ErrorAction SilentlyContinue
if ($compose) {
    $composeVersion = & docker-compose --version
    Write-Pass "Docker Compose installed: $composeVersion"
} else {
    Write-Fail "Docker Compose not installed"
}

Write-Host ""

# ========================================
# Check Git
# ========================================
Write-Host "📝 Checking Git configuration..." -ForegroundColor Magenta
Write-Host ""

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $gitVersion = & git --version
    Write-Pass "Git installed: $gitVersion"
    
    $gitDir = & git rev-parse --git-dir 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Git repository initialized"
        
        $remote = & git config --get remote.origin.url 2>$null
        if ($remote) {
            Write-Pass "Git remote configured: $remote"
        } else {
            Write-Warning "No git remote configured (configure with: git remote add origin <url>)"
        }
    } else {
        Write-Fail "Not a git repository"
    }
} else {
    Write-Fail "Git not installed"
}

Write-Host ""

# ========================================
# Validation Summary
# ========================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 Verification Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "✓ Passed: $global:PASSED" -ForegroundColor Green
if ($global:WARNINGS -gt 0) {
    Write-Host "⚠ Warnings: $global:WARNINGS" -ForegroundColor Yellow
}
if ($global:FAILED -gt 0) {
    Write-Host "✗ Failed: $global:FAILED" -ForegroundColor Red
}
Write-Host ""

# ========================================
# Next Steps
# ========================================
if ($global:FAILED -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣  GitHub Setup (One-time):" -ForegroundColor Yellow
    Write-Host "   - Follow GITHUB_ACTIONS_SETUP.md"
    Write-Host "   - Create Personal Access Token"
    Write-Host "   - Add GHCR_TOKEN secret"
    Write-Host ""
    Write-Host "2️⃣  Commit and Push:" -ForegroundColor Yellow
    Write-Host "   git add ."
    Write-Host "   git commit -m 'Add Docker + GitHub Actions pipeline'"
    Write-Host "   git push origin main"
    Write-Host ""
    Write-Host "3️⃣  Monitor Workflow:" -ForegroundColor Yellow
    Write-Host "   - Visit: https://github.com/yourusername/coficab_ai_agent/actions"
    Write-Host "   - Verify build completes successfully"
    Write-Host ""
    Write-Host "4️⃣  Deploy (for Supervisor):" -ForegroundColor Yellow
    Write-Host "   cp .env.example .env"
    Write-Host "   # Edit .env with credentials"
    Write-Host "   docker-compose up -d"
    Write-Host ""
    Write-Host "5️⃣  Verify Running:" -ForegroundColor Yellow
    Write-Host "   docker-compose ps"
    Write-Host "   docker-compose logs -f cable-ai"
    Write-Host ""
} else {
    Write-Host "❌ Some checks failed. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Ensure you're in the project root directory"
    Write-Host "  - Run: git clone <repo>"
    Write-Host "  - Install Docker and Docker Compose"
    Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  - DEPLOYMENT.md - For supervisors" -ForegroundColor Gray
Write-Host "  - GITHUB_ACTIONS_SETUP.md - For setup" -ForegroundColor Gray
Write-Host "  - DOCKER_GITHUB_ACTIONS_SUMMARY.md - Overview" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

exit $global:FAILED
