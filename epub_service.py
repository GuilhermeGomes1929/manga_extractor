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


        chapters_ebook = []
        pages = []

        page_style = 'body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden;} img { width: 100%; height: 100%; object-fit: fill; }'

        page_css = epub.EpubItem(uid="style_page",
                                file_name="style/page.css",
                                media_type="text/css",
                                content=page_style)
        book.add_item(page_css)
        
        chapter_style = 'body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }'

        chapter_css = epub.EpubItem(uid="style_chapter",
                                file_name="style/chapter.css",
                                media_type="text/css",
                                content=chapter_style)
        book.add_item(chapter_css)
        
        for chapter in interval:
            title = chapter['title']

            page_chapter = epub.EpubHtml(title=title,
                                            file_name=f'{title}.xhtml',
                                            content=f'<h1>{title}</h1>')

            
            page_chapter.add_item(chapter_css)
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

        epub.write_epub(f'epubs/{epub_title}_{interval[0]["title"]}-{interval[len(interval)-1]["title"]}.epub', book)


def get_chapters(chapters_path, interval_size, initial_chapter):
    intervals = []
    initial_chapter = initial_chapter - 1
    chapters_dir = sorted(os.listdir(chapters_path), key=lambda x: float(x))
    end_chapter = min(interval_size + initial_chapter, len(chapters_dir))

    while initial_chapter < len(chapters_dir):
        print(initial_chapter)
        print(end_chapter)
        chapters = []

        print(initial_chapter)
        print(end_chapter)
        chapters = chapters_dir[initial_chapter:end_chapter]
        print(chapters)
        interval = []
        for chapter in chapters:
            chapters_dir_path = os.path.join(chapters_path, chapter)
            if os.path.isdir(chapters_dir_path):
                images = get_images(chapters_dir_path)
                interval.append({
                    'title': f'Capítulo {chapter}',
                    'images': images
                })

        intervals.append(interval)

        initial_chapter += interval_size
        print(len(chapters_dir))
        end_chapter = min(end_chapter + interval_size, len(chapters_dir))
        print(initial_chapter)
        print(end_chapter)
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
