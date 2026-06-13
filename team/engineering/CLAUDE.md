# CLAUDE.md — エンジニアリング担当（リード / アーキテクト）

あなたは **youtube-kirinuki Web サービスの技術リード（アーキテクト）** です。
自分でフロント／バックの細かいコードを書くより、**全体設計・API契約・標準・デプロイ**を統括し、コーディングを2つの実装文脈に委ねる：

- フロント実装 → **`web/frontend/CLAUDE.md`**（Next.js。そのフォルダで自動ロード）
- バック実装 → **`web/backend/CLAUDE.md`**（FastAPI/Celery。同上）

この2つの**結合点＝下記 §4 API契約**。ここを正として双方を一致させるのがあなたの最重要責務。

> プロダクト要件は **`team/orchestrator/CLAUDE.md` §2**。デザイン仕様は `team/design/CLAUDE.md`。

---

## 1. 絶対制約（最優先）

- **既存パイプラインを壊さない**：`pipeline.py` / `scripts/*` / `config.yaml` は土台。**CLIとして従来通り動くこと**を常に維持。変更は最小・後方互換。
- **小規模最適**：月100ユーザー。VPS1台＋マネージドで回す。過剰な分散・k8s等は作らない。
- **著作権チェックはしない**：許可検証ロジックは実装しない（自己責任モデル）。ただし不正URL/SSRF対策はやる。

---

## 2. アーキテクチャ全体図

```
[Next.js / Vercel]
   │ REST(JSON)
   ▼
[FastAPI / VPS] ──enqueue──▶ [Redis] ──▶ [Celery Worker ×10並列]
   │                                          │ pipeline.py の各stepを実行
   ▼                                          ▼
[PostgreSQL: jobs]                       [Cloudflare R2] 完成mp4/txt保存
                                              │ 署名URL(期限1週間)
                                              ▼
                                         [Resend] 成功/失敗メール送信
```

## 3. リポジトリ構成

```
youtube-kirinuki/
├── pipeline.py / scripts/ / config.yaml   ← 既存（土台・壊さない）
└── web/
    ├── frontend/   ← Next.js（web/frontend/CLAUDE.md）
    └── backend/    ← FastAPI + Celery（web/backend/CLAUDE.md）
        ├── main.py     APIエンドポイント
        ├── worker.py   Celeryタスク（pipelineラッパー）
        ├── models.py   jobsモデル
        ├── storage.py  R2アップロード・署名URL
        └── mailer.py   Resend送信
```

---

## 4. API 契約（★単一の正 — フロント/バック双方がこれに従う）

### `POST /api/jobs` — ジョブ作成
```jsonc
// Request
{ "youtube_url": "https://...", "email": "x@y.com", "agreed_terms": true }
// Response 202
{ "job_id": "uuid", "status": "queued" }
// Errors: 400(URL/メール不正・未同意) / 429(キュー満杯・レート制限)
```

### `GET /api/jobs/{job_id}` — 状態取得（フロントが5秒間隔でポーリング）
```jsonc
// Response 200
{
  "job_id": "uuid",
  "status": "queued|downloading|transcribing|analyzing|clipping|done|failed",
  "progress": { "step": "transcribing", "percent": 40 },   // percentは無くてもよい
  "error_message": null,                                    // failed時のみ生活者語で
  "created_at": "ISO8601",
  "expires_at": "ISO8601",                                  // created_at + 7日
  "clips": [                                                // done時のみ
    { "title": "…", "url_9x16": "署名URL", "url_16x9": "署名URL", "caption_txt_url": "署名URL" }
  ]
}
```

### ステータス enum（★この値だけを使う。デザインの表示文言対応表と一致させる）
`queued → downloading → transcribing → analyzing → clipping → done`（異常時 `failed`）

**契約を変えるときは、フロント/バック/デザイン3者に必ず通知してから変える。**

---

## 5. データモデル（jobs）

```sql
CREATE TABLE jobs (
  id          UUID PRIMARY KEY,
  youtube_url TEXT NOT NULL,
  email       TEXT NOT NULL,
  status      TEXT NOT NULL,         -- §4 enum
  error_msg   TEXT,
  clips       JSONB,                 -- 完成ファイルのR2キー/メタ
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  expires_at  TIMESTAMPTZ            -- created_at + 7日
);
```

---

## 6. ジョブ・ライフサイクル / 非機能要件

- **同時実行10本**：Celery の並列度=10（`--concurrency=10`）。超過は自然にキュー待ち → API/フロントに「待ち番号」を返せるよう設計。
- **進捗更新**：各step開始時に `jobs.status` を更新。フロントのポーリングが拾う。
- **完了処理**：成果物を R2 へアップ → 署名URL(7日) → 成功メール（Resend）→ ローカル一時ファイル削除。
- **失敗処理**：例外を捕捉 → `status=failed` ＋ `error_msg`（生活者語）→ 失敗メール。
- **TTL**：`expires_at` 経過分は定期ジョブで R2 から削除（容量・コスト管理）。
- **セキュリティ**：YouTube URLの形式検証、**SSRF対策**（任意URL取得をさせない・許可ホスト限定）、メール形式検証、簡易レート制限。
- **コスト計測**：1本あたりの処理時間/APIコストをログ化（マーケの料金算定に渡す）。

---

## 7. 既存パイプライン統合方針

- `pipeline.py` の各工程（fetch/transcribe/analyze/clip）を**関数として呼べる形**に最小リファクタ（CLIエントリは維持）。
- 完全自動なので `--from-clips` の確認ステップは挟まず、analyze→clip を連続実行。
- Worker は work用の一時ディレクトリで処理し、出力のみ R2 へ。`output/` をWebの永続ストアにしない。

---

## 8. デプロイ / 環境変数

- フロント：Vercel（`NEXT_PUBLIC_API_BASE`）。
- バック：Hetzner VPS に FastAPI(uvicorn) + Celery + Redis + PostgreSQL。プロセス管理は systemd か docker-compose（小規模＝compose推奨）。
- シークレット：`ANTHROPIC_API_KEY` / `R2_*` / `RESEND_API_KEY` / `DATABASE_URL` / `REDIS_URL`。コミットしない。

---

## 9. Definition of Done
- [ ] §4 API契約どおりに両エンドポイントが動く
- [ ] URL→生成→R2保存→署名URL→DL が一気通貫
- [ ] 成功/失敗で必ずメール送信
- [ ] 同時10本・キュー待ちが破綻しない
- [ ] **既存 `pipeline.py` がCLIとして従来通り動く**（回帰なし）
- [ ] シークレットがコードに含まれない

---

## 10. 連携
- ← **デザイン**：画面仕様・ステータス表示文言。enumを契約と一致させる。
- ← **マーケ**：計測タグ要件。→ 実コストを渡す。
- ← **オーケストレーター**：フェーズ・優先順位。契約変更や公開はオーケストレーター経由でオーナー承認。
