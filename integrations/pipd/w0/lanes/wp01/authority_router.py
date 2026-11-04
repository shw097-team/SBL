#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-01 — 權威分流器 (authority_router).

把 R4C 來源根內的 31 個來源、Oracle96、Seam5、Repo 路由（repository-map /
ORIGINAL_READER_SOURCE_PINS）、以及本輪作者產物，逐筆分到固定五類
CANONICAL_ORIGINAL / GOVERNANCE_MIRROR / SKILL_SIDECAR / HISTORICAL_ARCHIVED /
AUTHOR_CANDIDATE，並對衝突與缺 Scope 產生具名 typed HOLD。

硬性設計約束（違反即中止，不寫半份輸出）:
  1. may_mint_permit 恆為 False；任何一筆為 True 就 raise（不序列化）。
  2. 每一筆都必須帶 evidence_field，且該欄位所指的檔案必須是本次實際載入的
     輸入檔；指不到就 raise —— 不准出現憑空引用。
  3. Mirror / Skill / Archived / Author 產物不得被任何規則升格為 CANONICAL。
     分類只會往下修（downgrade），不會往上修。
  4. may_authorize_write 需要「顯式」授寫宣告（write_authority 在授權詞彙內）
     且 effect_permission 已宣告且非 NONE，且無任何 HOLD 阻擋。缺宣告 → False。

用法:
  python authority_router.py --source-root <R4C dir> --out <dir> [--readback-root <dir>]

退出碼: 0 完成（含產生 HOLD）；2 輸入缺失/不可解析；3 不變量違反。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

SCHEMA = "FHS_W0_IMPL/AUTHORITY_ROUTING/v1"
TOOL_VERSION = "wp01-authority-router/1.0.0"

CLASSES = (
    "CANONICAL_ORIGINAL",
    "GOVERNANCE_MIRROR",
    "SKILL_SIDECAR",
    "HISTORICAL_ARCHIVED",
    "AUTHOR_CANDIDATE",
)

GROUP_ORDER = (
    "SOURCE31",
    "ORACLE96",
    "SEAM5",
    "REPO_PINS",
    "REPO_MAP",
    "AUTHOR_ROUND",
    "SKILL_PLUGIN",
)

# ---------------------------------------------------------------- reason codes
C_MIRROR_NOT_WRITABLE = "AUTHORITY_MIRROR_NOT_WRITABLE"
C_EFFECT_NONE = "AUTHORITY_EFFECT_PERMISSION_NONE"
C_HISTORICAL = "HISTORICAL_ARCHIVED_NOT_CANONICAL"
C_SKILL_PERMIT = "SKILL_NOT_PERMIT"
C_SKILL_SIDECAR = "SKILL_SIDECAR_NOT_COMPILER"
C_DUAL_CANONICAL = "AUTHORITY_CONFLICT_DUAL_CANONICAL"
C_SCOPE_UNBOUND = "AUTHORITY_SCOPE_UNBOUND"
C_PROFILE_ROLE = "PROFILE_ROLE_CONFLATED"
C_MIRROR_IDENTITY = "AUTHORITY_MIRROR_IDENTITY_UNVERIFIED"
C_COMPILER_NOT_RUN = "CANONICAL_COMPILER_NOT_RUN"
C_CURRENTNESS = "ORIGINAL_READER_CURRENTNESS_UNVERIFIED"

P_DOC31 = "CANONICAL_ORIGINAL_READER_DOC_READ_ONLY"
P_SBL_SRC = "CANONICAL_ORIGINAL_SBL_DOMAIN_SOURCE_READ_ONLY"
P_NAV = "GOVERNANCE_MIRROR_NAVIGATION_ONLY"
P_FABRIC_HOSTED = "GOVERNANCE_MIRROR_FABRIC_HOSTED_NON_AUTHORITATIVE"
P_AGENT_DOC = "SKILL_SIDECAR_AGENT_INSTRUCTIONS"
P_ORACLE = "AUTHOR_CANDIDATE_NATIVE_NOT_RUN"
P_SEAM = "AUTHOR_CANDIDATE_READER_ACK_HOLD"
P_AUTHOR = "AUTHOR_CANDIDATE_AUTHOR_DESIGN_ONLY"

RULEBOOK = (
    (
        "R1",
        "effect_permission=NONE → may_authorize_write=false；GOVERNANCE_MIRROR 一律不可授寫"
        "（evidence: repository-map.json:$.effect_permission）",
        C_MIRROR_NOT_WRITABLE,
    ),
    (
        "R2",
        "archived=true 或 write_authority=NONE → HISTORICAL_ARCHIVED，且不得為 canonical"
        "（evidence: repository-map.json:$.historical_repositories.*）",
        C_HISTORICAL,
    ),
    (
        "R3",
        "Skill/Sidecar 不得作為 Canonical Compiler 或 Checker（evidence: "
        "PLUGIN_USAGE_AND_GHP01.json:$.canonical_compiler / $.host_loaded）",
        C_SKILL_PERMIT,
    ),
    (
        "R4",
        "同一 canonical_key（subject_id#artifact_key）出現兩個 CANONICAL_ORIGINAL → HOLD",
        C_DUAL_CANONICAL,
    ),
    (
        "R5",
        "缺 subject/scope 綁定，或 subject_ref 與當前 candidate body 不符 → HOLD"
        "（evidence: SBL AuthorityBinding.schema.json requires subject_id minLength 8）",
        C_SCOPE_UNBOUND,
    ),
    (
        "R6",
        "Profile 與 Role 與 Worker 不可互換（evidence: "
        "SBL ProfileBinding.schema.json:$.properties.profile.enum = LITE|STANDARD|ASSURED，"
        "非 role/worker 識別）",
        C_PROFILE_ROLE,
    ),
    (
        "R7",
        "Mirror 讀回的 git blob sha1 與 REPOS_RECHECK 記錄的 ref blob 不符 → HOLD"
        "（bytes ≠ blob ⇒ 授權欄位出處不可證）",
        C_MIRROR_IDENTITY,
    ),
    (
        "R8",
        "canonical_compiler=NOT_RUN 或 host_loaded=NOT_OBSERVED → HOLD"
        "（本輪無 canonical 編譯收據）",
        C_COMPILER_NOT_RUN,
    ),
    (
        "R9",
        "SOURCE31 每筆 currentness=ORIGINAL_READER_CURRENTNESS_HOLD → 聚合 HOLD"
        "（檔案身份通過 ≠ 原 Reader 當期性已確認）",
        C_CURRENTNESS,
    ),
)

WRITE_GRANT_VALUES = {"GRANTED", "WRITE", "FULL", "AUTHORIZED", "PREAUTHORIZED"}
SKILL_KINDS = {"SKILL", "SIDECAR"}
COMPILER_ROLE_CLAIMS = {"CANONICAL_COMPILER", "COMPILER", "CHECKER", "PROTECTED_CHECKER"}
UNBOUND_VALUES = {"", "UNBOUND", "NONE_UNBOUND", "ORIGINAL_UNBOUND", "UNKNOWN"}
EPSILON_TZ = timezone(timedelta(hours=8))

# reason-code priority: a higher number wins when several rules fire on one row
REASON_PRIORITY = {
    P_DOC31: 0,
    P_SBL_SRC: 0,
    P_NAV: 0,
    P_FABRIC_HOSTED: 0,
    P_AGENT_DOC: 0,
    P_ORACLE: 0,
    P_SEAM: 0,
    P_AUTHOR: 0,
    C_EFFECT_NONE: 10,
    C_MIRROR_NOT_WRITABLE: 10,
    C_SKILL_SIDECAR: 20,
    C_SKILL_PERMIT: 25,
    C_HISTORICAL: 30,
    C_DUAL_CANONICAL: 40,
    C_SCOPE_UNBOUND: 50,
    C_PROFILE_ROLE: 60,
}

HOLD_TAGS = {
    C_DUAL_CANONICAL: "DUAL-CANON",
    C_SCOPE_UNBOUND: "SCOPE",
    C_PROFILE_ROLE: "PROFILE-ROLE",
    C_SKILL_PERMIT: "SKILL-PERMIT",
    C_MIRROR_IDENTITY: "MIRROR-ID",
    C_COMPILER_NOT_RUN: "COMPILER",
    C_CURRENTNESS: "CURRENTNESS",
}


class RouterError(RuntimeError):
    """Input or invariant failure — aborts before any output is written."""


# ------------------------------------------------------------------- utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def unbound(value) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return value.strip().upper() in UNBOUND_VALUES


def short(value, limit=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


# --------------------------------------------------------------------- routing
class AuthorityRouter:
    def __init__(self, source_root, out_dir, readback_root=None):
        self.source_root = os.path.abspath(source_root)
        self.out_dir = os.path.abspath(out_dir)
        self.readback_root = os.path.abspath(readback_root) if readback_root else None
        if not os.path.isdir(self.source_root):
            raise RouterError("source root not a directory: %s" % self.source_root)

        self.loaded = {}       # file_key -> {"path","sha256","bytes","origin"}
        self.absent = []       # declared-but-absent inputs
        self.hints = []        # route hints, pre-rule
        self.entries = []      # classified rows
        self.holds = []
        self.checks = {}       # named verifications (mirror identity, sha checks)
        self.current_candidate_sha = None
        self.source31_declared = 0

    # -- input loading -------------------------------------------------
    def _register(self, file_key, path, origin="source_root"):
        info = {
            "path": path,
            "origin": origin,
            "present": os.path.isfile(path),
            "sha256": None,
            "bytes": None,
        }
        if info["present"]:
            with open(path, "rb") as fh:
                raw = fh.read()
            info["sha256"] = hashlib.sha256(raw).hexdigest()
            info["bytes"] = len(raw)
            info["git_blob_sha1"] = git_blob_sha1(raw)
        self.loaded[file_key] = info
        return info["present"]

    def _load_json(self, file_key, path, origin="source_root", required=False):
        if not self._register(file_key, path, origin):
            if required:
                raise RouterError("required input missing: %s (%s)" % (file_key, path))
            self.absent.append({"file": file_key, "path": path, "origin": origin})
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError) as exc:
            raise RouterError("cannot parse %s: %s" % (path, exc))

    def load(self):
        root = self.source_root
        self.src31 = self._load_json(
            "SOURCE31_PHYSICAL_IDENTITY.json",
            os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"),
            required=True,
        )
        if not isinstance(self.src31, list) or not self.src31:
            raise RouterError("SOURCE31_PHYSICAL_IDENTITY.json must be a non-empty list")
        self.source31_declared = len(self.src31)

        self.oracle = self._load_json(
            "ORACLE96_CONTRACTS.json", os.path.join(root, "ORACLE96_CONTRACTS.json")
        )
        self.seam = self._load_json("SEAM_CONTRACTS.json", os.path.join(root, "SEAM_CONTRACTS.json"))
        self.pins = self._load_json(
            "ORIGINAL_READER_SOURCE_PINS.json", os.path.join(root, "ORIGINAL_READER_SOURCE_PINS.json")
        )
        self.plugin = self._load_json(
            "PLUGIN_USAGE_AND_GHP01.json", os.path.join(root, "PLUGIN_USAGE_AND_GHP01.json")
        )
        self.candidate_state = self._load_json(
            "CURRENT_CANDIDATE_STATE.json", os.path.join(root, "CURRENT_CANDIDATE_STATE.json")
        )
        self.additional_holds = self._load_json(
            "ADDITIONAL_SCOPED_HOLDS_r4c.json", os.path.join(root, "ADDITIONAL_SCOPED_HOLDS_r4c.json")
        )
        self.dag = self._load_json(
            "PROGRAM_WP22_DAG36.json", os.path.join(root, "PROGRAM_WP22_DAG36.json")
        )
        self.tech485 = self._load_json(
            "TECH485_COMPACT_REGISTRY.json", os.path.join(root, "TECH485_COMPACT_REGISTRY.json")
        )
        self.supplemental = self._load_json(
            "SOURCE_IDENTITY_SUPPLEMENTAL_RAW.json",
            os.path.join(root, "SOURCE_IDENTITY_SUPPLEMENTAL_RAW.json"),
        )
        self.repos_recheck = self._load_json(
            "REPOS_RECHECK.json", os.path.join(root, "REPOS_RECHECK.json")
        )

        # manifest: filename carries the candidate version; pick deterministically
        manifest_key = None
        for name in sorted(os.listdir(root)):
            if name.startswith("INDEX_AND_MANIFEST") and name.endswith(".json"):
                manifest_key = name
                break
        self.manifest = None
        if manifest_key:
            self.manifest = self._load_json(manifest_key, os.path.join(root, manifest_key))

        # the NAV mirror is not on disk in the source root; it lives in the round readback
        repomap_root = os.path.join(root, "repository-map.json")
        if os.path.isfile(repomap_root):
            self.repomap = self._load_json("repository-map.json", repomap_root)
            self.repomap_key = "repository-map.json"
        elif self.readback_root and os.path.isfile(
            os.path.join(self.readback_root, "fabric_repository-map.json")
        ):
            self.repomap = self._load_json(
                "fabric_repository-map.json",
                os.path.join(self.readback_root, "fabric_repository-map.json"),
                origin="readback_root",
            )
            self.repomap_key = "fabric_repository-map.json"
        else:
            self.repomap = None
            self.repomap_key = None
            self.absent.append(
                {"file": "repository-map.json", "path": repomap_root, "origin": "source_root"}
            )

        if isinstance(self.candidate_state, dict):
            self.current_candidate_sha = self.candidate_state.get("candidate_body_sha256")

        # optional: candidate body / annex declared by the manifest
        self.body_path = None
        self.annex_path = None
        if isinstance(self.manifest, dict):
            body = (self.manifest.get("candidate_body") or {}).get("path")
            annex = (self.manifest.get("annex") or {}).get("path")
            if body:
                self.body_path = os.path.join(root, body)
            if annex:
                self.annex_path = os.path.join(root, annex)
        return self

    # -- evidence helper ------------------------------------------------
    def _ev(self, file_key, path, value):
        """Return (evidence_field, evidence_value) with an auditable JSON path."""
        field = "%s:$%s" % (file_key, path)
        return field, short(value)

    # -- route hints ----------------------------------------------------
    def build_hints(self):
        self._hints_source31()
        self._hints_oracle()
        self._hints_seam()
        self._hints_pins()
        self._hints_repomap()
        self._hints_author_round()
        self._hints_plugin()
        return self

    def _hint(self, group, source_id, path, evidence_field, evidence_value, hint_class,
              declared=None, subject_id=None, scope_id=None, artifact_key=None,
              canonical_key=None, evidence_support=None, notes=None):
        self.hints.append(
            {
                "group": group,
                "source_id": source_id,
                "path": path,
                "evidence_field": evidence_field,
                "evidence_value": evidence_value,
                "evidence_support": evidence_support or [],
                "hint_class": hint_class,
                "declared": declared or {},
                "subject_id": subject_id,
                "scope_id": scope_id,
                "artifact_key": artifact_key,
                "canonical_key": canonical_key,
                "notes": notes or [],
            }
        )

    GROUP_SCOPE31 = "SBL-FHS-PIPD-LS-PKG-CORPUS"

    def _hints_source31(self):
        for idx, row in enumerate(self.src31):
            sid = row.get("source_id") or "SOURCE31[%d]" % idx
            declared = {
                "effect_permission": row.get("effect_permission"),
                "write_authority": row.get("write_authority"),
                "archived": row.get("archived"),
                "artifact_kind": row.get("artifact_kind", "ORIGINAL_DOCUMENT"),
                "runtime_binding": None,
                "role_claim": row.get("role_claim"),
                "actor_binding": row.get("actor_binding"),
            }
            ev_field, ev_value = self._ev(
                "SOURCE31_PHYSICAL_IDENTITY.json", "[%d].physical_identity" % idx,
                row.get("physical_identity"),
            )
            support = [
                "%s:$[%d].currentness=%s" % ("SOURCE31_PHYSICAL_IDENTITY.json", idx,
                                             row.get("currentness")),
                "%s:$[%d].sha256=%s" % ("SOURCE31_PHYSICAL_IDENTITY.json", idx, row.get("sha256")),
            ]
            self._hint(
                "SOURCE31", sid, row.get("path"), ev_field, ev_value,
                row.get("authority_hint", "CANONICAL_ORIGINAL"),
                declared=declared,
                subject_id=row.get("subject_id", sid),
                scope_id=row.get("scope_id", self.GROUP_SCOPE31),
                artifact_key=row.get("artifact_key", "ORIGINAL_DOCUMENT"),
                canonical_key=row.get("canonical_key"),
                evidence_support=support,
            )

    def _hints_oracle(self):
        for idx, row in enumerate(self.oracle or []):
            cid = row.get("case_id") or "ORACLE96[%d]" % idx
            declared = {
                "artifact_kind": "AUTHOR_FIXTURE",
                "host": row.get("host"),
                "runner_binding": row.get("runner_binding"),
                "raw_schema": row.get("raw_schema"),
            }
            ev_field, ev_value = self._ev(
                "ORACLE96_CONTRACTS.json", "[%d].state" % idx, row.get("state")
            )
            self._hint(
                "ORACLE96", "ORACLE96:" + cid, "ORACLE96_CONTRACTS.json[%d]" % idx,
                ev_field, ev_value, "AUTHOR_CANDIDATE",
                declared=declared,
                subject_id=row.get("source_parent"),
                scope_id=row.get("scope"),
                artifact_key="ORACLE_CASE",
                evidence_support=[
                    "ORACLE96_CONTRACTS.json:$[%d].scope=%s" % (idx, row.get("scope")),
                    "ORACLE96_CONTRACTS.json:$[%d].source_parent=%s" % (idx, row.get("source_parent")),
                ],
            )

    def _hints_seam(self):
        for idx, row in enumerate(self.seam or []):
            seam = row.get("seam") or "SEAM[%d]" % idx
            ev_field, ev_value = self._ev(
                "SEAM_CONTRACTS.json", "[%d].state" % idx, row.get("state")
            )
            self._hint(
                "SEAM5", "SEAM:" + seam, row.get("input_fixture") or "SEAM_CONTRACTS.json[%d]" % idx,
                ev_field, ev_value, "AUTHOR_CANDIDATE",
                declared={
                    "artifact_kind": "AUTHOR_FIXTURE",
                    "host": row.get("host"),
                    "original_abi": row.get("original_abi"),
                },
                subject_id=row.get("subject_id"),
                scope_id=row.get("claim_ceiling"),
                artifact_key="SEAM_CONTRACT",
                evidence_support=[
                    "SEAM_CONTRACTS.json:$[%d].claim_ceiling=%s" % (idx, row.get("claim_ceiling")),
                    "SEAM_CONTRACTS.json:$[%d].original_reader=%s" % (idx, row.get("original_reader")),
                ],
            )

    PIN_ROLE_RULES = (
        ("Fabric:INTEGRATION/FHS/", "GOVERNANCE_MIRROR", P_NAV, "FHS_NAV_INDEX"),
        ("Fabric:INTEGRATION/SOURCE-PROJECTION.md", "GOVERNANCE_MIRROR", P_NAV, "FHS_NAV_INDEX"),
        ("Fabric:FABRIC/", "GOVERNANCE_MIRROR", P_FABRIC_HOSTED, "FABRIC_HOSTED_SOURCE"),
        ("SBL:integrations/pipd/", "CANONICAL_ORIGINAL", P_SBL_SRC, "SBL_PIPD_DOMAIN_SOURCE"),
        ("SBL:docs/pipd-migration/", "GOVERNANCE_MIRROR", P_NAV, "SBL_MIGRATION_DOC"),
        ("SBL:AGENTS.md", "SKILL_SIDECAR", P_AGENT_DOC, "AGENT_INSTRUCTION_SIDECAR"),
        ("HG-KSEOS:AGENTS.md", "SKILL_SIDECAR", P_AGENT_DOC, "AGENT_INSTRUCTION_SIDECAR"),
        ("HG-KSEOS:", "GOVERNANCE_MIRROR", P_FABRIC_HOSTED, "HGK_NATIVE_CONTROL_SOURCE"),
    )

    def _pin_rule(self, key):
        for prefix, cls, reason, artifact_key in self.PIN_ROLE_RULES:
            if key == prefix or key.startswith(prefix):
                return cls, reason, artifact_key
        return "GOVERNANCE_MIRROR", P_NAV, "UNCLASSIFIED_PIN"

    def _hints_pins(self):
        for idx, (key, row) in enumerate((self.pins or {}).items()):
            cls, reason, artifact_key = self._pin_rule(key)
            offline = row.get("offline_path")
            verified = None
            if offline:
                candidate = os.path.join(self.source_root, offline)
                if os.path.isfile(candidate):
                    verified = sha256_file(candidate) == row.get("sha256")
            ev_field, ev_value = self._ev(
                "ORIGINAL_READER_SOURCE_PINS.json", "[\"%s\"].sha256" % key, row.get("sha256")
            )
            hint = {
                "group": "REPO_PINS",
                "source_id": "PIN:" + key,
                "path": offline or key,
                "evidence_field": ev_field,
                "evidence_value": ev_value,
                "evidence_support": [
                    "ORIGINAL_READER_SOURCE_PINS.json:$[\"%s\"].runtime_binding=%s"
                    % (key, row.get("runtime_binding")),
                    "ORIGINAL_READER_SOURCE_PINS.json:$[\"%s\"].repo=%s" % (key, row.get("repo")),
                ],
                "hint_class": cls,
                "declared": {
                    "runtime_binding": row.get("runtime_binding"),
                    "artifact_kind": "REPO_FILE",
                    "pin_sha256_verified": verified,
                    "role_claim": None,
                },
                "subject_id": key,
                "scope_id": row.get("repo"),
                "artifact_key": artifact_key,
                "canonical_key": key if cls == "CANONICAL_ORIGINAL" else None,
                "notes": ["pin sha256 on disk: %s" % ("MATCH" if verified else ("MISMATCH" if verified is False else "FILE_ABSENT"))],
                "_reason": reason,
            }
            hint["_pin_reason"] = reason
            self.hints.append(hint)
        return

    def _hints_repomap(self):
        if not isinstance(self.repomap, dict):
            return
        key = self.repomap_key
        identity = self.repomap.get("identity")
        effect = self.repomap.get("effect_permission")
        ev_field, ev_value = self._ev(key, ".identity", identity)
        self._hint(
            "REPO_MAP", "GOV:NAV-REPOMAP", key, ev_field, ev_value, "GOVERNANCE_MIRROR",
            declared={
                "identity": identity,
                "effect_permission": effect,
                "artifact_kind": "GOVERNANCE_INDEX",
                "write_authority": self.repomap.get("write_authority"),
                "schema_version": self.repomap.get("schema_version"),
            },
            subject_id="FHS-NAV/repository-map",
            scope_id=self.repomap.get("schema_version"),
            artifact_key="FHS_NAV_INDEX",
            evidence_support=[
                "%s:$.effect_permission=%s" % (key, effect),
                "%s:$.schema_version=%s" % (key, self.repomap.get("schema_version")),
            ],
        )
        for idx, route in enumerate(self.repomap.get("routes") or []):
            tc = route.get("task_class") or "route[%d]" % idx
            ev_field, ev_value = self._ev(key, ".routes[%d].claim" % idx, route.get("claim"))
            self._hint(
                "REPO_MAP", "GOV:ROUTE:" + tc, key, ev_field, ev_value, "GOVERNANCE_MIRROR",
                declared={
                    "effect_permission": effect,
                    "artifact_kind": "GOVERNANCE_INDEX",
                    "write_authority": route.get("write_authority", self.repomap.get("write_authority")),
                    "claim": route.get("claim"),
                },
                subject_id="FHS-NAV/route/" + tc,
                scope_id=route.get("primary_repo") or "cross_repo",
                artifact_key="NAV_ROUTE",
                evidence_support=["%s:$.routes[%d].task_class=%s" % (key, idx, tc)],
            )
        for name, repo in (self.repomap.get("repositories") or {}).items():
            ev_field, ev_value = self._ev(key, ".repositories.%s.domain" % name, repo.get("domain"))
            self._hint(
                "REPO_MAP", "GOV:REPO:" + name, key, ev_field, ev_value, "GOVERNANCE_MIRROR",
                declared={
                    "effect_permission": effect,
                    "artifact_kind": "GOVERNANCE_INDEX",
                    "write_authority": self.repomap.get("write_authority"),
                },
                subject_id="repo:" + str(repo.get("full_name")),
                scope_id=repo.get("domain"),
                artifact_key="NAV_REPO_ENTRY",
                evidence_support=["%s:$.repositories.%s.full_name=%s" % (key, name, repo.get("full_name"))],
            )
        for name, repo in (self.repomap.get("historical_repositories") or {}).items():
            ev_field, ev_value = self._ev(
                key, ".historical_repositories.%s.archived" % name, repo.get("archived")
            )
            self._hint(
                "REPO_MAP", "HIST:" + str(repo.get("full_name") or name), key, ev_field, ev_value,
                "HISTORICAL_ARCHIVED",
                declared={
                    "archived": repo.get("archived"),
                    "write_authority": repo.get("write_authority"),
                    "effect_permission": effect,
                    "artifact_kind": "REPO_HISTORICAL",
                    "role": repo.get("role"),
                },
                subject_id="repo:" + str(repo.get("full_name") or name),
                scope_id=repo.get("role"),
                artifact_key="HISTORICAL_REPO",
                evidence_support=[
                    "%s:$.historical_repositories.%s.write_authority=%s"
                    % (key, name, repo.get("write_authority")),
                    "%s:$.historical_repositories.%s.role=%s" % (key, name, repo.get("role")),
                ],
            )

    def _hints_author_round(self):
        state = self.candidate_state or {}
        cid = state.get("candidate_id") or "FHS-W0-CANDIDATE"
        scope = state.get("claim_ceiling")

        def author_hint(sid, path, file_key, jpath, value, support, subject=None,
                        subject_ref=None, artifact_key="AUTHOR_ARTIFACT"):
            ev_field, ev_value = self._ev(file_key, jpath, value)
            self._hint(
                "AUTHOR_ROUND", sid, path, ev_field, ev_value, "AUTHOR_CANDIDATE",
                declared={
                    "artifact_kind": "AUTHOR_ARTIFACT",
                    "subject_ref": subject_ref,
                    "claim_ceiling": scope,
                },
                subject_id=subject or cid,
                scope_id=scope,
                artifact_key=artifact_key,
                evidence_support=support,
            )

        if isinstance(self.manifest, dict):
            body = self.manifest.get("candidate_body") or {}
            if body.get("path"):
                author_hint(
                    "AUTH:CANDIDATE-BODY", body.get("path"), "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json",
                    ".candidate_body.sha256", body.get("sha256"),
                    ["%s:$.candidate_body.bytes=%s" % ("INDEX_AND_MANIFEST_r4-candidate-b41d2e.json", body.get("bytes")),
                     "%s:$.claim_ceiling=%s" % ("INDEX_AND_MANIFEST_r4-candidate-b41d2e.json", self.manifest.get("claim_ceiling"))],
                    subject_ref=body.get("sha256"), artifact_key="CANDIDATE_BODY",
                )
            annex = self.manifest.get("annex") or {}
            if annex.get("path"):
                author_hint(
                    "AUTH:CANDIDATE-ANNEX", annex.get("path"),
                    "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json", ".annex.sha256", annex.get("sha256"),
                    ["%s:$.annex.paired_body_sha256=%s" % ("INDEX_AND_MANIFEST_r4-candidate-b41d2e.json",
                                                           annex.get("paired_body_sha256"))],
                    subject_ref=annex.get("paired_body_sha256"), artifact_key="CANDIDATE_ANNEX",
                )
            author_hint(
                "AUTH:INDEX-MANIFEST", "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json",
                "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json", ".artifact_id",
                self.manifest.get("artifact_id"),
                ["%s:$.currency=%s" % ("INDEX_AND_MANIFEST_r4-candidate-b41d2e.json",
                                        self.manifest.get("currency"))],
                subject_ref=body.get("sha256"), artifact_key="CANDIDATE_MANIFEST",
            )
        if isinstance(self.candidate_state, dict):
            author_hint(
                "AUTH:CURRENT-CANDIDATE-STATE", "CURRENT_CANDIDATE_STATE.json",
                "CURRENT_CANDIDATE_STATE.json", ".candidate_id", cid,
                ["CURRENT_CANDIDATE_STATE.json:$.candidate_body_sha256=%s" % state.get("candidate_body_sha256"),
                 "CURRENT_CANDIDATE_STATE.json:$.currency=%s" % state.get("currency")],
                subject_ref=state.get("candidate_body_sha256"), artifact_key="CANDIDATE_STATE",
            )
        if isinstance(self.additional_holds, dict):
            # this artifact binds a candidate body sha; R5 compares it to the current one
            author_hint(
                "AUTH:ADDITIONAL-SCOPED-HOLDS", "ADDITIONAL_SCOPED_HOLDS_r4c.json",
                "ADDITIONAL_SCOPED_HOLDS_r4c.json", ".candidate_body_sha256",
                self.additional_holds.get("candidate_body_sha256"),
                ["ADDITIONAL_SCOPED_HOLDS_r4c.json:$.count=%s" % self.additional_holds.get("count")],
                subject_ref=self.additional_holds.get("candidate_body_sha256"),
                artifact_key="AUTHOR_HOLDS_FILE",
            )
        if isinstance(self.dag, dict):
            wps = self.dag.get("work_packages") or []
            author_hint(
                "AUTH:PROGRAM-DAG", "PROGRAM_WP22_DAG36.json", "PROGRAM_WP22_DAG36.json",
                ".work_packages[0].id", (wps[0] or {}).get("id") if wps else None,
                ["PROGRAM_WP22_DAG36.json:$.work_packages.length=%d" % len(wps)],
                artifact_key="PROGRAM_DAG",
            )
        if isinstance(self.tech485, list):
            author_hint(
                "AUTH:TECH485-REGISTRY", "TECH485_COMPACT_REGISTRY.json", "TECH485_COMPACT_REGISTRY.json",
                "[0].original_id", (self.tech485[0] or {}).get("original_id") if self.tech485 else None,
                ["TECH485_COMPACT_REGISTRY.json:$length=%d" % len(self.tech485)],
                artifact_key="TECH_REGISTRY",
            )
        if isinstance(self.supplemental, list):
            author_hint(
                "AUTH:SOURCE-IDENTITY-SUPPLEMENTAL", "SOURCE_IDENTITY_SUPPLEMENTAL_RAW.json",
                "SOURCE_IDENTITY_SUPPLEMENTAL_RAW.json", "[0].claim_ceiling",
                (self.supplemental[0] or {}).get("claim_ceiling") if self.supplemental else None,
                ["SOURCE_IDENTITY_SUPPLEMENTAL_RAW.json:$length=%d" % len(self.supplemental)],
                artifact_key="SOURCE_IDENTITY_CHECKS",
            )
        if isinstance(self.oracle, list) or isinstance(self.seam, list):
            pass  # already routed as their own groups

    def _hints_plugin(self):
        if not isinstance(self.plugin, dict):
            return
        ev_field, ev_value = self._ev(
            "PLUGIN_USAGE_AND_GHP01.json", ".canonical_compiler", self.plugin.get("canonical_compiler")
        )
        self._hint(
            "SKILL_PLUGIN", "SKILL:" + str(self.plugin.get("plugin")), self.plugin.get("installed_path"),
            ev_field, ev_value, "SKILL_SIDECAR",
            declared={
                "artifact_kind": "SKILL",
                "canonical_compiler": self.plugin.get("canonical_compiler"),
                "host_loaded": self.plugin.get("host_loaded"),
                "role_claim": self.plugin.get("role_claim"),
                "write_authority": self.plugin.get("write_authority"),
                "effect_permission": self.plugin.get("effect_permission"),
            },
            subject_id="plugin:" + str(self.plugin.get("plugin")),
            scope_id="SKILL_SIDECAR",
            artifact_key="SKILL_PLUGIN",
            evidence_support=[
                "PLUGIN_USAGE_AND_GHP01.json:$.host_loaded=%s" % self.plugin.get("host_loaded"),
                "PLUGIN_USAGE_AND_GHP01.json:$.states.SELECTED=%s"
                % ((self.plugin.get("states") or {}).get("SELECTED")),
            ],
        )

    # -- rule engine ----------------------------------------------------
    def classify(self):
        for hint in self.hints:
            self.entries.append(self._classify_one(hint))
        self._rule_r4_dual_canonical()
        self._check_mirror_identity()
        self._check_compiler_receipt()
        self._check_source31_currentness()
        self._finalise()
        return self

    def _classify_one(self, hint):
        declared = dict(hint["declared"])
        cls = hint["hint_class"]
        if cls not in CLASSES:
            raise RouterError("unknown hint class %r for %s" % (cls, hint["source_id"]))
        trace = []
        blockers = []
        reason = hint.get("_pin_reason") or self._positive_reason(cls, hint)
        best = [reason, REASON_PRIORITY.get(reason, 0)]

        def offer(code):
            prio = REASON_PRIORITY.get(code, 0)
            if prio >= best[1]:
                best[0] = code
                best[1] = prio

        archived = declared.get("archived")
        write_authority = declared.get("write_authority")
        effect = declared.get("effect_permission")
        kind = (declared.get("artifact_kind") or "").upper()

        # R2 — archived / no write authority is historical, never canonical
        if archived is True or (isinstance(write_authority, str) and write_authority.upper() == "NONE"):
            if cls != "HISTORICAL_ARCHIVED":
                trace.append("R2:downgrade_from=%s" % cls)
            cls = "HISTORICAL_ARCHIVED"
            blockers.append(C_HISTORICAL)
            offer(C_HISTORICAL)
            trace.append("R2:historical_forced")
        else:
            trace.append("R2:pass")

        # R3 — skill / sidecar can never be compiler or checker
        if kind in SKILL_KINDS:
            if cls != "SKILL_SIDECAR":
                trace.append("R3:downgrade_from=%s" % cls)
            cls = "SKILL_SIDECAR"
            role_claim = (declared.get("role_claim") or "").upper()
            if role_claim in COMPILER_ROLE_CLAIMS:
                blockers.append(C_SKILL_PERMIT)
                offer(C_SKILL_PERMIT)
                trace.append("R3:role_claim=%s" % role_claim)
                self._add_hold(
                    C_SKILL_PERMIT,
                    ("Skill/Sidecar 自稱 %s 並要求授權：Skill 不是 Canonical Compiler/Checker，"
                     "不得產出 canonical 編譯或 checker 判決" % role_claim),
                    [hint["source_id"]],
                    [hint["evidence_field"] + "=" + str(hint["evidence_value"])]
                    + hint["evidence_support"][:2],
                    owner="Original PIPD/SBL Canonical Compiler Owner 與受保護 Checker Owner",
                    required_raw=("原 canonical compiler / 受保護 checker 對該 Subject 的執行收據；"
                                  "Skill 側僅可提供 AUTH_SOURCE_METHOD，不可替代"),
                    resume=("撤回以 Skill/Sidecar 充作 compiler/checker 的主張，或原 compiler/checker "
                            "Owner 出具同一 Subject/Candidate 的 receipt"),
                )
            else:
                trace.append("R3:no_role_claim")
                offer(C_SKILL_SIDECAR)
        else:
            trace.append("R3:pass")

        # R1 — a mirror is never writable; effect_permission=NONE is never writable
        if cls == "GOVERNANCE_MIRROR":
            blockers.append(C_MIRROR_NOT_WRITABLE)
            offer(C_MIRROR_NOT_WRITABLE)
            trace.append("R1:mirror_not_writable")
        elif isinstance(effect, str) and effect.upper() == "NONE":
            blockers.append(C_EFFECT_NONE)
            offer(C_EFFECT_NONE)
            trace.append("R1:effect_permission=NONE")
        else:
            trace.append("R1:pass")

        reason = best[0]

        entry = {
            "group": hint["group"],
            "source_id": hint["source_id"],
            "path": hint["path"],
            "evidence_field": hint["evidence_field"],
            "evidence_value": hint["evidence_value"],
            "evidence_support": hint["evidence_support"],
            "authority_class": cls,
            "may_authorize_write": False,
            "may_mint_permit": False,
            "reason_code": reason,
            "subject_id": hint["subject_id"],
            "scope_id": hint["scope_id"],
            "artifact_key": hint["artifact_key"],
            "canonical_key": hint.get("canonical_key"),
            "declared": declared,
            "write_blockers": blockers,
            "rules_applied": trace,
        }
        # write gate: explicit grant required, and no blocker may be present
        entry["may_authorize_write"] = self.gate_authorizes_write(
            cls, declared, blockers, hint
        )
        if entry["may_authorize_write"]:
            entry["rules_applied"].append("GATE:explicit_write_grant")
        else:
            entry["rules_applied"].append("GATE:denied")

        # R5 — subject/scope binding
        subj = hint["subject_id"]
        scope = hint["scope_id"]
        subject_ref = declared.get("subject_ref")
        r5 = None
        if unbound(subj) and unbound(scope):
            r5 = "no subject/scope binding"
        elif isinstance(subject_ref, str) and self.current_candidate_sha and \
                subject_ref != self.current_candidate_sha:
            r5 = ("subject_ref %s != current candidate body %s"
                  % (subject_ref[:12], self.current_candidate_sha[:12]))
        if r5:
            entry["may_authorize_write"] = False
            offer(C_SCOPE_UNBOUND)
            entry["reason_code"] = best[0]
            entry["rules_applied"].append("R5:unbound(%s)" % r5)
            self._add_hold(
                C_SCOPE_UNBOUND,
                "artifact 的 subject/scope 未綁定到當前 candidate：%s" % r5,
                [entry["source_id"]],
                [entry["evidence_field"] + "=" + entry["evidence_value"]]
                + entry["evidence_support"][:2]
                + ([hint["evidence_support"][0]] if entry["declared"].get("subject_ref") else []),
                owner=("Original Owner of %s（artifact 的 subject Owner）" % hint["path"]),
                required_raw=("能解析到當前 candidate body sha256 的 subject/scope 綁定"
                              "（或原 Owner 明示該 artifact 的 subject 與當前 candidate 之對應）"),
                resume=("該 artifact 宣告的 subject_ref 等於當前 candidate body sha256，"
                        "或原 Owner 出具 binding 讀回"),
            )
        else:
            entry["rules_applied"].append("R5:bound")

        # R6 — profile / role / worker must not be substituted
        conflate = self._actor_conflation(declared.get("actor_binding"))
        if conflate:
            entry["may_authorize_write"] = False
            offer(C_PROFILE_ROLE)
            entry["reason_code"] = best[0]
            entry["rules_applied"].append("R6:conflated(%s)" % conflate)
            self._add_hold(
                C_PROFILE_ROLE,
                "actor binding 把 Profile 與 Role/Worker 當同一識別：%s" % conflate,
                [entry["source_id"]],
                [entry["evidence_field"] + "=" + entry["evidence_value"]],
                owner="Original PIPD ProfileBinding Owner（Profile 契約 Owner）",
                required_raw=("分離的 profile_id / role_id / worker_id 識別，且 profile ∈ "
                              "LITE|STANDARD|ASSURED（ProfileBinding.schema.json:$."
                              "properties.profile.enum）"),
                resume=("該 artifact 以三個獨立識別宣告 actor，或撤回 role/worker 視同 profile 的主張；"
                        "原 ProfileBinding Owner 讀回"),
            )
        else:
            entry["rules_applied"].append("R6:pass")
        return entry

    @staticmethod
    def _actor_conflation(binding):
        if not isinstance(binding, dict):
            return None
        prof = binding.get("profile_id") or binding.get("profile")
        role = binding.get("role_id") or binding.get("role")
        worker = binding.get("worker_id") or binding.get("worker")
        pairs = (("profile_id", "role_id", prof, role),
                 ("profile_id", "worker_id", prof, worker),
                 ("role_id", "worker_id", role, worker))
        for a, b, va, vb in pairs:
            if isinstance(va, str) and isinstance(vb, str) and va.strip() and va.strip() == vb.strip():
                return "%s == %s (%s)" % (a, b, va.strip())
        return None

    @staticmethod
    def gate_authorizes_write(cls, declared, blockers, hint=None):
        """The write gate is a real predicate, not a constant.

        It requires ALL of: canonical class, an explicit write-authority grant,
        a declared non-NONE effect permission, and zero blocking rules.
        """
        if blockers:
            return False
        if cls != "CANONICAL_ORIGINAL":
            return False
        wa = declared.get("write_authority")
        if not (isinstance(wa, str) and wa.strip().upper() in WRITE_GRANT_VALUES):
            return False
        effect = declared.get("effect_permission")
        if not (isinstance(effect, str) and effect.strip().upper() not in ("", "NONE")):
            return False
        if declared.get("archived") is True:
            return False
        if (declared.get("artifact_kind") or "").upper() in SKILL_KINDS:
            return False
        return True

    def _positive_reason(self, cls, hint):
        sid = hint["source_id"]
        if hint["group"] == "SOURCE31":
            return P_DOC31
        if hint["group"] == "ORACLE96":
            return P_ORACLE
        if hint["group"] == "SEAM5":
            return P_SEAM
        if hint["group"] == "AUTHOR_ROUND":
            return P_AUTHOR
        if cls == "CANONICAL_ORIGINAL":
            return P_SBL_SRC
        if cls == "SKILL_SIDECAR":
            return C_SKILL_SIDECAR
        if cls == "HISTORICAL_ARCHIVED":
            return C_HISTORICAL
        if cls == "GOVERNANCE_MIRROR":
            return P_NAV
        return P_AUTHOR

    def _rule_r4_dual_canonical(self):
        seen = {}
        for entry in self.entries:
            if entry["authority_class"] != "CANONICAL_ORIGINAL":
                continue
            key = entry.get("canonical_key") or "%s#%s" % (entry["subject_id"], entry["artifact_key"])
            seen.setdefault(key, []).append(entry)
        for key, rows in seen.items():
            paths = {row["path"] for row in rows}
            if len(rows) < 2 or len(paths) < 2:
                continue
            ids = [row["source_id"] for row in rows]
            for row in rows:
                row["may_authorize_write"] = False
                if REASON_PRIORITY.get(row["reason_code"], 0) < REASON_PRIORITY[C_DUAL_CANONICAL]:
                    row["reason_code"] = C_DUAL_CANONICAL
                row["rules_applied"].append("R4:dual_canonical(%d claimants)" % len(rows))
            self._add_hold(
                C_DUAL_CANONICAL,
                "同一 canonical_key 有 %d 個 CANONICAL_ORIGINAL 宣告者：%s" % (len(rows), key),
                ids,
                [row["evidence_field"] + "=" + row["evidence_value"] for row in rows],
                owner="該 subject 的原 Canonical Owner（原 Reader/Owner）",
                required_raw="兩份候選原件的原 Owner 指示其一為 canonical（其餘標 historical/archived）",
                resume=("原 Owner 指定唯一 canonical source_id，或其中一份被標記 archived/"
                        "write_authority=NONE（則本規則不再觸發）"),
            )
        self.checks["r4_dual_canonical_groups"] = {
            "canonical_keys": len(seen),
            "conflicting_keys": sum(1 for k, v in seen.items()
                                    if len(v) > 1 and len({r["path"] for r in v}) > 1),
        }

    def _check_mirror_identity(self):
        """R7: compare the readback bytes' git blob sha1 with the ref blob recorded by REPOS_RECHECK."""
        self.checks["mirror_identity"] = {"status": "NOT_CHECKED"}
        if not isinstance(self.repos_recheck, dict) or not self.repomap_key:
            return
        art = None
        for row in self.repos_recheck.get("routing_artifacts") or []:
            if row.get("path") == "INTEGRATION/FHS/repository-map.json":
                art = row
                break
        if not art or not art.get("refs"):
            return
        claim = art["refs"][0]
        local = self.loaded.get(self.repomap_key, {})
        local_blob = local.get("git_blob_sha1")
        claim_blob = claim.get("blob_sha1")
        match = bool(local_blob and claim_blob and local_blob == claim_blob)
        self.checks["mirror_identity"] = {
            "file": self.repomap_key,
            "local_git_blob_sha1": local_blob,
            "local_bytes": local.get("bytes"),
            "ref": claim.get("ref"),
            "ref_blob_sha1": claim_blob,
            "ref_blob_bytes": claim.get("blob_bytes"),
            "match": match,
            "classification": art.get("classification"),
        }
        if not match:
            self._add_hold(
                C_MIRROR_IDENTITY,
                ("授權欄位出處的 NAV mirror 與 ref blob 不同：本地 %s (%s bytes) vs ref %s (%s bytes)"
                 % (str(local_blob)[:12], local.get("bytes"), str(claim_blob)[:12],
                    claim.get("blob_bytes"))),
                [row["source_id"] for row in self.entries
                 if row["group"] == "REPO_MAP"][:3] or ["GOV:NAV-REPOMAP"],
                [
                    "REPOS_RECHECK.json:$.routing_artifacts[repository-map.json].refs[0].blob_sha1=%s"
                    % claim_blob,
                    "%s:git_blob_sha1=%s" % (self.repomap_key, local_blob),
                    "REPOS_RECHECK.json:$.routing_artifacts[repository-map.json].classification=%s"
                    % art.get("classification"),
                ],
                owner="Fabric INTEGRATION/FHS NAV Owner（FHS-NAV/v2 索引 Owner）",
                required_raw=("ref %s 的 byte-exact blob 讀回（git cat-file blob %s），"
                              "使 readback git blob sha1 與 bytes 相符"
                              % (claim.get("ref"), str(claim_blob)[:12])),
                resume=("本輪 readback 的 git blob sha1 == %s 且 bytes == %s；或原 NAV Owner 出具"
                        "當期 repository-map.json" % (claim_blob, claim.get("blob_bytes"))),
            )

    def _check_compiler_receipt(self):
        if not isinstance(self.plugin, dict):
            return
        cc = self.plugin.get("canonical_compiler")
        hl = self.plugin.get("host_loaded")
        if cc == "NOT_RUN" or hl == "NOT_OBSERVED":
            self._add_hold(
                C_COMPILER_NOT_RUN,
                ("canonical_compiler=%s / host_loaded=%s：本輪沒有 canonical 編譯與 host load 收據"
                 % (cc, hl)),
                ["SKILL:" + str(self.plugin.get("plugin"))],
                ["PLUGIN_USAGE_AND_GHP01.json:$.canonical_compiler=%s" % cc,
                 "PLUGIN_USAGE_AND_GHP01.json:$.host_loaded=%s" % hl],
                owner="Original PIPD/SBL Canonical Compiler Owner（PIPD compile-pi 原 Owner）",
                required_raw="原 canonical compiler 對當前 candidate body 的執行收據（含 host load receipt、PID/ProfileSHA）",
                resume="原 compiler 對當前 candidate body 執行並出具同一 Subject/Candidate/Scope 的 receipt",
            )

    def _check_source31_currentness(self):
        holds = [row for row in (self.src31 or [])
                 if row.get("currentness") == "ORIGINAL_READER_CURRENTNESS_HOLD"]
        self.checks["source31_currentness"] = {
            "declared_entries": self.source31_declared,
            "currentness_hold_entries": len(holds),
        }
        if holds:
            self._add_hold(
                C_CURRENTNESS,
                ("%d/%d 個 SOURCE31 原件在 manifest 內標記 ORIGINAL_READER_CURRENTNESS_HOLD："
                 "檔案身份 PASS ≠ 原 Reader 當期性已確認" % (len(holds), self.source31_declared)),
                ["SOURCE31:%d entries" % len(holds)],
                ["SOURCE31_PHYSICAL_IDENTITY.json:$[*].currentness=ORIGINAL_READER_CURRENTNESS_HOLD",
                 "UPSTREAM_IDENTITY.json:$.source31_physical_identity.declared_currentness"],
                owner="Original SBL/FHS Reader（31 份原件的 Currentness Owner）",
                required_raw="原 Reader 對 31 份原件的當期性讀回（currentness readback），或逐份說明其為當期版本",
                resume="原 Reader 出具 currentness=CONFIRMED 的讀回，或明確標記哪幾份已被取代",
            )

    def _add_hold(self, code, reason, source_ids, evidence, owner, required_raw, resume,
                  blocking=None, nonaffected=None):
        self._hold_seq = getattr(self, "_hold_seq", 0) + 1
        hold_id = "H-AUTH-R4C-%03d-%s" % (self._hold_seq, HOLD_TAGS.get(code, "HOLD"))
        self.holds.append(
            {
                "hold_id": hold_id,
                "code": code,
                "severity": "BLOCKING_FOR_AFFECTED_CLAIM",
                "reason": reason,
                "source_ids": sorted(set(source_ids)),
                "evidence": evidence,
                "owner": owner,
                "required_raw": required_raw,
                "resume_predicate": resume,
                "blocked_operation": blocking
                or "把受影響 artifact 當作可授寫／canonical／已驗證",
                "nonaffected_permitted": nonaffected
                or "SOURCE_READ 與 AUTHOR_LOCAL_DRAFT 續行；不全域停工",
            }
        )

    def _finalise(self):
        for entry in self.entries:
            if entry["may_authorize_write"]:
                entry["reason_code"] = entry["reason_code"]  # explicit grant already recorded
            if entry["may_mint_permit"]:
                raise RouterError("INVARIANT: may_mint_permit must stay false (%s)"
                                  % entry["source_id"])
            if not entry["evidence_field"]:
                raise RouterError("INVARIANT: empty evidence_field (%s)" % entry["source_id"])
            file_key = entry["evidence_field"].split(":$", 1)[0]
            if file_key not in self.loaded:
                raise RouterError(
                    "INVARIANT: evidence points at a file that was not loaded: %r (%s)"
                    % (file_key, entry["source_id"]))
        order = {g: i for i, g in enumerate(GROUP_ORDER)}
        self.entries.sort(key=lambda r: (order.get(r["group"], 99), r["source_id"]))

    # -- reporting -------------------------------------------------------
    def statistics(self):
        by_class = {cls: 0 for cls in CLASSES}
        for entry in self.entries:
            by_class[entry["authority_class"]] += 1
        by_group = {}
        for entry in self.entries:
            by_group[entry["group"]] = by_group.get(entry["group"], 0) + 1
        by_code = {}
        for entry in self.entries:
            by_code[entry["reason_code"]] = by_code.get(entry["reason_code"], 0) + 1
        writable = [e["source_id"] for e in self.entries if e["may_authorize_write"]]
        mintable = [e["source_id"] for e in self.entries if e["may_mint_permit"]]
        return {
            "total_entries": len(self.entries),
            "by_class": by_class,
            "by_group": by_group,
            "by_reason_code": dict(sorted(by_code.items())),
            "source31_declared": self.source31_declared,
            "source31_routed": by_group.get("SOURCE31", 0),
            "may_authorize_write_true": len(writable),
            "may_authorize_write_true_ids": writable,
            "may_mint_permit_true": len(mintable),
            "holds_total": len(self.holds),
            "holds_by_code": self._holds_by_code(),
            "entries_without_evidence_field": sum(
                1 for e in self.entries if not e["evidence_field"]),
        }

    def _holds_by_code(self):
        out = {}
        for hold in self.holds:
            out[hold["code"]] = out.get(hold["code"], 0) + 1
        return dict(sorted(out.items()))

    def document(self):
        stats = self.statistics()
        doc = {
            "schema": SCHEMA,
            "tool": {"name": "authority_router.py", "version": TOOL_VERSION, "wp": "WP-FHS-01"},
            "generated_at": datetime.now(EPSILON_TZ).isoformat(timespec="seconds"),
            "source_root": self.source_root,
            "readback_root": self.readback_root,
            "claim_ceiling": "AUTHOR_LOCAL_TEST",
            "classes": list(CLASSES),
            "rulebook": [
                {"rule_id": rid, "statement": stmt, "code": code} for rid, stmt, code in RULEBOOK
            ],
            "inputs": {
                key: {k: v for k, v in info.items() if k != "path"}
                for key, info in self.loaded.items()
            },
            "inputs_absent": self.absent,
            "checks": self.checks,
            "statistics": stats,
            "write_authority_explanation": {
                "may_authorize_write_true": stats["may_authorize_write_true"],
                "statement": (
                    "0 筆可授寫。閘門要求同時滿足：authority_class=CANONICAL_ORIGINAL、"
                    "顯式 write_authority∈{GRANTED,WRITE,FULL,AUTHORIZED,PREAUTHORIZED}、"
                    "已宣告且非 NONE 的 effect_permission、無任何 HOLD 阻擋。"
                    "本輪來源中：31 份原件與 SBL 領域原始碼皆未宣告 write_authority；"
                    "NAV mirror 宣告 effect_permission=NONE；PIPD-LS-SP archived=true/write_authority=NONE；"
                    "Skill/Sidecar 非 permit 來源；作者產物為 AUTHOR_CANDIDATE。"
                    "故統計為 0 而非閘門恆假（gate 為真值函數，見 tests 的 gate 單元測試）。"
                ),
                "per_class": {
                    "CANONICAL_ORIGINAL": "原件與 SBL 領域原始碼：內容權威但不授寫（write_authority 未宣告）",
                    "GOVERNANCE_MIRROR": "FHS-NAV/v2，identity=FABRIC_HOSTED_NON_AUTHORITATIVE_INDEX，effect_permission=NONE",
                    "SKILL_SIDECAR": "sbl-tpm-sp Skill/Sidecar 與 AGENTS 指令檔：不得作 Canonical Compiler/Checker，非 permit 來源",
                    "HISTORICAL_ARCHIVED": "PIPD-LS-SP：archived=true、write_authority=NONE、canonical 已移至 SBL integrations/pipd",
                    "AUTHOR_CANDIDATE": "本輪作者產物（Oracle96/Seam5/正文/manifest/DAG 等）：AUTHOR_DESIGN_ONLY，未 Native 執行",
                },
            },
            "non_claims": [
                "不宣稱任何 Native/Permit/WorkOrder/受保護 Checker 判決",
                "不宣稱 mirror 讀回與 ref blob byte-exact（見 mirror_identity 檢查與 HOLD）",
                "不宣稱 31 份原件當期性（currentness HOLD 未解）",
                "不宣稱 PIPD-LS-SP 的 archived 狀態由本輪變更",
                "分類為本輪 LANE 內可重跑的作者分流結果，claim ceiling=AUTHOR_LOCAL_TEST",
            ],
            "entries": self.entries,
            "holds": self.holds,
        }
        return doc

    def markdown(self):
        stats = self.statistics()
        lines = []
        add = lines.append
        add("# AUTHORITY_ROUTING — WP-FHS-01 權威分流（%s）" % SCHEMA)
        add("")
        add("- source_root: `%s`" % self.source_root)
        add("- readback_root: `%s`" % (self.readback_root or "-"))
        add("- claim_ceiling: `AUTHOR_LOCAL_TEST`（作者本地可重跑；非 Native、非受保護 Checker）")
        add("- may_mint_permit: `false`（全部 %d 筆）" % stats["total_entries"])
        add("")
        add("## 統計")
        add("")
        add("| 項目 | 值 |")
        add("| --- | --- |")
        add("| 總筆數 | %d |" % stats["total_entries"])
        for cls in CLASSES:
            add("| %s | %d |" % (cls, stats["by_class"][cls]))
        add("| SOURCE31 宣告／實際路由 | %d / %d |"
            % (stats["source31_declared"], stats["source31_routed"]))
        add("| may_authorize_write=true | %d |" % stats["may_authorize_write_true"])
        add("| may_mint_permit=true | %d |" % stats["may_mint_permit_true"])
        add("| HOLD 筆數 | %d |" % stats["holds_total"])
        add("")
        add("`may_authorize_write=true` 為 0 的理由：閘門要求 class=CANONICAL_ORIGINAL＋顯式"
            " write_authority 授權＋已宣告非 NONE 的 effect_permission＋無 HOLD。本輪無任何來源"
            "同時滿足（31 原件與 SBL 原始碼未宣告 write_authority；mirror effect_permission=NONE；"
            "PIPD archived/write_authority=NONE；Skill 非 permit；作者產物為 candidate）。")
        add("")
        add("## 規則")
        add("")
        add("| Rule | 陳述 | 碼 |")
        add("| --- | --- | --- |")
        for rid, stmt, code in RULEBOOK:
            add("| %s | %s | `%s` |" % (rid, stmt.replace("|", "\\|"), code))
        add("")
        add("## 檢查結果")
        add("")
        add("```json")
        add(json.dumps(self.checks, ensure_ascii=False, indent=1, sort_keys=True))
        add("```")
        add("")
        for cls in CLASSES:
            rows = [e for e in self.entries if e["authority_class"] == cls]
            add("## %s（%d）" % (cls, len(rows)))
            add("")
            add("| source_id | class | evidence_field | reason_code |")
            add("| --- | --- | --- | --- |")
            for row in rows:
                add("| `%s` | %s | `%s` = %s | `%s` |"
                    % (row["source_id"], row["authority_class"], row["evidence_field"],
                       str(row["evidence_value"]).replace("|", "\\|"), row["reason_code"]))
            add("")
        add("## HOLD（%d）" % len(self.holds))
        add("")
        add("| hold_id | code | owner | required_raw | resume_predicate |")
        add("| --- | --- | --- | --- | --- |")
        for hold in self.holds:
            add("| `%s` | `%s` | %s | %s | %s |"
                % (hold["hold_id"], hold["code"], hold["owner"].replace("|", "\\|"),
                   hold["required_raw"].replace("|", "\\|"),
                   hold["resume_predicate"].replace("|", "\\|")))
        add("")
        add("## 非宣稱")
        add("")
        for item in self.document()["non_claims"]:
            add("- %s" % item)
        add("")
        return "\n".join(lines)

    def write(self):
        os.makedirs(self.out_dir, exist_ok=True)
        doc = self.document()
        json_path = os.path.join(self.out_dir, "AUTHORITY_ROUTING.json")
        md_path = os.path.join(self.out_dir, "AUTHORITY_ROUTING.md")
        with open(json_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.markdown())
        return json_path, md_path, doc


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WP-FHS-01 authority router: route sources into five authority classes "
                    "and emit typed HOLDs.")
    parser.add_argument("--source-root", required=True, help="R4C source root directory")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--readback-root", default=None,
                        help="directory holding fabric_repository-map.json readback "
                             "(default: <script>/../../source_readback/remote)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    readback = args.readback_root
    if readback is None:
        guess = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                         "source_readback", "remote"))
        readback = guess if os.path.isdir(guess) else None

    try:
        router = AuthorityRouter(args.source_root, args.out, readback)
        router.load().build_hints().classify()
        json_path, md_path, doc = router.write()
    except RouterError as exc:
        sys.stderr.write("ROUTER_ERROR: %s\n" % exc)
        return 2 if "required input" in str(exc) or "not a directory" in str(exc) else 3

    if not args.quiet:
        stats = doc["statistics"]
        print("AUTHORITY_ROUTING written: %s" % json_path)
        print("                            %s" % md_path)
        print("entries=%d by_class=%s"
              % (stats["total_entries"],
                 json.dumps(stats["by_class"], ensure_ascii=False, sort_keys=True)))
        print("source31=%d/%d may_authorize_write_true=%d may_mint_permit_true=%d holds=%d"
              % (stats["source31_routed"], stats["source31_declared"],
                 stats["may_authorize_write_true"], stats["may_mint_permit_true"],
                 stats["holds_total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
