from tqdm import tqdm
from epub_service import *
from image_service import *

def main():
    manga_name = input('Digite o nome do mangá: ')
    url = input('Digite a url do mangá: ')
    # Para testes
    #url = 'https://mangahosted.com/manga/jujutsu-kaisen-mh41326/'
    print('Iniciando extração de capítulos.')
    chaps = extract_chaps(url)

    if len(chaps) > 0:
        print(f'Foram encontrados {len(chaps)} capítulos.')
        print('O programa se encarrega de baixar todos os capítulos que não foram baixados ainda.')
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