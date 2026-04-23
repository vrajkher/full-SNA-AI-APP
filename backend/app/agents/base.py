"""Base agent definition (OpenClaw-style)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.core import get_logger


class BaseAgent(ABC):
    """All Accotech AI agents derive from this class.

    Each concrete agent ships with three markdown files next to its
    implementation:

    - ``agent.md``  – role and goal
    - ``soul.md``   – behaviour and intelligence
    - ``skill.md``  – executable actions
    """

    name: str = "BaseAgent"

    def __init__(self) -> None:
        self.logger = get_logger(f"agent.{self.name}")

    @property
    def module_dir(self) -> Path:
        """Directory containing this agent's markdown identity files."""
        import sys

        module = sys.modules[self.__class__.__module__]
        return Path(module.__file__).resolve().parent  # type: ignore[arg-type]

    def identity(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for fname in ("agent.md", "soul.md", "skill.md"):
            fpath = self.module_dir / fname
            if fpath.exists():
                out[fname.replace(".md", "")] = fpath.read_text(encoding="utf-8")
        return out

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any: ...
