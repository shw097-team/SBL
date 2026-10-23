"""Capture the C21 evidence chain for the three installed bundles.

For each plugin: navigate to its detail page, take a window snapshot, and persist the raw tree plus the
fields the check needs (id, title, version, shortDescription, installed marker). Then capture the installed-
plugins list as the readback that all three are present at once.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import time

import run_bundles as rb

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence")
IDS = {
    "sbl-commander-sp": "Plugin_69dd1cac627c8191ab46fb465555aa22",
    "sbl-tpm-sp": "Plugin_43c6e757a0d8819183dc3486d166c24f",
    "sbl-external-challenge-sp": "Plugin_2ac58bf7ca888191b24ba74c22e352fb",
}


def fields(st: dict) -> dict:
    t = st.get("tree_markdown") or ""
    out = {"installed_marker": "已安裝" in t, "url": rb.url_of(st),
           "document_title": next((e.get("label") for e in st.get("elements") or []
                                   if e.get("role") == "Document"), None)}
    m = re.search(r"版本[\s\S]{0,80}?(\d+\.\d+\.\d+[A-Za-z0-9.\-]*)", t)
    out["version"] = m.group(1) if m else None
    m = re.search(r"By [^\n•]+•\s*([^\n]{0,160})", t)
    out["byline"] = m.group(1).strip() if m else None
    return out


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    report = {"schema": "SBL-C21-HOST-EVIDENCE/1",
              "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "account": "shw097 / 鬼人馬 (Plus)",
              "driver": "cua-driver CLI (session c21-r153), background-first; one foreground return for navigation",
              "bundles": {}}
    for name, pid in IDS.items():
        url = f"https://chatgpt.com/plugins/{pid}"
        got = rb.go(url)
        time.sleep(4)
        st = rb.state()
        f = fields(st)
        path = os.path.join(OUT, f"{name}.tree.md")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"<!-- {url} captured {report['captured_at_utc']} -->\n")
            fh.write(st.get("tree_markdown") or "")
        report["bundles"][name] = {"host_returned_url": url, "host_returned_plugin_id": pid,
                                   "navigated_to": got, **f,
                                   "detail_tree_ref": os.path.relpath(path, OUT)}
        print(json.dumps({name: report["bundles"][name]}, ensure_ascii=False), flush=True)

    rb.go("https://chatgpt.com/plugins")
    time.sleep(3)
    st = rb.state()
    link = next((e for e in st.get("elements") or [] if (e.get("label") or "") == "已安裝"), None)
    if link:
        rb.act("click", link["element_token"])
        time.sleep(4)
        st = rb.state()
    t = st.get("tree_markdown") or ""
    path = os.path.join(OUT, "installed_list.tree.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"<!-- installed list captured {report['captured_at_utc']} -->\n")
        fh.write(t)
    report["installed_list"] = {"ref": "installed_list.tree.md", "url": rb.url_of(st),
                                "all_three_visible": all(n in t for n in IDS)}
    print(json.dumps(report["installed_list"], ensure_ascii=False))
    with open(os.path.join(OUT, "C21_HOST_EVIDENCE.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
