from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding
from rich.columns import Columns
from rich import box

import json

from epub_service import *
from manga_service import *
import concurrent.futures
import curses

console = Console()

def menu():

    console.print(Panel("[bold red]Mangá extractor[/bold red]", style="bold", box=box.ROUNDED))
    console.print()
    console.print("Selecione uma opção:")
    console.print()
    console.print(Padding('[>] 1. Baixar mangá', (0, 2)))
    console.print(Padding('[>] 2. Criar ebook',(0,2)))
    console.print(Padding('[>] 3. Sair', (0,2)))
    console.print()
    return console.input('Digite a opção desejada: ')

def menu_select_manga():

    mangas = os.listdir('downloads')
    console.clear()

    if len(mangas) > 0:
        console.print(Panel("[bold red]Mangá extractor[/bold red]", style="bold", box=box.ROUNDED))
        console.print()
        console.print("Selecione uma opção:")
        console.print()
        for i, name in enumerate(mangas):
            console.print(Padding(f'[>] {i+1}. {name}', (0, 2)))
        console.print()
        manga_chosen = int(console.input('Digite a opção desejada: '))
        return mangas[manga_chosen-1]
    else:
        console.input('[bold]Não há mangás baixados... Pressione qualquer tecla para voltar')
        return None

def main():
    while True:
        functionality = int(menu())
        
        if (functionality == 1):
            download_mangas()
        if (functionality == 2):
            manga_chosen = menu_select_manga()
            if manga_chosen == None:
                pass
            else:
                export_to_epub(manga_chosen)
        if (functionality == 3):
            exit()

def download_mangas():
    main_panel = Panel("[bold red]Extração e download", style="bold", box=box.ROUNDED)
    max_workers = 4
    console.clear()
    url = console.input('[bold red]Digite a url do mangá: ')
    # Para testes
    #url = 'https://mangahosted.com/manga/jujutsu-kaisen-mh41326/'
    console.clear()
    console.print(main_panel)
    console.print(f'[bold red]Url: {url}')
    console.print()
    console.print('[blue]Iniciando a extração de informações...')
    console.print()

    with Progress(transient=True) as progress:
        progress.add_task('[bold blue]Extraindo informações...', start=False, total=None)
        infos = extract_manga_infos(url)
        chaps = infos['chaps']
        manga_name = infos['title']

    if len(infos) > 0:
        console.clear()
        console.print(Panel(f'[bold red]{infos["title"]}', style="bold", box=box.ROUNDED, padding=(1, 2)))
        console.print(Columns(map(lambda x: Panel(f'[magenta]{x}'), infos['tags']), equal=True, expand=False ))
        console.print()
        console.print(Columns([f'[red]Autor: {infos["author"]}', f"[red]Ano de lançamento: {infos['year']}"], equal=True, padding=(0, 6)))
        console.print()
        console.print(f'[red]Url da capa: {infos["cover"]}')
        console.print(f'[red]Foram encontrados [bold]{len(infos["chaps"])}[/bold] capítulos')
        console.print()
        console.input('[red]Pressione qualquer para iniciar o donwload dos capítulos...')
        console.clear()
        console.print(Panel("[bold red]Download das páginas", style="bold", box=box.ROUNDED))
        console.print()

        with Progress(transient=True) as progress:
            progress.add_task('[bold blue]Baixando informações...', start=False, total=None)
            download_cover(infos['cover'], manga_name)
            save_manga_infos(infos)

        chapters_progress = Progress(TextColumn("[progress.description]{task.description}"),
                                        BarColumn(),
                                        TaskProgressColumn(text_format='{task.completed}/{task.total}'),
                                        TimeRemainingColumn(),
                                        transient=True)
        chaps_task = chapters_progress.add_task("[cyan]Baixando...", total=len(chaps))
        chapters_progress.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

            def download_in_threads(chap):
                images = extract_images(url+chap)                
                pages_task = chapters_progress.add_task("[magenta]Baixando ...", total=len(images))
                if len(images) > 0:

                    for image in images:
                        try:
                            download_image(image, manga_name)
                        except Exception as e:
                            progress.console.print(f'[bold red]!!!{e}!!!]')
                        chapters_progress.update(pages_task, advance=1)

                else:
                    progress.console.print(f'[red bold]!!!Capítulo {chap} inválido!!!')
                chapters_progress.update(chaps_task, advance=1)
                chapters_progress.remove_task(pages_task)
                chapters_progress.refresh()

            results = []
            for result in executor.map(download_in_threads, chaps):
                results.append(result)

            chapters_progress.stop()
            console.print()
            console.print('[red]Extração finalizada.')
            console.print(f'[red][bold]{len(results)}[/bold] capítulos baixados.')
            

    else:
        print('[red bold]!!Não foi possível extrair os capítulos dessa url!!!')
        print(f'[red]url:[/red] [white]{url}[/white]')
    console.print()
    console.input('[red]Pressione qualquer tecla para [bold]continuar[/bold]...')
    console.clear()

def export_to_epub(manga_name):

    chapters_path = f'downloads/{manga_name}'
    with open(f'{chapters_path}/infos.json', 'r') as archive:
        json_data = archive.read()
    infos = json.loads(json_data)

    dir_list = os.listdir(chapters_path)
    number_chapters = len([item for item in dir_list if (os.path.isdir(os.path.join(chapters_path, item)) and item != 'cover')])

    console.clear()
    console.print(Panel("[bold red]Criação de epub", style="bold", box=box.ROUNDED))
    console.print()
    console.print(f'[red]Foram encontrados [bold]{number_chapters}[/bold] capítulos.')
    console.print()
    initial_chapter = int(console.input('[red]Capítulo inicial para criação do ebook: '))
    
    with Progress(transient=True) as progress:
        progress.add_task('[bold blue]Criando ebook...', start=False, total=None)
        create_epub(epub_title=manga_name, 
                language='pt', 
                author=infos['author'], 
                identifier=infos['title'], 
                chapters_path=chapters_path,
                interval_size=10,
                initial_chapter=initial_chapter)
    console.print()
    console.print('[bold red]Ebook criado com sucesso')
    console.print()
    console.input('[red]Pressione qualquer tecla para [bold]continuar[/bold]...')
    console.clear()


if __name__ == '__main__':
    main()
