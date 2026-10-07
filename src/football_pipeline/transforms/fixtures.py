from datetime import datetime
from psycopg.types.json import Jsonb

def to_row(item: dict, fetched_at: datetime) -> tuple:
    fixture = item.get("fixture") or {}
    periods = fixture.get("periods") or {}
    venue = fixture.get("venue") or {}
    status = fixture.get("status") or {}
    
    league = item.get("league") or {}

    teams = item.get("teams") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}

    goals = item.get("goals") or {}

    score = item.get("score") or {}
    halftime = score.get("halftime") or {}
    fulltime = score.get("fulltime") or {}
    extratime = score.get("extratime") or {}
    penalty = score.get("penalty") or {}

    return (
        fixture.get("id"),
        fixture.get("referee"),
        fixture.get("timezone"),
        fixture.get("date"),
        fixture.get("timestamp"),
        periods.get("first"),
        periods.get("second"),
        venue.get("id"),
        venue.get("name"),
        venue.get("city"),
        status.get("long"),
        status.get("short"),
        status.get("elapsed"),
        status.get("extra"),
        league.get("id"),
        league.get("name"),
        league.get("country"),
        league.get("logo"),
        league.get("flag"),
        league.get("season"),
        league.get("round"),
        league.get("standings"),
        home.get("id"),
        home.get("name"),
        home.get("logo"),
        home.get("winner"),
        away.get("id"),
        away.get("name"),
        away.get("logo"),
        away.get("winner"),
        goals.get("home"),
        goals.get("away"),
        halftime.get("home"),
        halftime.get("away"),
        fulltime.get("home"),
        fulltime.get("away"),
        extratime.get("home"),
        extratime.get("away"),
        penalty.get("home"),
        penalty.get("away"),
        Jsonb(item),
        fetched_at,
    )