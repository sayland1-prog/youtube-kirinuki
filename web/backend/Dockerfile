FROM python:3.11-slim

# システム依存（ffmpeg + yt-dlp 実行に必要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ルートの requirements（pipeline.py 依存）
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# バックエンド固有の requirements
COPY web/backend/requirements.txt /app/web/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/web/backend/requirements.txt

# ソースコード全体をコピー（pipeline.py / scripts/ が必要）
COPY . /app

ENV PYTHONPATH=/app
WORKDIR /app/web/backend
