"""
工程1: 動画取得
pytubefix で YouTube 動画とメタデータをダウンロードする。
yt-dlp が利用可能な場合はフォールバックとして使用する。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def fetch(url: str, work_dir: Path, resolution: int = 1080) -> dict:
    """動画をDLし、{'video': パス, 'meta': メタ情報} を返す。"""
    if not shutil.which("ffmpeg"):
        raise EnvironmentError(
            "ffmpeg が見つかりません。`brew install ffmpeg` でインストールしてください。"
        )

    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        return _fetch_pytubefix(url, work_dir, resolution)
    except Exception as e:
        print(f"  ⚠ pytubefix 失敗（{e}）。yt-dlp にフォールバック...")
        return _fetch_ytdlp(url, work_dir, resolution)


def _fetch_pytubefix(url: str, work_dir: Path, resolution: int) -> dict:
    try:
        from pytubefix import YouTube
    except ImportError:
        raise EnvironmentError(
            "pytubefix がインストールされていません。\n"
            "  `pip3 install pytubefix` を実行してください。"
        )

    video_path = work_dir / "source.mp4"
    print(f"  → pytubefix で取得中: {url}")

    yt = YouTube(url)
    meta = {
        "title": yt.title,
        "id": yt.video_id,
        "duration": yt.length,
        "uploader": yt.author,
    }

    # 映像ストリーム（指定解像度以下の最高画質）
    video_stream = (
        yt.streams
        .filter(adaptive=True, file_extension="mp4", only_video=True)
        .filter(res=f"{resolution}p")
        .first()
        or yt.streams
        .filter(adaptive=True, file_extension="mp4", only_video=True)
        .order_by("resolution")
        .desc()
        .first()
    )
    # 音声ストリーム
    audio_stream = (
        yt.streams
        .filter(adaptive=True, only_audio=True, file_extension="mp4")
        .order_by("abr")
        .desc()
        .first()
    )

    if not video_stream or not audio_stream:
        raise RuntimeError("適切なストリームが見つかりませんでした。")

    tmp_v = work_dir / "_tmp_video.mp4"
    tmp_a = work_dir / "_tmp_audio.mp4"

    print(f"     映像: {video_stream.resolution} / 音声: {audio_stream.abr}")
    video_stream.download(output_path=str(work_dir), filename="_tmp_video.mp4")
    audio_stream.download(output_path=str(work_dir), filename="_tmp_audio.mp4")

    # ffmpeg でマージ
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(tmp_v), "-i", str(tmp_a),
         "-c:v", "copy", "-c:a", "aac", str(video_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    tmp_v.unlink(missing_ok=True)
    tmp_a.unlink(missing_ok=True)

    # info.json を保存（yt-dlp 互換）
    info_path = work_dir / "source.info.json"
    info_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  ✓ 取得完了: {meta['title']}")
    return {"video": str(video_path), "meta": meta}


def _fetch_ytdlp(url: str, work_dir: Path, resolution: int) -> dict:
    video_path = work_dir / "source.mp4"

    yt_dlp_cmd = shutil.which("yt-dlp")
    yt_dlp_base = [yt_dlp_cmd] if yt_dlp_cmd else [sys.executable, "-m", "yt_dlp"]

    fmt = (
        f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/"
        f"best[height<={resolution}]/best"
    )
    cmd = yt_dlp_base + [
        "-f", fmt,
        "--merge-output-format", "mp4",
        "-o", str(video_path),
        "--write-info-json",
        "--no-playlist",
        "--force-overwrites",
        url,
    ]
    print(f"  → yt-dlp で取得中: {url}")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise EnvironmentError(
            "yt-dlp も pytubefix も使えません。`pip3 install pytubefix` を試してください。"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"yt-dlp が失敗しました（終了コード {e.returncode}）。\n"
            "  ・`pip3 install -U yt-dlp` で最新化すると解決することがあります。"
        ) from e

    meta = {}
    info_path = work_dir / "source.info.json"
    if info_path.exists():
        data = json.loads(info_path.read_text(encoding="utf-8"))
        meta = {
            "title": data.get("title"),
            "id": data.get("id"),
            "duration": data.get("duration"),
            "uploader": data.get("uploader"),
        }

    print(f"  ✓ 取得完了: {meta.get('title', video_path.name)}")
    return {"video": str(video_path), "meta": meta}


if __name__ == "__main__":
    out = _fetch_pytubefix(sys.argv[1], Path("output/manual"), 1080)
    print(json.dumps(out, ensure_ascii=False, indent=2))
