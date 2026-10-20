"""``sbl-todo`` CLI: one JSON object on stdout per invocation."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

SCHEMA = "SBL-TODO-STATE/1"
DATA_FILE = "data.json"
TMP_FILE = "data.json.tmp"

_EXIT_BY_CODE = {
    "SBL_E_EMPTY_TITLE": 2,
    "SBL_E_DUPLICATE_TITLE": 3,
    "SBL_E_BAD_STATE": 4,
    "SBL_E_FOREIGN_FILES": 5,
}


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _emit_error(error: SBLError, exit_code: int | None = None) -> int:
    _emit(error.as_dict())
    return _EXIT_BY_CODE.get(error.code, 4) if exit_code is None else exit_code


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _parse_global(argv: list[str]) -> tuple[Path, list[str]]:
    """Consume ``--data-dir`` options that precede the subcommand."""

    rest = list(argv)
    data_dir: str | None = None
    while rest:
        token = rest[0]
        if token == "--data-dir":
            if len(rest) < 2:
                raise SBLError(
                    "SBL_E_BAD_STATE", "--data-dir requires a path argument"
                )
            data_dir = rest[1]
            rest = rest[2:]
        elif token.startswith("--data-dir="):
            data_dir = token.split("=", 1)[1]
            rest = rest[1:]
        else:
            break
    if data_dir is None:
        env_home = os.environ.get("SBL_TODO_HOME")
        data_dir = env_home if env_home else str(Path.home() / ".sbl_todo")
    if not str(data_dir).strip():
        raise SBLError("SBL_E_BAD_STATE", "data dir must not be empty")
    return Path(data_dir).expanduser().resolve(), rest


def _flag_value(args: list[str], name: str) -> str | None:
    """Return the single value for ``name``; refuse anything unexpected."""

    value: str | None = None
    index = 0
    while index < len(args):
        token = args[index]
        if token == name:
            if index + 1 >= len(args):
                raise SBLError(
                    "SBL_E_BAD_STATE", f"{name} requires a value argument"
                )
            value = args[index + 1]
            index += 2
            continue
        if token.startswith(name + "="):
            value = token.split("=", 1)[1]
            index += 1
            continue
        raise SBLError(
            "SBL_E_BAD_STATE", f"unexpected argument {token!r}", {"args": args}
        )
    return value


def _only_flags(args: list[str], allowed: tuple[str, ...]) -> set[str]:
    """Accept only the listed boolean flags; refuse everything else."""

    seen: set[str] = set()
    for token in args:
        if token not in allowed:
            raise SBLError(
                "SBL_E_BAD_STATE", f"unexpected argument {token!r}", {"args": args}
            )
        seen.add(token)
    return seen


def _state_path(data_dir: Path) -> Path:
    return data_dir / DATA_FILE


def _load_state(data_dir: Path) -> dict[str, Any]:
    path = _state_path(data_dir)
    if not path.is_file():
        return {"schema": SCHEMA, "items": []}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "state file is unreadable",
            {"path": str(path), "error": str(exc)},
        ) from exc
    if (
        not isinstance(loaded, dict)
        or loaded.get("schema") != SCHEMA
        or not isinstance(loaded.get("items"), list)
    ):
        raise SBLError(
            "SBL_E_BAD_STATE",
            "state file does not match SBL-TODO-STATE/1",
            {"path": str(path)},
        )
    return loaded


def _save_state(data_dir: Path, state: dict[str, Any]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    target = _state_path(data_dir)
    tmp = data_dir / TMP_FILE
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, target)


def _cmd_init(data_dir: Path, args: list[str]) -> dict[str, Any]:
    _only_flags(args, ())
    data_dir.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "data_dir": str(data_dir)}


def _cmd_add(data_dir: Path, args: list[str]) -> dict[str, Any]:
    raw_title = _flag_value(args, "--title")
    if raw_title is None:
        raise SBLError("SBL_E_BAD_STATE", "add requires --title")
    title = raw_title.strip()
    if not title:
        raise SBLError(
            "SBL_E_EMPTY_TITLE", "title must not be empty", {"title": raw_title}
        )
    state = _load_state(data_dir)
    item_id = "T-" + sha256(title.encode("utf-8")).hexdigest()[:10]
    for existing in state["items"]:
        if not isinstance(existing, dict):
            continue
        if existing.get("id") == item_id or str(
            existing.get("title", "")
        ).strip() == title:
            raise SBLError(
                "SBL_E_DUPLICATE_TITLE",
                "an item with this title already exists",
                {"id": item_id, "title": title},
            )
    item = {"id": item_id, "title": title, "status": "open", "created": _now()}
    state["items"].append(item)
    _save_state(data_dir, state)
    return {"ok": True, "item": dict(item), "status": "open"}


def _cmd_list(data_dir: Path, args: list[str]) -> dict[str, Any]:
    flags = _only_flags(args, ("--json",))
    state = _load_state(data_dir)
    items = [dict(item) for item in state["items"] if isinstance(item, dict)]
    if "--json" not in flags:
        for item in items:
            sys.stderr.write(
                f"{item.get('id')}\t{item.get('status')}\t{item.get('title')}\n"
            )
        sys.stderr.flush()
    return {"ok": True, "items": items, "count": len(items)}


def _cmd_remove(data_dir: Path, args: list[str]) -> dict[str, Any]:
    item_id = _flag_value(args, "--id")
    if item_id is None:
        raise SBLError("SBL_E_BAD_STATE", "remove requires --id")
    state = _load_state(data_dir)
    kept = [
        item
        for item in state["items"]
        if not (isinstance(item, dict) and item.get("id") == item_id)
    ]
    if len(kept) == len(state["items"]):
        raise SBLError(
            "SBL_E_BAD_STATE", "no item with this id", {"id": item_id}
        )
    state["items"] = kept
    _save_state(data_dir, state)
    return {"ok": True, "removed": item_id}


def _cmd_uninstall(data_dir: Path, args: list[str]) -> dict[str, Any]:
    flags = _only_flags(args, ("--yes",))
    if "--yes" not in flags:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "uninstall requires --yes confirmation",
            {"data_dir": str(data_dir)},
        )
    if data_dir.exists():
        if not data_dir.is_dir():
            raise SBLError(
                "SBL_E_BAD_STATE",
                "data dir is not a directory",
                {"data_dir": str(data_dir)},
            )
        foreign = sorted(
            entry.name for entry in data_dir.iterdir() if entry.name != DATA_FILE
        )
        if foreign:
            raise SBLError(
                "SBL_E_FOREIGN_FILES",
                "data dir contains files that sbl-todo does not own",
                {"data_dir": str(data_dir), "files": foreign},
            )
        target = _state_path(data_dir)
        if target.exists():
            target.unlink()
        try:
            data_dir.rmdir()
        except OSError as exc:
            raise SBLError(
                "SBL_E_FOREIGN_FILES",
                "data dir could not be removed",
                {"data_dir": str(data_dir), "error": str(exc)},
            ) from exc
    return {"ok": True, "uninstalled": True}


_COMMANDS = {
    "init": _cmd_init,
    "add": _cmd_add,
    "list": _cmd_list,
    "remove": _cmd_remove,
    "uninstall": _cmd_uninstall,
}


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        data_dir, rest = _parse_global(raw)
    except SBLError as exc:
        return _emit_error(exc, 2)
    if not rest:
        return _emit_error(
            SBLError("SBL_E_BAD_STATE", "a subcommand is required"), 2
        )
    command, args = rest[0], rest[1:]
    handler = _COMMANDS.get(command)
    if handler is None:
        return _emit_error(
            SBLError(
                "SBL_E_BAD_STATE",
                f"unknown subcommand {command!r}",
                {"command": command, "known": sorted(_COMMANDS)},
            ),
            2,
        )
    try:
        payload = handler(data_dir, args)
    except SBLError as exc:
        return _emit_error(exc, 2 if exc.code in ("SBL_E_EMPTY_TITLE",) else None)
    except OSError as exc:
        return _emit_error(
            SBLError(
                "SBL_E_BAD_STATE",
                "filesystem failure",
                {"data_dir": str(data_dir), "error": str(exc)},
            )
        )
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
