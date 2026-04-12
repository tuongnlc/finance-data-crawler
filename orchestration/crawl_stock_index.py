from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main

with DAG(
    dag_id='crawl_stock_index',
    start_date=datetime(2024, 1, 1),
    schedule='30 20 * * *', 
    catchup=False,
    tags=['Crawl Stock Index'],
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Stock Index!"'
    )

    # Task 2: Python execution
    crawl_stock_index = PythonOperator(
        task_id='crawl_stock_index_task',
        python_callable=main,
        op_kwargs={
            "conn_id": "postgres_market_data",
            "url": "crawl_stock_index.yaml",
        },
    )

    start_crawl_dag >> crawl_stock_index
