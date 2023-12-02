from bs4 import BeautifulSoup

from .text2svg import Text2SVG


class HTML2SVG:
    def __init__(self):
        self.text2svg = Text2SVG()

    def __call__(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        for text_element in soup.find_all(text=True):
            if text_element.parent.name not in ['script', 'style']:  # Skip script and style tags
                lines = text_element.splitlines()
                lines = [f"<span>{self.text2svg(line)}</span>" for line in lines]
                new_text = "<br>".join(lines)
                text_element.replace_with(BeautifulSoup(new_text, 'html.parser'))
        return str(soup)
