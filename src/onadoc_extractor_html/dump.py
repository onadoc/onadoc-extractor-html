import sys
from typing import List
from bs4 import PageElement

import logging as logger

def dump(node:PageElement, field:str="COLLECTED", max_depth:int=999, file=sys.stdout):
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
            file=file,
        )

        for child in current.children:
            if child.name:
                _doit(child, depth=depth + 1)

    _doit(node)

def dump_COLLECTED(node:PageElement,max_depth:int=999, file=sys.stdout):
    dump(node, field="COLLECTED", max_depth=max_depth, file=file)

def dump_LOCAL(node:PageElement,max_depth:int=999, file=sys.stdout):
    dump(node, field="LOCAL", max_depth=max_depth, file=file)