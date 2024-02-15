## pip3 install newspaper3k

with open("data/arstechnica.com.html") as fin:
    data = fin.read()

from newspaper import Article
article = Article("")
article.download(input_html=data)
article.parse()

print(article.text)
