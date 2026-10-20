"""SBL v0.1 ``sbl-todo`` command surface.

Deliberately empty: importing ``main`` here would make ``python -m sbl_cli.sbl_todo``
load the module twice (package __init__ then __main__) and emit a RuntimeWarning.
Use ``from sbl_cli.sbl_todo import main`` or the ``sbl-todo`` console script.
"""
