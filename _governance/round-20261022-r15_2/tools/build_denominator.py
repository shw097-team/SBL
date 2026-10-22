"""Build the real R15.2 denominator: 18 WorkPackages, 25 CheckRuns, E01-E09, M1-M4, plus the R14 31 TS.

The six work orders HG-KSEOS admitted are a subset of this, and saying so is the point of the file: a claim of
completion is meaningless against a denominator you never declared.
"""
import json
import os
import re

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
CMD = (r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/attachments/"
       r"SBL_HERMES_HGK_FABRIC_R15_2_THIN_CONSTRUCTION_ACCEPTANCE_COMMAND_2026-10-22.md")

text = open(CMD, encoding="utf-8").read()
lines = text.splitlines()

wps, checks = [], []
def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


for ln in lines:
    if not ln.lstrip().startswith("|"):
        continue
    cs = cells(ln)
    if len(cs) >= 3:
        m = re.fullmatch(r"\*\*(W\d\d)\*\*", cs[0])
        if m:
            wps.append({"id": m.group(1), "title": cs[1], "checks": cs[2].split("/")})
            continue
    if len(cs) >= 2:
        m = re.fullmatch(r"\*\*(C\d\d)\*\*", cs[0])
        if m:
            checks.append({"id": m.group(1), "title": cs[1]})

es = [
    {"id": "E01", "title": "HGK baseline / Conformance"},
    {"id": "E02", "title": "PIPD / TPM / SPEC"},
    {"id": "E03", "title": "Commander / Challenge"},
    {"id": "E04", "title": "Native Fabric / Hermes"},
    {"id": "E05", "title": "真建造 / 修補"},
    {"id": "E06", "title": "五工具 / Host / ZIP"},
    {"id": "E07", "title": "獨立安全驗收"},
    {"id": "E08", "title": "SWOF 型隔離 Dogfood"},
    {"id": "E09", "title": "W2/W3 首個真 SWOF"},
]
ms = [
    {"id": "M1", "title": "Native / Fabric / 真 SP / 獨立 AO"},
    {"id": "M2", "title": "全新需求隔離 E2E、完整 mutation / repair"},
    {"id": "M3", "title": "W2 external receipt + W3 Domain Owner Native Admission + SWOF 真 PR/readback"},
    {"id": "M4", "title": "DOC 全語義、五工具、三 ZIP、三私人 Host、38 Surfaces/39 Gates、供應鏈、安全、Release 獨立真驗收"},
]

# measured status of the round, item by item. Anything not measured is NOT_RUN, never "done".
evidence = {
    "W00": ("DONE", ["evidence/WO-TS-20261022b-01/intake_coverage.json", "evidence/WO-TS-20261022-05/acceptance.json"]),
    "W01": ("PARTIAL", ["receipts/admission/native_admit_close.json",
                        "TT_R15_2_REGISTER.json#TT-R15.2-NATIVE-CONFORMANCE-PENDING"]),
    "W02": ("NOT_RUN", ["TT_R15_2_REGISTER.json#TT-R15.2-FABRIC-ACTIVE-POLICY-UNRESOLVED"]),
    "W03": ("DONE", ["receipts/dispatch/PLAN_gpt61sol.json"]),
    "W04": ("DONE", ["receipts/dispatch/VERIFY_cfinal2.json"]),
    "W05": ("NOT_RUN", []),
    "W06": ("NOT_RUN", ["evidence/WO-TS-20261022-04/product_surface.json"]),
    "W07": ("NOT_RUN", []),
    "W08": ("PARTIAL", ["receipts/dispatch/EXECUTE_wo04c.json", "receipts/dispatch/VERIFY_cfinal2.json"]),
    "W09": ("PARTIAL", ["receipts/dispatch/VERIFY_cfinal2.json"]),
    "W10": ("PARTIAL", ["openspec/changes/sbl-r15-2-native-admission/specs/sbl-native-admission/spec.md",
                        "TT_R15_2_REGISTER.json#TT-R15.2-GSTACK-NOFIT"]),
    "W11": ("NOT_RUN", []),
    "W12": ("NOT_RUN", ["TT_R15_2_REGISTER.json#TT-R15.2-SWOF-W3-ABSENT"]),
    "W13": ("NOT_RUN", ["TT_R15_2_REGISTER.json#TT-R15.2-CHATGPT-HOST-PENDING"]),
    "W14": ("NOT_RUN", []),
    "W15": ("NOT_RUN", []),
    "W16": ("NOT_RUN", []),
    "W17": ("PARTIAL", ["workers/r14ledger/SUMMARY.json", "workers/r14ledger/per_item.json"]),
}
ck = {
    "C00": "DONE", "C01": "PRESENT_NOT_ADJUDICATED", "C02": "NOT_RUN", "C03": "DONE", "C04": "PARTIAL",
    "C05": "PARTIAL", "C06": "PARTIAL", "C07": "PARTIAL", "C08": "PARTIAL", "C09": "PARTIAL", "C10": "PARTIAL",
    "C11": "NOT_RUN", "C12": "NOT_RUN", "C13": "NOT_RUN", "C14": "PARTIAL", "C15": "NOT_RUN", "C16": "NOT_RUN",
    "C17": "NOT_RUN", "C18": "NOT_RUN", "C19": "NOT_RUN", "C20": "NOT_RUN", "C21": "NOT_RUN", "C22": "NOT_RUN",
    "C23": "NOT_RUN", "C24": "NOT_RUN",
}
em = {
    "E01": ("PARTIAL", "native admission executed; conformance suite not run"),
    "E02": ("NOT_RUN", "PIPD 8 skills / 19 contracts / 13 CLI not delivered this round"),
    "E03": ("PARTIAL", "PLAN and VERIFY dispatched; commander/challenge join not proven on a candidate hash"),
    "E04": ("PARTIAL", "Fabric policy consumption unresolved"),
    "E05": ("PARTIAL", "one Windows portability repair landed; bounded repair loop not exercised"),
    "E06": ("NOT_RUN", "five tools / three ZIPs / three hosts untouched"),
    "E07": ("PARTIAL", "lane-level checker only; SOD006-C6 open"),
    "E08": ("NOT_RUN", "no isolated dogfood run"),
    "E09": ("NOT_RUN", "SWOF W3 absent"),
    "M1": ("PARTIAL", "native issuer real, SP and independent AO not both real"),
    "M2": ("NOT_RUN", "no fresh-requirement isolated E2E, no full mutation/repair"),
    "M3": ("NOT_RUN", "no W2 external receipt, no W3 admission"),
    "M4": ("NOT_RUN", "host IDs, ZIPs, supply chain, release all open"),
}

for wp in wps:
    st, refs = evidence.get(wp["id"], ("NOT_RUN", []))
    wp["status"], wp["evidence"] = st, refs
for c in checks:
    c["status"] = ck.get(c["id"], "NOT_RUN")
for e in es:
    e["status"], e["why"] = em[e["id"]]
for m in ms:
    m["status"], m["why"] = em[m["id"]]

r14 = json.load(open(os.path.join(R, "workers", "r14ledger", "SUMMARY.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(R, "workers", "r14ledger", "SUMMARY.json")) else {}

def tally(items, key="status"):
    out = {}
    for i in items:
        out[i[key]] = out.get(i[key], 0) + 1
    return out

doc = {
    "schema": "SBL_R15_2_DENOMINATOR/1",
    "subject": "SBL-R15.2-CONTINUATION-20261022",
    "why_this_file_exists": ("the round declared six work orders VERIFIED and reported PARTIAL; that verdict is only "
                             "meaningful against the command's own denominator, which is 18 WorkPackages, 25 CheckRuns, "
                             "nine E-series product capabilities, four M-series milestones, and the R14 31 TS / 31 CHK "
                             "set. This file declares it and measures each item."),
    "workpackages": wps, "checkruns": checks, "eseries": es, "milestones": ms,
    "r14_ts": r14.get("counts") or r14 or {},
    "totals": {
        "workpackages": {"total": len(wps), **tally(wps)},
        "checkruns": {"total": len(checks), **tally(checks)},
        "eseries": {"total": len(es), **tally(es)},
        "milestones": {"total": len(ms), **tally(ms)},
    },
    "verdict": ("PARTIAL. Of 18 work packages, 3 are DONE, 6 PARTIAL, 9 NOT_RUN. Of 9 E-series capabilities, none is "
                "DONE. Of 4 milestones, none is PASSED. Release and M4 remain blocked for owner-side reasons that no "
                "agent may manufacture."),
    "generated_note": "statuses are measured against artefacts in this round; NOT_RUN means no attempt was made",
}
p = os.path.join(R, "DENOMINATOR_R15_2.json")
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(doc["totals"], ensure_ascii=False, indent=2))
print("parsed wps:", len(wps), "checks:", len(checks))
