"""Naive tree diff for UI-IR suitable for live patching.

This keeps the diff small and predictable: we walk children by index and emit
simple operations. If structures diverge too much, higher layers can fallback
to a full rebuild.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .ui_ir_types import UIComponent, UIModel


@dataclass
class PatchOp:
    op: str
    path: Tuple[int, ...]
    payload: Dict[str, object]


def _match_children(old_children: List[UIComponent], new_children: List[UIComponent]) -> List[Tuple[int, int]]:
    matches: List[Tuple[int, int]] = []
    used_new: set[int] = set()
    # Try role/id/kind to align
    for i, old_child in enumerate(old_children):
        for j, new_child in enumerate(new_children):
            if j in used_new:
                continue
            if (old_child.role and old_child.role == new_child.role) or (old_child.kind == new_child.kind and old_child.text == new_child.text):
                matches.append((i, j))
                used_new.add(j)
                break
    return matches


def _diff_component(old: UIComponent, new: UIComponent, path: Tuple[int, ...], ops: List[PatchOp]) -> None:
    if old.kind != new.kind:
        ops.append(PatchOp(op="replace_subtree", path=path, payload={"component": new}))
        return
    if (old.text or "") != (new.text or ""):
        ops.append(PatchOp(op="update_text", path=path, payload={"text": new.text}))
    if (old.props or {}) != (new.props or {}):
        ops.append(PatchOp(op="update_props", path=path, payload={"props": new.props}))

    matches = _match_children(old.children, new.children)
    matched_old = {i for i, _ in matches}
    matched_new = {j for _, j in matches}

    # Removals
    for idx, child in enumerate(old.children):
        if idx not in matched_old:
            ops.append(PatchOp(op="remove", path=path + (idx,), payload={}))

    # Adds and diffs
    for idx, child in enumerate(new.children):
        if idx not in matched_new:
            ops.append(PatchOp(op="add", path=path + (idx,), payload={"component": child}))
        else:
            old_idx = next(i for i, j in matches if j == idx)
            if old_idx != idx:
                ops.append(PatchOp(op="move", path=path + (old_idx,), payload={"to": idx}))
            _diff_component(old.children[old_idx], child, path + (idx,), ops)


def diff_models(old: UIModel, new: UIModel) -> List[PatchOp]:
    ops: List[PatchOp] = []
    old_screens = {s.name: s for s in old.screens}
    new_screens = {s.name: s for s in new.screens}

    removed = set(old_screens) - set(new_screens)
    added = set(new_screens) - set(old_screens)

    for name in removed:
        ops.append(PatchOp(op="remove_screen", path=(), payload={"screen": name}))
    for name in added:
        ops.append(PatchOp(op="add_screen", path=(), payload={"screen": new_screens[name]}))

    for name in set(old_screens) & set(new_screens):
        old_root = old_screens[name].components[0] if old_screens[name].components else UIComponent("root", "widget")
        new_root = new_screens[name].components[0] if new_screens[name].components else UIComponent("root", "widget")
        _diff_component(old_root, new_root, (name,), ops)
    return ops
