from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from orchestration.python_script.crawl_market_data_v1 import main


with DAG(
    dag_id='crawl_fs_cash_flow_statement_type_four',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['Crawl Cash Flow Statement Type Four', 'Bank', 'Cash Flow Statement', 'Financial Statement'],   
) as dag:
    # Task 1: Bash execution
    start_crawl_dag = BashOperator(
        task_id='start_crawl_dag',
        bash_command='echo "Start Crawl Cash Flow Statement Type Four!"'
    )

    # Task 2: Python execution
    crawl_cash_flow_statement = PythonOperator(
        task_id='crawl_cash_flow_statement_task',
        python_callable=main,
        op_kwargs={
            "url": "crawl_fs_cash_flow_statement_type_4.yaml",
            "conn_id": "postgres_market_data"
        },
    )

    start_crawl_dag >> crawl_cash_flow_statement
