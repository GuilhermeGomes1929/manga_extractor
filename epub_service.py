from ebooklib import epub
import os

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
