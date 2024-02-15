# https://github.com/jmriebold/BoilerPy3
from boilerpy3 import extractors

extractor = extractors.ArticleExtractor()

doc = extractor.get_doc_from_file("data/arstechnica.com.html")
print(doc.content)
