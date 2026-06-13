# タスク指示書 — エンジニアリング（リード／アーキテクト）

> 発行：オーケストレーター ／ 指針：`team/engineering/CLAUDE.md` ／ 全体計画：`team/orchestrator/execution-plan.md`

## ブリーフ（依頼の要旨）

- **【背景】** フロント／バックの結合点＝**API契約**。これを早期に固めないと両側が手戻りする。pipelineラッパー化はデザイン待ち不要で先行できる。
- **【成果物】** P0：API契約確定＋データモデル＋pipelineラッパー方針。P1：技術PoC。P2：実装（FE/BE）＋E2E。P3：デプロイ。
- **【制約】** **既存 `pipeline.py`/`scripts` を壊さない（CLI維持）**。著作権チェックはしないがSSRF/入力検証は必須。小規模最適（VPS1台＋マネージド）。
- **【完了条件】** 契約どおりにE2Eが動き、既存CLIが回帰なく動作。シークレットがコードに無い。
- **【依存】** 先行：なし（API契約・ラッパー化は即着手可）。後続：FE/BE実装、マーケ料金（実コスト提供）。

---

## P0（SP1）— 一部先行着手可
- [ ] **API契約 §4 を確定**し、フロント/バック/デザインへ通知（enum固定）
- [ ] `jobs` データモデル確定（§5スキーマ）
- [ ] `pipeline_adapter` 設計（pipeline.pyを関数呼び出し化・CLIエントリ維持）※**先行着手OK**
- [ ] 1本あたり処理時間／コスト概算 → マーケへ
- 🚩 提出先：デザイン/FE/BE（契約）／統括（M1レビュー）

## P1（SP2）
- [ ] enum表示対応表をデザインと突合・最終化
- [ ] 技術PoC（緑にする）：Celery+Redis疎通／R2アップ＋7日署名URL／Resend送信
- [ ] SSRF・入力検証・レート制限の方針確定

## P2（SP3〜4）— ここで実装タスクを分割発行
- [ ] **`web/backend/TASKS.md` を発行**：FastAPI＋Celery＋pipeline統合＋R2＋メール
- [ ] **`web/frontend/TASKS.md` を発行**：画面①〜④＋API連携＋5秒ポーリング
- [ ] 統合E2E：URL→生成→R2→署名URL→DL＋成功/失敗メール
- [ ] 同時10本・キュー待ちの挙動確認

## P3（SP5）
- [ ] デプロイ：Vercel(FE)／VPS(BE: uvicorn+Celery+Redis+PostgreSQL, compose)
- [ ] 本番env・SSRF/レート制限・**期限切れR2削除ジョブ**
- [ ] 実コスト確定値 → マーケ料金設計へ

---

## Definition of Done
- §4契約どおりの両エンドポイント／status遷移がFEポーリングで追える
- R2保存・7日署名URL・成功/失敗メールが動作
- 同時10本＋キュー待ちが破綻しない／SSRF検証が効く
- **既存 `pipeline.py` がCLIとして回帰なく動く**
- シークレットがコードに含まれない
