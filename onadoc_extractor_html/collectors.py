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

def extract(soup:PageElement):
    """
    """
    body = soup.find("body")

    mutate_duplicates(body)
    mutate_hidden(body)
    
    add_LOCAL(body)
    collect_LOCAL(body)

    add_COLLECTED(body)
    collect_COLLECTED(body)
    
    best = best_COLLECTED(body, cutoff=0.4)
    best = mutate_best_parent(best)
    best = mutate_dissimilar_children(best)
    best = mutate_find_leading(best)
    best = mutate_strip_attributes(best)
    best = mutate_link_blocks(best)
    best = mutate_junk_nodes(best)
    best = mutate_empty_nodes(best)

    return best
