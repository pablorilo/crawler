
from bs4 import BeautifulSoup
import requests

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

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def main():
    BOE_LIBRARY_URL = "https://www.boe.es/biblioteca_juridica/index.php?tipo=C"
    soup = get_soup(BOE_LIBRARY_URL)
    data = extract_data(soup)
    print(data)