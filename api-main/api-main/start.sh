#!/bin/bash
set -e

echo "🚀 Iniciando aplicação..."

# Roda as migrations
echo "📦 Executando migrations..."
alembic upgrade head

# Verifica se as migrations foram executadas com sucesso
if [ $? -eq 0 ]; then
    echo "✅ Migrations executadas com sucesso!"
else
    echo "❌ Erro ao executar migrations!"
    exit 1
fi

# Inicia o servidor
echo "🌐 Iniciando servidor Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
