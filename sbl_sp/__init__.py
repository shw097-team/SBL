"""SBL Slice B1 - separated specialised principals (SP)."""

from .sp import MANIFEST_DIR, assert_permission, load_manifest, sign_verdict

# Deliberately NOT exported: ``load_key`` and ``expected_signature``. Exporting them made the
# package hand out both the key and the digest that proves possession of it, so any caller could
# mint a challenger credential (independent challenge round 2, NEW-02). Operator tooling imports
# them from ``sbl_sp.sp`` explicitly and provisions the key through the environment.
__all__ = [
    "MANIFEST_DIR",
    "assert_permission",
    "load_manifest",
    "sign_verdict",
]
