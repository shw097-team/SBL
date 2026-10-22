class HGKError(RuntimeError):
    """Base typed rejection."""


class InvariantViolation(HGKError):
    """A canonical invariant would be broken."""


class AdmissionDenied(HGKError):
    """A Harness admission check rejected an action."""


class StaleState(HGKError):
    """Optimistic version or source freshness check failed."""


class LeaseConflict(HGKError):
    """A second writer attempted to own the same object."""


class GroundingFailure(HGKError):
    """No sufficient canonical grounding was available."""

