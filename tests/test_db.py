from unittest.mock import MagicMock

import pytest

from app.db import ping_postgres


def _connect_returning(row, monkeypatch):
    cursor = MagicMock()
    cursor.fetchone.return_value = row
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    conn_cm = MagicMock()
    conn_cm.__enter__.return_value = conn
    monkeypatch.setattr("app.db.psycopg.connect", lambda *args, **kwargs: conn_cm)
    return cursor, conn_cm


def test_ping_postgres_ok(monkeypatch):
    _connect_returning((1,), monkeypatch)
    ping_postgres()


def test_ping_postgres_uses_connect_timeout(monkeypatch):
    captured = {}

    def fake_connect(*args, **kwargs):
        captured["kwargs"] = kwargs
        cursor = MagicMock()
        cursor.fetchone.return_value = (1,)
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        conn_cm = MagicMock()
        conn_cm.__enter__.return_value = conn
        return conn_cm

    monkeypatch.setattr("app.db.psycopg.connect", fake_connect)
    ping_postgres()
    assert captured["kwargs"]["connect_timeout"] == 3


def test_ping_postgres_rejects_empty_result(monkeypatch):
    _connect_returning(None, monkeypatch)
    with pytest.raises(RuntimeError, match="unexpected postgres ping result"):
        ping_postgres()


@pytest.mark.parametrize("row", [(0,), (2,), ("1",)])
def test_ping_postgres_rejects_non_one_payload(row, monkeypatch):
    _connect_returning(row, monkeypatch)
    with pytest.raises(RuntimeError, match="unexpected postgres ping result"):
        ping_postgres()


def test_ping_postgres_propagates_connection_errors(monkeypatch):
    monkeypatch.setattr(
        "app.db.psycopg.connect",
        lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError("connection timed out")),
    )
    with pytest.raises(TimeoutError, match="connection timed out"):
        ping_postgres()
