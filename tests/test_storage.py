from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.storage import ping_minio


def _client_error(code: str = "404") -> ClientError:
    return ClientError(
        {"Error": {"Code": code, "Message": "missing"}},
        "HeadBucket",
    )


def test_ping_minio_ok(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr("app.storage._client", lambda: client)
    ping_minio()
    client.head_bucket.assert_called_once()


def test_ping_minio_wraps_client_error(monkeypatch):
    client = MagicMock()
    client.head_bucket.side_effect = _client_error("404")
    monkeypatch.setattr("app.storage._client", lambda: client)
    with pytest.raises(RuntimeError, match="minio bucket .* is not reachable"):
        ping_minio()


@pytest.mark.parametrize("code", ["403", "404", "500"])
def test_ping_minio_wraps_http_error_codes(code, monkeypatch):
    client = MagicMock()
    client.head_bucket.side_effect = _client_error(code)
    monkeypatch.setattr("app.storage._client", lambda: client)
    with pytest.raises(RuntimeError):
        ping_minio()


def test_ping_minio_propagates_unexpected_errors(monkeypatch):
    client = MagicMock()
    client.head_bucket.side_effect = ConnectionError("refused")
    monkeypatch.setattr("app.storage._client", lambda: client)
    with pytest.raises(ConnectionError, match="refused"):
        ping_minio()


def test_ping_minio_uses_configured_bucket(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr("app.storage._client", lambda: client)
    monkeypatch.setattr("app.storage.settings.minio_bucket", "custom-bronze")
    ping_minio()
    client.head_bucket.assert_called_once_with(Bucket="custom-bronze")
