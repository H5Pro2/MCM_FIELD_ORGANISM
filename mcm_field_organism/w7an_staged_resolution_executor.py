"""Private six-phase in-memory executor for one W7-AN resolution."""

from __future__ import annotations

from dataclasses import dataclass

from .w7ae_cap_seven_path_consumer import (
    _audit_w7ae_branch_order,
    _audit_w7ae_path_order,
    _finalize_w7ae_cap_materialization,
    _finalize_w7ae_countercontrols,
    _materialize_w7ae_cap_paths,
)
from .w7ag_passive_cap_measurement_handoff import (
    _audit_w7ag_measurement_order,
    _audit_w7ag_observer_passivity,
    _finalize_w7ag_measurement_audits,
    _materialize_w7ag_measurements,
    _measurement_tasks,
)
from .w7an_r124_resolution_container import (
    W7ANResolutionResult,
    _build_pair_container,
    _build_witness,
    _digest,
    _resolution_payload,
)


class W7ANStagedResolutionExecutorError(RuntimeError):
    """Raised when staged execution leaves the six-phase contract."""


_PHASES = (
    ("cap-canonical", 67),
    ("cap-path-order-control", 67),
    ("cap-branch-order-control", 4),
    ("measurement-canonical", 35),
    ("measurement-order-control", 35),
    ("observer-passivity-control", 1),
)
_RESOLUTIONS = (("r1", 1), ("r2", 2), ("r4", 4))


def _receipt_payload(
    resolution_id: str,
    refinement: int,
    phase_id: str,
    completed_phase_count: int,
    integration_count: int,
    output_digest: str,
    resolution_result_ready: bool,
) -> dict[str, object]:
    return {
        "resolution_id": resolution_id,
        "refinement": refinement,
        "phase_id": phase_id,
        "completed_phase_count": completed_phase_count,
        "integration_count": integration_count,
        "output_digest": output_digest,
        "resolution_result_ready": resolution_result_ready,
    }


@dataclass(frozen=True, slots=True)
class W7ANPhaseReceipt:
    """In-memory receipt for one completed phase, not a research report."""

    resolution_id: str
    refinement: int
    phase_id: str
    completed_phase_count: int
    integration_count: int
    output_digest: str
    resolution_result_ready: bool
    phase_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            (self.resolution_id, self.refinement) not in _RESOLUTIONS
            or not 1 <= self.completed_phase_count <= len(_PHASES)
            or self.phase_id != _PHASES[self.completed_phase_count - 1][0]
            or self.integration_count
            != _PHASES[self.completed_phase_count - 1][1]
            or not self.output_digest
            or self.resolution_result_ready
            is not (self.completed_phase_count == len(_PHASES))
        ):
            raise W7ANStagedResolutionExecutorError(
                "phase receipt binding is invalid"
            )
        payload = _receipt_payload(
            self.resolution_id,
            self.refinement,
            self.phase_id,
            self.completed_phase_count,
            self.integration_count,
            self.output_digest,
            self.resolution_result_ready,
        )
        if self.phase_receipt_digest != _digest(payload):
            raise W7ANStagedResolutionExecutorError(
                "phase receipt digest differs"
            )


class _W7ANStagedResolutionExecutor:
    """Execute exactly one bounded phase per ``advance`` call."""

    def __init__(
        self,
        resolution_id,
        refinement,
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        p0_references,
    ) -> None:
        if (
            (resolution_id, refinement) not in _RESOLUTIONS
            or isinstance(refinement, bool)
        ):
            raise W7ANStagedResolutionExecutorError(
                "staged resolution role is invalid"
            )
        self.resolution_id = resolution_id
        self.refinement = refinement
        self.adapter = adapter
        self.family = family
        self.authorization = authorization
        self.plan = plan
        self.p0_result = p0_result
        self.observer_result = observer_result
        self.p0_references = p0_references
        self.completed_phase_count = 0
        self.receipts = []
        self.production_witnesses = []
        self.measurement_witnesses = []
        self.cap_materialization = None
        self.cap_path_audit = None
        self.cap_branch_audit = None
        self.cap_result = None
        self.measurement_materialization = None
        self.measurement_order_audit = None
        self.observer_passivity_audit = None
        self.cap_handoff = None
        self.pair_container = None
        self.resolution_result = None

    @property
    def next_phase_id(self) -> str | None:
        if self.completed_phase_count == len(_PHASES):
            return None
        return _PHASES[self.completed_phase_count][0]

    def _production_observer(self, segment, production, diagnostics):
        self._pending_witnesses.append(
            _build_witness(
                self.resolution_id,
                self.refinement,
                segment.branch_kind,
                segment,
                production,
                diagnostics,
            )
        )
        return None

    def _measurement_observer(self, segment, production, diagnostics):
        self._pending_witnesses.append(
            _build_witness(
                self.resolution_id,
                self.refinement,
                "measurement",
                segment,
                production,
                diagnostics,
            )
        )
        return None

    def _complete_phase(self, output_digest: str) -> W7ANPhaseReceipt:
        phase_id, integration_count = _PHASES[self.completed_phase_count]
        completed = self.completed_phase_count + 1
        ready = completed == len(_PHASES)
        payload = _receipt_payload(
            self.resolution_id,
            self.refinement,
            phase_id,
            completed,
            integration_count,
            output_digest,
            ready,
        )
        receipt = W7ANPhaseReceipt(
            self.resolution_id,
            self.refinement,
            phase_id,
            completed,
            integration_count,
            output_digest,
            ready,
            _digest(payload),
        )
        self.receipts.append(receipt)
        self.completed_phase_count = completed
        return receipt

    def advance(self) -> W7ANPhaseReceipt:
        """Run the next phase; never run more than one phase per call."""

        phase = self.next_phase_id
        if phase is None:
            raise W7ANStagedResolutionExecutorError(
                "staged resolution is already complete"
            )
        if phase == "cap-canonical":
            self._pending_witnesses = []
            materialization = _materialize_w7ae_cap_paths(
                self.adapter,
                self.family,
                self.authorization,
                self.plan,
                self.p0_result,
                self.observer_result,
                _refinement=self.refinement,
                _integration_observer=self._production_observer,
            )
            if len(self._pending_witnesses) != 67:
                raise W7ANStagedResolutionExecutorError(
                    "CAP materialization did not produce 67 witnesses"
                )
            self.cap_materialization = materialization
            self.production_witnesses = list(self._pending_witnesses)
            output = _digest(
                {
                    "path_digests": tuple(
                        item.cap_path_consumption_digest
                        for item in materialization.path_results
                    ),
                    "witness_digests": tuple(
                        item.witness_digest for item in self.production_witnesses
                    ),
                }
            )
        elif phase == "cap-path-order-control":
            self.cap_path_audit = _audit_w7ae_path_order(
                self.adapter,
                self.authorization,
                self.plan,
                self.cap_materialization.path_results,
                _refinement=self.refinement,
            )
            output = _digest(
                {"path_digests": self.cap_path_audit.path_digests}
            )
        elif phase == "cap-branch-order-control":
            self.cap_branch_audit = _audit_w7ae_branch_order(
                self.adapter,
                self.authorization,
                self.plan,
                self.cap_materialization.path_results,
                _refinement=self.refinement,
            )
            controls = _finalize_w7ae_countercontrols(
                self.cap_materialization.path_results,
                self.cap_path_audit,
                self.cap_branch_audit,
            )
            self.cap_result = _finalize_w7ae_cap_materialization(
                self.adapter,
                self.family,
                self.authorization,
                self.plan,
                self.p0_result,
                self.observer_result,
                self.cap_materialization,
                controls,
            )
            output = self.cap_result.cap_seven_path_consumption_digest
        elif phase == "measurement-canonical":
            self._pending_witnesses = []
            materialization = _materialize_w7ag_measurements(
                self.adapter,
                self.family,
                self.authorization,
                self.plan,
                self.cap_result,
                _refinement=self.refinement,
                _integration_observer=self._measurement_observer,
            )
            if len(self._pending_witnesses) != 35:
                raise W7ANStagedResolutionExecutorError(
                    "measurement materialization did not produce 35 witnesses"
                )
            self.measurement_materialization = materialization
            self.measurement_witnesses = list(self._pending_witnesses)
            output = _digest(
                {
                    "measurement_digests": tuple(
                        item.measurement_result_digest
                        for item in materialization.measurements
                    ),
                    "witness_digests": tuple(
                        item.witness_digest for item in self.measurement_witnesses
                    ),
                }
            )
        elif phase == "measurement-order-control":
            tasks = _measurement_tasks(self.plan, self.cap_result)
            self.measurement_order_audit = _audit_w7ag_measurement_order(
                self.adapter,
                self.authorization,
                tasks,
                self.measurement_materialization,
            )
            output = self.measurement_order_audit.order_countercontrol_digest
        else:
            self.observer_passivity_audit = _audit_w7ag_observer_passivity(
                self.adapter,
                self.authorization,
                self.plan,
                self.measurement_materialization,
            )
            self.cap_handoff = _finalize_w7ag_measurement_audits(
                self.plan,
                self.cap_result,
                self.measurement_materialization,
                self.measurement_order_audit,
                self.observer_passivity_audit,
            )
            self.pair_container = _build_pair_container(
                self.resolution_id,
                self.refinement,
                self.cap_handoff,
                self.p0_references,
            )
            self.resolution_result = self._finalize_resolution_result()
            output = self.resolution_result.resolution_result_digest
        return self._complete_phase(output)

    def _finalize_resolution_result(self):
        production = tuple(self.production_witnesses)
        measurement = tuple(self.measurement_witnesses)
        payload = _resolution_payload(
            self.resolution_id,
            self.refinement,
            self.plan.seven_path_plan_digest,
            self.cap_result.cap_seven_path_consumption_digest,
            production,
            self.cap_handoff.measurement_handoff_digest,
            measurement,
            self.pair_container.pair_container_digest,
            self.p0_references.p0_zero_start_measurement_reference_digest,
        )
        return W7ANResolutionResult(
            self.resolution_id,
            self.refinement,
            self.plan.seven_path_plan_digest,
            self.cap_result,
            production,
            self.cap_handoff,
            measurement,
            self.pair_container,
            self.p0_references,
            False,
            _digest(payload),
        )


def _start_w7an_staged_resolution(
    resolution_id,
    refinement,
    adapter,
    family,
    authorization,
    plan,
    p0_result,
    observer_result,
    p0_references,
) -> _W7ANStagedResolutionExecutor:
    """Create an unstarted private executor without running a phase."""

    return _W7ANStagedResolutionExecutor(
        resolution_id,
        refinement,
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        p0_references,
    )
