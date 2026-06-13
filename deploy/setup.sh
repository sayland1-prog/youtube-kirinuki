#!/bin/bash
# Hetzner VPS（Ubuntu 22.04）初回セットアップスクリプト
# 使い方: sudo bash deploy/setup.sh yourdomain.com your@email.com
set -e

DOMAIN="${1:?使い方: $0 <ドメイン> <メール>}"
EMAIL="${2:?使い方: $0 <ドメイン> <メール>}"

echo "=== Docker インストール ==="
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "=== Certbot（SSL）インストール ==="
apt-get install -y certbot

echo "=== SSL 証明書取得 ==="
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  -d "api.$DOMAIN"

echo "=== certbot 自動更新を cron に登録 ==="
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'docker compose -f /app/docker-compose.yml restart nginx'") | crontab -

echo "=== アプリディレクトリ作成 ==="
mkdir -p /app
echo "完了！次に /app に git clone してから deploy/start.sh を実行してください。"
