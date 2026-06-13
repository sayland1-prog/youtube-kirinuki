"""
工程2: 文字起こし
Whisper で動画の音声をタイムスタンプ付きで書き起こす。
"""
import json
import os
from pathlib import Path


def transcribe(video_path: str, work_dir: Path, cfg: dict) -> list:
    """文字起こし結果（segment配列）を返し、transcript.json に保存する。"""
    engine = cfg.get("engine", "faster-whisper")
    if engine == "openai-api":
        result = _openai_api(video_path, cfg)
    else:
        result = _faster_whisper(video_path, cfg)

    out = work_dir / "transcript.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ 文字起こし完了: {len(result)} セグメント → {out.name}")
    return result


def _faster_whisper(video_path: str, cfg: dict) -> list:
    """ローカルの faster-whisper を使用（推奨）。"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise EnvironmentError(
            "faster-whisper がインストールされていません。\n"
            "  `pip install faster-whisper` を実行してください。"
        )

    device = cfg.get("device", "auto")
    compute = cfg.get("compute_type", "auto")
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"
    if compute == "auto":
        compute = "float16" if device == "cuda" else "int8"

    model_name = cfg.get("model", "large-v3")
    print(f"  → faster-whisper ({model_name}, {device}/{compute}) で書き起こし中...")
    print(f"     ※ 初回はモデル（{model_name}）のダウンロードが発生します（数分かかる場合があります）")

    try:
        model = WhisperModel(model_name, device=device, compute_type=compute)
    except Exception as e:
        raise RuntimeError(
            f"Whisper モデルの読み込みに失敗しました: {e}\n"
            "  ・ディスク空き容量を確認してください（large-v3 は約3GB必要です）。\n"
            "  ・GPUエラーの場合は config.yaml の device を `cpu` に変更してください。"
        ) from e

    try:
        segments, _ = model.transcribe(
            video_path,
            language=cfg.get("language", "ja"),
            word_timestamps=True,
            vad_filter=True,
        )
        result = []
        for seg in segments:
            words = [
                {"start": w.start, "end": w.end, "word": w.word}
                for w in (seg.words or [])
            ]
            result.append(
                {"start": seg.start, "end": seg.end, "text": seg.text.strip(), "words": words}
            )
    except Exception as e:
        raise RuntimeError(f"文字起こし中にエラーが発生しました: {e}") from e

    return result


def _openai_api(video_path: str, cfg: dict) -> list:
    """OpenAI Whisper API を使用（GPU不要・従量課金）。"""
    try:
        from openai import OpenAI
    except ImportError:
        raise EnvironmentError(
            "openai パッケージがインストールされていません。\n"
            "  `pip install openai` を実行してください。"
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY が設定されていません。\n"
            "  `export OPENAI_API_KEY='sk-...'` を実行してください。"
        )

    print("  → OpenAI Whisper API で書き起こし中...")
    client = OpenAI()
    try:
        with open(video_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=cfg.get("language", "ja"),
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
            )
    except Exception as e:
        raise RuntimeError(f"OpenAI API の呼び出しに失敗しました: {e}") from e

    words = [{"start": w.start, "end": w.end, "word": w.word} for w in (resp.words or [])]
    result = []
    for seg in resp.segments:
        seg_words = [w for w in words if seg.start <= w["start"] < seg.end]
        result.append(
            {"start": seg.start, "end": seg.end, "text": seg.text.strip(), "words": seg_words}
        )
    return result


if __name__ == "__main__":
    import sys, yaml
    cfg = yaml.safe_load(Path("config.yaml").read_text())["transcribe"]
    transcribe(sys.argv[1], Path("output/manual"), cfg)
