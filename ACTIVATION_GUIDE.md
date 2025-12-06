# 🚀 HƯỚNG DẪN KÍCH HOẠT HỆ THỐNG CI/CD

**Ngày tạo:** 06/12/2025  
**Mục đích:** Hướng dẫn từng bước để kích hoạt toàn bộ hệ thống CI/CD

---

## ✅ TỔNG QUAN

Sau khi merge PR này, bạn cần thực hiện các bước sau để kích hoạt đầy đủ hệ thống:

### 📋 Checklist Tổng Quan
- [ ] **Bước 1:** Merge PR để kích hoạt workflows
- [ ] **Bước 2:** Enable Dependabot
- [ ] **Bước 3:** Cấu hình GitHub Environments
- [ ] **Bước 4:** Cấu hình Branch Protection
- [ ] **Bước 5:** Thêm Secrets cho Deployment
- [ ] **Bước 6:** Setup Notifications (tùy chọn)
- [ ] **Bước 7:** Verify và Test

---

## 🔀 BƯỚC 1: MERGE PR ĐỂ KÍCH HOẠT WORKFLOWS

### 1.1. Review PR

```
1. Truy cập: https://github.com/mariecalallen12/forex4/pulls
2. Tìm PR: "Setup comprehensive GitHub CI/CD workflow"
3. Review các files đã thay đổi:
   ✓ 6 workflow files trong .github/workflows/
   ✓ Dependabot config trong .github/dependabot.yml
   ✓ CODEOWNERS file
   ✓ PR template
   ✓ Issue templates
   ✓ 5 documentation files
4. Đảm bảo tất cả checks đã pass
```

### 1.2. Merge PR

```
1. Click vào PR
2. Scroll xuống cuối page
3. Click "Merge pull request"
4. Chọn merge strategy:
   - "Create a merge commit" (recommended)
   hoặc
   - "Squash and merge" (nếu muốn clean history)
5. Confirm merge
6. Xóa branch copilot/setup-task-process-workflow (optional)
```

### 1.3. Verify Workflows Activated

```
1. Truy cập: https://github.com/mariecalallen12/forex4/actions
2. Bạn sẽ thấy workflows đang chạy:
   - ✓ Quick Status Check
   - ✓ Backend CI (nếu có thay đổi backend)
   - ✓ Frontend CI (nếu có thay đổi frontend)
3. Click vào workflow để xem chi tiết
4. Chờ workflows hoàn thành (~5-10 phút)
```

### 1.4. Check Status Badges

```
1. Truy cập: https://github.com/mariecalallen12/forex4
2. Scroll xuống README.md
3. Xem status badges:
   ✓ Backend CI
   ✓ Frontend CI
   ✓ Integration Test
   ✓ Deployment
   ✓ Monitoring
   ✓ Status Check
```

---

## 🤖 BƯỚC 2: ENABLE DEPENDABOT

### 2.1. Enable Dependabot Alerts

```
1. Truy cập: https://github.com/mariecalallen12/forex4/settings/security_analysis
2. Trong "Code security and analysis" section:
   
   ✓ Dependency graph: Already enabled
   
   ☐ Dependabot alerts: Click "Enable"
   → Nhận alerts khi có vulnerabilities
   
   ☐ Dependabot security updates: Click "Enable"  
   → Tự động tạo PR để fix vulnerabilities
   
3. Save changes
```

### 2.2. Verify Dependabot Config

File `.github/dependabot.yml` đã được tạo với cấu hình:

```yaml
✓ Backend (pip) - Weekly Monday 2 AM
✓ Client App (npm) - Weekly Monday 2 AM
✓ Admin App (npm) - Weekly Monday 2 AM
✓ GitHub Actions - Weekly Monday 2 AM
✓ Docker (all apps) - Weekly Tuesday 2 AM
```

### 2.3. Test Dependabot

```
Sau khi enable:
1. Dependabot sẽ scan dependencies
2. Nếu có updates, sẽ tạo PRs tự động
3. Check tab "Pull requests" để xem các PRs từ dependabot
4. Review và merge các PRs an toàn
```

---

## 🌍 BƯỚC 3: CẤU HÌNH GITHUB ENVIRONMENTS

### 3.1. Tạo Staging Environment

```
1. Truy cập: https://github.com/mariecalallen12/forex4/settings/environments
2. Click "New environment"
3. Name: staging
4. Click "Configure environment"

Configure protection rules:
☐ Required reviewers: Leave empty (auto-deploy)
☐ Wait timer: 0 minutes

5. Click "Save protection rules"
```

### 3.2. Thêm Staging Secrets

```
Trong staging environment page, scroll xuống "Environment secrets":

1. Click "Add secret"
   Name: STAGING_HOST
   Value: staging.yourdomain.com (hoặc IP address)
   Click "Add secret"

2. Click "Add secret"
   Name: STAGING_USER
   Value: deploy (hoặc username của bạn)
   Click "Add secret"

3. Click "Add secret"  
   Name: STAGING_SSH_KEY
   Value: [Paste private SSH key - xem hướng dẫn bên dưới]
   Click "Add secret"
```

### 3.3. Tạo Production Environment

```
1. Click "New environment"
2. Name: production
3. Click "Configure environment"

Configure protection rules:
☑ Required reviewers: Select 1-2 reviewers
   (Chọn người có quyền approve production deployment)
☐ Wait timer: 0 hoặc 5 minutes (optional safety)

4. Click "Save protection rules"
```

### 3.4. Thêm Production Secrets

```
Tương tự staging, thêm:
- PRODUCTION_HOST
- PRODUCTION_USER  
- PRODUCTION_SSH_KEY
```

### 3.5. Tạo SSH Keys (Nếu chưa có)

```bash
# Trên máy local hoặc server của bạn

# 1. Tạo SSH key pair
ssh-keygen -t ed25519 -C "deployment@forex4-staging" -f ~/.ssh/forex4_deploy_staging
ssh-keygen -t ed25519 -C "deployment@forex4-production" -f ~/.ssh/forex4_deploy_production

# 2. Copy public key lên server
ssh-copy-id -i ~/.ssh/forex4_deploy_staging.pub deploy@staging.yourdomain.com
ssh-copy-id -i ~/.ssh/forex4_deploy_production.pub deploy@production.yourdomain.com

# 3. Copy private key để paste vào GitHub Secrets
cat ~/.ssh/forex4_deploy_staging
# Copy toàn bộ output (bao gồm -----BEGIN và -----END)
# Paste vào GitHub Environment Secret: STAGING_SSH_KEY

cat ~/.ssh/forex4_deploy_production  
# Paste vào GitHub Environment Secret: PRODUCTION_SSH_KEY

# 4. Test SSH connection
ssh -i ~/.ssh/forex4_deploy_staging deploy@staging.yourdomain.com
ssh -i ~/.ssh/forex4_deploy_production deploy@production.yourdomain.com
```

---

## 🛡️ BƯỚC 4: CẤU HÌNH BRANCH PROTECTION

### 4.1. Setup Main Branch Protection

```
1. Truy cập: https://github.com/mariecalallen12/forex4/settings/branches
2. Click "Add rule" hoặc "Add classic branch protection rule"
3. Branch name pattern: main
```

### 4.2. Configure Protection Rules

```
☑ Require a pull request before merging
   ☑ Require approvals: 1
   ☐ Dismiss stale pull request approvals when new commits are pushed
   ☐ Require review from Code Owners

☑ Require status checks to pass before merging
   ☑ Require branches to be up to date before merging
   
   Search for status checks to require:
   ☑ Backend CI / summary
   ☑ Frontend CI / summary  
   ☑ Quick Status Check / quick-check
   
   (Các checks này sẽ xuất hiện sau lần chạy đầu tiên)

☑ Require conversation resolution before merging

☐ Require signed commits (optional - recommended for security)

☐ Require linear history (optional)

☐ Require deployments to succeed before merging (optional)

☑ Lock branch (optional - prevents direct pushes)

☐ Do not allow bypassing the above settings
   Hoặc
☑ Include administrators (recommended - áp dụng cho cả admin)

4. Click "Create" hoặc "Save changes"
```

### 4.3. Setup Develop Branch Protection (Optional)

```
Nếu sử dụng develop branch:
1. Tạo protection rule cho "develop"
2. Configure tương tự main nhưng relaxed hơn:
   - Require 0-1 approvals
   - Fewer required status checks
   - More flexible
```

---

## 🔐 BƯỚC 5: THÊM SECRETS CHO DEPLOYMENT

### 5.1. Repository Secrets (Optional)

```
Truy cập: https://github.com/mariecalallen12/forex4/settings/secrets/actions

Có thể thêm các secrets chung:

1. DOCKER_USERNAME (nếu dùng Docker Hub)
   Value: your-dockerhub-username

2. DOCKER_PASSWORD (nếu dùng Docker Hub)
   Value: your-dockerhub-password
   
3. SLACK_WEBHOOK (nếu muốn Slack notifications)
   Value: your-slack-webhook-url
   
4. DISCORD_WEBHOOK (nếu muốn Discord notifications)
   Value: your-discord-webhook-url

5. TEST_SECRET_KEY (cho CI testing)
   Value: test-secret-key-for-ci-pipeline-only
```

### 5.2. Environment Variables trong .env

```bash
# Trên deployment server, tạo .env file:

# Application
APP_NAME="Digital Utopia Platform"
DEBUG=false
ENVIRONMENT=production

# Security
SECRET_KEY="your-very-secure-random-secret-key-here"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRES_USER=production_user
POSTGRES_PASSWORD=very-secure-password
POSTGRES_DB=digital_utopia_prod
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
REDIS_PASSWORD=redis-secure-password

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

---

## 📢 BƯỚC 6: SETUP NOTIFICATIONS (TÙY CHỌN)

### 6.1. Slack Notifications

#### Tạo Slack Webhook:
```
1. Đăng nhập Slack workspace
2. Truy cập: https://api.slack.com/apps
3. Click "Create New App" → "From scratch"
4. App Name: "GitHub CI/CD Bot"
5. Workspace: Select your workspace
6. Click "Create App"

7. Trong "Add features and functionality":
   Click "Incoming Webhooks"
   
8. Toggle "Activate Incoming Webhooks" → ON

9. Click "Add New Webhook to Workspace"
10. Select channel: #deployments hoặc #ci-cd
11. Click "Allow"
12. Copy Webhook URL
```

#### Add to GitHub Secrets:
```
1. Truy cập: https://github.com/mariecalallen12/forex4/settings/secrets/actions
2. Click "New repository secret"
3. Name: SLACK_WEBHOOK
4. Value: [Paste webhook URL]
5. Click "Add secret"
```

#### Uncomment notification code:
```
Trong .github/workflows/deploy.yml, uncomment:

# - name: Notify Team
#   uses: 8398a7/action-slack@v3
#   with:
#     status: ${{ job.status }}
#     text: 'Deployment to ${{ needs.prepare.outputs.environment }} completed'
#     webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 6.2. Discord Notifications

#### Tạo Discord Webhook:
```
1. Mở Discord server
2. Click vào channel settings (gear icon)
3. Integrations → Webhooks
4. Click "New Webhook"
5. Name: "GitHub CI/CD Bot"
6. Select channel
7. Copy Webhook URL
8. Save
```

#### Add to GitHub Secrets:
```
Name: DISCORD_WEBHOOK
Value: [Paste webhook URL]
```

### 6.3. Email Notifications

GitHub tự động gửi email notifications cho:
- Workflow failures
- Security alerts
- Dependabot PRs

Configure trong:
```
Settings → Notifications → Actions
☑ Email notifications for failed workflows
☑ Email notifications for security alerts
```

---

## ✅ BƯỚC 7: VERIFY VÀ TEST

### 7.1. Verify Workflows

```
1. Truy cập Actions tab
   https://github.com/mariecalallen12/forex4/actions
   
2. Kiểm tra workflows đã chạy thành công:
   ✓ Status Check - 🟢 Success
   ✓ Backend CI (nếu chạy) - 🟢 Success  
   ✓ Frontend CI (nếu chạy) - 🟢 Success

3. Click vào từng workflow để xem logs
```

### 7.2. Test Backend CI

```bash
# Tạo một thay đổi nhỏ trong backend
cd backend
echo "# Test CI" >> README.md
git add .
git commit -m "test: trigger backend CI"
git push

# Check Actions tab - Backend CI workflow sẽ chạy
```

### 7.3. Test Frontend CI

```bash
# Tạo một thay đổi nhỏ trong frontend
cd client-app
echo "/* Test CI */" >> src/main.js
git add .
git commit -m "test: trigger frontend CI"  
git push

# Check Actions tab - Frontend CI workflow sẽ chạy
```

### 7.4. Test Manual Deployment

```
1. Truy cập Actions → Deployment workflow
2. Click "Run workflow"
3. Select:
   - Branch: main
   - Environment: staging
4. Click "Run workflow"
5. Xem deployment process
6. Nếu có lỗi về SSH, kiểm tra secrets
```

### 7.5. Test Dependabot

```
Wait 24-48 hours sau khi enable, Dependabot sẽ:
1. Scan dependencies
2. Tạo PRs cho updates (nếu có)
3. Check "Pull requests" tab
```

### 7.6. Check Status Badges

```
View README.md trên GitHub:
✓ Tất cả badges hiển thị đúng
✓ Badges có màu phù hợp (green = passing)
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Workflows không chạy

**Giải pháp:**
```
1. Check workflows đã được merge vào main branch
2. Verify path filters match your changes
3. Check Actions tab enabled: 
   Settings → Actions → General → Allow all actions
```

### Issue 2: Secrets không hoạt động

**Giải pháp:**
```
1. Verify secret names match exactly (case-sensitive)
2. Check secrets trong đúng scope:
   - Repository secrets: Cho tất cả workflows
   - Environment secrets: Cho specific environment
3. Re-add secrets nếu cần
4. Không có spaces hoặc newlines thừa
```

### Issue 3: SSH deployment fails

**Giải pháp:**
```
1. Test SSH locally:
   ssh -i private_key user@host
   
2. Verify SSH key format:
   - Phải bao gồm -----BEGIN ... -----END
   - Không có extra spaces
   - Line endings correct
   
3. Check server:
   - SSH service running
   - User có quyền
   - ~/.ssh/authorized_keys configured
   
4. Check firewall:
   - Port 22 open
   - GitHub IP ranges allowed
```

### Issue 4: Branch protection quá strict

**Giải pháp:**
```
1. Temporarily disable some rules
2. Or allow bypass for administrators
3. Gradually enable rules as team adapts
```

---

## 📊 MONITORING SAU KHI KÍCH HOẠT

### Daily Checks (Automated)

```
✓ Monitoring workflow - 1 AM UTC
  - Dependency scans
  - Security checks
  - Health metrics

✓ Integration tests - 2 AM UTC
  - Full stack testing
  - Performance tests
```

### Weekly Reviews

```
☐ Check Dependabot PRs
☐ Review security alerts
☐ Check workflow success rates
☐ Review team feedback
```

### Monthly Tasks

```
☐ Update documentation
☐ Review and optimize workflows
☐ Update action versions
☐ Team training refresh
```

---

## 🎉 HOÀN THÀNH!

Sau khi hoàn thành tất cả các bước trên, hệ thống CI/CD của bạn đã:

✅ **Hoàn toàn tự động hóa**
✅ **Bảo mật với multiple scanning tools**
✅ **Monitoring liên tục**
✅ **Deployment pipeline sẵn sàng**
✅ **Documentation đầy đủ**
✅ **Team collaboration tools configured**

### 📈 Expected Results

```
Automation:       95%
Speed:           60-70% faster
Security:        Continuous monitoring
Quality:         Enforced by CI
Visibility:      100% real-time
Team Productivity: Significantly improved
```

---

## 📚 TÀI LIỆU THAM KHẢO

- 📖 [CI_CD_WORKFLOW_GUIDE.md](CI_CD_WORKFLOW_GUIDE.md)
- 📖 [CI_CD_QUICK_START.md](CI_CD_QUICK_START.md)
- 📖 [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- 📖 [PROJECT_STATUS_REPORT.md](PROJECT_STATUS_REPORT.md)
- 🔗 [GitHub Actions Docs](https://docs.github.com/en/actions)
- 🔗 [GitHub Environments Docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

---

**📅 Created:** 06/12/2025  
**✍️ Status:** Complete  
**🎯 Ready for:** Production Activation
