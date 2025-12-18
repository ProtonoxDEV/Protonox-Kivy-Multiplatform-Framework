"""KV strict mode helpers (opt-in, dev-only)."""

from __future__ import annotations

from typing import Dict, List, Tuple

from kivy.lang import Builder
from kivy.logger import Logger

from protonox_studio.flags import is_enabled
from protonox_studio.devtools.logger import prefixed_logger

KV_LOG = prefixed_logger("kv")


def _find_duplicate_ids(source: str) -> List[Tuple[str, int]]:
    seen: Dict[str, int] = {}
    duplicates: List[Tuple[str, int]] = []
    for idx, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("id:"):
            continue
        _, _, ident = stripped.partition(":")
        ident = ident.strip()
        if not ident:
            continue
        if ident in seen:
            duplicates.append((ident, idx))
        else:
            seen[ident] = idx
    return duplicates


def _report_duplicate_ids(duplicates: List[Tuple[str, int]], filename: str) -> None:
    if not duplicates:
        return
    formatted = ", ".join([f"{name} (line {line})" for name, line in duplicates])
    raise ValueError(f"Duplicate KV ids detected in {filename}: {formatted}")


def _strict_load_string(source: str, filename: str, original_loader) -> None:
    duplicates = _find_duplicate_ids(source)
    _report_duplicate_ids(duplicates, filename)
    original_loader(source, filename=filename)


def enable_kv_strict_mode() -> None:
    """Enable strict KV validation using the PROTONOX_KV_STRICT flag."""

    if not is_enabled("KV_STRICT", False):
        return

    KV_LOG.info("KV strict mode enabled (duplicate id checks + parser errors raised)")

    original_load_file = Builder.load_file
    original_load_string = Builder.load_string

    def _safe_load_file(filename, **kwargs):  # type: ignore[override]
        try:
            with open(filename, "r", encoding="utf-8") as fh:
                source = fh.read()
        except FileNotFoundError:
            return original_load_file(filename, **kwargs)
        _strict_load_string(source, filename=filename, original_loader=original_load_string)

    def _safe_load_string(source, **kwargs):  # type: ignore[override]
        filename = kwargs.get("filename", "<string>")
        _strict_load_string(source, filename, original_loader=original_load_string)

    Builder.load_file = _safe_load_file  # type: ignore[assignment]
    Builder.load_string = _safe_load_string  # type: ignore[assignment]

    # Trigger a no-op load to surface immediate parser issues during bootstrap
    try:
        Builder.load_string("#:kivy 2.3.1", filename="<protonox-strict-check>")
    except Exception as exc:
        Logger.warning(f"[KV] Strict preflight raised: {exc}")


__all__ = ["enable_kv_strict_mode"]
