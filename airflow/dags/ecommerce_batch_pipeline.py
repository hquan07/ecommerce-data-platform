from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ecommerce_batch_pipeline',
    default_args=default_args,
    description='Batch pipeline for Olist data (MinIO -> Spark -> Postgres)',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ecommerce', 'batch']
) as dag:

    start_pipeline = EmptyOperator(task_id='start_pipeline')

    # Note: In a production environment with proper Docker routing, 
    # we would use DockerOperator or SparkSubmitOperator.
    # Here we mock the execution steps for Airflow orchestration testing.
    ingest_task = BashOperator(
        task_id='ingest_bronze_layer',
        bash_command='echo "Simulating Data Ingestion..." && sleep 5',
    )

    process_task = BashOperator(
        task_id='process_silver_gold_layer',
        bash_command='echo "Simulating Spark Processing..." && sleep 5',
    )

    quality_check_task = BashOperator(
        task_id='data_quality_check',
        bash_command='echo "Simulating Data Quality Checks..." && sleep 5',
    )
    
    end_pipeline = EmptyOperator(task_id='end_pipeline')

    start_pipeline >> ingest_task >> process_task >> quality_check_task >> end_pipeline
