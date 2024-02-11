import sys
import copy

from bs4 import PageElement

import logging as logger

def mutate_link_blocks(node:PageElement) -> PageElement:
    """
    """

    for child in node.find_all([ "ol", "ul" ]):
        COLLECTED = child.COLLECTED
        if COLLECTED.links <= 1:
            continue
        
        if COLLECTED.links != len(child.find_all("li")):
            continue

        child.decompose()

    return node
