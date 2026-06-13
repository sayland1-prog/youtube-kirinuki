from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    youtube_url = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)
    # queued / downloading / transcribing / analyzing / clipping / done / failed
    status = Column(String(32), nullable=False, default="queued")
    error_msg = Column(Text, nullable=True)
    # [{"title": str, "r2_key_9x16": str, "r2_key_16x9": str, "r2_key_txt": str}]
    clips = Column(JSON, nullable=True)
    queue_position = Column(String(16), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=7),
    )

    def to_response_dict(self, signed_urls: Optional[dict[str, str]] = None) -> dict:
        """API レスポンス用の dict を返す。"""
        clip_items = None
        if self.status == "done" and self.clips and signed_urls:
            clip_items = [
                {
                    "title": c.get("title", ""),
                    "url_9x16": signed_urls.get(c.get("r2_key_9x16", ""), ""),
                    "url_16x9": signed_urls.get(c.get("r2_key_16x9", ""), ""),
                    "caption_txt_url": signed_urls.get(c.get("r2_key_txt", ""), ""),
                }
                for c in self.clips
            ]

        progress_step = self.status if self.status not in ("done", "failed", "queued") else None

        return {
            "job_id": str(self.id),
            "status": self.status,
            "progress": {"step": progress_step, "percent": None} if progress_step else None,
            "error_message": self.error_msg,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "clips": clip_items,
        }
