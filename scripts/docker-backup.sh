#!/bin/bash
# Script backup database
# Usage: ./scripts/docker-backup.sh

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_FILE="backup_$DATE.sql.gz"

echo "💾 Creating database backup..."

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U postgres digital_utopia | gzip > $BACKUP_DIR/$BACKUP_FILE

echo "✅ Backup created: $BACKUP_FILE"
echo "📁 Location: $BACKUP_DIR/$BACKUP_FILE"

# Show backup size
SIZE=$(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)
echo "📊 Size: $SIZE"

# Clean old backups (keep last 7 days)
echo "🧹 Cleaning old backups (keeping last 7 days)..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Show remaining backups
echo ""
echo "📋 Current backups:"
ls -lh $BACKUP_DIR/backup_*.sql.gz 2>/dev/null || echo "No backups found"
