from typing import List, Iterable
import copy
import re 
from bs4 import PageElement

import logging as logger

def order_by_text_length(nodes:Iterable[PageElement]) -> List[PageElement]:
    """
    Order nodes by text length
    """
    nodes = list(nodes)
    nodes = [ node for node in nodes if node.name ]
    nodes = sorted(nodes, key=lambda node: node.COLLECTED.texts_length, reverse=True)
    nodes = list(nodes) 

    return nodes

def order_by_paragraphs(nodes:Iterable[PageElement]) -> List[PageElement]:
    """
    Order nodes by paragraphs
    """
    nodes = list(nodes)
    nodes = [ node for node in nodes if node.name ]
    nodes = [ node for node in nodes if node.COLLECTED.paragraphs ]
    nodes = sorted(nodes, key=lambda node: node.COLLECTED.paragraphs, reverse=True)
    nodes = list(nodes) 

    return nodes

def is_image_block(node:PageElement) -> bool:
    """
    This is a hack for now - really we want to see if the images are big.

    The core observation is that an image block has a single IMG tag
    """
    L = "is_image_block"

    image_like = 0
    not_image_like = 0
    social = 0
    nodes = 0

    for child in node.find_all():
        nodes += 1

        if child.name in [ "li", "ol", "u", "table", ]:
            not_image_like += 1
        elif child.name == "img":
            alt = (child.get("alt") or "").lower()
            if alt in [ 
                "x", "reddit", "twitter", "facebook", "email", "pinterest", 
                "instagram", "whatsapp", "linkedin", "tumblr", "print", "share",
            ]:
                social += 1
                continue

            image_like += 1

    logger.debug(f"{L}: {image_like=} {not_image_like=} {social=} {nodes=}")

    if social > 1:
        return False
    
    if image_like == 1:
        return True
    
        # import sys
        # print(node.prettify(), file=sys.stderr)
        # return True
    
    return False

def mutate_dissimilar_children(
    node:PageElement,
) -> PageElement:
    """
    Find and remove dissimilar children
    """
    L = "mutate_dissimilar_children"

    ## find the best child - the one with the most text
    best_by_texts = order_by_text_length(node.children)
    if len(best_by_texts) < 2:
        return node
    
    ## nodes should look like this
    prototype = None
    
    best_by_paragraphs = order_by_paragraphs(node.children)
    if best_by_paragraphs:
        if best_by_texts[0].name == best_by_paragraphs[0].name:
            prototype = best_by_texts[0]
        elif best_by_paragraphs[0].COLLECTED.paragraphs > 1:
            prototype = best_by_paragraphs[0]
        else:
            prototype = best_by_texts[0]
    else:
        prototype = best_by_texts[0]

    if not prototype:
        return node

    logger.debug(f"{L}: prototype={prototype.name} {prototype.COLLECTED.texts_length}")

    new_children = []
    for child in list(node.children):
        keep = False
        if not child.name:
            keep = True
        if child.name in [ "h1", "h2", "h3", "h4", "h5", "p", "table", "ul", "ol", "picture", "img", ]:
            keep = True
        if child.name == prototype.name:
            if prototype.COLLECTED.paragraphs and not child.COLLECTED.paragraphs:
                keep = False
            else:
                keep = True

        if not keep and is_image_block(child):
            keep = True

        if keep:
            new_children.append(child)
            continue

        if child.COLLECTED.headers:
            for header in child.find_all(["h1", "h2", "h3", "h4", ]):
                new_children.append(header)

                logger.debug(f"{L}: RECOVER HEADER {header.name} {header.text[:16]}")

        logger.debug(f"{L}: removing {child.name} {repr(child.prettify()[:50])}")
        # import sys
        # from onadoc_extractor_html.collectors import dump_COLLECTED
        # dump_COLLECTED(child, file=sys.stderr)
        # print("---", file=sys.stderr)
        # print(child.prettify(), file=sys.stderr)
        # print("---", file=sys.stderr)
        # child.decompose()

    ## replace node's children with new_children
    node.clear()
    for child in new_children:
        node.append(child)

    return node
