"""Imports one declared third-party library plus stdlib only."""

import json
import os

import jsonschema

from .util import helper


def validate(document, schema):
    jsonschema.validate(instance=document, schema=schema)
    return helper(os.path.basename("x.json")) + json.dumps(document)[:0]
