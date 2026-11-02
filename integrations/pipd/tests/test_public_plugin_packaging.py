"""Packaging tests for the public Skills-only plugin builder and source freezer.

These tests pin the fail-closed contract of ``tools/build_public_plugin.py`` and
``tools/freeze_public_plugin_source.py``. Every case drives the REAL ``build_plugin(...)`` /
``freeze(...)`` functions (never a re-implementation) and every case runs inside a private
temporary directory: no network, no writes into the repository, nothing under ``dist/`` or
``.hgk/``.

They are also the historical red cases: they were written against the defect where the builder
accepted a ``SKILL.md`` whose frontmatter ``name`` did not match its skill directory (the tool is
fixed here, in ``project_skill_md``), and they pin the digest-pinnable, locally authored
``plugin.schema.json`` subset that the builder validates the manifest with.

The package root is the OFFICIAL Agent Plugins 1.0 manifest (``packaging/public-plugin/plugin.json``
validated against the byte-locked ``vendor-plugin.schema.json``); PIPD's own bookkeeping is
``packaging/public-plugin/plugin.release.json``, embedded verbatim in the manifest's
``extensions["com.pipd.s4"]`` namespace. The vendor's own validator and the Portal scan stay
NOT_EXECUTED.

Symlinks are exercised through the documented ``build_public_plugin._path_is_symlink`` seam when
the host refuses to create a real symlink (unprivileged Windows), so the gate itself is always
executed; where the OS allows the real thing, the real thing is used.
"""
from __future__ import annotations

import contextlib
import functools
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_public_plugin as B  # noqa: E402  (sibling tool, stdlib-only)
import freeze_public_plugin_source as F  # noqa: E402  (sibling tool, stdlib-only)

PACKAGING = ROOT / "packaging" / "public-plugin"
SCHEMA_PATH = PACKAGING / "plugin.schema.json"
CHECKED_IN_MANIFEST = PACKAGING / "plugin.json"
CHECKED_IN_RELEASE = PACKAGING / "plugin.release.json"
VENDOR_SCHEMA_PATH = PACKAGING / "vendor-plugin.schema.json"
# The bytes the round downloaded from the Agent Plugins 1.0 specification. The byte-copy case is
# skipped when the round's evidence tree is absent; the digest assertion always runs.
ROUND_VENDOR_SCHEMA = (ROOT / ".hgk" / "rounds" /
                       "S4POST-20261012-postrepair-recheck-and-triple-upgrade" / "stage-b" /
                       "vendor" / "plugin.schema.json")
VENDOR_SCHEMA_SHA256 = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
GIT = shutil.which("git")

COMMIT = "c" * 40
TREE = "d" * 40
PLUGIN_ID = "pipd-ls-sp-public-skills"
SKILLS = tuple(F.EXPECTED_SKILLS)

# The fixture frontmatter carries both portable and non-portable keys, exactly like the real packs.
APPROVED_KEYS = ("name", "description", "license")
DROPPED_KEYS = ("version", "owner", "triggers", "schemas", "references", "tests")

FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_MODE = 0o644


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def skill_md_text(name: str, *, declared_name: str | None = None) -> str:
    declared = name if declared_name is None else declared_name
    return (
        "---\n"
        f"name: {declared}\n"
        "description: Fixture skill for the public plugin packaging tests.\n"
        "license: Apache-2.0\n"
        "version: 1\n"
        "owner: PIPD-EC (deterministic compiler)\n"
        "triggers:\n"
        "  - fixture trigger\n"
        "schemas:\n"
        "  - schemas/input.schema.json\n"
        "references:\n"
        "  - references/contract.md\n"
        "tests:\n"
        "  - tests/cases.yaml\n"
        "---\n"
        "\n"
        f"# {name}\n"
        "\n"
        "## Contract (imperative)\n"
        "\n"
        "1. Keep the body byte-identical across the frontmatter projection.\n"
        "2. Never let a packaging run touch a real repository tree.\n"
    )


class Env:
    """A throwaway source checkout + packaging root, entirely under one temp directory."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.source = root / "source"
        self.skills = self.source / "skills"
        self.packaging = root / "packaging"
        self.assets = self.packaging / "assets"
        self.out = root / "release"
        for name in SKILLS:
            skill_dir = self.skills / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(skill_md_text(name), encoding="utf-8", newline="")
        self.assets.mkdir(parents=True, exist_ok=True)
        # The real, checked-in local schema subset is what the builder must consume.
        shutil.copyfile(SCHEMA_PATH, self.packaging / "plugin.schema.json")
        # The real, checked-in byte copy of the official vendor schema, too.
        shutil.copyfile(VENDOR_SCHEMA_PATH, self.packaging / "vendor-plugin.schema.json")
        (self.assets / "icon-128.png").write_bytes(B.png_icon_bytes(128))

    @property
    def schema_bytes(self) -> bytes:
        return (self.packaging / "plugin.schema.json").read_bytes()

    @property
    def vendor_bytes(self) -> bytes:
        return (self.packaging / "vendor-plugin.schema.json").read_bytes()

    @property
    def icon_bytes(self) -> bytes:
        return (self.assets / "icon-128.png").read_bytes()

    def freeze(self) -> dict:
        return F.freeze(self.source, require_git=False, commit_override=COMMIT,
                        tree_override=TREE, repo_url_override="FIXTURE_NO_NETWORK")

    def release_doc(self, **overrides) -> dict:
        """PIPD's release bookkeeping: the shape the local ``plugin.schema.json`` subset pins."""
        doc = {
            "schema": B.RELEASE_SCHEMA_ID,
            "plugin_id": PLUGIN_ID,
            "display_name": "PIPD Fixture Public Skills",
            "version": "0.1.1",
            "license": "Apache-2.0",
            "skills": list(SKILLS),
            "official_schema_sha256": sha256(self.vendor_bytes),
            "publisher": {
                "name": "PIPD Owner",
                "identity": "owner@example.invalid",
                "identity_sha256": "f" * 64,
            },
            "icons": [{"path": "assets/icon-128.png", "sha256": sha256(self.icon_bytes),
                       "size": 128}],
            "release": {"claim_ceiling": "LOCAL_PACKAGER_PASS_ONLY",
                        "official_portal_verification": "NOT_EXECUTED"},
        }
        doc.update(overrides)
        return doc

    def official_manifest(self, *, release: dict | None = None, **overrides) -> dict:
        """The official Agent Plugins 1.0 package-root manifest."""
        rel = release if release is not None else self.release_doc()
        doc = {
            "$schema": B.VENDOR_SCHEMA_ID,
            "name": PLUGIN_ID,
            "version": rel["version"],
            "description": "PIPD fixture public Skills-only plugin.",
            "repository": "https://example.invalid/pipd-ls-sp",
            "license": "Apache-2.0",
            "keywords": ["agent-plugins", "skills", "fixture"],
            "extensions": {
                B.RELEASE_EXTENSION_KEY: rel,
                "com.openai": {"interface": {"display_name": "PIPD Fixture Public Skills"}},
            },
        }
        doc.update(overrides)
        return doc

    def write_packaging(self, ledger: dict, *, manifest: dict | None = None,
                        release: dict | None = None, derivations: dict | None = None) -> None:
        rel = release if release is not None else self.release_doc()
        man = manifest if manifest is not None else self.official_manifest(release=rel)
        (self.packaging / "plugin.json").write_bytes(B.canonical_json_bytes(man))
        (self.packaging / "plugin.release.json").write_bytes(B.canonical_json_bytes(rel))
        deriv = derivations if derivations is not None else derivations_doc(ledger)
        (self.packaging / "derivations.json").write_bytes(B.canonical_json_bytes(deriv))

    def write_ledger(self, ledger: dict) -> Path:
        path = self.root / "ledger.json"
        path.write_bytes(B.canonical_json_bytes(ledger))
        return path

    def build(self, ledger: dict, *, source_commit: str | None = COMMIT, **kwargs):
        return B.build_plugin(source_root=self.source, ledger=ledger, source_commit=source_commit,
                              packaging_root=self.packaging, out_dir=self.out, **kwargs)


def derivation_record(ledger: dict, name: str, **overrides) -> dict:
    rel = f"skills/{name}/SKILL.md"
    record = {
        "skill": name,
        "source_path": rel,
        "source_sha256": ledger["files"][rel],
        "kept_keys": list(APPROVED_KEYS),
        "dropped_keys": list(DROPPED_KEYS),
        "approved_by": "owner@example.invalid",
        "approval_receipt": "owner-approval-receipt-20261012-0001",
    }
    record.update(overrides)
    return record


def derivations_doc(ledger: dict, *, overrides: dict[str, dict] | None = None) -> dict:
    overrides = overrides or {}
    return {
        "schema": "PIPD-PUBLIC-PLUGIN-DERIVATIONS/1",
        "derivations": [derivation_record(ledger, name, **overrides.get(name, {}))
                        for name in sorted(SKILLS)],
    }


@contextlib.contextmanager
def temp_env():
    with tempfile.TemporaryDirectory() as tmp:
        yield Env(Path(tmp))


@contextlib.contextmanager
def as_symlink(path: Path, target: Path):
    """Present ``path`` as a symlink to ``target``; fall back to the documented seam.

    The seam (``build_public_plugin._path_is_symlink``) exists precisely so the symlink gates can
    be exercised on hosts that forbid real symlinks. Only the predicate is substituted; every
    other line of the gate is the real, unmodified code.
    """
    try:
        os.symlink(target, path, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError):
        real = B._path_is_symlink
        wanted = Path(path)

        def fake(candidate, _wanted=wanted, _real=real):
            try:
                if Path(candidate) == _wanted:
                    return True
            except TypeError:
                pass
            return _real(candidate)

        B._path_is_symlink = fake
        try:
            yield
        finally:
            B._path_is_symlink = real
    else:
        try:
            yield
        finally:
            try:
                path.unlink()
            except OSError:
                pass


def zip_entries(path: Path) -> tuple[list[zipfile.ZipInfo], dict[str, bytes]]:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        members = {info.filename: archive.read(info.filename) for info in infos}
    return infos, members


class PublicPluginPackagingTest(unittest.TestCase):
    # ------------------------------------------------------------------ helpers
    def assert_refusal(self, code: str, func, *args, **kwargs) -> B.Refusal:
        with self.assertRaises(B.Refusal) as caught:
            func(*args, **kwargs)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return caught.exception

    def assert_no_zip(self, env: Env) -> None:
        if env.out.exists():
            self.assertEqual([p.name for p in env.out.iterdir()], [],
                             "a refused build must not leave anything behind")

    def run_git(self, repo: Path, *args: str) -> str:
        proc = subprocess.run(
            [GIT, "-C", str(repo), "-c", "user.email=fixture@example.invalid",
             "-c", "user.name=packaging-fixture", "-c", "commit.gpgsign=false",
             "-c", "init.defaultBranch=main", *args],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        return proc.stdout

    # ------------------------------------------------------- 0. the schema subset
    def test_00_local_schema_is_a_locally_authored_subset(self) -> None:
        doc = json.loads(SCHEMA_PATH.read_bytes().decode("utf-8"))
        self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(doc["additionalProperties"], False)
        description = doc["description"].upper()
        self.assertIn("LOCALLY AUTHORED SUBSET", description)
        self.assertIn("NOT THE OFFICIAL VENDOR SCHEMA", description)
        self.assertIn("NOT_EXECUTED", description)
        self.assertEqual(sorted(doc["properties"]), sorted([
            "schema", "plugin_id", "display_name", "version", "license", "skills",
            "official_schema_sha256", "publisher", "icons", "release"]))
        # The builder's own validator consumes the subset and accepts PIPD's release bookkeeping
        # (the release document is what the locally authored closed key set still describes)...
        release = json.loads(CHECKED_IN_RELEASE.read_bytes().decode("utf-8"))
        self.assertEqual(B.validate_subset(release, doc), [])
        # ... rejects an unknown key, a ninth skill, and a non-enum skill name.
        self.assertTrue(B.validate_subset({**release, "custom": 1}, doc))
        extra = json.loads(json.dumps(release))
        extra["skills"] = list(SKILLS) + ["pipd-extra-skill"]
        self.assertTrue(B.validate_subset(extra, doc))
        renamed = json.loads(json.dumps(release))
        renamed["skills"] = ["pipd-not-a-skill"] + list(SKILLS)[1:]
        self.assertTrue(B.validate_subset(renamed, doc))

    # --------------------------------------------------------- 1. broken icon data
    def test_01_png_signature_with_broken_body_is_refused(self) -> None:
        fake = B.PNG_SIG + b"garbage-body"
        with temp_env() as env:
            ledger = env.freeze()
            (env.assets / "icon-128.png").write_bytes(fake)
            env.write_packaging(ledger, release=env.release_doc(icons=[
                {"path": "assets/icon-128.png", "sha256": sha256(fake), "size": 128}]))
            exc = self.assert_refusal("ICON_INVALID", env.build, ledger)
            self.assertIn("truncated_chunk", str(exc))
            self.assert_no_zip(env)

    def test_01_non_png_icon_is_refused(self) -> None:
        fake = b"GIF89a this is not a png file\n"
        with temp_env() as env:
            ledger = env.freeze()
            (env.assets / "icon-128.png").write_bytes(fake)
            env.write_packaging(ledger, release=env.release_doc(icons=[
                {"path": "assets/icon-128.png", "sha256": sha256(fake), "size": 128}]))
            exc = self.assert_refusal("ICON_INVALID", env.build, ledger)
            self.assertIn("signature", str(exc))
            self.assert_no_zip(env)

    # ------------------------------------------------------- 2. manifest key set
    def test_02_unknown_manifest_property_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            doc = env.official_manifest()
            doc["custom"] = {"anything": 1}
            env.write_packaging(ledger, manifest=doc)
            exc = self.assert_refusal("MANIFEST_SCHEMA_VIOLATION", env.build, ledger)
            self.assertIn("custom", str(exc))
            self.assert_no_zip(env)

    # --------------------------------------------------------- 3. SKILL frontmatter
    def test_03_skill_without_frontmatter_is_refused(self) -> None:
        with temp_env() as env:
            (env.skills / "pipd-pd-bind" / "SKILL.md").write_text(
                "# pipd-pd-bind\n\nno frontmatter lives here\n", encoding="utf-8", newline="")
            ledger = env.freeze()
            env.write_packaging(ledger, derivations=derivations_doc(
                ledger, overrides={"pipd-pd-bind": {"kept_keys": [], "dropped_keys": []}}))
            self.assert_refusal("SKILL_FRONTMATTER_INVALID", env.build, ledger)
            self.assert_no_zip(env)

    def test_03_skill_with_wrong_frontmatter_name_is_refused(self) -> None:
        with temp_env() as env:
            (env.skills / "pipd-pi-compile" / "SKILL.md").write_text(
                skill_md_text("pipd-pi-compile", declared_name="some-other-skill"),
                encoding="utf-8", newline="")
            ledger = env.freeze()
            env.write_packaging(ledger)
            exc = self.assert_refusal("SKILL_FRONTMATTER_INVALID", env.build, ledger)
            self.assertIn("some-other-skill", str(exc))
            self.assert_no_zip(env)

    # ------------------------------------------------------------ 4. source commit
    def test_04_source_commit_gates(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            self.assert_refusal("SOURCE_COMMIT_NULL", env.build, ledger, source_commit=None)
            self.assert_refusal("SOURCE_COMMIT_INVALID", env.build, ledger, source_commit="abc123")
            self.assert_refusal("SOURCE_COMMIT_MISMATCH", env.build, ledger, source_commit="e" * 40)
            self.assert_no_zip(env)

    # ------------------------------------------------- 5. symlinked output release
    def test_05_symlinked_output_root_is_refused_and_target_untouched(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            target = env.root / "release-target"
            target.mkdir()
            sentinel = target / "SENTINEL.txt"
            sentinel_bytes = b"sentinel bytes that must survive untouched\n"
            sentinel.write_bytes(sentinel_bytes)
            link = env.root / "release-link"
            with as_symlink(link, target):
                env.out = link
                self.assert_refusal("OUTPUT_ROOT_SYMLINK", env.build, ledger)
            self.assertEqual(sentinel.read_bytes(), sentinel_bytes)
            self.assertEqual(sorted(p.name for p in target.iterdir()), ["SENTINEL.txt"])

    # ------------------------------------------------------ 6. source set vs ledger
    def test_06_extra_skill_member_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            (env.skills / "pipd-pd-bind" / "notes.md").write_text(
                "not in the frozen ledger\n", encoding="utf-8", newline="")
            exc = self.assert_refusal("SOURCE_SET_CHANGED", env.build, ledger)
            self.assertIn("notes.md", str(exc))
            self.assert_no_zip(env)

    def test_06_missing_skill_member_is_refused(self) -> None:
        with temp_env() as env:
            (env.skills / "pipd-pd-bind" / "notes.md").write_text(
                "frozen member\n", encoding="utf-8", newline="")
            ledger = env.freeze()
            env.write_packaging(ledger)
            self.assertIn("skills/pipd-pd-bind/notes.md", ledger["files"])
            (env.skills / "pipd-pd-bind" / "notes.md").unlink()
            exc = self.assert_refusal("SOURCE_SET_CHANGED", env.build, ledger)
            self.assertIn("notes.md", str(exc))
            self.assert_no_zip(env)

    # ---------------------------------------------------------- 7. ninth skill dir
    def test_07_ninth_skill_directory_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            ninth = env.skills / "pipd-extra-skill"
            ninth.mkdir()
            (ninth / "SKILL.md").write_text(skill_md_text("pipd-extra-skill"),
                                            encoding="utf-8", newline="")
            exc = self.assert_refusal("UNEXPECTED_SKILL", env.build, ledger)
            self.assertIn("pipd-extra-skill", str(exc))
            self.assert_no_zip(env)

    # ------------------------------------------------- 8. symlink / non-regular member
    def test_08_symlinked_source_member_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            member = env.skills / "pipd-authority-source" / "notes.md"
            member.write_text("payload\n", encoding="utf-8", newline="")
            with as_symlink(member, env.skills / "pipd-authority-source" / "SKILL.md"):
                exc = self.assert_refusal("SOURCE_SYMLINK", env.build, ledger)
            self.assertIn("notes.md", str(exc))
            self.assert_no_zip(env)

    def test_08_non_regular_source_member_is_refused(self) -> None:
        # A non-directory entry where a skill pack is expected.
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            (env.skills / "STRAY_MEMBER.txt").write_text(
                "not a skill directory\n", encoding="utf-8", newline="")
            exc = self.assert_refusal("SOURCE_SPECIAL_MEMBER", env.build, ledger)
            self.assertIn("STRAY_MEMBER.txt", str(exc))
            self.assert_no_zip(env)
        if hasattr(os, "mkfifo"):
            # POSIX only: a FIFO inside a skill is a non-regular source member.
            with temp_env() as env:
                ledger = env.freeze()
                env.write_packaging(ledger)
                os.mkfifo(env.skills / "pipd-pd-bind" / "pipe")
                exc = self.assert_refusal("SOURCE_SPECIAL_MEMBER", env.build, ledger)
                self.assertIn("pipe", str(exc))

    # ------------------------------------------------------- 9. dirty worktree freeze
    @unittest.skipUnless(GIT, "git is required to exercise the real freeze() git gates")
    def test_09_dirty_worktree_at_freeze_time_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            self.run_git(repo, "init", "--quiet")
            (repo / "UNTRACKED.txt").write_text("uncommitted\n", encoding="utf-8")
            with self.assertRaises(F.FreezeRefusal) as caught:
                F.freeze(repo)
            self.assertEqual(caught.exception.code, "DIRTY_WORKTREE")
            self.assertIn("UNTRACKED.txt", str(caught.exception))

    # --------------------------------------------------------- 10. determinism
    def test_10_two_builds_are_byte_identical(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            first = env.build(ledger)
            first_zip = Path(first["out_zip"])
            first_bytes = first_zip.read_bytes()
            first_infos, first_members = zip_entries(first_zip)

            second = B.build_plugin(source_root=env.source, ledger=ledger, source_commit=COMMIT,
                                    packaging_root=env.packaging, out_dir=env.root / "release-2")
            second_zip = Path(second["out_zip"])
            second_bytes = second_zip.read_bytes()
            second_infos, second_members = zip_entries(second_zip)

            self.assertEqual(sha256(first_bytes), first["zip_sha256"])
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(sha256(first_bytes), sha256(second_bytes))
            self.assertEqual(first_members, second_members)
            self.assertEqual([i.filename for i in first_infos],
                             [i.filename for i in second_infos])
            self.assertEqual([i.filename for i in first_infos], sorted(first_members))
            for info in first_infos:
                self.assertEqual(info.date_time, FIXED_DATE_TIME)
                self.assertEqual(info.external_attr >> 16, FIXED_MODE)
                self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)

    # ------------------------------------- 11. missing owner record -> non-zero exit
    def test_11_missing_owner_derivation_is_a_non_zero_exit(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, derivations={
                "schema": "PIPD-PUBLIC-PLUGIN-DERIVATIONS/1", "derivations": []})
            ledger_path = env.write_ledger(ledger)
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                code = B.main(["--source-root", str(env.source), "--ledger", str(ledger_path),
                               "--source-commit", COMMIT, "--packaging-root", str(env.packaging),
                               "--out-dir", str(env.out)])
            printed = captured.getvalue().strip()
            self.assertEqual(printed,
                             "REFUSED OWNER_INPUT_MISSING: "
                             + B.DERIVATION_MISSING_TEMPLATE.format(skill="pipd-assurance-tqaep"))
            self.assertEqual(code, 2)
            self.assertNotEqual(code, 0)
            self.assert_no_zip(env)

    # ------------------------------------------ 12. complete record -> verbatim body
    def test_12_complete_owner_record_builds_and_projects_the_body_verbatim(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            report = env.build(ledger)
            self.assertEqual(report["verdict"], "BUILT")
            infos, members = zip_entries(Path(report["out_zip"]))
            root = PLUGIN_ID

            mapping = json.loads(members[f"{root}/SOURCE_TO_PLUGIN_MAPPING.json"].decode("utf-8"))
            receipt = json.loads(members[f"{root}/RELEASE_RECEIPT.json"].decode("utf-8"))
            self.assertEqual(receipt["claim_ceiling"], "LOCAL_PACKAGER_PASS_ONLY")
            self.assertEqual(receipt["official_portal_verification"], "NOT_EXECUTED")
            rows = {row["source_path"]: row for row in mapping["entries"]}

            for name in SKILLS:
                rel = f"skills/{name}/SKILL.md"
                row = rows[rel]
                self.assertEqual(row["mode"], "DERIVED_WITH_OWNER_APPROVAL")
                self.assertEqual(row["destination_path"], f"{root}/{rel}")
                self.assertEqual(row["source_sha256"], ledger["files"][rel])

                source_bytes = F.canonical_bytes((env.skills / name / "SKILL.md").read_bytes())
                _, source_map, source_body = B.parse_skill_md(source_bytes.decode("utf-8"))
                projected = members[f"{root}/{rel}"]
                _, projected_map, projected_body = B.parse_skill_md(projected.decode("utf-8"))

                # The body survives the projection byte-for-byte; only approved keys move.
                self.assertEqual(projected_body, source_body)
                self.assertEqual(set(projected_map), set(APPROVED_KEYS))
                for key in APPROVED_KEYS:
                    self.assertEqual(projected_map[key], source_map[key])
                for key in DROPPED_KEYS:
                    self.assertNotIn(key, projected_map)
                self.assertEqual(row["destination_sha256"], sha256(projected))

            self.assertEqual(members[f"{root}/plugin.schema.json"], env.schema_bytes)

    # ------------------------------------------- 13. output root overlap / dist
    def test_13_output_root_overlapping_the_repo_or_dist_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            cases = (
                (env.source, "OUTPUT_ROOT_OVERLAPS_REPO"),
                (env.source / "candidate", "OUTPUT_ROOT_OVERLAPS_REPO"),
                (env.root, "OUTPUT_ROOT_OVERLAPS_REPO"),
                (env.source / "dist", "OUTPUT_ROOT_IN_DIST"),
                (env.source / "dist" / "nested", "OUTPUT_ROOT_IN_DIST"),
            )
            for out_dir, code in cases:
                with self.subTest(out_dir=str(out_dir)):
                    call = functools.partial(
                        B.build_plugin, source_root=env.source, ledger=ledger,
                        source_commit=COMMIT, packaging_root=env.packaging, out_dir=out_dir)
                    self.assert_refusal(code, call)
            self.assertFalse((env.source / "dist").exists())

    # --------------------------------------------- 14. owner placeholders refuse
    def test_14_owner_placeholders_are_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, release=env.release_doc(
                official_schema_sha256="OWNER_INPUT_REQUIRED"))
            self.assert_refusal("OWNER_INPUT_MISSING", env.build, ledger)

            env.write_packaging(ledger, release=env.release_doc(publisher={
                "name": "OWNER_INPUT_REQUIRED",
                "identity": "owner@example.invalid",
                "identity_sha256": "f" * 64,
            }))
            self.assert_refusal("OWNER_INPUT_MISSING", env.build, ledger)

            env.write_packaging(ledger, release=env.release_doc(icons=[
                {"path": "assets/icon-128.png", "sha256": "OWNER_INPUT_REQUIRED", "size": 128}]))
            self.assert_refusal("OWNER_INPUT_MISSING", env.build, ledger)
            self.assert_no_zip(env)

    # --------------------------------------- 15. the official manifest vs the vendor schema
    def test_15_official_manifest_validates_against_the_vendor_schema(self) -> None:
        vendor_bytes = VENDOR_SCHEMA_PATH.read_bytes()
        vendor_doc = json.loads(vendor_bytes.decode("utf-8"))
        self.assertEqual(sha256(vendor_bytes), B.VENDOR_SCHEMA_SHA256)
        self.assertEqual(B.VENDOR_SCHEMA_SHA256, VENDOR_SCHEMA_SHA256)
        self.assertEqual(vendor_doc["$id"], B.VENDOR_SCHEMA_ID)
        self.assertEqual(vendor_doc["required"], ["$schema", "name"])
        self.assertIs(vendor_doc["additionalProperties"], False)
        self.assertEqual(sorted(vendor_doc["properties"]), sorted([
            "$schema", "name", "version", "description", "author", "homepage", "repository",
            "license", "keywords", "extensions"]))

        manifest = json.loads(CHECKED_IN_MANIFEST.read_bytes().decode("utf-8"))
        release = json.loads(CHECKED_IN_RELEASE.read_bytes().decode("utf-8"))
        self.assertEqual(manifest["$schema"], vendor_doc["$id"])
        self.assertEqual(B.validate_subset(manifest, vendor_doc), [])
        self.assertEqual(sorted(manifest), sorted([
            "$schema", "name", "version", "description", "repository", "license", "keywords",
            "extensions"]))
        # PIPD's bookkeeping is in the vendor-blessed namespace, embedded verbatim, and pinned.
        self.assertEqual(manifest["extensions"][B.RELEASE_EXTENSION_KEY], release)
        self.assertEqual(release["official_schema_sha256"], B.VENDOR_SCHEMA_SHA256)
        self.assertEqual(release["skills"], list(SKILLS))
        # The closed key set and the extensions object type are enforced, not assumed.
        self.assertTrue(B.validate_subset({**manifest, "plugin_id": "leaked"}, vendor_doc))
        self.assertTrue(B.validate_subset(
            {**manifest, "extensions": {"com.x": "not-an-object"}}, vendor_doc))
        self.assertEqual(B.validate_subset(
            {**manifest, "extensions": {"com.x": {"any": ["object"]}}}, vendor_doc), [])

    @unittest.skipUnless(ROUND_VENDOR_SCHEMA.is_file(),
                         "the round's downloaded vendor schema is not present on this host")
    def test_15_checked_in_vendor_schema_is_a_byte_copy_of_the_downloaded_bytes(self) -> None:
        self.assertEqual(VENDOR_SCHEMA_PATH.read_bytes(), ROUND_VENDOR_SCHEMA.read_bytes())

    # ---------------------------------------- 16. the root manifest is the official one
    def test_16_unknown_top_level_key_in_the_official_manifest_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            doc = env.official_manifest()
            doc["official_schema_sha256"] = "0" * 64  # the shape the old internal manifest had
            env.write_packaging(ledger, manifest=doc)
            exc = self.assert_refusal("MANIFEST_SCHEMA_VIOLATION", env.build, ledger)
            self.assertIn("official_schema_sha256", str(exc))
            self.assertIn("additionalProperties", str(exc))
            self.assert_no_zip(env)

    def test_16_the_previous_internal_manifest_is_refused_as_the_package_root(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            legacy = env.release_doc()
            for doc, code, needle in (
                    (legacy, "OFFICIAL_SCHEMA_ID_MISMATCH", "$schema"),
                    ({**legacy, "$schema": B.VENDOR_SCHEMA_ID},
                     "MANIFEST_SCHEMA_VIOLATION", "required")):
                with self.subTest(code=code):
                    env.write_packaging(ledger, manifest=doc)
                    exc = self.assert_refusal(code, env.build, ledger)
                    self.assertIn(needle, str(exc))
            self.assert_no_zip(env)

    # ------------------------------------------------ 17. the vendor schema lock
    def test_17_pinned_vendor_digest_mismatch_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, release=env.release_doc(
                official_schema_sha256="a" * 64))
            exc = self.assert_refusal("VENDOR_SCHEMA_DIGEST_MISMATCH", env.build, ledger)
            self.assertIn(B.VENDOR_SCHEMA_SHA256, str(exc))
            self.assert_no_zip(env)

            # Unpinned is the pre-existing owner gate; a malformed digest is its own gate.
            env.write_packaging(ledger, release=env.release_doc(
                official_schema_sha256="OWNER_INPUT_REQUIRED"))
            self.assert_refusal("OWNER_INPUT_MISSING", env.build, ledger)
            env.write_packaging(ledger, release=env.release_doc(
                official_schema_sha256="not-a-digest"))
            self.assert_refusal("OFFICIAL_SCHEMA_DIGEST_INVALID", env.build, ledger)
            self.assert_no_zip(env)

    def test_17_locked_vendor_schema_bytes_are_refused_when_they_drift(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            target = env.packaging / "vendor-plugin.schema.json"
            doc = json.loads(target.read_text(encoding="utf-8"))
            doc["description"] = doc["description"] + " (drifted)"
            target.write_bytes(B.canonical_json_bytes(doc))
            exc = self.assert_refusal("VENDOR_SCHEMA_DIGEST_MISMATCH", env.build, ledger)
            self.assertIn("locked digest", str(exc))
            self.assert_no_zip(env)

    def test_17_vendor_schema_id_mismatch_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            target = env.packaging / "vendor-plugin.schema.json"
            doc = json.loads(target.read_text(encoding="utf-8"))
            doc["$id"] = "https://example.invalid/schemas/1.0.0/plugin.schema.json"
            target.write_bytes(B.canonical_json_bytes(doc))
            exc = self.assert_refusal("VENDOR_SCHEMA_ID_MISMATCH", env.build, ledger)
            self.assertIn(B.VENDOR_SCHEMA_ID, str(exc))
            self.assert_no_zip(env)

    # ------------------------------------------------ 18. the vendor name pattern
    def test_18_official_name_violating_the_vendor_pattern_is_refused(self) -> None:
        bad_names = ("PIPD Public Skills", "pipd--ls--sp", "pipd..ls", "-pipd", "pipd-", "PIPD_LS")
        with temp_env() as env:
            ledger = env.freeze()
            for name in bad_names:
                with self.subTest(name=name):
                    env.write_packaging(ledger, manifest=env.official_manifest(name=name))
                    exc = self.assert_refusal("MANIFEST_SCHEMA_VIOLATION", env.build, ledger)
                    self.assertIn("pattern", str(exc))
            self.assert_no_zip(env)
            env.write_packaging(ledger)
            self.assertEqual(env.build(ledger)["verdict"], "BUILT")

    # ---------------------------------- 19. the zip root manifest is the official one
    def test_19_zip_root_plugin_json_is_the_official_shaped_manifest(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            report = env.build(ledger)
            infos, members = zip_entries(Path(report["out_zip"]))
            root = PLUGIN_ID
            vendor_doc = json.loads(VENDOR_SCHEMA_PATH.read_bytes().decode("utf-8"))
            root_manifest = json.loads(members[f"{root}/plugin.json"].decode("utf-8"))

            self.assertEqual(root_manifest["$schema"], B.VENDOR_SCHEMA_ID)
            self.assertEqual(root_manifest["name"], PLUGIN_ID)
            self.assertEqual(B.validate_subset(root_manifest, vendor_doc), [])
            # The internal bookkeeping is NOT at the root: it is namespaced and shipped separately.
            for leaked in ("schema", "plugin_id", "display_name", "skills", "publisher", "icons",
                           "release", "official_schema_sha256"):
                self.assertNotIn(leaked, root_manifest)
            release_member = json.loads(members[f"{root}/plugin.release.json"].decode("utf-8"))
            self.assertEqual(root_manifest["extensions"][B.RELEASE_EXTENSION_KEY], release_member)
            self.assertEqual(release_member["skills"], list(SKILLS))
            self.assertEqual(release_member["official_schema_sha256"], sha256(env.vendor_bytes))
            self.assertIn("com.openai", root_manifest["extensions"])
            self.assertEqual(members[f"{root}/vendor-plugin.schema.json"], env.vendor_bytes)

            # The bookkeeping document still satisfies the local closed-key-set subset.
            subset_doc = json.loads(SCHEMA_PATH.read_bytes().decode("utf-8"))
            self.assertEqual(B.validate_subset(release_member, subset_doc), [])
            # The receipt records the identity of the schema the root manifest was validated with.
            receipt = json.loads(members[f"{root}/RELEASE_RECEIPT.json"].decode("utf-8"))
            self.assertEqual(receipt["official_schema_sha256"], sha256(env.vendor_bytes))
            self.assertEqual(receipt["official_schema_id"], B.VENDOR_SCHEMA_ID)
            self.assertEqual([info.filename for info in infos], sorted(members))


    # ------------------------------------ 18. AO-01: a pre-seeded output member must not be written
    def test_18_preseeded_hardlinked_sidecar_is_refused_and_never_overwritten(self) -> None:
        """AO-01 of the round's independent acceptance challenge, kept as a permanent regression.

        The sidecar/mapping/receipt writes used to go through ``Path.write_bytes``, which opens
        whatever the name already resolves to. A hardlink pre-seeded into the output directory made
        the builder truncate and rewrite a file OUTSIDE it. The independent acceptance officer
        measured exactly that on the unpatched tool; this case keeps the hole closed, and it must
        hold even where the OS refuses to create symlinks (a hardlink is an ordinary regular file).
        """
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            env.out.mkdir(parents=True, exist_ok=True)
            outside = env.root / "OUTSIDE_SENTINEL.txt"
            outside_bytes = b"INDEPENDENT_ACCEPTANCE_SENTINEL_DO_NOT_OVERWRITE\n"
            outside.write_bytes(outside_bytes)
            seeded = env.out / f"{PLUGIN_ID}.zip.sha256"
            try:
                os.link(outside, seeded)
            except (OSError, NotImplementedError, AttributeError) as exc:  # pragma: no cover
                self.skipTest(f"host cannot create a hardlink: {exc}")
            self.assertEqual(seeded.stat().st_ino, outside.stat().st_ino)
            exc = self.assert_refusal("OUTPUT_MEMBER_EXISTS", env.build, ledger)
            self.assertIn(seeded.name, str(exc))
            self.assertEqual(outside.read_bytes(), outside_bytes,
                             "the file behind the pre-seeded hardlink was overwritten")
            # Nothing else may be published either: the refusal happens before the artifact is promoted.
            self.assertNotIn(f"{PLUGIN_ID}.zip", [p.name for p in env.out.iterdir()])
            self.assertEqual([p.name for p in env.out.iterdir()], [seeded.name])

    def test_18_preseeded_artifact_name_is_refused(self) -> None:
        """A pre-existing release artifact name refuses the build before anything is written."""
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            env.out.mkdir(parents=True, exist_ok=True)
            (env.out / f"{PLUGIN_ID}.zip").write_bytes(b"ATTACKER_SUPPLIED_BYTES")
            exc = self.assert_refusal("OUTPUT_ARTIFACT_EXISTS", env.build, ledger)
            self.assertIn(f"{PLUGIN_ID}.zip", str(exc))
            self.assertEqual((env.out / f"{PLUGIN_ID}.zip").read_bytes(), b"ATTACKER_SUPPLIED_BYTES")
            self.assertEqual([p.name for p in env.out.iterdir()], [f"{PLUGIN_ID}.zip"])

    def test_18_preseeded_mapping_member_is_refused_and_rolled_back(self) -> None:
        """A pre-seeded mapping member refuses the build and the partial sidecars are rolled back."""
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            env.out.mkdir(parents=True, exist_ok=True)
            seeded = env.out / "SOURCE_TO_PLUGIN_MAPPING.json"
            seeded.write_bytes(b"ATTACKER_SUPPLIED_MAPPING")
            self.assert_refusal("OUTPUT_MEMBER_EXISTS", env.build, ledger)
            self.assertEqual(seeded.read_bytes(), b"ATTACKER_SUPPLIED_MAPPING")
            self.assertEqual([p.name for p in env.out.iterdir()], ["SOURCE_TO_PLUGIN_MAPPING.json"])


    # ------------------------- 20. the official manifest must BE the release identity (CR-IDENTITY-BIND)
    def test_20_official_name_not_bound_to_the_release_plugin_id_is_refused(self) -> None:
        """A *valid* vendor-shaped name that is not the release identity must be refused.

        The ZIP root directory and the release receipt are named from the release bookkeeping, so an
        official manifest naming a different plugin ships two contradicting identities in one
        artefact. The earlier builder validated the manifest's shape only and accepted this at
        exit 0 (independently reported as CR-IDENTITY-BIND).
        """
        with temp_env() as env:
            ledger = env.freeze()
            doc = env.official_manifest(name="pipd-other-valid-plugin")
            env.write_packaging(ledger, manifest=doc)
            exc = self.assert_refusal("MANIFEST_IDENTITY_MISMATCH", env.build, ledger)
            self.assertIn("pipd-other-valid-plugin", str(exc))
            self.assert_no_zip(env)
            env.write_packaging(ledger)
            self.assertEqual(env.build(ledger)["verdict"], "BUILT")

    def test_20_manifest_version_not_bound_to_the_release_version_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, manifest=env.official_manifest(version="999.0.0"))
            exc = self.assert_refusal("MANIFEST_VERSION_MISMATCH", env.build, ledger)
            self.assertIn("999.0.0", str(exc))
            self.assert_no_zip(env)

    def test_20_manifest_license_not_bound_to_the_release_license_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, manifest=env.official_manifest(license="MIT"))
            exc = self.assert_refusal("MANIFEST_LICENSE_MISMATCH", env.build, ledger)
            self.assertIn("MIT", str(exc))
            self.assert_no_zip(env)

    def test_20_a_release_bookkeeping_without_plugin_id_is_refused(self) -> None:
        with temp_env() as env:
            ledger = env.freeze()
            rel = env.release_doc()
            rel.pop("plugin_id")
            env.write_packaging(ledger, release=rel, manifest=env.official_manifest(release=rel))
            self.assert_refusal("RELEASE_IDENTITY_INVALID", env.build, ledger)
            self.assert_no_zip(env)

    # ------------------------- 20. only reviewed extension namespaces (CR-EXT-UNREVIEWED)
    def test_20_unreviewed_extension_namespace_is_refused(self) -> None:
        """An opaque namespace the vendor schema happily accepts must still be refused.

        The locked vendor schema permits arbitrary object-valued reverse-domain namespaces, so
        without this gate unreviewed content travels in the ZIP at exit 0 (independently reported as
        CR-EXT-UNREVIEWED). The owner derivation records authorize SKILL.md transformations only,
        never manifest namespaces.
        """
        with temp_env() as env:
            ledger = env.freeze()
            doc = env.official_manifest()
            doc["extensions"]["com.ao3.unreviewed"] = {"anything": 1}
            env.write_packaging(ledger, manifest=doc)
            exc = self.assert_refusal("EXTENSION_NAMESPACE_UNREVIEWED", env.build, ledger)
            self.assertIn("com.ao3.unreviewed", str(exc))
            self.assertIn("com.openai", str(exc))
            self.assert_no_zip(env)

    def test_20_removing_a_reviewed_namespace_drops_the_interface_is_refused(self) -> None:
        """`extensions` must stay a non-empty object; an empty one is not a valid public manifest."""
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger, manifest=env.official_manifest(extensions={}))
            self.assert_refusal("MANIFEST_EXTENSIONS_INVALID", env.build, ledger)
            self.assert_no_zip(env)

    def test_20_the_reviewed_namespace_set_is_exactly_what_the_gate_allows(self) -> None:
        """Pin the reviewed set: widening it must be a deliberate, reviewed edit, not a drive-by."""
        self.assertEqual(tuple(B.REVIEWED_EXTENSION_NAMESPACES),
                         ("com.openai", B.RELEASE_EXTENSION_KEY))
        with temp_env() as env:
            ledger = env.freeze()
            env.write_packaging(ledger)
            report = env.build(ledger)
            self.assertEqual(report["verdict"], "BUILT")
            infos, members = zip_entries(Path(report["out_zip"]))
            manifest = json.loads(members[f"{PLUGIN_ID}/plugin.json"].decode("utf-8"))
            self.assertEqual(sorted(manifest["extensions"]),
                             sorted(B.REVIEWED_EXTENSION_NAMESPACES))


if __name__ == "__main__":
    unittest.main()
