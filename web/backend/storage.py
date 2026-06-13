import os
from pathlib import Path

import boto3
from botocore.config import Config

_R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
_R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY_ID", "")
_R2_SECRET_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
_R2_BUCKET = os.environ.get("R2_BUCKET", "kirinuki")

_SIGNED_URL_EXPIRES = 7 * 24 * 3600  # 7日間（秒）


def _client():
    return boto3.client(
        "s3",
        endpoint_url=_R2_ENDPOINT,
        aws_access_key_id=_R2_ACCESS_KEY,
        aws_secret_access_key=_R2_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_file(local_path: Path, r2_key: str) -> None:
    """ファイルを R2 にアップロードする。"""
    content_type = "video/mp4" if str(local_path).endswith(".mp4") else "text/plain"
    _client().upload_file(
        str(local_path),
        _R2_BUCKET,
        r2_key,
        ExtraArgs={"ContentType": content_type},
    )


def generate_signed_url(r2_key: str, expires_in: int = _SIGNED_URL_EXPIRES) -> str:
    """署名付き URL を生成する（デフォルト7日間有効）。"""
    return _client().generate_presigned_url(
        "get_object",
        Params={"Bucket": _R2_BUCKET, "Key": r2_key},
        ExpiresIn=expires_in,
    )


def generate_signed_urls(r2_keys: list[str]) -> dict[str, str]:
    """複数キーの署名付き URL を一括生成して {key: url} の dict を返す。"""
    return {key: generate_signed_url(key) for key in r2_keys if key}


def delete_file(r2_key: str) -> None:
    """R2 からファイルを削除する。"""
    _client().delete_object(Bucket=_R2_BUCKET, Key=r2_key)


def delete_expired_jobs(expired_clip_records: list[dict]) -> None:
    """
    期限切れジョブの R2 ファイルを一括削除する。
    expired_clip_records: Job.clips の値のリスト
    """
    client = _client()
    objects = []
    for clips in expired_clip_records:
        if not clips:
            continue
        for clip in clips:
            for key_field in ("r2_key_9x16", "r2_key_16x9", "r2_key_txt"):
                key = clip.get(key_field)
                if key:
                    objects.append({"Key": key})

    if not objects:
        return

    # 1000件ずつバッチ削除
    for i in range(0, len(objects), 1000):
        client.delete_objects(
            Bucket=_R2_BUCKET,
            Delete={"Objects": objects[i : i + 1000]},
        )
