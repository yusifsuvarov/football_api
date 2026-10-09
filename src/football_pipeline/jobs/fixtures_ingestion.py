import os
from datetime import date, datetime, timezone

from football_pipeline.clients.football_api import fetch_fixtures
from football_pipeline.repositories.postgres_fixtures import upsert_fixtures
from football_pipeline.storage.raw_json import read_raw_payload, save_raw_payload


def fetch_and_save_raw(fixture_dates: list[date]) -> list[dict]:
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        raise RuntimeError("API_FOOTBALL_KEY did not found")

    saved_payloads = []

    for fixture_date in fixture_dates:
        fetched_at = datetime.now(timezone.utc)

        payload = fetch_fixtures(api_key=api_key, fixture_date=fixture_date)

        path = save_raw_payload(payload=payload, fixture_date=fixture_date, fetched_at=fetched_at)

        saved_payloads.append(
            {
                "fixture_date": fixture_date.isoformat(),
                "fetched_at": fetched_at.isoformat(),
                "path": path
            }
        )

    return saved_payloads


def load_raw_files_to_postgres(saved_payloads: list[dict]) -> dict:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL did not found")

    counts = {}

    for saved_payload in saved_payloads:
        fixture_date = saved_payload["fixture_date"]
        fetched_at = datetime.fromisoformat(saved_payload["fetched_at"])

        payload = read_raw_payload(saved_payload["path"])

        count = upsert_fixtures(database_url=database_url, payload=payload, fetched_at=fetched_at)

        counts[fixture_date] = count
        print(f"{fixture_date}: {count} fixtures worked")

    return counts