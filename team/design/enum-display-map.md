# ステータス Enum → 表示文言 対応表

> エンジニアとデザインの契約。この表の値のみを使う。
> 変更時はENG（API契約）とDesign両方を同時に更新すること。

---

## 対応表

| enum値 | ステッパー表示 | 説明文（進捗画面） | 推定残り時間 | アイコン |
|--------|--------------|-----------------|------------|---------|
| `queued` | 順番待ち中 | 現在混み合っています。もう少々お待ちください。 | — | 🕐 |
| `downloading` | 動画を準備中 | 動画データを取得しています... | 約1〜3分 | 📥 |
| `transcribing` | 音声を解析中 | 音声からテキストを生成しています... | 約5〜10分 | 🎙️ |
| `analyzing` | 見どころを選定中 | AIが盛り上がった場面を選んでいます... | 約2〜5分 | 🤖 |
| `clipping` | 動画を加工中 | 縦型・横型の動画と投稿文を生成しています... | 約5〜10分 | ✂️ |
| `done` | 完成！ | 切り抜き動画ができました。ダウンロードしてください。 | — | ✅ |
| `failed` | 処理に失敗 | 処理中にエラーが発生しました。 | — | ❌ |

---

## ステッパーの表示ルール

```
queued      → ステッパー外（別途「順番待ち」バナーで表示）
downloading → step 1 / 4（●アニメーション）
transcribing → step 2 / 4
analyzing   → step 3 / 4
clipping    → step 4 / 4
done        → 全ステップ ✓（完了画面に切り替え）
failed      → 失敗したstepを ✗ 表示（失敗画面に切り替え）
```

**ステッパーに表示する4ステップ（queuedを除く）**：
1. 動画を準備中
2. 音声を解析中
3. 見どころを選定中
4. 動画を加工中

---

## 実装ノート（ENG向け）

```typescript
// lib/status.ts に実装する
export const STATUS_LABEL: Record<JobStatus, string> = {
  queued:       '順番待ち中',
  downloading:  '動画を準備中',
  transcribing: '音声を解析中',
  analyzing:    '見どころを選定中',
  clipping:     '動画を加工中',
  done:         '完成！',
  failed:       '処理に失敗',
}

export const STATUS_DESCRIPTION: Record<JobStatus, string> = {
  queued:       '現在混み合っています。もう少々お待ちください。',
  downloading:  '動画データを取得しています...',
  transcribing: '音声からテキストを生成しています...',
  analyzing:    'AIが盛り上がった場面を選んでいます...',
  clipping:     '縦型・横型の動画と投稿文を生成しています...',
  done:         '切り抜き動画ができました。ダウンロードしてください。',
  failed:       '処理中にエラーが発生しました。',
}
```
