# デザイントークン — youtube-kirinuki

> Tailwind CSS の設定値として使用。shadcn/ui のデフォルトを上書きする部分のみ定義。

---

## カラーパレット

```typescript
// tailwind.config.ts に追加
colors: {
  primary: {
    DEFAULT: '#2563EB', // blue-600: CTAボタン・リンク・アクティブ状態
    hover:   '#1D4ED8', // blue-700
    light:   '#EFF6FF', // blue-50: 安心メッセージ背景等
  },
  success: {
    DEFAULT: '#16A34A', // green-600: 完了状態・チェックマーク
    light:   '#F0FDF4', // green-50
  },
  error: {
    DEFAULT: '#DC2626', // red-600: エラー状態・失敗
    light:   '#FEF2F2', // red-50: エラー背景
  },
  warning: {
    DEFAULT: '#D97706', // amber-600: 注意（有効期限等）
    light:   '#FFFBEB', // amber-50
  },
  queue: {
    DEFAULT: '#6B7280', // gray-500: 待機状態
    light:   '#F9FAFB', // gray-50
  },
}
```

---

## タイポグラフィ（日本語最適化）

```typescript
// tailwind.config.ts に追加
fontFamily: {
  sans: [
    'Hiragino Kaku Gothic ProN', // macOS
    'Hiragino Sans',
    'Yu Gothic Medium',           // Windows
    'Meiryo',
    'Noto Sans JP',               // Web fallback
    'sans-serif',
  ],
},
```

### テキストスケール

| 用途 | クラス | サイズ | 行間 | 備考 |
|------|--------|--------|------|------|
| ページH1 | `text-3xl font-bold` | 30px | 1.4 | ヒーローキャッチコピー |
| セクション見出し | `text-xl font-semibold` | 20px | 1.5 | |
| カード見出し | `text-lg font-medium` | 18px | 1.5 | クリップタイトル等 |
| 本文 | `text-base` | 16px | 1.75 | 説明文。日本語は行間広めに |
| 補足・ラベル | `text-sm` | 14px | 1.5 | フィールドラベル等 |
| マイクロコピー | `text-xs` | 12px | 1.4 | 有効期限・注意書き |

---

## スペーシングスケール

Tailwindデフォルトを使用。主要な値：
- コンポーネント間: `gap-4`（16px）/ `gap-6`（24px）
- カードパディング: `p-5`（20px）/ `p-6`（24px）
- ページ左右マージン: `px-4`（16px、モバイル）/ `px-6`（24px、タブレット以上）
- 最大幅: `max-w-xl mx-auto`（640px）

---

## コンポーネント仕様

### ボタン

| 種類 | Tailwindクラス（主要部分） | 状態 |
|------|------------------------|------|
| プライマリCTA | `bg-primary text-white rounded-lg py-3 px-6 font-medium w-full` | disabled: `opacity-50 cursor-not-allowed` / loading: スピナー付き |
| セカンダリ | `border border-gray-300 bg-white text-gray-700 rounded-lg py-3 px-6` | hover: `bg-gray-50` |
| テキストリンク | `text-primary underline` | — |

### テキスト入力

```
border border-gray-300 rounded-lg px-4 py-3 w-full
focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
error: border-error focus:ring-error
```

### チェックボックス

```
accent-primary w-4 h-4  // ネイティブcheckbox with accent-color
```
ラベルはクリック可能領域を広くする（`<label>` でwrap）。

### ステッパー

```
● アクティブ: bg-primary text-white animate-pulse
✓ 完了: bg-success text-white
○ 未来: bg-gray-200 text-gray-400
│ 縦線（コネクタ）: border-l-2 border-gray-200（未来）/ border-success（完了）
```

### 安心メッセージバナー

```
bg-blue-50 border border-blue-200 rounded-lg p-4
text-blue-800 text-sm
```

### エラーバナー（フォーム上部）

```
bg-red-50 border border-red-200 rounded-lg p-4 mb-4
text-red-800 text-sm
```
