## pip install goose3[all]

from goose3 import Goose

with open("data/arstechnica.com.html") as fin:
    data = fin.read()

g = Goose()
article = g.extract(raw_html=data)
print(article.cleaned_text)
