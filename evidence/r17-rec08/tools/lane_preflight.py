#!/usr/bin/env python3
"""REC08 F1 — lane preflight.

Separates the failure classes REC08 §F1 demands:
  RELAY_UNREACHABLE / PROVIDER_QUOTA / MODEL_UNSERVED / ARM_NO_NONCE /
  EXECUTOR_TIMEOUT / OK

Read-only against the relay: one tiny deterministic handshake that demands a
nonce echo. Never writes to a governed repo. Emits a JSON receipt.

Usage:
  python tools/lane_preflight.py --base http://127.0.0.1:10105/v1 \
      --model deepseek-v4.1-flash --nonce R17REC08-F1-01 \
      --out receipts/F1_PREFLIGHT.json [--timeout 90]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

RELAY_UNREACHABLE = "RELAY_UNREACHABLE"
PROVIDER_QUOTA = "PROVIDER_QUOTA"
MODEL_UNSERVED = "MODEL_UNSERVED"
ARM_NO_NONCE = "ARM_NO_NONCE"
EXECUTOR_TIMEOUT = "EXECUTOR_TIMEOUT"
MODEL_NONCOMPLIANCE = "MODEL_NONCOMPLIANCE"
OK = "OK"


def _post(url: str, payload: dict, timeout: float) -> tuple[int, str]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:  # 4xx/5xx still carries a body
        return exc.code, exc.read().decode("utf-8", "replace")


def _get(url: str, timeout: float) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - classification is the point
        return 0, f"{type(exc).__name__}: {exc}"


def classify(status: int, body: str, nonce: str) -> tuple[str, dict]:
    """Map one handshake to exactly one REC08 failure class."""
    detail: dict = {"http_status": status, "nonce_echoed": nonce in body}

    if status == 0:
        return RELAY_UNREACHABLE, detail
    if status == 429:
        return PROVIDER_QUOTA, detail
    if status in (401, 403):
        # credential rejected / not provisioned for this model
        return MODEL_UNSERVED, detail
    if status == 404:
        return MODEL_UNSERVED, detail
    if status >= 500:
        return RELAY_UNREACHABLE, detail
    if status == 200:
        if nonce not in body:
            return ARM_NO_NONCE, detail
        return OK, detail
    return MODEL_NONCOMPLIANCE, detail


def extract_served(body: str) -> dict:
    """Pull whatever identity the relay actually returned."""
    out: dict = {}
    try:
        doc = json.loads(body)
    except Exception:  # noqa: BLE001
        return out
    for key in ("model", "system_fingerprint"):
        if isinstance(doc.get(key), str):
            out[key] = doc[key]
    choices = doc.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") or {}
        if isinstance(msg.get("content"), str):
            out["content"] = msg["content"][:400]
    usage = doc.get("usage")
    if isinstance(usage, dict):
        out["usage"] = {
            k: usage.get(k)
            for k in ("prompt_tokens", "completion_tokens", "total_tokens")
            if k in usage
        }
    if isinstance(doc.get("output"), list):  # responses-style
        chunks = []
        for item in doc["output"]:
            for part in item.get("content") or []:
                if isinstance(part.get("text"), str):
                    chunks.append(part["text"])
        if chunks:
            out["content"] = "".join(chunks)[:400]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:10105/v1")
    ap.add_argument("--model", default="deepseek-v4.1-flash")
    ap.add_argument("--nonce", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=float, default=90.0)
    args = ap.parse_args(argv)

    receipt: dict = {
        "schema": "LANE_PREFLIGHT.v1",
        "order": "REC08_F1",
        "nonce": args.nonce,
        "base": args.base,
        "requested_model": args.model,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    health_status, health_body = _get(args.base.rsplit("/v1", 1)[0] + "/healthz", 10)
    receipt["healthz"] = {"status": health_status, "body": health_body[:200]}

    prompt = (
        f"Reply with exactly this token and nothing else: {args.nonce}\n"
        "Do not call tools. Do not read files. One short line."
    )
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 32,
        "temperature": 0,
        "stream": False,
    }

    t0 = time.monotonic()
    try:
        status, body = _post(args.base + "/chat/completions", payload, args.timeout)
    except Exception as exc:  # noqa: BLE001 - timeouts land here
        elapsed = round(time.monotonic() - t0, 2)
        name = type(exc).__name__
        verdict = EXECUTOR_TIMEOUT if "timeout" in name.lower() else RELAY_UNREACHABLE
        receipt.update(
            verdict=verdict,
            error=f"{name}: {exc}",
            elapsed_seconds=elapsed,
            detail={"http_status": 0, "nonce_echoed": False},
        )
    else:
        elapsed = round(time.monotonic() - t0, 2)
        verdict, detail = classify(status, body, args.nonce)
        served = extract_served(body)
        # arm identity must come from what actually answered, never the request
        served_arm = None
        if served.get("model"):
            m = served["model"]
            served_arm = m if "/" in m else f"opencode-go/{m}"
        receipt.update(
            verdict=verdict,
            elapsed_seconds=elapsed,
            detail=detail,
            served=served,
            served_arm=served_arm,
            required_arm=f"opencode-go/{args.model}",
            arm_matches=_arm_matches(served_arm, args.model),
            raw_body_head=body[:1200],
        )

    receipt["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    receipt["conclusion"] = _conclusion(receipt)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(json.dumps({k: receipt[k] for k in ("verdict", "elapsed_seconds", "conclusion")},
                     ensure_ascii=False))
    return 0 if receipt["verdict"] == OK else 1


def _arm_matches(served_arm: str | None, requested_model: str) -> bool:
    if not served_arm:
        return False
    return served_arm == f"opencode-go/{requested_model}"


def _conclusion(receipt: dict) -> str:
    v = receipt["verdict"]
    if v == OK:
        if receipt.get("arm_matches"):
            return "ARM_QUALIFIED: required==served and nonce echoed"
        return "TRANSPORT_OK_BUT_ARM_UNQUALIFIED: nonce present, served identity differs from required"
    return {
        RELAY_UNREACHABLE: "relay is not answering; fix transport before any dispatch",
        PROVIDER_QUOTA: "provider quota exhausted; do not retry blindly, escalate",
        MODEL_UNSERVED: "relay up but this model/credential is not served",
        ARM_NO_NONCE: "model answered but did not echo the dispatch nonce",
        EXECUTOR_TIMEOUT: "arm did not finish within the budget",
        MODEL_NONCOMPLIANCE: "unexpected status; treat as fail-closed",
    }.get(v, v)


if __name__ == "__main__":
    sys.exit(main())
