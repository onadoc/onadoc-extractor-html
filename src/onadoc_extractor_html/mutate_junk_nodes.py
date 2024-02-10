import sys
import copy

from bs4 import PageElement

def mutate_find_leading(node:PageElement) -> PageElement:
    """
    This will try to get data that's not in the best node, but in the parent.
    They must appear "before" the best node.
    """

    print("---", "patch_leading", file=sys.stderr)
    inserts = []
    best = node
    previous = node
    current = node.parent
    while True:
        print(current.name, current.COLLECTED, file=sys.stderr)

        for child in current.children:
            if previous == child:
                break

            if child.name in [ "h1", "h2", "h3", "h4" ]:
                header = child
            elif child.name:
                header = child.find(["h1", "h2", "h3", "h4"])
            else:
                header = None
            if header:
                print("   HEADER", header.name, repr(header.text), file=sys.stderr)
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
    from bs4 import Comment

    for child in node.find_all(['script', 'noscript', 'button', 'form', 'iframe', 'style', 'link', 'svg', 'aside', "footer", "XXXheader", "nav"]):
        child.decompose()
    comments = node.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    return node
