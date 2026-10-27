# Portable TPM candidate adapters

New local reader and planning adapter code for `sbl-tpm-sp`. This source-only
candidate uses the Python 3.11 standard library and does not include a Plugin
manifest, P4 source, raw DOC corpus, third-party Donor code, credentials, or
trusted receipts. It is not a complete installable plugin or a production release.

The complete private candidate is retained in the builder's local deliverables.
The selected GitHub repository is public; unresolved P4/DOC distribution grants
prevent uploading that full package. This branch does not change repository
policy or claim to install/update the account plugin.

Implemented: exact-hash local Artifact/Graph Readers, conservative 12-axis risk
projection, draft three-role SPEC materialization, Planned TQAEP, affected-only
errors, dependency evaluation, question reuse, and deny-by-default GitHub/Native
interfaces. These cannot issue Canonical PIPD, HGK, Checker or Publisher authority.

Run `python -m unittest discover -s portable-tpm-candidate -p "test_*.py" -v`
from the repository root, or `python -m unittest -v` in this folder.

Current limits: raw corpus is omitted, original graph EDGE fixture remains
unresolved locally, formal Oracle/StageMap/source grants remain open, actual
model-trigger and Agent acceptance remain NOT_RUN. CLI install/load/uninstall
and local CLI/brownfield FUO evidence do not mean Native or Production Accepted.
