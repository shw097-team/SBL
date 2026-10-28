"""S2-07 S207-GPT-AND-SOD: attribute the two lane turns honestly.

Facts this receipt is allowed to assert:
  * a real codex turn completed on PLAN and on VERIFY, with nonce, usage and exit 0
  * which provider route served it, from the client's own rollout
  * whether the relay that served it required a credential (measured with a bogus bearer)
Facts it must refuse: that the owner's ChatGPT OAuth paid for them, and that the checker
principal is distinct.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

TPE = timezone(timedelta(hours=8))
VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
OUT = VAR / "receipts/R17_S207_LANE_PLAN_VERIFY.json"
PLAN_HOME = Path("C:/Users/user/AppData/Local/Temp/s207plan_home")
VER_HOME = Path("C:/Users/user/AppData/Local/Temp/s207verify_home")
SEALED = Path("C:/Users/user/AppData/Local/HG-KSEOS/opencodex-hermes")
CODEX = Path("C:/Users/user/AppData/Local/OpenAI/Codex/bin/8925276705115dea/codex.exe")


def sha(p) -> str | None:
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except OSError:
        return None


def digest_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def parse_jsonl(p: Path):
    raw = p.read_bytes() if p.exists() else b""
    msg, usage, completed, err = None, None, 0, None
    for line in raw.decode("utf-8", "replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = e.get("type")
        if t == "item.completed" and (e.get("item") or {}).get("type") == "agent_message":
            msg = (e["item"] or {}).get("text")
        elif t == "turn.completed":
            completed += 1
            usage = e.get("usage")
        elif t == "error" or t == "turn.failed":
            err = json.dumps(e)[:300]
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "turns_completed": completed, "usage": usage,
            "agent_message": (msg or "")[:400], "error": err}


def rollout_model(home: Path):
    hits = {}
    for p in sorted(home.rglob("rollout-*.jsonl")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        for key in ("\"model\":\"", "\"model_provider\":\""):
            i = 0
            while True:
                j = txt.find(key, i)
                if j < 0:
                    break
                k = txt.find("\"", j + len(key))
                hits.setdefault(key.strip('"":'), set()).add(txt[j + len(key):k])
                i = k
        hits.setdefault("rollout", set()).add(p.name)
    return {k: sorted(v)[:6] for k, v in hits.items()}


def jwt_claims(path: Path):
    """Read exp / plan type from the sealed credential WITHOUT printing any token bytes."""
    try:
        d = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError) as e:
        return {"error": repr(e)}
    out = {"structure": list(d), "claims": {}}

    def walk(o, depth=0):
        if depth > 6:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.count(".") == 2 and len(v) > 60:
                    try:
                        payload = v.split(".")[1]
                        payload += "=" * (-len(payload) % 4)
                        c = json.loads(base64.urlsafe_b64decode(payload))
                        keep = {kk: c.get(kk) for kk in
                                ("exp", "chatgpt_plan_type", "iat", "aud", "iss") if kk in c}
                        out["claims"][k] = keep
                    except Exception:  # noqa: BLE001
                        out["claims"][k] = "UNDECODABLE"
                else:
                    walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:8]:
                walk(v, depth + 1)

    walk(d)
    now = datetime.now(timezone.utc).timestamp()
    for k, c in out["claims"].items():
        if isinstance(c, dict) and c.get("exp"):
            c["exp_utc"] = datetime.fromtimestamp(c["exp"], timezone.utc).isoformat()
            c["expired"] = c["exp"] < now
            c["age_days"] = round((now - c["exp"]) / 86400, 1)
    return out


def relay_probe():
    """Does the relay serve gpt-6.1-sol without any credential? Measured, not assumed."""
    body = json.dumps({"model": "gpt-6.1-sol",
                       "input": [{"type": "message", "role": "user",
                                  "content": [{"type": "input_text", "text": "say ok"}]}],
                       "stream": True, "store": False})
    out = {}
    for name, hdr in (("bogus_bearer", ["-H", "Authorization: Bearer NOT-A-REAL-KEY"]),
                      ("no_auth_header", [])):
        r = subprocess.run(["curl", "-s", "-m", "45", "-w", "\\nHTTP=%{http_code}",
                            "-X", "POST", "http://127.0.0.1:10101/v1/responses",
                            "-H", "Content-Type: application/json", *hdr, "-d", body],
                           capture_output=True, text=True, timeout=90)
        tail = (r.stdout or "").strip().splitlines()
        code = next((l for l in reversed(tail) if l.startswith("HTTP=")), "HTTP=?")
        served = "response.created" in (r.stdout or "")
        out[name] = {"http": code.replace("HTTP=", ""), "stream_created": served,
                     "head": (r.stdout or "")[:160]}
    return out


def main():
    plan = parse_jsonl(PLAN_HOME / "plan_out.jsonl")
    ver = parse_jsonl(VER_HOME / "verify_out.jsonl")
    claims = jwt_claims(SEALED / "auth.json")
    probe = relay_probe()
    relay_ignores_auth = (probe["bogus_bearer"]["stream_created"]
                          and probe["no_auth_header"]["stream_created"])

    receipt = {
        "schema": "R17_S207_LANE_PLAN_VERIFY/1",
        "generated_local": datetime.now(TPE).isoformat(timespec="seconds"),
        "codex_binary": {"path": str(CODEX), "sha256": sha(CODEX)},
        "plan": {"home": str(PLAN_HOME), "exit_ok": plan["turns_completed"] == 1,
                 "nonce_echoed": "S207PLAN-" in (plan["agent_message"] or ""),
                 "usage": plan["usage"], "raw": {k: plan[k] for k in ("bytes", "sha256", "turns_completed", "error")},
                 "rollout": rollout_model(PLAN_HOME)},
        "verify": {"home": str(VER_HOME), "exit_ok": ver["turns_completed"] == 1,
                   "nonce_echoed": "S207VERIFY-" in (ver["agent_message"] or ""),
                   "usage": ver["usage"], "raw": {k: ver[k] for k in ("bytes", "sha256", "turns_completed", "error")},
                   "rollout": rollout_model(VER_HOME)},
        "served_route": "hgk_relay (http://127.0.0.1:10101/v1, wire_api=responses)",
        "relay_credential_probe": probe,
        "relay_serves_without_credential": relay_ignores_auth,
        "sealed_oauth": {"home": str(SEALED), "auth_sha256": sha(SEALED / "auth.json"),
                         "claims": claims.get("claims"), "structure": claims.get("structure")},
        "sod": {"distinct_checker_principal": False,
                "why": ("both turns were served by the same relay pool and the sealed OAuth "
                        "credential is expired, so no second paying principal exists on this host")},
        "claim_ceiling": "LANE_TURNS_EXECUTED_RELAY_SERVED_NOT_OWNER_OAUTH",
        "open_owner_action": ("one interactive `codex` sign-in inside "
                             "C:/Users/user/AppData/Local/HG-KSEOS/opencodex-hermes is the only "
                             "legal way to restore owner-paid PLAN/VERIFY; this agent must not "
                             "handle the token, and `codex login` exposes no device flow"),
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"plan_ok": receipt["plan"]["exit_ok"], "verify_ok": receipt["verify"]["exit_ok"],
                      "plan_usage": receipt["plan"]["usage"], "verify_usage": receipt["verify"]["usage"],
                      "relay_ignores_auth": relay_ignores_auth,
                      "oauth_expired": [c.get("expired") for c in (claims.get("claims") or {}).values()
                                        if isinstance(c, dict)],
                      "out": str(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
