"""Mapping of Protonox extensions to compatibility warnings.

The fork stays dormant unless a developer opts in. When enabled, this module
helps surface what changed and how to disable it. It does not alter runtime
behaviour by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CompatWarning:
    key: str
    message: str
    flag: str
    mitigation: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "key": self.key,
            "message": self.message,
            "flag": self.flag,
            "mitigation": self.mitigation,
        }


COMPAT_WARNINGS: List[CompatWarning] = [
    CompatWarning(
        key="layout_telemetry",
        message="Layout telemetry is opt-in; disable PROTONOX_LAYOUT_TELEMETRY to run vanilla behaviour.",
        flag="PROTONOX_LAYOUT_TELEMETRY",
        mitigation="Unset the flag or avoid calling telemetry helpers.",
    ),
    CompatWarning(
        key="ui_observability",
        message="UI observability exports extra metadata but does not mutate layouts.",
        flag="PROTONOX_UI_OBSERVABILITY",
        mitigation="Leave disabled to preserve exact upstream behaviour.",
    ),
    CompatWarning(
        key="runtime_diagnostics",
        message="Runtime diagnostics read GPU/GL/Window state for doctor reports only.",
        flag="PROTONOX_RUNTIME_DIAGNOSTICS",
        mitigation="Unset to avoid extra probing; no core changes either way.",
    ),
]

__all__ = ["CompatWarning", "COMPAT_WARNINGS"]
