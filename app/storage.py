import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.settings import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ping_minio() -> None:
    client = _client()
    try:
        client.head_bucket(Bucket=settings.minio_bucket)
    except ClientError as exc:
        raise RuntimeError(f"minio bucket {settings.minio_bucket} is not reachable") from exc
