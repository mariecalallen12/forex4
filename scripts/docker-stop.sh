#!/bin/bash
# Script dừng Docker deployment
# Usage: ./scripts/docker-stop.sh [dev|prod]

set -e

MODE=${1:-prod}

echo "🛑 Stopping Digital Utopia Platform ($MODE mode)..."

if [ "$MODE" == "dev" ]; then
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Development environment stopped!"
else
    docker-compose down
    echo "✅ Production environment stopped!"
fi

echo ""
echo "💡 To remove all data: ./scripts/docker-clean.sh"
