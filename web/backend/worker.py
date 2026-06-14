"""
Celery タスク: YouTube URL → 切り抜き動画生成 → R2 アップロード → メール送信
"""
import json
import tempfile
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # .env を最初にロード（celery_app より先に環境変数を確定させる）

from sqlalchemy import select

from celery_app import celery_app
from database import SessionLocal
from models import Job
from pipeline_adapter import load_limits, run_fetch, run_analyze, run_clip, run_transcribe

_LIMITS = load_limits()


class VideoTooLongError(Exception):
    """処理上限を超える長尺動画。"""
from storage import delete_expired_jobs, generate_signed_urls, upload_file
from mailer import send_failure_email, send_success_email


def _update_status(job_id: str, status: str, error_msg: str | None = None) -> None:
    """DB のジョブステータスを更新する。"""
    with SessionLocal() as db:
        job = db.get(Job, uuid.UUID(job_id))
        if job:
            job.status = status
            if error_msg is not None:
                job.error_msg = error_msg
            db.commit()


def _to_user_error(exc: Exception) -> str:
    """例外を生活者語のエラーメッセージに変換する。"""
    msg = str(exc).lower()
    if "download" in msg or "yt-dlp" in msg or "fetch" in msg:
        return "動画を取得できませんでした。URLをご確認ください。"
    if "private" in msg or "unavailable" in msg:
        return "動画にアクセスできませんでした。非公開または削除された動画の可能性があります。"
    if "transcri" in msg or "whisper" in msg:
        return "音声の解析中にエラーが発生しました。"
    if "analyz" in msg or "claude" in msg or "anthropic" in msg:
        return "見どころの選定中にエラーが発生しました。"
    if "clip" in msg or "ffmpeg" in msg:
        return "動画の加工中にエラーが発生しました。"
    return "処理中にエラーが発生しました。再度お試しください。"


@celery_app.task(bind=True, max_retries=0)
def process_job(self, job_id: str) -> None:
    """メインの切り抜きジョブタスク。"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir) / job_id

        try:
            # ジョブ情報を取得
            with SessionLocal() as db:
                job = db.get(Job, uuid.UUID(job_id))
                if not job:
                    return
                youtube_url = job.youtube_url
                email = job.email
                expires_at = job.expires_at.isoformat() if job.expires_at else None

            # 工程1: ダウンロード
            _update_status(job_id, "downloading")
            result = run_fetch(youtube_url, work_dir)
            meta = result.get("meta", {})

            # コスト防御: 尺上限を超える動画は文字起こし(CPU)/Claude(トークン)前に拒否
            duration = meta.get("duration") or 0
            max_seconds = _LIMITS["max_video_seconds"]
            if duration and duration > max_seconds:
                raise VideoTooLongError(
                    f"動画が長すぎます（{int(duration // 60)}分）。"
                    f"{max_seconds // 60}分以内の動画をご利用ください。"
                )

            # 工程2: 文字起こし
            _update_status(job_id, "transcribing")
            run_transcribe(work_dir)

            # 工程3: ハイライト選定（完全自動・確認なし）
            _update_status(job_id, "analyzing")
            run_analyze(work_dir, meta)

            # 工程4: 動画加工
            _update_status(job_id, "clipping")
            generated_files = run_clip(work_dir)

            # clips.json からタイトルを取得（ファイル名ステムではなく正式タイトルを使う）
            clips_json_path = work_dir / "clips.json"
            clips_data: list[dict] = json.loads(clips_json_path.read_text(encoding="utf-8")) if clips_json_path.exists() else []
            # 番号プレフィックス "01_" などからタイトルを引くための辞書を作成
            title_by_index = {str(i + 1).zfill(2): c.get("title", "") for i, c in enumerate(clips_data)}

            # R2 アップロード
            clip_records = []

            # generated_files をクリップ単位でグループ化
            stems: dict[str, dict] = {}
            for f in generated_files:
                if f.suffix not in (".mp4", ".txt"):
                    continue
                # ファイル名パターン: 01_タイトル_9x16.mp4 / 01_タイトル_16x9.mp4 / 01_タイトル.txt
                name = f.stem
                if name.endswith("_9x16"):
                    base = name[:-5]
                    stems.setdefault(base, {})["9x16"] = f
                elif name.endswith("_16x9"):
                    base = name[:-5]
                    stems.setdefault(base, {})["16x9"] = f
                else:
                    stems.setdefault(name, {})["txt"] = f

            for base, files in stems.items():
                prefix = f"jobs/{job_id}/{base}"
                # clips.json の正式タイトルを使う。なければファイル名ステムにフォールバック
                idx = base.split("_")[0] if "_" in base else base
                title = title_by_index.get(idx, base)
                record: dict = {"title": title}

                for variant, local_path in files.items():
                    if variant == "9x16":
                        key = f"{prefix}_9x16.mp4"
                    elif variant == "16x9":
                        key = f"{prefix}_16x9.mp4"
                    else:
                        key = f"{prefix}.txt"
                    upload_file(local_path, key)
                    record[f"r2_key_{variant}"] = key

                clip_records.append(record)

            # DB 更新: done
            with SessionLocal() as db:
                job = db.get(Job, uuid.UUID(job_id))
                if job:
                    job.status = "done"
                    job.clips = clip_records
                    db.commit()

            # 署名付き URL 生成 → 成功メール
            all_keys = [
                v for rec in clip_records
                for k, v in rec.items() if k.startswith("r2_key_")
            ]
            signed_urls = generate_signed_urls(all_keys)

            clips_for_mail = [
                {
                    "title": rec.get("title", ""),
                    "url_9x16": signed_urls.get(rec.get("r2_key_9x16", ""), ""),
                    "url_16x9": signed_urls.get(rec.get("r2_key_16x9", ""), ""),
                    "caption_txt_url": signed_urls.get(rec.get("r2_key_txt", ""), ""),
                }
                for rec in clip_records
            ]
            send_success_email(email, job_id, clips_for_mail, expires_at)

        except VideoTooLongError as exc:
            # 尺超過はそのままユーザーへ見せる（生活者語で十分な文言のため）
            user_msg = str(exc)
            _update_status(job_id, "failed", user_msg)
            with SessionLocal() as db:
                job = db.get(Job, uuid.UUID(job_id))
                if job:
                    send_failure_email(job.email, job_id, user_msg)
            return

        except Exception as exc:
            user_msg = _to_user_error(exc)
            _update_status(job_id, "failed", user_msg)
            with SessionLocal() as db:
                job = db.get(Job, uuid.UUID(job_id))
                if job:
                    send_failure_email(job.email, job_id, user_msg)
            raise


@celery_app.task
def delete_expired_jobs_task() -> None:
    """期限切れジョブの R2 ファイルを削除する定期タスク（毎日0時）。"""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        expired = db.execute(
            select(Job).where(Job.expires_at < now, Job.clips.isnot(None))
        ).scalars().all()

        clip_records = [job.clips for job in expired if job.clips]
        if clip_records:
            delete_expired_jobs(clip_records)

        # clips を null にして二重削除を防ぐ
        for job in expired:
            job.clips = None
        db.commit()
