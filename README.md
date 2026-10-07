# Football Fixtures Data Pipeline

An end-to-end data engineering project that collects football fixtures from API-Football, loads them into Neon PostgreSQL with Apache Airflow, and builds Bronze, Silver, and Gold Delta tables in Databricks.

## Architecture

```text
API-Football
     │
     ▼
Apache Airflow DAG
     ├── Raw JSON files
     └── Neon PostgreSQL: football.fixtures
                          │
                          ▼
                 Databricks foreign catalog
                          │
                          ▼
          Bronze → Silver → Gold Delta tables

Data layers
- Bronze — copies fixture data from the Neon PostgreSQL source and merges new or updated records.
- Silver — cleans and standardizes fixture data using PySpark.
- Gold — creates daily league-level summaries using Spark SQL.
Technology stack
- Python
- Apache Airflow
- Docker Compose
- PostgreSQL / Neon
- Databricks
- PySpark, Spark SQL, Delta Lake
- API-Football

.
├── dags/
│   └── football_fixtures_dag.py
├── data/
│   └── raw/
├── databricks/
│   └── notebooks/
│       ├── bronze/
│       │   └── 01_bronze_fixtures.sql
│       ├── silver/
│       │   └── 01_silver_fixtures.py
│       └── gold/
│           └── 01_gold_summary.py
├── sql/
│   └── postgres/
│       └── 001_create_fixtures.sql
├── src/
│   └── football_pipeline/
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt

Prerequisites
- Docker Desktop with Docker Compose
- An API-Football API key
- A Neon PostgreSQL database
- A Databricks workspace with permission to create or use Unity Catalog objects
Configuration
Create a local .env file in the project root. Add the required values:
API_FOOTBALL_KEY=your_api_football_key
DATABASE_URL=your_neon_postgresql_connection_string

Never commit .env or real credentials to Git. Use .env.example with placeholder values when sharing the project.

Run Airflow locally
Start the services:
docker compose up -d
Open the Airflow UI at:
http://localhost:8080

Trigger the football_fixtures_to_neon DAG and check that its tasks complete successfully.
To stop the services:
docker compose down

Databricks setup
The Neon PostgreSQL connection and its foreign catalog must be configured in Unity Catalog. The SQL and notebook files in this repository use that catalog to read the source table.
The notebooks create or update these target tables:
football_api.bronze.fixtures
football_api.silver.fixtures
football_api.gold.daily_league_summary

Open and run the notebooks in this order:
1. databricks/notebooks/bronze/01_bronze_fixtures.sql
2. databricks/notebooks/silver/01_silver_fixtures.py
3. databricks/notebooks/gold/01_gold_summary.py
The Unity Catalog connection, credentials, and required permissions are environment-specific and are not included in the repository.
Data quality checks
After running the pipeline, verify that:
- fixture_id is populated and unique.
- fixture_date is populated.
- Bronze and Neon record counts are consistent.
- Silver contains the expected cleaned fixture records.
- Gold summaries contain sensible match and goal totals.
Security
- Do not commit .env, API keys, database URLs, or passwords.
- Keep local raw data and logs out of Git unless a small sanitized sample is intentionally added.
- Grant Databricks connection and catalog access only to users who need it.

