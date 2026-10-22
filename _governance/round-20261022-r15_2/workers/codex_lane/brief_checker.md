You are an independent read-only checker. You may not create or modify any file. Do not run git.

Audit the bounded write that was just produced at workers/codex_writer/EXECUTE_WRITER_RECEIPT.md:
1. Read it.
2. Compare its declared write_set, model and effect lines against what actually exists on disk.
3. State whether the receipt over-claims anything (e.g. calls itself a Permit, or claims a product
   change) and whether the file is a pure addition that touches no product source.

Print ONLY a single-line JSON object with keys: verdict (PASS|FAIL), addition_only (bool),
overclaims (array of strings), note (string).
