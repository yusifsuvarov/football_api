# RUN ---------- 
spark.sql("CREATE SCHEMA IF NOT EXISTS football_api.gold")

# RUN ---------- 
spark.sql("""
CREATE OR REPLACE TABLE football_api.gold.daily_league_summary
USING DELTA
AS
SELECT
    match_date,
    league_id,
    league_name,
    league_country,
    league_season,

    COUNT(*) AS total_fixtures,

    SUM(
        CASE
            WHEN status_short IN('FT', 'AET', 'PEN') THEN 1
            ELSE 0
        END
    ) AS completed_fixtures,

    SUM(
        CASE
            WHEN status_short IN ('FT', 'AET', 'PEN')
            AND goals_home > goals_away THEN 1
            ELSE 0
        END
    ) AS home_wins,

    SUM(
        CASE
            WHEN status_short IN ('FT', 'AET', 'PEN')
            AND goals_home = goals_away THEN 1
            ELSE 0
        END
    ) AS draws,

    SUM(
        CASE
            WHEN status_short IN ('FT', 'AET', 'PEN')
            AND goals_home < goals_away THEN 1
            ELSE 0
        END
    ) AS away_wins,

    SUM(
        CASE
            WHEN status_short IN ('FT', 'AET', 'PEN')
            THEN COALESCE(goals_home, 0) + COALESCE(goals_away, 0)
            ELSE 0
        END
    ) AS total_goals,

    AVG(
        CASE
            WHEN status_short IN ('FT', 'AET', 'PEN')
            AND goals_home IS NOT NULL
            AND goals_away IS NOT NULL
            THEN CAST(goals_home + goals_away AS DOUBLE)
        END
    ) AS average_goals_per_completed_fixture

    FROM football_api.silver.fixtures
    GROUP BY
        match_date,
        league_id,
        league_name,
        league_country,
        league_season
""")

# RUN ---------- 
display(
    spark.table("football_api.gold.daily_league_summary")
    .orderBy("match_date", "league_name")
)