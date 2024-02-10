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

def phase_add_LOCAL(node:PageElement) -> None:
    """
    Add LOCAL to each node in the tree.
    """
    node.LOCAL = Collector()

    for child in node.children:
        if child.name:
            phase_add_LOCAL(child)

def phase_add_COLLECTED(node:PageElement) -> None:
    """
    Add COLLECTED to each node in the tree.
    """
    node.COLLECTED = Collector()

    for child in node.children:
        if child.name:
            phase_add_COLLECTED(child)

def collect_LOCAL(node:PageElement, ignore_text:bool=False) -> None:
    """
    Compute the length of the text at the local node level
    """
    from data import ignores, pushes

    local_node = node
    while getattr(local_node, "name", None) in pushes:
        local_node = local_node.parent

    LOCAL = local_node.LOCAL

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
        if node.name in [ "a", ]:
            LOCAL.links += 1
            LOCAL.links_length += len(node.text)

    for child in node.children:
        if child.name:
            collect_LOCAL(child, ignore_text=ignore_text)

def collect_COLLECTED(node:PageElement, ignore_text:bool=False) -> None:
    """
    Compute the length of the text at the collected node level

    The herustic is to ignore the text length if the text length is less than 25 characters.
    This then pushes those vales up to all parents
    """
    from data import ignores, pushes

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