#!/bin/bash
# アプリ起動 / 更新スクリプト（/app で実行）
set -e

cd /app

echo "=== DB マイグレーション ==="
docker compose run --rm api python -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('DB マイグレーション完了')
"

echo "=== コンテナ起動 ==="
docker compose pull
docker compose up -d --build

echo "=== ヘルスチェック（30秒待機）==="
sleep 30
curl -sf http://localhost:8000/health && echo "API: OK" || echo "API: NG（ログを確認してください）"

echo "完了"
