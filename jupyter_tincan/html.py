from bs4 import BeautifulSoup

from .text2svg import Text2SVG


class HTML2SVG:
    def __init__(self):
        self.text2svg = Text2SVG()

    def __call__(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        for text_element in soup.find_all(text=True):
            if text_element.parent.name not in ['script', 'style']:  # Skip script and style tags
                new_text = self.text2svg(text_element)
                text_element.replace_with(BeautifulSoup(new_text, 'html.parser'))
        return str(soup)
