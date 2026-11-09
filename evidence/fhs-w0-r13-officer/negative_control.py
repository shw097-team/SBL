"""Negative control for G19, run by the officer against a tampered in-memory artifact.

No file is written: the register is loaded, one member digest is replaced in memory, and the check is
called directly. It must refuse with MEMBER_DIGEST_DRIFT. If it returns OK, the check does not bite.
"""
import copy, importlib.util, json, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("gate_r13", os.path.join(root, "tools", "gate_r13.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

real = json.load(open(os.path.join(root, "lanes", "D", "COPY_REGISTER_ALL.json"), encoding="utf-8"))

class Ctx:
    round_dir = root
    sources_dir = r"C:/Projects/Agent_Workspace/FHS_W1_Work_Final/FHS_W1_Work_Final/sources"
    profile = "round"
    scope = "full"
    def __init__(self, doc): self._doc = doc
    def load(self, rel): return self._doc

ok_real, code_real, detail_real = g.g19_copy_register(Ctx(copy.deepcopy(real)))
tampered = copy.deepcopy(real)
tampered["names_exact"][0]["members"][0]["sha256"] = "0" * 64
ok_t, code_t, detail_t = g.g19_copy_register(Ctx(tampered))

print(json.dumps({
    "baseline": {"ok": ok_real, "code": code_real, "detail": detail_real[:120]},
    "tampered": {"ok": ok_t, "code": code_t, "detail": detail_t[:160]},
    "check_bites": (ok_real is True and ok_t is False and code_t == "MEMBER_DIGEST_DRIFT"),
}, ensure_ascii=False, indent=1))
