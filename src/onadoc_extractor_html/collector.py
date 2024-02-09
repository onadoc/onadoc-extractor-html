import dataclasses
from bs4 import BeautifulSoup
import sys

ignores = [
    "script",
    "style"
    "svg",
    "noscript",
    "picture",
    "iframe",
    "object",
]
pushes = [
    "li",
    "em",
    "i",
    "b",
    "span",
    "strong",
    "a",
    "abbr",
    "acronym",
    "address",
]

@dataclasses.dataclass
class Collector:
    texts: int = 0
    text_length: int = 0

    counts: dict = dataclasses.field(default_factory=dict)

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

def phase_local_text_length(node, ignore_text:bool=False):
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
        LOCAL.text_length += len(text)

    for child in node.children:
        if child.name:
            phase_local_text_length(child, ignore_text=ignore_text)

def phase_collected_text_length(node):
    """
    Compute the length of the text at the collected node level

    The herustic is to ignore the text length if the text length is less than 25 characters.
    This then pushes those vales up to all parents
    """
    LOCAL = node.LOCAL

    if LOCAL.text_length >= 25:
        current = node
        while True:
            COLLECTED = current.COLLECTED
            COLLECTED.texts += LOCAL.texts
            COLLECTED.text_length += LOCAL.text_length
            # print("heere", COLLECTED.text_length)

            current = current.parent
            if not current or current.name in [ "body", "html", ]:
                break

    for child in node.children:
        if child.name:
            phase_collected_text_length(child)

def dump_LOCAL(node, depth=0):
    print("  " * depth, node.name, node.LOCAL.texts, node.LOCAL.text_length) 

    for child in node.children:
        if child.name:
            dump_LOCAL(child, depth + 1)

def dump_COLLECTED(node, depth=0):
    COLLECTED = node.COLLECTED

    if COLLECTED.text_length:
        print("  " * depth, node.name, COLLECTED.texts, COLLECTED.text_length) 

    for child in node.children:
        if child.name:
            dump_COLLECTED(child, depth + 1)

def best_COLLECTED(node, depth=0, cutoff:float=0.5, verbose:bool=False):
    best = None

    for child in node.children:
        if verbose and hasattr(child, "COLLECTED") and child.COLLECTED.text_length:
            print(" " * depth, child.name, child.COLLECTED.text_length, file=sys.stderr)

        if not child.name:
            continue
        if not child.COLLECTED.text_length:
            continue

        if not best:
            best = child
        elif child.COLLECTED.text_length > best.COLLECTED.text_length:
            best = child

    if best:
        if verbose:
            print(" " * depth, best.name, best.COLLECTED.text_length, file=sys.stderr)

        best_child = best_COLLECTED(best, depth + 1)
        if not best_child:
            return best
        
        if best_child.COLLECTED.text_length < best.COLLECTED.text_length * cutoff:
            return best
        else:
            return best_child
    
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

if __name__ == '__main__'
    # with open("substack.html") as fin:
    with open("globe.html") as fin:
        soup = BeautifulSoup(fin, "lxml")

    body = soup.find("body")
    phase_add_LOCAL(body)
    phase_local_text_length(body)
    # dump_LOCAL(body)

    if True:
        phase_add_COLLECTED(body)
        phase_collected_text_length(body)
        # dump_COLLECTED(body)
        best = best_COLLECTED(body)
        best = best.parent.parent
        util_strip_node(best)
        # print(best.name)
        print("""
    <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
        """)
        print(best.prettify())
        print("""
        </body>
    """)
    # collect(body)
    # dump(body)
