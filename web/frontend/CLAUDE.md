# CLAUDE.md — フロントエンド実装（Next.js）

このフォルダは **youtube-kirinuki の Web フロントエンド**。あなたはここで実際にコードを書く実装担当。
（このCLAUDE.mdは `web/frontend/` 配下で自動的に文脈に入る）

> **上位の正**：API契約・ステータスenumは **`team/engineering/CLAUDE.md` §4** に従う（勝手に形を変えない）。
> 画面仕様・文言は **`team/design/CLAUDE.md`**。要件は `team/orchestrator/CLAUDE.md` §2。
> 現状：未スキャフォールド。これは実装着手時の規約。

---

## 1. スタック
- **Next.js（App Router）＋ TypeScript**（厳格な型）。
- スタイル：**Tailwind CSS ＋ shadcn/ui**（デザインと合意した標準コンポーネント）。
- データ取得/ポーリング：**TanStack Query**（`GET /api/jobs/{id}` を5秒間隔 refetch）。
- フォームバリデーション：**zod**（URL/メール/同意）。
- デプロイ：**Vercel**。

## 2. ディレクトリ構成（目安）
```
web/frontend/
├── app/
│   ├── page.tsx           ① 入力画面（トップ/LP兼用）
│   └── jobs/[id]/page.tsx ②③④ 進捗・完了・失敗（statusで出し分け）
├── components/            UI（フォーム・ステッパー・DLカード）
└── lib/
    ├── api.ts             APIクライアント（契約の型定義をここに集約）
    └── status.ts          enum → 表示文言の対応（デザインの対応表を実装）
```

## 3. API 呼び出し規約
- `lib/api.ts` に契約（§4）の **TypeScript型** を定義し、全呼び出しをこの型経由に。
- `POST /api/jobs` 成功 → `jobs/{job_id}` へ遷移。
- `jobs/{id}` は TanStack Query で5秒ポーリング。`status==="done"||"failed"` で **ポーリング停止**。
- エラー（400/429）はユーザー向け文言（デザインの文言集）に変換して表示。スタックトレースを出さない。

## 4. 画面実装の要点
- **入力画面**：同意チェックOFFは送信ボタン非活性。バリデーションエラーはフィールド直下。
- **進捗画面**：ステッパー＋「閉じてOK・メールで届く」を必ず表示。429/キュー待ちは順番待ち表示。
- **完了画面**：clipsを9:16/16:9/txtのDLカードで列挙＋「1週間で失効」明示。
- **失敗画面**：`error_message` を表示＋再試行導線。

## 5. コーディング規約
- TypeScript strict、`any`禁止（契約型で表現）。
- サーバー/クライアントコンポーネントを適切に分離。状態は最小限。
- ESLint + Prettier。コミット前に lint/format/型チェックを通す。
- 環境変数：`NEXT_PUBLIC_API_BASE` のみ公開。秘密情報をフロントに置かない。

## 6. レスポンシブ / アクセシビリティ
- **モバイルファースト**。タップ領域・コントラスト確保。フォームは適切な inputmode（email等）。

## 7. Definition of Done
- [ ] 契約型に沿って①〜④が動く（done/failedで出し分け）
- [ ] ポーリングが完了/失敗で確実に止まる
- [ ] バリデーション・エラー文言がデザイン準拠（生活者語）
- [ ] スマホ/PCで崩れない
- [ ] 型チェック・lintがパス
