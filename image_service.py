import os
import re
from bs4 import BeautifulSoup
import requests


def extract_html(url):

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    else:
        return None

def download_image(image_url, path):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

        filename = image_url.split("/")[-1]
        filename = filename.split(".")[0] + ".png"
        foldername = image_url.split("/")[-2]
        download_path = os.path.join('downloads', path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        folder_path = os.path.join(download_path, foldername)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filepath = os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            return
            
        response = requests.get(image_url, headers=headers)

        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            #print(f'image salva: {filename}')
        else:
            print(f"Falha ao baixar a imagem: {filename}")
    except Exception as e:
        print(f"Erro ao baixar a imagem: {str(e)}")

def extract_images(url):
    images_url = []
    download_page = extract_html(url)
    if download_page:

        div_slider = download_page.find('div', id='slider')
        
        if div_slider:
            tags_a = div_slider.find_all('a', title=re.compile(r'Page \d+'))

            for tag_a in tags_a:
                picture_tag = tag_a.find('picture')

                if picture_tag:
                    source_tag = picture_tag.find('source')

                    if source_tag and 'srcset' in source_tag.attrs:
                        srcset_value = source_tag['srcset']
                        images_url.append(srcset_value)
        else:
            print('A tag <div> com o id "slider" não foi encontrada.')
    return images_url

def extract_chaps(url):
    chaps = []
    chaps_page = extract_html(url)

    div_chapters = chaps_page.find('div', class_='chapters')
    
    if div_chapters:

        divs_pop = div_chapters.find_all('div', id=re.compile(r'pop-\d+'))
        
        for div_pop in divs_pop:
            id = div_pop['id'].split('-')[1]
            tag_a = div_pop.find('a', id=id)
            chaps.append(tag_a.text)
    
    return chaps
