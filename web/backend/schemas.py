import re
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# YouTube URL の許可パターン（SSRF対策: youtube.com / youtu.be のみ）
_YT_PATTERN = re.compile(
    r"^https?://(www\.)?(youtube\.com/watch\?.*v=[\w-]+|youtu\.be/[\w-]+)",
    re.IGNORECASE,
)

JobStatus = Literal[
    "queued", "downloading", "transcribing", "analyzing", "clipping", "done", "failed"
]


# ---------- リクエスト ----------

class CreateJobRequest(BaseModel):
    youtube_url: str = Field(..., description="YouTube 動画 URL")
    email: EmailStr = Field(..., description="完了通知先メールアドレス")
    agreed_terms: bool = Field(..., description="利用規約への同意（必ず True）")

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if not _YT_PATTERN.match(v.strip()):
            raise ValueError(
                "YouTubeの動画URLを入力してください（例: https://www.youtube.com/watch?v=...）"
            )
        return v.strip()

    @field_validator("agreed_terms")
    @classmethod
    def must_agree(cls, v: bool) -> bool:
        if not v:
            raise ValueError("利用規約に同意してください")
        return v


# ---------- レスポンス ----------

class CreateJobResponse(BaseModel):
    job_id: UUID
    status: JobStatus = "queued"


class ProgressInfo(BaseModel):
    step: Optional[str]
    percent: Optional[int]


class ClipItem(BaseModel):
    title: str
    url_9x16: str
    url_16x9: str
    caption_txt_url: str


class JobResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    progress: Optional[ProgressInfo] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    clips: Optional[list[ClipItem]] = None


# ---------- エラー ----------

class ErrorResponse(BaseModel):
    detail: str
