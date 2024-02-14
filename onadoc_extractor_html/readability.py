from bs4 import BeautifulSoup, PageElement

class Document:
    """Somewhat readability-lxml compatible interface"""

    def __init__(self, input, *av, **ad):
        """Generate the document

        :param input: string of the html content.

        All other parameters are ignored.

        API methods:
        .title() -- full title
        .short_title() -- cleaned up title
        .content() -- full content
        .summary() -- cleaned up content
        """
        from . import collectors

        self.input = input

        self._soup = BeautifulSoup(self.input, "html.parser")

        if header := self._best.find("h1") or self._best.find("h2") or self._soup.find("title"):
            self._title = header.get_text()

        self._best = collectors.extract(self._soup)

        
    def content(self) -> str:
        """Returns document body"""

        return self._soup.find("body").prettify()

    def title(self) -> str:
        """Returns document title"""

        return self._title

    def author(self) -> str:
        """Returns document author"""

    def short_title(self) -> str:
        """Returns cleaned up document title"""

        return self._title

    def summary(self, html_partial=False) -> str:
        """
        Given a HTML file, extracts the text of the article.

        :param html_partial: return only the div of the document, don't wrap
                             in html and body tags.

        Warning: It mutates internal DOM representation of the HTML document,
        so it is better to call other API methods before this one.
        """
        from .flatten import flatten

        if html_partial:
            return self._best.prettify()
        

        parts = []
        parts.append("""\
<html>
<head>
    <meta charset="utf-8">
</head>
<body>""")
        
        for node in flatten(self._best):
            parts.append(node.prettify())
            
        parts.append("""</body></html>""")

        return "\n".join(parts)
