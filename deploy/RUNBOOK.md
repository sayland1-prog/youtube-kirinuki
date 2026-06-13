# デプロイ手順書

## 前提条件

| サービス | 目的 | URL |
|---------|------|-----|
| Hetzner Cloud | VPS サーバー | https://www.hetzner.com/cloud |
| Cloudflare R2 | 動画ファイル保存 | https://dash.cloudflare.com |
| Resend | メール送信 | https://resend.com |
| Vercel | フロントエンド | https://vercel.com |
| GitHub | CI/CD | https://github.com |

---

## Step 1: Hetzner VPS を作成する

1. https://www.hetzner.com/cloud → **新しいプロジェクト** を作成
2. **サーバー追加**:
   - タイプ: `CX42`（8コア/32GB/€30/月）
   - OS: `Ubuntu 22.04`
   - SSH キー: ローカルの公開鍵（`~/.ssh/id_ed25519.pub`）を登録
3. 作成後の IP アドレスをメモ（例: `49.12.xx.xx`）

---

## Step 2: ドメインの DNS 設定

お使いのドメインレジストラで以下を設定:

```
api.yourdomain.com  A  49.12.xx.xx   （サーバー IP）
```

DNS 伝播に数分〜1時間かかることがある。

---

## Step 3: Cloudflare R2 の設定

1. https://dash.cloudflare.com → **R2** → **バケットを作成**
   - バケット名: `kirinuki`（任意）
2. **R2 API トークン**を発行:
   - 「APIトークンを管理」→「トークンを作成」
   - 権限: `オブジェクト読み取り & 書き込み`
   - `Access Key ID` と `Secret Access Key` をメモ
3. **エンドポイント URL** をメモ:
   - `https://<AccountID>.r2.cloudflarestorage.com`
   - AccountID は R2 ダッシュボードの右上に表示

---

## Step 4: Resend の設定

1. https://resend.com → サインアップ
2. **ドメイン認証**: 「Domains」→ `yourdomain.com` を追加
   - 表示された DNS レコード（MX / DKIM / SPF）をドメインレジストラに追加
3. **API キー発行**: 「API Keys」→「Create API Key」
   - `re_xxxxxxxxxxxx` をメモ

---

## Step 5: サーバー初期セットアップ

```bash
# ローカルから SSH 接続
ssh root@49.12.xx.xx

# セットアップスクリプト実行（yourdomain.com を実際のドメインに変更）
curl -fsSL https://raw.githubusercontent.com/sayland1-prog/youtube-kirinuki/main/deploy/setup.sh \
  | bash -s yourdomain.com your@email.com
```

---

## Step 6: アプリをサーバーに配置

```bash
# サーバー上で実行
cd /app
git clone https://github.com/sayland1-prog/youtube-kirinuki.git .

# .env を作成
cp web/backend/.env.example web/backend/.env
nano web/backend/.env  # 以下の値を埋める
```

埋めるべき値:

```env
DATABASE_URL=postgresql://kirinuki:強いパスワード@db:5432/kirinuki
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=sk-ant-...
R2_ACCESS_KEY_ID=（Step 3 でメモした値）
R2_SECRET_ACCESS_KEY=（Step 3 でメモした値）
R2_BUCKET=kirinuki
R2_ENDPOINT=https://<AccountID>.r2.cloudflarestorage.com
RESEND_API_KEY=re_...（Step 4 でメモした値）
MAIL_FROM=noreply@yourdomain.com
SERVICE_URL=https://yourdomain.com
FRONTEND_ORIGIN=https://your-app.vercel.app
```

また、ルートの `.env`（docker-compose 用）を作成:

```bash
echo "POSTGRES_PASSWORD=強いパスワード" > /app/.env
```

---

## Step 7: nginx.conf のドメインを更新

```bash
sed -i 's/api.yourdomain.com/api.実際のドメイン.com/g' /app/deploy/nginx.conf
```

---

## Step 8: アプリ起動

```bash
cd /app
bash deploy/start.sh
```

ブラウザで `https://api.yourdomain.com/health` にアクセスして `{"status":"ok"}` が返れば成功。

---

## Step 9: Vercel フロントエンドのデプロイ

1. https://vercel.com → **Add New Project**
2. GitHub の `sayland1-prog/youtube-kirinuki` リポジトリを選択
3. **Root Directory**: `web/frontend`
4. **環境変数**を追加:
   - `NEXT_PUBLIC_API_URL` = `https://api.yourdomain.com`
5. **Deploy** をクリック
6. 割り当てられた Vercel URL（例: `your-app.vercel.app`）をメモ

---

## Step 10: GitHub Actions で自動デプロイを設定

1. GitHub → リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. 以下のシークレットを追加:
   - `SERVER_HOST` = `49.12.xx.xx`（サーバー IP）
   - `SERVER_USER` = `root`
   - `SERVER_SSH_KEY` = ローカルの秘密鍵の中身（`cat ~/.ssh/id_ed25519`）

これ以降、`main` ブランチに push するたびに自動デプロイが走る。

---

## Step 11: バックエンドの FRONTEND_ORIGIN を更新

Vercel の URL が確定したらサーバーの `.env` を更新:

```bash
# サーバー上で
nano /app/web/backend/.env
# FRONTEND_ORIGIN=https://your-app.vercel.app  に変更

docker compose restart api
```

---

## 確認チェックリスト

- [ ] `https://api.yourdomain.com/health` → `{"status":"ok"}`
- [ ] Vercel フロントページが表示される
- [ ] YouTube URL を入力 → ジョブ送信 → 進捗ページに遷移する
- [ ] 処理完了後メールが届く
- [ ] 失敗時もメールが届く

---

## トラブルシューティング

```bash
# API ログ
docker compose logs -f api

# Worker ログ
docker compose logs -f worker

# DB 確認
docker compose exec db psql -U kirinuki -c "SELECT id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 10;"

# コンテナ再起動
docker compose restart api worker
```
