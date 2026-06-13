"""
オーケストレーター
取得 → 文字起こし → ハイライト選定 → 切り抜き加工 を一気通貫で実行する。

使い方:
  # 全工程を一気に実行
  python pipeline.py "https://www.youtube.com/watch?v=XXXX"

  # 選定までで止めて clips.json を確認 → 承認後に切り抜き
  python pipeline.py "URL" --until analyze
  python pipeline.py "URL" --from-clips output/XXXX/clips.json

  # 切り抜き加工をスキップして候補一覧だけ確認（--dry-run）
  python pipeline.py "URL" --dry-run

  # 複数URLをまとめて処理（--batch）
  python pipeline.py --batch urls.txt
  python pipeline.py --batch urls.txt --dry-run
  python pipeline.py --batch urls.txt --until analyze
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

from scripts.fetch import fetch
from scripts.transcribe import transcribe
from scripts.analyze import analyze
from scripts.clip import make_clips


def load_cfg() -> dict:
    return yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))


def workdir_for(video_id: str) -> Path:
    return Path("output") / video_id


def run_single(url: str, args, cfg: dict) -> bool:
    """1つのURLを処理。成功したら True、失敗したら False を返す。"""
    try:
        # --- 承認済みクリップから加工だけ再開 ---
        if args.from_clips:
            clips_path = Path(args.from_clips)
            work = clips_path.parent
            transcript_data = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
            video = str(work / "source.mp4")
            clips = json.loads(clips_path.read_text(encoding="utf-8"))
            print("■ 工程4: 切り抜き加工（承認済みクリップ）")
            make_clips(video, transcript_data, clips, work, cfg)
            return True

        # --- 工程1: 取得 ---
        print("■ 工程1: 取得")
        f = fetch(url, Path("output") / "tmp", cfg["download"]["resolution"])
        video_id = f["meta"].get("id") or "clip"
        work = workdir_for(video_id)
        work.mkdir(parents=True, exist_ok=True)

        # source.mp4 を正しいworkdirへ移動（tmpから）
        tmp_video = Path("output") / "tmp" / "source.mp4"
        final_video = work / "source.mp4"
        if tmp_video.exists() and tmp_video != final_video:
            tmp_video.rename(final_video)
            info_src = Path("output") / "tmp" / "source.info.json"
            if info_src.exists():
                info_src.rename(work / "source.info.json")

        f["video"] = str(final_video)

        if args.until == "fetch":
            print(f"  ⏸ fetch で停止。作業フォルダ: {work}")
            return True

        # --- 工程2: 文字起こし ---
        print("■ 工程2: 文字起こし")
        transcript_data = transcribe(f["video"], work, cfg["transcribe"])
        if args.until == "transcribe":
            print(f"  ⏸ transcribe で停止。作業フォルダ: {work}")
            return True

        # --- 工程3: ハイライト選定 ---
        print("■ 工程3: ハイライト選定")
        clips = analyze(transcript_data, f["meta"], cfg["analyze"])
        clips_path = work / "clips.json"
        clips_path.write_text(json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  → 選定結果: {clips_path}")

        if args.until == "analyze" or getattr(args, "dry_run", False):
            if getattr(args, "dry_run", False):
                print("\n  🏃 --dry-run モード: 切り抜き加工をスキップします")
            else:
                print(f"\n確認後、次で切り抜きを実行:")
                print(f'  python pipeline.py "{url}" --from-clips {clips_path}')
            return True

        # --- 工程4: 切り抜き加工 ---
        print("■ 工程4: 切り抜き加工")
        make_clips(f["video"], transcript_data, clips, work, cfg)
        print("\n=== 完了 ===")
        return True

    except (EnvironmentError, RuntimeError) as e:
        print(f"\n❌ エラー: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}", file=sys.stderr)
        return False


def run_batch(batch_file: str, args, cfg: dict):
    """テキストファイルから複数URLを読み込んで順番に処理する。"""
    urls = []
    for line in Path(batch_file).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)

    if not urls:
        print(f"⚠ {batch_file} に処理対象のURLが見つかりませんでした。")
        return

    print(f"バッチ処理: {len(urls)} 件のURLを処理します\n")
    results = []
    for i, url in enumerate(urls, 1):
        print(f"{'='*50}")
        print(f"[{i}/{len(urls)}] {url}")
        print(f"{'='*50}")
        ok = run_single(url, args, cfg)
        results.append((url, ok))
        print()

    # サマリー
    print("\n" + "="*50)
    print("バッチ処理サマリー")
    print("="*50)
    success = sum(1 for _, ok in results if ok)
    fail = len(results) - success
    for url, ok in results:
        status = "✓ 成功" if ok else "✗ 失敗"
        print(f"  {status}  {url}")
    print(f"\n合計: {success} 件成功 / {fail} 件失敗 / {len(results)} 件")


def main():
    ap = argparse.ArgumentParser(description="YouTube 切り抜き自動化パイプライン")
    ap.add_argument("url", nargs="?", help="YouTube 動画URL（--batch 使用時は省略可）")
    ap.add_argument("--until", choices=["fetch", "transcribe", "analyze"],
                    help="この工程まで実行して停止（確認用）")
    ap.add_argument("--from-clips", help="承認済み clips.json から切り抜きだけ実行")
    ap.add_argument("--dry-run", action="store_true",
                    help="切り抜き加工をスキップして候補一覧だけ確認")
    ap.add_argument("--batch", metavar="FILE",
                    help="URLを1行1件で書いたテキストファイルを指定してバッチ処理")
    args = ap.parse_args()

    if not args.url and not args.batch and not args.from_clips:
        ap.print_help()
        sys.exit(1)

    cfg = load_cfg()

    if args.batch:
        run_batch(args.batch, args, cfg)
    else:
        ok = run_single(args.url or "", args, cfg)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
