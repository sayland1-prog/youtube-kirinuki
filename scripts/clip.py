"""
工程4: 切り抜き加工
ffmpeg で指定区間をカットし、9:16 / 16:9 に整形、字幕を焼き込む。
"""
import re
import subprocess
from pathlib import Path

from scripts.subtitle_utils import write_ass


def _slug(text: str, n: int = 30) -> str:
    """ファイル名向けに安全化。"""
    s = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]+", "_", text).strip("_")
    return s[:n] or "clip"


def _ass_path_for_filter(p: Path) -> str:
    """ffmpeg フィルタ用にパスをエスケープ（Windowsのドライブコロン対策含む）。"""
    s = str(p.resolve())
    return s.replace("\\", "/").replace(":", "\\:")


def make_clips(video: str, transcript: list, clips: list, work_dir: Path, cfg: dict):
    """全クリップを生成し、メタ情報テキストを書き出す。"""
    out_dir = work_dir / "clips"
    out_dir.mkdir(parents=True, exist_ok=True)
    sub_cfg = cfg["subtitle"]
    clip_cfg = cfg["clip"]
    burn = clip_cfg.get("burn_subtitles", True)

    results = []
    for i, c in enumerate(clips, 1):
        start, dur = c["start"], c["end"] - c["start"]
        base = f"{i:02d}_{_slug(c['title'])}"
        print(f"\n  [{i}/{len(clips)}] {c['title']}  ({start:.0f}-{c['end']:.0f}s)")

        if clip_cfg.get("horizontal", True):
            ass = None
            if burn:
                ass = write_ass(transcript, start, c["end"], out_dir / f"{base}_h.ass", 1920, 1080, sub_cfg)
            outp = out_dir / f"{base}_16x9.mp4"
            _run_horizontal(video, start, dur, ass, outp)
            print(f"      ✓ 横型: {outp.name}")

        if clip_cfg.get("vertical", True):
            ass = None
            if burn:
                ass = write_ass(transcript, start, c["end"], out_dir / f"{base}_v.ass", 1080, 1920, sub_cfg)
            outp = out_dir / f"{base}_9x16.mp4"
            _run_vertical(video, start, dur, ass, outp, clip_cfg.get("vertical_layout", "blur"))
            print(f"      ✓ 縦型: {outp.name}")

        # 投稿用メタ情報
        meta_txt = (
            f"{c['title']}\n\n{c.get('caption','')}\n\n"
            f"{' '.join(c.get('hashtags', []))}\n\n"
            f"---\n選定理由: {c.get('reason','')}\n元区間: {start:.0f}-{c['end']:.0f}s"
        )
        (out_dir / f"{base}.txt").write_text(meta_txt, encoding="utf-8")
        results.append(base)

    print(f"\n  ✓ 全 {len(results)} 件を {out_dir} に出力しました。")
    return results


def _run_horizontal(video, start, dur, ass, outp):
    vf = "scale=1920:1080:force_original_aspect_ratio=decrease," \
         "pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
    if ass:
        vf += f",ass={_ass_path_for_filter(ass)}"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", video, "-t", str(dur),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", str(outp),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _run_vertical(video, start, dur, ass, outp, layout):
    if layout == "crop":
        # 中央クロップ（左右が切れる代わりに被写体が大きく映る）
        chain = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    else:
        # ぼかし背景にフィット（左右を切らない / 配信向けに無難）
        chain = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=24:6[bg];"
            "[0:v]scale=1080:-2[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )

    if layout == "crop":
        vf = chain + (f",ass={_ass_path_for_filter(ass)}" if ass else "")
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", video, "-t", str(dur),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", str(outp),
        ]
    else:
        fc = chain + (f",ass={_ass_path_for_filter(ass)}" if ass else "") + "[outv]"
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", video, "-t", str(dur),
            "-filter_complex", fc, "-map", "[outv]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", str(outp),
        ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
