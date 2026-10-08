# Databricks notebook source

# Packages, variables and creating silver schema
from pyspark.sql import functions as F
from delta.tables import DeltaTable

source_table = "football_api.bronze.fixtures"
target_table = "football_api.silver.fixtures"

spark.sql("CREATE SCHEMA IF NOT EXISTS football_api.silver")

# COMMAND ----------

# Build the Silver DataFrame from the Bronze table
bronze_df = spark.table(source_table)

silver_df = (
    bronze_df
    .filter(
        F.col("fixture_id").isNotNull()
        & F.col("fixture_date").isNotNull()
    )
    .select(
        "fixture_id",
        "fixture_date",
        F.to_date("fixture_date").alias("match_date"),
        F.upper(F.trim(F.col("status_short"))).alias("status_short"),
        F.trim(F.col("status_long")).alias("status_long"),
        "league_id",
        "league_name",
        "league_country",
        "league_season",
        "home_team_id",
        F.trim(F.col("home_team_name")).alias("home_team_name"),
        "away_team_id",
        F.trim(F.col("away_team_name")).alias("away_team_name"),
        "goals_home",
        "goals_away",
        "halftime_home",
        "halftime_away",
        "fulltime_home",
        "fulltime_away",
        "venue_name",
        "venue_city",
        "fetched_at",
        "created_at",
        "updated_at",
        "bronze_loaded_at",
        "source_system",
    )
)

# COMMAND ----------

# Create or merge into the Silver table
if not spark.catalog.tableExists(target_table):
    (
        silver_df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(target_table)
    )
else:
    target = DeltaTable.forName(spark, target_table)

    (
        target.alias("target")
        .merge(
            silver_df.alias("source"),
            "target.fixture_id = source.fixture_id",
        )
        .whenMatchedUpdateAll(
            condition="source.updated_at > target.updated_at"
        )
        .whenNotMatchedInsertAll()
        .execute()
    )
