# 🚀 CI/CD Quick Start Guide

**Quick reference cho việc sử dụng CI/CD pipeline của Digital Utopia Platform**

---

## ⚡ Quick Commands

### Backend Testing
```bash
# Chạy tests
cd backend
pytest tests/ -v

# Với coverage
pytest tests/ --cov=app --cov-report=html

# Chỉ chạy một test file
pytest tests/test_auth_integration.py -v

# Security scan
bandit -r app/
safety check -r requirements.txt
```

### Frontend Build
```bash
# Client App
cd client-app
npm ci
npm run build

# Admin App
cd Admin-app
npm ci
npm run build
```

### Docker
```bash
# Build tất cả services
docker-compose build

# Start services
docker-compose up -d

# Xem logs
docker-compose logs -f backend

# Health check
curl http://localhost:8000/health

# Stop và cleanup
docker-compose down -v
```

---

## 🔍 CI/CD Status Check

### View Workflows
1. Truy cập: https://github.com/mariecalallen12/forex4/actions
2. Chọn workflow muốn xem
3. Click vào run để xem chi tiết
4. Review logs và artifacts

### Common Workflows

| Workflow | Khi nào chạy | Thời gian |
|----------|--------------|-----------|
| **Status Check** | Mọi push | ~2 phút |
| **Backend CI** | Push backend/ | ~10 phút |
| **Frontend CI** | Push client-app/ hoặc Admin-app/ | ~8 phút |
| **Integration Test** | Push main/develop, daily | ~15 phút |

---

## 🐛 Debugging Failed Workflows

### Backend CI Failed

**1. Check Logs:**
```
Actions → Backend CI → Click failed run → Expand failed step
```

**2. Common Issues:**
- ❌ **Test failed**: Check test logs, verify database connection
- ❌ **Lint failed**: Run `black .` và `isort .` locally
- ❌ **Security issue**: Review Bandit report in artifacts

**3. Fix Locally:**
```bash
cd backend
# Run what failed
pytest tests/ -v              # If tests failed
black .                       # If formatting failed
bandit -r app/               # If security scan failed
```

### Frontend CI Failed

**1. Common Issues:**
- ❌ **Build failed**: Check for syntax errors, missing dependencies
- ❌ **Docker build failed**: Check Dockerfile, verify build context

**2. Fix Locally:**
```bash
cd client-app  # or Admin-app
npm ci
npm run build
# Fix any errors shown
```

### Docker Compose Failed

**1. Check Locally:**
```bash
docker-compose up --build
# Watch for errors in output
docker-compose logs backend
docker-compose logs postgres
```

**2. Common Fixes:**
- Missing `.env` file → Create from `.env.example`
- Port conflict → Stop other services using same ports
- Database error → Check credentials in `.env`

---

## 📊 Viewing Reports

### Test Coverage
1. Go to: Actions → Backend CI → Latest run
2. Download: `coverage-report` artifact
3. Extract and open: `htmlcov/index.html`

### Security Reports
1. Go to: Repository → Security tab
2. View: Code scanning alerts, Dependabot alerts
3. Review: Trivy scan results in artifacts

### Build Artifacts
1. Go to: Actions → Workflow run
2. Scroll down to: Artifacts section
3. Download: Available for 7-90 days depending on type

---

## 🚀 Manual Deployment

### Trigger Deployment

**Method 1: Via GitHub UI**
```
1. Go to Actions → Deployment workflow
2. Click "Run workflow"
3. Select branch: main
4. Choose environment: staging or production
5. Click "Run workflow"
```

**Method 2: Via Tag**
```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This triggers production deployment automatically
```

### Monitor Deployment
```
1. Go to Actions → Deployment
2. Watch progress in real-time
3. Check each job status
4. Review deployment summary
```

---

## 🔐 Secrets Configuration

### Required Secrets

**For Deployment (Settings → Secrets → Actions):**
```
# Staging
STAGING_HOST          # Staging server hostname
STAGING_USER          # SSH username
STAGING_SSH_KEY       # SSH private key

# Production
PRODUCTION_HOST       # Production server hostname
PRODUCTION_USER       # SSH username
PRODUCTION_SSH_KEY    # SSH private key

# Optional
SLACK_WEBHOOK         # For notifications
DOCKER_USERNAME       # If using Docker Hub
DOCKER_PASSWORD       # If using Docker Hub
```

---

## 📈 Monitoring

### Daily Checks
- Check Actions tab for failed workflows
- Review Security tab for vulnerabilities
- Check Dependabot PRs for updates

### Weekly Reviews
- Review coverage trends
- Check performance metrics
- Update dependencies if needed

### Monthly Tasks
- Review all security scans
- Update documentation
- Optimize workflows if needed

---

## 🆘 Getting Help

### Documentation
- 📖 [Full CI/CD Guide](CI_CD_WORKFLOW_GUIDE.md)
- 📖 [Deployment Guide](DEPLOYMENT_GUIDE.md)
- 📖 [Docker Guide](DOCKER_DEPLOYMENT.md)

### Support Channels
1. Create issue in repository
2. Check existing issues for solutions
3. Review workflow logs carefully
4. Test locally before pushing

---

## ✅ Pre-Push Checklist

### Before Every Push
```bash
# 1. Test backend
cd backend
pytest tests/

# 2. Check frontend builds
cd ../client-app && npm run build
cd ../Admin-app && npm run build

# 3. Test Docker
docker-compose up --build -d
curl http://localhost:8000/health

# 4. Check git status
git status
git diff

# 5. Commit and push
git add .
git commit -m "Your message"
git push
```

### For Production
- [ ] All tests passing locally
- [ ] No security warnings
- [ ] Docker builds successfully
- [ ] Documentation updated
- [ ] Tag created for release
- [ ] Team notified

---

## 🎯 Tips & Best Practices

### Commits
- ✅ Make small, focused commits
- ✅ Write clear commit messages
- ✅ Test before committing
- ❌ Don't commit `.env` files
- ❌ Don't commit secrets

### Pull Requests
- ✅ Wait for CI to pass before merging
- ✅ Review security scan results
- ✅ Check coverage reports
- ✅ Test integration locally
- ❌ Don't bypass failed checks

### Workflow Optimization
- Re-run only failed jobs when possible
- Use workflow caching (already configured)
- Skip workflows when not needed (path filters active)
- Review workflow duration regularly

---

**📝 Last Updated:** 06/12/2025  
**📚 Full Documentation:** [CI_CD_WORKFLOW_GUIDE.md](CI_CD_WORKFLOW_GUIDE.md)
