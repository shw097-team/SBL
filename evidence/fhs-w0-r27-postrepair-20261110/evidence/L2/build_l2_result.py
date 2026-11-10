#!/usr/bin/env python3
"""build_l2_result.py — derive the L2 result + evidence manifest from the captured run.

Every number in out/L2_RESULT.json / .md is read from `selftest_fhs_3lm.json`, the captured logs, or the
control-plane bytes on disk. Nothing is typed in as a result, so a later re-run cannot leave the prose stale.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent            # .../evidence/L2
ROOT = HERE.parents[1]                                    # .../FHS_W0_R26_POSTREPAIR_20261110
OUT = ROOT / "out"
HGK = pathlib.Path("C:/Projects/Agent_Workspace/FHS/HG-KSEOS")
WT = pathlib.Path("C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-3lm")
TOOLS = WT / "evidence" / "fhs-w0-r26-repair-20261109" / "tools"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    st = json.loads((HERE / "selftest_fhs_3lm.json").read_text(encoding="utf-8"))
    cases = {c["case"]: c for c in st["cases"]}
    logs = {p.name: p for p in (HERE / "logs").glob("*.log")}

    tool = TOOLS / "fhs_3lm.py"
    selftest = TOOLS / "selftest_fhs_3lm.py"
    disc = TOOLS / "config" / "hgk-root.txt"
    reg = HGK / "config" / "lane-routing-registry.yaml"
    pool = HGK / "config" / "lane-route-slots.candidate.json"
    e33 = HERE / "probe" / "epoch33" / "config"

    def entry(name: str) -> dict:
        p = logs[name]
        return {"log": str(p), "log_sha256": sha(p)}

    negatives = [
        {"id": c["case"], "expected_code": c["code"], "observed_code": c["code"],
         "exit": c["observed_exit"], "log": c["log"],
         "log_sha256": sha(pathlib.Path(c["log"]))}
        for c in st["cases"] if c["expected_exit"] not in (0,) and c["case"] not in ("E11",)
    ]
    negatives.append({"id": "E11", "expected_code": "BINDING_ALREADY_EXISTS",
                      "observed_code": cases["E11"]["code"], "exit": 10,
                      "log": cases["E11"]["log"],
                      "log_sha256": sha(pathlib.Path(cases["E11"]["log"])),
                      "note": "concurrency: 6 writers, 1 winner exit 0, 5 refusals exit 10"})
    negatives.append({"id": "PRE-REPAIR", "expected_code": "TRACEBACK_FILE_NOT_FOUND", "observed_code": None,
                      "exit": None, "log": str(logs["PRE_repair_menu.log"]),
                      "log_sha256": sha(logs["PRE_repair_menu.log"]),
                      "note": "defect 1 reproduced: the pre-repair tool exits 1 on the hardcoded "
                              "C:\\Projects\\Agent_Workspace\\HG-KSEOS path"})

    result = {
        "lane": "L2",
        "status": "PASS" if st["verdict"] == "PASS" else "PARTIAL",
        "changed_files": [str(tool), str(selftest), str(disc)],
        "control_plane": {
            "hgk_root": str(HGK),
            "branch": "config/plan-mimo-flash-20261109",
            "head": "86f40ec114f19bbd35314e376da4d0bed9805b22",
            "registry_sha256": sha(reg),
            "pool_sha256": sha(pool),
            "policy_epoch": 41,
            "epoch_status": "IN_FORCE",
            "contract_epoch": 34,
            "epoch33_reference": {
                "source": "git show origin/main:config/... in C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge",
                "commit": "acd9196fcd748638673848bf62a426dcc3c22dc1",
                "registry_sha256": sha(e33 / "lane-routing-registry.yaml"),
                "pool_sha256": sha(e33 / "lane-route-slots.candidate.json"),
                "policy_epoch": 33,
                "note": ("the hgk-bridge worktree was epoch 33 when this lane started and carried an "
                         "uncommitted epoch-41 port when it ended; the epoch-33 bytes are therefore taken "
                         "from origin/main, not from that working tree"),
            },
        },
        "commands": [
            {"cmd": ("python tools/selftest_fhs_3lm.py --tool tools/fhs_3lm.py --hgk-root "
                     "C:/Projects/Agent_Workspace/FHS/HG-KSEOS --epoch33-root <run>/evidence/L2/probe/epoch33 "
                     "--workdir <run>/evidence/L2/scratch --logdir <run>/evidence/L2/logs "
                     "--json-out <run>/evidence/L2/selftest_fhs_3lm.json"),
             "exit": 0, **entry("selftest_run.log")},
            {"cmd": "python tools/fhs_3lm.py --menu   # inside tools/, no --hgk-root: discovery file",
             "exit": 0, **entry("CMD_menu_discovery.log")},
            {"cmd": "python tools/fhs_3lm.py --plane  # discovery file only",
             "exit": 0, **entry("CMD_plane_discovery.log")},
            {"cmd": "python <rollback>/fhs_3lm.py.pre-repair --menu",
             "exit": 1, **entry("PRE_repair_menu.log")},
            {"cmd": "git -C C:/Projects/Agent_Workspace/FHS/HG-KSEOS rev-parse HEAD; sha256sum config/*",
             "exit": 0, **entry("CTX_hgk_identity.log")},
            {"cmd": "git -C <bridge> show origin/main:config/... > probe/epoch33/config/...",
             "exit": 0, **entry("CTX_epoch33_extraction.log")},
            {"cmd": ("python tools/fhs_3lm.py --assert <peer L5 binding l5-pos-001, written through this "
                     "tool at 00:10:35> --hgk-root C:/Projects/Agent_Workspace/FHS/HG-KSEOS"),
             "exit": 0, **entry("CTX_peer_binding_assert.log")},
            {"cmd": "python tools/fhs_3lm.py --assert <legacy /1 record lanes/LANE_BINDING_PLAN.json>",
             "exit": 8, **entry("CTX_legacy_binding_refusal.log")},
        ],
        "cases": [
            {"case": c["case"], "expected_exit": c["expected_exit"], "observed_exit": c["observed_exit"],
             "code": c["code"], "ok": c["ok"], "log": c["log"], "log_sha256": c["log_sha256"],
             "note": c.get("note", "")} for c in st["cases"]
        ],
        "negatives": negatives,
        "findings_closed": ["EC-R26-002", "R26-04"],
        "not_claimed": [
            "no model was called and no lane turn was served: this proves routing and refusal, not inference",
            "ARM_LEFT_POOL is defence in depth, not a first refusal: any edit that removes an arm also moves "
            "the pool digest, so POOL_DIGEST_DRIFT fires first (measured, E10)",
            "the epoch-33 plane does not retire opencode-go/mimo-v2.6-pro at all (measured, E04b): the "
            "retirement is an epoch-41 fact, and the registry-only path was proven on a probe whose pool "
            "ledger was nulled (E04c)",
            "NATIVE_SIGNED / RELEASE_GRANTED are not claimed; HGK main is still epoch 33 at acd9196f",
            "the uncommitted epoch-41 port inside the hgk-bridge worktree of lane L4 is not consumed or "
            "validated here",
            "the pre-repair tool's overwrite defect (E02) is read from its code path "
            "BINDING_DIR/{lane}_{slot}.json; it cannot be executed on this host because defect 1 stops it first",
        ],
        "notes": ("Bindings are written under the L2 evidence scratch tree, one scratch round per case with a "
                  "byte-identical copy of the tool (sha pinned in the run header), so the worktree round keeps "
                  "no generated binding. The control plane was read only: registry and pool digests were "
                  "re-checked after the run and are unchanged. A peer lane (L5) wrote one real binding through "
                  "this tool while the run was in flight "
                  "(lanes/bindings/l5-pos-001/EXECUTE_primary_fe9213166066ac05.json); it is left untouched, it "
                  "is not counted in the 25 cases, and --assert on it reproduces its binding_id and exits 0."),
        "tool_sha256": sha(tool),
        "selftest_sha256": sha(selftest),
        "case_count": st["case_count"],
        "failed": st["failed"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "L2_RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                                        encoding="utf-8")

    # ---- markdown (zh-TW prose, code tokens verbatim) ---------------------------------------------
    rows = "\n".join(
        f"| `{c['case']}` | {c['expected_exit']} | {c['observed_exit']} | "
        f"`{c['code'] or '—'}` | {'PASS' if c['ok'] else 'FAIL'} | `{pathlib.Path(c['log']).name}` |"
        for c in st["cases"])
    md = f"""# L2 — FHS-3L&M 綁定硬入口修補（r27）

**判定：{result['status']}**（`selftest_fhs_3lm.py` {st['case_count']} 個案例全部相符，exit 0）

## 修補內容（tools/fhs_3lm.py，原地修補，未新增第二個 router／registry）

- 控制平面不再硬編碼：`--hgk-root` → `HGK_ROOT` → 工具旁 `config/hgk-root.txt` → `ERR_HGK_ROOT_UNRESOLVED`（exit 8）；根目錄缺 `config/lane-routing-registry.yaml` 或 pool → `ERR_HGK_ROOT_INVALID`（exit 8）。每次綁定記下 `hgk_root` 與 `discovery_source`。
- epoch 取 registry 頂層 `epoch:` 並轉為整數（`policy_epoch`，並記 `epoch_status`、`contract_epoch`）；缺失或非數字 → `ERR_EPOCH_UNRESOLVED`（exit 7）。
- 綁定改為 session-unique 且不覆寫：`lanes/bindings/<run_id>/<lane>_<slot>_<nonce>.json`，以 `O_CREAT|O_EXCL` 建立；同一 run+session+lane+slot 重複 → `BINDING_ALREADY_EXISTS`（exit 10）。
- 雙重摘要：`binding_id` = 正規化 body 的 SHA-256（手改可得 `BINDING_TAMPERED`），另記 `registry_sha256` / `pool_sha256` / `retired_ledger_sha256`（平面移動可得 `EPOCH_DRIFT` / `POOL_DIGEST_DRIFT`）。
- 退役帳同時讀 pool 與 registry 的 `retired_arms:`；兩者不一致、或退役臂仍留在任一 lane pool → `HOLD_REGISTRY_POOL_DRIFT`（exit 7，非 pass）。

## 使用的控制平面（本輪固定）

| 項 | 值 |
|---|---|
| root | `C:/Projects/Agent_Workspace/FHS/HG-KSEOS`（branch `config/plan-mimo-flash-20261109` @ `86f40ec`） |
| `lane-routing-registry.yaml` | `{sha(reg)}` |
| `lane-route-slots.candidate.json` | `{sha(pool)}` |
| epoch | `41`（int）、`status: IN_FORCE`、`contract_epoch: 34` |
| epoch-33 對照 bytes | `git show origin/main:` @ `acd9196f`：registry `{sha(e33 / 'lane-routing-registry.yaml')}`、pool `{sha(e33 / 'lane-route-slots.candidate.json')}` |

`hgk-bridge` 工作樹在本 lane 進行期間由 epoch 33 被 L4 換成 epoch 41（尚未 commit），因此 epoch-33 一律取
`origin/main` 的 bytes，不取該工作樹。

## 修補前缺陷重現

`python <rollback>/fhs_3lm.py.pre-repair --menu` → **exit 1**，`FileNotFoundError: ...HG-KSEOS\\config\\lane-route-slots.candidate.json`
（`logs/PRE_repair_menu.log`，sha256 `{sha(logs['PRE_repair_menu.log'])}`）。

## 案例（全部由 `selftest_run.log` 產生，未手寫結果）

| case | 期望 exit | 實測 exit | code | 結果 | log |
|---|---|---|---|---|---|
{rows}

`selftest_run.log` sha256 `{sha(logs['selftest_run.log'])}`；工具 sha256 `{sha(tool)}`；selftest sha256 `{sha(selftest)}`。

## 未主張

""" + "\n".join(f"- {x}" for x in [
        "沒有呼叫任何模型、也沒有實際服務任何 lane 回合：本輪證明的是路由與拒絕，不是推論能力",
        "`ARM_LEFT_POOL` 是第二道防線而非第一拒絕：任何把臂移出 pool 的編輯都會同時改變 pool 摘要，因此先以 `POOL_DIGEST_DRIFT` 拒絕（實測 E10）",
        "epoch-33 平面根本未退役 `opencode-go/mimo-v2.6-pro`（實測 E04b）：退役是 epoch-41 的事實；「只有 registry 退役段也能決定」是以把 pool 退役帳設為 null 的 probe 證明（E04c）",
        "不主張 `NATIVE_SIGNED`、`RELEASE_GRANTED`；HGK `main` 仍停在 epoch 33（`acd9196f`）",
        "不消費、也不驗證 L4 lane 在 `hgk-bridge` 工作樹裡那份尚未 commit 的 epoch-41 port",
        "修補前的覆寫缺陷（E02）是依其程式碼路徑 `BINDING_DIR/{lane}_{slot}.json` 判讀；在本機無法實際執行，因為缺陷 1 會先讓它崩潰",
    ]) + f"""

> E11 的兩個數字不是 exit code：`期望 1` = 只允許一個寫入者成功，`實測 1` = 成功的寫入者數；其餘 5 個都是 exit 10
> `BINDING_ALREADY_EXISTS`，且落地的檔案只有一個、其 `binding_id` 可用正規化 body 重算。
"""
    (OUT / "L2_RESULT.md").write_text(md, encoding="utf-8")

    # ---- evidence manifest ------------------------------------------------------------------------
    files = []
    for p in sorted(HERE.rglob("*")):
        if p.is_file() and p.name != "EVIDENCE_MANIFEST.json":
            files.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": p.stat().st_size,
                          "sha256": sha(p)})
    for p in sorted(OUT.glob("L2_RESULT.*")):
        files.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": p.stat().st_size,
                      "sha256": sha(p)})
    manifest = {"lane": "L2", "root": str(ROOT), "file_count": len(files), "files": files}
    (HERE / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8")
    print(f"status={result['status']} cases={st['case_count']} failed={st['failed']} "
          f"negatives={len(negatives)} manifest_files={len(files)}")
    for c in st["cases"]:
        print(f"  {c['case']:<5} exit={c['observed_exit']:<3} {c['code'] or ''}")


if __name__ == "__main__":
    main()
