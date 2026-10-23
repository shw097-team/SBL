"""Thin wrapper over cua-driver's CLI for the C21 plugin upload run.

Every action re-reads the window snapshot first, because element tokens are only valid for
the snapshot that produced them. `set_value` is attempted background-first and the
background_unavailable refusal is climbed exactly once to foreground, per the driver contract.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

DRIVER = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Cua", "cua-driver", "bin", "cua-driver.exe")
SESSION = "c21-r153"
PID = 15152
WIN = 2295894


def call(tool: str, args: dict) -> dict:
    args = dict(args)
    args.setdefault("session", SESSION)
    p = subprocess.run([DRIVER, "call", tool, "--json", json.dumps(args)],
                       capture_output=True, text=True, timeout=120)
    out = (p.stdout or "").strip()
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:400], "_err": (p.stderr or "")[:300], "_rc": p.returncode}


def state(pid: int = PID, win: int = WIN) -> dict:
    return call("get_window_state", {"pid": pid, "window_id": win})


def find(st: dict, needle: str, role: str | None = None) -> list[dict]:
    hits = []
    for e in st.get("elements") or []:
        lab = (e.get("label") or "") + " " + str(e.get("value") or "")
        if needle in lab and (role is None or e.get("role") == role):
            hits.append(e)
    return hits


def act(tool: str, token: str, **kw) -> dict:
    args = {"pid": PID, "element_token": token}
    args.update({k: v for k, v in kw.items() if v is not None})
    r = call(tool, args)
    if isinstance(r, dict) and r.get("code") == "background_unavailable":
        args["delivery_mode"] = "foreground"
        r = call(tool, args)
        r["_escalated"] = True
    return r


def set_url(url: str) -> dict:
    st = state()
    hits = find(st, "網址與搜尋列", "Edit")
    if not hits:
        return {"error": "address edit not found", "n": len(st.get("elements") or [])}
    r = act("set_value", hits[0]["element_token"], value=url)
    if isinstance(r, dict) and r.get("_escalated"):
        return r
    k = act("press_key", hits[0]["element_token"], key="return")
    r["_return"] = k
    return r


def click_label(needle: str, role: str | None = None, action: str | None = None) -> dict:
    st = state()
    hits = find(st, needle, role)
    if not hits:
        return {"error": "not found", "needle": needle, "labels": [e.get("label") for e in (st.get("elements") or [])][:40]}
    e = hits[0]
    r = act("click", e["element_token"], action=action)
    r["_clicked"] = {"label": e.get("label"), "role": e.get("role")}
    return r


def labels(limit: int = 60) -> list[str]:
    st = state()
    return [f"{e.get('role')}:{e.get('label')}" for e in (st.get("elements") or [])][:limit]


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "state":
        st = state()
        print(json.dumps({"n": len(st.get("elements") or []), "title": st.get("window_title"),
                          "labels": [f"{e.get('role')}:{e.get('label')}" for e in (st.get("elements") or [])][:40]},
                         ensure_ascii=False)[:1500])
    elif cmd == "url":
        print(json.dumps(set_url(sys.argv[2]), ensure_ascii=False)[:400])
    elif cmd == "click":
        print(json.dumps(click_label(sys.argv[2]), ensure_ascii=False)[:400])
    elif cmd == "wait":
        time.sleep(float(sys.argv[2]))
        print("waited")
