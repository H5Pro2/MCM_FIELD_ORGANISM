"""Static execution decomposition for the unfinished W7-AN container."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json


class W7ANExecutionDecompositionError(ValueError):
    """Raised when the W7-AN execution inventory is inconsistent."""


_PLAN_ID = "w7an.r124-execution-decomposition.v1"
_RESOLUTIONS = (("r1", 1), ("r2", 2), ("r4", 4))
_PHASES = (
    ("cap-canonical", 67),
    ("cap-path-order-control", 67),
    ("cap-branch-order-control", 4),
    ("measurement-canonical", 35),
    ("measurement-order-control", 35),
    ("observer-passivity-control", 1),
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _batch_payload(
    batch_id: str,
    pass_id: str,
    resolution_id: str,
    refinement: int,
    phase: str,
    integration_count: int,
    retained_witness_count: int,
) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "pass_id": pass_id,
        "resolution_id": resolution_id,
        "refinement": refinement,
        "phase": phase,
        "integration_count": integration_count,
        "retained_witness_count": retained_witness_count,
    }


@dataclass(frozen=True, slots=True)
class W7ANExecutionBatch:
    """One bounded static batch; it does not execute a runtime."""

    batch_id: str
    pass_id: str
    resolution_id: str
    refinement: int
    phase: str
    integration_count: int
    retained_witness_count: int
    batch_digest: str

    def __post_init__(self) -> None:
        expected_count = dict(_PHASES).get(self.phase)
        if (
            self.pass_id not in {"primary", "reverse-repeat"}
            or (self.resolution_id, self.refinement) not in _RESOLUTIONS
            or expected_count is None
            or self.integration_count != expected_count
            or isinstance(self.integration_count, bool)
            or self.integration_count < 1
            or isinstance(self.retained_witness_count, bool)
            or self.retained_witness_count < 0
            or self.retained_witness_count > self.integration_count
        ):
            raise W7ANExecutionDecompositionError(
                "execution batch inventory is invalid"
            )
        expected_witnesses = (
            self.integration_count
            if self.pass_id == "primary"
            and self.phase in {"cap-canonical", "measurement-canonical"}
            else 0
        )
        expected_id = (
            f"{self.pass_id}.{self.resolution_id}.{self.phase}"
        )
        payload = _batch_payload(
            self.batch_id,
            self.pass_id,
            self.resolution_id,
            self.refinement,
            self.phase,
            self.integration_count,
            self.retained_witness_count,
        )
        if (
            self.batch_id != expected_id
            or self.retained_witness_count != expected_witnesses
            or self.batch_digest != _digest(payload)
        ):
            raise W7ANExecutionDecompositionError(
                "execution batch binding differs"
            )


def _build_batch(
    pass_id: str,
    resolution_id: str,
    refinement: int,
    phase: str,
    integration_count: int,
) -> W7ANExecutionBatch:
    batch_id = f"{pass_id}.{resolution_id}.{phase}"
    witness_count = (
        integration_count
        if pass_id == "primary"
        and phase in {"cap-canonical", "measurement-canonical"}
        else 0
    )
    payload = _batch_payload(
        batch_id,
        pass_id,
        resolution_id,
        refinement,
        phase,
        integration_count,
        witness_count,
    )
    return W7ANExecutionBatch(
        batch_id,
        pass_id,
        resolution_id,
        refinement,
        phase,
        integration_count,
        witness_count,
        _digest(payload),
    )


def _plan_payload(
    batches: tuple[W7ANExecutionBatch, ...],
) -> dict[str, object]:
    return {
        "plan_id": _PLAN_ID,
        "batch_digests": tuple(item.batch_digest for item in batches),
        "primary_integration_count": 627,
        "repeat_integration_count": 627,
        "total_integration_count": 1254,
        "retained_witness_count": 306,
        "validation_integration_count": 948,
        "maximum_batch_integration_count": 67,
        "runtime_executed": False,
        "container_completed": False,
    }


@dataclass(frozen=True, slots=True)
class W7ANExecutionDecomposition:
    """Bounded primary and reverse-repeat inventory for W7-AN."""

    plan_id: str
    batches: tuple[W7ANExecutionBatch, ...] = field(repr=False)
    primary_integration_count: int
    repeat_integration_count: int
    total_integration_count: int
    retained_witness_count: int
    validation_integration_count: int
    maximum_batch_integration_count: int
    runtime_executed: bool
    container_completed: bool
    execution_decomposition_digest: str

    def __post_init__(self) -> None:
        batches = tuple(self.batches)
        expected_roles = tuple(
            (pass_id, resolution_id, refinement, phase)
            for pass_id, resolutions in (
                ("primary", _RESOLUTIONS),
                ("reverse-repeat", tuple(reversed(_RESOLUTIONS))),
            )
            for resolution_id, refinement in resolutions
            for phase, _ in _PHASES
        )
        actual_roles = tuple(
            (
                item.pass_id,
                item.resolution_id,
                item.refinement,
                item.phase,
            )
            for item in batches
        )
        if (
            self.plan_id != _PLAN_ID
            or actual_roles != expected_roles
            or self.primary_integration_count != 627
            or self.repeat_integration_count != 627
            or self.total_integration_count != 1254
            or self.retained_witness_count != 306
            or self.validation_integration_count != 948
            or self.maximum_batch_integration_count != 67
            or self.runtime_executed is not False
            or self.container_completed is not False
        ):
            raise W7ANExecutionDecompositionError(
                "execution decomposition inventory differs"
            )
        if (
            sum(item.integration_count for item in batches[:18]) != 627
            or sum(item.integration_count for item in batches[18:]) != 627
            or sum(item.retained_witness_count for item in batches) != 306
            or max(item.integration_count for item in batches) != 67
        ):
            raise W7ANExecutionDecompositionError(
                "execution decomposition totals differ"
            )
        payload = _plan_payload(batches)
        if self.execution_decomposition_digest != _digest(payload):
            raise W7ANExecutionDecompositionError(
                "execution decomposition digest differs"
            )
        object.__setattr__(self, "batches", batches)


def build_w7an_execution_decomposition() -> W7ANExecutionDecomposition:
    """Build the static plan without running CAP, P0, or any test world."""

    batches = tuple(
        _build_batch(pass_id, resolution_id, refinement, phase, count)
        for pass_id, resolutions in (
            ("primary", _RESOLUTIONS),
            ("reverse-repeat", tuple(reversed(_RESOLUTIONS))),
        )
        for resolution_id, refinement in resolutions
        for phase, count in _PHASES
    )
    payload = _plan_payload(batches)
    return W7ANExecutionDecomposition(
        _PLAN_ID,
        batches,
        627,
        627,
        1254,
        306,
        948,
        67,
        False,
        False,
        _digest(payload),
    )
