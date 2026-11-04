#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 tests/fixtures/neg1..neg5 的合成來源根（可重跑，內容固定）。

每個 fixture 都是一個最小合法 `--source-root`：至少含
SOURCE31_PHYSICAL_IDENTITY.json，再加上該 NEG 要觸發的宣告檔。
這些 fixture 是「合成」而非真實來源，僅用於證明規則會真的 red；
不得被引用為任何真實來源的證據。
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")

DOC = {
    "original_name": "SYNTHETIC_DOC-00(1).md",
    "bytes": 100,
    "lines": 10,
    "physical_identity": "PASS",
    "currentness": "SYNTHETIC_FIXTURE",
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def source31(*rows):
    out = []
    for idx, extra in enumerate(rows):
        row = dict(DOC)
        row.update(
            {
                "source_id": extra.pop("source_id", "SYN-DOC-%02d" % idx),
                "path": extra.pop("path", "synthetic/corpus/SYN_DOC-%02d.md" % idx),
                "sha256": extra.pop("sha256", "%064d" % (idx + 1)),
            }
        )
        row.update(extra)
        out.append(row)
    return out


# ---- neg1: mirror 自稱可授寫（mirror-as-authority） --------------------------
def neg1():
    root = os.path.join(FIXTURES, "neg1_mirror_as_authority")
    write(os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"), source31({}))
    write(
        os.path.join(root, "repository-map.json"),
        {
            "schema_version": "FHS-NAV/v2",
            "identity": "FABRIC_HOSTED_NON_AUTHORITATIVE_INDEX",
            "effect_permission": "NONE",
            "write_authority": "GRANTED",
            "source_state": "PROPOSED_NOT_OWNER_RATIFIED",
            "repositories": {
                "sbl": {"full_name": "shw097-team/SBL", "default_branch": "main",
                        "domain": "PRODUCT_TPM", "write_authority": "GRANTED"},
            },
            "historical_repositories": {},
            "routes": [
                {"task_class": "sbl_product", "primary_repo": "sbl",
                 "affected_repos": ["fabric"], "claim": "NAVIGATION_ONLY",
                 "write_authority": "GRANTED"},
            ],
        },
    )


# ---- neg2: Skill 自稱 Canonical Compiler 並要求授權（skill-as-permit） -------
def neg2():
    root = os.path.join(FIXTURES, "neg2_skill_as_permit")
    write(os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"), source31({}))
    write(
        os.path.join(root, "PLUGIN_USAGE_AND_GHP01.json"),
        {
            "plugin": "sbl-tpm-sp",
            "installed_path": "synthetic/plugins/sbl-tpm-sp",
            "states": {"SELECTED": "USER_PLUGIN_MENTION"},
            "canonical_compiler": "CLAIMED_BY_SKILL",
            "host_loaded": "CLAIMED_BY_SKILL",
            "role_claim": "CANONICAL_COMPILER",
            "write_authority": "GRANTED",
            "effect_permission": "GRANTED",
        },
    )


# ---- neg3: 同一 subject 兩個 canonical 宣告者（dual canonical） --------------
def neg3():
    root = os.path.join(FIXTURES, "neg3_dual_canonical")
    rows = source31(
        {"source_id": "SYN-DUP-A", "path": "synthetic/corpus/DUP-A.md",
         "subject_id": "SUBJ-DUP-001", "artifact_key": "ORIGINAL_DOCUMENT",
         "write_authority": "GRANTED", "effect_permission": "GRANTED"},
        {"source_id": "SYN-DUP-B", "path": "synthetic/corpus/DUP-B.md",
         "subject_id": "SUBJ-DUP-001", "artifact_key": "ORIGINAL_DOCUMENT",
         "write_authority": "GRANTED", "effect_permission": "GRANTED"},
    )
    write(os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"), rows)


# ---- neg4: 缺 subject/scope 綁定（scope unbound） ---------------------------
def neg4():
    root = os.path.join(FIXTURES, "neg4_scope_unbound")
    rows = source31(
        {"source_id": "SYN-UNBOUND", "path": "synthetic/corpus/UNBOUND.md",
         "subject_id": "UNBOUND", "scope_id": "UNBOUND",
         "write_authority": "GRANTED", "effect_permission": "GRANTED"},
    )
    write(os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"), rows)


# ---- neg5: Profile 被當 Role/Worker 用（profile-role conflation） ------------
def neg5():
    root = os.path.join(FIXTURES, "neg5_profile_role_conflated")
    rows = source31(
        {"source_id": "SYN-PROFILE", "path": "synthetic/corpus/PROFILE.md",
         "subject_id": "SUBJ-PROFILE-001",
         "actor_binding": {"profile_id": "PIPD-OWNER-01",
                           "role_id": "PIPD-OWNER-01",
                           "worker_id": "WORKER-77"},
         "write_authority": "GRANTED", "effect_permission": "GRANTED"},
    )
    write(os.path.join(root, "SOURCE31_PHYSICAL_IDENTITY.json"), rows)


def main():
    for fn in (neg1, neg2, neg3, neg4, neg5):
        fn()
    print("fixtures written under %s" % FIXTURES)


if __name__ == "__main__":
    main()
