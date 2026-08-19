import psycopg

from app.settings import settings


def ping_postgres() -> None:
    with psycopg.connect(settings.postgres_dsn, connect_timeout=3) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            row = cur.fetchone()
            if row is None or row[0] != 1:
                raise RuntimeError("unexpected postgres ping result")
