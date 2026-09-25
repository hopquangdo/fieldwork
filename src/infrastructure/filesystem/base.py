"""Tool framework.

Every filesystem action is an :class:`FsTool` — a small class carrying ``name`` /
``description`` and an ``execute`` method. Instances are **callable**, so ordinary
code just does ``move_file(src, dst)``.
"""
from __future__ import annotations

from typing import ClassVar


class FsTool:
    """One filesystem operation. Subclasses set the two class attrs + ``execute``."""

    name: ClassVar[str]
    description: ClassVar[str]

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{type(self).__name__} {self.name!r}>"
