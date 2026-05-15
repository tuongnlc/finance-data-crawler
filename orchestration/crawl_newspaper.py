from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main


with DAG(
    dag_id='crawl_newspaper',
    start_date=datetime(2024, 1, 1),
    schedule='05 21 * * *', # Manual trigger only
    catchup=False,
    tags=['Newspaper'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Newspaper!"'
    )

    # Task 2: Python execution
    crawl_newspaper = PythonOperator(
        task_id='crawl_newspaper_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_newspaper.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_newspaper
