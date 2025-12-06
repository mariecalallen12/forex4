#!/bin/bash
# Script khởi động Docker deployment
# Usage: ./scripts/docker-start.sh [dev|prod]

set -e

MODE=${1:-prod}

echo "🚀 Starting Digital Utopia Platform in $MODE mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
    echo "⚠️  Especially change SECRET_KEY and database passwords!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/postgres data/redis backups nginx/logs

# Set permissions
chmod 700 data/postgres data/redis

if [ "$MODE" == "dev" ]; then
    echo "🔧 Starting DEVELOPMENT environment..."
    docker-compose -f docker-compose.dev.yml up -d
    
    echo ""
    echo "✅ Development environment started!"
    echo ""
    echo "🌐 Access points:"
    echo "   Backend API:     http://localhost:8000"
    echo "   API Docs:        http://localhost:8000/docs"
    echo "   Client App:      http://localhost:5173"
    echo "   Admin App:       http://localhost:5174"
    echo "   PgAdmin:         http://localhost:5050"
    echo "   Redis Commander: http://localhost:8081"
    echo ""
    echo "📝 View logs: docker-compose -f docker-compose.dev.yml logs -f"
    
else
    echo "🏭 Starting PRODUCTION environment..."
    
    # Build images
    echo "🔨 Building Docker images..."
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Run database migrations
    echo "🗄️  Running database migrations..."
    docker-compose exec -T backend alembic upgrade head || echo "⚠️  Migration failed or already up to date"
    
    echo ""
    echo "✅ Production environment started!"
    echo ""
    echo "🌐 Access points:"
    echo "   Main Site:    http://localhost"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo "   Client App:   http://localhost:3000"
    echo "   Admin App:    http://localhost:3001"
    echo ""
    echo "🔍 Health check: curl http://localhost/health"
    echo "📝 View logs: docker-compose logs -f"
fi

echo ""
echo "🎉 Deployment complete!"
