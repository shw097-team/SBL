#!/usr/bin/env python3
"""REC08 F3-d driver — three NEW intents through a full product lifecycle.

Every check is behavioural: the outcome is read from the installed artefact's own output, not
from the generator's intent. A NEG that does not fail is reported as a FAILURE of the suite.

Run:
  python run_three_kinds.py [--root <dir>]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import kind_factory as KF          # noqa: E402
import lifecycle as LC             # noqa: E402

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
RESULTS: list[tuple[str, str, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, "PASS" if ok else "FAIL", detail))


def build_intents() -> list[KF.Intent]:
    """Three NEW intents — not the sbl-todo fixture, not a template copy."""
    return [
        KF.Intent(
            intent_id="sbl_line_measure", kind="CLI_TOOL",
            title="Measure a text file without opening it in an editor",
            fuo="`sbl-line-measure --json FILE` prints lines/words/chars as JSON and exits 2 with "
                "a typed code when the file is absent",
            non_goals=("no network", "no shell execution"),
            source_clause="SBL_PIPD-LS-PKG_DOC-02:L214",
        ),
        KF.Intent(
            intent_id="sbl_release_checklist", kind="AGENT_SKILL",
            title="Turn a changelog into a release checklist",
            fuo="asking to 'prepare a release checklist from CHANGELOG.md' produces grouped "
                "checklist lines, one per input entry, with unknowns marked UNKNOWN",
            non_goals=("no publishing", "no tag creation"),
            source_clause="SBL_PIPD-LS-PKG_DOC-12:L481",
            triggers=("prepare a release checklist", "release checklist from changelog"),
        ),
        KF.Intent(
            intent_id="sbl_readonly_audit", kind="SIMPLE_AGENT",
            title="Audit a directory read-only and stop on any write attempt",
            fuo="a plan of read/list steps yields a receipt with per-step verdicts; a write step "
                "is DENIED and stops the run",
            non_goals=("no writes", "no network", "no self-directed loop"),
            source_clause="SBL_PIPD-LS-PKG_DOC-05:L902",
            allowed_tools=("read_file", "list_dir"),
            denied_tools=("write_file", "delete_file", "http_get"),
        ),
    ]


def run_cli(intent: KF.Intent, root: Path) -> None:
    built = KF.build_cli_tool(intent, root / "build")
    check("CLI built (pyproject+entrypoint)", Path(built["root"], "pyproject.toml").is_file(), built["root"])

    prefix = root / "host" / "cli_prefix"
    inst = LC.cli_install(Path(built["root"]), built["entrypoint"], prefix)
    check("CLI install", inst["ok"] is True, inst.get("code") or inst.get("installed_dist_info"))
    entry = Path(inst["entrypoint"])

    sample = root / "host" / "sample.txt"
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text("alpha beta\ngamma\n", encoding="utf-8")

    helptext = LC.cli_invoke(entry, ["--help"])
    check("CLI --help", helptext["exit"] == 0 and "--json" in helptext["stdout"],
          f"exit={helptext['exit']}")

    pos = LC.cli_invoke(entry, ["--json", str(sample)])
    payload = json.loads(pos["stdout"]) if pos["stdout"].strip().startswith("{") else {}
    check("CLI invoke POS json FUO",
          pos["exit"] == 0 and payload == {"lines": 2, "words": 3, "chars": 17, "ok": True},
          pos["stdout"].strip())

    neg = LC.cli_invoke(entry, ["--json", str(root / "absent.txt")])
    negp = json.loads(neg["stderr"]) if neg["stderr"].strip().startswith("{") else {}
    check("CLI NEG missing input typed nonzero",
          neg["exit"] == 2 and negp.get("code") == "INPUT_NOT_FOUND",
          f"exit={neg['exit']} code={negp.get('code')}")

    un = LC.cli_uninstall(prefix, built["entrypoint"])
    check("CLI uninstall no residue", un["ok"] is True, un.get("code") or f"residue={un['residue']}")

    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "receipts" / "CLI_TOOL.json").write_text(json.dumps(
        {"intent": intent.intent_id, "build": built, "install": inst, "help": helptext,
         "pos": pos, "neg": neg, "uninstall": un}, ensure_ascii=False, indent=2), encoding="utf-8")


def run_skill(intent: KF.Intent, root: Path) -> None:
    built = KF.build_agent_skill(intent, root / "build")
    host = root / "host" / "skills"
    inst = LC.skill_install(Path(built["root"]), host)
    check("SKILL install discovered", inst["ok"] is True,
          inst.get("code") or str(inst["discovery"]["name"] if inst.get("discovery") else None))

    disc = LC.skill_discover(host)
    mine = dict(next((s for s in disc["skills"] if s.get("name") == built["name"]), {}))

    trig_hit = LC.skill_match(mine, "please prepare a release checklist from CHANGELOG.md")
    check("SKILL trigger POS", trig_hit is True, str(mine.get("triggers")))
    trig_miss = LC.skill_match(mine, "what is the weather in Taipei")
    check("SKILL nontrigger NEG", trig_miss is False, "ordinary query must not trigger")

    # The procedure's real output contract is checked, not just the manifest's claims.
    body = (Path(built["root"]) / "SKILL.md").read_text(encoding="utf-8")
    contract = (Path(built["root"]) / "references" / "output_contract.md").read_text(encoding="utf-8")
    has_steps = all(s in body for s in ("## Procedure", "Never invent an entry", "UNKNOWN"))
    has_contract = '"unknown"' in contract and '"groups"' in contract
    check("SKILL procedure + machine contract present", has_steps and has_contract,
          f"steps={has_steps} contract={has_contract}")

    un = LC.skill_uninstall(host, built["name"])
    check("SKILL uninstall no residue", un["ok"] is True, un.get("code") or f"residue={un['residue']}")

    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "receipts" / "AGENT_SKILL.json").write_text(json.dumps(
        {"intent": intent.intent_id, "build": built, "install": inst, "discovery": disc,
         "trigger_pos": trig_hit, "nontrigger_neg": trig_miss,
         "files": inst.get("files"), "uninstall": un}, ensure_ascii=False, indent=2), encoding="utf-8")


def run_agent(intent: KF.Intent, root: Path) -> None:
    built = KF.build_simple_agent(intent, root / "build")
    host = root / "host" / "agents"
    inst = LC.agent_install(Path(built["root"]), host)
    check("AGENT install with allowlist+stop policy", inst["ok"] is True,
          inst.get("code") or str(inst["allowlist"]))
    dst = Path(inst["dst"])

    work = root / "work"
    target = root / "host" / "audit_target"
    target.mkdir(parents=True, exist_ok=True)
    (target / "a.txt").write_text("alpha", encoding="utf-8")

    pos = LC.agent_run(dst, [{"tool": "list_dir", "arg": str(target)},
                             {"tool": "read_file", "arg": str(target / "a.txt")}], work, "pos")
    check("AGENT POS bounded run",
          pos["exit"] == 0 and pos["receipt"].get("ok") is True
          and [s["verdict"] for s in pos["receipt"].get("steps", [])] == ["OK", "OK"],
          pos["stdout"][:200])

    neg = LC.agent_run(dst, [{"tool": "list_dir", "arg": str(target)},
                             {"tool": "write_file", "arg": str(target / "x.txt")}], work, "neg")
    steps = neg["receipt"].get("steps", [])
    denied = steps[-1] if steps else {}
    check("AGENT NEG write denied and stopped",
          neg["exit"] == 3 and denied.get("verdict") == "DENIED"
          and neg["receipt"].get("stop_code") == "STOP_DENIED_TOOL"
          and not (target / "x.txt").exists(),
          json.dumps({"exit": neg["exit"], "stop": neg["receipt"].get("stop_code"),
                      "denied": denied.get("code"), "file_created": (target / "x.txt").exists()}))

    budget = LC.agent_run(dst, [{"tool": "list_dir", "arg": str(target)}] * 7, work, "budget")
    check("AGENT stop policy caps steps",
          budget["receipt"].get("stop_code") == "STOP_STEP_BUDGET",
          str(budget["receipt"].get("stop_code")))

    un = LC.agent_uninstall(host, dst.name)
    check("AGENT uninstall no residue", un["ok"] is True, un.get("code") or f"residue={un['residue']}")

    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "receipts" / "SIMPLE_AGENT.json").write_text(json.dumps(
        {"intent": intent.intent_id, "build": built, "install": inst,
         "pos": pos, "neg": neg, "budget": budget, "uninstall": un},
        ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(VAR / "products" / "three_kinds"))
    args = ap.parse_args()
    root = Path(args.root)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    intents = build_intents()
    for it in intents:
        it.validate()
    check("three intents are distinct and in V0.1 scope",
          len({i.intent_id for i in intents}) == 3
          and {i.kind for i in intents} == {"CLI_TOOL", "AGENT_SKILL", "SIMPLE_AGENT"},
          ",".join(f"{i.kind}:{i.intent_id}" for i in intents))

    t0 = time.time()
    run_cli(intents[0], root / "cli")
    run_skill(intents[1], root / "skill")
    run_agent(intents[2], root / "agent")

    bad = [r for r in RESULTS if r[1] == "FAIL"]
    for label, verdict, detail in RESULTS:
        print(f"{verdict:4} {label}" + (f"  | {detail}" if detail else ""))
    print(f"\n{len(RESULTS) - len(bad)}/{len(RESULTS)} passed in {round(time.time() - t0, 1)}s")

    rec = {
        "schema": "THREE_KINDS_LIFECYCLE.v1", "order": "REC08_F3D",
        "root": str(root),
        "intents": [{"id": i.intent_id, "kind": i.kind, "fuo": i.fuo,
                     "source_clause": i.source_clause} for i in intents],
        "total": len(RESULTS), "passed": len(RESULTS) - len(bad),
        "results": [{"label": l, "verdict": v, "detail": d} for l, v, d in RESULTS],
        "claim_ceiling": "CANDIDATE_TESTED",
        "not_claimed": ["NATIVE_EFFECT_VERIFIED", "HOST_UAT", "INDEPENDENT_PASS", "RELEASED"],
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    out = VAR / "receipts" / "F3D_THREE_KINDS.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"receipt={out}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
