#!/bin/bash
set -e

echo "⏳ Waiting for Weaviate to be ready..."
until curl -s -o /dev/null -w "%{http_code}" http://weaviate:8080/v1/.well-known/ready | grep -q "200"; do
  echo "⚠️  Weaviate is not ready yet ...."
  sleep 3
done
echo "✅ Weaviate is ready!"

echo "⏳ Running ingest script..."
python /app/ingest.py

echo "✅ Ingest complete, starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
