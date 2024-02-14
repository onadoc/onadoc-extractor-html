from bs4 import PageElement

def mutate_hidden(node:PageElement):
    """
    Detect node with 'hidden' class and remove them. Very tailwind
    """
    for hidden in node.find_all(class_="hidden"):
        hidden.decompose()

