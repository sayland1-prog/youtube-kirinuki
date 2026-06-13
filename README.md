# YouTube 切り抜き自動化パイプライン

YouTube 動画を **取得 → 文字起こし → ハイライト選定 → 切り抜き加工** まで自動化する。
Claude Code をハブに、yt-dlp / Whisper / Claude / ffmpeg を順に駆動する構成。

```
URL ──▶ yt-dlp ──▶ Whisper ──▶ Claude ──▶ ffmpeg ──▶ 縦横クリップ + 投稿文
       (取得)     (文字起こし)  (選定/命名)  (切り抜き/字幕焼込)
```

判断が要る「ハイライト選定・タイトル生成」だけが Claude の仕事で、
残りは決定論的なツールが処理する。

## 必要なもの

| ツール | 用途 | 導入 |
|---|---|---|
| Python 3.10+ | 実行環境 | — |
| ffmpeg | 切り抜き・字幕焼込 | `brew install ffmpeg` |
| yt-dlp | 動画取得 | requirements に同梱 |
| faster-whisper | 文字起こし | requirements に同梱 |
| Anthropic API キー | ハイライト選定 | 環境変数で設定 |

> GPU があると文字起こしが大幅に高速。なくても `int8` で CPU 実行できる。

## セットアップ

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
# OpenAI Whisper API を使う場合のみ:
# export OPENAI_API_KEY="sk-..."
```

初回は faster-whisper のモデル（large-v3 で約3GB）が自動ダウンロードされる。

## 使い方

### A. 段階確認しながら（推奨）
```bash
# 1. 選定まで実行（候補を確認）
python pipeline.py "https://www.youtube.com/watch?v=XXXX" --until analyze

# 2. output/XXXX/clips.json を確認・編集（start/end やタイトルを調整）

# 3. 承認後に切り抜き
python pipeline.py "https://www.youtube.com/watch?v=XXXX" --from-clips output/XXXX/clips.json
```

### B. 一気に最後まで
```bash
python pipeline.py "https://www.youtube.com/watch?v=XXXX"
```

### C. Claude Code から
プロジェクトを開いて「このURL切り抜いて → <URL>」と話しかければ、
`CLAUDE.md` の手順に沿って段階確認しながら進む。

## 出力（`output/<動画ID>/clips/`）
- `01_タイトル_9x16.mp4` … ショート用（縦・字幕焼込）
- `01_タイトル_16x9.mp4` … 通常クリップ（横・字幕焼込）
- `01_タイトル.txt` … タイトル / 概要 / ハッシュタグ

## カスタマイズ（config.yaml）
クリップ数・尺、字幕フォント/サイズ、縦型レイアウト（blur/crop）、選定モデルを変更可能。

## 注意（重要）
- **切り抜き許可のある動画のみを対象にすること。** 配信者のガイドライン（クレジット表記等）に従う。
- yt-dlp は YouTube 仕様変更で動かなくなることがある。失敗したら `pip install -U yt-dlp` で最新化。

## 拡張アイデア
- 工程5として YouTube Data API での自動アップロードを追加
- word単位タイムスタンプを使ったカラオケ字幕（1語ずつハイライト）
- 複数URLをキューに入れてバッチ処理
