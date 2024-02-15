# onadoc-extractor-html
Extract the "real" text from HTML

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