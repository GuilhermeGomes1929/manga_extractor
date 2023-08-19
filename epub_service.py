from ebooklib import epub
import os

import os

def create_epub(epub_title, language, author, identifier, chapters_path, interval_size, initial_chapter):
    intervals = get_chapters(chapters_path, interval_size, initial_chapter)
    for interval in intervals:
    
        book = epub.EpubBook()
    
        book.set_title(epub_title)
        book.set_language(language)
        book.add_author(author)
        book.set_identifier(identifier)
        book.set_cover('cover.jpg', open(f'{chapters_path}/cover/cover.jpg', 'rb').read())

        chapters_ebook = []
        pages = []

        page_style = '''
            body { 
                margin: 0; 
                padding:0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                overflow: hidden;
            } 
            img { 
                width: 100%; 
                height: 100%; 
                object-fit: fill;
            }
        
        '''

        page_css = epub.EpubItem(uid="page_styles",
                                file_name="page.css",
                                media_type="text/css",
                                content=page_style)
        book.add_item(page_css)
        
        chapter_style = '''
            body {
                margin: 0;
                padding: 0;
                text-align: center;
                height: 100%;
                width: 100%;
                vertical-align: middle;
                overflow: hidden;
            }

            img {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: fill;
                pointer-events: none;
                opacity: 0.3;
            }

            h1 {
                text-align: center;
                font-size: 50px;
                font-family: 'Impact'
                margin-top: 40vh;
                background-color: white;
                padding: 20px;
                color: black;
                display: inline-block;
                opacity: 1.0;
                position: relative;
                z-index: 1; 
                border-radius: 10px;
            }
        '''

        chapter_css = epub.EpubItem(uid="style_chapter",
                                file_name="chapter.css",
                                media_type="text/css",
                                content=chapter_style)
        book.add_item(chapter_css)

        chap_cover_epub = epub.EpubImage(
                        uid='chap_cover',
                        file_name='chap_cover.jpg',
                        media_type='image/jpeg',
                        content=open(f'{chapters_path}/cover/cover.jpg', 'rb').read()
                    )
        book.add_item(chap_cover_epub)
        
        for chapter in interval:
            title = chapter['title']

            page_chapter = epub.EpubHtml(title=title,
                                            file_name=f'{title}.xhtml',
                                            content=f'<img src="chap_cover.jpg" alt="chap_cover"><h1>{title}</h1>')

            
            page_chapter.add_item(chapter_css)
            book.add_item(page_chapter)
            chapters_ebook.append(page_chapter)
            pages.append(page_chapter)

            images = get_images(chapter['chapter_path'])

            for i, image in enumerate(images):
                path = image['path'].split("\\")[-1]
                image_epub = epub.EpubImage(
                        uid=path,
                        file_name=f'{path}',
                        media_type='image/jpeg',
                        content=image['content']
                    )
                container_image = epub.EpubHtml(uid=f'{title}_{i}',title=f'Página {i}', file_name=f'{title}-{i}.xhtml')
                container_image.set_content(f'<img src="{path}"/>')
                
                container_image.add_item(page_css)
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
        if not os.path.exists(f'epubs/{epub_title}'):
            os.makedirs(f'epubs/{epub_title}')

        epub.write_epub(f'epubs/{epub_title}/{epub_title}_{interval[0]["title"]}-{interval[len(interval)-1]["title"]}.epub', book)
        

def is_convertible_to_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_chapters(chapters_path, interval_size, initial_chapter):
    intervals = []
    initial_chapter = initial_chapter - 1
    chapters_dir = []

    for value in os.listdir(chapters_path):
        try:
            float(value)
            chapters_dir.append(value)
        except ValueError:
            pass

    chapters_dir = sorted(chapters_dir, key=lambda x: float(x))
    end_chapter = min(interval_size + initial_chapter, len(chapters_dir))

    while initial_chapter < len(chapters_dir):
        chapters = []

        chapters = chapters_dir[initial_chapter:end_chapter]

        interval = []
        for chapter in chapters:
            chapters_dir_path = os.path.join(chapters_path, chapter)
            if os.path.isdir(chapters_dir_path):
                interval.append({
                    'title': f'Capítulo {chapter}',
                    'chapter_path': chapters_dir_path
                })

        intervals.append(interval)

        initial_chapter += interval_size
        end_chapter = min(end_chapter + interval_size, len(chapters_dir))
    return intervals

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
