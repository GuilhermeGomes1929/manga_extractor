import os
import re
from time import sleep
from bs4 import BeautifulSoup
import requests
from rich import print
import json


def extract_html(url):

    tries = 0

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    while tries <= 5:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        else:
            tries += 1
        sleep(0.5)
        
    return None
    
def download_cover(image_url, path):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

        tries = 0
        filename = "cover.jpg"
        foldername = 'cover'
        download_path = os.path.join('downloads', path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        folder_path = os.path.join(download_path, foldername)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filepath = os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            return

        while tries <= 3:
            response = requests.get(image_url, headers=headers)

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                    return
            else:
                tries += 1
            
            if(response.status_code != 200 and tries >= 3):
                raise Exception(f'Erro ao baixar imagem: {image_url}')
            sleep(0.5)
            
    except Exception as e:
        raise e

def download_image(image_url, path):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

        tries = 0
        filename = image_url.split("/")[-1]
        filename = filename.split(".")[0] + ".jpg"
        foldername = image_url.split("/")[-2]
        download_path = os.path.join('downloads', path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        folder_path = os.path.join(download_path, foldername)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filepath = os.path.join(folder_path, f'{foldername}_{filename}')
        if os.path.exists(filepath):
            return

        while tries <= 3:
            response = requests.get(image_url, headers=headers)

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                    return
            else:
                tries += 1
            
            if(response.status_code != 200 and tries >= 3):
                raise Exception(f'Erro ao baixar imagem: {image_url}')
            sleep(0.5)
            
    except Exception as e:
        raise e

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
                    img_tag = picture_tag.find('img')

                    if img_tag and 'src' in img_tag.attrs:
                        src_value = img_tag['src']
                        images_url.append(src_value)
                else:
                    img_tag = tag_a.find('img')

                    if img_tag and 'src' in img_tag.attrs:
                        src_value = img_tag['src']
                        images_url.append(src_value)
        else:
            print('A tag <div> com o id "slider" não foi encontrada.')
    else: 
        print('Não foi possível baixar a página')
    return images_url


def save_manga_infos(infos):
    json_data = json.dumps(infos, indent=4)

    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    filename = "infos.json"
    foldername = infos['title']
    folder_path = os.path.join('downloads', foldername)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    filepath = os.path.join(folder_path, filename)
    if os.path.exists(filepath):
        return

    with open(filepath, 'w') as archive:
        archive.write(json_data)
    


def extract_manga_infos(url):
    main_page = extract_html(url)
    info_div = main_page.find("div", class_="xlkai alert alert-left w-row")

    infos = {}
    infos["status"] = info_div.find("strong", text="Status: ").next_sibling.strip()
    infos["author"] = info_div.find("strong", text="Autor: ").next_sibling.strip()
    infos["year"] = info_div.find("strong", text="Ano: ").next_sibling.strip()
    infos['chaps'] = extract_chaps(main_page)
    infos['title'] = extract_manga_title(main_page)
    infos['tags'] = extract_manga_tags(main_page)
    infos['cover'] = extract_manga_cover_url(main_page)

    return infos

def extract_manga_cover_url(page):
    container_div = page.find("div", class_="w-col w-col-3")
    img_element = container_div.find('img')
    return img_element['src']

def extract_manga_title(page):
    article = page.find('article')
    h1_title = article.find('h1', class_='title')
    return h1_title.text

def extract_manga_tags(page):
    manga_tags = []
    article = page.find('article')
    div_tags = article.find('div', class_='tags')
    tags = div_tags.find_all('a', class_='tag')
    for tag in tags:
        manga_tags.append(tag.text)
    return manga_tags

def extract_chaps(page):
    chaps = []

    div_chapters = page.find('div', class_='chapters')
    
    if div_chapters:

        divs_pop = div_chapters.find_all('div', id=re.compile(r'pop-\d+'))
        
        for div_pop in divs_pop:
            id = div_pop['id'].split('-')[1]
            tag_a = div_pop.find('a', id=id)
            chaps.append(tag_a.text)
    
    return chaps
