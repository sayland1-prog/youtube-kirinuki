# CLAUDE.md — バックエンド実装（FastAPI / Celery）

このフォルダは **youtube-kirinuki の Web バックエンド**。あなたはここで実際にコードを書く実装担当。
（このCLAUDE.mdは `web/backend/` 配下で自動的に文脈に入る）

> **上位の正**：API契約・データモデル・非機能要件は **`team/engineering/CLAUDE.md` §4〜§8** に従う。
> 要件は `team/orchestrator/CLAUDE.md` §2。
> 現状：未スキャフォールド。これは実装着手時の規約。

---

## 1. 絶対ルール
- **既存 `../../pipeline.py` / `../../scripts/*` を壊さない**。CLIとして従来通り動くことを維持。呼び出しは後方互換のラッパー経由。
- **著作権チェックは実装しない**（自己責任モデル）。ただし **URL検証・SSRF対策は必須**。

## 2. スタック
- **FastAPI**（uvicorn）— API層。リクエスト/レスポンスは **Pydantic** で契約(§4)に厳密一致。
- **Celery + Redis** — 非同期ジョブ。`--concurrency=10`。
- **SQLAlchemy + PostgreSQL** — `jobs` テーブル（契約§5のスキーマ）。
- **boto3（S3互換）** — Cloudflare R2 アップロード・署名URL（期限7日）。
- **Resend** — 成功/失敗メール。

## 3. ディレクトリ構成
```
web/backend/
├── main.py     FastAPI: POST /api/jobs, GET /api/jobs/{id}
├── worker.py   Celeryタスク（pipelineを順次実行・status更新）
├── models.py   SQLAlchemy: Job
├── schemas.py  Pydantic: 契約の入出力型
├── storage.py  R2アップロード・署名URL生成
├── mailer.py   Resend送信（成功/失敗テンプレ）
└── pipeline_adapter.py  既存pipeline.pyを関数として呼ぶ薄いラッパー
```

## 4. エンドポイント実装
- `POST /api/jobs`：URL形式＋SSRF許可ホスト検証、メール検証、`agreed_terms`必須。OKなら Job作成(status=queued)→Celery enqueue→202返す。満杯/レート超過は429。
- `GET /api/jobs/{id}`：Jobを契約(§4)のJSONで返す。`done`時のみ `clips`（署名URL）を含める。

## 5. Celery タスク設計（worker.py）
処理順に `jobs.status` を更新しながら進める：
```
queued → downloading → transcribing → analyzing → clipping → done
```
- 各stepは `pipeline_adapter` 経由で既存処理を呼ぶ。**完全自動**（`--from-clips`の確認は挟まない）。
- 作業は一時ディレクトリ。完了したら成果物(9:16/16:9/txt)を **R2へアップ→署名URL→clipsに保存→成功メール→一時削除**。
- 例外は捕捉して `status=failed` ＋ `error_msg`（**生活者語**。内部例外は別途ログ）→ 失敗メール。
- リトライ方針：一時的失敗（DL失敗等）は限定回数リトライ可。確定的失敗は即failed。

## 6. パイプライン統合（pipeline_adapter.py）
- `pipeline.py` の fetch/transcribe/analyze/clip を**関数として呼べる形**に最小リファクタ（CLIエントリ `__main__` は維持）。
- 出力は一時dirに限定し、`output/` をWeb永続ストアにしない。

## 7. セキュリティ / 非機能
- **SSRF**：取得対象を YouTube ドメインに限定。内部IP/任意URLを弾く。
- メール形式検証、簡易レート制限（IP/メール単位）。
- シークレットは環境変数：`ANTHROPIC_API_KEY` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET` / `R2_ENDPOINT` / `RESEND_API_KEY` / `DATABASE_URL` / `REDIS_URL`。
- **期限切れ削除**：`expires_at` 超過のR2オブジェクトを定期タスクで削除。
- 1本あたり処理時間/コストをログ化（料金算定用）。

## 8. Definition of Done
- [ ] 契約(§4)どおりのI/O（Pydanticで保証）
- [ ] queued→…→done のstatus遷移がフロントのポーリングで追える
- [ ] R2保存・7日署名URL・成功/失敗メールが動く
- [ ] 同時10本・キュー待ちが破綻しない
- [ ] SSRF/入力検証が効いている
- [ ] **既存pipeline.pyがCLIとして回帰なく動く**
- [ ] シークレットがコードに無い
