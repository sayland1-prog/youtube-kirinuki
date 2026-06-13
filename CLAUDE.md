# CLAUDE.md — 切り抜き自動化の運用ガイド

このプロジェクトは YouTube 動画から切り抜きショートを自動生成する。
ユーザーが URL を渡して「切り抜いて」と言ったら、以下の手順で進めること。

## 大前提（必ず守る）
- **対象は「切り抜き許可のある配信者」の動画のみ**。URL を受け取ったら、許可済みか一言確認する。
- 配信者が定める切り抜きガイドライン（クレジット表記・収益化条件など）があれば従う。

## 推奨ワークフロー（段階確認つき）
ユーザーは各段階での確認を好むため、一気に最後まで走らせず以下で進める。

1. **選定まで実行**
   ```
   python pipeline.py "<URL>" --until analyze
   ```
   → `output/<動画ID>/clips.json` に候補が出る。

2. **候補をユーザーに提示**
   `clips.json` を読み、各クリップの `title` / 区間 / `reason` を一覧で見せ、
   「この5本で切り抜きますか？ 差し替え・尺調整あれば言ってください」と確認する。

3. **必要なら clips.json を直接編集**
   start/end の微調整、タイトル書き換え、不要クリップの削除はファイルを編集すればよい。

4. **承認後に切り抜き加工**
   ```
   python pipeline.py "<URL>" --from-clips output/<動画ID>/clips.json
   ```
   → `output/<動画ID>/clips/` に `*_9x16.mp4`（縦）/ `*_16x9.mp4`（横）/ `*.txt`（投稿文）が出る。

## 出力物
- `*_9x16.mp4` … ショート用（字幕焼き込み・ぼかし背景フィット）
- `*_16x9.mp4` … 通常クリップ（字幕焼き込み）
- `*.txt` … タイトル / 概要 / ハッシュタグ（投稿時にコピペ）

## 設定変更（config.yaml）
- クリップ数・尺: `analyze.num_clips / min_seconds / max_seconds`
- 字幕フォント・サイズ: `subtitle.*`（フォントは環境に存在する日本語フォント名にする）
- 縦型レイアウト: `clip.vertical_layout`（`blur`=左右切らない / `crop`=被写体大きく）
- 選定モデル: `analyze.model`（判断重視なら `claude-opus-4-8`）

## トラブル時
- yt-dlp が失敗 → まず `pip install -U yt-dlp` で最新化（YouTube仕様変更に追従が必要）。
- 字幕の日本語が豆腐（□）になる → `subtitle.font` を環境にあるフォントへ変更。
- 文字起こしが遅い → GPUなしなら `config.yaml` の `transcribe.model` を `medium` に下げる。
