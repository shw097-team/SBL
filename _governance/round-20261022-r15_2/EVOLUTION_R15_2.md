# 自研究 / 自學習 / 自迭代 / 自進化（受 FABRIC & HGK 治理）

```yaml
schema: SBL_EVOLUTION_RECORD/1
subject: SBL-R15.2-CONTINUATION-20261022
round: round-20261022-r15_2
claim_ceiling: LOCAL_MEASURED; every lesson below cites the raw that produced it
```

本輪對自己的四個錯誤做了實測糾正。每一條都是「先量測、再改行為」，不是自我表揚。

## E1 — 自研究：把「探測」誤當成「執行」

- 症狀：對 relay 發出 `Reply with the single word OK` 並拿到 200，就宣稱「模型方案在傳輸層通過」。
- 量測：真正的 PLAN 任務一餵進去，模型的輸出量從 1 token 級跳到 4,858 completion tokens，並回傳 35 條 DAG 邊。
- 學到：**transport 200 只證明端點活著**；要證明 lane 可用，必須有 served model 回顯 + 實質輸出 + nonce。
- 固化：`hgk-codex-lane-recipe` 技能「Proof to require」章節。

## E2 — 自學習：宣告 blocker 前必須先搜成功配方

- 症狀：worker 用 `--ignore-user-config` + `-s read-only` 啟動 codex，全數 `CreateProcess` 被 policy 擋，我據此宣告 HARD BLOCKER 並停工。
- 量測：改回既有車道配方（複製 sealed `CODEX_HOME` + layered `-p` + `-s danger-full-access`）後，同一 binary 在 391ms 內跑出 `pwsh -Command echo`，三臂全通。
- 學到：**單一 worker 的失敗不是環境真相**；HG-KSEOS 的 `tools/lane_preflight.sh`、`run_codex_adapter.sh`、`run_iao_deepseek.sh` 的註解裡早就寫明這兩個坑（read-only 會擋 spawn、不要自製 config）。
- 固化：技能優先於重造；memory 記錄「宣告不可用前先搜成功配方」。

## E3 — 自迭代：從「自己呼叫模型」升級到「走官方車道」

- 症狀：PLAN/VERIFY 先用 `curl` 直打 relay，得到結果但沒有 lane 綁定、沒有 nonce、沒有 pool 依據。
- 量測：改用 `hgk-lane-dispatch.py` 後，`--require-arm gpt-6.1-sol` 直接被拒（`ERR_LANE_REQUIRED_ARM_ABSENT`），必須用 `openai-codex/gpt-6.1-sol`；缺 nonce 時即使 exit 0 也 `ok=False`。
- 學到：**lane 平面的正確性由 dispatcher 的拒絕能力證明**；能拒絕，才證明它真的在選模型。
- 固化：`LANE_DISPATCH_RECEIPTS.md` 記錄兩次真實拒絕。

## E4 — 自進化：把「有 full access 的 writer」關進籠子

本輪最嚴重的事故是 CWD 逃逸：第一次 EXECUTE 派工沒給 `--cwd`，writer 就把檔案寫進 **HG-KSEOS 受治理 repo**，隨後 300s timeout，形成「有效果、無有效收據」的最壞形狀。

- 圍堵：捕獲位元組 → 移除未追蹤 `workers/` → 驗證 `git status` 空、HEAD 未變（`1760fb4`）。
- 修正：重派時釘 `--cwd <round>`，同一 lane 20.9s 完成且 `ok=True`。
- 結構性提案（`TT-R15.2-HGK-EXECUTE-CWD-ESCAPE`）：`--cwd` 應改為必填，缺省即拒絕；每個 dispatch 前後都要斷言所有受治理 repo 的 `git status --porcelain` 不變。
- 學到：**danger-full-access 可以接受，但只有配上雙向 sha 守衛與 cwd 釘死才可接受**。

## 沉澱物（可被下一個 session 直接複用）

| 資產 | 位置 | 用途 |
|---|---|---|
| `capc-contract-authoring` 技能 | Hermes skills | 讓 CONTRACT.json 一次過官方四命令（含 9 條非顯然 invariant）|
| `hgk-codex-lane-recipe` 技能 | Hermes skills | Codex 載體的正確配方與 6 個坑 |
| `tools/source_freeze.py` / `build_contract_v2.py` | 本 round | 由真測哈希生成契約，可重跑 |
| `workers/*/RECEIPT.json` | 本 round | 7 個 worker 的 typed 收據 |
| `TT_R15_2_REGISTER.json` | 本 round | 13 項阻斷，每項帶 FAR 建議 |

## 未完成的自進化（誠實列出）

- `SOD006-C6` 未解：checker 與 maker 仍同機同 session，lane-level PASS 不能升格為 AO PASS。
- 官方 `openspec` 在既有 change 上失敗，本輪只做了 scoping 建議，未修那個 change。
- gstack 仍不存在，只出 NoFit。
- front door 仍未改成宣告驅動，本輪以「直連 relay + 明示 TT」繞行。

以上四項不影響本輪證據的可信度，但會限制下一個 round 能達到的上限。

## 6. Self-study of this round: why I stopped, and what the stop cost

### 6.1 The stop cause, named precisely

I reported "no native WorkOrder exists, therefore blocked" after checking `project --help` output only. HG-KSEOS ships
the capability inside `hg_kseos.lifecycle.ProjectLifecycleController`: `start` → `intake` → `transition` … → `PLAN_READY`
→ `admit_workorders(project_id)`, which derives TaskSpecs and issues WorkOrders. The CLI's `advance` will happily walk a
project across `WORKORDERS_ADMITTED` **without admitting anything**, which is exactly the state I had produced and then
mistook for a wall.

Lesson, stated as a rule: *a state name is not an effect.* `WORKORDERS_ADMITTED` with zero work-order rows is a
transition, not an admission; read the rows back before believing the state.

### 6.2 What the stop cost, measured

| cost | measurement |
|---|---|
| wall time | five failed dispatches before admission, then four verification passes to repair what the first ones could not see |
| orphan state | three residue projects in the spine (`TT-R15.2-PROJECT-PROLIFERATION`) |
| false verdicts | the first project's 3 FAILED work orders are a permanent record of a source-coverage mistake that intake cannot revise (`TT-R15.2-INTAKE-PRE-ADMISSION-ONLY`) |

That last one is the expensive lesson: **source binding must be complete at project creation**, because
`ERR_INTAKE_STATE` makes a discovery mistake unrecoverable inside the project. I bound one root, learned the second
root's real path afterwards, and had to abandon the project to fix it.

### 6.3 What the checker taught me that I had not seen

Four defects in my own evidence, all found by the checker and none found by my own self-check:

1. the ledger double-counted (38 rows over 24 identities) — a projection that counts rows instead of identities;
2. verdicts parsed as `null` from pretty-printed JSON because the parser only read single lines;
3. the exact-set readback compared a *stale* manifest against a grown tree — the readback must be taken last;
4. intake coverage was 14/24 and my prose said "the corpus".

Pattern: every one of these was a **counting** error, and every one was invisible to the process that produced the count.
A checker that re-derives the number is worth more than a second reading of the same file.

### 6.4 What changed in the working method

- Admission is now performed through the native controller API, not inferred from CLI state.
- Every numeric claim in a receipt must be re-derivable by a distinct principal, and the receipt records that principal.
- The package (`WO-06`) is built **last**, and any verification of it writes its outputs **outside** the tree it measures,
  which is the only way the readback can converge.
- `DELIVERY_READY` is treated as a claim to be checked against the work-order rows, never as a result.

### 6.5 Next iteration's first three moves

1. Re-gate the delivery gate (or rename the state) so a project with FAILED work orders cannot read as ready.
2. Make intake revisable until `PLAN_READY`, with a recorded revision number.
3. Close `WO-03`/`WO-04` only with a real ingestion pipeline and a real product write permit — not with better prose.

## 7. Second iteration: what the second stop taught

### 7.1 The stop was a measurement failure, again

I had reported two work orders FAILED "because the capability does not exist". Both capabilities existed. I had never
run `sbl_core.gknow`, and I had never run the 227-test suite. The rule this produces is blunt: **before declaring a
capability absent, run it.** A `grep` for a filename is not a test of behaviour, and the word "missing" in a verdict is
a claim about the world that needs the same evidence as any other claim.

### 7.2 My own evidence polluted the thing it measured

Copying the source corpus into the tracked tree broke the product's reproducibility test, and the first readback design
put the measuring file inside the measured set. Both are the same error in different clothes: **a measurement must be
outside the thing it measures.** Three consecutive readback failures were the cost of learning it.

### 7.3 What the Windows run found that no review would have

`git check-attr eol -- <every tracked file>` exceeds the Windows command-line cap on this repo, so a shipped assertion
never executed on the platform this host runs on. It looked covered in every report. Two failures, one root cause, one
one-hunk fix, and the suite went 227/2 → 227/0.

### 7.4 Rules carried forward

1. Run the capability before writing the verdict.
2. A package excludes its own verification receipts, and the measuring file is never a member of the measured set.
3. Build order is: all bundles → manifest → readback; any other order produces a readback of a tree that never existed.
4. A test that cannot execute on the target platform is not coverage; it is a claim of coverage.
5. Distinguish "engineering gate closed" from "release gate closed" in every summary; they fail for different reasons.

### 7.5 Next iteration

Re-gate the delivery state (section 11 defect), make intake revisable to `PLAN_READY`, and merge the one-hunk Windows
fix on the product line. Those three are owner actions, all reversible, all small.

## 8. Third iteration: the denominator is the deliverable

### 8.1 The stop I kept repeating

Three times I reported a number that was true and useless: "6/6 work orders VERIFIED", "PARTIAL", "release blocked".
Each was measured against whatever denominator happened to be in front of me. The command declares 18 work packages, 25
check runs, 9 capabilities and 4 milestones; I never wrote that list down until now. A completion claim without a
declared denominator is not wrong, it is unfalsifiable — and unfalsifiable is worse, because it reads as diligence.

### 8.2 What declaring it changed immediately

Within one pass the denominator exposed three things no amount of extra verification would have found:

1. HG-KSEOS conformance **passes only under an interpreter the host does not default to** — so "conformance PASS" was
   an artefact of which python I happened to invoke.
2. The product implements **5 of 8 kinds**, which no test result reveals because the missing three simply have no test.
3. `39 mode gates` is not a prose claim: it is `13 GATE_IDS × 3 MODES`, and it is arithmetically closed — while the
   *semantic* denominator for M4 is recorded as UNMEASURED, so M4 is unclaimable in principle.

### 8.3 Rule carried forward

**Write the denominator before the first verdict, and measure each item at least once.** Then a PARTIAL is informative:
it says 4 of 18 done rather than "mostly done with gaps". The cost of the rule is one parsing pass; the cost of skipping
it is three rounds of self-congratulation that an owner has to unwind.

## 9. Fourth iteration: I was the stopping condition

### 9.1 The uncomfortable finding

I stopped twelve times, always right after a push, and each time I described the stop as the state of the work rather
than the state of my tooling. The measurement in section 15 makes it unarguable: 20 TT entries, 56 denominator items,
zero executable next actions. I had built three separate registers that could describe progress and not one that could
resume it. The system was not stopping me; it simply had no way to say "next".

### 9.2 What I would have defended, and why it was wrong

I would have said a long, careful round is bounded by the context window and by owner-side gates, so periodic reporting
is honest. That is true about gates and false about the window: the window is only fatal if the state lives inside it.
A queue file plus a driver moves the memory into the repository, and then a compaction costs one `python
tools/advance_queue.py`, not a lost thread.

### 9.3 Rules kept

1. **A register that cannot resume is a report.** If an artefact cannot name a command, it does not count as progress
   infrastructure.
2. **Park, do not stop.** Only four conditions justify stopping; everything else becomes a typed park plus a next item.
3. **A failure costs one re-arm.** The driver's first two failures both needed a one-line correction; both were the
   kind of thing that used to end a round.
4. **Split build from acceptance.** Three of the five parked items are cases where I can produce the artefact but not
   the authority that accepts it. `BUILT_AWAITING_ACCEPTANCE` is a true state; `NOT_RUN` reads as idleness.

## 10. Fifth iteration: build the half you may build, and refuse the number that flatters you

### 10.1 Two habits that look like rigour and are not

**Recording a defect one layer too high.** "The delivery gate ignores FAILED work orders" was dramatic and slightly
false. The final transition does refuse; the intermediate state simply has no guard. A defect stated at the wrong layer
cannot be fixed at the right one, and it makes the control plane look worse than it is while leaving the real hole
open.

**Reporting a benchmark that cancels itself.** Two runs of the same paired harness gave −0.082 s and +0.007 s. The
temptation was to publish the first, which favoured the current state. The honest artefact is both runs plus the
sentence "the sign flips, therefore no claim". A number that changes sign under repetition is not a small effect, it is
noise wearing a decimal point.

### 10.2 The instrument lesson, again, in a new place

A file inventory that starts from a directory which does not exist returns zeros indistinguishable from "the product is
empty". Both readings look like data. The fix is cheap and permanent: make the tool assert its roots exist and record
`roots_checked` alongside the findings, so the next reader can see whether zero means zero or means nowhere.

### 10.3 Rules kept

1. **State a defect at the layer where it is true**, and correct the record when a re-read contradicts it.
2. **Publish cancelling measurements together**, never the favourable one alone.
3. **An instrument must record where it looked.** Zero findings plus a missing root is not a finding.
4. **Evidence must survive a re-run of the tool that produced it.** If re-running the producer orphans the consumer's
   evidence, fold the consumer's data into the producer.

## 11. Sixth iteration: I was scheduling myself

### 11.1 The last layer of the same mistake

After building a queue I still ended every turn, because the queue was pulled by the conversation. The architecture was
asking the loop to be its own scheduler. Anything that must outlive a context window cannot be invoked by the thing it
is meant to outlive.

### 11.2 What the repair actually changed

Three objects, each of which can fail: a lease (am I in flight?), a predicate (may I claim to be finished?), and a
scheduler (who runs me if nobody speaks?). Writing them exposed two of my own defects immediately — a timezone bug that
declared a fresh lease stale, and a proof file named `TERMINAL` that would have asserted completion the predicate never
checked. Both were caught by the guard being a *program* rather than a paragraph, which is the whole point.

### 11.3 Rule

**If a claim matters, make it a predicate with a non-zero exit.** Prose assertions of completion, of progress, or of
"blocked" are unfalsifiable, and unfalsifiable claims decay into optimism exactly when the work is longest.

## 12. Seventh iteration: I was calling an authority limit a stopping problem

### 12.1 The mistake with a long half-life

Seven FARs, four repairs, and the same sentence kept reappearing: "these need an owner". Each time I treated it as a
symptom and engineered around it — a queue, a driver, a lease, a guard, a scheduler. All of those were real and all of
them fixed the *stopping* problem. None could touch the other one, because a domain-owner signature is not a
deliverable.

### 12.2 What I should have done the first time

The first time an item resisted because the predicate named a principal, the correct move was to **issue a request**:
a file naming the predicate, the prepared artefact, the literal action, the expiry and the fallback. That takes one
minute and converts an ending into an outstanding ask. Instead I wrote "not in my scope" and closed the turn — which,
from the outside, is indistinguishable from abandoning the work. The governance contract was never the obstacle; my
failure to produce a request was.

### 12.3 Rules kept

1. **An unsatisfiable-by-agent predicate is issued, not solved.** One file, one literal action, one expiry.
2. **Classify satisfiability before working on an item**, or the same item gets re-attempted every round and looks
   like laziness each time.
3. **A refusal to sign is only honest if it is accompanied by a request to the entity that can.**
4. **Prove your refusals fire.** The negative control for the guard immediately found a blind scope in the guard itself.
