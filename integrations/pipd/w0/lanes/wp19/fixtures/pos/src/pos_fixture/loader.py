"""Loader used by the positive tree (stdlib only)."""

import pathlib


def load(path):
    return pathlib.Path(path).read_text(encoding="utf-8")
