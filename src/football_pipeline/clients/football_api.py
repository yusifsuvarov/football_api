from datetime import date
import requests


API_URL = "https://v3.football.api-sports.io/fixtures"


def fetch_fixtures(api_key: str, fixture_date: date) -> dict:
    response = requests.get(
        API_URL,
        headers={"x-apisports-key": api_key},
        params={"date": fixture_date.isoformat()},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(
            f"API-Football error ({fixture_date}): {payload['errors']}"
        )

    return payload