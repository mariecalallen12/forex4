# 🐳 HƯỚNG DẪN TRIỂN KHAI DOCKER - DIGITAL UTOPIA PLATFORM

**Phiên bản:** 2.0.0  
**Ngày cập nhật:** 06/12/2025  
**Trạng thái:** Production Ready ✅

---

## 📋 MỤC LỤC

1. [Tổng Quan](#1-tổng-quan)
2. [Yêu Cầu Hệ Thống](#2-yêu-cầu-hệ-thống)
3. [Cấu Trúc Docker](#3-cấu-trúc-docker)
4. [Cấu Hình Environment](#4-cấu-hình-environment)
5. [Triển Khai Development](#5-triển-khai-development)
6. [Triển Khai Production](#6-triển-khai-production)
7. [Database Migration](#7-database-migration)
8. [Monitoring và Logs](#8-monitoring-và-logs)
9. [Backup và Recovery](#9-backup-và-recovery)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. TỔNG QUAN

### 1.1. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80/443)                  │
│          Reverse Proxy + Load Balancer + SSL           │
└────────────┬────────────────────────────────────────────┘
             │
        ┌────┴────┬──────────────┬──────────────┐
        │         │              │              │
   ┌────▼─────┐ ┌▼───────────┐ ┌▼──────────┐  │
   │ Backend  │ │ Client App │ │ Admin App │  │
   │ FastAPI  │ │   Vue 3    │ │   Vue 3   │  │
   │:8000     │ │   :3000    │ │   :3001   │  │
   └────┬─────┘ └────────────┘ └───────────┘  │
        │                                       │
   ┌────┴─────┬──────────────┐                │
   │          │              │                 │
┌──▼──────┐ ┌─▼──────┐      │                 │
│PostgreSQL│ │ Redis  │      │                 │
│  :5432   │ │ :6379  │      │                 │
└──────────┘ └────────┘      │                 │
                              │                 │
    Data Volumes              │                 │
    ─────────────            │                 │
    • postgres_data          │                 │
    • redis_data             │                 │
    • uploads                │                 │
    • logs                   └─────────────────┘
```

### 1.2. Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| **nginx** | forex4-nginx | 80, 443 | Reverse proxy, SSL termination |
| **backend** | forex4-backend | 8000 | FastAPI REST API |
| **client-app** | forex4-client | 3000 | Customer frontend |
| **admin-app** | forex4-admin | 3001 | Admin dashboard |
| **postgres** | forex4-postgres | 5432 | PostgreSQL database |
| **redis** | forex4-redis | 6379 | Cache và session |

---

## 2. YÊU CẦU HỆ THỐNG

### 2.1. Software Requirements

```bash
# Required
Docker:          20.10+ hoặc Docker Desktop
Docker Compose:  1.29+ hoặc v2

# Check versions
docker --version
docker-compose --version
```

### 2.2. Hardware Requirements

**Minimum (Development):**
```
CPU:     2 cores
RAM:     4GB
Storage: 20GB
```

**Recommended (Production):**
```
CPU:     4-8 cores
RAM:     8-16GB
Storage: 100GB SSD
Network: 1Gbps
```

---

## 3. CẤU TRÚC DOCKER

### 3.1. Files và Directories

```
forex4/
├── docker-compose.yml           # Production deployment
├── docker-compose.dev.yml       # Development deployment
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── backend/
│   ├── Dockerfile              # Standard backend image
│   ├── Dockerfile.prod         # Production optimized
│   ├── requirements.txt
│   └── ...
├── client-app/
│   ├── Dockerfile              # Production build
│   ├── Dockerfile.dev          # Development with hot-reload
│   └── ...
├── Admin-app/
│   ├── Dockerfile              # Production build
│   ├── Dockerfile.dev          # Development with hot-reload
│   └── ...
├── nginx/
│   ├── nginx.conf              # Nginx configuration
│   ├── ssl/                    # SSL certificates
│   └── logs/                   # Nginx logs
├── data/                        # Data volumes
│   ├── postgres/               # PostgreSQL data
│   └── redis/                  # Redis data
└── backups/                     # Database backups
```

### 3.2. Docker Images

**Production:**
- `postgres:15-alpine` - Database
- `redis:7-alpine` - Cache
- `nginx:alpine` - Reverse proxy
- Custom builds:
  - `forex4-backend` - FastAPI backend
  - `forex4-client` - Client app
  - `forex4-admin` - Admin app

---

## 4. CẤU HÌNH ENVIRONMENT

### 4.1. Create Environment File

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

### 4.2. Environment Variables

```env
# ========== Application ==========
APP_NAME=Digital Utopia Platform
DEBUG=false
ENVIRONMENT=production

# ========== Security ==========
# IMPORTANT: Generate new key for production!
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========== Database ==========
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-this-strong-password
POSTGRES_DB=digital_utopia
POSTGRES_PORT=5432

# ========== Redis ==========
REDIS_PORT=6379
REDIS_PASSWORD=

# ========== Ports ==========
BACKEND_PORT=8000
CLIENT_PORT=3000
ADMIN_PORT=3001

# ========== CORS ==========
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# ========== Rate Limiting ==========
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

### 4.3. Generate Secret Key

```bash
# Generate secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

---

## 5. TRIỂN KHAI DEVELOPMENT

### 5.1. Quick Start

```bash
# 1. Clone repository
git clone https://github.com/mariecalallen12/forex4.git
cd forex4

# 2. Setup environment
cp .env.example .env
nano .env  # Edit as needed

# 3. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 4. Check status
docker-compose -f docker-compose.dev.yml ps
```

### 5.2. Development Features

**Hot-reload enabled for:**
- ✅ Backend: Code changes auto-reload
- ✅ Frontend: Vite hot module replacement
- ✅ Admin: Vite hot module replacement

**Development tools included:**
- 🔍 PgAdmin - Database management (http://localhost:5050)
- 🔍 Redis Commander - Redis management (http://localhost:8081)

### 5.3. Access Services

```
Backend API:     http://localhost:8000
API Docs:        http://localhost:8000/docs
Client App:      http://localhost:5173
Admin App:       http://localhost:5174
PgAdmin:         http://localhost:5050 (admin@digitalutopia.com / admin)
Redis Commander: http://localhost:8081
```

### 5.4. Development Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f client-app

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (clean start)
docker-compose -f docker-compose.dev.yml down -v
```

---

## 6. TRIỂN KHAI PRODUCTION

### 6.1. Pre-deployment Checklist

- [ ] ✅ Environment variables configured (.env)
- [ ] ✅ SECRET_KEY changed from default
- [ ] ✅ Strong database password set
- [ ] ✅ CORS origins configured correctly
- [ ] ✅ SSL certificates prepared (if using HTTPS)
- [ ] ✅ Data directories created
- [ ] ✅ Backup strategy planned

### 6.2. Create Data Directories

```bash
# Create directories for persistent data
mkdir -p data/postgres data/redis backups

# Set permissions
chmod 700 data/postgres
chmod 700 data/redis
chmod 755 backups
```

### 6.3. Build Images

```bash
# Build all images
docker-compose build

# Or build specific service
docker-compose build backend
docker-compose build client-app
docker-compose build admin-app

# Build with no cache (fresh build)
docker-compose build --no-cache
```

### 6.4. Start Production

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Check health
docker-compose ps
curl http://localhost/health
curl http://localhost:8000/health
```

### 6.5. Verify Deployment

```bash
# 1. Check all containers are running
docker-compose ps

# Expected output:
# NAME               STATUS    PORTS
# forex4-nginx       Up        0.0.0.0:80->80/tcp
# forex4-backend     Up        0.0.0.0:8000->8000/tcp
# forex4-client      Up        0.0.0.0:3000->80/tcp
# forex4-admin       Up        0.0.0.0:3001->80/tcp
# forex4-postgres    Up        0.0.0.0:5432->5432/tcp
# forex4-redis       Up        0.0.0.0:6379->6379/tcp

# 2. Check health endpoints
curl http://localhost/health          # Nginx health
curl http://localhost:8000/health     # Backend health

# 3. Check database connection
docker-compose exec postgres pg_isready

# 4. Check Redis connection
docker-compose exec redis redis-cli ping

# 5. View logs for errors
docker-compose logs --tail=50
```

---

## 7. DATABASE MIGRATION

### 7.1. Run Migrations

```bash
# Check current migration status
docker-compose exec backend alembic current

# Run all pending migrations
docker-compose exec backend alembic upgrade head

# Verify migrations
docker-compose exec backend alembic current
```

### 7.2. Create New Migration

```bash
# Auto-generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "Description of changes"

# Create empty migration
docker-compose exec backend alembic revision -m "Description"

# Edit migration file and apply
docker-compose exec backend alembic upgrade head
```

### 7.3. Rollback Migration

```bash
# Rollback one version
docker-compose exec backend alembic downgrade -1

# Rollback to specific version
docker-compose exec backend alembic downgrade <revision>

# Rollback all
docker-compose exec backend alembic downgrade base
```

---

## 8. MONITORING VÀ LOGS

### 8.1. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend

# Logs since specific time
docker-compose logs --since 30m backend
```

### 8.2. Resource Monitoring

```bash
# Monitor resource usage
docker stats

# Check specific container
docker stats forex4-backend

# Disk usage
docker system df

# Container details
docker-compose ps
docker inspect forex4-backend
```

### 8.3. Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# Nginx health
curl http://localhost/health
```

---

## 9. BACKUP VÀ RECOVERY

### 9.1. Database Backup

**Manual backup:**
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres digital_utopia > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker-compose exec -T postgres pg_dump -U postgres digital_utopia | gzip > backups/backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Automated backup script:**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
docker-compose exec -T postgres pg_dump -U postgres digital_utopia | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
echo "Backup created: backup_$DATE.sql.gz"
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /path/to/forex4/backup.sh
```

### 9.2. Database Recovery

```bash
# Stop backend service
docker-compose stop backend

# Restore from backup
gunzip < backups/backup_20251206.sql.gz | docker-compose exec -T postgres psql -U postgres digital_utopia

# Or from uncompressed backup
cat backups/backup_20251206.sql | docker-compose exec -T postgres psql -U postgres digital_utopia

# Start backend
docker-compose start backend
```

### 9.3. Full System Backup

```bash
# Backup all data volumes
tar -czf forex4_backup_$(date +%Y%m%d).tar.gz data/ backups/ .env

# Restore
tar -xzf forex4_backup_20251206.tar.gz
```

---

## 10. TROUBLESHOOTING

### 10.1. Common Issues

**Issue: Container fails to start**
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart service
docker-compose restart backend

# Rebuild and start
docker-compose up -d --build backend
```

**Issue: Database connection error**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready

# Restart database
docker-compose restart postgres
```

**Issue: Port already in use**
```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :5432

# Change port in .env
# Then restart services
docker-compose down
docker-compose up -d
```

**Issue: Permission denied**
```bash
# Fix directory permissions
sudo chown -R $USER:$USER data/
chmod 700 data/postgres
chmod 700 data/redis
```

### 10.2. Reset Everything

```bash
# Stop all services
docker-compose down

# Remove all containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a

# Start fresh
docker-compose up -d
```

### 10.3. Debug Mode

```bash
# Run container in interactive mode
docker-compose run --rm backend /bin/bash

# Execute commands in running container
docker-compose exec backend /bin/bash

# Check environment variables
docker-compose exec backend env

# Test database connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"
```

---

## 📞 SUPPORT

### Quick Commands Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# Status
docker-compose ps

# Health check
curl http://localhost/health

# Database backup
docker-compose exec postgres pg_dump -U postgres digital_utopia > backup.sql

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Health Check URLs

```
System:     http://localhost/health
Backend:    http://localhost:8000/health
API Docs:   http://localhost:8000/docs
Client:     http://localhost:3000
Admin:      http://localhost:3001/admin
```

---

## ✅ CHECKLIST SẢN XUẤT

Trước khi deploy production, đảm bảo:

- [ ] ✅ Environment variables đã được cấu hình đúng
- [ ] ✅ SECRET_KEY đã được thay đổi
- [ ] ✅ Database password mạnh
- [ ] ✅ CORS origins chính xác
- [ ] ✅ SSL certificates đã được cài đặt
- [ ] ✅ Firewall rules đã được cấu hình
- [ ] ✅ Backup schedule đã được thiết lập
- [ ] ✅ Monitoring đã được cấu hình
- [ ] ✅ Logs rotation đã được thiết lập
- [ ] ✅ Health checks đang hoạt động
- [ ] ✅ Database migrations đã chạy thành công
- [ ] ✅ All services đang healthy

---

**Version:** 1.0.0  
**Last Updated:** 06/12/2025  
**Status:** ✅ Production Ready  
**Documentation:** Complete with real deployment examples
