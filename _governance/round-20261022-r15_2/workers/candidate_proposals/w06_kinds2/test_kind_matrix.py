"""Tests for the M03 kind matrix candidate (Q1b).

The candidate module is loaded by file path rather than imported as
``sbl_core.m03_routing``: the point of these tests is to exercise the
*proposal* as written, without first applying it over the live tree. The
round tree's ``sbl_core`` package is still imported so that ``SpecAtom``,
``RouteDecision`` and ``SBLError`` are the real types the candidate binds to.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

WORK_DIR = pathlib.Path(__file__).resolve().parent
ROUND_ROOT = WORK_DIR.parents[3]
CANDIDATE_PATH = WORK_DIR / "m03_routing.candidate.py"
MATRIX_PATH = WORK_DIR / "kind_matrix.json"

if str(ROUND_ROOT) not in sys.path:
    sys.path.insert(0, str(ROUND_ROOT))

from sbl_core.dto import SpecAtom, atom_id_for  # noqa: E402
from sbl_core.errors import SBLError  # noqa: E402


def _load_candidate():
    # The candidate uses relative imports (``from .dto import ...``), so it has
    # to be loaded *as a submodule of the real sbl_core package* rather than as
    # a free-standing module; only then do its sibling imports resolve to the
    # round tree's frozen DTOs and errors.
    spec = importlib.util.spec_from_file_location(
        "sbl_core.m03_routing_candidate", CANDIDATE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def m03():
    return _load_candidate()


@pytest.fixture(scope="module")
def matrix_rows(m03):
    return m03.GovernedRouting().kind_matrix()


@pytest.fixture()
def atom():
    return SpecAtom(atom_id_for("t"), "t", "x.md#L1")


def _resolve(module, attr, default):
    """Read a constant from the candidate, or fall back to its literal default.

    The candidate declares SUPPORTED/DEFERRED/UNSUPPORTED at module level. The
    fallback keeps these tests honest if the proposal is ever trimmed.
    """

    return getattr(module, attr, default)


# ------------------------------------------------------- disposition coverage


def test_canonical_denominator_is_eight(m03):
    """DOC-01 names eight ProductKinds; a ninth canonical kind would silently move the denominator."""

    assert len(m03.CANONICAL_KINDS) == 8
    assert len(set(m03.CANONICAL_KINDS)) == 8


def test_every_canonical_kind_has_a_disposition(m03, matrix_rows):
    covered = {row["kind"] for row in matrix_rows}
    assert covered == set(m03.CANONICAL_KINDS)
    for row in matrix_rows:
        assert row["disposition"] in {"SUPPORTED", "DEFERRED", "UNSUPPORTED"}, row
        assert row["reason"].strip(), f"{row['kind']} has no reason"
        assert row["code_ref"].strip(), f"{row['kind']} has no code_ref"


def test_matrix_json_matches_the_module(m03, matrix_rows):
    """The checked-in kind_matrix.json must be a readback of the code, not a hand-written copy."""

    payload = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    assert payload["rows"] == matrix_rows
    assert payload["canonical_count"] == len(m03.CANONICAL_KINDS)


def test_supported_kinds_have_a_target(m03):
    routing = m03.GovernedRouting()
    for kind in m03.CANONICAL_KINDS:
        if routing.disposition(kind) == _resolve(m03, "SUPPORTED", "SUPPORTED"):
            assert routing.policy.get(kind), f"{kind} is SUPPORTED but has no target"


def test_only_supported_kinds_have_a_target(m03):
    """A target on a deferred or unsupported kind is a permission the disposition denies."""

    routing = m03.GovernedRouting()
    for kind in m03.CANONICAL_KINDS:
        if routing.disposition(kind) != _resolve(m03, "SUPPORTED", "SUPPORTED"):
            assert routing.policy.get(kind) is None, kind


def test_undeclared_kind_defaults_to_unsupported(m03):
    assert m03.GovernedRouting().disposition("NOT_A_KIND") == _resolve(
        m03, "UNSUPPORTED", "UNSUPPORTED"
    )


# ------------------------------------------------------------- fail-closed


@pytest.mark.parametrize("kind", ["SIMPLE_AGENT", "PLUGIN", "PROFILE"])
def test_deferred_kind_fails_closed(m03, atom, kind):
    with pytest.raises(SBLError) as caught:
        m03.GovernedRouting().route(atom, kind)
    assert caught.value.code == "SBL_E_DEFERRED_KIND"
    assert caught.value.detail["disposition"] == "DEFERRED"
    assert caught.value.detail["kind"] == kind


@pytest.mark.parametrize("kind", ["AGENT_OS", "AI_SYSTEM", "GENIE/GENIE.md"])
def test_unsupported_kind_fails_closed(m03, atom, kind):
    with pytest.raises(SBLError) as caught:
        m03.GovernedRouting().route(atom, kind)
    assert caught.value.code == "SBL_E_PROHIBITED_KIND"
    assert caught.value.detail["disposition"] == "UNSUPPORTED"


@pytest.mark.parametrize(
    "kind", ["SIMPLE_AGENT", "PLUGIN", "PROFILE", "AGENT_OS", "AI_SYSTEM", "GENIE/GENIE.md"]
)
def test_refused_kinds_produce_no_route_decision(m03, atom, kind):
    """Refusal must happen before a RouteDecision exists, so nothing reads as permission."""

    with pytest.raises(SBLError):
        m03.GovernedRouting().route(atom, kind)


def test_retired_alias_is_not_routed(m03, atom):
    """"SKILL" was the old spelling of AGENT_SKILL; it must fail as unknown, not route under a contract-absent name."""

    with pytest.raises(SBLError) as caught:
        m03.GovernedRouting().route(atom, "SKILL")
    assert caught.value.code == "SBL_E_UNKNOWN_KIND"


def test_unknown_kind_is_not_silently_deferred(m03, atom):
    with pytest.raises(SBLError) as caught:
        m03.GovernedRouting().route(atom, "MAGIC")
    assert caught.value.code == "SBL_E_UNKNOWN_KIND"


# --------------------------------------------------------- supported unchanged


def test_supported_kinds_still_route_as_before(m03, atom):
    routing = m03.GovernedRouting()

    cli = routing.route(atom, "CLI_TOOL")
    assert cli.permitted is True
    assert cli.target == "SBLM04_GOVERNED_BUILD_BRIDGE"
    assert cli.atom_id == atom.atom_id
    assert cli.reason == "CLI_TOOL_ROUTED"

    skill = routing.route(atom, "AGENT_SKILL")
    assert skill.permitted is True
    assert skill.target == "GJ03_SKILL_AGENT_BRIDGE"
    assert skill.reason == "AGENT_SKILL_ROUTED"


def test_brown_patch_route_survives_but_is_not_canonical(m03, atom):
    """GJ02's existing-repo patch route must keep working without inflating the eight-kind denominator."""

    assert "BROWN_PATCH" not in m03.CANONICAL_KINDS
    decision = m03.GovernedRouting().route(atom, "BROWN_PATCH")
    assert decision.target == "SBLM04_GOVERNED_BUILD_BRIDGE"


def test_injected_policy_can_retarget_a_declared_kind(m03, atom):
    """An injected policy still overrides the target of a kind that has a disposition."""

    routing = m03.GovernedRouting(policy={"CLI_TOOL": "OTHER_TARGET"})
    assert routing.route(atom, "CLI_TOOL").target == "OTHER_TARGET"


def test_injected_policy_cannot_open_an_undeclared_kind(m03, atom):
    """Behaviour change vs. the baseline, asserted deliberately.

    In the baseline, adding a key to the injected policy was enough to route it:
    ``kind not in self.policy`` was the only gate. The candidate gates on the
    *disposition* as well, and ``disposition()`` defaults to UNSUPPORTED, so a
    policy entry alone no longer opens a kind. Opening a kind now requires a
    disposition, which is the governance property the proposal is aiming for.
    """

    routing = m03.GovernedRouting(policy={"ONLY": "T"})
    assert routing.disposition("ONLY") == "UNSUPPORTED"
    with pytest.raises(SBLError) as caught:
        routing.route(atom, "ONLY")
    assert caught.value.code == "SBL_E_PROHIBITED_KIND"


def test_injected_policy_cannot_bypass_a_deferral(m03, atom):
    """Handing a deferred kind a target must not make it routable."""

    routing = m03.GovernedRouting(policy={"PLUGIN": "SOME_TARGET"})
    with pytest.raises(SBLError) as caught:
        routing.route(atom, "PLUGIN")
    assert caught.value.code == "SBL_E_DEFERRED_KIND"

