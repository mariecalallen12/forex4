# 🐳 Docker Deployment - Quick Start Guide

## 🚀 Khởi Động Nhanh (Quick Start)

### 1. Clone và Setup

```bash
# Clone repository
git clone https://github.com/mariecalallen12/forex4.git
cd forex4

# Copy environment file
cp .env.example .env

# Edit environment variables (IMPORTANT!)
nano .env
# Change: SECRET_KEY, POSTGRES_PASSWORD
```

### 2. Start Development

```bash
# Start development environment
./scripts/docker-start.sh dev

# Access services:
# - Backend: http://localhost:8000
# - Client:  http://localhost:5173
# - Admin:   http://localhost:5174
# - Docs:    http://localhost:8000/docs
```

### 3. Start Production

```bash
# Start production environment
./scripts/docker-start.sh prod

# Access services:
# - Main:    http://localhost
# - Backend: http://localhost:8000
# - Client:  http://localhost:3000
# - Admin:   http://localhost:3001
```

---

## 📦 Available Services

| Service | Port | URL |
|---------|------|-----|
| Nginx (Prod) | 80 | http://localhost |
| Backend API | 8000 | http://localhost:8000 |
| Client App (Prod) | 3000 | http://localhost:3000 |
| Admin App (Prod) | 3001 | http://localhost:3001 |
| Client App (Dev) | 5173 | http://localhost:5173 |
| Admin App (Dev) | 5174 | http://localhost:5174 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| PgAdmin (Dev) | 5050 | http://localhost:5050 |
| Redis Commander (Dev) | 8081 | http://localhost:8081 |

---

## 🛠️ Management Scripts

All scripts are located in `scripts/` directory:

```bash
# Start services
./scripts/docker-start.sh [dev|prod]

# Stop services
./scripts/docker-stop.sh [dev|prod]

# Check health
./scripts/docker-health.sh

# Backup database
./scripts/docker-backup.sh

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
```

---

## 📊 Common Commands

### Development

```bash
# Start dev environment
docker-compose -f docker-compose.dev.yml up -d

# Stop dev environment
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart backend (after code changes)
docker-compose -f docker-compose.dev.yml restart backend
```

### Production

```bash
# Build and start
docker-compose build
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3
```

### Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d digital_utopia

# Backup database
docker-compose exec postgres pg_dump -U postgres digital_utopia > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres digital_utopia
```

---

## 🔧 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in .env
```

### Permission denied

```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod 700 data/postgres data/redis
```

### Clean everything and restart

```bash
# Stop and remove everything
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a

# Start fresh
./scripts/docker-start.sh prod
```

---

## 📚 Documentation

Detailed documentation:
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - General deployment guide
- [BAO_CAO_DANH_GIA_DU_AN.md](BAO_CAO_DANH_GIA_DU_AN.md) - Project evaluation

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Configure `CORS_ORIGINS` correctly
- [ ] Setup SSL certificates (nginx/ssl/)
- [ ] Configure firewall rules
- [ ] Setup backup schedule
- [ ] Configure monitoring
- [ ] Test all health checks
- [ ] Run database migrations
- [ ] Verify all services are healthy

---

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Check health: `./scripts/docker-health.sh`
3. Review documentation: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
4. Check environment: Verify `.env` configuration
5. Clean and restart: `docker-compose down -v && ./scripts/docker-start.sh prod`

---

**Last Updated:** 06/12/2025  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
