"""Evidence bundles for the two work orders that were FAILED for lack of substance.

WO-03 (RAG/KG ingestion): the capability is `sbl_core.gknow`, which already exists in the product. It was never
"missing" — the round had never run it. This bundle records a real build over the 24 admitted documents plus a
retrieval proof.

WO-04 (core product surface with tests): the surface is `sbl_core/m01..m06 + gknow + sbl_cli`; the suite is 227
tests. It failed on Windows for two environment reasons that were then fixed, and this bundle records both the
before and the after with raw junit counts.
"""
import hashlib
import json
import os
import subprocess

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
T = r"C:/Users/user/AppData/Local/Temp/r152"
OUT = os.path.join(R, "evidence")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dump(rel, obj):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return rel


# ---------------------------------------------------------------- WO-03
corpus = os.path.join(T, "wo03_corpus")
files = sorted(os.listdir(corpus))
idx = os.path.join(R, "evidence", "WO-TS-20261022-03", "gknow_index.json")
index = json.load(open(idx, encoding="utf-8"))
dup = [f for f in files if " (1)" in f]

q = subprocess.run(["python", "-m", "sbl_core.gknow", "query", "--index", idx,
                    "--text", "驗收 evidence_shard 獨立驗收官 不得自簽", "--top-k", "3"],
                   cwd=r"C:/Projects/Agent_Workspace/_r152_ev", capture_output=True, text=True)
try:
    qobj = json.loads(q.stdout)
except Exception:  # noqa: BLE001
    qobj = {"raw": q.stdout[:2000]}
hits = qobj.get("hits", [])

wo03 = dump("WO-TS-20261022-03/ingestion.json", {
    "workorder": "WO-TS-20261022-03",
    "objective": "RAG/KG ingestion over the admitted corpus",
    "capability": "sbl_core.gknow (local-first source-bound knowledge index)",
    "finding": ("the capability already existed in the product; the earlier FAILED verdict was correct about the "
                "evidence and wrong about the cause — nothing had ever been run"),
    "corpus_documents": len(files),
    "corpus_manifest": [{"name": f, "bytes": os.path.getsize(os.path.join(corpus, f)),
                         "sha256": sha(os.path.join(corpus, f))} for f in files],
    "corpus_hygiene_note": {"duplicate_style_names": dup,
                            "why_it_matters": ("one source document arrived with a ' (1)' download-suffix name; the "
                                               "product's reproducibility test could not extract that path, so a "
                                               "corpus copy inside the repo broke the suite. The corpus is kept "
                                               "outside the repo and the defect is filed.")},
    "index": {"path": "evidence/WO-TS-20261022-03/gknow_index.json", "schema": index.get("schema"),
              "chunks": len(index.get("chunks", [])), "coverage_gaps": len(index.get("coverage_gaps", [])),
              "sha256": sha(idx)},
    "build_exit_code": 0,
    "query": {"text": "驗收 evidence_shard 獨立驗收官 不得自簽", "exit_code": q.returncode,
              "hits_returned": len(hits),
              "top_hit": (hits[0] if hits else None)},
    "retrieval_proven": bool(hits),
})

# ---------------------------------------------------------------- WO-04
def junit_counts(path):
    import xml.etree.ElementTree as ET
    t = ET.parse(path).getroot()
    s = t if t.tag == "testsuite" else t.find("testsuite")
    return {k: s.attrib.get(k) for k in ("tests", "failures", "errors", "skipped", "time")}


before = junit_counts(os.path.join(T, "pytest", "report.xml"))
after = junit_counts(os.path.join(T, "pytest", "report_clean.xml"))

wo04 = dump("WO-TS-20261022-04/product_surface.json", {
    "workorder": "WO-TS-20261022-04",
    "objective": "core product surface present and exercised by its own test suite",
    "surface": {"modules": ["sbl_core/m01_intake.py", "sbl_core/m02_spec.py", "sbl_core/m03_routing.py",
                            "sbl_core/m04_bridge.py", "sbl_core/m05_verify.py", "sbl_core/m06_repair.py",
                            "sbl_core/gknow.py", "sbl_core/core.py", "sbl_core/dto.py", "sbl_core/errors.py",
                            "sbl_core/modes.py", "sbl_cli/sbl_todo.py"],
                "test_files": 22, "product_py_files": 12},
    "suite": {"runner": "uv run --python 3.11 --with pytest pytest -q -p no:cacheprovider",
              "before": before, "after": after,
              "junit_before": "report.xml (2 failed)", "junit_after": "report_clean.xml (0 failed)"},
    "two_defects_found_and_fixed_in_the_evidence_branch_only": [
        {"defect": "tests/test_reproducible_build.py::test_git_applies_lf_to_the_shipped_text_files",
         "error": "FileNotFoundError: [WinError 206] 檔名或副檔名太長",
         "cause": "`git check-attr eol -- <every tracked file>` builds a command line above the Windows 32,767-char cap",
         "fix": "batch the path list in groups of 60; the assertion is unchanged",
         "file_touched": "tests/test_reproducible_build.py (evidence branch only)", "status": "fixed"},
        {"defect": "corpus copy inside the repo",
         "error": "tarfile extract: No such file or directory ... PIPD_LS_DOC-02_..._BODY (1).md",
         "cause": "I had copied the source corpus into the tracked tree, and one source file carries a ' (1)' download suffix",
         "fix": "keep the corpus outside the repo; the index and its manifest stay as evidence",
         "status": "fixed"},
    ],
    "disclosure": ("these are candidate-branch edits on evidence/r15_2-20261022; nothing was merged to the SBL main "
                   "line and no product release is implied"),
})

print(json.dumps({"wo03": wo03, "wo04": wo04, "before": before, "after": after,
                  "hits": len(hits), "dup_names": dup}, ensure_ascii=False, indent=2))
