from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from interfaces.airflow.tasks.pipeline_tasks import (
    fetch_youtube_data,
    load_raw_iceberg,
    load_to_postgres,
    process_clean_data,
    run_dbt_models,
)


with DAG(
    dag_id="youtube_analytics_pipeline",
    description="YouTube data pipeline using Airflow, Spark, Iceberg, PostgreSQL, and dbt",
    start_date=datetime(2024, 1, 1),
    schedule="0 */3 * * *",
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
    tags=["youtube", "analytics", "iceberg", "spark"],
) as dag:
    start = EmptyOperator(task_id="start")

    task_fetch_youtube_data = PythonOperator(
        task_id="fetch_youtube_data",
        python_callable=fetch_youtube_data,
    )

    task_load_raw_iceberg = PythonOperator(
        task_id="load_raw_iceberg",
        python_callable=load_raw_iceberg,
    )

    task_process_clean_data = PythonOperator(
        task_id="process_clean_data",
        python_callable=process_clean_data,
    )

    task_load_to_postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
    )

    task_run_dbt_models = PythonOperator(
        task_id="run_dbt_models",
        python_callable=run_dbt_models,
    )

    end = EmptyOperator(task_id="end")

    (
        start
        >> task_fetch_youtube_data
        >> task_load_raw_iceberg
        >> task_process_clean_data
        >> task_load_to_postgres
        >> task_run_dbt_models
        >> end
    )
