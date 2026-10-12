from datetime import datetime, timezone

from football_pipeline.transforms.fixtures import to_row


def test_to_row_maps_fixture_fields_and_keeps_raw_payload():
    fetched_at = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)

    item = {
        "fixture": {
            "id": 12345,
            "referee": "Referee Name",
            "timezone": "UTC",
            "date": "2026-10-12T12:00:00+00:00",
            "timestamp": 1791806400,
            "periods": {"first": 100, "second": 200},
            "venue": {"id": 10, "name": "Stadium", "city": "Baku"},
            "status": {
                "long": "Match Finished",
                "short": "FT",
                "elapsed": 90,
                "extra": 5,
            },
        },
        "league": {
            "id": 39,
            "name": "Premier League",
            "country": "England",
            "logo": "league-logo",
            "flag": "england-flag",
            "season": 2026,
            "round": "Regular Season - 1",
            "standings": True,
        },
        "teams": {
            "home": {
                "id": 1,
                "name": "Home Team",
                "logo": "home-logo",
                "winner": True,
            },
            "away": {
                "id": 2,
                "name": "Away Team",
                "logo": "away-logo",
                "winner": False,
            },
        },
        "goals": {"home": 2, "away": 1},
        "score": {
            "halftime": {"home": 1, "away": 0},
            "fulltime": {"home": 2, "away": 1},
            "extratime": {"home": None, "away": None},
            "penalty": {"home": None, "away": None},
        },
    }

    row = to_row(item, fetched_at)

    assert len(row) == 42
    assert row[0] == 12345
    assert row[3] == "2026-10-12T12:00:00+00:00"
    assert row[11] == "FT"
    assert row[14] == 39
    assert row[22] == 1
    assert row[26] == 2
    assert row[30:36] == (2, 1, 1, 0, 2, 1)
    assert row[40].obj == item
    assert row[41] == fetched_at


def test_to_row_handles_missing_nested_fields():
    fetched_at = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)

    row = to_row({}, fetched_at)

    assert len(row) == 42
    assert all(value is None for value in row[:40])
    assert row[40].obj == {}
    assert row[41] == fetched_at