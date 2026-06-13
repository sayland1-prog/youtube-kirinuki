import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/kirinuki")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI の Depends で使う DB セッションジェネレータ。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """アプリ起動時にテーブルを作成する。"""
    from models import Base  # 循環回避のため遅延 import
    Base.metadata.create_all(bind=engine)
