"""UI-IR normalization helpers.

The normalizer ensures identifiers are stable, structural hashes are
available, and placeholder-safe defaults exist even when the source HTML
is incomplete. The goal is a predictable IR that downstream exporters
and validators can consume without mutating the user's application code.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, MutableMapping


_IDENTIFIER_RE = re.compile(r"[^a-zA-Z0-9_]+")


def sanitize_identifier(raw: str) -> str:
    sanitized = _IDENTIFIER_RE.sub("_", raw).strip("_")
    if not sanitized:
        return "node"
    return sanitized.lower()


def _hash_payload(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass
class NormalizedNode:
    role: str
    bounds: Dict[str, float]
    children: list["NormalizedNode"] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "bounds": self.bounds,
            "children": [child.to_dict() for child in self.children],
            "meta": self.meta,
        }


@dataclass
class NormalizedUIModel:
    root: NormalizedNode
    viewport: Dict[str, int]
    assets: Dict[str, Any]
    routes: Iterable[str]
    layout_fingerprint: str
    route_signature: str | None = None

    def to_dict(self) -> dict:
        return {
            "root": self.root.to_dict(),
            "viewport": self.viewport,
            "assets": self.assets,
            "routes": list(self.routes),
            "layout_fingerprint": self.layout_fingerprint,
            "route_signature": self.route_signature,
        }


def _ensure_node(payload: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    payload.setdefault("role", payload.get("type", "unknown"))
    payload.setdefault("bounds", {"x": 0, "y": 0, "width": 0, "height": 0})
    payload.setdefault("children", [])
    payload.setdefault("meta", {})
    identifier = payload.get("id") or payload.get("identifier") or ""
    payload["id"] = sanitize_identifier(str(identifier) or payload["role"])
    return payload


def _normalize_tree(payload: MutableMapping[str, Any]) -> NormalizedNode:
    payload = _ensure_node(payload)
    children = [_normalize_tree(child) for child in payload.get("children", [])]
    meta = payload.get("meta") or {}
    meta.setdefault("source_identifier", payload.get("identifier"))
    meta.setdefault("role", payload.get("role"))
    return NormalizedNode(role=payload["role"], bounds=payload["bounds"], children=children, meta=meta)


def normalize_ui_model(ui_model: MutableMapping[str, Any]) -> NormalizedUIModel:
    viewport = ui_model.get("viewport") or {"width": 1280, "height": 720}
    assets = ui_model.get("assets") or {}
    routes = ui_model.get("routes") or ["/"]

    root_payload = ui_model.get("root") or ui_model.get("tree") or {}
    normalized_root = _normalize_tree(root_payload)

    fingerprint = _hash_payload(normalized_root.to_dict())
    route_signature = None
    if assets or ui_model.get("entrypoint"):
        signature_payload = {"assets": assets, "entrypoint": ui_model.get("entrypoint")}
        route_signature = _hash_payload(signature_payload)

    return NormalizedUIModel(
        root=normalized_root,
        viewport=viewport,
        assets=assets,
        routes=routes,
        layout_fingerprint=fingerprint,
        route_signature=route_signature,
    )


__all__ = [
    "normalize_ui_model",
    "NormalizedUIModel",
    "NormalizedNode",
    "sanitize_identifier",
]
