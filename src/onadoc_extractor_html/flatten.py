from typing import List, Iterable
import copy
import re 
from bs4 import PageElement, BeautifulSoup

import logging as logger

_soup = BeautifulSoup()

def flatten(node:PageElement) -> Iterable[PageElement]:
    """
    """

    if not node.name:
        p_node = _soup.new_tag("p")
        p_node.string = node.text

        yield p_node
    elif node.name in [ "p", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "table", "blockquote", "code" ]:
        yield node
    elif node.name in [ "figcaption", ]:
        node.tag = "p"
        yield node
    elif node.name in [ "a", "b", "em", "i", "img", ]:
        p_node = _soup.new_tag("p")
        p_node.append(node)

        yield p_node
    else:
        for child in node.children:
            yield from flatten(child)
