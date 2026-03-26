from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_vn_index import main

with DAG(
    dag_id='crawl_vn_index',
    start_date=datetime(2024, 1, 1),
    schedule='30 20 * * *', 
    catchup=False,
    tags=['Crawl VN Index'],
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl VN Index!"'
    )

    # Task 2: Python execution
    crawl_price_task = PythonOperator(
        task_id='crawl_vn_index_task',
        python_callable=main,
        op_kwargs={
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_price_task