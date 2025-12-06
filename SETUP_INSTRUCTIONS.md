# 🚀 HƯỚNG DẪN KÍCH HOẠT CI/CD - DIGITAL UTOPIA PLATFORM

**Mục đích:** Hướng dẫn từng bước để kích hoạt và sử dụng hệ thống CI/CD đã được cài đặt.

---

## ✅ DANH SÁCH KIỂM TRA

### Đã Hoàn Thành Tự Động ✓
- [x] 6 GitHub Actions workflows đã được tạo
- [x] Tất cả workflow files đã được validate
- [x] Documentation đầy đủ (Vietnamese)
- [x] Status badges đã được thêm vào README
- [x] .gitignore đã được cấu hình

### Cần Cấu Hình Bởi Admin ⚙️
- [ ] Enable GitHub Environments
- [ ] Configure Dependabot
- [ ] Add deployment server credentials
- [ ] Setup notification webhooks (optional)
- [ ] Configure branch protection rules (optional)

---

## 📋 BƯỚC 1: KÍCH HOẠT WORKFLOWS

### Workflows Tự Động Chạy
Sau khi merge PR này vào main branch, các workflows sẽ **tự động kích hoạt**:

1. **Status Check** - Chạy trên mọi push
2. **Backend CI** - Chạy khi có thay đổi trong `backend/`
3. **Frontend CI** - Chạy khi có thay đổi trong `client-app/` hoặc `Admin-app/`
4. **Integration Test** - Chạy hàng ngày lúc 2 AM UTC
5. **Monitoring** - Chạy hàng ngày lúc 1 AM UTC

### Kiểm Tra Workflows
```
1. Truy cập: https://github.com/mariecalallen12/forex4/actions
2. Bạn sẽ thấy danh sách workflows
3. Click vào bất kỳ workflow nào để xem chi tiết
4. Workflows sẽ tự động chạy sau lần push đầu tiên
```

---

## 🔐 BƯỚC 2: CẤU HÌNH GITHUB ENVIRONMENTS

### Tạo Staging Environment

1. **Truy cập Settings:**
   ```
   Repository → Settings → Environments → New environment
   ```

2. **Tạo Staging Environment:**
   ```
   Name: staging
   ```

3. **Cấu hình Protection Rules (Optional):**
   ```
   [ ] Required reviewers: None
   [ ] Wait timer: 0 minutes
   ```

4. **Add Environment Secrets:**
   ```
   STAGING_HOST=staging.yourdomain.com
   STAGING_USER=deploy
   STAGING_SSH_KEY=<your-ssh-private-key>
   ```

### Tạo Production Environment

1. **Tạo Production Environment:**
   ```
   Name: production
   ```

2. **Cấu hình Protection Rules:**
   ```
   [x] Required reviewers: Select 1-2 team members
   [ ] Wait timer: 0 minutes (or 5 for additional safety)
   ```

3. **Add Environment Secrets:**
   ```
   PRODUCTION_HOST=yourdomain.com
   PRODUCTION_USER=deploy
   PRODUCTION_SSH_KEY=<your-ssh-private-key>
   ```

### Tạo SSH Keys (Nếu Chưa Có)

```bash
# Trên local machine
ssh-keygen -t ed25519 -C "deployment@forex4" -f ~/.ssh/forex4_deploy

# Copy public key lên server
ssh-copy-id -i ~/.ssh/forex4_deploy.pub deploy@yourdomain.com

# Copy private key content
cat ~/.ssh/forex4_deploy
# Paste vào GitHub Secrets → STAGING_SSH_KEY / PRODUCTION_SSH_KEY
```

---

## 🤖 BƯỚC 3: ENABLE DEPENDABOT

### Kích Hoạt Dependabot Alerts

1. **Truy cập Security Settings:**
   ```
   Repository → Settings → Security → Code security and analysis
   ```

2. **Enable các features:**
   ```
   [x] Dependency graph (already enabled)
   [x] Dependabot alerts
   [x] Dependabot security updates
   ```

### Cấu Hình Dependabot (Optional)

Tạo file `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "python"
    
  # Client app npm dependencies
  - package-ecosystem: "npm"
    directory: "/client-app"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "npm"
    
  # Admin app npm dependencies
  - package-ecosystem: "npm"
    directory: "/Admin-app"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "npm"
    
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
```

---

## 🔔 BƯỚC 4: SETUP NOTIFICATIONS (OPTIONAL)

### Slack Notifications

1. **Create Slack Webhook:**
   ```
   Slack → Settings → Manage apps → Incoming Webhooks → Add to Slack
   Choose channel → Copy webhook URL
   ```

2. **Add to GitHub Secrets:**
   ```
   Repository → Settings → Secrets → New repository secret
   Name: SLACK_WEBHOOK
   Value: <your-webhook-url>
   ```

3. **Uncomment notification step in workflows:**
   Edit `.github/workflows/deploy.yml` and uncomment:
   ```yaml
   # - name: Notify Team
   #   uses: 8398a7/action-slack@v3
   #   with:
   #     status: ${{ job.status }}
   #     text: 'Deployment to ${{ needs.prepare.outputs.environment }} completed'
   #     webhook_url: ${{ secrets.SLACK_WEBHOOK }}
   ```

### Discord Notifications

1. **Create Discord Webhook:**
   ```
   Server Settings → Integrations → Webhooks → New Webhook
   Copy webhook URL
   ```

2. **Add to GitHub Secrets:**
   ```
   Name: DISCORD_WEBHOOK
   Value: <your-webhook-url>
   ```

---

## 🛡️ BƯỚC 5: BRANCH PROTECTION (OPTIONAL)

### Cấu Hình Branch Protection cho Main

1. **Truy cập Branch Settings:**
   ```
   Repository → Settings → Branches → Add rule
   ```

2. **Branch Name Pattern:**
   ```
   main
   ```

3. **Protection Rules:**
   ```
   [x] Require a pull request before merging
       [x] Require approvals: 1
       [ ] Dismiss stale pull request approvals
       
   [x] Require status checks to pass before merging
       [x] Require branches to be up to date before merging
       Status checks that are required:
           [x] Backend CI / summary
           [x] Frontend CI / summary
           [x] Quick Status Check / quick-check
       
   [x] Require conversation resolution before merging
   [ ] Require signed commits
   [ ] Require linear history
   
   [x] Include administrators (optional - for strict enforcement)
   ```

4. **Save Changes**

---

## 📊 BƯỚC 6: VERIFY SETUP

### Test Workflows Manually

1. **Test Status Check:**
   ```
   Make a small change (e.g., update README)
   Commit and push
   Check Actions tab - should see "Quick Status Check" running
   ```

2. **Test Backend CI:**
   ```
   Make a change in backend/ (e.g., add comment)
   Commit and push
   Check Actions tab - should see "Backend CI/CD" running
   ```

3. **Test Frontend CI:**
   ```
   Make a change in client-app/ (e.g., update package.json description)
   Commit and push
   Check Actions tab - should see "Frontend CI/CD" running
   ```

4. **Test Deployment (Manual):**
   ```
   Go to Actions → Deployment → Run workflow
   Select branch: main
   Select environment: staging
   Click "Run workflow"
   Watch the deployment process
   ```

### Check Status Badges

Visit your README.md on GitHub - you should see:
- ![Backend CI](https://github.com/mariecalallen12/forex4/actions/workflows/backend-ci.yml/badge.svg)
- ![Frontend CI](https://github.com/mariecalallen12/forex4/actions/workflows/frontend-ci.yml/badge.svg)
- And others...

---

## 🎯 BƯỚC 7: LOCAL TESTING

### Test Locally Before Push

```bash
# 1. Backend tests
cd backend
python -m pytest tests/ -v

# 2. Frontend builds
cd ../client-app
npm run build

cd ../Admin-app
npm run build

# 3. Docker compose test
cd ..
docker-compose up --build
```

### Use Act for Local Workflow Testing (Optional)

```bash
# Install Act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test workflow locally
act -j quick-check              # Test status check
act -j lint                     # Test backend linting
act pull_request               # Simulate PR
```

---

## 📚 BƯỚC 8: TEAM ONBOARDING

### Share Documentation

Ensure team members have access to:
1. **CI_CD_WORKFLOW_GUIDE.md** - Complete guide
2. **CI_CD_QUICK_START.md** - Quick reference
3. **PROJECT_STATUS_REPORT.md** - Project assessment
4. **This file** - Setup instructions

### Team Training Points

1. **How to view workflow status:**
   - Check Actions tab
   - Look at status badges
   - Review PR checks

2. **How to debug failures:**
   - Click on failed workflow
   - Expand failed step
   - Download artifacts if needed

3. **How to trigger deployment:**
   - Tag a release: `git tag v1.0.0 && git push --tags`
   - Or use manual workflow dispatch

4. **How to handle security alerts:**
   - Check Security tab
   - Review CodeQL results
   - Update dependencies

---

## 🔄 DAILY OPERATIONS

### Morning Checklist

1. **Check Actions Dashboard:**
   - Any failed workflows overnight?
   - Review monitoring results (1 AM UTC run)
   - Check integration tests (2 AM UTC run)

2. **Review Security Tab:**
   - New vulnerabilities?
   - Dependabot PRs to review?
   - CodeQL alerts?

3. **Check PR Status:**
   - All required checks passing?
   - Coverage acceptable?
   - Ready to merge?

### Weekly Tasks

1. **Review trends:**
   - Test success rate
   - Build times
   - Coverage changes

2. **Update dependencies:**
   - Review Dependabot PRs
   - Test updates locally
   - Merge if safe

3. **Documentation:**
   - Update if workflows changed
   - Add new troubleshooting tips
   - Share learnings with team

---

## 🆘 TROUBLESHOOTING

### Workflows Not Running

**Problem:** Workflows don't trigger after push
```
Solution:
1. Check .github/workflows/ files are in main branch
2. Verify YAML syntax (all files validated ✓)
3. Check path filters match your changes
4. Review Actions tab for any errors
```

### Deployment Failing

**Problem:** Deployment job fails
```
Solution:
1. Check if server credentials are set in Secrets
2. Verify SSH key has correct permissions
3. Test SSH connection manually
4. Review server logs
5. For now: Deployment needs server setup
```

### Tests Failing

**Problem:** Tests pass locally but fail in CI
```
Solution:
1. Check environment variables
2. Verify service dependencies (postgres, redis)
3. Review test logs in CI
4. Check for race conditions
5. Verify database schema in CI
```

---

## ✅ COMPLETION CHECKLIST

### Immediate Actions (Required)
- [ ] Merge this PR to enable workflows
- [ ] Verify workflows run successfully
- [ ] Check status badges appear on README
- [ ] Review first workflow run results

### Optional Enhancements (Recommended)
- [ ] Configure GitHub Environments (staging, production)
- [ ] Enable Dependabot
- [ ] Setup branch protection rules
- [ ] Add notification webhooks
- [ ] Configure deployment servers
- [ ] Enable GitHub Pages for docs (optional)

### Team Readiness
- [ ] Share documentation with team
- [ ] Conduct training session
- [ ] Establish workflow for handling alerts
- [ ] Define deployment procedures
- [ ] Create incident response plan

---

## 🎉 SUCCESS CRITERIA

Your CI/CD is successfully setup when:

✅ **Workflows:**
- All 6 workflows appear in Actions tab
- Status Check runs on every push (< 5 min)
- CI pipelines run on relevant changes
- Daily monitoring jobs execute successfully

✅ **Status:**
- Status badges show on README
- Workflow results appear in PRs
- Artifacts are uploaded
- Reports are accessible

✅ **Security:**
- CodeQL scans running
- Trivy scans containers
- Security alerts visible
- Dependency updates tracked

✅ **Team:**
- Everyone can view workflow status
- Team knows how to debug failures
- Deployment process understood
- Documentation accessible

---

## 📞 SUPPORT

### Resources
- 📖 [CI/CD Workflow Guide](CI_CD_WORKFLOW_GUIDE.md)
- 📖 [Quick Start Guide](CI_CD_QUICK_START.md)
- 📖 [Project Status Report](PROJECT_STATUS_REPORT.md)
- 🔗 [GitHub Actions Docs](https://docs.github.com/en/actions)

### Getting Help
1. Check documentation first
2. Review existing GitHub Issues
3. Create new Issue with:
   - Workflow name
   - Error message
   - Steps to reproduce
   - Expected vs actual behavior

---

**🎯 Next Step:** Merge this PR to activate all CI/CD workflows!

**📅 Created:** 06/12/2025  
**✍️ Status:** Ready for Production  
**🔄 Last Updated:** 06/12/2025
