from typing import List
from bs4 import PageElement

import logging as logger

def mutate_strip_attributes(
    node:PageElement, 
    names:List[str] = None,
    retain:List[str] = [ "href", "src "],
) -> PageElement:
    """
    Remove all attributes except (normally) href and src
    """
    if not node.name:
        return
    
    names = names or [ "*" ]
    for subnode in node.find_all(names):
        for attr in list(subnode.attrs):
            if not retain or attr not in retain:
                del node[attr]
    
    '''
    for attr in list(node.attrs):
        if not retain or attr not in retain:
            del node[attr]

    for child in node.children:
        mutate_strip_attributes(child)
    '''
    
    return node
