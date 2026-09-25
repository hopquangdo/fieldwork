from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from langgraph.graph import StateGraph

from config.loader import Config


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    summary: str
    default_rules: str | None = None    # path relative to the feature package directory


class Feature(abc.ABC):
    spec: ClassVar[FeatureSpec]

    @abc.abstractmethod
    def build_graph(self, config: Config) -> StateGraph:
        """Return an uncompiled StateGraph. graphrun compiles + runs it."""

    def rules_path(self) -> Path | None:
        if not self.spec.default_rules:
            return None
        return Path(inspect.getfile(type(self))).resolve().parent / self.spec.default_rules

    def rules_for(self, input_path: Path) -> Path | None:
        """Which rules file to use for this input (peeked before Config is loaded).

        Override to auto-select (e.g. by reading a metadata file). Default: ``rules_path()``.
        """
        return self.rules_path()
