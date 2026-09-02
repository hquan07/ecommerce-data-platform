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

    # Run dbt models to transform raw data to dimensional/fact tables
    dbt_run_task = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    )
    
    # Run dbt data tests
    dbt_test_task = BashOperator(
        task_id='dbt_test_data',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
    )

    quality_check_task = BashOperator(
        task_id='data_quality_check',
        bash_command='python /opt/airflow/gx/run_gx_checkpoint.py',
    )
    
    end_pipeline = EmptyOperator(task_id='end_pipeline')

    start_pipeline >> ingest_task >> dbt_run_task >> dbt_test_task >> quality_check_task >> end_pipeline
