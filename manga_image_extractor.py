import os
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from ebooklib import epub

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
            
        response = requests.get(image_url, headers=headers)

        if response.status_code == 200:

            filepath = os.path.join(folder_path, filename)

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


def create_epub(epub_title, language, author, identifier, chapters_path):
    book = epub.EpubBook()

    book.set_title(epub_title)
    book.set_language(language)
    book.add_author(author)
    book.set_identifier(identifier)

    chapters = get_chapters(chapters_path)

    chapters_ebook = []
    pages = []
    
    for chapter in chapters:
        title = chapter['title']

        page_chapter = epub.EpubHtml(title=title,
                                         file_name=f'{title}.xhtml',
                                         content=f'<h1>{title}</h1>')

        book.add_item(page_chapter)
        chapters_ebook.append(page_chapter)
        pages.append(page_chapter)

        for i, image in enumerate(chapter['images']):
            path = image['path']
            image_epub = epub.EpubImage(
                    file_name=f'{path}',
                    media_type='image/gif',
                    content=image['content']
                )
            container_image = epub.EpubHtml(title=f'Página {i}', file_name=f'{title}-{i}.xhtml')
            container_image.set_content(f'<img src="{path}"/>')
            book.add_item(container_image)
            book.add_item(image_epub)
            pages.append(container_image)

    style = 'body { font-family: Times, Times New Roman, serif; }'

    nav_css = epub.EpubItem(uid="style_nav",
                            file_name="style/nav.css",
                            media_type="text/css",
                            content=style)
    book.add_item(nav_css)

    book.toc = chapters_ebook

    spine = ['nav']
    for page in pages:
        spine.append(page)

    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    if not os.path.exists('epubs'):
        os.makedirs('epubs')

    epub.write_epub(f'epubs/{epub_title}.epub', book)


def get_chapters(chapters_path):
    chapters = []

    for chapters_dir in sorted(os.listdir(chapters_path)):
        chapters_dir_path = os.path.join(chapters_path, chapters_dir)
        if os.path.isdir(chapters_dir_path):
            images = get_images(chapters_dir_path)
            chapters.append({
                'title': f'Capítulo {chapters_dir}',
                'images': images
            })
    return chapters

def get_images(chapter_dir):
    images = []

    for image_file in sorted(os.listdir(chapter_dir)):
        image_path = os.path.join(chapter_dir, image_file)
        if os.path.isfile(image_path):
            with open(image_path, 'rb') as file:
                content = file.read()
                images.append({
                    'path': image_path,
                    'content': content
                })

    return images 

def main():
    manga_name = input('Digite o nome do mangá: ')
    url = input('Digite a url do mangá: ')
    # Para testes
    #url = 'https://mangahosted.com/manga/jujutsu-kaisen-mh41326/'
    print('Iniciando extração de capítulos.')
    chaps = extract_chaps(url)

    if len(chaps) > 0:
        print(f'Foram encontrados {len(chaps)} capítulos.')
        print('Iniciando extração de imagens.')

        for chap in tqdm(chaps, desc='Capítulos', unit='chaps'):

            images = extract_images(url+chap)
            
            if len(images) > 0:

                for image in tqdm(images, desc='Imagens', unit='images'):
                    download_image(image, manga_name)
            else:
                print('Não foi possível extrair as imagens dessa url.')
                print(f'url: {url+chap}')
        
        print('Extração finalizada.')
        print(f'{len(chaps)} capítulos baixados.')
        print('Iniciando criação do ebook')
        create_epub(epub_title=manga_name, language='pt', author='GuiGomes1929', identifier=manga_name, chapters_path=f'downloads/{manga_name}')

    else:
        print('Não foi possível extrair os capítulos dessa url.')
        print(f'url: {url}')

main()