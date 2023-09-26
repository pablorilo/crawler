from datetime import timedelta, datetime
from airflow import DAG

from airflow.operators.python_operator import PythonOperator

from bs4 import BeautifulSoup
import requests


BOE_LIBRARY_URL = "https://www.boe.es/biblioteca_juridica/index.php?tipo=C" 
def extract_data(**kwargs) -> dict:
    soup = kwargs[0]
    # dictionary to store the results
    result_dict = {}

    # find all the h4 tags and the ul tag that follows it
    for h4 in soup.find_all('h4'):
        key = h4.text.strip()  # store the text in h4 as the key
        ul = h4.find_next_sibling('ul')
        
        # check if the ul tag exists and has the correct id
        if ul and ul.get('id', '').startswith('lista_bloque'):
            value = []  # list to store the dictionaries for the current key

            # find all li tags with class "etiqueta"
            for li in ul.find_all('li', class_='etiqueta'):
                a = li.find('a')  # find the a tag inside the li
                if a:
                    # store the text in "tit_codigo" and the href url in a dictionary
                    sub_dict = {
                        'tit_codigo': a.find('span', class_='tit_codigo').text.strip(),
                        'href': a.get('href', '')
                    }
                    value.append(sub_dict)

            result_dict[key] = value
    return result_dict

def get_soup(**kwargs):
    url = kwargs[0]
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

default_args ={
    'owner': 'airflow',
    'email' : ['pablo@cicerai.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
dag = DAG('crawler_boe',
          description= 'crawler BOW',
          default_args= default_args,
          start_date=datetime(2023, 9, 26),
          catchup=False,
          tags=['crawler'])

get_soup_task  = PythonOperator(
    task_id ='get_soup',
    python_callable = get_soup,
    params={'url': BOE_LIBRARY_URL},
    provide_context=True,
    dag = dag
)

extract_data_task  = PythonOperator(
    task_id ='crawler_on',
    python_callable = extract_data,
    params={'BOE_LIBRARY_URL': BOE_LIBRARY_URL},
    templates_dict={'get_soup_result': "{{ task_instance.xcom_pull(task_ids='get_soup') }}"}, 
    dag = dag
)

get_soup_task >> extract_data_task