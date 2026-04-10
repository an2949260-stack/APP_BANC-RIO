"""script para verificar saúde da aplicação"""
#!/bin/bash

set -e

API_URL="${1:-http://localhost:8000}"
RETRIES=5
DELAY=2

echo "🏥 Verificando saúde de: $API_URL"

for i in $(seq 1 $RETRIES); do
    echo "Tentativa $i/$RETRIES..."
    
    if curl -s "$API_URL/api/health" > /dev/null 2>&1; then
        echo "✅ API está saudável!"
        exit 0
    fi
    
    if [ $i -lt $RETRIES ]; then
        echo "⏳ Aguardando $DELAY segundos..."
        sleep $DELAY
    fi
done

echo "❌ API não está respondendo após $RETRIES tentativas"
exit 1
