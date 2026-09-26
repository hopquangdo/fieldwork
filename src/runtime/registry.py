from __future__ import annotations

from importlib.metadata import entry_points

from runtime.feature import Feature

GROUP = "photo_sort.features"


def load_features() -> dict[str, Feature]:
    return {ep.name: ep.load()() for ep in entry_points(group=GROUP)}


def get_feature(name: str) -> Feature:
    feats = load_features()
    if name not in feats:
        raise KeyError(f"unknown feature {name!r}; available: {sorted(feats)}")
    return feats[name]
