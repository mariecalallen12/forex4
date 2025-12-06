#!/bin/bash
# Script kiểm tra health của tất cả services
# Usage: ./scripts/docker-health.sh

echo "🏥 Checking health of all services..."
echo ""

# Check if services are running
echo "📊 Service Status:"
docker-compose ps
echo ""

# Check backend health
echo "🔧 Backend Health:"
curl -s http://localhost:8000/health || echo "❌ Backend not responding"
echo ""

# Check nginx health
echo "🌐 Nginx Health:"
curl -s http://localhost/health || echo "❌ Nginx not responding"
echo ""

# Check PostgreSQL
echo "🗄️  PostgreSQL Health:"
docker-compose exec postgres pg_isready || echo "❌ PostgreSQL not ready"
echo ""

# Check Redis
echo "💾 Redis Health:"
docker-compose exec redis redis-cli ping || echo "❌ Redis not responding"
echo ""

# Resource usage
echo "📈 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

echo "✅ Health check complete!"
