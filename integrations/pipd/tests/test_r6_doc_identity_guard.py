"""F-R6-01: one doc-link / release-identity guard for the install page and the user guide.

The defect being guarded: the published ``v0.1.1-preview.4`` release serves a
``PIPD_WEB_FALLBACK.md`` whose own header still declares the earlier ``v0.1.1-preview.3``
provenance (``release_commit: cbf69756...``) -- a real, frozen provenance drift in an immutable
release. Around that fact the install page pins a generation and points a reader at a mount pack,
and both pages carry in-page anchor links; nothing in the tree checked, as a single check, that the
prose never mixes two releases, that every build example names one generation whose pack really
exists, that no phantom ``dist/mount/`` directory is cited, that every in-page anchor resolves, that
every outgoing relative link resolves to a file that is really there, and
that the user guide's ``S4_FULL_PASS`` ceiling stays honest.

The mutation cases exist so this guard is falsifiable -- a guard that cannot fail is not evidence.
Checks 1 through 4 are each also run against a deliberately mutated copy of the document (written
into a ``tempfile.TemporaryDirectory()``) and asserted to FAIL, so a regression that neuters a check
is caught rather than silently passing. The checking logic lives in module-level pure functions so
the tests can call it on either the real file or a mutated copy.

Derived, not hand-written: the preview.3 target commit is read out of ``docs/RELEASE_TUPLE.json``
and the existing ``dist/mount/`` set is resolved from git at HEAD, exactly as
``test_r5r3_install_route_identity`` re-derives tag facts from git instead of hard-coding them.
Only the tag names are hard-coded. Pure stdlib + ``unittest``; no network.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:  # every test file bootstraps src/ (tests/test_tooling_executes.py)
    sys.path.insert(0, str(SRC))
INSTALL_REL = "docs/install/README.md"
USER_GUIDE_REL = "docs/USER_GUIDE.md"
INSTALL = ROOT / INSTALL_REL
USER_GUIDE = ROOT / USER_GUIDE_REL
TUPLE = ROOT / "docs" / "RELEASE_TUPLE.json"

PREVIEW3 = "v0.1.1-preview.3"
PREVIEW4 = "v0.1.1-preview.4"
GEN_RE = re.compile(r"v\d+\.\d+\.\d+-preview\.\d+")


def _generation(value: str) -> str | None:
    m = GEN_RE.search(value or "")
    return m.group(0) if m else None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def preview3_target_commit() -> str:
    """The preview.3 target commit, READ from the tuple rather than hard-coded here."""
    data = json.loads(read_text(TUPLE))
    entry = next(r for r in data["releases"] if r["release_id"] == PREVIEW3)
    return entry["release_tag_target"]


def _tuple_commit_generations() -> dict[str, set[str]]:
    """Map each commit the tuple names to the generation(s) that name it."""
    data = json.loads(read_text(TUPLE))
    mapping: dict[str, set[str]] = {}
    for rel in data["releases"]:
        gen = _generation(rel["release_id"])
        for commit in (rel.get("release_tag_target"), rel.get("build_source_commit")):
            if commit:
                mapping.setdefault(commit, set()).add(gen)
    return mapping


def paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def fenced_blocks(text: str) -> list[dict]:
    """Every fenced code block, with the 1-based line of its opening fence."""
    lines = text.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```"):
            lang = lines[i].strip()[3:].strip()
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            blocks.append({
                "lang": lang,
                "line": i + 1,
                "body_index": (i, min(j, len(lines) - 1)),
                "text": "\n".join(lines[i + 1:j]),
            })
            i = j + 1
        else:
            i += 1
    return blocks


def _neighbour_prose(text: str, body_index: tuple[int, int]) -> str:
    """The prose paragraph immediately before the block plus the one immediately after."""
    lines = text.splitlines()
    start, end = body_index
    before: list[str] = []
    k = start - 1
    while k >= 0 and lines[k].strip() and not lines[k].lstrip().startswith("```"):
        before.insert(0, lines[k])
        k -= 1
    after: list[str] = []
    k = end + 1
    while k < len(lines) and lines[k].strip() and not lines[k].lstrip().startswith("```"):
        after.append(lines[k])
        k += 1
    return "\n".join(before + after)


def _exists_at_head(repo_root: Path, rel: str) -> bool:
    """True when ``rel`` (a file or a directory) is present in the tree at HEAD."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root).replace("\\", "/"), "cat-file", "-e", f"HEAD:{rel}"],
            capture_output=True, text=True,
        )
    except OSError:
        return (repo_root / rel).exists()
    if proc.returncode == 0:
        return True
    if "not a git repository" in (proc.stderr or "").lower():
        return (repo_root / rel).exists()
    return False


def check_no_cross_release_mixing(text: str, preview3_commit: str) -> list[str]:
    """1. No paragraph may mix the preview.4 release id with the preview.3 target commit
    unless it explicitly marks that commit as preview.3 (``preview.3`` or ``preview. 3``)."""
    problems: list[str] = []
    for index, para in enumerate(paragraphs(text)):
        if PREVIEW4 in para and preview3_commit in para:
            low = para.lower()
            if "preview.3" not in low and "preview. 3" not in low:
                problems.append(
                    f"{INSTALL_REL} paragraph {index} names {PREVIEW4} together with the preview.3 "
                    f"target commit {preview3_commit} without marking it preview.3"
                )
    return problems


def _clip_optional(body: str, name: str) -> str | None:
    m = re.search(rf"--{re.escape(name)}\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))", body)
    if not m:
        return None
    return next(g for g in m.groups() if g is not None)


def check_build_examples(text: str, repo_root: Path) -> list[str]:
    """2. Every ```bash example that contains ``--release-id`` must name one generation, and any
    ``--mount-pack`` path it gives must exist at HEAD or the block must be labelled legacy/historical
    in the surrounding prose."""
    problems: list[str] = []
    commit_gen = _tuple_commit_generations()
    for block in fenced_blocks(text):
        if block["lang"] not in ("bash", "sh", "") or "--release-id" not in block["text"]:
            continue
        line = block["line"]
        body = block["text"]
        release_id = _clip_optional(body, "release-id")
        mount_pack = _clip_optional(body, "mount-pack")
        release_commit = _clip_optional(body, "release-commit")

        rid_gen = _generation(release_id or "")
        if rid_gen is None:
            problems.append(f"{INSTALL_REL} line {line}: --release-id value {release_id!r} names no "
                            f"vX.Y.Z-preview.N generation")
            continue

        generations = {rid_gen}
        if mount_pack is not None:
            mp_gen = _generation(mount_pack)
            if mp_gen is not None:
                generations.add(mp_gen)
        if release_commit is not None:
            for gen in commit_gen.get(release_commit, set()):
                generations.add(gen)
        if len(generations) != 1:
            problems.append(
                f"{INSTALL_REL} line {line}: build example names more than one release generation "
                f"{sorted(generations)} (--release-id {release_id!r}, --mount-pack {mount_pack!r}, "
                f"--release-commit {release_commit!r})"
            )

        if mount_pack is not None and not _exists_at_head(repo_root, mount_pack):
            prose = (_neighbour_prose(text, block["body_index"]) + "\n" + body).lower()
            if "legacy" not in prose and "historical" not in prose:
                problems.append(
                    f"{INSTALL_REL} line {line}: --mount-pack {mount_pack!r} does not exist at HEAD "
                    f"and the block is not labelled legacy/historical in the surrounding prose"
                )
    return problems


def check_no_phantom_pack(text: str, repo_root: Path) -> list[str]:
    """3. No reference to a ``dist/mount/`` entry that does not exist at HEAD."""
    problems: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"dist/mount/[^\s`'\"()\[\]<>]+", text):
        ref = m.group(0).rstrip(".,;:")
        segment = ref.split("dist/mount/", 1)[1].split("/", 1)[0]
        if not segment or segment in seen:
            continue
        seen.add(segment)
        if not _exists_at_head(repo_root, f"dist/mount/{segment}"):
            problems.append(f"{INSTALL_REL} references dist/mount/{segment}, which does not exist at HEAD")
    return problems


def slugify(heading: str) -> str:
    """GitHub's heading-slug rule: lowercase, drop anything not alphanumeric/space/hyphen,
    then spaces to hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return s.replace(" ", "-")


def check_anchors_resolve(text: str, rel: str) -> list[str]:
    """4. Every markdown link of the form ``](#fragment)`` inside the file resolves to a heading."""
    slugs = {slugify(m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.*)$", text, re.M)}
    problems: list[str] = []
    for m in re.finditer(r"\]\(#([^)\s]+)\)", text):
        fragment = m.group(1)
        if fragment not in slugs:
            problems.append(f"{rel} in-page anchor {fragment!r} resolves to no heading")
    return problems


def check_outgoing_links_resolve(text: str, rel: str, repo_root: Path) -> list[str]:
    """6. Every relative markdown link target must resolve to something present at HEAD.

    The defect being guarded: the install page told a reader that the release's identities live in
    ``docs/RELEASE_TUPLE.json`` and linked it as ``](RELEASE_TUPLE.json)`` -- which, relative to
    ``docs/install/``, is ``docs/install/RELEASE_TUPLE.json``, a path that does not exist. The
    documented route pointed at nothing, and the in-page anchor check (4) could not see it because
    an anchor and an outgoing path are different link kinds. External URLs, in-page anchors and
    absolute paths are out of scope here; a target that escapes the repository root is a problem.
    """
    problems: list[str] = []
    base = os.path.dirname(rel)
    for m in re.finditer(r"\]\(([^)\s]+)\)", text):
        target = m.group(1).split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "/", "<")):
            continue
        resolved = os.path.normpath(os.path.join(base, target)).replace("\\", "/")
        if resolved.startswith(".."):
            problems.append(f"{rel}: link target {target!r} escapes the repository root")
            continue
        if not _exists_at_head(repo_root, resolved):
            problems.append(
                f"{rel}: link target {target!r} resolves to {resolved}, which does not exist at HEAD"
            )
    return problems


def check_user_guide_ceilings(text: str) -> list[str]:
    """5. The user guide keeps ``S4_FULL_PASS`` as ``NOT_GRANTED`` and no longer carries the
    preview.3-era ``Merge and release are HOLD`` wording."""
    problems: list[str] = []
    if "S4_FULL_PASS" not in text or "NOT_GRANTED" not in text:
        problems.append(f"{USER_GUIDE_REL} must keep S4_FULL_PASS as NOT_GRANTED")
    else:
        for para in paragraphs(text):
            if "S4_FULL_PASS" in para and "NOT_GRANTED" not in para:
                problems.append(f"{USER_GUIDE_REL} mentions S4_FULL_PASS without NOT_GRANTED in the "
                                f"same paragraph")
    if re.search(r"Merge and release are\s+HOLD", text):
        problems.append(f"{USER_GUIDE_REL} still carries the 'Merge and release are HOLD' wording")
    return problems


class RealDocumentsPassTests(unittest.TestCase):
    """The checks all pass against the documents as committed."""

    def test_1_no_cross_release_mixing(self) -> None:
        self.assertEqual(
            check_no_cross_release_mixing(read_text(INSTALL), preview3_target_commit()), [])

    def test_2_every_build_example_names_one_generation(self) -> None:
        self.assertEqual(check_build_examples(read_text(INSTALL), ROOT), [])

    def test_3_no_phantom_pack(self) -> None:
        self.assertEqual(check_no_phantom_pack(read_text(INSTALL), ROOT), [])

    def test_4_in_page_anchors_resolve(self) -> None:
        self.assertEqual(check_anchors_resolve(read_text(INSTALL), INSTALL_REL), [])
        self.assertEqual(check_anchors_resolve(read_text(USER_GUIDE), USER_GUIDE_REL), [])

    def test_5_user_guide_ceilings_stay_honest(self) -> None:
        self.assertEqual(check_user_guide_ceilings(read_text(USER_GUIDE)), [])

    def test_6_outgoing_links_resolve(self) -> None:
        self.assertEqual(
            check_outgoing_links_resolve(read_text(INSTALL), INSTALL_REL, ROOT), [])
        self.assertEqual(
            check_outgoing_links_resolve(read_text(USER_GUIDE), USER_GUIDE_REL, ROOT), [])


class MutationsAreCaughtTests(unittest.TestCase):
    """Each check is falsifiable: a mutated copy in a temp dir must make its check FAIL."""

    def _mutate(self, original: str, mutated: str, check) -> list[str]:
        self.assertNotEqual(mutated, original, "the mutation fixture no longer matches the document")
        with tempfile.TemporaryDirectory(prefix="pipd_r6_guard_") as tmp:
            path = Path(tmp) / "mutated.md"
            path.write_text(mutated, encoding="utf-8")
            return check(path.read_text(encoding="utf-8"))

    def test_mutation_1_preview3_commit_in_a_preview4_paragraph_is_caught(self) -> None:
        """Swap the preview.4 target commit for the preview.3 one inside the version-pin bullet
        (which has no preview.3 marking): the paragraph now mixes the two releases."""
        original = read_text(INSTALL)
        mutated = original.replace(
            "dereferences to target commit `cc6c1930765160697e7e51d6e37735b9220a30db`",
            f"dereferences to target commit `{preview3_target_commit()}`",
            1,
        )
        problems = self._mutate(
            original, mutated, lambda t: check_no_cross_release_mixing(t, preview3_target_commit()))
        self.assertTrue(problems, "the cross-release mixing check passed a mixed paragraph")

    def test_mutation_2_generation_mismatch_in_a_build_block_is_caught(self) -> None:
        """Point ``--mount-pack`` at a preview.4 directory while ``--release-id`` stays preview.3:
        the block now names two generations."""
        original = read_text(INSTALL)
        mutated = original.replace(
            "dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.3",
            "dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.4",
            1,
        )
        problems = self._mutate(original, mutated, lambda t: check_build_examples(t, ROOT))
        self.assertTrue(problems, "the build-example check passed a mixed-generation block")

    def test_mutation_3_phantom_mount_dir_is_caught(self) -> None:
        """Cite a ``dist/mount/`` directory that does not exist at HEAD."""
        original = read_text(INSTALL)
        mutated = original.replace(
            "dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.3",
            "dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.4",
            1,
        )
        problems = self._mutate(original, mutated, lambda t: check_no_phantom_pack(t, ROOT))
        self.assertTrue(problems, "the phantom-pack check accepted a missing dist/mount/ directory")

    def test_mutation_4_dangling_anchor_is_caught(self) -> None:
        """Delete a heading that an in-page anchor points at."""
        original = read_text(INSTALL)
        mutated = original.replace("## States that are NOT the same\n", "", 1)
        problems = self._mutate(
            original, mutated, lambda t: check_anchors_resolve(t, INSTALL_REL))
        self.assertTrue(problems, "the anchor check accepted a dangling #states-that-are-not-the-same")

    def test_mutation_6_unresolvable_outgoing_link_is_caught(self) -> None:
        """Re-break the outgoing link exactly as it was found in the tree: a target written as if it
        resolved from the repository root when it actually resolves from ``docs/install/``."""
        original = read_text(INSTALL)
        mutated = original.replace("](../RELEASE_TUPLE.json)", "](RELEASE_TUPLE.json)", 1)
        self.assertNotEqual(mutated, original, "the mutation fixture no longer matches the document")
        problems = self._mutate(
            original, mutated, lambda t: check_outgoing_links_resolve(t, INSTALL_REL, ROOT))
        self.assertTrue(problems, "the outgoing-link check accepted a target that resolves to nothing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
