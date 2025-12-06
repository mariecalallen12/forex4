#!/bin/bash

# ================================================================
# DEPLOYMENT SERVER PREPARATION SCRIPT
# Digital Utopia Platform - Production/Staging Setup
# ================================================================

set -e  # Exit on error

echo "================================================================"
echo "   Digital Utopia Platform - Server Preparation"
echo "================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root. Use a regular user with sudo privileges.${NC}"
    exit 1
fi

echo "This script will prepare your server for deployment."
echo ""
read -p "Is this for (1) Staging or (2) Production? Enter 1 or 2: " ENV_TYPE

if [ "$ENV_TYPE" == "1" ]; then
    ENVIRONMENT="staging"
    DOMAIN="staging.yourdomain.com"
elif [ "$ENV_TYPE" == "2" ]; then
    ENVIRONMENT="production"
    DOMAIN="yourdomain.com"
else
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Preparing $ENVIRONMENT environment...${NC}"
echo ""

# ================================================================
# 1. SYSTEM UPDATE
# ================================================================
echo "Step 1/10: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# ================================================================
# 2. INSTALL DOCKER
# ================================================================
echo ""
echo "Step 2/10: Installing Docker..."

if command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker already installed${NC}"
    docker --version
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}Docker installed successfully${NC}"
fi

# ================================================================
# 3. INSTALL DOCKER COMPOSE
# ================================================================
echo ""
echo "Step 3/10: Installing Docker Compose..."

if command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose already installed${NC}"
    docker-compose --version
else
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
fi

# ================================================================
# 4. INSTALL ADDITIONAL TOOLS
# ================================================================
echo ""
echo "Step 4/10: Installing additional tools..."
sudo apt install -y git nginx certbot python3-certbot-nginx ufw fail2ban

# ================================================================
# 5. CONFIGURE FIREWALL
# ================================================================
echo ""
echo "Step 5/10: Configuring firewall..."

sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw status

echo -e "${GREEN}Firewall configured${NC}"

# ================================================================
# 6. CREATE PROJECT DIRECTORY
# ================================================================
echo ""
echo "Step 6/10: Creating project directory..."

PROJECT_DIR="/opt/forex4"
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR

cd $PROJECT_DIR
echo -e "${GREEN}Project directory created: $PROJECT_DIR${NC}"

# ================================================================
# 7. CREATE DATA DIRECTORIES
# ================================================================
echo ""
echo "Step 7/10: Creating data directories..."

mkdir -p data/postgres
mkdir -p data/redis
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p nginx/logs
mkdir -p backups

echo -e "${GREEN}Data directories created${NC}"

# ================================================================
# 8. SETUP SSH FOR DEPLOYMENT
# ================================================================
echo ""
echo "Step 8/10: Setting up SSH for deployment..."

# Create deploy user if doesn't exist
if ! id "deploy" &>/dev/null; then
    sudo useradd -m -s /bin/bash deploy
    sudo usermod -aG docker deploy
    echo -e "${GREEN}Deploy user created${NC}"
else
    echo -e "${YELLOW}Deploy user already exists${NC}"
fi

# Setup SSH directory
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo touch /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh

echo ""
echo -e "${YELLOW}=== IMPORTANT ===${NC}"
echo "Add your GitHub Actions public SSH key to:"
echo "/home/deploy/.ssh/authorized_keys"
echo ""
echo "You can add it with:"
echo "sudo nano /home/deploy/.ssh/authorized_keys"
echo ""
read -p "Press Enter to continue after adding the SSH key..."

# ================================================================
# 9. CREATE ENVIRONMENT FILE
# ================================================================
echo ""
echo "Step 9/10: Creating environment file..."

cat > $PROJECT_DIR/.env <<EOF
# Application
APP_NAME=Digital Utopia Platform
DEBUG=false
ENVIRONMENT=$ENVIRONMENT

# Security - CHANGE THESE!
SECRET_KEY=CHANGE-THIS-TO-RANDOM-SECRET-KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - CHANGE THESE!
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE-THIS-PASSWORD
POSTGRES_DB=digital_utopia_$ENVIRONMENT
POSTGRES_PORT=5432

# Redis - CHANGE THESE!
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE-THIS-PASSWORD

# Ports
BACKEND_PORT=8000
CLIENT_PORT=3000
ADMIN_PORT=3001

# CORS
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
EOF

echo -e "${GREEN}Environment file created at $PROJECT_DIR/.env${NC}"
echo -e "${RED}IMPORTANT: Edit this file and change all passwords!${NC}"
echo ""
read -p "Press Enter to edit .env file now..."
nano $PROJECT_DIR/.env

# ================================================================
# 10. CONFIGURE FAIL2BAN
# ================================================================
echo ""
echo "Step 10/10: Configuring Fail2ban..."

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

echo -e "${GREEN}Fail2ban configured${NC}"

# ================================================================
# FINAL SUMMARY
# ================================================================
echo ""
echo "================================================================"
echo "              SERVER PREPARATION COMPLETE!"
echo "================================================================"
echo ""
echo -e "${GREEN}✓${NC} Docker installed"
echo -e "${GREEN}✓${NC} Docker Compose installed"
echo -e "${GREEN}✓${NC} Firewall configured"
echo -e "${GREEN}✓${NC} Project directory created: $PROJECT_DIR"
echo -e "${GREEN}✓${NC} Data directories created"
echo -e "${GREEN}✓${NC} Deploy user created"
echo -e "${GREEN}✓${NC} Environment file created"
echo -e "${GREEN}✓${NC} Security tools installed"
echo ""
echo "================================================================"
echo "              NEXT STEPS"
echo "================================================================"
echo ""
echo "1. Clone your repository:"
echo "   cd $PROJECT_DIR"
echo "   git clone https://github.com/mariecalallen12/forex4.git ."
echo ""
echo "2. Verify .env configuration:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "3. Pull Docker images:"
echo "   docker-compose pull"
echo ""
echo "4. Start services:"
echo "   docker-compose up -d"
echo ""
echo "5. Check logs:"
echo "   docker-compose logs -f"
echo ""
echo "6. Setup SSL certificate (if not done):"
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
echo "7. Configure Nginx reverse proxy (if needed)"
echo ""
echo "================================================================"
echo "              IMPORTANT SECURITY NOTES"
echo "================================================================"
echo ""
echo -e "${RED}⚠ CHANGE ALL DEFAULT PASSWORDS IN .env${NC}"
echo -e "${RED}⚠ ADD SSH PUBLIC KEY TO /home/deploy/.ssh/authorized_keys${NC}"
echo -e "${RED}⚠ SETUP SSL CERTIFICATE WITH CERTBOT${NC}"
echo -e "${RED}⚠ REGULAR BACKUPS ARE ESSENTIAL${NC}"
echo ""
echo "================================================================"
echo ""
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN"
echo "Project Directory: $PROJECT_DIR"
echo ""
echo "Happy deploying! 🚀"
echo ""
