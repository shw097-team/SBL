#!/usr/bin/env python3
"""S4 replay identity: the same input lock must reproduce the same artefacts byte for byte.

Two INDEPENDENT subprocesses run the whole chain. Comparing in-process results would prove nothing,
because the first run could be caching; a fresh interpreter per run is what makes the identity claim
real. Also checks that the 19 schema files are byte-stable across the two runs.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".hgk" / "artifacts" / "s4"; OUT.mkdir(parents=True, exist_ok=True)
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
GOAL = "Implement the lifecycle compiler and verify it against the source spec."
SRC = str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")

RUNNER = """
import json, sys
sys.path.insert(0, r"{src}")
from pipd_ls_sp import pipeline as P
card = P.intake({goal!r}, sources=[{src_path!r}])
pi = P.compile_pi(card, "STANDARD")
pd = P.bind_pd(pi, {{"root": {root!r}, "head": "pinned", "tracked_files": 171, "writable_scope": "src/**"}})
cc = P.compile_construction_contract(pd)
ecp = P.compile_ecp(pd, pi)
tq = P.compile_tqaep(pi, ecp, maker="HERMES-MAKER", checker="glm-5.3-flash/opencode-go",
                     checker_execution_receipt="r")
print(json.dumps({{"card": card, "pi": P.strip_sidecar(pi), "pd": pd, "cc": cc, "ecp": ecp, "tqaep": tq}},
                 sort_keys=True, ensure_ascii=False))
"""


def one_run() -> tuple[dict, str]:
    code = RUNNER.format(src=str(ROOT / "src"), goal=GOAL, src_path=SRC, root=str(ROOT))
    r = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, env=ENV,
                       cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit(f"runner failed: {r.stderr[-400:]}")
    payload = json.loads(r.stdout)
    return payload, hashlib.sha256(r.stdout.encode()).hexdigest()


def main() -> int:
    a, sa = one_run()
    b, sb = one_run()
    per_artefact = {}
    for k in a:
        ha = hashlib.sha256(json.dumps(a[k], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        hb = hashlib.sha256(json.dumps(b[k], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        per_artefact[k] = {"identical": ha == hb, "sha256": ha[:32]}
    schemas = sorted((ROOT / "schemas").glob("*.schema.json"))
    schema_sig = hashlib.sha256(b"".join(p.read_bytes() for p in schemas)).hexdigest()
    payload = {
        "runs": 2, "fresh_interpreter_per_run": True,
        "stdout_sha256": {"run1": sa, "run2": sb, "identical": sa == sb},
        "per_artefact": per_artefact,
        "schema_files": len(schemas), "schema_digest": schema_sig[:32],
        "candidate_head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                         capture_output=True, text=True).stdout.strip(),
    }
    payload["verdict"] = "PASS" if (sa == sb and all(v["identical"] for v in per_artefact.values())) else "FAIL"
    (OUT / "REPLAY.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    print(json.dumps({"stdout_identical": sa == sb,
                      "all_artefacts_identical": all(v["identical"] for v in per_artefact.values()),
                      "verdict": payload["verdict"], "schema_files": len(schemas)}, ensure_ascii=False, indent=1))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
