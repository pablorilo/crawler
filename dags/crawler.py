from datetime import timedelta
from airflow import DAG

from airflow.operators.python_operator import PythonOperator

from utils.main import extract_data, get_soup

BOE_LIBRARY_URL = "https://www.boe.es/biblioteca_juridica/index.php?tipo=C" 

default_args ={
    'owner': 'airflow',
    'email' : ['pablo@cicerai.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
dag = DAG('crawler BOE',
          description= 'crawler BOW',
          default_args= default_args,
          catchup=False,
          tags=['crawler'])

get_soup = PythonOperator(
    task_id ='get_soup',
    python_callable = get_soup,
    op_args=[BOE_LIBRARY_URL]
    dag = dag
)
