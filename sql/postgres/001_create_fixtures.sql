CREATE SCHEMA IF NOT EXISTS football;

CREATE TABLE IF NOT EXISTS football.fixtures (
    -- fixture
    fixture_id BIGINT PRIMARY KEY,
    fixture_referee TEXT,
    fixture_timezone TEXT,
    fixture_date TIMESTAMPTZ NOT NULL,
    fixture_timestamp BIGINT,
    periods_first BIGINT,
    periods_second BIGINT,

    -- fixture.venue
    venue_id BIGINT,
    venue_name TEXT,
    venue_city TEXT,

    -- fixture.status
    status_long TEXT,
    status_short TEXT,
    status_elapsed SMALLINT,
    status_extra SMALLINT,

    -- league
    league_id BIGINT,
    league_name TEXT,
    league_country TEXT,
    league_logo TEXT,
    league_flag TEXT,
    league_season INTEGER,
    league_round TEXT,
    league_standings BOOLEAN,

    -- teams.home
    home_team_id BIGINT,
    home_team_name TEXT,
    home_team_logo TEXT,
    home_team_winner BOOLEAN,

    -- teams.away
    away_team_id BIGINT,
    away_team_name TEXT,
    away_team_logo TEXT,
    away_team_winner BOOLEAN,

    -- goals
    goals_home INTEGER,
    goals_away INTEGER,

    -- score
    halftime_home INTEGER,
    halftime_away INTEGER,
    fulltime_home INTEGER,
    fulltime_away INTEGER,
    extratime_home INTEGER,
    extratime_away INTEGER,
    penalty_home INTEGER,
    penalty_away INTEGER,

    -- JSON data
    raw_payload JSONB NOT NULL,

    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fixtures_date
    ON football.fixtures (fixture_date);

CREATE INDEX IF NOT EXISTS idx_fixtures_league_season
    ON football.fixtures (league_id, league_season);

CREATE INDEX IF NOT EXISTS idx_fixtures_status
    ON football.fixtures (status_short);