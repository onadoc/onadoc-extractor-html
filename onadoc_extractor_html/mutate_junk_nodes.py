import sys
import copy

from bs4 import PageElement

import logging as logger

def mutate_find_leading(node:PageElement) -> PageElement:
    """
    This will try to get data that's not in the best node, but in the parent.
    They must appear "before" the best node.
    """
    L = "mutate_find_leading"

    inserts = []
    best = node
    previous = node
    current = node.parent
    while True:
        logger.debug(f"{L}: {current.name} {current.COLLECTED}")

        for child in current.children:
            if previous == child:
                break

            if child.name in [ "h1", "h2", "h3", "h4" ]:
                headers = [ child ]
            elif child.name:
                headers = child.find_all(["h1", "h2", "h3", "h4"])
            else:
                headers = []
            if headers:
                for header in headers:
                    logger.debug(f"{L}: HEADER {header.name} {repr(header.text)}")
                    cheader = copy.copy(header)
                    cheader.LOCAL = copy.copy(header.LOCAL)
                    cheader.COLLECTED = copy.copy(header.COLLECTED)
                    inserts.append(cheader)

        previous = current
        current = current.parent
        if not current or current.name in [ "xbody", "html", "xmain", "xarticle", ]:
            break

    for insert in reversed(inserts):
        best.insert(0, insert)
        # print("INSERTING", insert)

    # print("BEST", best)
        
    # print("---", best.name, inserts, file=sys.stderr)

    return best
        
def mutate_junk_nodes(node:PageElement) -> PageElement:
    """
    Delete children that are:
    - script
    - iframe
    - comments
    - style
    - link
    """
    L = "mutate_junk_nodes"

    from bs4 import Comment

    for child in node.find_all(['script', 'noscript', 'button', 'form', 'iframe', 'style', 'link', 'svg', 'aside', "footer", "XXXheader", "nav"]):
        logger.debug(f"{L}: REMOVE {child.name}")
        child.decompose()

    comments = node.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    return node

def mutate_empty_nodes(node:PageElement) -> PageElement:
    """
    Delete empty nodes
    """

    def deleter(n):
        if n == node:
            return
        if n.name in [ "hr", "img" ]:
            return
        if len(list(n.children)):
            return
        if (n.text or "").strip():
            return
        
        p = n.parent
        n.decompose()

        deleter(p)

    for n in node.find_all():
        deleter(n)

    return node

