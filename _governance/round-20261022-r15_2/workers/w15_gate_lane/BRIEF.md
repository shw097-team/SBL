# EXECUTE brief — W15 gate diff: re-emit and prove the DELIVERY_READY guard behaviourally

You are the bounded writer. Everything you produce goes **only** under
`C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/w15_gate_lane/`.
You must NOT modify `C:/Projects/Agent_Workspace/HG-KSEOS` (read-only source), must not run git commit,
must not dispatch another lane, must not spawn sub-agents.

## Context

`workers/candidate_proposals/w15_gate/proposal.diff` changes one guard in
`HG-KSEOS/src/hg_kseos/lifecycle.py` so that the "pending work orders" refusal fires at `DELIVERY_READY`
as well as `DELIVERED`. It was authored in-session and therefore has **no lane receipt**; this job exists to
re-do it under the mandated lane and to prove the behaviour with executed tests rather than inspection.

## Steps (do them in order, keep each command's output)

1. `mkdir -p workers/w15_gate_lane/isolated` and copy `HG-KSEOS/src` into
   `workers/w15_gate_lane/isolated/src` (plain copy, do not touch the original).
2. Apply `workers/candidate_proposals/w15_gate/proposal.diff` to the copy with
   `git apply -p1 --directory=isolated <diff>` from the round-tree root, or `patch -p1` inside
   `isolated/`. Record the command, exit code, and `sha256sum` of `isolated/src/hg_kseos/lifecycle.py`
   before and after.
3. Write `workers/w15_gate_lane/test_delivery_ready_guard.py` with exactly these four behavioural cases,
   each driving the real `ProjectLifecycle` transition code against a temporary spine database (copy the
   fixture style already used by `HG-KSEOS/tests/` — read one, do not invent an ORM):
   - T1 open required work order + `-> DELIVERY_READY` => refused `ERR_PENDING_WORK_CANNOT_DELIVER`
   - T2 open required work order + `-> DELIVERED` => refused `ERR_PENDING_WORK_CANNOT_DELIVER`
   - T3 all required work orders terminal (`VERIFIED`) + `-> DELIVERY_READY` => allowed, state persisted
   - T4 an illegal transition (e.g. `DRAFT -> DELIVERED` if not in `VALID_TRANSITIONS`) still refused
     `ERR_ILLEGAL_TRANSITION` — i.e. the new guard did not widen the transition set
4. Run them:
   `"C:/Users/user/AppData/Roaming/uv/python/cpython-3.12-windows-x86_64-none/python.exe" -m pytest -q -p no:cacheprovider workers/w15_gate_lane/test_delivery_ready_guard.py`
   with `PYTHONPATH` pointing at `isolated/src` (never at the live HG-KSEOS/src). Capture the full output.
   If a test fails because the copy cannot import, fix the copy's `PYTHONPATH`, not the production file.
5. Write `workers/w15_gate_lane/RESULT.json`:
   `{"applied": bool, "diff_sha256": "...", "lifecycle_sha256_before": "...", "lifecycle_sha256_after": "...",
     "tests": [{"id": "T1", "cmd": "...", "rc": 0, "verdict": "PASS|FAIL", "observed": "<=200 chars"}],
     "control_plane_untouched": true, "claim_ceiling": "candidate diff validated in an isolated copy; not applied to the live control plane"}`
6. Also emit `workers/w15_gate_lane/proposal.reapplied.diff` = `git diff` of the isolated copy against the
   source, so the patch can be replayed byte-for-byte by someone else.

## Rules

- If the guarded behaviour cannot be exercised without editing production code, write that fact into
  RESULT.json under `"blocked_reason"` and stop. Do not weaken a test to get green.
- Every number in RESULT.json must come from a command you actually ran this turn.
- Your final message: the four verdicts, the two sha256 values, and one line naming the exact file paths you wrote.
