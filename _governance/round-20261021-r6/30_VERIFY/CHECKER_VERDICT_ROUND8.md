STRENGTHS
- Wheel SHA-256 matches `wheel.sha256`: `cc69291b8f0c9dbbcfeccea61e0a254876e54d9396360345bdc305c9769a9e02`.

WEAKNESSES
- Pytest exited with code 1; the expected `192 passed, 2 skipped` result was not achieved.
- Test setup encountered `PermissionError: [WinError 5]` accessing `.checker_tmp/bt8`.

ITEMS-LIST
- Executed only the two requested checks; no remediation or rerun.
- Pytest output was truncated; exact aggregate counts are unavailable.

VERDICT: FAIL
R6CHK29R8-NC
