import sys
import os
import time
import requests
import firebase_admin
import google.cloud.logging

from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import storage
from bs4 import BeautifulSoup
from google.cloud.exceptions import GoogleCloudError

from legalia_os.legalia_utils import generate_unique_id, check_gcs_exists,download_and_upload_pdf

BOE_URL = "https://www.boe.es"
BOE_LIBRARY_URL = "https://www.boe.es/biblioteca_juridica/index.php?tipo=C"
BOE_BASE_URL_PDF = "https://www.boe.es/biblioteca_juridica/codigos/"
BOE_LANDING_BUCKET = 'boe-docs-landing'
credentials_file = "/app/credenciales.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file

def create_semaphore(bucket_name, semaphore_filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(semaphore_filename)
    try:
        blob.upload_from_string("", content_type="application/octet-stream")
        print(f"Semaphore created: gs://{bucket_name}/{semaphore_filename}")
    except GoogleCloudError as e:
        print(f"Error creating semaphore: {str(e)}")

def delete_semaphore(bucket_name, semaphore_filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(semaphore_filename)
    blob.delete()
    print(f"Semaphore deleted: gs://{bucket_name}/{semaphore_filename}")

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def extract_data(soup) -> dict:

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

def extract_pdf_from_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the p tag that contains "Última modificación"
    div = soup.find('div', class_ = 'datosPubli')
    # extract the date from the strong tag inside the p tag
    date_modified = div.find('strong').text.strip() if div else None
    

    # find the a tag inside the li tag with class "puntoPDF2"
    a = soup.find('li', class_='puntoPDF2').find('a') if soup.find('li', class_='puntoPDF2') else None

    # extract the href from the a tag
    pdf_url = a.get('href') if a else None
    
    return BOE_BASE_URL_PDF + pdf_url, date_modified

def insert_firestore(url_dict: dict, db, collection:str="BOE") -> None:

    collection_ref = db.collection(collection)

    for title, subcategories in url_dict.items():
        unique_id = generate_unique_id(title)
        doc_ref = collection_ref.document(unique_id)
        doc_ref.set({'title': title})

        for subcategory in subcategories:
            sub_collection_ref = doc_ref.collection('subcategory')
            sub_unique_id = generate_unique_id(subcategory['tit_codigo'])
            sub_doc_ref = sub_collection_ref.document(sub_unique_id)
            sub_doc_ref.set(subcategory)

def main():

    SEMAPHORE_BUCKET = "boe-docs-landing"
    SEMAPHORE_FILENAME = "script_semaphore.lock"

    create_semaphore(SEMAPHORE_BUCKET, SEMAPHORE_FILENAME)

    cred = credentials.Certificate(credentials_file)
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    soup = get_soup(BOE_LIBRARY_URL)
    data = extract_data(soup)

    value = []
    key = "Otros códigos electrónicos"
    res = soup.find_all('div', class_="lista_bloque")
    for li in res[-1].find_all('li', class_='etiqueta'):
        a = li.find('a')  # find the a tag inside the li
        if a:
            # store the text in "tit_codigo" and the href url in a dictionary
            sub_dict = {
                'tit_codigo': a.find('span', class_='tit_codigo').text.strip(),
                'href': a.get('href', '')
            }
            value.append(sub_dict)
    data[key] = value

    for title, subcategories in data.items():

        for subcategory in subcategories:
            # if not "filename" in subcategory or not legalia_utils.check_gcs_exists(BOE_LANDING_BUCKET, subcategory["filename"]):
                url = BOE_URL + subcategory['href']
                pdf_url, date = extract_pdf_from_site(url)
                filename = pdf_url.split("=")[-1]
                subcategory["bucket"] = BOE_LANDING_BUCKET
                subcategory["filename"] = filename
                subcategory["last_modified"] =  date
                if not check_gcs_exists(BOE_LANDING_BUCKET, subcategory["filename"]):
                    print("Downloading and pushing to gcs: " + filename)
                    download_and_upload_pdf(pdf_url, BOE_LANDING_BUCKET, filename)
                    time.sleep(3)
                else:
                    print("Already exists in GCS: " + subcategory["filename"])

    insert_firestore(url_dict=data, db=db)

    delete_semaphore(SEMAPHORE_BUCKET, SEMAPHORE_FILENAME)
    
if __name__ == "__main__":
    main()


