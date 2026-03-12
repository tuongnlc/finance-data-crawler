from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_foreign_trade import main

with DAG(
    dag_id='crawl_foreign_trade',
    start_date=datetime(2024, 1, 1),
    schedule='40 20 * * *', # Manual trigger only
    catchup=False,
    tags=['Crawl Foreign Trade'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Foreign Trade!"'
    )

    # Task 2: Python execution
    crawl_price_task = PythonOperator(
        task_id='crawl_foreign_trade_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_foreign_trade.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_price_task