-- Databricks notebook source
CREATE CATALOG IF NOT EXISTS football_api;

CREATE SCHEMA IF NOT EXISTS football_api.bronze;

-- COMMAND ----------
-- Load data from Neon PostgreSQL into the Bronze layer
CREATE TABLE IF NOT EXISTS football_api.bronze.fixtures
USING DELTA
AS
SELECT
    source.*,
    CURRENT_TIMESTAMP() AS bronze_loaded_at,
    'neon_postgres' AS source_system
FROM neon_football_postgres_catalog.football.fixtures as source;

-- COMMAND ----------
-- Merge datas from Neon Postgres into bronze layer
MERGE INTO football_api.bronze.fixtures AS target
USING (
    SELECT
        source.*,
        current_timestamp() AS bronze_loaded_at,
        'neon_postgres' AS source_system
    FROM neon_football_postgres_catalog.football.fixtures AS source
    WHERE source.updated_at >= (
        SELECT COALESCE(
            MAX(updated_at) - INTERVAL 3 DAYS,
            TIMESTAMP '1900-01-01 00:00:00'
        )
        FROM football_api.bronze.fixtures
    )
) AS incoming
ON target.fixture_id = incoming.fixture_id

WHEN MATCHED
    AND incoming.updated_at > target.updated_at
THEN UPDATE SET *

WHEN NOT MATCHED
THEN INSERT *;
