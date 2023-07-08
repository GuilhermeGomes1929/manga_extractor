from rich.progress import Progress
from epub_service import *
from image_service import *
import concurrent.futures



def main():
    max_workers = 4
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

        chapters_progress = Progress()
        chaps_task = chapters_progress.add_task("[cyan]Baixando...", total=len(chaps))
        chapters_progress.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

            def download_in_threads(chap):
                images = extract_images(url+chap)                
                pages_task = chapters_progress.add_task("[green]Baixando ...", total=len(images))
                if len(images) > 0:

                    for image in images:
                        download_image(image, manga_name)
                        chapters_progress.update(pages_task, advance=1)

                else:
                    print('Não foi possível extrair as imagens dessa url.')
                    print(f'url: {url+chap}')
                chapters_progress.update(chaps_task, advance=1)
                chapters_progress.remove_task(pages_task)
                chapters_progress.refresh()

            results = []
            for result in executor.map(download_in_threads, chaps):
                results.append(result)

            chapters_progress.stop()
            print('Extração finalizada.')
            print(f'{len(results)} capítulos baixados.')
            print('Iniciando criação do ebook')
            initial_chapter = int(input('A partir de qual capítulo você deseja realizar o download? '))
            create_epub(epub_title=manga_name, 
                        language='pt', 
                        author='GuiGomes1929', 
                        identifier=manga_name, 
                        chapters_path=f'downloads/{manga_name}',
                        interval_size=20,
                        initial_chapter=initial_chapter)

    else:
        print('Não foi possível extrair os capítulos dessa url.')
        print(f'url: {url}')
if __name__ == '__main__':
    main()
