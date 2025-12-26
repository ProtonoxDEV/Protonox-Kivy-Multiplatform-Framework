"""UI-IR helpers for runtime consumption (diff + apply)."""

from .ui_ir_types import UIComponent, UIScreen, UIModel, load_ui_model
from .diff import PatchOp, diff_models
from .apply import apply_patch_ops

__all__ = [
    "UIComponent",
    "UIScreen",
    "UIModel",
    "PatchOp",
    "diff_models",
    "apply_patch_ops",
    "load_ui_model",
]
