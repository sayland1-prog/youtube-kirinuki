import os

from dotenv import load_dotenv
load_dotenv()  # .env を最初にロード

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "kirinuki",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Tokyo",
    enable_utc=True,
    worker_concurrency=int(os.environ.get("MAX_CONCURRENT_JOBS", "10")),
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # 1ジョブずつ取得（重い処理なので）
    beat_schedule={
        # 毎日0時に期限切れファイルを削除
        "delete-expired-jobs": {
            "task": "worker.delete_expired_jobs_task",
            "schedule": crontab(hour=0, minute=0),
        },
    },
)
