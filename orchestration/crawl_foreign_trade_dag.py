from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main


with DAG(
    dag_id='2026_09_06_foreign_trade_crawler',
    start_date=datetime(2026, 9, 6),
    schedule=None,
    catchup=False,
    tags=['Foreign Trade', 'Crawler'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Foreign Trade!"'
    )

    # Task 2: Python execution
    crawl_foreign_trade = PythonOperator(
        task_id='crawl_foreign_trade_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_foreign_trade.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_foreign_trade