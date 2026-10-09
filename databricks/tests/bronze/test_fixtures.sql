-- Databricks notebook source

-- Bronze fixtures quality gate
-- Every check must return 0 failures.


CREATE OR REPLACE TEMP VIEW bronze_quality_results AS

SELECT
    'null_fixture_id' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures
WHERE fixture_id IS NULL

UNION ALL

SELECT
    'duplicate_fixture_id' AS check_name,
    COUNT(*) AS failures
FROM (
    SELECT fixture_id
    FROM football_api.bronze.fixtures
    GROUP BY fixture_id
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'null_updated_at' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures
WHERE updated_at IS NULL

UNION ALL

SELECT
    'row_count_mismatch' AS check_name,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM neon_football_postgres_catalog.football.fixtures
        ) = (
            SELECT COUNT(*)
            FROM football_api.bronze.fixtures
        )
        THEN 0
        ELSE 1
    END AS failures

UNION ALL

SELECT
    'source_missing_in_bronze' AS check_name,
    COUNT(*) AS failures
FROM neon_football_postgres_catalog.football.fixtures AS source
LEFT ANTI JOIN football_api.bronze.fixtures AS bronze
    ON source.fixture_id = bronze.fixture_id

UNION ALL

SELECT
    'bronze_missing_in_source' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures AS bronze
LEFT ANTI JOIN neon_football_postgres_catalog.football.fixtures AS source
    ON bronze.fixture_id = source.fixture_id

UNION ALL

SELECT
    'updated_at_mismatch' AS check_name,
    COUNT(*) AS failures
FROM neon_football_postgres_catalog.football.fixtures AS source
INNER JOIN football_api.bronze.fixtures AS bronze
    ON source.fixture_id = bronze.fixture_id
WHERE NOT (source.updated_at <=> bronze.updated_at)

UNION ALL

SELECT
    'null_bronze_loaded_at' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures
WHERE bronze_loaded_at IS NULL

UNION ALL

SELECT
    'invalid_source_system' AS check_name,
    COUNT(*) AS failures
FROM football_api.bronze.fixtures
WHERE source_system IS NULL
   OR source_system <> 'neon_postgres';

-- COMMAND ----------

SELECT *
FROM bronze_quality_results
ORDER BY check_name;

-- COMMAND ----------

SELECT
    assert_true(
        SUM(failures) = 0,
        CONCAT(
            'Bronze quality gate failed. Total failures: ',
            CAST(SUM(failures) AS STRING)
        )
    ) AS bronze_quality_gate
FROM bronze_quality_results;