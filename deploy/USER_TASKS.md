# 初めての方向け：本番公開までの手順書

このファイルに書かれた作業は、**あなた自身がブラウザやターミナルで行う必要がある操作**です。
上から順番に進めてください。所要時間の目安は合計 **2〜3 時間**です。

> **困ったときは** Claude に「Step X が分からない」と伝えれば一緒に解決できます。

---

## Step 1: SSH キーを作成する（サーバーへの鍵）

SSH キーとは「パスワードの代わりにサーバーへログインするための鍵」です。
すでに作成済みの場合はスキップしてください。

**ターミナル（Mac のアプリ）を開いて以下を実行:**

```bash
# 鍵ファイルが既にあるか確認
ls ~/.ssh/id_ed25519.pub
```

- `No such file or directory` と表示された → 鍵を作成する（下記を実行）
- ファイル名が表示された → このステップはスキップ

```bash
# 鍵を作成（質問が出たら全て Enter を押してOK）
ssh-keygen -t ed25519 -C "your@email.com"
```

作成後、公開鍵の中身をコピーしておく（後で使います）:

```bash
cat ~/.ssh/id_ed25519.pub
# 表示された1行（ssh-ed25519 AAAA... で始まる）をコピーしておく
```

- [ ] 完了

---

## Step 2: Hetzner Cloud でサーバーを借りる

Hetzner（ヘッツナー）はドイツのクラウドサービスです。月 €30 ほどで動画処理に十分なスペックのサーバーが借りられます。

### 2-1. アカウント作成

1. https://www.hetzner.com/cloud を開く
2. 右上の「Get started」→「Sign up」
3. メールアドレス・パスワードを入力して登録
4. 届いた確認メールのリンクをクリック
5. クレジットカードを登録（使った分だけ課金）

### 2-2. プロジェクト作成

1. ログイン後、「+ New project」をクリック
2. プロジェクト名を入力（例: `kirinuki`）→「Add project」

### 2-3. SSH キーを登録

1. 左メニュー「Security」→「SSH Keys」→「Add SSH key」
2. 「Public key」の欄に、Step 1 でコピーした `ssh-ed25519 AAAA...` の1行を貼り付ける
3. 名前を入力（例: `my-mac`）→「Add SSH key」

### 2-4. サーバーを作成

1. 左メニュー「Servers」→「Add server」
2. 以下のように選択:
   - **Location**: Nuremberg（どこでもOK）
   - **Image**: Ubuntu 22.04
   - **Type**: Shared vCPU → **x86** → `CX42`（8コア / 32GB RAM / €30.99/月）
   - **SSH Keys**: Step 2-3 で登録したキーにチェック
3. 「Create & Buy now」をクリック
4. 作成後、一覧に表示される **IP アドレス**（例: `49.12.34.56`）をメモ

- [ ] IPアドレスをメモした: `__________`

---

## Step 3: ドメインの DNS を設定する

「ドメイン」とは `yourdomain.com` のような URL のことです。
お持ちのドメインのレジストラ（お名前.com / Cloudflare / Namecheap など）で以下を設定します。

**レジストラの管理画面で「DNS レコードの追加」を行う:**

| 種類 | ホスト名 | 値 |
|------|---------|-----|
| A | `api` | Step 2 でメモしたサーバーの IP アドレス |

※ レジストラによって画面が違います。「DNS管理」や「ネームサーバー設定」などのメニューを探してください。

設定後、反映を確認（ターミナルで実行、`49.12.34.56` の部分が自分のIPになれば成功）:

```bash
dig api.yourdomain.com +short
# サーバーのIPアドレスが表示されればOK（最大1時間かかることがある）
```

- [ ] DNS を設定した
- [ ] `dig` コマンドで IP アドレスが表示された

---

## Step 4: Cloudflare R2 を設定する（動画の保存場所）

R2 は動画ファイルを保存するためのクラウドストレージです。転送料が無料なので採用しています。

### 4-1. Cloudflare アカウント作成

1. https://dash.cloudflare.com/sign-up を開く
2. メールアドレスとパスワードを入力して登録
3. 届いた確認メールのリンクをクリック

### 4-2. バケット（保存場所）を作成

1. ログイン後、左メニュー「R2 Object Storage」をクリック
2. 「Create bucket」をクリック
3. Bucket name に `kirinuki` と入力
4. Location: **APAC** を選択
5. 「Create bucket」をクリック

### 4-3. API トークンを発行

1. R2 のページ右上に「Manage R2 API Tokens」というリンクがある → クリック
2. 「Create API Token」をクリック
3. 以下を設定:
   - Token name: `kirinuki-token`（任意）
   - Permissions: **Object Read & Write**
   - Specify bucket: `kirinuki` を選択
4. 「Create API Token」をクリック
5. 表示される値を**今すぐメモ**（この画面を閉じると Secret は二度と見られません）:
   - **Access Key ID**: `__________`
   - **Secret Access Key**: `__________`

### 4-4. アカウント ID を確認

1. Cloudflare ダッシュボードのトップページ（https://dash.cloudflare.com）を開く
2. 右側に「Account ID」が表示される → **コピーしてメモ**
   - エンドポイント URL: `https://<アカウントID>.r2.cloudflarestorage.com`

- [ ] Access Key ID をメモした: `__________`
- [ ] Secret Access Key をメモした
- [ ] アカウント ID をメモした: `__________`

---

## Step 5: Resend を設定する（メール送信サービス）

処理完了や失敗をユーザーにメールで通知するためのサービスです。

### 5-1. アカウント作成

1. https://resend.com を開く
2. 「Get Started」→「Sign Up」
3. GitHub アカウントまたはメールで登録

### 5-2. 送信ドメインを認証する

1. ログイン後、左メニュー「Domains」→「Add Domain」
2. 自分のドメイン（例: `yourdomain.com`）を入力 → 「Add」
3. 表示された DNS レコード（3〜4行）をドメインレジストラの DNS 設定に追加する
   - Step 3 と同じ画面で追加します
4. 「Verify DNS Records」をクリック → 全て ✅ になるまで待つ（最大1時間）

### 5-3. API キーを発行

1. 左メニュー「API Keys」→「Create API Key」
2. Name に `kirinuki`（任意）と入力
3. Permission: **Full access**
4. 「Add」をクリック
5. 表示された `re_xxxx...` をメモ（この画面でしか表示されません）

- [ ] ドメインが Verified になった
- [ ] API キーをメモした: `re___________`

---

## Step 6: サーバーにアプリをセットアップする

ここからはサーバー上での作業です。ターミナルから操作します。

### 6-1. サーバーに SSH 接続

```bash
# yourdomain.com の部分を Step 2 でメモしたIPアドレスに変更
ssh root@49.12.34.56
```

初回接続時に「Are you sure you want to continue connecting?」と聞かれたら `yes` と入力して Enter。

### 6-2. セットアップスクリプトを実行

```bash
# yourdomain.com と your@email.com を自分のものに変更
curl -fsSL https://raw.githubusercontent.com/sayland1-prog/youtube-kirinuki/main/deploy/setup.sh \
  | bash -s yourdomain.com your@email.com
```

Docker・SSL証明書などを自動インストールします（5〜10分かかります）。

### 6-3. リポジトリをクローン

```bash
mkdir -p /app && cd /app
git clone https://github.com/sayland1-prog/youtube-kirinuki.git .
```

### 6-4. 環境変数ファイルを作成

```bash
cp web/backend/.env.example web/backend/.env
nano web/backend/.env
```

`nano` というテキストエディタが開きます。各行を以下の値に書き換えてください。
（矢印キーで移動、書き換えたら `Ctrl+O` → Enter で保存、`Ctrl+X` で閉じる）

```env
DATABASE_URL=postgresql://kirinuki:あなたが決めた強いパスワード@db:5432/kirinuki
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=sk-ant-（Claude の API キー）
R2_ACCESS_KEY_ID=（Step 4-3 でメモした値）
R2_SECRET_ACCESS_KEY=（Step 4-3 でメモした値）
R2_BUCKET=kirinuki
R2_ENDPOINT=https://（Step 4-4 のアカウントID）.r2.cloudflarestorage.com
RESEND_API_KEY=（Step 5-3 でメモした re_xxx...）
MAIL_FROM=noreply@yourdomain.com
SERVICE_URL=https://yourdomain.com
FRONTEND_ORIGIN=https://your-app.vercel.app  ← Step 7 完了後に更新する
MAX_CONCURRENT_JOBS=10
```

### 6-5. Docker Compose 用のパスワードファイルを作成

```bash
# 6-4 で決めたパスワードと同じものを入力
echo "POSTGRES_PASSWORD=あなたが決めた強いパスワード" > /app/.env
```

### 6-6. nginx の設定にドメインを反映

```bash
# yourdomain.com を自分のドメインに変更
sed -i 's/api.yourdomain.com/api.自分のドメイン.com/g' /app/deploy/nginx.conf
```

### 6-7. アプリを起動

```bash
bash deploy/start.sh
```

完了後、以下を実行してレスポンスが返れば成功です:

```bash
curl https://api.yourdomain.com/health
# {"status":"ok"} と表示されればOK
```

- [ ] SSH 接続できた
- [ ] `.env` に全ての値を入力した
- [ ] `{"status":"ok"}` が返ってきた

---

## Step 7: Vercel でフロントエンドを公開する

Vercel はフロントエンド（ユーザーが見る画面）を無料でホスティングできるサービスです。

### 7-1. アカウント作成

1. https://vercel.com を開く
2. 「Sign Up」→「Continue with GitHub」（GitHub アカウントで登録が便利）

### 7-2. プロジェクトを作成

1. ダッシュボードの「Add New...」→「Project」
2. 「Import Git Repository」で `sayland1-prog/youtube-kirinuki` を選択
   - 見つからない場合: 「Adjust GitHub App Permissions」→ リポジトリを追加
3. 以下を設定:
   - **Root Directory**: `web/frontend` と入力（重要）
   - **Framework Preset**: Next.js（自動で検出される）
4. 「Environment Variables」を開いて追加:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://api.yourdomain.com`（自分のドメイン）
5. 「Deploy」をクリック

### 7-3. デプロイ後の URL をメモ

デプロイが完了すると URL が表示される（例: `kirinuki.vercel.app`）。

- [ ] Vercel の URL をメモした: `https://___________`

---

## Step 8: サーバーの設定を Vercel URL で更新する

Step 7 で確定した Vercel の URL を、サーバーの設定に反映させます。

```bash
# ターミナルでサーバーに SSH 接続
ssh root@49.12.34.56

# .env を開いて FRONTEND_ORIGIN を実際の Vercel URL に書き換える
nano /app/web/backend/.env
# FRONTEND_ORIGIN=https://kirinuki.vercel.app  ← 実際の URL に変更

# API を再起動して設定を反映
docker compose -f /app/docker-compose.yml restart api
```

- [ ] FRONTEND_ORIGIN を更新してAPIを再起動した

---

## Step 9: GitHub Actions で自動デプロイを設定する

コードを更新したときに自動でサーバーにデプロイされるようにします。

1. GitHub のリポジトリページ（https://github.com/sayland1-prog/youtube-kirinuki）を開く
2. 上部メニュー「Settings」→ 左メニュー「Secrets and variables」→「Actions」
3. 「New repository secret」で以下の3つを追加（1つずつ「Add secret」をクリック）:

| Name | Value |
|------|-------|
| `SERVER_HOST` | サーバーの IP アドレス（例: `49.12.34.56`） |
| `SERVER_USER` | `root` |
| `SERVER_SSH_KEY` | ローカルのターミナルで `cat ~/.ssh/id_ed25519` を実行した結果（`-----BEGIN OPENSSH PRIVATE KEY-----` から始まる全文） |

4. 動作確認: 適当なファイルを編集して `main` に push し、「Actions」タブでデプロイが成功するか確認

- [ ] 3つのシークレットを登録した
- [ ] Actions が成功した（緑の ✅ が表示される）

---

## Step 10: 最終動作確認

全て完了したら、実際に使ってみて確認します。

- [ ] `https://kirinuki.vercel.app`（自分の Vercel URL）をブラウザで開いてフォームが表示される
- [ ] 切り抜き許可のある配信者の YouTube URL とメールアドレスを入力して送信
- [ ] 進捗ページ（`/jobs/xxxxxxxx-...`）に自動遷移し、「動画を準備中」などのステータスが表示される
- [ ] 5秒ごとにステータスが更新される
- [ ] 処理完了後（15〜30分）、入力したメールにダウンロードリンクが届く
- [ ] 失敗した場合もメールで通知が届く

---

## メモ欄（ここに書き込みながら進めてください）

| 項目 | 値 |
|------|-----|
| サーバー IP | |
| ドメイン | |
| DB パスワード | |
| R2 アカウント ID | |
| R2 Access Key ID | |
| Vercel URL | |
| Anthropic API キー | sk-ant-... |

---

## よくあるトラブル

| 症状 | 確認すること |
|------|------------|
| SSH 接続できない | IP アドレスが合っているか / SSH キーが正しく登録されているか |
| `curl health` が返ってこない | DNS 伝播が終わっていないか（`dig api.ドメイン +short` で IP が表示されるか確認） |
| メールが届かない | Resend のドメインが Verified になっているか / MAIL_FROM が認証済みドメインと一致しているか |
| Vercel でビルドエラー | Root Directory が `web/frontend` に設定されているか |
| 処理が進まない | `ssh root@IP` してから `docker compose -f /app/docker-compose.yml logs worker` でログを確認 |
