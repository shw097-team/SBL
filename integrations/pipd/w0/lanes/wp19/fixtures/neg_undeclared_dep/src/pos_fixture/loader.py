"""Loader that imports a library the manifest never declares."""

import pathlib

import yaml


def load(path):
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
