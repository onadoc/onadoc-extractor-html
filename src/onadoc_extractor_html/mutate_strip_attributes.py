from typing import List
from bs4 import PageElement

import logging as logger

def mutate_strip_attributes(
    node:PageElement, 
    names:List[str] = None,
    retain:List[str] = [ "href", "src", ],
) -> PageElement:
    """
    Remove all attributes except (normally) href and src
    """
    if not node.name:
        return
    
    if not names or node.name in names:
        for attr in list(node.attrs.keys()):
            if not retain or attr not in retain:
                del node.attrs[attr]

    for child in node.children:
        mutate_strip_attributes(child)
    
    return node
