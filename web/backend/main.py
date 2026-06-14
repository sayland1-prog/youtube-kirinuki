"""
FastAPI エントリポイント
POST /api/jobs  — ジョブ作成
GET  /api/jobs/{job_id} — ジョブ状態取得
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv()  # .env を最初にロード（他の import より前に実行）
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Job
from pipeline_adapter import load_limits
from schemas import CreateJobRequest, CreateJobResponse, ErrorResponse, JobResponse
from storage import generate_signed_urls
from worker import process_job

MAX_CONCURRENT_JOBS = int(os.environ.get("MAX_CONCURRENT_JOBS", "10"))
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
LIMITS = load_limits()  # コスト防御の上限（config.yaml の limits）


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


def _client_ip(request: Request) -> str:
    """プロキシ(nginx)経由のため X-Forwarded-For 先頭を信頼。無ければ直 IP。"""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _count_since(db: Session, *, hours: int, email: str | None = None, ip: str | None = None) -> int:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = db.query(Job).filter(Job.created_at >= since)
    if email is not None:
        q = q.filter(Job.email == email)
    if ip is not None:
        q = q.filter(Job.client_ip == ip)
    return q.count()


@app.post(
    "/api/jobs",
    response_model=CreateJobResponse,
    status_code=202,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def create_job(body: CreateJobRequest, request: Request, db: Session = Depends(get_db)):
    # 同時処理上限チェック
    if _active_job_count(db) >= MAX_CONCURRENT_JOBS:
        raise HTTPException(
            status_code=429,
            detail="現在混み合っています。少し時間をおいてから再度お試しください。",
        )

    # コスト防御: 日次レート制限（全体 → IP → メール の順で安い判定から）
    ip = _client_ip(request)
    email = str(body.email)
    if _count_since(db, hours=24) >= LIMITS["rate_total_day"]:
        raise HTTPException(
            status_code=429,
            detail="本日の受付上限に達しました。時間をおいて再度お試しください。",
        )
    if _count_since(db, hours=24, ip=ip) >= LIMITS["rate_per_ip_day"]:
        raise HTTPException(
            status_code=429,
            detail="本日のご利用回数の上限に達しました。明日以降に再度お試しください。",
        )
    if _count_since(db, hours=24, email=email) >= LIMITS["rate_per_email_day"]:
        raise HTTPException(
            status_code=429,
            detail="このメールアドレスの本日のご利用回数の上限に達しました。",
        )

    job = Job(
        youtube_url=body.youtube_url,
        email=email,
        client_ip=ip,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Celery キューに積む
    process_job.delay(str(job.id))

    return CreateJobResponse(job_id=job.id, status="queued")


@app.get("/health")
def health():
    return {"status": "ok"}


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
