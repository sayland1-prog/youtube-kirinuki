# DESIGN.md — kirinuki デザインシステム

## 正典原則

> **このファイルに定義されていない色・フォントサイズ・余白・角丸をCSSやTailwindクラスに直接書いてはいけない。**

- HTML/TSXはこのファイルから派生する生成物
- デザイン変更時はHTMLを直さずこのファイルを先に修正する
- コミット前にこのファイルと実装のズレを確認する
- v0.devで生成したコードも、このファイルのトークンに合わせてから取り込む

---

## ビジュアルテーマ

**ウォームミニマリズム** — 温かみのある白・クリーム系のベースに、テラコッタ赤のプライマリ1色。
装飾を排し、余白とタイポグラフィで質感を出す。

---

## カラー

### CSS変数定義（`globals.css` の `:root`）

```css
--background:       40 33% 97%;   /* クリーム白 — ページ背景 */
--foreground:       30 10% 15%;   /* 深いブラウン黒 — 本文テキスト */
--card:              0  0% 100%;  /* 純白 — カード・フォーム背景 */
--card-foreground:  30 10% 15%;   /* カード内テキスト */
--primary:          14 80% 45%;   /* テラコッタ赤 — CTA・強調・アイコンアクセント */
--primary-foreground: 0  0% 99%;  /* primaryボタン上のテキスト */
--secondary:        40 20% 94%;   /* バッジ・サブ背景 */
--secondary-foreground: 30 10% 25%;
--muted:            40 20% 94%;   /* 薄い背景 */
--muted-foreground: 30  8% 45%;   /* プレースホルダー・補足テキスト */
--border:           40 15% 88%;   /* ボーダー・区切り線 */
--input:            40 15% 88%;   /* 入力欄ボーダー */
--ring:             14 80% 45%;   /* フォーカスリング */
--radius:           0.625rem;     /* 角丸基準値（10px）*/
```

### 状態カラー（Tailwindデフォルト色を使用）

| 用途     | テキスト        | 背景         | ボーダー          |
|---------|---------------|-------------|-----------------|
| エラー   | `text-red-600` | `bg-red-50` | `border-red-200` |
| 成功     | `text-green-600` | `bg-green-50` | `border-green-200` |
| 処理中   | `text-blue-600` | `bg-blue-50` | `border-blue-200` |

### 使い分けルール

- `primary` → CTAボタン、リンク、アクティブ状態、アイコンアクセント
- `secondary` → バッジ、チェックボックスエリア背景、補足UI
- `muted-foreground` → プレースホルダー、注釈、ラベル以外の説明文

---

## タイポグラフィ

### フォントスタック

```
Hiragino Kaku Gothic ProN, Hiragino Sans, Yu Gothic Medium, Meiryo, Noto Sans JP, sans-serif
```

日本語優先。macOS / Windows / Android でシステムフォントにフォールバック。

### スケール（このスケール以外の `text-*` を使わない）

| 用途                  | Tailwindクラス                       |
|-----------------------|-------------------------------------|
| ページタイトル（h1）   | `text-4xl font-bold sm:text-5xl`    |
| セクション見出し       | `text-lg font-semibold`             |
| ボタンラベル          | `text-base font-semibold`           |
| フォームラベル         | `text-sm font-medium`               |
| 本文・説明            | `text-base leading-relaxed`         |
| 補足・注釈・フッター   | `text-sm text-muted-foreground`     |
| バッジ                | `text-xs font-medium`               |

### コピールール

- フレンドリーで短い。マイクロコピーで不安を先回りして消す
- ボタンは「動詞＋結果」（例：「切り抜きを作る」）
- 専門用語禁止（「文字起こし」→ 表示では「準備中」等に翻訳）

---

## スペーシング

このスケール以外の `p-*` / `m-*` / `gap-*` を自由に使わない。

| 用途                     | クラス              |
|--------------------------|-------------------|
| ページ横パディング         | `px-6`            |
| フォームカード内パディング  | `p-6 sm:p-8`      |
| フォームフィールド間        | `gap-5`           |
| ヒーロー → フォームカード   | `mt-10 sm:mt-12`  |
| カード下フッター           | `mt-6`            |
| バッジ内                  | `px-3 py-1.5`     |
| 同意エリア内              | `p-4`             |

---

## 角丸

`--radius: 0.625rem` を基準に倍率管理。この表以外の `rounded-*` を使わない。

| クラス         | 値                              | 用途                  |
|---------------|---------------------------------|-----------------------|
| `rounded-lg`  | `0.5rem`（Tailwindデフォルト）   | 小さいUI要素           |
| `rounded-xl`  | `calc(var(--radius) * 1.4)`     | 入力欄・ボタン         |
| `rounded-2xl` | `calc(var(--radius) * 1.8)`     | フォームカード         |
| `rounded-full`| `9999px`                        | バッジ・ピル形状       |

---

## コンポーネント仕様

### 入力欄（Input）

```
w-full rounded-xl border bg-background
py-3 pl-11 pr-4
text-base text-foreground placeholder:text-muted-foreground
transition focus:outline-none focus:ring-4 focus:ring-primary/15
border-border focus:border-primary
```

エラー時：`border-red-500 focus:border-red-500 focus:ring-red-500/15`

左端アイコン：`absolute left-3.5 top-1/2 -translate-y-1/2 size-5 text-muted-foreground`

### CTAボタン（Primary）

```
inline-flex items-center justify-center gap-2
rounded-xl bg-primary px-6 py-3.5
text-base font-semibold text-primary-foreground shadow-sm
transition hover:opacity-90
focus:outline-none focus:ring-4 focus:ring-primary/30
disabled:cursor-not-allowed disabled:opacity-40
```

右端 `<ArrowRight size={20} />`、hover で `translate-x-0.5`。

### フォームカード

```
rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8
```

### バッジ（ピル）

```
inline-flex items-center gap-1.5
rounded-full bg-secondary px-3 py-1.5
text-xs font-medium text-secondary-foreground
```

アイコン付き：`<Icon className="size-4 text-primary" />`

### 同意チェックボックスエリア

```
flex cursor-pointer items-start gap-3
rounded-xl bg-secondary/60 p-4
text-sm leading-relaxed text-muted-foreground
```

チェックボックス：`size-5 rounded accent-primary`

### エラーメッセージ（フィールド直下）

```
text-red-600 text-sm
```

### エラーバナー（サーバーエラー）

```
rounded-xl bg-red-50 border border-red-200 p-4 text-red-800 text-sm
```

---

## アイコン

ライブラリ：**lucide-react** のみ使用。

| 用途              | アイコン名       | サイズ   |
|------------------|----------------|---------|
| ブランドロゴ      | `Scissors`     | `size-4`（ヘッダー内 `size-8` ボックス）|
| URLフィールド     | `Link`         | `size-5`|
| メールフィールド  | `Mail`         | `size-5`|
| 文字起こしバッジ  | `FileText`     | `size-4`|
| 選定バッジ        | `Scissors`     | `size-4`|
| 字幕バッジ        | `Captions`     | `size-4`|
| 投稿文バッジ      | `Send`         | `size-4`|
| ボタン矢印        | `ArrowRight`   | `size-5`|

---

## 画面別デザイン要件

### ① 入力画面（実装済み）

構成順：ヘッダー → バッジ → h1 → サブテキスト → 機能バッジ列 → フォームカード → フッター

- h1 の「30分」を `text-primary` で強調
- 機能バッジは `flex flex-wrap list-none gap-2`

### ② 進捗画面

- ステッパー文言：「動画取得中」→「文字起こし中」→「選定中」→「加工中」→「完成」
- アクティブ：`text-primary`、完了：`text-green-600`、未着手：`text-muted-foreground`
- **安心メッセージ（必須）**：同意エリアと同スタイル（`bg-secondary/60 rounded-xl p-4`）で常時表示
  - 文言：「このページを閉じても大丈夫。完成したらメールでお知らせします」
- アニメーション：`animate-pulse`

### ③ 完了画面

- クリップカード：`rounded-2xl border border-border bg-card p-4 shadow-sm`
- DLボタン：9:16 / 16:9 / txt の3種を横並び
- 有効期限：`text-sm text-muted-foreground`「このリンクは1週間で消えます」
- 「もう一本作る」→ CTAボタンスタイルで `/` へ

### ④ 失敗画面

- エラーバナースタイルでエラー内容を表示
- 再試行ボタン：CTAボタンスタイル
- 技術スタックトレース禁止。生活者語のみ

---

## 変更フロー

1. デザイン変更の必要が生じたら、**まずこのファイルを修正する**
2. `globals.css` / `tailwind.config.ts` をこのファイルに合わせて更新する
3. コンポーネントを更新する
4. `CHANGELOG.md` に記録する
