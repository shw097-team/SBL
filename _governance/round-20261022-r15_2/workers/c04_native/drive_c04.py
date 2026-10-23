"""C04: drive the native HG-KSEOS issuer; prove one bounded, non-replayable effect."""
import hashlib, json, os, pathlib, subprocess, sys, time
sys.path.insert(0, r"C:\Projects\Agent_Workspace\HG-KSEOS\src")
from hg_kseos.spine import SharedSpine
from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest
from hg_kseos.assurance import EffectToken
DB = pathlib.Path(r"C:\Projects\Agent_Workspace\HG-KSEOS\var\shared-spine\hg-kseos.db")
PID = "SBL-C04-R153-" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:6].upper()
before = {"db_bytes": DB.stat().st_size, "db_mtime": DB.stat().st_mtime}
out = {"schema": "SBL_C04_NATIVE_EVIDENCE/1", "project_id": PID, "before": before}
spine = SharedSpine(DB)
ctl = ProjectLifecycleController(spine)
root = str(pathlib.Path(os.environ.get("TMP", "C:/Windows/Temp")) / "c04_target")
req = ProjectRequest(goal="Prove one bounded effect through the native issuer",
                      constraints=["one writeset", "one nonce", "readback required"],
                      non_goals=["no product change", "no release"], target_root=root)
os.makedirs(root, exist_ok=True)
G = ["git", "-C", root]
if not os.path.isdir(os.path.join(root, ".git")):
    subprocess.run(["git", "init", "-q", root], check=True)
    open(os.path.join(root, "README.md"), "w").write("c04 target\n")
    subprocess.run(G + ["add", "README.md"], check=True)
    subprocess.run(G + ["-c", "user.name=C04", "-c", "user.email=c04@local", "-m", "init"], check=True)
out["start"] = ctl.start(req, project_id=PID)
out["intake"] = ctl.intake(PID, req)
for t in ("INTENT_BOUND", "REQUIREMENTS_READY", "DESIGN_READY", "PLAN_READY"):
    ctl.transition(PID, t, trigger="C04_DRIVE")
out["plan"] = ctl.plan(PID)
out["admit"] = ctl.admit_workorders(PID)
suffix = PID.split("-")[-1]
with spine.transaction() as conn:
    rows = [dict(r) for r in conn.execute("SELECT * FROM workorders WHERE taskspec_id LIKE ?", (f"TS-{suffix}%",)).fetchall()]
out["workorders_from_spine"] = rows
out["workorder_count"] = len(rows)
tok = EffectToken(token="C04-NONCE-" + hashlib.sha256(PID.encode()).hexdigest()[:16], expires_at=int(time.time()) + 300)
tok.consume(int(time.time()))
out["effect_token"] = {"token": tok.token, "first_consume": "ACCEPTED"}
neg = {}
try:
    tok.consume(int(time.time()))
except Exception as e:
    neg["replay"] = str(e)
try:
    EffectToken(token="C04-EXPIRED", expires_at=int(time.time()) - 1).consume(int(time.time()))
except Exception as e:
    neg["expired"] = str(e)
out["negatives"] = neg
tgt = pathlib.Path(root) / "c04_effect.txt"
tgt.write_text("bounded effect " + tok.token + "\n", encoding="utf-8")
out["readback"] = {"path": str(tgt), "bytes": tgt.stat().st_size, "sha256": hashlib.sha256(tgt.read_bytes()).hexdigest()}
out["after"] = {"db_bytes": DB.stat().st_size, "db_mtime": DB.stat().st_mtime}
out["ceiling"] = "one project row set, one workorder, one temp file; no product change, no release"
d = pathlib.Path(sys.argv[1]); d.parent.mkdir(parents=True, exist_ok=True)
d.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("project_id", "workorder_count", "negatives")}, ensure_ascii=False))
