"""WO-S4-DOC-FIRSTUSE-01 (S4-R2): the documented first-run walk-through actually runs.

The README's compiler section shows a copy-paste chain and claims a reader can run it. This test
is the machine-checkable half of that claim: it drives the EXACT documented commands against the
checked-in ``examples/first-run/`` fixture, using the CLI surface (``python -m pipd_ls_sp.cli``),
and pins three things the front page now asserts:

  * the positive chain (``init`` -> ``intake`` -> ``compile-pi`` -> ``bind-pd`` -> ``compile-ecp``
    -> ``compile-tqaep`` -> ``validate``) exits 0 and validates with no findings;
  * a SECOND run in a fresh workspace reproduces byte-identical artefact digests;
  * a source locator that does not exist is refused with a typed, non-zero ``AUTHORITY_UNKNOWN``
    and writes no artefact.

It never touches ``src/**``, ``schemas/**`` or the network. The interpreter is pinned to the
absolute path that carries ``jsonschema`` (falling back to the running interpreter if absent).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FIXTURE = ROOT / "examples" / "first-run"
ASSEMBLE = FIXTURE / "assemble_bundle.py"
SOURCE = "examples/first-run/source.txt"          # relative to the repo root, exactly as documented
GOAL = "Compile this example clause source into a validated PI to PD to ECP to TQAEP chain."
CONSTRAINT = "candidate-only, no release"
NON_GOAL = "no upstream document bodies copied"

PINNED = Path("C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe")
INTERP = str(PINNED) if PINNED.is_file() else sys.executable

ENV = {**os.environ, "PYTHONPATH": str(SRC),
       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}

ARTEFACTS = ("intent.card.json", "pi.json", "pd.json", "ecp.json", "tqaep.json")


def _cli(root: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run([INTERP, "-B", "-m", "pipd_ls_sp.cli", "--root", str(root), *args],
                          cwd=str(ROOT), env=ENV, capture_output=True, text=True, encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_chain(root: Path, ctx: Path, art: Path) -> tuple[dict[str, str], dict]:
    """Drive the documented chain into ``root``; return ({artefact: sha256}, validate payload).

    ``ctx`` is the read-only RepoContext directory ``bind-pd`` binds against; it is the SAME dir
    across runs, because PD legitimately binds ``RepoContext.root`` and PD/ECP derive from it.
    """
    art.mkdir(parents=True, exist_ok=True)
    ctx.mkdir(parents=True, exist_ok=True)

    steps: list[tuple[str, list[str]]] = [
        ("intent.card.json", ["intake", "--goal", GOAL, "--source", SOURCE,
                              "--constraint", CONSTRAINT, "--non-goal", NON_GOAL]),
        ("pi.json", ["compile-pi", "--intent", str(art / "intent.card.json"), "--profile", "LITE"]),
        ("pd.json", ["bind-pd", "--pi", str(art / "pi.json"), "--repo-root", str(ctx)]),
        ("ecp.json", ["compile-ecp", "--pd", str(art / "pd.json"), "--pi", str(art / "pi.json")]),
        ("tqaep.json", ["compile-tqaep", "--pi", str(art / "pi.json"),
                        "--ecp", str(art / "ecp.json"), "--maker", "HERMES-MAKER",
                        "--checker", "GLM-5.3-FLASH-AO-LANE",
                        "--checker-receipt", "deleg_example/lane-C"]),
    ]
    init = _cli(root, "init")
    assert init.returncode == 0, f"init failed: {init.stdout[:300]}"
    for name, args in steps:
        proc = _cli(root, *args)
        assert proc.returncode == 0, f"{args[0]} failed ({proc.returncode}): {proc.stdout[:300]}"
        (art / name).write_text(proc.stdout, encoding="utf-8")

    bundle = subprocess.run(
        [INTERP, "-B", str(ASSEMBLE), str(art / "pi.json"), str(art / "pd.json"),
         str(art / "ecp.json"), str(art / "tqaep.json")],
        cwd=str(ROOT), env=ENV, capture_output=True, text=True, encoding="utf-8")
    assert bundle.returncode == 0, f"assemble_bundle.py failed: {bundle.stderr[:300]}"
    (art / "bundle.json").write_text(bundle.stdout, encoding="utf-8")

    val = _cli(root, "validate", "--bundle", str(art / "bundle.json"))
    assert val.returncode == 0, f"validate failed ({val.returncode}): {val.stdout[:400]}"
    return {n: _sha256(art / n) for n in ARTEFACTS}, json.loads(val.stdout)


class FirstRunExamples(unittest.TestCase):
    def test_positive_chain_runs_and_validates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pipd_firstrun_a_") as tmp:
            base = Path(tmp)
            digests, validation = _run_chain(base / "ws", base / "ctx", base / "art")
        self.assertEqual(validation["verdict"], "PASS", str(validation.get("findings"))[:800])
        self.assertEqual(validation["checked"], 4)
        self.assertEqual(validation["findings"], [])
        for name, digest in digests.items():
            self.assertRegex(digest, r"^[0-9a-f]{64}$", name)

    def test_second_run_reproduces_the_same_digests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pipd_firstrun_b_") as tmp:
            base = Path(tmp)
            # One shared RepoContext dir; two FRESH workspaces.
            ctx = base / "ctx"
            run1, val1 = _run_chain(base / "ws1", ctx, base / "art1")
            run2, val2 = _run_chain(base / "ws2", ctx, base / "art2")
        self.assertEqual(run1, run2, "a second run did not reproduce the artefact digests")
        self.assertEqual(val1["verdict"], "PASS")
        self.assertEqual(val2["verdict"], "PASS")
        self.assertEqual(val1["findings"], val2["findings"])
        self.assertEqual(val1["checked"], val2["checked"])

    def test_negative_missing_source_is_typed_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pipd_firstrun_neg_") as tmp:
            base = Path(tmp)
            root, art = base / "ws", base / "art"
            art.mkdir(parents=True, exist_ok=True)
            self.assertEqual(_cli(root, "init").returncode, 0)
            proc = _cli(root, "intake", "--goal", GOAL,
                        "--source", "examples/first-run/missing.txt",
                        "--constraint", CONSTRAINT)
            self.assertEqual(proc.returncode, 2,
                             f"expected a non-zero refusal, got {proc.returncode}")
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["verdict"], "FAIL")
            self.assertEqual(payload["code"], "AUTHORITY_UNKNOWN")
            self.assertIn("missing.txt", payload["message"])
            self.assertEqual(list(art.iterdir()), [], "a refusal wrote an artefact")


if __name__ == "__main__":
    unittest.main(verbosity=2)
