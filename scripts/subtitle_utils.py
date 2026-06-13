"""
字幕ユーティリティ
文字起こしから指定区間の word を取り出し、0秒起点に再配置して、
焼き込み用の ASS 字幕ファイルを生成する。
"""
from pathlib import Path


def _fmt_time(t: float) -> str:
    """秒 → ASS 形式 (H:MM:SS.cc)"""
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    if cs == 100:
        cs = 0
        s += 1
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _collect_words(transcript: list, start: float, end: float):
    """区間内の word を 0秒起点に再配置して取り出す。なければセグメント単位で代用。"""
    words = []
    for seg in transcript:
        for w in seg.get("words", []):
            if w["end"] > start and w["start"] < end:
                words.append(
                    {
                        "start": max(0, w["start"] - start),
                        "end": min(end, w["end"]) - start,
                        "word": w["word"].strip(),
                    }
                )
    if words:
        return words
    # フォールバック: word が無ければ segment 単位
    for seg in transcript:
        if seg["end"] > start and seg["start"] < end:
            words.append(
                {
                    "start": max(0, seg["start"] - start),
                    "end": min(end, seg["end"]) - start,
                    "word": seg["text"].strip(),
                }
            )
    return words


def _group(words, max_chars=18, max_gap=0.7):
    """word を読みやすい字幕行にまとめる。"""
    lines, buf = [], []
    enders = "。．！？!?、，,"
    for w in words:
        if buf and (w["start"] - buf[-1]["end"] > max_gap):
            lines.append(buf)
            buf = []
        buf.append(w)
        text = "".join(x["word"] for x in buf)
        if len(text) >= max_chars or (text and text[-1] in enders):
            lines.append(buf)
            buf = []
    if buf:
        lines.append(buf)

    events = []
    for grp in lines:
        if not grp:
            continue
        text = "".join(x["word"] for x in grp).strip().rstrip("、，,")
        if text:
            events.append({"start": grp[0]["start"], "end": grp[-1]["end"], "text": text})
    return events


def write_ass(transcript, start, end, out_path: Path, play_w, play_h, cfg):
    """指定区間の ASS 字幕を生成する。"""
    words = _collect_words(transcript, start, end)
    events = _group(words, cfg.get("max_chars", 18), cfg.get("max_gap", 0.7))

    font = cfg.get("font", "Hiragino Sans")
    outline = cfg.get("outline", 4)
    # 縦型は下から1/3あたり、横型は最下部に配置
    if play_h > play_w:  # vertical
        fontsize = cfg.get("fontsize_vertical", 72)
        margin_v = int(play_h * 0.27)
    else:  # horizontal
        fontsize = cfg.get("fontsize_horizontal", 52)
        margin_v = int(play_h * 0.06)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_w}
PlayResY: {play_h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{fontsize},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,{outline},2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]
    for ev in events:
        txt = ev["text"].replace("\n", "\\N")
        lines.append(
            f"Dialogue: 0,{_fmt_time(ev['start'])},{_fmt_time(ev['end'])},Default,,0,0,0,,{txt}"
        )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
