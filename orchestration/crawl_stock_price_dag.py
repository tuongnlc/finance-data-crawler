from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main

with DAG(
    dag_id='2026_06_09_stock_price_crawler',
    start_date=datetime(2026, 6, 9),
    schedule=None,
    catchup=False,
    tags=['Stock Price', 'Crawler'],
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Stock Price!"'
    )

    # Task 2: Python execution
    crawl_price_task = PythonOperator(
        task_id='crawl_stock_price_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_stock_price.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_price_task