from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main


with DAG(
    dag_id='crawl_fs_balance_sheet_type_one',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['Crawl Balance Sheet Type One', 'Product Company'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Balance Sheet Type One!"'
    )

    # Task 2: Python execution
    crawl_balance_sheet = PythonOperator(
        task_id='crawl_balance_sheet_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_fs_balance_sheet_type_1.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_balance_sheet
