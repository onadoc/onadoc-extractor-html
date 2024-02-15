# onadoc-extractor-html

Extract the core HTML content from a webpage. 
This includes **text and images**.

Output will be very similar to Safari's Reader mode.

It is also similar to these other projects, with the caveat that
our goal is to preserve some HTML and the image content.

### Similar Projects

* [readability]()
* [goose3](https://github.com/goose3/goose3)
* [newspaper3k](https://github.com/codelucas/newspaper/)
* [boilerpy3](https://github.com/jmriebold/BoilerPy3)
* [dragnet](https://github.com/dragnet-org/dragnet)

## Installation
```bash

pip install onadoc-extractor-html
```

## Command Line Usage

### Extract text from a URL

```bash
python -m onadoc_extractor_html.app \
    --url 'https://arstechnica.com/space/2024/02/spacex-and-intuitive-machines-seek-to-blaze-a-new-trail-to-the-moon/'
```

### Extract text from a file

```bash
curl -s 'https://arstechnica.com/space/2024/02/spacex-and-intuitive-machines-seek-to-blaze-a-new-trail-to-the-moon/' > /tmp/article.html
python -m onadoc_extractor_html.app \
    --file /tmp/article.html
```

### Print Structure of Document

For debugging

Before processing

```bash
python -m onadoc_extractor_html.app \
    --url 'https://www.cbc.ca/sports/hockey/nhl/nhl-blue-jackets-fire-kekalainen-1.7116104' \
    --dump-local
```

After processing

```bash
python -m onadoc_extractor_html.app \
    --url 'https://www.cnn.com/2024/02/15/cars/headlights-tech-adaptable-high-beams-cars/index.html' \
    --dump-collected
```

## Program Usage

### 

```python