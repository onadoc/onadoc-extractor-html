import sys

from bs4 import PageElement

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

    if node.name not in pushes:
        return node
    
    parent = node.parent

    for child in node.children:
        parent.append(child)

    node.decompose()

    return best_parents(parent)
