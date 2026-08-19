import pytest


@pytest.mark.parametrize(
    ("postgres_ok", "minio_ok", "status_code", "status"),
    [
        (True, True, 200, "ok"),
        (False, True, 503, "degraded"),
        (True, False, 503, "degraded"),
        (False, False, 503, "degraded"),
    ],
)
def test_health_status_matrix(client, monkeypatch, postgres_ok, minio_ok, status_code, status):
    def ping_postgres():
        if not postgres_ok:
            raise RuntimeError("postgres down")

    def ping_minio():
        if not minio_ok:
            raise RuntimeError("minio down")

    monkeypatch.setattr("app.main.ping_postgres", ping_postgres)
    monkeypatch.setattr("app.main.ping_minio", ping_minio)

    response = client.get("/health")
    body = response.json()

    assert response.status_code == status_code
    assert body["status"] == status
    assert body["postgres"] == ("ok" if postgres_ok else "error")
    assert body["minio"] == ("ok" if minio_ok else "error")
    assert body["bucket"] == "veyra-bronze"


def test_health_includes_bucket_from_settings(client, monkeypatch):
    monkeypatch.setattr("app.main.ping_postgres", lambda: None)
    monkeypatch.setattr("app.main.ping_minio", lambda: None)
    monkeypatch.setattr("app.main.settings.minio_bucket", "alt-bronze")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["bucket"] == "alt-bronze"


def test_health_does_not_leak_exception_details(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.ping_postgres",
        lambda: (_ for _ in ()).throw(RuntimeError("dsn=postgresql://veyra:secret@db")),
    )
    monkeypatch.setattr("app.main.ping_minio", lambda: None)

    response = client.get("/health")
    body = response.json()

    assert response.status_code == 503
    assert "secret" not in str(body)
    assert body == {
        "status": "degraded",
        "postgres": "error",
        "minio": "ok",
        "bucket": "veyra-bronze",
    }


def test_unknown_route_is_not_health(client):
    response = client.get("/ready")
    assert response.status_code == 404
