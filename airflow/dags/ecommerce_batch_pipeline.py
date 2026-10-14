from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from integrations.ecommerce_reports import export_daily_sales_report, upload_daily_sales_report

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
        bash_command='python /opt/airflow/run_gx_checkpoint.py',
    )

    export_report_task = PythonOperator(
        task_id='export_daily_sales_report',
        python_callable=export_daily_sales_report,
        op_kwargs={
            'output_dir': '/tmp/ecommerce-reports',
            'logical_date': '{{ ds }}',
        },
    )

    def upload_report(**context):
        report_path = context['ti'].xcom_pull(task_ids='export_daily_sales_report')
        if not report_path:
            raise ValueError('Daily Sales export did not return a local path')
        return upload_daily_sales_report(
            report_path,
            logical_date=context['ds'],
            source_run_id=context['run_id'],
        )

    upload_report_task = PythonOperator(
        task_id='upload_daily_sales_report',
        python_callable=upload_report,
    )
    
    end_pipeline = EmptyOperator(task_id='end_pipeline')

    start_pipeline >> ingest_task >> dbt_run_task >> dbt_test_task >> quality_check_task
    quality_check_task >> export_report_task >> upload_report_task >> end_pipeline
