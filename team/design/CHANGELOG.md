# デザイン変更履歴

## 2026-06-14 — 入力画面UIをv0.devデザインに刷新

### 変更内容
- ヒーローセクションを全面リデザイン（「30分」を primary カラーでアクセント）
- 機能バッジ（文字起こし・選定・字幕・投稿文）をアイコン付きピル形式で追加
- フォームカードに `bg-card / rounded-2xl / shadow-sm` で視覚的まとまりを付与
- 入力欄に lucide-react アイコン（Link・Mail）を左端に配置
- 送信ボタンを `ArrowRight` アイコン付きに変更、hover でスライドアニメーション
- 利用規約同意欄を `bg-secondary/60` の背景付きエリアに変更
- ヘッダーをシザーズアイコン付きコンパクトヘッダーに変更

### デザインソース
- `team/design/url-to-short-clip.zip`（v0.devで生成）
- プレビュー画像：`shot.png`（デスクトップ）/ `mobile.png`（モバイル）

### デザイントークン変更
- プライマリカラー：`#2563EB`（青）→ `oklch(0.62 0.2 25)`（テラコッタ赤）
- CSS変数を `globals.css` に追加（`--background`, `--foreground`, `--card`, `--primary` 等）
- Tailwind config に CSS変数ベースのカラー定義を追加

### ロジック維持
- zod バリデーション、react-hook-form、API連携はすべて既存のまま維持
