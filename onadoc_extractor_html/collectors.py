from bs4 import BeautifulSoup, PageElement
import sys
import copy
import os

from .collected import dump_COLLECTED, dump_LOCAL
from .collected import best_COLLECTED, mutate_best_parent
from .collected import add_LOCAL, add_COLLECTED, collect_LOCAL, collect_COLLECTED

from .flatten import flatten

from .mutate_dissimilar_children import mutate_dissimilar_children
from .mutate_duplicates import mutate_duplicates
from .mutate_hidden import mutate_hidden
from .mutate_junk_nodes import mutate_find_leading, mutate_junk_nodes, mutate_empty_nodes
from .mutate_strip_attributes import mutate_strip_attributes
from .mutate_link_blocks import mutate_link_blocks

def dump_local(soup:PageElement, max_depth:int=999):
    """
    """
    body = soup.find("body")
    add_LOCAL(body)
    collect_LOCAL(body)
    dump_LOCAL(body, max_depth=max_depth)
    
def dump_collected(soup:PageElement, max_depth:int=999):
    """
    """
    body = soup.find("body")
    mutate_duplicates(body)
    mutate_hidden(body)
    add_LOCAL(body)
    collect_LOCAL(body)

    add_COLLECTED(body)
    collect_COLLECTED(body)
    # print(body)

    best = best_COLLECTED(body, cutoff=0.4)
    best = mutate_best_parent(best)
    best = mutate_dissimilar_children(best)

    best = mutate_find_leading(best)
    best = mutate_strip_attributes(best)
    best = mutate_junk_nodes(best)
    best = mutate_empty_nodes(best)

    dump_COLLECTED(best, max_depth=max_depth)

def extract(soup:PageElement, verbose:bool=False, max_depth:int=999):
    """
    """
    body = soup.find("body")
    # print("H1", soup.find("h1"), file=sys.stderr)
    mutate_duplicates(body)
    mutate_hidden(body)
    # print("H1", soup.find("h1"), file=sys.stderr)
    add_LOCAL(body)
    collect_LOCAL(body)

    add_COLLECTED(body)
    collect_COLLECTED(body)
    
    best = best_COLLECTED(body, cutoff=0.4)

    best = mutate_best_parent(best)
    best = mutate_dissimilar_children(best)

    best = mutate_find_leading(best)
    # dump_COLLECTED(best, max_depth=4, file=sys.stderr, _class=True)
    best = mutate_strip_attributes(best)
    best = mutate_link_blocks(best)
    best = mutate_junk_nodes(best)
    best = mutate_empty_nodes(best)
    # print(best.name)

    if verbose:
        dump_COLLECTED(best, max_depth=max_depth, file=sys.stderr)

    if True:
        print("""
<html>
<head>
    <meta charset="utf-8">
</head>
<body>""")
        for node in flatten(best):
            print(node.prettify())
        print("""</body></html>""")
    else:
        print("""
<html>
<head>
    <meta charset="utf-8">
</head>
<body>""")
        print(best.prettify())
        print("""</body></html>""")
    # collect(body)
    # dump(body)
            
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)


    FOLDER = "tests/data/"
    FILENAME = "too-many-images.sample.html"
    FILENAME = "telegraph-sussex.html"
    FILENAME = "theatlantic.com.html"
    FILENAME = "cbc-mexico-1.html"
    FILENAME = "the-hurricane-rubin-carter-denzel-washington.html"
    FILENAME = "si-game.sample.html"
    FILENAME = "grapevine.is.html"
    FILENAME = "cnn.com.html"
    FILENAME = "globe.html"
    FILENAME = "timesnownews.com.html"
    FILENAME = "nationalpost.com.html"
    FILENAME = "substack.html"
    FILENAME = "dailymail.co.uk.html"
    FILENAME = "digitalocean.com-wireguard.html"
    FILENAME = "torontosun.com-kinsella.html"

    with open(os.path.join(FOLDER, FILENAME)) as fin:
        soup = BeautifulSoup(fin, 'html.parser')

    do_extract(soup)

