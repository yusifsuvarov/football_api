-- Databricks notebook source

-- Gold daily league summary quality gate
-- Every check must return 0 failures.

-- COMMAND ----------
CREATE OR REPLACE TEMP VIEW gold_quality_results AS

WITH expected AS (
    SELECT
        match_date,
        league_id,
        league_season,

        COUNT(*) AS total_fixtures,

        SUM(
            CASE
                WHEN status_short IN ('FT', 'AET', 'PEN') THEN 1
                ELSE 0
            END
        ) AS completed_fixtures,

        SUM(
            CASE
                WHEN status_short IN ('FT', 'AET', 'PEN')
                 AND goals_home > goals_away
                THEN 1
                ELSE 0
            END
        ) AS home_wins,

        SUM(
            CASE
                WHEN status_short IN ('FT', 'AET', 'PEN')
                 AND goals_home = goals_away
                THEN 1
                ELSE 0
            END
        ) AS draws,

        SUM(
            CASE
                WHEN status_short IN ('FT', 'AET', 'PEN')
                 AND goals_home < goals_away
                THEN 1
                ELSE 0
            END
        ) AS away_wins

    FROM football_api.silver.fixtures
    GROUP BY
        match_date,
        league_id,
        league_season
),

aggregate_mismatches AS (
    SELECT
        COUNT(*) AS failures
    FROM expected
    FULL OUTER JOIN football_api.gold.daily_league_summary AS gold
        ON expected.match_date = gold.match_date
       AND expected.league_id = gold.league_id
       AND expected.league_season = gold.league_season
    WHERE expected.match_date IS NULL
       OR gold.match_date IS NULL
       OR NOT (expected.total_fixtures <=> gold.total_fixtures)
       OR NOT (expected.completed_fixtures <=> gold.completed_fixtures)
       OR NOT (expected.home_wins <=> gold.home_wins)
       OR NOT (expected.draws <=> gold.draws)
       OR NOT (expected.away_wins <=> gold.away_wins)
)

SELECT
    'null_group_keys' AS check_name,
    COUNT(*) AS failures
FROM football_api.gold.daily_league_summary
WHERE match_date IS NULL
   OR league_id IS NULL
   OR league_season IS NULL

UNION ALL

SELECT
    'duplicate_groups' AS check_name,
    COUNT(*) AS failures
FROM (
    SELECT
        match_date,
        league_id,
        league_season
    FROM football_api.gold.daily_league_summary
    GROUP BY
        match_date,
        league_id,
        league_season
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'invalid_total_fixtures' AS check_name,
    COUNT(*) AS failures
FROM football_api.gold.daily_league_summary
WHERE total_fixtures IS NULL
   OR total_fixtures <= 0

UNION ALL

SELECT
    'mismatched_gold_groups' AS check_name,
    failures
FROM aggregate_mismatches

UNION ALL

SELECT
    'invalid_metric_rows' AS check_name,
    COUNT(*) AS failures
FROM football_api.gold.daily_league_summary
WHERE completed_fixtures < 0
   OR completed_fixtures > total_fixtures
   OR home_wins < 0
   OR draws < 0
   OR away_wins < 0
   OR home_wins + draws + away_wins <> completed_fixtures;

-- COMMAND ----------
SELECT *
FROM gold_quality_results
ORDER BY check_name;

-- COMMAND ----------
SELECT
    assert_true(
        SUM(failures) = 0,
        CONCAT(
            'Gold quality gate failed. Total failures: ',
            CAST(SUM(failures) AS STRING)
        )
    ) AS gold_quality_gate
FROM gold_quality_results;