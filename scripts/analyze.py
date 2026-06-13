"""
工程3: ハイライト抽出（このパイプラインの頭脳）
文字起こしを Claude に渡し、切り抜きに向く区間を start/end で選定させ、
タイトル・概要・ハッシュタグまで生成させる。
"""
import json
import os
from pathlib import Path
from anthropic import Anthropic


def analyze(transcript: list, meta: dict, cfg: dict) -> list:
    """クリップ候補のリストを返す。"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY が設定されていません。\n"
            "  `export ANTHROPIC_API_KEY='sk-ant-...'` を実行してください。"
        )

    client = Anthropic()

    lines = [f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in transcript]
    transcript_text = "\n".join(lines)
    duration = meta.get("duration") or (transcript[-1]["end"] if transcript else 0)

    num = cfg.get("num_clips", 5)
    lo = cfg.get("min_seconds", 15)
    hi = cfg.get("max_seconds", 60)

    prompt = f"""あなたは切り抜き動画編集のプロです。以下の動画から、ショート動画として伸びる/価値が高い区間を選びます。

# 動画情報
タイトル: {meta.get('title')}
配信者: {meta.get('uploader')}
総尺: 約 {duration:.0f} 秒

# 文字起こし（[開始秒-終了秒] テキスト）
{transcript_text}

# 指示
- 上記から、切り抜きに向く区間を {num} 個選んでください。
- 各区間は {lo}〜{hi} 秒。話の途中で切れないよう、自然な区切りで start/end を取ること。
- 冒頭に強い引き（フック）がある／結論や感情の山場が含まれる区間を優先。
- 区間どうしは重複させない。end は総尺（{duration:.0f}秒）を超えない。
- タイトルは続きが見たくなる引きのある日本語、30字以内。

# 出力（JSON配列のみ。前置き・説明・コードフェンス禁止）
[{{"start": 開始秒(数値), "end": 終了秒(数値), "title": "タイトル", "caption": "概要欄テキスト2〜3文", "hashtags": ["#タグ1","#タグ2","#タグ3"], "reason": "選定理由(編集者向け)"}}]"""

    model = cfg.get("model", "claude-sonnet-4-6")
    print(f"  → Claude ({model}) でハイライト選定中...")

    clips = _call_with_retry(client, model, prompt, max_retries=2)

    # バリデーション
    valid = [c for c in clips if c["end"] > c["start"] and (c["end"] - c["start"]) >= 1]
    print(f"  ✓ {len(valid)} 個のクリップ候補を選定")
    for i, c in enumerate(valid, 1):
        print(f"    [{i}] {c['start']:.0f}-{c['end']:.0f}s  {c['title']}")
    return valid


def _call_with_retry(client, model: str, prompt: str, max_retries: int = 2) -> list:
    """APIを呼び出し、JSONパースを最大 max_retries 回リトライする。"""
    last_error = None
    last_text = ""
    for attempt in range(1, max_retries + 2):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            last_text = text
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_error = e
            if attempt <= max_retries:
                print(f"  ⚠ JSONパース失敗（試行 {attempt}/{max_retries + 1}）。リトライ中...")
            continue
        except Exception as e:
            raise RuntimeError(f"Claude API の呼び出しに失敗しました: {e}") from e

    # すべてのリトライが失敗した場合
    dump_path = Path("output") / "analyze_raw_output.txt"
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    dump_path.write_text(last_text, encoding="utf-8")
    raise RuntimeError(
        f"Claude の応答を JSON として解析できませんでした（{max_retries + 1}回試行）。\n"
        f"  生レスポンスを {dump_path} に保存しました。内容を確認してください。\n"
        f"  最後のエラー: {last_error}"
    )


if __name__ == "__main__":
    import yaml
    cfg = yaml.safe_load(Path("config.yaml").read_text())["analyze"]
    work = Path("output/manual")
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    meta = json.loads((work / "source.info.json").read_text(encoding="utf-8"))
    clips = analyze(transcript, meta, cfg)
    (work / "clips.json").write_text(json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8")
