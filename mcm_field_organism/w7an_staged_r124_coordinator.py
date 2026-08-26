"""Private primary/reverse-repeat coordinator for staged W7-AN execution."""

from __future__ import annotations

from dataclasses import dataclass

from .w7an_r124_resolution_container import (
    _P0_REFERENCE_DIGEST,
    _digest,
    _finalize_w7an_r124_resolution_results,
)
from .w7an_staged_resolution_executor import (
    W7ANStagedResolutionExecutorError,
    _start_w7an_staged_resolution,
)


class W7ANStagedR124CoordinatorError(RuntimeError):
    """Raised when the staged R1/R2/R4 coordination contract fails."""


_ROLES = (
    ("primary", "r1", 1),
    ("primary", "r2", 2),
    ("primary", "r4", 4),
    ("reverse-repeat", "r4", 4),
    ("reverse-repeat", "r2", 2),
    ("reverse-repeat", "r1", 1),
)
_PHASES_PER_RESOLUTION = 6
_TOTAL_PHASES = len(_ROLES) * _PHASES_PER_RESOLUTION
_CANONICAL_STAGED_R1_DIGEST = (
    "60be9b3cbe32360e86f603051be4d9d3af2325f76b822975e0bbdf420ae16edc"
)
_CANONICAL_STAGED_RESOLUTION_DIGESTS = {
    "r1": _CANONICAL_STAGED_R1_DIGEST,
    "r2": "ac59bc804e393cdd9984ec5df4e1f9659bb87c3cdba21be87a769c4cf29e7c86",
    "r4": "8b356d0d3e67108747c13098e366160a13ccc43378b32c574d9b183dbf320f4c",
}
_CANONICAL_STAGED_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)


def _receipt_payload(
    pass_id: str,
    resolution_id: str,
    refinement: int,
    phase_id: str,
    completed_phase_count: int,
    child_receipt_digest: str,
    resolution_completed: bool,
    coordinator_completed: bool,
) -> dict[str, object]:
    return {
        "pass_id": pass_id,
        "resolution_id": resolution_id,
        "refinement": refinement,
        "phase_id": phase_id,
        "completed_phase_count": completed_phase_count,
        "child_receipt_digest": child_receipt_digest,
        "resolution_completed": resolution_completed,
        "coordinator_completed": coordinator_completed,
    }


@dataclass(frozen=True, slots=True)
class W7ANCoordinatorPhaseReceipt:
    """In-memory binding for one coordinator-controlled child phase."""

    pass_id: str
    resolution_id: str
    refinement: int
    phase_id: str
    completed_phase_count: int
    child_receipt_digest: str
    resolution_completed: bool
    coordinator_completed: bool
    coordinator_phase_receipt_digest: str

    def __post_init__(self) -> None:
        role_index = (self.completed_phase_count - 1) // _PHASES_PER_RESOLUTION
        expected_role = _ROLES[role_index] if 0 <= role_index < len(_ROLES) else None
        expected_resolution_complete = (
            self.completed_phase_count % _PHASES_PER_RESOLUTION == 0
        )
        if (
            expected_role
            != (self.pass_id, self.resolution_id, self.refinement)
            or not self.phase_id
            or not self.child_receipt_digest
            or not 1 <= self.completed_phase_count <= _TOTAL_PHASES
            or self.resolution_completed is not expected_resolution_complete
            or self.coordinator_completed
            is not (self.completed_phase_count == _TOTAL_PHASES)
        ):
            raise W7ANStagedR124CoordinatorError(
                "coordinator phase receipt binding is invalid"
            )
        payload = _receipt_payload(
            self.pass_id,
            self.resolution_id,
            self.refinement,
            self.phase_id,
            self.completed_phase_count,
            self.child_receipt_digest,
            self.resolution_completed,
            self.coordinator_completed,
        )
        if self.coordinator_phase_receipt_digest != _digest(payload):
            raise W7ANStagedR124CoordinatorError(
                "coordinator phase receipt digest differs"
            )


class _W7ANStagedR124Coordinator:
    """Advance one child phase at a time across primary and reverse roles."""

    def __init__(
        self,
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        p0_references,
    ) -> None:
        if (
            getattr(
                p0_references,
                "p0_zero_start_measurement_reference_digest",
                None,
            )
            != _P0_REFERENCE_DIGEST
        ):
            raise W7ANStagedR124CoordinatorError(
                "coordinator requires the canonical shared P0 reference"
            )
        self.adapter = adapter
        self.family = family
        self.authorization = authorization
        self.plan = plan
        self.p0_result = p0_result
        self.observer_result = observer_result
        self.p0_references = p0_references
        self.role_index = 0
        self.completed_phase_count = 0
        self.active_executor = None
        self.primary_results = {}
        self.repeat_results = {}
        self.receipts = []
        self.terminal_error = None
        self.resolution_container = None

    @property
    def next_role(self):
        if self.role_index == len(_ROLES):
            return None
        return _ROLES[self.role_index]

    @property
    def completed(self) -> bool:
        return self.role_index == len(_ROLES) and self.terminal_error is None

    def _start_active_executor(self):
        pass_id, resolution_id, refinement = self.next_role
        executor = _start_w7an_staged_resolution(
            resolution_id,
            refinement,
            self.adapter,
            self.family,
            self.authorization,
            self.plan,
            self.p0_result,
            self.observer_result,
            self.p0_references,
        )
        if executor.p0_references is not self.p0_references:
            raise W7ANStagedR124CoordinatorError(
                "child executor did not retain the shared P0 object"
            )
        self.active_executor = executor
        return pass_id, resolution_id, refinement

    def _bind_completed_resolution(
        self,
        pass_id: str,
        resolution_id: str,
        result,
    ) -> None:
        digest = result.resolution_result_digest
        if pass_id == "primary":
            if resolution_id in self.primary_results:
                raise W7ANStagedR124CoordinatorError(
                    "primary resolution was completed twice"
                )
            if digest != _CANONICAL_STAGED_RESOLUTION_DIGESTS[resolution_id]:
                raise W7ANStagedR124CoordinatorError(
                    "primary resolution differs from its canonical staged digest"
                )
            self.primary_results[resolution_id] = result
            return
        primary = self.primary_results.get(resolution_id)
        if (
            primary is None
            or primary.resolution_result_digest != digest
        ):
            raise W7ANStagedR124CoordinatorError(
                "reverse-repeat resolution differs from its primary"
            )
        self.repeat_results[resolution_id] = result

    def advance(self) -> W7ANCoordinatorPhaseReceipt:
        """Advance exactly one phase in the globally bound role order."""

        if self.terminal_error is not None:
            raise W7ANStagedR124CoordinatorError(self.terminal_error)
        if self.completed:
            raise W7ANStagedR124CoordinatorError(
                "staged R1/R2/R4 coordination is already complete"
            )
        if self.active_executor is None:
            pass_id, resolution_id, refinement = self._start_active_executor()
        else:
            pass_id, resolution_id, refinement = self.next_role
        try:
            child_receipt = self.active_executor.advance()
        except W7ANStagedResolutionExecutorError:
            raise
        resolution_completed = child_receipt.resolution_result_ready
        if resolution_completed:
            try:
                self._bind_completed_resolution(
                    pass_id,
                    resolution_id,
                    self.active_executor.resolution_result,
                )
            except W7ANStagedR124CoordinatorError as error:
                self.terminal_error = str(error)
                raise
        completed_phase_count = self.completed_phase_count + 1
        coordinator_completed = completed_phase_count == _TOTAL_PHASES
        payload = _receipt_payload(
            pass_id,
            resolution_id,
            refinement,
            child_receipt.phase_id,
            completed_phase_count,
            child_receipt.phase_receipt_digest,
            resolution_completed,
            coordinator_completed,
        )
        receipt = W7ANCoordinatorPhaseReceipt(
            pass_id,
            resolution_id,
            refinement,
            child_receipt.phase_id,
            completed_phase_count,
            child_receipt.phase_receipt_digest,
            resolution_completed,
            coordinator_completed,
            _digest(payload),
        )
        self.receipts.append(receipt)
        self.completed_phase_count = completed_phase_count
        if resolution_completed:
            self.role_index += 1
            self.active_executor = None
        return receipt


def _start_w7an_staged_r124_coordinator(
    adapter,
    family,
    authorization,
    plan,
    p0_result,
    observer_result,
    p0_references,
) -> _W7ANStagedR124Coordinator:
    """Create the private coordinator without executing any phase."""

    return _W7ANStagedR124Coordinator(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        p0_references,
    )


def _finalize_w7an_staged_r124_coordinator(
    state: _W7ANStagedR124Coordinator,
    canonical_cap,
    canonical_handoff,
    canonical_raw,
):
    """Finalize a completed coordinator without executing another phase."""

    if not isinstance(state, _W7ANStagedR124Coordinator):
        raise W7ANStagedR124CoordinatorError(
            "global finalization requires the staged coordinator"
        )
    if state.resolution_container is not None:
        raise W7ANStagedR124CoordinatorError(
            "global resolution container was already finalized"
        )
    expected_ids = {"r1", "r2", "r4"}
    if (
        not state.completed
        or state.completed_phase_count != _TOTAL_PHASES
        or len(state.receipts) != _TOTAL_PHASES
        or set(state.primary_results) != expected_ids
        or set(state.repeat_results) != expected_ids
    ):
        raise W7ANStagedR124CoordinatorError(
            "global finalization requires all 36 verified phases"
        )
    resolutions = tuple(
        state.primary_results[resolution_id]
        for resolution_id in ("r1", "r2", "r4")
    )
    if (
        any(
            item.p0_references is not state.p0_references
            for item in resolutions
        )
        or any(
            state.repeat_results[item.resolution_id].resolution_result_digest
            != item.resolution_result_digest
            for item in resolutions
        )
    ):
        raise W7ANStagedR124CoordinatorError(
            "global finalization inputs differ from verified coordination"
        )
    container = _finalize_w7an_r124_resolution_results(
        state.plan,
        state.p0_references,
        canonical_cap,
        canonical_handoff,
        canonical_raw,
        resolutions,
    )
    if (
        container.resolution_container_digest
        != _CANONICAL_STAGED_CONTAINER_DIGEST
    ):
        raise W7ANStagedR124CoordinatorError(
            "global container differs from the canonical staged digest"
        )
    state.resolution_container = container
    return container
