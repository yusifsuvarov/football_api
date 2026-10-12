from datetime import datetime, timezone
from unittest.mock import MagicMock

from football_pipeline.repositories import postgres_fixtures


def test_upsert_fixtures_sends_rows_to_postgres(monkeypatch):
    fetched_at = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
    payload = {"response": [{"fixture": {"id": 1}}, {"fixture": {"id": 2}}]}
    expected_rows = [("row-1",), ("row-2",)]

    monkeypatch.setattr(
        postgres_fixtures,
        "to_row",
        lambda item, fetched_at: ("row-" + str(item["fixture"]["id"]),),
    )

    cursor = MagicMock()
    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor

    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value = cursor_context

    connect = MagicMock(return_value=connection)
    monkeypatch.setattr(postgres_fixtures.psycopg, "connect", connect)

    result = postgres_fixtures.upsert_fixtures(
        database_url="postgresql://test",
        payload=payload,
        fetched_at=fetched_at,
    )

    assert result == 2
    connect.assert_called_once_with("postgresql://test")
    cursor.executemany.assert_called_once()
    assert cursor.executemany.call_args.args[1] == expected_rows


def test_upsert_fixtures_skips_database_for_empty_response(monkeypatch):
    connect = MagicMock()
    monkeypatch.setattr(postgres_fixtures.psycopg, "connect", connect)

    result = postgres_fixtures.upsert_fixtures(
        database_url="postgresql://test",
        payload={"response": []},
        fetched_at=datetime(2026, 10, 12, tzinfo=timezone.utc),
    )

    assert result == 0
    connect.assert_not_called()
