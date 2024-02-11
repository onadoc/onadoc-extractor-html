from typing import List
import copy
import re 
from bs4 import PageElement

import logging as logger

def mutate_duplicates(
    node:PageElement,
    names:List[str] = [ "div" ],
) -> PageElement:
    """
    Detect duplicates DIVs
    """
    from mutate_strip_attributes import mutate_strip_attributes

    L = "mutate_detect_duplicates"

    textd = {}

    for node in node.find_all(names):
        cnode = mutate_strip_attributes(copy.copy(node))

        text = cnode.prettify().strip()
        if not text:
            continue

        text = re.sub(r"\d+", "#" , text)
        # print(text[:128])

        textd.setdefault(text, []).append(node)

    for text, nodes in textd.items():
        if len(nodes) <= 1:
            continue

        # n = nodes[0]
        # if img := n.find("img"):
        #     import sys
        #     print("---", file=sys.stderr)
        #     print(img.prettify(), file=sys.stderr)
        #     print("---", file=sys.stderr)

        logger.debug(f"{L}: {repr(text[:64])}")
        for node in nodes:
            node.decompose()

