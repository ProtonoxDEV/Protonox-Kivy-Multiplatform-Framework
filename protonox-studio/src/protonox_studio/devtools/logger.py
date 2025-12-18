"""Prefixed logging helpers to keep dev-time logs actionable."""

from __future__ import annotations


from kivy.logger import Logger

PREFIXES = {
    "hotreload": "[HOTRELOAD]",
    "build": "[BUILD]",
    "kv": "[KV]",
    "ui": "[UI]",
}


class _PrefixedLogger:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def _fmt(self, message: str) -> str:
        return f"{self.prefix} {message}" if self.prefix else message

    def info(self, message: str) -> None:
        Logger.info(self._fmt(message))

    def warning(self, message: str) -> None:
        Logger.warning(self._fmt(message))

    def debug(self, message: str) -> None:
        Logger.debug(self._fmt(message))

    def error(self, message: str) -> None:
        Logger.error(self._fmt(message))


def prefixed_logger(channel: str) -> _PrefixedLogger:
    """Return a logger with a static prefix label."""

    prefix = PREFIXES.get(channel, f"[{channel.upper()}]")
    return _PrefixedLogger(prefix=prefix)


__all__ = ["prefixed_logger"]
