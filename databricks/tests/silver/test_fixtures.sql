-- Databricks notebook source

-- Silver fixtures quality gate
-- Every check must return 0 failures.

CREATE OR REPLACE TEMP VIEW silver_quality_results AS

SELECT
    'null_fixture_id' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE fixture_id IS NULL

UNION ALL

SELECT
    'duplicate_fixture_id' AS check_name,
    COUNT(*) AS failures
FROM (
    SELECT fixture_id
    FROM football_api.silver.fixtures
    GROUP BY fixture_id
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'null_fixture_date' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE fixture_date IS NULL

UNION ALL

SELECT
    'null_match_date' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE match_date IS NULL

UNION ALL

SELECT
    'null_updated_at' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE updated_at IS NULL

UNION ALL

SELECT
    'invalid_match_date' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE match_date <> CAST(fixture_date AS DATE)
   OR match_date IS NULL
   OR fixture_date IS NULL

UNION ALL

SELECT
    'bronze_missing_in_silver' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures AS bronze
LEFT ANTI JOIN football_api.silver.fixtures AS silver
    ON bronze.fixture_id = silver.fixture_id
WHERE bronze.fixture_id IS NOT NULL
  AND bronze.fixture_date IS NOT NULL

UNION ALL

SELECT
    'silver_missing_in_bronze' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures AS silver
LEFT ANTI JOIN football_api.bronze.fixtures AS bronze
    ON silver.fixture_id = bronze.fixture_id

UNION ALL

SELECT
    'unnormalized_status_short' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE status_short <> UPPER(TRIM(status_short))

UNION ALL

SELECT
    'untrimmed_status_long' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE status_long <> TRIM(status_long)

UNION ALL

SELECT
    'untrimmed_home_team_name' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE home_team_name <> TRIM(home_team_name)

UNION ALL

SELECT
    'untrimmed_away_team_name' AS check_name,
    COUNT(*) AS failures
FROM football_api.silver.fixtures
WHERE away_team_name <> TRIM(away_team_name)

UNION ALL

SELECT
    'row_count_mismatch' AS check_name,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM football_api.bronze.fixtures
            WHERE fixture_id IS NOT NULL
              AND fixture_date IS NOT NULL
        ) = (
            SELECT COUNT(*)
            FROM football_api.silver.fixtures
        )
        THEN 0
        ELSE 1
    END AS failures;

-- COMMAND ----------
SELECT *
FROM silver_quality_results
ORDER BY check_name;

-- COMMAND ----------
SELECT
    assert_true(
        SUM(failures) = 0,
        CONCAT(
            'Silver quality gate failed. Total failures: ',
            CAST(SUM(failures) AS STRING)
        )
    ) AS silver_quality_gate
FROM silver_quality_results;