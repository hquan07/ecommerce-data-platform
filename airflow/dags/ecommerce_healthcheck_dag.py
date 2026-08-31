from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def healthcheck():
    print("E-commerce Data Platform DAG is healthy.")


with DAG(
    dag_id="ecommerce_healthcheck",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ecommerce", "mvp"],
) as dag:
    PythonOperator(task_id="healthcheck", python_callable=healthcheck)
