"""Guards the install-route surface: this repository documents THREE routes, not two.

The defect being guarded: the front page and the install SSOT both said "two routes and only two"
(one page even specified it as a requirement) while the repository published a third route -- the
private plugin ZIP `pipd-ls-sp-public-skills.zip` on the `v0.1.1-preview.4` release. A reader was
therefore told that an available, evidence-backed route did not exist, and the two pages contradicted
their own navigation table, plugin-route ceiling row and download instructions.

Three assertions, all offline and deterministic:
  1. no document on this surface still claims the count is two;
  2. the install SSOT names the plugin ZIP route and links its release asset;
  3. the install SSOT's route headings are exactly Route 1, Route 2 and Route 3 -- so adding or losing
     a route without touching the enumeration fails here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SURFACE = [ROOT / "README.md", ROOT / "docs" / "install" / "README.md", ROOT / "docs" / "USER_GUIDE.md"]
FORBIDDEN = [
    "only two routes",
    "two install routes and only two",
    "two routes exist, and only two",
    "install is one of **two routes**",
    "by either route",
    "subordinate to the two routes",
]


def test_no_document_on_this_surface_claims_only_two_routes() -> None:
    for path in SURFACE:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN:
            assert phrase.lower() not in text, f"{path.relative_to(ROOT)} still claims {phrase!r}"


def test_install_page_names_the_plugin_zip_route_and_its_release_asset() -> None:
    text = (ROOT / "docs" / "install" / "README.md").read_text(encoding="utf-8")
    assert "pipd-ls-sp-public-skills.zip" in text
    assert "releases/download/v0.1.1-preview.4/pipd-ls-sp-public-skills.zip" in text


def test_route_headings_are_numbered_one_to_three() -> None:
    text = (ROOT / "docs" / "install" / "README.md").read_text(encoding="utf-8")
    numbers = [int(m.group(1)) for m in re.finditer(r"^## Route (\d+) ", text, re.M)]
    assert numbers == [1, 2, 3], f"install page route headings are {numbers}, expected [1, 2, 3]"
