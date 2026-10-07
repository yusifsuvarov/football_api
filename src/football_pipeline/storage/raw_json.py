import json
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def save_raw_payload(payload: dict, fixture_date: date, fetched_at: datetime) -> None:
    folder = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "api_football"
        / "fixtures"
        / f"ingestion_date={fetched_at.date().isoformat()}"
    )
    folder.mkdir(parents=True, exist_ok=True)

    timestamp = fetched_at.strftime("%Y%m%dT%H%M%SZ")

    path = folder / f"fixtures_{fixture_date.isoformat()}_{timestamp}.json"

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    return str(path)

def read_raw_payload(path: str) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )