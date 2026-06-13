"""
FastAPI エントリポイント
POST /api/jobs  — ジョブ作成
GET  /api/jobs/{job_id} — ジョブ状態取得
"""
import os
import uuid

from dotenv import load_dotenv
load_dotenv()  # .env を最初にロード（他の import より前に実行）
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Job
from schemas import CreateJobRequest, CreateJobResponse, ErrorResponse, JobResponse
from storage import generate_signed_urls
from worker import process_job

MAX_CONCURRENT_JOBS = int(os.environ.get("MAX_CONCURRENT_JOBS", "10"))
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="youtube-kirinuki API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # allow_origins にワイルドカードサブドメインは効かないため allow_origin_regex を使う
    allow_origins=[FRONTEND_ORIGIN],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _active_job_count(db: Session) -> int:
    return db.query(Job).filter(
        Job.status.in_(["queued", "downloading", "transcribing", "analyzing", "clipping"])
    ).count()


@app.post(
    "/api/jobs",
    response_model=CreateJobResponse,
    status_code=202,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def create_job(body: CreateJobRequest, db: Session = Depends(get_db)):
    # 同時処理上限チェック
    if _active_job_count(db) >= MAX_CONCURRENT_JOBS:
        raise HTTPException(
            status_code=429,
            detail="現在混み合っています。少し時間をおいてから再度お試しください。",
        )

    job = Job(
        youtube_url=body.youtube_url,
        email=str(body.email),
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Celery キューに積む
    process_job.delay(str(job.id))

    return CreateJobResponse(job_id=job.id, status="queued")


@app.get(
    "/api/jobs/{job_id}",
    response_model=JobResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_job(job_id: str, db: Session = Depends(get_db)):
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="このリンクは無効か、有効期限が切れています。")

    job = db.get(Job, uid)
    if not job:
        raise HTTPException(status_code=404, detail="このリンクは無効か、有効期限が切れています。")

    # done の場合のみ署名付き URL を生成
    signed_urls: dict[str, str] = {}
    if job.status == "done" and job.clips:
        all_keys = [
            v for rec in job.clips
            for k, v in rec.items() if k.startswith("r2_key_")
        ]
        signed_urls = generate_signed_urls(all_keys)

    return JobResponse(**job.to_response_dict(signed_urls))
