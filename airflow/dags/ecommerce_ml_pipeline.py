from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ecommerce_data_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ecommerce_ml_pipeline',
    default_args=default_args,
    description='Run Customer Segmentation ML Model',
    schedule_interval='@weekly',
    start_date=datetime(2026, 8, 31),
    catchup=False,
    tags=['ml', 'segmentation'],
) as dag:

    run_segmentation = BashOperator(
        task_id='run_customer_segmentation',
        bash_command='python /opt/airflow/src/ml/customer_segmentation.py',
    )

    run_segmentation
