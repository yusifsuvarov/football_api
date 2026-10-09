from datetime import date, datetime, timezone

import pytest

from football_pipeline.jobs import fixtures_ingestion


def test_fetch_and_save_raw_requires_api_key(monkeypatch):
    monkeypatch.delenv("API_FOOTBALL_KEY", raising=False)

    with pytest.raises(RuntimeError, match="API_FOOTBALL_KEY did not found"):
        fixtures_ingestion.fetch_and_save_raw([date(2026, 10, 9)])


def test_fetch_and_save_raw_saves_each_date(monkeypatch):
    monkeypatch.setenv("API_FOOTBALL_KEY", "test-api-key")

    requested_dates = [
        date(2026, 10, 8),
        date(2026, 10, 9),
    ]
    fetched_dates = []
    saved_dates = []

    def fake_fetch_fixtures(*, api_key, fixture_date):
        assert api_key == "test-api-key"
        fetched_dates.append(fixture_date)
        return {"response": []}

    def fake_save_raw_payload(*, payload, fixture_date, fetched_at):
        assert payload == {"response": []}
        assert fetched_at.tzinfo == timezone.utc
        saved_dates.append(fixture_date)
        return f"raw/{fixture_date}.json"

    monkeypatch.setattr(
        fixtures_ingestion, "fetch_fixtures", fake_fetch_fixtures
    )
    monkeypatch.setattr(
        fixtures_ingestion, "save_raw_payload", fake_save_raw_payload
    )

    result = fixtures_ingestion.fetch_and_save_raw(requested_dates)

    assert fetched_dates == requested_dates
    assert saved_dates == requested_dates
    assert [item["fixture_date"] for item in result] == [
        "2026-10-08",
        "2026-10-09",
    ]
    assert [item["path"] for item in result] == [
        "raw/2026-10-08.json",
        "raw/2026-10-09.json",
    ]
    assert all(
        datetime.fromisoformat(item["fetched_at"]).tzinfo is not None
        for item in result
    )


def test_load_raw_files_to_postgres_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL did not found"):
        fixtures_ingestion.load_raw_files_to_postgres([])


def test_load_raw_files_to_postgres_reads_and_upserts_payload(
    monkeypatch,
):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")

    saved_payloads = [
        {
            "fixture_date": "2026-10-09",
            "fetched_at": "2026-10-09T12:00:00+00:00",
            "path": "raw/2026-10-09.json",
        }
    ]
    raw_payload = {"response": [{"fixture": {"id": 123}}]}
    read_paths = []
    upsert_calls = []

    def fake_read_raw_payload(path):
        read_paths.append(path)
        return raw_payload

    def fake_upsert_fixtures(*, database_url, payload, fetched_at):
        upsert_calls.append((database_url, payload, fetched_at))
        return 1

    monkeypatch.setattr(
        fixtures_ingestion, "read_raw_payload", fake_read_raw_payload
    )
    monkeypatch.setattr(
        fixtures_ingestion, "upsert_fixtures", fake_upsert_fixtures
    )

    result = fixtures_ingestion.load_raw_files_to_postgres(saved_payloads)

    assert read_paths == ["raw/2026-10-09.json"]
    assert result == {"2026-10-09": 1}
    assert upsert_calls == [
        (
            "postgresql://test",
            raw_payload,
            datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc),
        )
    ]