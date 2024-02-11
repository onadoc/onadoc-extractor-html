from bs4 import BeautifulSoup
import sys
import copy

from collected import dump_COLLECTED, dump_LOCAL
from collected import best_COLLECTED, mutate_best_parent
from collected import add_LOCAL, add_COLLECTED, collect_LOCAL, collect_COLLECTED

from flatten import flatten

from mutate_dissimilar_children import mutate_dissimilar_children
from mutate_duplicates import mutate_duplicates
from mutate_hidden import mutate_hidden
from mutate_junk_nodes import mutate_find_leading, mutate_junk_nodes, mutate_empty_nodes
from mutate_strip_attributes import mutate_strip_attributes
from mutate_link_blocks import mutate_link_blocks

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    def do_dump_local(soup):
        body = soup.find("body")
        # mutate_detect_duplicates(body)
        add_LOCAL(body)
        collect_LOCAL(body)
        dump_LOCAL(body)
        
    def do_dump_collected(soup):
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

        dump_COLLECTED(best, max_depth=1)

    def do_extract(soup):
        body = soup.find("body")
        # print("H1", soup.find("h1"), file=sys.stderr)
        mutate_duplicates(body)
        mutate_hidden(body)
        # print("H1", soup.find("h1"), file=sys.stderr)
        add_LOCAL(body)
        collect_LOCAL(body)

        add_COLLECTED(body)
        collect_COLLECTED(body)
        
        if True:
            best = best_COLLECTED(body, cutoff=0.4)
            # dump_COLLECTED(best)

        if True:
            best = mutate_best_parent(best)
            best = mutate_dissimilar_children(best)

            best = mutate_find_leading(best)
            # dump_COLLECTED(best, max_depth=4, file=sys.stderr, _class=True)
            best = mutate_strip_attributes(best)
            best = mutate_link_blocks(best)
            best = mutate_junk_nodes(best)
            best = mutate_empty_nodes(best)
            # print(best.name)

        dump_COLLECTED(best, max_depth=4, file=sys.stderr)

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
            
    FILENAME = "../../tests/data/in/too-many-images.sample.html"
    FILENAME = "../../tests/data/in/telegraph-sussex.html"
    FILENAME = "../../tests/data/in/theatlantic.com.html"
    FILENAME = "../../tests/data/in/cbc-mexico-1.html"
    FILENAME = "../../tests/data/in/the-hurricane-rubin-carter-denzel-washington.html"
    FILENAME = "../../tests/data/in/si-game.sample.html"
    FILENAME = "../../tests/data/in/grapevine.is.html"
    FILENAME = "../../tests/data/in/cnn.com.html"
    FILENAME = "../../tests/data/in/globe.html"
    FILENAME = "../../tests/data/in/torontosun.com-kinsella.html"
    FILENAME = "../../tests/data/in/substack.html"
    FILENAME = "../../tests/data/in/nationalpost.com.html"
    FILENAME = "../../tests/data/in/timesnownews.com.html"
    FILENAME = "../../tests/data/in/dailymail.co.uk.html"

    with open(FILENAME) as fin:
        ## soup = BeautifulSoup(fin, "lxml")
        soup = BeautifulSoup(fin, 'html.parser')


    # # print(soup.find("h1"))
    # do_dump_local(soup)
    # do_dump_collected(soup)
    do_extract(soup)

