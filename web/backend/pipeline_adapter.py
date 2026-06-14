"""
既存 pipeline.py / scripts/* を Web バックエンドから呼び出すための薄いラッパー。
CLI エントリポイント（pipeline.py の main()）は一切変更しない。
"""
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Callable, Optional

# scripts/ が pipeline.py と同階層にあるため sys.path に追加
_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import yaml
from scripts.fetch import fetch
from scripts.transcribe import transcribe
from scripts.analyze import analyze
from scripts.clip import make_clips

ProgressCallback = Optional[Callable[[str, int], None]]


def _load_cfg() -> dict:
    cfg_path = _REPO_ROOT / "config.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


# コスト防御用のデフォルト（config.yaml の limits が無い場合のフォールバック）
_DEFAULT_LIMITS = {
    "max_video_seconds": 5400,
    "max_transcript_chars": 80000,
    "rate_per_ip_day": 5,
    "rate_per_email_day": 5,
    "rate_total_day": 100,
}


def load_limits() -> dict:
    """Web サービスのコスト防御上限を返す。config.yaml の limits をデフォルトにマージ。"""
    cfg = _load_cfg()
    limits = dict(_DEFAULT_LIMITS)
    limits.update(cfg.get("limits") or {})
    return limits


def run_fetch(
    youtube_url: str,
    work_dir: Path,
    cfg: Optional[dict] = None,
    on_progress: ProgressCallback = None,
) -> dict:
    """
    工程1: YouTube 動画を取得して work_dir/source.mp4 に保存する。
    戻り値: fetch() の返り値（video パスと meta を含む dict）
    """
    if cfg is None:
        cfg = _load_cfg()
    if on_progress:
        on_progress("downloading", 0)

    work_dir.mkdir(parents=True, exist_ok=True)

    # fetch() は出力先ディレクトリを受け取る
    result = fetch(youtube_url, work_dir, cfg["download"]["resolution"])

    # fetch が tmp に出力した場合は work_dir へ移動
    tmp_video = work_dir / "source.mp4"
    if not tmp_video.exists():
        # fetch の返り値から video パスを確認
        src = Path(result.get("video", ""))
        if src.exists() and src != tmp_video:
            shutil.move(str(src), str(tmp_video))
            info_src = src.parent / "source.info.json"
            if info_src.exists():
                shutil.move(str(info_src), str(work_dir / "source.info.json"))

    result["video"] = str(tmp_video)

    if on_progress:
        on_progress("downloading", 100)
    return result


def run_transcribe(
    work_dir: Path,
    cfg: Optional[dict] = None,
    on_progress: ProgressCallback = None,
) -> dict:
    """
    工程2: work_dir/source.mp4 を文字起こしして work_dir/transcript.json を生成。
    戻り値: transcript データ（dict）
    """
    if cfg is None:
        cfg = _load_cfg()
    if on_progress:
        on_progress("transcribing", 0)

    video_path = work_dir / "source.mp4"
    transcript_data = transcribe(str(video_path), work_dir, cfg["transcribe"])

    if on_progress:
        on_progress("transcribing", 100)
    return transcript_data


def run_analyze(
    work_dir: Path,
    meta: dict,
    cfg: Optional[dict] = None,
    on_progress: ProgressCallback = None,
) -> list:
    """
    工程3: transcript.json からハイライト候補を選定して work_dir/clips.json を生成。
    Web サービスでは確認ステップを挟まず完全自動で進める。
    戻り値: clips リスト
    """
    if cfg is None:
        cfg = _load_cfg()
    if on_progress:
        on_progress("analyzing", 0)

    transcript_path = work_dir / "transcript.json"
    transcript_data = json.loads(transcript_path.read_text(encoding="utf-8"))

    # コスト防御: Claude へ渡す文字起こしの総量を上限で打ち切る（入力トークン暴発の二重防止）
    max_chars = load_limits()["max_transcript_chars"]
    total = 0
    capped = []
    for seg in transcript_data:
        total += len(seg.get("text", ""))
        if total > max_chars:
            break
        capped.append(seg)
    transcript_data = capped or transcript_data[:1]

    clips = analyze(transcript_data, meta, cfg["analyze"])

    # clips.json に保存
    clips_path = work_dir / "clips.json"
    clips_path.write_text(
        json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if on_progress:
        on_progress("analyzing", 100)
    return clips


def run_clip(
    work_dir: Path,
    cfg: Optional[dict] = None,
    on_progress: ProgressCallback = None,
) -> list[Path]:
    """
    工程4: clips.json をもとに動画を加工して work_dir/clips/ 以下に出力。
    戻り値: 生成されたファイルパスのリスト
    """
    if cfg is None:
        cfg = _load_cfg()
    if on_progress:
        on_progress("clipping", 0)

    video_path = work_dir / "source.mp4"
    transcript_path = work_dir / "transcript.json"
    clips_path = work_dir / "clips.json"

    transcript_data = json.loads(transcript_path.read_text(encoding="utf-8"))
    clips = json.loads(clips_path.read_text(encoding="utf-8"))

    make_clips(str(video_path), transcript_data, clips, work_dir, cfg)

    # 生成されたファイルを収集
    clips_dir = work_dir / "clips"
    generated: list[Path] = []
    if clips_dir.exists():
        generated = sorted(clips_dir.iterdir())

    if on_progress:
        on_progress("clipping", 100)
    return generated
