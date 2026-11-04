# FHS NAV-only agent instructions

This file is only a local navigation guide when the host actually loads it. It is not a permission system or cross-repository instruction that applies automatically outside this directory.

1. Classify a task as a **proposal** using an exact `task_class` from `repository-map.json`; never use an unverified LLM guess for high effects.
2. Read the original source and confirm branch / HEAD / RepoContext / original Owner / affected Consumer; FHS URLs and static CI do not prove native source identity.
3. `cross_repo` means separate original-domain readers and candidate PRs, not an omnipotent push.
4. `hermes_runtime` requires the original Host Reader for fresh PID, ProfileSHA, loaded and invoked state, requested/served models; never infer from GitHub.
5. Unclassified or conflicting request: HOLD its affected write; legitimate read-only work and drafts continue according to existing permission.
6. Never issue WorkOrder, Permit, Policy, PI compiler output, protected checker receipt or release from this directory.
