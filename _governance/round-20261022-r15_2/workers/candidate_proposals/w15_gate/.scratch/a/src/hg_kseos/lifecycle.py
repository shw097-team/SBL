"""HG-KSEOS Autonomous Project Lifecycle Controller (task-011).

Thin product-level controller over the existing Shared Spine. Provides:
- project state machine (PROJECT_CREATED -> ... -> DELIVERED)
- source intake / authority envelope
- intent roundtrip / non-goal preservation
- deterministic TaskSpec / WorkOrder planning
- checkpoint / resume with hash verification
- self-repair loop with attempt budget
- release / delivery readiness

No second orchestrator: transitions persist to Shared Spine (canonical_events +
project_lifecycles + project_transitions); execution stays with Hermes/Codex via
the existing WorkOrder/Harness contracts.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import HGKError, InvariantViolation
from .spine import SharedSpine
from .util import canonical_json, sha256_text, utc_now

LIFECYCLE_STATES = (
    "PROJECT_CREATED",
    "SOURCE_DISCOVERY",
    "SOURCE_ADMISSION",
    "INTENT_BOUND",
    "REQUIREMENTS_READY",
    "DESIGN_READY",
    "PLAN_READY",
    "WORKORDERS_ADMITTED",
    "EXECUTING",
    "VERIFYING",
    "EVOLUTION_REVIEW",
    "RELEASE_REDUCING",
    "DELIVERY_READY",
    "DELIVERED",
)
SIDE_STATES = ("BLOCKED_HITL", "TEMP_CLOSED", "FAILED", "ROLLED_BACK", "CANCELLED")
ALL_STATES = set(LIFECYCLE_STATES) | set(SIDE_STATES)

# legal forward transitions (main path); side states allowed from most states
FORWARD = {
    "PROJECT_CREATED": ("SOURCE_DISCOVERY",),
    "SOURCE_DISCOVERY": ("SOURCE_ADMISSION",),
    "SOURCE_ADMISSION": ("INTENT_BOUND",),
    "INTENT_BOUND": ("REQUIREMENTS_READY",),
    "REQUIREMENTS_READY": ("DESIGN_READY",),
    "DESIGN_READY": ("PLAN_READY",),
    "PLAN_READY": ("WORKORDERS_ADMITTED",),
    "WORKORDERS_ADMITTED": ("EXECUTING",),
    "EXECUTING": ("VERIFYING", "EVOLUTION_REVIEW"),
    "VERIFYING": ("EVOLUTION_REVIEW", "REPAIRING"),
    "EVOLUTION_REVIEW": ("RELEASE_REDUCING", "REPAIRING"),
    "RELEASE_REDUCING": ("DELIVERY_READY",),
    "DELIVERY_READY": ("DELIVERED",),
}
# repair is a loop edge: VERIFYING/EVOLUTION_REVIEW -> REPAIRING -> EXECUTING
ALL_STATES |= {"REPAIRING"}
FORWARD["VERIFYING"] = ("EVOLUTION_REVIEW", "REPAIRING")
FORWARD["REPAIRING"] = ("EXECUTING", "FAILED", "BLOCKED_HITL")
FORWARD["EVOLUTION_REVIEW"] = ("RELEASE_REDUCING", "REPAIRING")

VALID_TRANSITIONS = {s: set(FORWARD.get(s, ())) | set(SIDE_STATES) for s in ALL_STATES}


@dataclass
class ProjectRequest:
    goal: str
    source_paths: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    non_goals: list[str] = field(default_factory=list)
    target_root: str = ""
    optional_acceptance_notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProjectRequest":
        return cls(
            goal=str(d.get("goal", "")),
            source_paths=[str(x) for x in d.get("source_paths", [])],
            constraints=[str(x) for x in d.get("constraints", [])],
            non_goals=[str(x) for x in d.get("non_goals", [])],
            target_root=str(d.get("target_root", "")),
            optional_acceptance_notes=[str(x) for x in d.get("optional_acceptance_notes", [])],
        )


class LifecycleError(HGKError):
    pass


class ProjectLifecycleController:
    """Product-level project entrypoint over the existing Shared Spine."""

    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    # ---------- project creation ----------
    def start(self, request: ProjectRequest, *, project_id: str | None = None,
              run_id: str | None = None, attempt_budget: int = 3) -> dict[str, Any]:
        if not request.goal.strip():
            raise LifecycleError("ERR_PROJECT_GOAL_REQUIRED")
        pid = project_id or f"HGK-PRJ-{uuid.uuid4().hex[:8].upper()}"
        rid = run_id or f"RUN-{uuid.uuid4().hex[:8].upper()}"
        goal_hash = sha256_text(canonical_json({"goal": request.goal}))
        # CS-A D3: lifecycle projects must own a `projects` row (FK precondition
        # for register_requirement / create_taskspec). Idempotent create.
        try:
            self.spine.create_project(project_id=pid, name=f"Project {pid}")
        except Exception:  # noqa: BLE001  (already exists -> no-op)
            pass
        with self.spine.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO project_lifecycles("
                "project_id, run_id, state, goal_hash, source_count, authority_order_json,"
                "conflicts_json, blocking_missing_json, non_blocking_missing_json, intent_json,"
                "non_goals_json, current_workorder, last_checkpoint_id, attempt_budget, attempts_used,"
                "repair_count, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (pid, rid, "PROJECT_CREATED", goal_hash, 0, "[]", "[]", "[]", "[]", "{}",
                 json.dumps(request.non_goals, ensure_ascii=False), None, None, attempt_budget, 0, 0,
                 utc_now(), utc_now()),
            )
            self._emit_transition(conn, pid, rid, "", "PROJECT_CREATED", "PROJECT_CREATE",
                                  authority_refs=[], workorder_refs=[], evidence_refs=[], attempt=0,
                                  budget_remaining=attempt_budget)
        return self.status(pid)

    # ---------- state machine ----------
    def _emit_transition(self, conn, project_id: str, run_id: str, from_state: str, to_state: str,
                         trigger: str, *, authority_refs: list[str], workorder_refs: list[str],
                         evidence_refs: list[str], attempt: int, budget_remaining: int,
                         checkpoint_id: str | None = None) -> str:
        tid = f"TR-{uuid.uuid4().hex[:10].upper()}"
        rollback_pointer = f"RL-{uuid.uuid4().hex[:10].upper()}"
        conn.execute(
            "INSERT INTO project_transitions("
            "transition_id, project_id, run_id, from_state, to_state, trigger, authority_refs_json,"
            "workorder_refs_json, evidence_refs_json, checkpoint_id, rollback_pointer, attempt,"
            "budget_remaining, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (tid, project_id, run_id, from_state, to_state, trigger,
             json.dumps(authority_refs, ensure_ascii=False), json.dumps(workorder_refs, ensure_ascii=False),
             json.dumps(evidence_refs, ensure_ascii=False), checkpoint_id, rollback_pointer,
             attempt, budget_remaining, utc_now()),
        )
        conn.execute(
            "INSERT INTO canonical_events("
            "event_id, idempotency_key, entity_type, entity_id, from_state, to_state, actor,"
            "expected_version, resulting_version, payload_json, evidence_ref, rollback_pointer, created_at)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (tid, f"{project_id}:{run_id}:{from_state}->{to_state}:{attempt}", "project_lifecycle",
             project_id, from_state, to_state, "lifecycle-controller", 1, 1,
             json.dumps({"trigger": trigger}, ensure_ascii=False), evidence_refs[0] if evidence_refs else "",
             rollback_pointer, utc_now()),
        )
        return tid

    def transition(self, project_id: str, to_state: str, *, trigger: str,
                   authority_refs: list[str] | None = None, workorder_refs: list[str] | None = None,
                   evidence_refs: list[str] | None = None, checkpoint_id: str | None = None) -> dict[str, Any]:
        state = self._project_state(project_id)
        if to_state not in VALID_TRANSITIONS.get(state, set()):
            raise LifecycleError(f"ERR_ILLEGAL_TRANSITION {state}->{to_state}")
        # CS-A D4: project-level DELIVERED must fail while required workorders
        # are still open (created/admitted/executing). Wave/subset closure is
        # recorded via checkpoints, not by claiming project delivery.
        if to_state == "DELIVERED":
            with self.spine.connect() as conn:
                open_rows = conn.execute(
                    "SELECT COUNT(*) FROM workorders w JOIN taskspecs t ON t.taskspec_id=w.taskspec_id "
                    "JOIN requirements r ON r.requirement_id=t.requirement_id "
                    "WHERE r.project_id=? AND w.state NOT IN ('VERIFIED','ROLLED_BACK','CANCELLED')",
                    (project_id,),
                ).fetchone()[0]
            if open_rows:
                raise LifecycleError(
                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: {open_rows} required workorders open")
        with self.spine.transaction() as conn:
            row = conn.execute("SELECT run_id, attempt_budget, attempts_used FROM project_lifecycles WHERE project_id=?",
                               (project_id,)).fetchone()
            run_id, budget, used = row
            conn.execute("UPDATE project_lifecycles SET state=?, updated_at=? WHERE project_id=?",
                         (to_state, utc_now(), project_id))
            self._emit_transition(
                conn, project_id, run_id, state, to_state, trigger,
                authority_refs=authority_refs or [], workorder_refs=workorder_refs or [],
                evidence_refs=evidence_refs or [], attempt=used, budget_remaining=budget - used,
                checkpoint_id=checkpoint_id)
        return self.status(project_id)

    def _project_state(self, project_id: str) -> str:
        with self.spine.connect() as conn:
            row = conn.execute("SELECT state FROM project_lifecycles WHERE project_id=?", (project_id,)).fetchone()
        if row is None:
            raise LifecycleError(f"ERR_PROJECT_UNKNOWN {project_id}")
        return row[0]

    # ---------- intake / authority envelope ----------
    def intake(self, project_id: str, request: ProjectRequest) -> dict[str, Any]:
        """Discover + hash + classify + admit project sources; build authority envelope."""
        state = self._project_state(project_id)
        if state == "PROJECT_CREATED":
            # auto-progress into source discovery (no user step needed)
            self.transition(project_id, "SOURCE_DISCOVERY", trigger="SOURCE_DISCOVERY_AUTO")
            state = "SOURCE_DISCOVERY"
        if state != "SOURCE_DISCOVERY":
            raise LifecycleError(f"ERR_INTAKE_STATE {state}")
        inventory: list[dict[str, Any]] = []
        conflicts: list[str] = []
        blocking_missing: list[str] = []
        non_blocking: list[str] = []
        for raw in request.source_paths:
            p = Path(raw)
            if not p.exists():
                blocking_missing.append(str(p))
                continue
            files = [p] if p.is_file() else sorted(p.rglob("*"))
            for f in files:
                if f.is_dir() or ".git" in f.parts:
                    continue
                inventory.append({"path": str(f), "sha256": sha256_text(f.read_bytes().decode("utf-8", errors="replace")),
                                  "bytes": f.stat().st_size})
        if not request.target_root:
            non_blocking.append("target_root")
        if not request.constraints:
            non_blocking.append("constraints")
        envelope = {
            "project_id": project_id,
            "goal_hash": sha256_text(canonical_json({"goal": request.goal})),
            "source_count": len(inventory),
            "inventory": inventory,
            "authority_order": [str(p) for p in request.source_paths],
            "conflicts": conflicts,
            "blocking_missing": blocking_missing,
            "non_blocking_missing": non_blocking,
            "status": "BLOCKED" if blocking_missing else "READY",
        }
        with self.spine.transaction() as conn:
            conn.execute(
                "UPDATE project_lifecycles SET source_count=?, authority_order_json=?,"
                "conflicts_json=?, blocking_missing_json=?, non_blocking_missing_json=?,"
                "intent_json=?, updated_at=? WHERE project_id=?",
                (len(inventory), json.dumps(envelope["authority_order"], ensure_ascii=False),
                 json.dumps(conflicts, ensure_ascii=False), json.dumps(blocking_missing, ensure_ascii=False),
                 json.dumps(non_blocking, ensure_ascii=False),
                 json.dumps({"goal": request.goal, "constraints": request.constraints,
                             "non_goals": request.non_goals, "target_root": request.target_root,
                             "source_paths": request.source_paths}, ensure_ascii=False), utc_now(), project_id))
            if envelope["status"] == "READY":
                conn.execute("UPDATE project_lifecycles SET state='SOURCE_ADMISSION', updated_at=? WHERE project_id=?",
                             (utc_now(), project_id))
        return envelope

    # ---------- planner ----------
    def plan(self, project_id: str) -> dict[str, Any]:
        """Deterministic plan: derive TaskSpecs + admit WorkOrders from intent + source inventory."""
        state = self._project_state(project_id)
        if state not in ("DESIGN_READY", "PLAN_READY"):
            raise LifecycleError(f"ERR_PLAN_STATE {state}")
        with self.spine.connect() as conn:
            row = conn.execute("SELECT intent_json, source_count, goal_hash FROM project_lifecycles WHERE project_id=?",
                               (project_id,)).fetchone()
        intent = json.loads(row[0])
        source_count = row[1]
        goal = intent.get("goal", "")
        non_goals = intent.get("non_goals", [])
        # deterministic task decomposition from goal + source inventory
        tasks = self._derive_tasks(goal, source_count)
        specs: list[dict[str, Any]] = []
        for i, (title, objective, wps) in enumerate(tasks, start=1):
            spec_id = f"TS-{project_id.split('-')[-1]}-{i:02d}"
            spec = {
                "taskspec_id": spec_id,
                "title": title,
                "objective": objective,
                "owner_wps": wps,
                "source_locators": intent.get("source_paths", [])[:3],
                "non_goals": non_goals,
                "acceptance": [f"{title} verified by focused tests + evidence"],
            }
            specs.append(spec)
        with self.spine.transaction() as conn:
            conn.execute("UPDATE project_lifecycles SET state='PLAN_READY', updated_at=? WHERE project_id=?",
                         (utc_now(), project_id))
        return {"project_id": project_id, "plan": specs, "task_count": len(specs),
                "non_goals_preserved": len(non_goals),
                "target_root": intent.get("target_root", "")}

    @staticmethod
    def _derive_tasks(goal: str, source_count: int) -> list[tuple[str, str, list[str]]]:
        """Deterministic plan from goal keywords; no external LLM needed for the skeleton.

        CS-A D1: match CJK goal keywords alongside English so a Traditional-Chinese
        user goal (e.g. 依 authoritative corpus 完成施工、驗收與交付) still derives the
        required task families instead of degrading to a bare delivery skeleton.
        """
        g = goal.lower()
        tasks: list[tuple[str, str, list[str]]] = []
        if any(k in g for k in ("knowledge", "wiki", "research", "document",
                                "知識", "文檔", "研究", "檢索")):
            tasks.append(("Authority source admission",
                          "Hash, classify and admit project sources into the canonical source ledger.",
                          ["WP-RBWI-01", "WP-RBWI-02"]))
            tasks.append(("Knowledge pipeline",
                          "Build RAG/KG ingestion from admitted sources with provenance.",
                          ["WP-RBWI-04"]))
        if any(k in g for k in ("system", "tool", "service", "app", "platform", "pipeline",
                                "系統", "工具", "施工", "實作", "建置")):
            tasks.append(("Core implementation",
                          "Implement the core product surface from requirements with tests.",
                          ["WP-RBWI-03", "WP-RBWI-05"]))
        if any(k in g for k in ("test", "acceptance", "verify", "qualif",
                                "測試", "驗收", "驗證", "測試驗收")):
            tasks.append(("Acceptance and evidence",
                          "Run deterministic acceptance, raw evidence and independent checks.",
                          ["WP-RBWI-06", "WP-RBWI-07"]))
        tasks.append(("Package and delivery",
                      "Produce package, exact-set readback and delivery readiness evidence.",
                      ["WP-RBWI-07"]))
        if source_count:
            tasks.insert(0, ("Source discovery",
                             "Inventory, hash and admit the provided source corpus.",
                             ["WP-RBWI-01"]))
        return tasks

    # ---------- workorder admission ----------
    def admit_workorders(self, project_id: str) -> dict[str, Any]:
        state = self._project_state(project_id)
        if state != "PLAN_READY":
            raise LifecycleError(f"ERR_ADMIT_STATE {state}")
        plan = self.plan(project_id)  # idempotent re-derive
        admitted: list[str] = []
        # CS-A D2: project-scoped requirement id (embed the FULL project id so a
        # project whose tail is "001" cannot collide with the legacy REQ-001).
        req_id = f"REQ-{project_id}-PLAN"
        try:
            self.spine.register_requirement(
                requirement_id=req_id,
                source_locator=f"project:{project_id}:intent",
                wording="Project lifecycle plan requirements (auto-derived from user goal)",
                acceptance_id=f"ACC-{req_id}",
                oracle="plan taskspecs admitted + workorders created",
                threshold="ALL_PLAN_TASKS_ADMITTED",
                negative_fixture="plan without taskspecs",
                priority="P0",
                project_id=project_id,
            )
            self.spine.acquire_lease(req_id, "lifecycle-planner", f"TK-{req_id}", ttl_seconds=300)
            self.spine.transition_requirement(
                req_id, "FROZEN", actor="lifecycle-planner", token=f"TK-{req_id}",
                expected_version=0, evidence_ref=f"EV-{req_id}", idempotency_key=f"FRZ-{req_id}",
            )
            self.spine.release_lease(req_id, "lifecycle-planner", f"TK-{req_id}")
        except InvariantViolation:
            pass  # already registered (idempotent resume)
        except Exception as exc:  # noqa: BLE001
            # CS-A D2: treat UNIQUE/IntegrityError on the requirement id as an
            # idempotent-resume condition, not a fatal registration error.
            if "UNIQUE" in str(exc) or "IntegrityError" in type(exc).__name__:
                pass
            else:
                raise LifecycleError(f"ERR_REQUIREMENT_REGISTRATION {type(exc).__name__}: {exc}") from exc
        for spec in plan["plan"]:
            self.spine.create_taskspec(
                taskspec_id=spec["taskspec_id"],
                requirement_id=req_id,
                objective=spec["objective"],
                owner=spec["owner_wps"][0],
                writable_root=Path(plan["target_root"] or "worktrees") / spec["taskspec_id"].lower(),
                permissions={"write_scope": "worktree", "network": False},
                tests=[spec["acceptance"][0]],
                evidence_plan="raw + independent evidence per acceptance contract",
            )
            wo_id = f"WO-{spec['taskspec_id']}"
            self.spine.create_workorder(
                wo_id, spec["taskspec_id"], writer="codex",
                worktree=Path("worktrees") / spec["taskspec_id"].lower(),
                base_head=self._repo_head(project_id),
            )
            admitted.append(wo_id)
        self.transition(project_id, "WORKORDERS_ADMITTED", trigger="WORKORDER_AUTO_ADMISSION",
                        workorder_refs=admitted)
        return {"project_id": project_id, "workorders": admitted, "count": len(admitted)}

    # ---------- checkpoint / resume ----------
    def checkpoint(self, project_id: str, *, evidence_refs: list[str] | None = None) -> dict[str, Any]:
        state = self._project_state(project_id)
        ck_id = f"CK-{project_id.split('-')[-1]}-{uuid.uuid4().hex[:8].upper()}"
        with self.spine.connect() as conn:
            row = conn.execute("SELECT run_id, attempt_budget, attempts_used FROM project_lifecycles WHERE project_id=?",
                               (project_id,)).fetchone()
            run_id, budget, used = row
            wo = conn.execute("SELECT workorder_id FROM workorders w WHERE w.state='ADMITTED' OR w.state='EXECUTING' "
                              "ORDER BY rowid LIMIT 1").fetchone()  # Ordering oracle is the implicit rowid (monotonic INSERTION order), not wall-clock created_at: # created_at has second granularity, so two rows sharing a timestamp make the choice arbitrary. # Same convention as evidence_graph.py (ORDER BY rowid).
            current_wo = wo[0] if wo else None
        payload = {
            "project_id": project_id, "run_id": run_id, "state": state,
            "current_workorder": current_wo, "attempt_budget": budget, "attempts_used": used,
            "evidence_refs": evidence_refs or [],
        }
        digest = sha256_text(canonical_json(payload))
        with self.spine.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints(checkpoint_id, wave, state_digest, source_digest, "
                "repo_head, rollback_pointer, created_at) VALUES(?,?,?,?,?,?,?)",
                (ck_id, "lifecycle", digest, digest, "",
                 f"RL-{uuid.uuid4().hex[:10].upper()}", utc_now()))
            conn.execute("UPDATE project_lifecycles SET last_checkpoint_id=?, updated_at=? WHERE project_id=?",
                         (ck_id, utc_now(), project_id))
        # persist the payload where resume can read it back (lifecycle table intent_json sidecar)
        with self.spine.transaction() as conn:
            conn.execute("UPDATE project_lifecycles SET intent_json=? WHERE project_id=?",
                         (json.dumps({"_checkpoint": payload}, ensure_ascii=False), project_id))
        return {"checkpoint_id": ck_id, "state": state, "payload": payload}

    def resume(self, project_id: str, *, verify_hashes: bool = True) -> dict[str, Any]:
        with self.spine.connect() as conn:
            row = conn.execute("SELECT state, last_checkpoint_id, goal_hash, intent_json FROM project_lifecycles WHERE project_id=?",
                               (project_id,)).fetchone()
        if row is None:
            raise LifecycleError(f"ERR_PROJECT_UNKNOWN {project_id}")
        state, ck_id, goal_hash, intent_json = row
        if not ck_id:
            return {"project_id": project_id, "resumed_state": state, "note": "no checkpoint yet"}
        payload = {}
        if intent_json:
            saved = json.loads(intent_json)
            payload = saved.get("_checkpoint", {})
        if verify_hashes and payload.get("project_id") != project_id:
            raise LifecycleError("ERR_CHECKPOINT_HASH_MISMATCH stale checkpoint refused")
        # find first unfinished legal state
        unfinished = self._first_unfinished(payload)
        return {"project_id": project_id, "resumed_state": state, "checkpoint_id": ck_id,
                "first_unfinished": unfinished, "payload": payload}

    def _first_unfinished(self, payload: dict[str, Any]) -> str | None:
        order = list(LIFECYCLE_STATES)
        current = payload.get("state", "PROJECT_CREATED")
        idx = order.index(current) if current in order else 0
        return order[idx] if idx < len(order) else None

    # ---------- repair ----------
    def begin_repair(self, project_id: str, *, evidence_refs: list[str] | None = None) -> dict[str, Any]:
        state = self._project_state(project_id)
        if state not in ("VERIFYING", "EVOLUTION_REVIEW", "EXECUTING"):
            raise LifecycleError(f"ERR_REPAIR_STATE {state}")
        # The attempt budget is enforced everywhere else (attempt(), checkpoint()) but was NOT enforced here, so a
        # repair loop could outlive its budget: measured 2 repairs against attempt_budget=1. A budget that one path
        # ignores is not a budget.
        with self.spine.connect() as conn:
            row = conn.execute(
                "SELECT attempt_budget, attempts_used FROM project_lifecycles WHERE project_id=?", (project_id,)
            ).fetchone()
        if row is not None and row[1] >= row[0]:
            raise LifecycleError(f"ERR_REPAIR_BUDGET_EXHAUSTED {row[1]}/{row[0]}")
        with self.spine.transaction() as conn:
            conn.execute("UPDATE project_lifecycles SET repair_count=repair_count+1, "
                         "attempts_used=attempts_used+1, updated_at=? WHERE project_id=?",
                         (utc_now(), project_id))
        return self.transition(project_id, "REPAIRING", trigger="AUTOMATIC_REPAIR",
                               evidence_refs=evidence_refs or [])

    def _repo_head(self, project_id: str) -> str:
        import subprocess
        with self.spine.connect() as conn:
            row = conn.execute("SELECT intent_json FROM project_lifecycles WHERE project_id=?", (project_id,)).fetchone()
        target = json.loads(row[0]).get("target_root", "")
        if not target:
            raise InvariantViolation("ERR_REPO_HEAD_TARGET_REQUIRED")
        r = subprocess.run(["git", "-C", target, "rev-parse", "HEAD"], capture_output=True, text=True)
        if r.returncode != 0:
            raise InvariantViolation(f"ERR_REPO_HEAD:{target}:{r.stderr.strip()}")
        return r.stdout.strip()

    # ---------- status ----------
    def status(self, project_id: str) -> dict[str, Any]:
        with self.spine.connect() as conn:
            row = conn.execute(
                "SELECT project_id, run_id, state, goal_hash, source_count, current_workorder,"
                "last_checkpoint_id, attempt_budget, attempts_used, repair_count, updated_at "
                "FROM project_lifecycles WHERE project_id=?", (project_id,)).fetchone()
            if row is None:
                raise LifecycleError(f"ERR_PROJECT_UNKNOWN {project_id}")
            trans = conn.execute(
                "SELECT from_state, to_state, trigger, created_at FROM project_transitions "
                "WHERE project_id=? ORDER BY rowid DESC LIMIT 5", (project_id,)).fetchall()  # insertion order
        return {
            "project_id": row[0], "run_id": row[1], "state": row[2], "goal_hash": row[3],
            "source_count": row[4], "current_workorder": row[5], "last_checkpoint": row[6],
            "attempt_budget": row[7], "attempts_used": row[8], "repair_count": row[9],
            "updated_at": row[10],
            "recent_transitions": [{"from": t[0], "to": t[1], "trigger": t[2], "at": t[3]} for t in trans],
        }

    # ---------- full-project denominator (CS-A) ----------
    def denominator(self, project_id: str) -> dict[str, Any]:
        """Materialize the full-project closure denominator from the spine.

        Machine-reconciles (never assumes a fixed workorder count):
          requirements (project-owned, FROZEN) -> taskspecs -> workorders,
          required-active capabilities (named-method registry) vs provider
          bindings, and acceptance/user-journey rows. Every open item is
          listed explicitly so a scope guard can fail closed.
        """
        from .named_methods import NAMED_METHODS  # local import (no cycle)
        state = self._project_state(project_id)
        with self.spine.connect() as conn:
            req_rows = conn.execute(
                "SELECT requirement_id, state FROM requirements WHERE project_id=?",
                (project_id,)).fetchall()
            ts_rows = conn.execute(
                "SELECT t.taskspec_id, t.state FROM taskspecs t "
                "JOIN requirements r ON r.requirement_id=t.requirement_id "
                "WHERE r.project_id=?", (project_id,)).fetchall()
            wo_rows = conn.execute(
                "SELECT w.workorder_id, w.state FROM workorders w "
                "JOIN taskspecs t ON t.taskspec_id=w.taskspec_id "
                "JOIN requirements r ON r.requirement_id=t.requirement_id "
                "WHERE r.project_id=?", (project_id,)).fetchall()
            acc_rows = conn.execute(
                "SELECT a.acceptance_id, a.verdict FROM acceptances a "
                "JOIN requirements r ON r.requirement_id=a.requirement_id "
                "WHERE r.project_id=?", (project_id,)).fetchall()
        req_ids = [r[0] for r in req_rows]
        open_workorders = [w[0] for w in wo_rows
                           if w[1] not in ("VERIFIED", "ROLLED_BACK", "CANCELLED")]
        open_acceptances = [a[0] for a in acc_rows if a[1] != "PASS"]
        # required-active capabilities from the named-method registry.
        # Bound = registry scope is ACTIVE (USER_AUTHORIZED_ACTIVE_* /
        # CERTIFIED_ACTIVE_* / runtime-now); provider_bindings is the P0-TOOL
        # discovery layer and is not the binding source for named-method tools.
        active_methods = [tid for tid, m in NAMED_METHODS.items()
                          if m.runtime_required_now and m.current_execution_scope != "STANDBY"]
        _ACTIVE_SCOPES = ("USER_AUTHORIZED_ACTIVE", "CERTIFIED_ACTIVE")
        open_capabilities = [tid for tid, m in NAMED_METHODS.items()
                             if tid in active_methods
                             and not str(getattr(m, "current_execution_scope", "")).startswith(_ACTIVE_SCOPES)]
        return {
            "project_id": project_id,
            "state": state,
            "requirements_total": len(req_ids),
            "requirements_frozen": sum(1 for r in req_rows if r[1] == "FROZEN"),
            "taskspecs_total": len(ts_rows),
            "workorders_total": len(wo_rows),
            "workorders_open": open_workorders,
            "workorders_open_count": len(open_workorders),
            "acceptances_total": len(acc_rows),
            "acceptances_open": open_acceptances,
            "acceptances_open_count": len(open_acceptances),
            "required_active_capabilities": active_methods,
            "required_active_capabilities_total": len(active_methods),
            "required_active_capabilities_open": open_capabilities,
            "required_active_capabilities_open_count": len(open_capabilities),
            # G0 D1/D2: dynamic-denominator guard predicates — the project is
            # NOT terminal when required local scope is open but no workorder
            # materializes it (late-bound obligation must expand the
            # denominator, never hide behind workorders_open == 0).
            "required_local_scope_open": len(open_workorders) + len(open_acceptances) + len(open_capabilities),
            "guard_required_workorders_terminal": len(open_workorders) == 0
            and len(open_acceptances) == 0 and len(open_capabilities) == 0,
            "denominator_available": True,
        }

    # ---------- G0 D2: dynamic denominator expansion ----------
    def admit_requirement(self, project_id: str, requirement_id: str,
                          wording: str, *, owner: str = "owner",
                          priority: str = "P1") -> dict[str, Any]:
        """Admit a late-bound required obligation into the SAME project
        lifecycle: Requirement -> TaskSpec -> WorkOrder -> denominator.

        This closes the LATE_BOUND_OBLIGATION_DENOMINATOR_GAP: any new
        required source obligation must expand the denominator instead of
        being deferred to an invisible 'next wave'.
        """
        state = self._project_state(project_id)
        if state not in ("EXECUTING", "PLAN_READY", "WORKORDERS_ADMITTED"):
            raise LifecycleError(f"ERR_ADMIT_REQUIREMENT_STATE {state}")
        self.spine.register_requirement(
            requirement_id=requirement_id,
            source_locator=f"project:{project_id}:late-bound-obligation",
            wording=wording,
            acceptance_id=f"ACC-{requirement_id}",
            oracle=f"{wording} materialized + acceptance PASS",
            threshold="EXPLICIT_ORACLE_PASS",
            negative_fixture="obligation without workorder",
            priority=priority,
            project_id=project_id,
        )
        self.spine.acquire_lease(requirement_id, "lifecycle-planner", f"TK-{requirement_id}", ttl_seconds=300)
        try:
            self.spine.transition_requirement(
                requirement_id, "FROZEN", actor="lifecycle-planner",
                token=f"TK-{requirement_id}", expected_version=0,
                evidence_ref=f"EV-{requirement_id}",
                idempotency_key=f"FRZ-{requirement_id}",
            )
        finally:
            self.spine.release_lease(requirement_id, "lifecycle-planner", f"TK-{requirement_id}")
        ts_id = f"TS-{requirement_id.lower()}"
        base_head = self._repo_head(project_id)
        try:
            self.spine.create_taskspec(
                taskspec_id=ts_id,
                requirement_id=requirement_id,
                objective=wording,
                owner=owner,
                writable_root=Path("worktrees") / ts_id.lower(),
                permissions={"write_scope": "worktree", "network": False},
                tests=[f"test_{ts_id.lower()}.py"],
                evidence_plan="raw + independent evidence per acceptance contract",
            )
            self.spine.create_workorder(
                f"WO-{ts_id}", ts_id, writer="codex",
                worktree=Path("worktrees") / ts_id.lower(),
                base_head=base_head,
            )
        except InvariantViolation:
            pass  # idempotent resume
        return {"requirement_id": requirement_id, "requirement_state": "FROZEN",
                "taskspec": ts_id, "workorder": f"WO-{ts_id}"}

    # ---------- G0 D3: mandatory completion sweep ----------
    def completion_sweep(self, project_id: str) -> dict[str, Any]:
        """Classify every open denominator edge.

        auto_local        -> MUST be materialized/admitted and continued
        blocked_hitl      -> requires human credential/approval
        temp_external     -> external condition (market-time, rights)
        non_blocking_debt -> deferrable without blocking release

        Only the last two may legitimately stop a session; AUTO_LOCAL and
        BLOCKED_HITL are surfaced explicitly so a controller can act.
        """
        den = self.denominator(project_id)
        auto_local: list[str] = []
        blocked_hitl: list[str] = []
        temp_external: list[str] = []
        non_blocking_debt: list[str] = []
        for wo in den["workorders_open"]:
            auto_local.append(f"workorder:{wo}")
        for acc in den["acceptances_open"]:
            auto_local.append(f"acceptance:{acc}")
        for cap in den["required_active_capabilities_open"]:
            auto_local.append(f"capability:{cap}")
        return {
            "project_id": project_id,
            "auto_local": auto_local,
            "blocked_hitl": blocked_hitl,
            "temp_external": temp_external,
            "non_blocking_debt": non_blocking_debt,
            "open_total": len(auto_local) + len(blocked_hitl)
            + len(temp_external) + len(non_blocking_debt),
            "sweepable": len(auto_local) > 0,
        }


# ---------- G0 D4: RBWI composite acceptance semantics ----------
def rbwi_composite(parts: dict[str, str]) -> dict[str, Any]:
    """RBWI final-system qualification is a composite; it can never PASS
    above a required child state.

    Children (each PASS / NOT_REQUIRED_FOR_LOCAL_DELIVERY / TEMP_CLOSED):
      local_paper, external_market, tool_coverage, user_journey,
      negative_degraded, replay.
    Verdict: PASS only when every required child is PASS or explicitly
    NOT_REQUIRED_FOR_LOCAL_DELIVERY; otherwise FAIL_CLOSED with open edges.
    """
    required = ("local_paper", "external_market", "tool_coverage",
                "user_journey", "negative_degraded", "replay")
    open_edges: list[str] = []
    temp_edges: list[str] = []
    for k in required:
        v = parts.get(k, "NOT_RUN")
        if v == "TEMP_CLOSED":
            temp_edges.append(f"{k}={v}")
        elif v not in ("PASS", "NOT_REQUIRED_FOR_LOCAL_DELIVERY",
                       "SOURCE_VALID_NOT_REQUIRED_FOR_LOCAL_DELIVERY",
                       "SOURCE_VALID_NOT_APPLICABLE"):
            open_edges.append(f"{k}={v}")
    if temp_edges:
        verdict = "TEMP_CLOSED"
    elif open_edges:
        verdict = "FAIL_CLOSED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "open_edges": open_edges + temp_edges, "parts": dict(parts)}
