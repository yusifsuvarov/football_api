from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


from football_pipeline.jobs.fixtures_ingestion import fetch_and_save_raw, load_raw_files_to_postgres


def determine_fixture_dates(**context):
    run_date = (context["data_interval_end"].in_timezone("Asia/Baku").date())

    return [
        run_date - timedelta(days=1), 
        run_date,
        run_date + timedelta(days=1)
    ]


def run_fetch_task(**context):
    fixture_dates = determine_fixture_dates(**context)
    return fetch_and_save_raw(fixture_dates)


def run_load_task(**context):
    task_instance = context["ti"]

    saved_payloads = task_instance.xcom_pull(task_ids="fetch_and_save_raw")

    return load_raw_files_to_postgres(saved_payloads)


with DAG(
    dag_id="football_fixtures_to_neon",
    description="Insert API-Football to Neon PostgreSQL",
    schedule="0 3 * * *",
    start_date=pendulum.datetime(2026, 10, 3, tz="Asia/Baku"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5)
    },
    tags=["football", "api", "neon"]
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_and_save_raw",
        python_callable=run_fetch_task
    )

    load_task = PythonOperator(
        task_id="load_raw_to_postgres",
        python_callable=run_load_task
    )

    fetch_task >> load_task






# from datetime import timedelta

# import pendulum
# from airflow import DAG
# from airflow.operators.python import PythonOperator

# from football_pipeline.ingestion import ingest_fixture_dates


# def run_daily_ingestion(**context):
#     # Günlük çalışmanın bitiş tarihini Bakü saat diliminde al.
#     run_date = context["data_interval_end"].in_timezone("Asia/Baku").date()

#     # Dünkü maçların sonuçlarını güncelle; bugünü ve yarını da al.
#     dates_to_fetch = [
#         run_date - timedelta(days=1),
#         run_date,
#         run_date + timedelta(days=1),
#     ]

#     return ingest_fixture_dates(dates_to_fetch)


# with DAG(
#     dag_id="football_fixtures_to_neon",
#     description="Adding and Updating API-Football data to Neon PostgreSQL",
#     schedule="0 3 * * *",
#     start_date=pendulum.datetime(2026, 10, 3, tz="Asia/Baku"),
#     catchup=False,
#     max_active_runs=1,
#     default_args={
#         "retries": 2,
#         "retry_delay": timedelta(minutes=5),
#     },
#     tags=["football", "api", "neon"],
# ) as dag:
#     ingest_fixtures = PythonOperator(
#         task_id="fetch_and_upsert_fixtures",
#         python_callable=run_daily_ingestion,
#     )
