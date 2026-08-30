"""Thin wrapper so `photo-sort <in> <out>` works without typing `graphrun run photo-sort`."""
from __future__ import annotations

import sys

from graphrun.cli import main as graphrun_main


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    return graphrun_main(["run", "photo-sort", *argv])


if __name__ == "__main__":
    sys.exit(main())
