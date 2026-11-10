#!/usr/bin/env bash
# R26/L1 — replay the four r26 CI steps (plus the manifest pre-check) exactly as the workflow runs them,
# recording the real exit code of each. Paths are the workflow's own.
set -u
ROUND="C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum/evidence/fhs-w0-r26-repair-20261109"
PY="C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe"
cd "$ROUND" || exit 9
rc_all=0
step() {
  local name="$1"; shift
  echo "=== STEP: $name"
  echo "=== CMD: $*"
  "$@"
  local rc=$?
  echo "=== EXIT: $rc"
  [ $rc -ne 0 ] && rc_all=1
  echo
  return 0
}
step "r26 payload manifest resolves inside its own payload" \
  "$PY" tools/verify_payload_manifest.py --root .
step "r26 gate (payload profile, includes G29)" \
  "$PY" tools/gate_r20.py --round . --profile payload --scope payload --skip-hygiene
step "r26 signed vote quorum (17 cases)" \
  "$PY" tools/verify_quorum.py --selftest
step "r26 signed vote quorum scan (signed receipts, fail-closed)" \
  "$PY" tools/verify_quorum.py --root .
step "r26 checksums" sha256sum -c SHA256SUMS
echo "=== ALL_STEPS_EXIT: $rc_all"
exit $rc_all
