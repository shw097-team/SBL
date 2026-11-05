#!/usr/bin/env python3
"""WP-FHS-20 — the 192-cell registry, with real host raw for the cells W1 actually consumes.

The original identity of every cell (CellID, Kind, Mode, Host, legacy ON/OFF, source line) is taken
from the parsed source registry and preserved verbatim: this tool never re-derives a CellID and never
maps a legacy token to a boolean.

Per cell it records:
  * `applicability` — is that Host present on this machine (a real `--version` probe), is that Mode
    the one this wave runs in;
  * `host_raw`      — only for the cells W1 consumes, with the command, exit, version and digest that
    were actually observed here;
  * `state`         — `W1_RAW_OBSERVED`, `DELEGATED_TO_W3` (another host/mode belongs to a later
    wave), `HOST_ABSENT`, or `CELL_TOKEN_OWNER_ACK_MISSING` for the token half.

The token half is never claimed: flipping a cell's legacy ON/OFF is the original Cell Owner's act, so
every cell keeps `token_state=NOT_OBSERVED` and the typed gap
`WP-FHS-20.FIRST_FAIL:CELL_TOKEN_OWNER_ACK_MISSING` where the token is what would be measured.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOST_BINARIES = {"Hermes Agent": "hermes", "Codex": "codex",
                 "Claude Code": "claude", "DeepSeek Harness": "deepseek"}
W1_HOST = "Hermes Agent"
W1_MODE = "STANDALONE"


def sha_file(p: str | Path) -> str:
    path = Path(p)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def probe_host(binary: str) -> dict:
    found = shutil.which(binary)
    if not found:
        return {"present": False, "binary": binary}
    out = {"present": True, "binary": binary, "path": found, "sha256": sha_file(found)}
    try:
        v = subprocess.run([found, "--version"], capture_output=True, text=True, timeout=40)
        out.update(exit=v.returncode, version=(v.stdout or v.stderr).strip().splitlines()[0][:160])
    except Exception as exc:
        out.update(exit=None, version_error=str(exc)[:160])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True, help="cells_192.json produced from the W1 source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile-config",
                    default=r"D:/Hermes-Recovery/live22/profiles/hgk-governed/config.yaml")
    args = ap.parse_args()

    src = json.loads(Path(args.cells).read_text(encoding="utf-8"))
    cells = src["cells"]
    cfg = Path(args.profile_config)
    host_probe = {h: probe_host(b) for h, b in HOST_BINARIES.items()}

    provider = {}
    if cfg.is_file():
        text = cfg.read_text(encoding="utf-8")
        provider = {"config": str(cfg), "sha256": sha_file(cfg),
                    "model": next((l.split(":", 1)[1].strip() for l in text.splitlines()
                                   if l.strip().startswith("default:")), ""),
                    "provider": next((l.split(":", 1)[1].strip() for l in text.splitlines()
                                      if l.strip().startswith("provider:")), "")}

    out_cells = []
    for c in cells:
        host = c["host"]
        present = host_probe.get(host, {}).get("present", False)
        consumed = host == W1_HOST and c["mode"] == W1_MODE
        rec = {
            "cell_id": c["cell_id"],
            "kind": c["kind"],
            "kind_qualifier": c.get("kind_qualifier"),
            "mode": c["mode"],
            "host": host,
            "legacy_raw_token": c["legacy_raw_token"],
            "source": {"file": "09B_KIND_MODE_HOST_192(4).md", "line": c.get("source_line"),
                       "refs": c.get("source_refs")},
            "applicability": {
                "host_present_on_this_machine": present,
                "mode_is_this_wave": c["mode"] == W1_MODE,
                "consumed_by_w1": consumed,
            },
            "nofit": None,
            "token_state": "NOT_OBSERVED",
            "token_first_fail": "WP-FHS-20.FIRST_FAIL:CELL_TOKEN_OWNER_ACK_MISSING",
        }
        if consumed:
            hraw = host_probe.get(W1_HOST, {})
            rec["host_raw"] = {
                "reader": "hermes --version + installed path digest + profile config digest",
                "command": f"{hraw.get('path')} --version",
                "exit": hraw.get("exit"),
                "version": hraw.get("version"),
                "binary_sha256": hraw.get("sha256"),
                "python": sys.version.split()[0],
                "os": platform.platform(),
                "profile": provider,
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "evidence_class": "HOST_BOUND_LOCAL",
            }
            rec["state"] = "W1_RAW_OBSERVED"
        elif not present:
            rec["state"] = "HOST_ABSENT"
        else:
            rec["state"] = "DELEGATED_TO_W3"
        out_cells.append(rec)

    states = {}
    for r in out_cells:
        states[r["state"]] = states.get(r["state"], 0) + 1
    record = {
        "schema": "FHS.W1.WP20.CellHostRaw@1",
        "source_registry": {"path": args.cells, "sha256": sha_file(args.cells),
                            "parsed_count": src.get("parsed_count"),
                            "source_sha256": (src.get("generated_from") or {}).get("sha256")},
        "hosts_probed": host_probe,
        "cells": out_cells,
        "counts": {"cells": len(out_cells), "states": states,
                   "w1_consumed": sum(1 for r in out_cells if r["applicability"]["consumed_by_w1"]),
                   "delegated_to_w3": states.get("DELEGATED_TO_W3", 0)},
        "claim_ceiling": "HOST_BOUND_FOR_HERMES_STANDALONE_CELLS__TOKEN_NOT_OBSERVED",
        "not_claimed": ["cell token ON/OFF mapping", "other hosts' raw", "W3 worlds", "release"],
    }
    record["registry_sha256"] = hashlib.sha256(
        json.dumps({k: v for k, v in record.items() if k != "registry_sha256"},
                   sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": record["counts"],
                      "hosts": {h: v.get("present") for h, v in host_probe.items()},
                      "sha256": record["registry_sha256"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
