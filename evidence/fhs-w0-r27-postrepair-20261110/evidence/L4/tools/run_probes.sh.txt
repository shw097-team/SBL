#!/usr/bin/env bash
# L4 — evidence probes that need an explicit exit code. Read-only against the worktree; writes only logs.
set -u
E="C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/L4"
WT="C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge"
PY="C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe"
HOOK="C:/Projects/Agent_Workspace/FHS/HG-KSEOS/.git/hooks/pre-commit"

# --- 1. the four H0 driver logs are per-command; the driver itself gets an exit line ------------
cd "$E" || exit 1
{
  echo '$ bash run_h0.sh   (re-run to capture the driver exit code)'
  bash run_h0.sh
} > "$E/h0_driver_rerun.log" 2>&1
echo "EXIT=$?" >> "$E/h0_driver_rerun.log"
cp "$E/h0_driver_rerun.log" "$E/h0_driver.log"

# --- 2. identity of the committed blobs ---------------------------------------------------------
cd "$WT" || exit 1
{
  echo '# working tree vs committed blob digests'
  for p in config/lane-routing-registry.yaml config/lane-route-slots.candidate.json \
           config/model-lane-assignment.json scripts/lane_epoch_validate.py tests/test_lane_epoch_validate.py; do
    w=$(sha256sum "$p" | cut -d' ' -f1); c=$(git cat-file -p "HEAD:$p" | sha256sum | cut -d' ' -f1)
    if [ "$w" = "$c" ]; then r=IDENTICAL; else r=DIFFERS; fi
    echo "$r  $p  worktree=$w  blob=$c"
  done
  echo '# HEAD / tree / base / ahead'
  git log -1 --format='%H %T %s'
  git merge-base HEAD origin/main
  git rev-list --count origin/main..HEAD
  echo '# nothing pushed: no ref on origin names this commit'
  git branch -r --contains HEAD
} > "$E/final_commit_identity.log" 2>&1
echo "EXIT=$?" >> "$E/final_commit_identity.log"

# --- 3. why the installed pre-commit hook cannot run -------------------------------------------
{
  echo "hook path: $HOOK"
  echo "hook sha256: $(sha256sum "$HOOK" 2>/dev/null | cut -d' ' -f1)"
  echo '--- hook body ---'; cat "$HOOK" 2>&1
  echo '--- core.hooksPath (empty = unset) ---'; git -C "$WT" config --get core.hooksPath
  echo '--- interpreter the hook hardcodes ---'
  ls "C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/venv/Scripts/python.exe" 2>&1
  echo '--- scripts/review_lock.py at acd9196f ---'
  git -C "$WT" cat-file -e acd9196f:scripts/review_lock.py 2>&1
  echo "cat-file exit=$?"
  echo '--- latest ref that does carry it ---'
  git -C "$WT" log --all --format='%h %ad %s' --date=short -1 -- scripts/review_lock.py
} > "$E/precommit_hook_defect.log" 2>&1
echo "EXIT=$?" >> "$E/precommit_hook_defect.log"

# --- 4. semantic diff of reconcile --write ----------------------------------------------------
"$PY" "$E/tools/reconcile_write_semantic_diff.py" "$E" > "$E/ported_reconcile_write_semantic_diff.log" 2>&1
echo "EXIT=$?" >> "$E/ported_reconcile_write_semantic_diff.log"

for f in h0_driver final_commit_identity precommit_hook_defect ported_reconcile_write_semantic_diff; do
  printf '%-40s %s  %s\n' "$f" "$(tail -1 "$E/$f.log")" "$(sha256sum "$E/$f.log" | cut -d' ' -f1)"
done
