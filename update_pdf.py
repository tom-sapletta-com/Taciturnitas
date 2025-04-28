import os
import re
import logging
import markdown2
import weasyprint
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def resize_image(image_path, max_width, max_height):
    """
    Zmiana rozmiaru obrazu przy zachowaniu proporcji

    :param image_path: Ścieżka do obrazu
    :param max_width: Maksymalna szerokość
    :param max_height: Maksymalna wysokość
    :return: Ścieżka do przeskalowanego obrazu lub None
    """
    try:
        # Otwórz obraz
        with Image.open(image_path) as img:
            # Pobierz oryginalne wymiary
            orig_width, orig_height = img.size
            logger.info(f"Oryginalne wymiary obrazu: {orig_width} x {orig_height}")

            # Oblicz współczynnik skalowania
            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            scale_factor = min(width_ratio, height_ratio)

            # Oblicz nowe wymiary
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)

            # Zmień rozmiar obrazu
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

            # Zapisz tymczasowy obraz
            temp_path = os.path.join(
                os.path.dirname(image_path),
                f'temp_{os.path.basename(image_path)}'
            )
            resized_img.save(temp_path)

            logger.info(f"Przeskalowane wymiary obrazu: {new_width} x {new_height}")
            return temp_path
    except Exception as e:
        logger.error(f"Błąd przetwarzania obrazu {image_path}: {e}")
        return None


def resolve_image_path(image_path, base_dir):
    """
    Rozwiąż ścieżkę obrazu względem katalogu bazowego

    :param image_path: Ścieżka obrazu z Markdown
    :param base_dir: Katalog bazowy dokumentu
    :return: Pełna ścieżka do obrazu
    """
    # Jeśli ścieżka jest bezwzględna, zwróć ją bez zmian
    if os.path.isabs(image_path):
        return image_path

    # Spróbuj kilku wariantów ścieżek
    possible_paths = [
        os.path.join(base_dir, image_path),  # Względem katalogu dokumentu
        os.path.join(os.getcwd(), image_path),  # Względem bieżącego katalogu
        image_path  # Oryginalna ścieżka
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def process_markdown_images(html, base_dir):
    """
    Przetworz obrazy w HTML wygenerowanym z Markdown

    :param html: Treść HTML
    :param base_dir: Katalog bazowy dokumentu
    :return: Zmodyfikowana treść HTML
    """
    # Parsuj HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Znajdź wszystkie obrazy
    for img_tag in soup.find_all('img'):
        # Pobierz ścieżkę obrazu
        src = img_tag.get('src', '')

        # Rozwiąż pełną ścieżkę obrazu
        full_path = resolve_image_path(src, base_dir)

        if full_path:
            # Zmień rozmiar obrazu
            resized_path = resize_image(full_path, 800, 600)

            if resized_path:
                # Zamień na bezwzględną ścieżkę pliku
                img_tag['src'] = 'file://' + os.path.abspath(resized_path)
            else:
                # Usuń tag obrazu, jeśli nie udało się przetworzyć
                img_tag.decompose()
        else:
            # Usuń tag obrazu, jeśli nie znaleziono pliku
            img_tag.decompose()

    return str(soup)


def md_to_pdf(md_file, pdf_file, cover_image=None):
    """
    Konwersja Markdown do PDF z zaawansowanym przetwarzaniem obrazów

    :param md_file: Ścieżka do pliku Markdown
    :param pdf_file: Ścieżka do wyjściowego pliku PDF
    :param cover_image: Opcjonalny obraz okładki
    """
    try:
        # Katalog bazowy dokumentu
        base_dir = os.path.dirname(os.path.abspath(md_file))

        # Wczytaj treść Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Konwertuj Markdown do HTML
        html = markdown2.markdown(md_content, extras=['metadata', 'fenced-code-blocks'])

        # Przetworz obrazy w HTML
        processed_html = process_markdown_images(html, base_dir)

        # Dodaj podstawowy szablon HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 2; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 10px; 
                }}
                img {{ 
                    max-width: 100%; 
                    height: auto; 
                    display: block; 
                    margin: 10px auto; 
                }}
                h1, h2 {{ color: #333; }}
                code {{ 
                    background-color: #f4f4f4; 
                    padding: 2px 4px; 
                    border-radius: 4px; 
                }}
                pre {{ 
                    background-color: #f4f4f4; 
                    padding: 10px; 
                    border-radius: 4px; 
                    overflow: auto; 
                }}
            </style>
        </head>
        <body>
            {processed_html}
        </body>
        </html>
        """

        # Dodaj obraz okładki, jeśli podano
        if cover_image:
            cover_path = resolve_image_path(cover_image, base_dir)
            if cover_path:
                # Zmień rozmiar obrazu okładki
                resized_cover = resize_image(cover_path, 800, 600)
                if resized_cover:
                    # Zamień na bezwzględną ścieżkę pliku
                    cover_src = 'file://' + os.path.abspath(resized_cover)
                    # Dodaj obraz okładki przed treścią
                    full_html = full_html.replace('<body>',
                                                  f'<body><img src="{cover_src}" style="width: 100%; margin-bottom: 20px;">')

        # Konwertuj HTML do PDF
        weasyprint.HTML(string=full_html, base_url='file://' + base_dir + '/').write_pdf(pdf_file)

        logger.info("Konwersja PDF zakończona sukcesem!")
        return True

    except Exception as e:
        logger.error(f"Błąd konwersji PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


# Uruchom konwersję
if __name__ == '__main__':
    try:
        success = md_to_pdf('README.md', 'Taciturnitas.pdf', cover_image='okladka.png')
        if not success:
            print("Konwersja PDF nie powiodła się. Sprawdź logi.")
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas konwersji PDF: {e}")
        import traceback

        traceback.print_exc()