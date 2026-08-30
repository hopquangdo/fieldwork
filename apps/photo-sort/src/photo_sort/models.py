from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Photo:
    path: str            # relative to the station root, forward slashes
    prefix: str          # parsed component prefix ("" if timestamp-only)
    is_primary: bool

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def folder(self) -> str:
        return self.path.rsplit("/", 1)[0] if "/" in self.path else ""


@dataclass(frozen=True)
class Move:
    src: str                     # relative to station root
    dest_dir: str                # relative to station root
    new_name: str | None = None  # rename on move (SOP filename convention)
    convert: bool = False        # re-encode bytes to JPEG (e.g. .png screenshot -> .jpg)
