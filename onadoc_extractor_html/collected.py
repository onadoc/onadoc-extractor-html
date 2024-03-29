import sys
from typing import List
from bs4 import PageElement

import logging as logger

import dataclasses
from typing import List
from bs4 import PageElement

import logging as logger

@dataclasses.dataclass
class Collector:
    texts: int = 0
    texts_length: int = 0

    links: int = 0
    links_length: int = 0

    headers: int = 0
    paragraphs: int = 0

def add_LOCAL(node:PageElement) -> None:
    """
    Add LOCAL to each node in the tree.
    """
    node.LOCAL = Collector()

    for child in node.children:
        if child.name:
            add_LOCAL(child)

def add_COLLECTED(node:PageElement) -> None:
    """
    Add COLLECTED to each node in the tree.
    """
    node.COLLECTED = Collector()

    for child in node.children:
        if child.name:
            add_COLLECTED(child)

def collect_LOCAL(node:PageElement, ignore_text:bool=False) -> None:
    """
    Compute the length of the text at the local node level
    """
    from .data import ignores, pushes

    local_node = node
    while getattr(local_node, "name", None) in pushes:
        local_node = local_node.parent

    LOCAL = local_node.LOCAL

    ## we can accept A here, but not later
    if not ignore_text and node.name in [ "a", ]: 
        LOCAL.links += 1
        LOCAL.links_length += len(node.text)

    if node.name in ignores:
       ignore_text = True

    text = (node.string or "").strip()
    if text and not ignore_text:
        LOCAL.texts += 1
        LOCAL.texts_length += len(text)

    if not ignore_text:
        if node.name in [ "h1", "h2", "h3", "h4" ]:
            LOCAL.headers += 1
        if node.name in [ "p", ]:
            LOCAL.paragraphs += 1

    for child in node.children:
        if child.name:
            collect_LOCAL(child, ignore_text=ignore_text)

def collect_COLLECTED(node:PageElement, ignore_text:bool=False) -> None:
    """
    Compute the length of the text at the collected node level

    The herustic is to ignore the text length if the text length is less than 25 characters.
    This then pushes those vales up to all parents
    """
    from .data import ignores, pushes

    LOCAL = node.LOCAL

    if node.name in ignores:
       ignore_text = True

    current = node
    while True:
        COLLECTED = current.COLLECTED
        if not ignore_text and LOCAL.texts_length >= 25:
            COLLECTED.texts += LOCAL.texts
            COLLECTED.texts_length += LOCAL.texts_length
        COLLECTED.links += LOCAL.links
        COLLECTED.links_length += LOCAL.links_length
        COLLECTED.headers += LOCAL.headers
        COLLECTED.paragraphs += LOCAL.paragraphs
        # print("heere", COLLECTED.texts_length)

        current = current.parent
        if not current or current.name in [ "body", "html", ]:
            break

    for child in node.children:
        if child.name:
            collect_COLLECTED(child, ignore_text=ignore_text)

def dump(node:PageElement, field:str="COLLECTED", max_depth:int=999, file=sys.stdout, _class=False):
    def _doit(current:PageElement, depth:int=0):
        if depth > max_depth:
            return
        
        collector = getattr(current, field)
        if not collector:
            return

        print(
            f"{depth:2d} ",
            "  " * depth,
            current.name,
            f"text={collector.texts}/{collector.texts_length}",
            f"links={collector.links}/{collector.links_length}",
            f"ps={collector.paragraphs}",
            f"hds={collector.headers}",
            repr((current.text or "").strip()[:40]),
            # current.attrs.get("class"),
            file=file,
        )

        for child in current.children:
            if child.name:
                _doit(child, depth=depth + 1)

    _doit(node)

def dump_COLLECTED(node:PageElement, **ad):
    dump(node, field="COLLECTED", **ad)

def dump_LOCAL(node:PageElement, **ad):
    dump(node, field="LOCAL", **ad)

def best_COLLECTED(node:PageElement, depth=0, cutoff:float=0.5, verbose:bool=False) -> PageElement:
    """
    This is the core algorithm to find the best "text-y"" in the tree.
    """
    best = None

    for child in node.children:
        if verbose and hasattr(child, "COLLECTED") and child.COLLECTED.texts_length:
            print(" " * depth, child.name, child.COLLECTED.texts_length, file=sys.stderr)

        if not child.name:
            continue
        if not child.COLLECTED.texts_length:
            continue

        if not best:
            best = child
        elif child.COLLECTED.texts_length > best.COLLECTED.texts_length:
            best = child

    if best:
        if verbose:
            print(" " * depth, best.name, best.COLLECTED.texts_length, file=sys.stderr)

        best_child = best_COLLECTED(best, depth + 1)
        if not best_child:
            return best
        
        if best_child.COLLECTED.texts_length < best.COLLECTED.texts_length * cutoff:
            return best
        else:
            return best_child
        
def mutate_best_parent(node:PageElement) -> PageElement:
    """
    Just in case SPAN etc is selected, this will bubble up to the best parent
    """
    from .data import pushes

    if node.name not in pushes:
        return node
    
    parent = node.parent

    for child in node.children:
        parent.append(child)

    node.decompose()

    return mutate_best_parent(parent)
