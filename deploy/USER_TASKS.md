# ユーザーが手動で行う必要があるタスク一覧

Claude では実行できないアカウント操作・ブラウザ操作をまとめたチェックリスト。
上から順番に実施してください。

---

## 1. Hetzner Cloud — サーバー調達

- [ ] https://www.hetzner.com/cloud にアクセスしてアカウント作成
- [ ] 新しいプロジェクトを作成
- [ ] サーバーを追加
  - タイプ: `CX42`（8コア / 32GB / €30/月）
  - OS: `Ubuntu 22.04`
  - SSH キー: ローカルの公開鍵（`cat ~/.ssh/id_ed25519.pub`）を登録
- [ ] 作成後の **サーバー IP アドレス** をメモ

---

## 2. ドメイン DNS 設定

- [ ] お使いのドメインレジストラで以下の A レコードを追加
  ```
  api.yourdomain.com  →  <サーバーIP>
  ```
- [ ] DNS 伝播を確認（数分〜1時間）
  ```bash
  dig api.yourdomain.com +short
  ```

---

## 3. Cloudflare R2 — ストレージ

- [ ] https://dash.cloudflare.com → **R2** → バケットを作成
  - バケット名: `kirinuki`
  - リージョン: APAC
- [ ] R2 API トークンを発行
  - 「R2 APIトークンを管理」→「APIトークンを作成」
  - 権限: オブジェクト読み取り & 書き込み
  - **Access Key ID** をメモ
  - **Secret Access Key** をメモ（この画面でしか表示されない）
- [ ] **アカウント ID** をメモ（ダッシュボード右上に表示）
  - エンドポイント形式: `https://<アカウントID>.r2.cloudflarestorage.com`

---

## 4. Resend — メール送信

- [ ] https://resend.com にサインアップ
- [ ] 「Domains」→ 自分のドメインを追加
  - 表示された DNS レコード（MX / DKIM / SPF）をドメインレジストラに追加
  - Verified になるまで待つ
- [ ] 「API Keys」→「Create API Key」
  - **API キー**（`re_xxxx...`）をメモ

---

## 5. サーバー上での操作

- [ ] SSH でサーバーに接続
  ```bash
  ssh root@<サーバーIP>
  ```
- [ ] セットアップスクリプトを実行
  ```bash
  curl -fsSL https://raw.githubusercontent.com/sayland1-prog/youtube-kirinuki/main/deploy/setup.sh \
    | bash -s yourdomain.com your@email.com
  ```
- [ ] リポジトリをクローン
  ```bash
  cd /app && git clone https://github.com/sayland1-prog/youtube-kirinuki.git .
  ```
- [ ] `.env` を作成して値を埋める
  ```bash
  cp web/backend/.env.example web/backend/.env
  nano web/backend/.env
  ```
  埋める値:
  ```env
  DATABASE_URL=postgresql://kirinuki:強いパスワード@db:5432/kirinuki
  REDIS_URL=redis://redis:6379/0
  ANTHROPIC_API_KEY=sk-ant-...
  R2_ACCESS_KEY_ID=（Step 3 でメモ）
  R2_SECRET_ACCESS_KEY=（Step 3 でメモ）
  R2_BUCKET=kirinuki
  R2_ENDPOINT=https://<アカウントID>.r2.cloudflarestorage.com
  RESEND_API_KEY=re_...（Step 4 でメモ）
  MAIL_FROM=noreply@yourdomain.com
  SERVICE_URL=https://yourdomain.com
  FRONTEND_ORIGIN=https://your-app.vercel.app  ← Step 6 完了後に更新
  MAX_CONCURRENT_JOBS=10
  ```
- [ ] docker-compose 用 `.env` を作成
  ```bash
  echo "POSTGRES_PASSWORD=強いパスワード" > /app/.env
  ```
- [ ] nginx.conf のドメインを書き換え
  ```bash
  sed -i 's/api.yourdomain.com/api.実際のドメイン.com/g' /app/deploy/nginx.conf
  ```
- [ ] アプリを起動
  ```bash
  bash deploy/start.sh
  ```
- [ ] 動作確認
  ```bash
  curl https://api.yourdomain.com/health
  # → {"status":"ok"} が返れば OK
  ```

---

## 6. Vercel — フロントエンドデプロイ

- [ ] https://vercel.com にサインアップ（GitHub アカウントで連携推奨）
- [ ] 「Add New Project」→ `sayland1-prog/youtube-kirinuki` を選択
- [ ] 設定:
  - **Root Directory**: `web/frontend`
  - **Framework Preset**: Next.js（自動検出）
- [ ] 環境変数を追加:
  - `NEXT_PUBLIC_API_URL` = `https://api.yourdomain.com`
- [ ] **Deploy** をクリック
- [ ] デプロイ後の URL（例: `your-app.vercel.app`）をメモ

---

## 7. サーバーの FRONTEND_ORIGIN を更新

Vercel URL が確定したらサーバーの `.env` を更新:

- [ ] SSH でサーバーに接続
  ```bash
  nano /app/web/backend/.env
  # FRONTEND_ORIGIN=https://your-app.vercel.app  を実際の URL に変更
  docker compose restart api
  ```

---

## 8. GitHub Actions — 自動デプロイ設定

- [ ] GitHub → リポジトリ → **Settings** → **Secrets and variables** → **Actions**
- [ ] 以下の3つのシークレットを追加:
  | シークレット名 | 値 |
  |--------------|-----|
  | `SERVER_HOST` | サーバーの IP アドレス |
  | `SERVER_USER` | `root` |
  | `SERVER_SSH_KEY` | ローカル秘密鍵の中身（`cat ~/.ssh/id_ed25519`） |
- [ ] 設定後、適当なファイルを編集して `main` に push し、Actions が成功することを確認

---

## 9. 最終動作確認

- [ ] Vercel の URL をブラウザで開いてトップページが表示される
- [ ] YouTube URL + メールアドレスを入力して送信
- [ ] 進捗ページ（`/jobs/<uuid>`）に自動遷移し、ステータスが更新される
- [ ] 処理完了後、入力したメールにダウンロードリンクが届く
- [ ] 失敗時もメールが届くことを確認

---

## メモ欄

| 項目 | 値 |
|------|-----|
| サーバー IP | |
| ドメイン | |
| R2 アカウント ID | |
| Vercel URL | |
