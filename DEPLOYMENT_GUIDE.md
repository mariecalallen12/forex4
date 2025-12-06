# 🚀 HƯỚNG DẪN DEPLOYMENT - DIGITAL UTOPIA PLATFORM

**Phiên bản:** 2.0.0  
**Ngày cập nhật:** 06/12/2025  
**Môi trường:** Production Ready

---

## 📋 MỤC LỤC

1. [Yêu Cầu Hệ Thống](#1-yêu-cầu-hệ-thống)
2. [Chuẩn Bị Môi Trường](#2-chuẩn-bị-môi-trường)
3. [Deployment với Docker](#3-deployment-với-docker)
4. [Deployment với Kubernetes](#4-deployment-với-kubernetes)
5. [Deployment trên AWS](#5-deployment-trên-aws)
6. [Configuration](#6-configuration)
7. [Database Setup](#7-database-setup)
8. [SSL/TLS Setup](#8-ssltls-setup)
9. [Monitoring & Logging](#9-monitoring--logging)
10. [Backup & Recovery](#10-backup--recovery)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. YÊU CẦU HỆ THỐNG

### 1.1. Minimum Requirements

**Server Specifications:**
```
CPU:     4 cores
RAM:     8GB
Storage: 100GB SSD
Network: 1Gbps
OS:      Ubuntu 20.04 LTS hoặc newer
```

**Software Requirements:**
```
Docker:       20.10+
Docker Compose: 1.29+
Python:       3.11+
Node.js:      18+
PostgreSQL:   15+
Redis:        7+
Nginx:        1.18+
```

### 1.2. Recommended Requirements

**Production Server:**
```
CPU:     8-16 cores
RAM:     16-32GB
Storage: 500GB NVMe SSD
Network: 10Gbps
OS:      Ubuntu 22.04 LTS
```

**Additional Components:**
```
Load Balancer:  HAProxy hoặc Nginx
CDN:            CloudFlare hoặc AWS CloudFront
Monitoring:     Prometheus + Grafana
Logging:        ELK Stack hoặc Loki
```

---

## 2. CHUẨN BỊ MÔI TRƯỜNG

### 2.1. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y git nginx certbot python3-certbot-nginx

# Verify installations
docker --version
docker-compose --version
nginx -v
```

### 2.2. Clone Repository

```bash
# Clone source code
cd /opt
sudo git clone https://github.com/mariecalallen12/forex4.git
cd forex4

# Set permissions
sudo chown -R $USER:$USER /opt/forex4
```

### 2.3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Application
APP_NAME=Digital Utopia Platform
APP_ENV=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/digital_utopia
DB_HOST=postgres
DB_PORT=5432
DB_NAME=digital_utopia
DB_USER=dbuser
DB_PASSWORD=secure_db_password

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# API
API_BASE_URL=https://api.yourdomain.com
API_PORT=8000

# Frontend
CLIENT_APP_URL=https://app.yourdomain.com
ADMIN_APP_URL=https://admin.yourdomain.com

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AWS (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

---

## 3. DEPLOYMENT VỚI DOCKER

### 3.1. Docker Compose Setup

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: forex4-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./client-app/dist:/usr/share/nginx/html/app:ro
      - ./Admin-app/dist:/usr/share/nginx/html/admin:ro
    depends_on:
      - backend
    networks:
      - forex4-network
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: forex4-backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - forex4-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: forex4-postgres
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - forex4-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: forex4-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - forex4-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  forex4-network:
    driver: bridge
```

### 3.2. Build và Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### 3.3. Database Migration

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify migrations
docker-compose -f docker-compose.prod.yml exec backend alembic current

# Rollback if needed
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## 4. DEPLOYMENT VỚI KUBERNETES

### 4.1. Kubernetes Manifests

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: forex4-prod
```

**deployment-backend.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: forex4-backend
  namespace: forex4-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: forex4-backend
  template:
    metadata:
      labels:
        app: forex4-backend
    spec:
      containers:
      - name: backend
        image: your-registry/forex4-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: forex4-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: forex4-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**service-backend.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: forex4-backend-service
  namespace: forex4-prod
spec:
  selector:
    app: forex4-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 4.2. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic forex4-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=redis-url=$REDIS_URL \
  --from-literal=jwt-secret=$JWT_SECRET_KEY \
  -n forex4-prod

# Deploy application
kubectl apply -f k8s/deployment-backend.yaml
kubectl apply -f k8s/service-backend.yaml

# Check status
kubectl get pods -n forex4-prod
kubectl get services -n forex4-prod

# View logs
kubectl logs -f deployment/forex4-backend -n forex4-prod
```

---

## 5. DEPLOYMENT TRÊN AWS

### 5.1. Architecture

```
Internet
   ↓
Route 53 (DNS)
   ↓
CloudFront (CDN)
   ↓
ALB (Load Balancer)
   ↓
ECS/EKS (Containers)
   ↓
RDS (PostgreSQL) + ElastiCache (Redis)
   ↓
S3 (File Storage)
```

### 5.2. AWS Resources Setup

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter: Access Key, Secret Key, Region, Output format

# Create ECR repository
aws ecr create-repository --repository-name forex4-backend
aws ecr create-repository --repository-name forex4-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 5.3. Build và Push Images

```bash
# Build backend
cd backend
docker build -t forex4-backend:latest -f Dockerfile.prod .

# Tag và push
docker tag forex4-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/forex4-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/forex4-backend:latest

# Tương tự cho frontend
cd ../client-app
docker build -t forex4-frontend:latest .
docker tag forex4-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/forex4-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/forex4-frontend:latest
```

### 5.4. ECS Deployment

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name forex4-prod

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster forex4-prod \
  --service-name forex4-backend \
  --task-definition forex4-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 6. CONFIGURATION

### 6.1. Nginx Configuration

**nginx.conf:**
```nginx
upstream backend_api {
    server backend:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # API Proxy
    location /api/ {
        proxy_pass http://backend_api/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket Support
    location /ws/ {
        proxy_pass http://backend_api/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

server {
    listen 443 ssl http2;
    server_name app.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    root /usr/share/nginx/html/app;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 7. DATABASE SETUP

### 7.1. PostgreSQL Configuration

```bash
# Connect to database
docker-compose exec postgres psql -U dbuser -d digital_utopia

# Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

# Verify tables
\dt

# Exit
\q
```

### 7.2. Run Migrations

```bash
# Check migration status
alembic current

# Run all migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback one version
alembic downgrade -1
```

---

## 8. SSL/TLS SETUP

### 8.1. Let's Encrypt với Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com -d admin.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
echo "0 0 * * * certbot renew --quiet" | sudo crontab -
```

---

## 9. MONITORING & LOGGING

### 9.1. Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### 9.2. Monitoring Setup

**Prometheus configuration:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'forex4-backend'
    static_configs:
      - targets: ['backend:8000']
```

---

## 10. BACKUP & RECOVERY

### 10.1. Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U dbuser digital_utopia > backup_$(date +%Y%m%d).sql

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U dbuser digital_utopia | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
echo "0 2 * * * /opt/forex4/backup.sh" | crontab -
```

### 10.2. Restore Database

```bash
# Restore from backup
gunzip < backup_20250106.sql.gz | docker-compose exec -T postgres psql -U dbuser digital_utopia
```

---

## 11. TROUBLESHOOTING

### 11.1. Common Issues

**Backend không start:**
```bash
# Check logs
docker-compose logs backend

# Check database connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"
```

**High memory usage:**
```bash
# Monitor resources
docker stats

# Restart services
docker-compose restart backend
```

**Database connection errors:**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Reset connections
docker-compose restart postgres
```

---

## 📞 SUPPORT

Nếu gặp vấn đề trong quá trình deployment:

1. Check logs: `docker-compose logs -f`
2. Verify configuration: Review `.env` file
3. Check health endpoints
4. Review error messages
5. Consult documentation

---

**Deployment Guide Version:** 1.0.0  
**Last Updated:** 06/12/2025  
**Status:** Production Ready ✅
