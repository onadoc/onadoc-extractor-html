import dataclasses
from bs4 import BeautifulSoup
import sys
import copy


ignores = [
    "script",
    "style",
    "svg",
    "noscript",
    "picture",
    "iframe",
    "object",
    "form",
    "textarea",
    "input",
    "a", ## ???
]
pushes = [
    "li",
    "em",
    "i",
    "b",
    "span",
    "strong",
    # "a",
    "abbr",
    "acronym",
    "address",
]

@dataclasses.dataclass
class Collector:
    texts: int = 0
    texts_length: int = 0

    links: int = 0
    links_length: int = 0

def count_children(node):
    count = 0
    for child in node.children:
        count += 1
        if child.name is not None:  # If the child is a tag (node)
            count += count_children(child)  # Recursively count children
    return count

def phase_add_LOCAL(node):
    """
    Add LOCAL to each node in the tree.
    """
    node.LOCAL = Collector()

    for child in node.children:
        if child.name:
            phase_add_LOCAL(child)

def phase_add_COLLECTED(node):
    """
    Add COLLECTED to each node in the tree.
    """
    node.COLLECTED = Collector()

    for child in node.children:
        if child.name:
            phase_add_COLLECTED(child)

def phase_local_texts_length(node, ignore_text:bool=False):
    """
    Compute the length of the text at the local node level
    """
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

    for child in node.children:
        if child.name:
            phase_local_texts_length(child, ignore_text=ignore_text)

def phase_local_links_length(node):
    for link in node.find_all("a"):
        LOCAL = link.LOCAL
        LOCAL.links += 1
        LOCAL.links_length += len(link.text)

def phase_collected_texts_length(node, ignore_text:bool=False):
    """
    Compute the length of the text at the collected node level

    The herustic is to ignore the text length if the text length is less than 25 characters.
    This then pushes those vales up to all parents
    """
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
        # print("heere", COLLECTED.texts_length)

        current = current.parent
        if not current or current.name in [ "body", "html", ]:
            break

    for child in node.children:
        if child.name:
            phase_collected_texts_length(child, ignore_text=ignore_text)

def dump_LOCAL(node, depth=0):
    LOCAL = node.LOCAL

    print(
        f"{depth:2d} ",
        "  " * depth, node.name,
        f"{LOCAL.texts}/{LOCAL.texts_length}", 
        f"{LOCAL.links}/{LOCAL.links_length}", 
        (node.text or "")[:20]
    ) 

    for child in node.children:
        if child.name:
            dump_LOCAL(child, depth + 1)

def dump_COLLECTED(node, depth=0):
    COLLECTED = node.COLLECTED

    if COLLECTED.texts_length:
        print(
            f"{depth:2d} ",
            "  " * depth, node.name, 
              f"{COLLECTED.texts}/{COLLECTED.texts_length}", 
              f"{COLLECTED.links}/{COLLECTED.links_length}", 
              (node.text or "")[:40]) 

    for child in node.children:
        if child.name:
            dump_COLLECTED(child, depth + 1)

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
                print("   HEADER", header.name, header.text, file=sys.stderr)
                inserts.append(copy.copy(child))

        previous = current
        current = current.parent
        if not current or current.name in [ "body", "html", "xmain", "xarticle", ]:
            break

    for insert in reversed(inserts):
        best.insert(0, insert)
        
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

    for child in node.find_all(['script', 'noscript', 'iframe', 'style', 'link', 'svg', 'aside', "footer", "XXXheader", "nav"]):
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


def phase_detect_duplicates(node):
    """
    Detect duplicates in the tree
    """
    textd = {}

    for node in node.find_all():
        text = (node.text or "").strip()
        text = text
        if not ( node.name and text ):
            continue

        if node.name in [ "h1", "h2", "h3 "]:
            continue

        key = ( node.name, text )
        textd.setdefault(key, []).append(node)

    for key, value in textd.items():
        if len(value) <= 1:
            continue

        for node in value:
            node.decompose()

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
    def do_dump_local(soup):
        body = soup.find("body")
        # phase_detect_duplicates(body)
        phase_add_LOCAL(body)
        phase_local_texts_length(body)
        phase_local_links_length(body)
        dump_LOCAL(body)
        
    def do_dump_collected(soup):
        body = soup.find("body")
        # phase_detect_duplicates(body)
        phase_add_LOCAL(body)
        phase_local_texts_length(body)
        phase_local_links_length(body)

        phase_add_COLLECTED(body)
        phase_collected_texts_length(body)
        # print(body)
    
        best = best_COLLECTED(body, cutoff=0.4)
        dump_COLLECTED(best)

    def do_extract(soup):
        body = soup.find("body")
        # print("H1", soup.find("h1"), file=sys.stderr)
        # phase_detect_duplicates(body)
        phase_detect_hidden(body)
        # print("H1", soup.find("h1"), file=sys.stderr)
        phase_add_LOCAL(body)
        phase_local_texts_length(body)
        phase_local_links_length(body)

        phase_add_COLLECTED(body)
        phase_collected_texts_length(body)
        
        if True:
            best = best_COLLECTED(body, cutoff=0.4)
            # dump_COLLECTED(best)
            best = best_parents(best)

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
    FILENAME = "../../tests/data/in/cbc-mexico-1.html"
    FILENAME = "../../tests/data/in/globe.html"
    FILENAME = "../../tests/data/in/nationalpost.com.html"
    FILENAME = "../../tests/data/in/telegraph-sussex.html"
    FILENAME = "../../tests/data/in/the-hurricane-rubin-carter-denzel-washington.html"

    with open(FILENAME) as fin:
        ## soup = BeautifulSoup(fin, "lxml")
        soup = BeautifulSoup(fin, 'html.parser')


    # # print(soup.find("h1"))
    # do_dump_local(soup)
    # do_dump_collected(soup)
    do_extract(soup)

