"""Local pass-through to opencode.ai/zen/go/v1 - the sanctioned EXECUTE route is broken, not the model.

Measured 2026-10-23:
  * https://opencode.ai/zen/go/v1/responses with the shw0968 key answers 200 for deepseek-v4.1-flash
    (and mimo-v2.6-flash answers 200 on /chat/completions), so the mandated EXECUTE arm is AVAILABLE.
  * the two local proxies are not: :10101 (opencodex) forwards a credential the provider calls invalid,
    :10102 (desktop-model-router) holds a key whose workspace is over its monthly limit (429).

This shim exists so a lane can reach the model the owner already pays for without touching either proxy (both
belong to other sessions) and without minting anything: it reads ONE key file, adds the session header the
provider demands, and streams the answer back unchanged. It is a TRANSPORT, not an authority: it never decides
anything, and a lane that uses it must disclose `transport: ocg_passthrough` in its receipt.

Usage:  python tools/ocg_passthrough.py --port 10105 --key-file "<path>" [--upstream https://opencode.ai/zen/go/v1]
"""
from __future__ import annotations

import argparse
import http.client
import json
import ssl
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

KEY = ""
UPSTREAM = "https://opencode.ai/zen/go/v1"
PROVIDER_PREFIXES = ("opencode-go/", "opencode-go:")


def rewrite_model(raw: bytes) -> bytes:
    """codex sends the provider-qualified slug; the provider wants the bare model name."""
    try:
        obj = json.loads(raw)
    except Exception:
        return raw
    m = obj.get("model")
    if isinstance(m, str):
        for p in PROVIDER_PREFIXES:
            if m.startswith(p):
                obj["model"] = m[len(p):]
                return json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return raw


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ocg-passthrough/1"

    def log_message(self, fmt, *args):  # keep the lane's stdout clean
        sys.stderr.write("ocg_passthrough: " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/healthz", "/"):
            self._send(200, json.dumps({
                "schema": "OCG-PASSTHROUGH-HEALTH/1",
                "status": "ok",
                "upstream": UPSTREAM,
                "claim_ceiling": "TRANSPORT_ONLY_NOT_AN_AUTHORITY",
                "model_rewrite": "provider-qualified slug -> bare model name",
            }).encode())
            return
        if self.path.startswith("/v1/models"):
            self._proxy("GET", b"")
            return
        self._send(404, b'{"error":"not proxied"}')

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        self._proxy("POST", body)

    def _proxy(self, method: str, body: bytes):
        u = urlparse(UPSTREAM)
        conn = http.client.HTTPSConnection(u.netloc, timeout=600, context=ssl.create_default_context())
        path = u.path + self.path[len("/v1"):] if self.path.startswith("/v1") else self.path
        headers = {
            "Authorization": "Bearer " + KEY,
            "x-opencode-session": "hgk-lane-" + uuid.uuid4().hex,
            "Content-Type": self.headers.get("Content-Type", "application/json"),
            "Accept": self.headers.get("Accept", "text/event-stream, application/json"),
        }
        if body:
            body = rewrite_model(body)
            headers["Content-Length"] = str(len(body))
        try:
            conn.request(method, path, body=body or None, headers=headers)
            resp = conn.getresponse()
        except Exception as exc:  # transport failure is reported, never invented around
            self._send(502, json.dumps({"error": {"type": "passthrough_upstream_unreachable",
                                                  "message": str(exc)}}).encode())
            return
        self.send_response(resp.status)
        self.send_header("Content-Type", resp.getheader("Content-Type", "application/json"))
        if resp.status != 200:
            try:
                data = resp.read()
            except Exception:
                data = b""
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            self.wfile.write(b"%x\r\n" % len(chunk) + chunk + b"\r\n")
            self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


def main() -> int:
    global KEY, UPSTREAM
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=10105)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--upstream", default=UPSTREAM)
    a = ap.parse_args()
    UPSTREAM = a.upstream.rstrip("/")
    KEY = open(a.key_file, encoding="utf-8").read().strip()
    if not KEY:
        print("empty key file", file=sys.stderr)
        return 2
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(json.dumps({"schema": "OCG-PASSTHROUGH-START/1", "listen": f"http://{a.host}:{a.port}",
                      "upstream": UPSTREAM, "key_len": len(KEY),
                      "claim_ceiling": "TRANSPORT_ONLY_NOT_AN_AUTHORITY"}), flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
