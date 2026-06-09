from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main


with DAG(
    dag_id='2026_06_10_newspapers_crawler',
    start_date=None,
    schedule=None,
    catchup=False,
    tags=['Newspaper', 'Newspaper Urls', 'Crawler'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Newspapers!"'
    )

    # Task 2: Python execution
    crawl_newspaper_url = PythonOperator(
        task_id='crawl_newspaper_url_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_newspaper_url.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    # Task 3: Crawl Newspaper
    crawl_newspaper = PythonOperator(
        task_id='crawl_newspaper_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_newspaper.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_newspaper_url >> crawl_newspaper
