"""Script para backup do banco de dados"""
#!/bin/bash

set -e

BACKUP_DIR="${1:-.backups}"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="banco_app"

echo "📦 Iniciando backup do banco de dados..."

mkdir -p $BACKUP_DIR

# Com Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "Usando Docker Compose..."
    docker-compose exec -T postgres pg_dump -U bancario $DB_NAME | gzip > $BACKUP_DIR/banco_$DATE.sql.gz
else
    # Local sem Docker
    echo "Usando psql local..."
    pg_dump -U bancario -d $DB_NAME | gzip > $BACKUP_DIR/banco_$DATE.sql.gz
fi

echo "✅ Backup criado: $BACKUP_DIR/banco_$DATE.sql.gz"

# Listar últimos 5 backups
echo ""
echo "📋 Últimos backups:"
ls -lh $BACKUP_DIR/ | tail -6

# Limpeza de backups antigos (mais de 7 dias)
echo ""
echo "🧹 Limpando backups antigos..."
find $BACKUP_DIR -mtime +7 -delete
echo "✅ Limpeza concluída"
