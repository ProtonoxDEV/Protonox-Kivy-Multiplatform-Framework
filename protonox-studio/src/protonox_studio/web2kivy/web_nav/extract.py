"""Lightweight navigation extraction from HTML fragments.

This is intentionally heuristic: it surfaces candidate routes for human
confirmation rather than mutating navigation automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import List, Set


@dataclass
class NavEdge:
    source: str
    target: str
    label: str | None = None


@dataclass
class NavGraph:
    edges: List[NavEdge] = field(default_factory=list)
    routes: Set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "routes": sorted(self.routes),
            "edges": [edge.__dict__ for edge in self.edges],
        }


class _LinkParser(HTMLParser):
    def __init__(self, base_route: str = "/"):
        super().__init__()
        self.base_route = base_route
        self.routes: Set[str] = set()
        self.edges: List[NavEdge] = []
        self._current_text: List[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href and href.startswith("/"):
                self._current_href = href
                self.routes.add(href)

    def handle_data(self, data: str):
        if self._current_href:
            self._current_text.append(data.strip())

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._current_href:
            label = " ".join([chunk for chunk in self._current_text if chunk]).strip() or None
            self.edges.append(NavEdge(source=self.base_route, target=self._current_href, label=label))
            self._current_href = None
            self._current_text = []


def extract_navigation(html: str, base_route: str = "/") -> NavGraph:
    parser = _LinkParser(base_route=base_route)
    parser.feed(html)
    graph = NavGraph(edges=parser.edges, routes=parser.routes | {base_route})
    return graph


__all__ = ["NavGraph", "NavEdge", "extract_navigation"]
