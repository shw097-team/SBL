# TS23 M2 sandbox - what these three programs promise, and what they do not

This file exists because three review rounds kept finding behaviour that was never specified. An unspecified behaviour
cannot fail a test, so a wrong answer passes it. The rules below are the contract; each one has a fixture, and each fixture
asserts its own precondition before it asserts the program's answer.

## ts23-newline (read-only byte and line-terminator census)

- `bytes` is the file size in bytes. The file is read as bytes, never decoded.
- `newlines` is the number of line **terminators**, not the number of lines. A terminator is one of: LF (`\n`), CRLF
  (`\r\n`), or a lone CR (`\r`). The count is therefore `count(LF) + count(CR) - count(CRLF)`.
  - `alpha\nbeta\n` -> 2. The trailing terminator counts.
  - `alpha\nbeta` -> 1. An unterminated final line is not a terminator.
  - `alpha\rbeta\r` -> 2. A lone CR is a terminator.
  - `a\n\rb` -> 2. LF and CR that are not adjacent as CRLF are two terminators.
  - `\r\n\r\n\n\r` -> 4.
  - A file of only terminators counts all of them; it is not treated as empty.
- `sha256` is the digest of the exact bytes read.
- A missing or unreadable path exits **2**, writes `ERR_INPUT` to stderr, writes **nothing to stdout** and prints no
  traceback.
- The file is never rewritten; the census is read-only.
- A UTF-8 BOM is bytes. It is counted, not stripped. Binary content is fine: nothing is decoded.

## ts23-headings (ATX heading inventory)

- A heading is a line starting with 1 to 6 `#` characters, followed by **at least one space or tab**, followed by text.
  `#NoSpace` is not a heading; a tab is a valid separator.
- Leading and trailing **ASCII space or tab** is trimmed; **internal whitespace is preserved** (`##  two  spaces  ` ->
  `two  spaces`). Nothing else is whitespace here: U+00A0, U+3000 and every other Unicode space is content, so
  `## Gamma\u00a0` -> `Gamma\u00a0`, not `Gamma`.
- A line is delimited by LF, CRLF or CR **only**. U+2028, U+2029, NEL (U+0085), VT (U+000B) and FF (U+000C) are content,
  because the census in `ts23-newline` counts exactly those three terminators and the two programs must agree on the same
  bytes: `# A\u2028B` -> text `A\u2028B`, not `A`.
- An empty text after trimming is **not** a heading (`## ` alone is ignored).
- 7 or more `#` characters is not a heading. That line is ignored, not an error.
- An ATX **closing sequence** - an ASCII space or tab, then one or more `#` at end of line - is removed: a Unicode
  space (U+00A0, U+3000) is content, not whitespace:
  `## Beta ##` -> `Beta`. A `#` that is not preceded by whitespace is content: `## tag#` -> `tag#`.
- Text is kept exactly as written, including non-ASCII characters and including decomposed (NFD) sequences. No Unicode
  normalisation is performed.
- `line` is the 1-based line number in the file.
- A missing or undecodable file exits **2**, writes `ERR_INPUT` to stderr, writes **nothing to stdout** and prints no
  traceback.

## ts23-review (bounded deterministic evidence review)

- The queue is a JSON array of file paths, read in order. `--max-steps N` bounds how many are reviewed (default 2).
- Each review entry records `path`, `bytes` (exact size) and `sha256` (digest of those bytes).
- `steps` is the number reviewed; `remaining` is `len(queue) - steps`.
- `halt_reason` is `BUDGET` when the step limit stopped the run and `QUEUE_EXHAUSTED` when the queue ran out. An **empty
  queue** therefore reports `steps 0, remaining 0, reviews [], halt_reason QUEUE_EXHAUSTED` - nothing was queued, so nothing
  was budget-limited.
- A queue that is not a JSON array exits **2**. An entry that cannot be read exits **2**; nothing is silently skipped.
  In both cases stderr carries `ERR_INPUT` and stdout stays empty. "Cannot be read" includes a **directory** and a
  permission-denied file, not only a path that does not exist: a program that special-cases `FileNotFoundError` alone is
  wrong on those inputs.
- A queue longer than the step limit reports `BUDGET`; a queue shorter than the limit reports `QUEUE_EXHAUSTED`.
- **Precedence:** a step limit of zero or less reports `BUDGET` **even when the queue is empty**, because the limit stopped
  the run before anything could be read. The empty-queue rule above applies only when the limit is one or more. This
  resolves the contradiction between the two clauses: budget decides first, the queue decides second.

## Out of scope, deliberately

These are named so that a test is not expected to cover them, rather than being quietly missing:

- fenced code blocks and indented code blocks: a `#` line inside a fence is still reported as a heading;
- setext headings (`text` underlined with `===` or `---`);
- a UTF-8 BOM: it is bytes in the file and is counted as such; it is not stripped before parsing;
- symlinks, devices, files that change while being read (the census reads the bytes it was given, whatever they are);
- any concurrency, retry, caching or non-local I/O.

## Reporting contract shared by all three

- `path` in every output is the **resolved** absolute path, so a caller can compare it with `Path.resolve()`.
- The installed package must carry its `SKILL.md`; the bundle check reads it from the installed distribution, not from
  the source tree.
- A budget (`--max-steps`) of zero or less reviews nothing and reports `BUDGET`: the limit stopped the run, even though
  the queue is untouched.

## How this is checked

`ts23_build.py` generates the three programs, their tests and the fixtures, then records a RED run (a placeholder that runs
and answers wrongly), installs the packages into a hermetic venv, and records a GREEN run plus an installed-location check.
`ts23_mutation_check.py` then applies one textual substitution at a time to the **installed** source, probes every
invocation the tests use, and counts a mutation as caught only when the program still answers and a test fails on an
assertion that is not a crash. The flags it prints (`all_caught`, `no_false_reds`, `all_restored`, `baseline_all_pass`)
decide its exit code, so a failing receipt cannot look like a passing one.
