# 🔄 CI/CD Workflow Guide - Digital Utopia Platform

**Phiên bản:** 1.0.0  
**Ngày tạo:** 06/12/2025  
**Mục đích:** Hướng dẫn đầy đủ về quy trình CI/CD và công cụ GitHub Actions

---

## 📋 MỤC LỤC

1. [Tổng Quan](#1-tổng-quan)
2. [GitHub Actions Workflows](#2-github-actions-workflows)
3. [Backend CI/CD](#3-backend-cicd)
4. [Frontend CI/CD](#4-frontend-cicd)
5. [Integration Testing](#5-integration-testing)
6. [Deployment Process](#6-deployment-process)
7. [Monitoring & Maintenance](#7-monitoring--maintenance)
8. [Status Badges](#8-status-badges)
9. [Local Testing](#9-local-testing)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. TỔNG QUAN

### 1.1. Mục Đích Hệ Thống CI/CD

Hệ thống CI/CD được thiết kế để:
- ✅ Tự động kiểm tra code quality và security
- ✅ Chạy tests tự động khi có thay đổi code
- ✅ Build và test Docker images
- ✅ Triển khai tự động lên staging/production
- ✅ Giám sát và báo cáo real-time
- ✅ Đánh giá chính xác tình trạng dự án

### 1.2. Công Cụ GitHub Được Sử Dụng

| Công Cụ | Mục Đích | Status |
|---------|----------|--------|
| **GitHub Actions** | CI/CD automation | ✅ Active |
| **GitHub Packages** | Container registry | ✅ Active |
| **GitHub Security** | Security scanning (CodeQL, Dependabot) | ✅ Active |
| **GitHub Pages** | Documentation hosting | 🔄 Optional |
| **GitHub Environments** | Deployment management | ✅ Active |
| **GitHub Artifacts** | Build artifacts storage | ✅ Active |

---

## 2. GITHUB ACTIONS WORKFLOWS

### 2.1. Danh Sách Workflows

#### 🔵 **backend-ci.yml** - Backend CI/CD Pipeline
- **Trigger**: Push to backend/, PRs, manual
- **Jobs**:
  - `lint`: Code formatting check (Black, isort, Flake8)
  - `security`: Security scanning (Bandit, Safety)
  - `test`: Unit & integration tests with coverage
  - `build`: Docker image build
  - `health-check`: Container health verification
  - `summary`: CI results summary

#### 🟢 **frontend-ci.yml** - Frontend CI/CD Pipeline
- **Trigger**: Push to client-app/ or Admin-app/, PRs, manual
- **Jobs**:
  - `lint-client`: Client app linting
  - `build-client`: Client app build & size analysis
  - `docker-client`: Client Docker image build
  - `lint-admin`: Admin app linting
  - `build-admin`: Admin app build & size analysis
  - `docker-admin`: Admin Docker image build
  - `test-integration`: API integration tests
  - `summary`: Frontend CI summary

#### 🟣 **integration-test.yml** - Integration & E2E Testing
- **Trigger**: Push to main/develop, PRs, daily schedule (2 AM UTC)
- **Jobs**:
  - `docker-compose-test`: Full stack integration test
  - `performance-test`: Load testing with Apache Bench
  - `security-scan`: Container security with Trivy
  - `summary`: Integration test summary

#### 🔴 **deploy.yml** - Deployment Pipeline
- **Trigger**: Push to main, tags (v*.*.*), manual
- **Jobs**:
  - `prepare`: Determine environment & version
  - `build-and-push`: Build & push images to registry
  - `deploy-staging`: Deploy to staging environment
  - `deploy-production`: Deploy to production (with approval)
  - `post-deployment`: Post-deployment tasks & notifications

#### 🟡 **monitoring.yml** - Monitoring & Maintenance
- **Trigger**: Daily schedule (1 AM UTC), manual
- **Jobs**:
  - `dependency-check`: Check for vulnerabilities
  - `code-quality`: CodeQL analysis & code statistics
  - `docker-image-scan`: Security scanning for images
  - `health-check`: Repository health metrics
  - `update-dependencies`: Check for outdated packages
  - `summary`: Daily monitoring summary

#### 🟠 **status-check.yml** - Quick Status Check
- **Trigger**: All pushes, PRs, manual
- **Jobs**:
  - `quick-check`: Fast health check (< 5 minutes)
    - File structure verification
    - Docker configuration check
    - Backend/Frontend configuration
    - Security quick scan
    - CI/CD workflow verification

---

## 3. BACKEND CI/CD

### 3.1. Linting & Code Quality

```bash
# Local testing commands
cd backend

# Run Black formatter
black --check .

# Run isort
isort --check-only .

# Run Flake8
flake8 app/ --max-line-length=127
```

### 3.2. Security Scanning

```bash
# Bandit security scanner
bandit -r app/ -f screen

# Check dependencies
safety check -r requirements.txt
```

### 3.3. Testing

```bash
# Run simple tests
python simple_test.py

# Run full test suite with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

**Test Requirements:**
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- Environment variables configured

**Coverage Reports:**
- HTML: `backend/htmlcov/index.html`
- XML: `backend/coverage.xml`
- Uploaded as GitHub artifact

### 3.4. Docker Build

```bash
# Build backend image
docker build -t forex4-backend:test ./backend

# Test container
docker run -d --name test-backend \
  -e SECRET_KEY=test \
  -e POSTGRES_SERVER=postgres \
  -p 8000:8000 \
  forex4-backend:test

# Health check
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## 4. FRONTEND CI/CD

### 4.1. Client App Build

```bash
cd client-app

# Install dependencies
npm ci

# Build production
npm run build

# Check build size
du -sh dist/
```

**Build Outputs:**
- Production build: `client-app/dist/`
- Size analysis in CI summary
- Artifact uploaded for 7 days

### 4.2. Admin App Build

```bash
cd Admin-app

# Install dependencies
npm ci

# Build production
npm run build

# Preview build
npm run preview
```

### 4.3. Docker Build

```bash
# Build client app
docker build -t forex4-client:test \
  --build-arg VITE_API_BASE_URL=http://localhost:8000 \
  ./client-app

# Build admin app
docker build -t forex4-admin:test \
  --build-arg VITE_API_BASE_URL=http://localhost:8000 \
  ./Admin-app
```

---

## 5. INTEGRATION TESTING

### 5.1. Docker Compose Test

**Full Stack Test:**
```bash
# Create directories
mkdir -p data/postgres data/redis backend/uploads backend/logs

# Create .env file
cp .env.example .env
# Edit .env with test credentials

# Start services
docker-compose up -d

# Wait for services
sleep 30

# Health checks
curl http://localhost:8000/health    # Backend
curl http://localhost:3000           # Client
curl http://localhost:3001           # Admin

# View logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# Cleanup
docker-compose down -v
```

### 5.2. Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test API endpoints
ab -n 1000 -c 10 http://localhost:8000/
```

**Performance Metrics:**
- Requests per second
- Time per request
- Connection times
- Results in CI summary

### 5.3. Security Scanning

**Trivy Scanner:**
```bash
# Scan backend image
trivy image forex4-backend:latest

# Scan client image
trivy image forex4-client:latest

# Scan configuration
trivy config ./backend
trivy config ./client-app
```

---

## 6. DEPLOYMENT PROCESS

### 6.1. Environments

| Environment | Branch | Approval Required | URL |
|-------------|--------|-------------------|-----|
| **Development** | Any branch | No | Local |
| **Staging** | develop, main | No | staging.yourdomain.com |
| **Production** | main, tags | Yes | yourdomain.com |

### 6.2. Deployment Workflow

1. **Automatic Triggers:**
   - Push to `main` → Staging deployment
   - Tag `v*.*.*` → Production deployment

2. **Manual Deployment:**
   ```yaml
   # Go to Actions → Deployment → Run workflow
   # Select environment: staging or production
   ```

3. **Image Tagging:**
   ```
   ghcr.io/mariecalallen12/forex4-backend:latest
   ghcr.io/mariecalallen12/forex4-backend:v1.0.0
   ghcr.io/mariecalallen12/forex4-backend:main-abc123
   ```

### 6.3. Production Deployment Checklist

- [ ] All CI tests passing
- [ ] Security scans completed
- [ ] Database migrations prepared
- [ ] Backup completed
- [ ] Rollback plan documented
- [ ] Team notified
- [ ] Monitoring dashboards ready
- [ ] Manual approval obtained

### 6.4. Rollback Procedure

```bash
# Method 1: Deploy previous tag
git tag -l  # List tags
# Trigger deployment with previous tag

# Method 2: Revert commit
git revert <commit-hash>
git push origin main

# Method 3: Manual rollback
docker-compose down
docker-compose pull forex4-backend:v1.0.0
docker-compose up -d
```

---

## 7. MONITORING & MAINTENANCE

### 7.1. Daily Monitoring Jobs

**Automated Checks (1 AM UTC):**
- ✅ Dependency vulnerability scanning
- ✅ Code quality analysis with CodeQL
- ✅ Docker image security scanning
- ✅ Repository health metrics
- ✅ Outdated dependency check

**Reports Available:**
- Security vulnerabilities (Python/Node.js)
- Code statistics (lines of code, complexity)
- Docker image vulnerabilities
- Repository health (TODOs, documentation)
- Dependency updates available

### 7.2. Artifacts & Reports

**Available Artifacts:**

1. **Backend:**
   - `bandit-security-report`: Security scan results
   - `coverage-report`: Test coverage HTML/XML
   - `test-report`: Pytest HTML report
   - `backend-docker-image`: Built Docker image

2. **Frontend:**
   - `client-app-dist`: Production build
   - `admin-app-dist`: Production build

3. **Security:**
   - `python-security-reports`: Safety & pip-audit results
   - `nodejs-security-reports`: npm audit results
   - SARIF files uploaded to Security tab

**Retention:**
- Test reports: 30 days
- Build artifacts: 7 days
- Security reports: 90 days

### 7.3. GitHub Security Features

**CodeQL Analysis:**
- Languages: Python, JavaScript
- Runs on: Daily schedule, PRs
- Results: Security tab

**Dependabot:**
- Automatic PR creation for updates
- Security vulnerability alerts
- Version update suggestions

**Secret Scanning:**
- Automatic detection of exposed secrets
- Alerts for committed credentials

---

## 8. STATUS BADGES

### 8.1. Add to README.md

```markdown
## CI/CD Status

![Backend CI](https://github.com/mariecalallen12/forex4/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/mariecalallen12/forex4/actions/workflows/frontend-ci.yml/badge.svg)
![Integration Test](https://github.com/mariecalallen12/forex4/actions/workflows/integration-test.yml/badge.svg)
![Deployment](https://github.com/mariecalallen12/forex4/actions/workflows/deploy.yml/badge.svg)
![Monitoring](https://github.com/mariecalallen12/forex4/actions/workflows/monitoring.yml/badge.svg)
```

### 8.2. Real-time Monitoring

**GitHub Actions Dashboard:**
- Go to: `https://github.com/mariecalallen12/forex4/actions`
- View: All workflow runs, status, logs
- Filter: By workflow, branch, status

**Workflow Status:**
- 🟢 Success - All jobs passed
- 🔴 Failure - One or more jobs failed
- 🟡 In Progress - Running
- ⚪ Skipped - Conditions not met

---

## 9. LOCAL TESTING

### 9.1. Test Workflows Locally

**Using Act (GitHub Actions Local Runner):**

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -j lint                    # Run specific job
act pull_request              # Simulate PR event
act -l                        # List all jobs

# With secrets
act -s GITHUB_TOKEN=<token>
```

### 9.2. Pre-commit Testing

```bash
# Before committing, run locally:

# Backend
cd backend
black .
isort .
flake8 app/
pytest tests/

# Frontend
cd client-app
npm run build

cd ../Admin-app
npm run build

# Docker
docker-compose up --build
```

### 9.3. Test Docker Compose

```bash
# Full integration test locally
docker-compose -f docker-compose.dev.yml up --build

# Check health
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl http://localhost:3000
curl http://localhost:3001

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

---

## 10. TROUBLESHOOTING

### 10.1. Common Issues

#### ❌ Backend Tests Failing

**Problem:** Database connection error
```
Solution:
- Check PostgreSQL service is running
- Verify environment variables
- Check network connectivity
- Review database migrations
```

**Problem:** Import errors
```
Solution:
- Verify requirements.txt installed
- Check Python version (3.11)
- Rebuild virtual environment
```

#### ❌ Frontend Build Failing

**Problem:** Node modules error
```
Solution:
- Delete node_modules/
- Delete package-lock.json
- Run npm install
- Check Node version (20)
```

**Problem:** Build size too large
```
Solution:
- Check for unnecessary dependencies
- Review imported libraries
- Enable tree-shaking
- Optimize images and assets
```

#### ❌ Docker Build Failing

**Problem:** Context timeout
```
Solution:
- Check .dockerignore
- Reduce build context size
- Use multi-stage builds
- Optimize layer caching
```

**Problem:** Health check failing
```
Solution:
- Increase health check timeout
- Verify service ports
- Check application startup time
- Review service dependencies
```

### 10.2. Debugging Workflows

**View Workflow Logs:**
```
1. Go to Actions tab
2. Click on workflow run
3. Click on failed job
4. Expand failed step
5. View detailed logs
```

**Enable Debug Logging:**
```
Repository Settings → Secrets → Add:
- ACTIONS_RUNNER_DEBUG = true
- ACTIONS_STEP_DEBUG = true
```

**Re-run Failed Jobs:**
```
1. Go to workflow run
2. Click "Re-run failed jobs"
3. Or "Re-run all jobs"
```

### 10.3. Getting Help

**Resources:**
1. [GitHub Actions Documentation](https://docs.github.com/en/actions)
2. [Docker Documentation](https://docs.docker.com/)
3. [FastAPI Documentation](https://fastapi.tiangolo.com/)
4. [Vue.js Documentation](https://vuejs.org/)

**Contact:**
- Create issue in repository
- Check existing issues/discussions
- Review project documentation

---

## 📊 WORKFLOW SUMMARY

### Current Status

| Workflow | Purpose | Frequency | Duration |
|----------|---------|-----------|----------|
| Backend CI | Code quality, tests, build | On push/PR | ~10 mins |
| Frontend CI | Build, lint, Docker | On push/PR | ~8 mins |
| Integration | Full stack test | Daily + PR | ~15 mins |
| Deployment | Deploy to environments | On tag/manual | ~20 mins |
| Monitoring | Security & health | Daily | ~15 mins |
| Status Check | Quick validation | On all pushes | ~2 mins |

### Total Coverage

- ✅ **6 Workflows** configured
- ✅ **29 Jobs** total
- ✅ **100+ Steps** automated
- ✅ **Real-time** status reporting
- ✅ **Automated** deployment pipeline
- ✅ **Comprehensive** security scanning

---

## 🎯 NEXT STEPS

### Recommended Enhancements

1. **Enable GitHub Environments:**
   - Settings → Environments → Add staging/production
   - Configure required reviewers
   - Add environment secrets

2. **Setup Notifications:**
   - Add Slack/Discord webhooks
   - Configure email notifications
   - Setup status monitoring

3. **Configure Auto-merge:**
   - Enable Dependabot auto-merge
   - Setup branch protection rules
   - Configure status checks

4. **Add Custom Actions:**
   - Database migration action
   - Backup automation
   - Performance benchmarking

5. **Implement Staging Server:**
   - Configure SSH access
   - Setup deployment keys
   - Add server credentials to secrets

---

**📝 Note:** Tài liệu này sẽ được cập nhật khi có thay đổi trong quy trình CI/CD.

**🔄 Last Updated:** 06/12/2025  
**✍️ Maintained by:** DevOps Team
