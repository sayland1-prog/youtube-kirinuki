# バグレポート — youtube-kirinuki Web サービス

> 担当：デバッグ担当 / 対象：初回実装コード全体

---

## 修正済みバグ一覧

### Bug 1 — CORS ワイルドカードサブドメインが無効 ✅ 修正済み
- **ファイル**: `web/backend/main.py`
- **問題**: `allow_origins=["https://*.vercel.app"]` は FastAPI/Starlette では動作しない。`allow_origins` はリテラル一致のみ。
- **影響**: 本番 Vercel ドメインからの API リクエストが全て CORS エラーになる。
- **修正**: `allow_origin_regex=r"https://.*\.vercel\.app"` に変更。

### Bug 2 — クリップタイトルがファイル名ステムになっていた ✅ 修正済み
- **ファイル**: `web/backend/worker.py`
- **問題**: R2 にアップロードしたクリップの `title` フィールドに `clips.json` の実際のタイトルではなく、ファイル名ステム（`"01_タイトル"` 等）が入っていた。
- **影響**: 完了メール・ダウンロード画面に表示されるタイトルが不正確。
- **修正**: `clips.json` を読み込んで番号インデックスでタイトルを引く処理を追加。

### Bug 3 — root layout に `"use client"` → SSR 破壊 ✅ 修正済み
- **ファイル**: `web/frontend/app/layout.tsx`
- **問題**: `"use client"` を root layout に書くと Next.js App Router 全体がクライアントバンドルに落ちる。サーバーコンポーネントが使えなくなり、Metadata export も効かなくなる。
- **影響**: SEO（OGP/メタタグ）が機能しない。ページが重くなる。
- **修正**: `Providers` コンポーネント（`app/providers.tsx`）を新規作成して `QueryClientProvider` を分離。`layout.tsx` はサーバーコンポーネントに戻し、`Metadata` を export に変更。

### Bug 4 — `use(params)` は Next.js 15 API ✅ 修正済み
- **ファイル**: `web/frontend/app/jobs/[id]/page.tsx`
- **問題**: `use(params)` は React 19 / Next.js 15 の新 API。`package.json` が Next.js 14 を指定しているため型エラー＆ランタイムエラーになる。
- **影響**: `/jobs/[id]` ページが起動時クラッシュ。
- **修正**: `{ params }: { params: { id: string } }` の直接アクセスに変更。

### Bug 5 — Tailwind カスタムカラーの参照が間違っていた ✅ 修正済み
- **ファイル**: `app/page.tsx`, `components/ProgressView.tsx`, `components/DoneView.tsx`, `components/FailedView.tsx`
- **問題**: `bg-primary-DEFAULT` / `text-primary-DEFAULT` は Tailwind v3 で生成されるクラス名ではない。`DEFAULT` キーは `-DEFAULT` サフィックスなしで `bg-primary` / `text-primary` として参照する。`accent-primary-DEFAULT` も同様に無効。
- **影響**: ボタン・リンク・ステッパーの色が全て未適用（透明/デフォルト色）になる。
- **修正**: 全箇所を `bg-primary` / `text-primary` / `accent-blue-600` に一括変換。

---

### Bug 6 — `import json` が worker.py に欠落 ✅ 修正済み
- **ファイル**: `web/backend/worker.py`
- **問題**: `clips.json` を `json.loads()` で読んでいるのに `import json` がなかった。
- **影響**: Celery Worker 起動時に `NameError: name 'json' is not defined` でクラッシュ。
- **修正**: `import json` を先頭に追加。

### Bug 7 — resend SDK v2 の `to` フィールドはリスト必須 ✅ 修正済み
- **ファイル**: `web/backend/mailer.py`
- **問題**: `requirements.txt` で `resend>=2.0.0` を指定しているのに、`"to": email`（文字列）を渡していた。resend SDK v2 では `to` は `list[str]` が必須。
- **影響**: 成功・失敗メールの送信が全て型エラーで失敗する。
- **修正**: `"to": [email]` に変更（2箇所）。

### Bug 8 — `.env` がどのエントリポイントでもロードされていない ✅ 修正済み
- **ファイル**: `main.py` / `worker.py` / `celery_app.py`
- **問題**: `python-dotenv` を依存に入れているにもかかわらず、`load_dotenv()` を呼んでいなかった。`ANTHROPIC_API_KEY` / `RESEND_API_KEY` / `DATABASE_URL` 等が全て空文字になる。
- **影響**: ローカル開発で `.env` を置いても一切の環境変数が読まれず、起動直後から全機能が壊れる。
- **修正**: 各ファイルの冒頭（他の import より前）に `load_dotenv()` を追加。

### Bug 9 — `from sqlalchemy import select` が関数内部にあった ✅ 修正済み
- **ファイル**: `worker.py` の `delete_expired_jobs_task` 関数内
- **問題**: `select` がタスク実行のたびにインポートされる。インポートエラーがタスク実行時まで検出されない。
- **修正**: `select` を `worker.py` のトップレベルインポートに移動。

## 確認済み（バグなし）

| 項目 | 結論 |
|------|------|
| `SessionLocal` のコンテキストマネージャー | SQLAlchemy 2.0 で `with SessionLocal() as db:` は正式サポート。問題なし。 |
| `pipeline_adapter.py` の関数シグネチャ | `fetch(url, work_dir, resolution)` / `transcribe(video_path, work_dir, cfg)` / `analyze(transcript, meta, cfg)` / `make_clips(video, transcript, clips, work_dir, cfg)` — 全て一致。 |
| `schemas.py` の SSRF 対策 | YouTube ドメインのみ許可する正規表現バリデーションが正しく機能する。 |
| `worker.py` の例外処理 | 全例外が `failed` ステータスに落ちて失敗メールが送信される経路を確認。 |
| ポーリング停止条件 | `isTerminal("done") === true` / `isTerminal("failed") === true` で `refetchInterval: false` が返る。正常に停止する。 |
| `import json` の欠落（worker.py） | `import json` は worker.py の先頭にある。問題なし。 |

---

## 残存リスク（修正不要・要注意）

| リスク | 内容 | 対応方針 |
|--------|------|---------|
| `pipeline.py` の `output/tmp` ディレクトリ | CLI 実行時に `output/tmp` が残る場合がある | Web サービスは一時ディレクトリを使うので無影響 |
| `clips.json` の番号マッチング | clip.py が生成するファイル名の番号形式が変わった場合にタイトル解決が失敗する | clip.py の出力形式が変わったら `worker.py` の `idx` 抽出ロジックも更新 |
| Resend の `api_key` 設定タイミング | モジュールロード時に `resend.api_key = os.environ.get(...)` を実行している。環境変数が後から設定される場合は空になる | `.env` を起動前に必ずロードする運用で回避 |
