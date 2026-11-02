"""Typed failure codes for the 13-command PIPD-EC surface (總藍圖 §5.9.3)."""
from __future__ import annotations


class PipdError(Exception):
    code = "PIPD_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code

    def as_dict(self) -> dict:
        return {"verdict": "FAIL", "code": self.code, "message": self.message}


class InitConflict(PipdError):
    code = "INIT_CONFLICT"


class ProfileStale(PipdError):
    code = "PROFILE_STALE"


class IntakeInvalid(PipdError):
    code = "INTAKE_INVALID"


class AuthorityUnknown(PipdError):
    code = "AUTHORITY_UNKNOWN"


class ProfileVeto(PipdError):
    code = "PROFILE_VETO"


class UnsupportedSurface(PipdError):
    code = "UNSUPPORTED_SURFACE"


class PiSchemaFail(PipdError):
    code = "PI_SCHEMA"


class PiSemanticFail(PipdError):
    code = "PI_SEMANTIC"


class TraceFail(PipdError):
    code = "TRACE_FAIL"


class RepoContextMissing(PipdError):
    code = "REPO_CONTEXT_MISSING"


class StaleProvider(PipdError):
    code = "STALE_PROVIDER"


class EcpPermissionFail(PipdError):
    code = "ECP_PERMISSION"


class EffectUnknown(PipdError):
    code = "EFFECT_UNKNOWN"


class TqTraceFail(PipdError):
    code = "TQ_TRACE"


class TqOracleFail(PipdError):
    code = "TQ_ORACLE"


class TqSodFail(PipdError):
    code = "TQ_SOD"


class ValidationFail(PipdError):
    code = "VALIDATION_FAIL"


class ToolDrift(PipdError):
    code = "TOOL_DRIFT"


class ProjectionLoss(PipdError):
    code = "PROJECTION_LOSS"


class ExportSecretFound(PipdError):
    code = "EXPORT_SECRET_SCAN"


class ExportMemberUnsafe(PipdError):
    """A member of the export file set has an absolute, escaping or ``..`` path.

    R5-WO3 (REQ-PIPD-R5-EXPORT-003): the portable bundle refuses the whole export,
    typing the refusal and writing nothing, rather than shipping a traversing path.
    """
    code = "EXPORT_MEMBER_UNSAFE"


class ExportVerificationFailed(PipdError):
    """The staged bundle failed independent re-verification of its archive.

    R5-WO3: the published bundle is only published after re-opening the archive and
    recomputing every member digest; a mismatch is a typed refusal.
    """
    code = "EXPORT_VERIFY_FAILED"


class DiffIncompatible(PipdError):
    code = "DIFF_INCOMPATIBLE_SCHEMA"


class RepairScopeFail(PipdError):
    code = "REPAIR_SCOPE"


class SelfAcceptForbidden(PipdError):
    code = "REPAIR_SELF_ACCEPT"


class EvidenceGap(PipdError):
    code = "EVIDENCE_GAP"

class IoNotFound(PipdError):
    """An input path could not be read. Typed so the CLI never surfaces a bare traceback."""
    code = "IO_NOT_FOUND"


class ParseInvalid(PipdError):
    """An input file is not parseable JSON. Typed: a caller must be able to branch on this."""
    code = "PARSE_INVALID"


class InputShapeInvalid(PipdError):
    """An input record is missing a field this command requires."""
    code = "INPUT_SHAPE_INVALID"


class UsageInvalid(PipdError):
    """The command line itself was wrong (bad flag, missing argument)."""
    code = "USAGE_INVALID"
