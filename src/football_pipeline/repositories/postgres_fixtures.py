from datetime import datetime
import psycopg
from football_pipeline.transforms.fixtures import to_row


COLUMNS = [
    "fixture_id", "fixture_referee", "fixture_timezone", "fixture_date",
    "fixture_timestamp", "periods_first", "periods_second",
    "venue_id", "venue_name", "venue_city",
    "status_long", "status_short", "status_elapsed", "status_extra",
    "league_id", "league_name", "league_country", "league_logo", "league_flag",
    "league_season", "league_round", "league_standings",
    "home_team_id", "home_team_name", "home_team_logo", "home_team_winner",
    "away_team_id", "away_team_name", "away_team_logo", "away_team_winner",
    "goals_home", "goals_away",
    "halftime_home", "halftime_away",
    "fulltime_home", "fulltime_away",
    "extratime_home", "extratime_away",
    "penalty_home", "penalty_away",
    "raw_payload", "fetched_at"
]

placeholders = ", ".join(["%s"] * len(COLUMNS))
column_sql = ", ".join(COLUMNS)

updates = ", ".join(
    f"{column} = EXCLUDED.{column}"
    for column in COLUMNS
    if column != "fixture_id"
)

UPSERT_SQL = f"""
    INSERT INTO football.fixtures ({column_sql})
    VALUES ({placeholders})
    ON CONFLICT (fixture_id) DO UPDATE SET
        {updates},
        updated_at = NOW()
"""

def upsert_fixtures(database_url: str, payload: dict, fetched_at: datetime) -> int:
    items = payload.get("response") or []
    rows = [to_row(item, fetched_at) for item in items]

    if not rows:
        return 0

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, rows)

    return len(rows)