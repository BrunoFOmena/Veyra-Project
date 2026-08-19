import pytest
from pydantic import ValidationError

from app.settings import Settings


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_default_postgres_dsn():
    settings = _settings()
    assert settings.postgres_dsn == "postgresql://veyra:veyra@postgres:5432/veyra"


def test_dsn_percent_encodes_special_characters_in_password():
    settings = _settings(postgres_password="p@ss:w/rd")
    assert settings.postgres_dsn == "postgresql://veyra:p%40ss%3Aw%2Frd@postgres:5432/veyra"


def test_dsn_percent_encodes_special_characters_in_user():
    settings = _settings(postgres_user="veyra@ops")
    assert settings.postgres_dsn == "postgresql://veyra%40ops:veyra@postgres:5432/veyra"


def test_minio_url_uses_http_when_insecure():
    settings = _settings(minio_secure=False)
    assert settings.minio_url == "http://minio:9000"


def test_minio_url_uses_https_when_secure():
    settings = _settings(minio_secure=True, minio_endpoint="minio.internal:9000")
    assert settings.minio_url == "https://minio.internal:9000"


def test_env_overrides_host_and_bucket(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("MINIO_BUCKET", "other-bronze")
    settings = Settings(_env_file=None)
    assert settings.postgres_host == "localhost"
    assert settings.minio_bucket == "other-bronze"


@pytest.mark.parametrize("port", [1, 5432, 65535])
def test_postgres_port_accepts_valid_boundaries(port):
    settings = _settings(postgres_port=port)
    assert settings.postgres_port == port


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_postgres_port_rejects_out_of_range(port):
    with pytest.raises(ValidationError):
        _settings(postgres_port=port)


def test_empty_host_still_builds_dsn():
    settings = _settings(postgres_host="")
    assert settings.postgres_dsn == "postgresql://veyra:veyra@:5432/veyra"


def test_extra_env_is_ignored(monkeypatch):
    monkeypatch.setenv("UNKNOWN_FLAG", "1")
    settings = Settings(_env_file=None)
    assert not hasattr(settings, "unknown_flag")
