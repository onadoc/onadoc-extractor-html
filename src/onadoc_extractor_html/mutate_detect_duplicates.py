import sys
import copy
from bs4 import PageElement

import logging as logger

def mutate_detect_duplicates(node:PageElement) -> PageElement:
    """
    Detect duplicates in the tree
    """
    from mutate_strip_attributes import mutate_strip_attributes

    L = "mutate_detect_duplicates"

    textd = {}

    for node in node.find_all("div"):
        node = copy.copy(node)
        mutate_strip_attributes(node, retain=None)
        text = node.prettify().strip()
        text = (node.prettify() or "").strip()
        if not text:
            continue

        # text = text
        if not ( node.name and text ):
            continue

        # if node.name in [ "h1", "h2", "h3 "]:
        #     continue

        key = ( node.name, text )
        textd.setdefault(key, []).append(node)

    for ( name, text ), nodes in textd.items():
        if len(nodes) <= 1:
            continue

        logger.debug(f"{L}: {name=} {repr(text[:20])}")

    return
    for key, value in textd.items():
        if len(value) <= 1:
            continue

        for node in value:
            node.decompose()

