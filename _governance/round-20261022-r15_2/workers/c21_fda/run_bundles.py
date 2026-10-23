"""Upload + install the remaining SBL plugin bundles through the ChatGPT plugins page via cua-driver.

Path proven on the first bundle: 外掛程式 -> 新增(expand) -> 上傳外掛程式封存檔 -> 點選上傳 -> native 開啟 dialog
(檔案名稱(N) set_value + 開啟(O) invoke) -> 新增外掛程式 -> plugin detail (Plugin_<id>) -> 安裝外掛程式.
Every step re-reads the window so element tokens always belong to a live snapshot.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

DRIVER = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Cua", "cua-driver", "bin", "cua-driver.exe")
SESSION = "c21-r153"
CHROME_PID = 15152
CHROME_WIN = 2295894
LOG: list[dict] = []


def call(tool: str, args: dict) -> dict:
    args = dict(args)
    args.setdefault("session", SESSION)
    p = subprocess.run([DRIVER, "call", tool, "--json", json.dumps(args)],
                       capture_output=True, text=True, timeout=180)
    out = (p.stdout or "").strip()
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:300], "_rc": p.returncode}


def tree() -> list[dict]:
    return (call("get_accessibility_tree", {}) or {}).get("windows") or []


def state(pid: int = CHROME_PID, win: int = CHROME_WIN) -> dict:
    return call("get_window_state", {"pid": pid, "window_id": win})


def pick(st: dict, needle: str, role: str | None = None, prefix: bool = False) -> dict | None:
    for e in st.get("elements") or []:
        lab = e.get("label") or ""
        if ((lab.startswith(needle) if prefix else needle in lab)
                and (role is None or e.get("role") == role)):
            return e
    return None


def act(tool: str, token: str, pid: int = CHROME_PID, **kw) -> dict:
    args = {"pid": pid, "element_token": token}
    args.update({k: v for k, v in kw.items() if v is not None})
    r = call(tool, args)
    if isinstance(r, dict) and r.get("code") == "background_unavailable":
        args["delivery_mode"] = "foreground"
        r = call(tool, args)
        r["_escalated"] = True
    return r


def url_of(st: dict) -> str:
    for e in st.get("elements") or []:
        if (e.get("label") or "") == "網址與搜尋列":
            return str(e.get("value") or "")
    return ""


def go(url: str) -> str:
    st = state()
    e = pick(st, "網址與搜尋列", "Edit")
    act("set_value", e["element_token"], value=url)
    act("press_key", e["element_token"], key="return")
    for _ in range(12):
        time.sleep(1.5)
        u = url_of(state())
        if url.split("//")[-1].split("/")[0] in u:
            return u
    return url_of(state())


def click_label(needle: str, role: str | None = None, prefix: bool = False) -> dict:
    st = state()
    e = pick(st, needle, role, prefix)
    if not e:
        return {"error": "label not found", "needle": needle}
    r = act("click", e["element_token"])
    r["_label"] = (e.get("label") or "")[:60]
    return r


def upload(zip_path: str) -> dict:
    steps = []
    go("https://chatgpt.com/plugins")
    time.sleep(2)
    st = state()
    add = pick(st, "新增", "Button")
    if not add:
        return {"error": "no 新增 button", "steps": steps}
    steps.append({"click": "新增", "r": act("click", add["element_token"], action="expand")})
    time.sleep(1.5)
    r = click_label("上傳外掛程式封存檔", "MenuItem")
    steps.append({"click": "上傳外掛程式封存檔", "r": r})
    if r.get("error"):
        return {"error": "menu item missing", "steps": steps}
    time.sleep(2)
    r = click_label("點選上傳", "Button")
    steps.append({"click": "點選上傳", "r": r})
    if r.get("error"):
        return {"error": "upload button missing", "steps": steps}
    dlg = None
    for _ in range(10):
        time.sleep(1)
        dlg = next((w for w in tree() if str(w.get("title")) in ("開啟", "Open")), None)
        if dlg:
            break
    if not dlg:
        return {"error": "native dialog never appeared", "steps": steps}
    dpid, dwin = dlg.get("pid"), dlg.get("window_id")
    dst = call("get_window_state", {"pid": dpid, "window_id": dwin})
    edit = pick(dst, "檔案名稱", "Edit")
    btn = None
    for e in dst.get("elements") or []:
        if (e.get("label") or "").startswith("開啟(") and e.get("role") == "Button":
            btn = e
            break
    steps.append({"set_value": zip_path, "r": call("set_value", {"pid": dpid, "element_token": edit["element_token"], "value": zip_path})})
    steps.append({"click": "開啟(O)", "r": call("click", {"pid": dpid, "element_token": btn["element_token"]})})
    time.sleep(3)
    r = click_label("新增外掛程式", "Button")
    steps.append({"click": "新增外掛程式", "r": r})
    pid = None
    for _ in range(15):
        time.sleep(2)
        st = state()
        m = re.search(r"Plugin_[0-9a-f]+", url_of(st) + " " + (st.get("tree_markdown") or ""))
        if m:
            pid = m.group(0)
            break
    inst = None
    if pid:
        st = state()
        btn = pick(st, "安裝外掛程式", "Button")
        if btn:
            inst = act("click", btn["element_token"])
            time.sleep(4)
            st = state()
            text = (st.get("tree_markdown") or "")
            inst = {"clicked": True, "installed_visible": "已安裝" in text}
    return {"plugin_id": pid, "url": url_of(state()), "install": inst, "steps": steps}


if __name__ == "__main__":
    out = {}
    for name, path in [("tpm", r"C:\tmp\sbl_plugins_r153\sbl-tpm-sp-0.1.1rc1.zip"),
                       ("challenge", r"C:\tmp\sbl_plugins_r153\sbl-external-challenge-sp-0.1.1rc1.zip")]:
        out[name] = upload(path)
        out[name].pop("steps", None)
        print(json.dumps({name: out[name]}, ensure_ascii=False), flush=True)
    print(json.dumps(out, ensure_ascii=False, indent=1))
