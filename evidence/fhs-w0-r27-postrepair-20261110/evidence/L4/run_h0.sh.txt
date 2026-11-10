#!/usr/bin/env bash
# H0 — HGK ancestry forensic. Read-only. Captures raw output + exit per command.
set -u
CLONE="C:/Projects/Agent_Workspace/FHS/HG-KSEOS"
OUT="C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/L4"
A=acd9196f
B=86f40ec

run() {
  local name="$1"; shift
  local log="$OUT/h0_${name}.log"
  { printf '$ git -C %s %s\n' "$CLONE" "$*"; git -C "$CLONE" "$@" 2>&1; } > "$log"
  local rc=$?
  printf 'EXIT=%d\n' "$rc" >> "$log"
  printf '%-28s exit=%d log=%s sha256=%s\n' "$name" "$rc" "$log" "$(sha256sum "$log" | cut -d' ' -f1)"
}

echo "== host =="
date -Is
git --version
echo "== clone =="
git -C "$CLONE" rev-parse --show-toplevel

run resolve_A rev-parse $A
run resolve_B rev-parse $B
run catfile_A cat-file -p $A
run catfile_B cat-file -p $B
run mergebase merge-base $A $B
run roots_A rev-list --max-parents=0 $A
run roots_B rev-list --max-parents=0 $B
run roots_all_A rev-list --max-parents=0 --all
run count_A rev-list --count $A
run count_B rev-list --count $B
run leftright rev-list --left-right --count "$A...$B"
run tree_A log -1 --format=%T $A
run tree_B log -1 --format=%T $B
run is_ancestor_AinB merge-base --is-ancestor $A $B
run is_ancestor_BinA merge-base --is-ancestor $B $A
run shallow rev-parse --is-shallow-repository
run refs_list refs list
run for_each_ref_roots rev-list --max-parents=0 --branches --all
run ancestors_A rev-list --count $A --not $B
run ancestors_B rev-list --count $B --not $A
