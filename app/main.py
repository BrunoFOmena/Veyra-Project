from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db import ping_postgres
from app.settings import settings
from app.storage import ping_minio

app = FastAPI(title="Veyra", version="0.1.0")


@app.get("/health")
def health() -> JSONResponse:
    postgres = "ok"
    minio = "ok"

    try:
        ping_postgres()
    except Exception:
        postgres = "error"

    try:
        ping_minio()
    except Exception:
        minio = "error"

    ok = postgres == "ok" and minio == "ok"
    payload = {
        "status": "ok" if ok else "degraded",
        "postgres": postgres,
        "minio": minio,
        "bucket": settings.minio_bucket,
    }
    return JSONResponse(content=payload, status_code=200 if ok else 503)
