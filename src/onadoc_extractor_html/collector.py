from bs4 import BeautifulSoup
import sys
import copy

from dump import dump_COLLECTED, dump_LOCAL
from facts import phase_add_LOCAL, phase_add_COLLECTED, collect_LOCAL, collect_COLLECTED
from mutate_dissimilar_children import mutate_dissimilar_children

def best_COLLECTED(node, depth=0, cutoff:float=0.5, verbose:bool=False):
    """
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
        

def best_parents(node):
    """
    Just in case SPAN etc is selected
    """
    from data import pushes

    ## just in case a SPAN, etc is selected
    current = node
    while current:
        if current.name not in pushes:
            break

        current = current.parent

    return current

def patch_leading(node):
    """
    This will try to get data that's not in the best node, but in the parent.
    They must appear "before" the best node.
    """

    print("---", file=sys.stderr)
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
        if not current or current.name in [ "body", "html", "xmain", "xarticle", ]:
            break

    for insert in reversed(inserts):
        best.insert(0, insert)
        # print("INSERTING", insert)

    # print("BEST", best)
        
    # print("---", best.name, inserts, file=sys.stderr)

    return best
        
def util_delete_nodes(node):
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

    # for x in range(4):
    #     empty_elements = node.find_all(['div', 'p', 'section'], text=lambda text: (text or "").strip() == '')
    #     print("HERE:XXX", empty_elements, file=sys.stderr)
    #     for element in empty_elements:
    #         if not element.children:
    #             element.decompose()

    return node

def util_delete_empty_nodes(node):
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

def phase_detect_hidden(node):
    """
    Detect node with 'hidden' class and remove them. Very tailwind
    """
    for hidden in node.find_all(class_="hidden"):
        hidden.decompose()


from mutate_detect_duplicates import mutate_detect_duplicates

def util_strip_node(node):
    """
    Remove all attributes except href and src
    """
    if not node.name:
        return
    
    for attr in list(node.attrs):
        if attr not in ["href", "src"]:
            del node[attr]

    for child in node.children:
        util_strip_node(child)
    
    return node

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    def do_dump_local(soup):
        body = soup.find("body")
        # mutate_detect_duplicates(body)
        phase_add_LOCAL(body)
        collect_LOCAL(body)
        dump_LOCAL(body)
        
    def do_dump_collected(soup):
        body = soup.find("body")
        mutate_detect_duplicates(body)
        phase_detect_hidden(body)
        phase_add_LOCAL(body)
        collect_LOCAL(body)

        phase_add_COLLECTED(body)
        collect_COLLECTED(body)
        # print(body)
    
        best = best_COLLECTED(body, cutoff=0.4)
        best = best_parents(best)
        best = mutate_dissimilar_children(best)

        best = patch_leading(best)
        best = util_strip_node(best)
        best = util_delete_nodes(best)
        best = util_delete_empty_nodes(best)
        dump_COLLECTED(best, max_depth=2)

    def do_extract(soup):
        body = soup.find("body")
        # print("H1", soup.find("h1"), file=sys.stderr)
        mutate_detect_duplicates(body)
        phase_detect_hidden(body)
        # print("H1", soup.find("h1"), file=sys.stderr)
        phase_add_LOCAL(body)
        collect_LOCAL(body)

        phase_add_COLLECTED(body)
        collect_COLLECTED(body)
        
        if True:
            best = best_COLLECTED(body, cutoff=0.4)
            # dump_COLLECTED(best)

        if True:
            best = best_parents(best)
            best = mutate_dissimilar_children(best)

            best = patch_leading(best)
            best = util_strip_node(best)
            best = util_delete_nodes(best)
            best = util_delete_empty_nodes(best)
            # print(best.name)

        if True:
            print("""
<html>
    <head>
        <meta charset="utf-8">
    </head>
<body>""")
            print(best.prettify())
            print("""</body></html>""")
        # collect(body)
        # dump(body)
            
    FILENAME = "../../tests/data/in/too-many-images.sample.html"
    FILENAME = "../../tests/data/in/substack.html"
    FILENAME = "../../tests/data/in/si-game.sample.html"
    FILENAME = "../../tests/data/in/the-hurricane-rubin-carter-denzel-washington.html"
    FILENAME = "../../tests/data/in/telegraph-sussex.html"
    FILENAME = "../../tests/data/in/globe.html"
    FILENAME = "../../tests/data/in/cnn.com.html"
    FILENAME = "../../tests/data/in/nationalpost.com.html"
    FILENAME = "../../tests/data/in/theatlantic.com.html"
    FILENAME = "../../tests/data/in/cbc-mexico-1.html"

    with open(FILENAME) as fin:
        ## soup = BeautifulSoup(fin, "lxml")
        soup = BeautifulSoup(fin, 'html.parser')


    # # print(soup.find("h1"))
    # do_dump_local(soup)
    do_dump_collected(soup)
    ## do_extract(soup)

