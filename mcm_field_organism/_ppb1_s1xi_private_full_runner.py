"""Private S1-XI full-shape runner locked to substitute execution."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import PPB1BankState, _digest
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from ._ppb1_s1xc_fixture_registry import (
    S1XC_PROBE_CLASSES,
    S1XC_REGISTRY_DIGEST,
    S1XC_SYSTEM_IDS,
    S1XCBaselinePrestate,
    S1XCCellPlan,
    S1XCModalityFixture,
    _frame_digest,
    materialize_s1xc_fixture_registry,
    probe_s1xc_baseline_read_only,
)
from ._ppb1_s1xf_private_miniature_runner import (
    S1XFFormationReceipt,
    _form_candidate,
)


S1XI_SCHEMA_VERSION = "ppb1.s1xi.private-full-runner.v1"
S1XI_PREFLIGHT_DIGEST = (
    "11971a2c994806c2abd51540d5bd931c5fd70290c771e43fa248c157c009ea13"
)
S1XI_RUN_CONTRACT_DIGEST = (
    "eb501a103ec40dc9234e946553afb554279089ed2381a03011daa91f9db7731c"
)
S1XI_S1XC_SOURCE_DIGEST = (
    "d22543d4c442c25fefde7719458c2b3a3c4abfbc7adbac3d1ec4c263a5c324b9"
)
S1XI_S1WU_SOURCE_DIGEST = (
    "1e47680f9c340149c99e0fb182fc1f25d475b773ce34b37a9d2103fad05303ef"
)
S1XI_SUBSTITUTE_PROBE_CLASSES = ("exact-positive", "distinct-negative")
S1XI_SUBSTITUTE_FINAL = (
    "SUBSTITUTE_RUNNER_AND_AGGREGATOR_VALID_NO_REGISTERED_DECISION"
)
S1XI_REGISTERED_EXECUTION_ENABLED = False

S1XI_INVALID_PLAN = "S1XI_INVALID_PLAN"
S1XI_INVALID_RECEIPT = "S1XI_INVALID_RECEIPT"
S1XI_INVALID_RUN = "S1XI_INVALID_RUN"
S1XI_REGISTERED_EXECUTION_LOCKED = "S1XI_REGISTERED_EXECUTION_LOCKED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_DISTANCE_TOLERANCE = 1e-12


class S1XIError(ValueError):
    """One fail-closed S1-XI plan, receipt or execution violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _receipt_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1XI_SCHEMA_VERSION,
            "preflight_digest": S1XI_PREFLIGHT_DIGEST,
            **payload,
        }
    )


@dataclass(frozen=True, slots=True)
class S1XIExecutionPlan:
    cell_id: str
    cell_plan_digest: str
    system_id: str
    modality_id: str
    probe_class: str
    expected_recognized: bool
    expected_distance: float | None
    registered: bool

    def __post_init__(self) -> None:
        prefix = "s1xa" if self.registered else "s1xi-sub"
        if (
            self.cell_id
            != f"{prefix}.{self.modality_id}.{self.system_id}.{self.probe_class}"
            or not _valid_digest(self.cell_plan_digest)
            or self.system_id not in S1XC_SYSTEM_IDS
            or self.modality_id not in {"auditory", "visual"}
            or self.probe_class not in S1XC_PROBE_CLASSES
            or not isinstance(self.expected_recognized, bool)
        ):
            raise S1XIError(S1XI_INVALID_PLAN, "invalid execution plan")
        if self.expected_distance is not None and (
            not math.isfinite(self.expected_distance)
            or self.expected_distance < 0.0
            or self.expected_distance > 2.0
        ):
            raise S1XIError(S1XI_INVALID_PLAN, "invalid expected distance")


@dataclass(frozen=True, slots=True)
class S1XIRegisteredCellReceipt:
    cell_id: str
    cell_plan_digest: str
    system_id: str
    modality_id: str
    probe_class: str
    finding_digest: str
    recognized: bool
    nearest_distance: float | None
    observed_state_present: bool
    observed_state_digest_before: str | None
    observed_state_digest_after: str | None
    state_identity_digest: str | None
    state_provenance_digest: str | None
    storage_role_count: int
    stored_scalar_value_count: int
    raw_history_access_used: bool
    state_unchanged: bool
    matches_prebound_expectation: bool
    cell_receipt_digest: str

    def __post_init__(self) -> None:
        prefix = "s1xa" if self.cell_id.startswith("s1xa.") else "s1xi-sub"
        if (
            self.cell_id
            != f"{prefix}.{self.modality_id}.{self.system_id}.{self.probe_class}"
            or not _valid_digest(self.cell_plan_digest)
            or self.system_id not in S1XC_SYSTEM_IDS
            or self.modality_id not in {"auditory", "visual"}
            or self.probe_class not in S1XC_PROBE_CLASSES
            or not _valid_digest(self.finding_digest)
            or not isinstance(self.recognized, bool)
            or not isinstance(self.observed_state_present, bool)
            or not isinstance(self.raw_history_access_used, bool)
            or not isinstance(self.state_unchanged, bool)
            or not isinstance(self.matches_prebound_expectation, bool)
        ):
            raise S1XIError(S1XI_INVALID_RECEIPT, "invalid cell receipt anatomy")
        if self.nearest_distance is not None and (
            not math.isfinite(self.nearest_distance)
            or self.nearest_distance < 0.0
            or self.nearest_distance > 2.0
        ):
            raise S1XIError(S1XI_INVALID_RECEIPT, "invalid observed distance")
        for count in (self.storage_role_count, self.stored_scalar_value_count):
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise S1XIError(S1XI_INVALID_RECEIPT, "invalid storage count")
        optional_digests = (
            self.observed_state_digest_before,
            self.observed_state_digest_after,
            self.state_identity_digest,
            self.state_provenance_digest,
        )
        if any(value is not None and not _valid_digest(value) for value in optional_digests):
            raise S1XIError(S1XI_INVALID_RECEIPT, "invalid optional digest role")
        if self.observed_state_present:
            if (
                self.observed_state_digest_before is None
                or self.observed_state_digest_before
                != self.observed_state_digest_after
                or not self.state_unchanged
                or self.state_provenance_digest is None
            ):
                raise S1XIError(
                    S1XI_INVALID_RECEIPT, "observed state is not immutable and bound"
                )
        elif any(value is not None for value in optional_digests):
            raise S1XIError(
                S1XI_INVALID_RECEIPT, "absent state requires canonical null roles"
            )
        if self.system_id == "ppb1":
            if self.state_identity_digest is None or self.raw_history_access_used:
                raise S1XIError(
                    S1XI_INVALID_RECEIPT, "candidate identity or history role invalid"
                )
        elif self.state_identity_digest is not None:
            raise S1XIError(
                S1XI_INVALID_RECEIPT, "baseline received candidate identity"
            )
        if self.system_id == "no-memory" and (
            self.observed_state_present
            or self.recognized
            or self.nearest_distance is not None
            or self.storage_role_count != 0
            or self.stored_scalar_value_count != 0
            or self.raw_history_access_used
        ):
            raise S1XIError(
                S1XI_INVALID_RECEIPT, "no-memory roles are not canonical"
            )
        if self.cell_receipt_digest != _receipt_digest(
            self.payload_without_digest()
        ):
            raise S1XIError(S1XI_INVALID_RECEIPT, "cell receipt digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "run_contract_digest": S1XI_RUN_CONTRACT_DIGEST,
            "cell_id": self.cell_id,
            "cell_plan_digest": self.cell_plan_digest,
            "system_id": self.system_id,
            "modality_id": self.modality_id,
            "probe_class": self.probe_class,
            "finding_digest": self.finding_digest,
            "recognized": self.recognized,
            "nearest_distance": self.nearest_distance,
            "observed_state_present": self.observed_state_present,
            "observed_state_digest_before": self.observed_state_digest_before,
            "observed_state_digest_after": self.observed_state_digest_after,
            "state_identity_digest": self.state_identity_digest,
            "state_provenance_digest": self.state_provenance_digest,
            "storage_role_count": self.storage_role_count,
            "stored_scalar_value_count": self.stored_scalar_value_count,
            "raw_history_access_used": self.raw_history_access_used,
            "state_unchanged": self.state_unchanged,
            "matches_prebound_expectation": self.matches_prebound_expectation,
        }


@dataclass(frozen=True, slots=True)
class S1XIRegisteredMatrixReceipt:
    run_contract_digest: str
    s1xc_source_digest: str
    s1wu_source_digest: str
    registry_digest: str
    materialization_digest: str
    auditory_formation_receipt_digest: str
    visual_formation_receipt_digest: str
    ordered_cell_receipt_digests: tuple[str, ...]
    candidate_pass_cell_count: int
    baseline_explanation_by_system: tuple[tuple[str, bool], ...]
    method_valid: bool
    technical_function_decision: str | None
    baseline_explanation_decision: str | None
    final_decision: str
    matrix_receipt_digest: str

    def __post_init__(self) -> None:
        for value in (
            self.run_contract_digest,
            self.s1xc_source_digest,
            self.s1wu_source_digest,
            self.registry_digest,
            self.materialization_digest,
            self.auditory_formation_receipt_digest,
            self.visual_formation_receipt_digest,
            *self.ordered_cell_receipt_digests,
        ):
            if not _valid_digest(value):
                raise S1XIError(S1XI_INVALID_RECEIPT, "invalid matrix digest role")
        if (
            self.run_contract_digest != S1XI_RUN_CONTRACT_DIGEST
            or self.s1xc_source_digest != S1XI_S1XC_SOURCE_DIGEST
            or self.s1wu_source_digest != S1XI_S1WU_SOURCE_DIGEST
            or isinstance(self.candidate_pass_cell_count, bool)
            or not isinstance(self.candidate_pass_cell_count, int)
            or self.candidate_pass_cell_count < 0
            or not isinstance(self.method_valid, bool)
        ):
            raise S1XIError(S1XI_INVALID_RECEIPT, "invalid matrix identity")
        systems = tuple(system for system, _ in self.baseline_explanation_by_system)
        if systems != S1XC_SYSTEM_IDS[1:] or any(
            not isinstance(value, bool)
            for _, value in self.baseline_explanation_by_system
        ):
            raise S1XIError(
                S1XI_INVALID_RECEIPT, "baseline explanation inventory is invalid"
            )
        substitute = self.final_decision == S1XI_SUBSTITUTE_FINAL
        if substitute:
            if (
                len(self.ordered_cell_receipt_digests) != 24
                or self.candidate_pass_cell_count != 4
                or not self.method_valid
                or self.technical_function_decision is not None
                or self.baseline_explanation_decision is not None
                or self.registry_digest == S1XC_REGISTRY_DIGEST
            ):
                raise S1XIError(
                    S1XI_INVALID_RECEIPT, "substitute receipt crossed decision boundary"
                )
        else:
            valid_registered_decisions = (
                (
                    not self.method_valid
                    and self.technical_function_decision is None
                    and self.baseline_explanation_decision is None
                    and self.final_decision
                    == "METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION"
                )
                or (
                    self.method_valid
                    and self.technical_function_decision
                    == "TECHNICAL_MEMORY_FUNCTION_FAIL"
                    and self.baseline_explanation_decision is None
                    and self.final_decision == "TECHNICAL_MEMORY_FUNCTION_FAIL"
                )
                or (
                    self.method_valid
                    and self.technical_function_decision
                    == "TECHNICAL_MEMORY_FUNCTION_PASS"
                    and self.baseline_explanation_decision
                    in {
                        "TECHNICAL_MEMORY_FUNCTION_PASS_BASELINE_EXPLAINED",
                        "TECHNICAL_MEMORY_FUNCTION_PASS_UNEXPLAINED_ENGINEERING_DIFFERENCE",
                    }
                    and self.final_decision
                    == self.baseline_explanation_decision
                )
            )
            if (
                len(self.ordered_cell_receipt_digests) != 60
                or self.registry_digest != S1XC_REGISTRY_DIGEST
                or not valid_registered_decisions
            ):
                raise S1XIError(
                    S1XI_INVALID_RECEIPT,
                    "registered receipt count, registry or decision is invalid",
                )
        if self.matrix_receipt_digest != _receipt_digest(
            self.payload_without_digest()
        ):
            raise S1XIError(S1XI_INVALID_RECEIPT, "matrix receipt digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "run_contract_digest": self.run_contract_digest,
            "s1xc_source_digest": self.s1xc_source_digest,
            "s1wu_source_digest": self.s1wu_source_digest,
            "registry_digest": self.registry_digest,
            "materialization_digest": self.materialization_digest,
            "auditory_formation_receipt_digest": (
                self.auditory_formation_receipt_digest
            ),
            "visual_formation_receipt_digest": self.visual_formation_receipt_digest,
            "ordered_cell_receipt_digests": list(
                self.ordered_cell_receipt_digests
            ),
            "candidate_pass_cell_count": self.candidate_pass_cell_count,
            "baseline_explanation_by_system": [
                [system, value]
                for system, value in self.baseline_explanation_by_system
            ],
            "method_valid": self.method_valid,
            "technical_function_decision": self.technical_function_decision,
            "baseline_explanation_decision": self.baseline_explanation_decision,
            "final_decision": self.final_decision,
        }


@dataclass(frozen=True, slots=True)
class S1XIRunResult:
    formation_receipts: tuple[S1XFFormationReceipt, ...]
    cell_receipts: tuple[S1XIRegisteredCellReceipt, ...]
    matrix_receipt: S1XIRegisteredMatrixReceipt

    def __post_init__(self) -> None:
        if (
            tuple(item.modality_id for item in self.formation_receipts)
            != ("auditory", "visual")
            or tuple(item.cell_receipt_digest for item in self.cell_receipts)
            != self.matrix_receipt.ordered_cell_receipt_digests
            or self.formation_receipts[0].formation_receipt_digest
            != self.matrix_receipt.auditory_formation_receipt_digest
            or self.formation_receipts[1].formation_receipt_digest
            != self.matrix_receipt.visual_formation_receipt_digest
        ):
            raise S1XIError(S1XI_INVALID_RUN, "run result is not atomic")


def _substitute_plans(
    modalities: tuple[S1XCModalityFixture, ...],
) -> tuple[S1XIExecutionPlan, ...]:
    plans = []
    for fixture in modalities:
        modality = fixture.config.modality_id
        for system in S1XC_SYSTEM_IDS:
            for probe_class, index in zip(
                S1XI_SUBSTITUTE_PROBE_CLASSES, (0, 4), strict=True
            ):
                expected_recognized = (
                    False
                    if system == "no-memory"
                    else probe_class == "exact-positive"
                )
                expected_distance = (
                    None
                    if system == "no-memory"
                    else fixture.probe_frames[index].values[0]
                )
                values = {
                    "cell_id": f"s1xi-sub.{modality}.{system}.{probe_class}",
                    "system_id": system,
                    "modality_id": modality,
                    "probe_class": probe_class,
                    "expected_recognized": expected_recognized,
                    "expected_distance": expected_distance,
                    "registered": False,
                }
                plans.append(
                    S1XIExecutionPlan(
                        cell_plan_digest=_receipt_digest(values),
                        **values,
                    )
                )
    return tuple(plans)


def _registered_plans(cell_plans: tuple[S1XCCellPlan, ...]) -> tuple[S1XIExecutionPlan, ...]:
    return tuple(
        S1XIExecutionPlan(
            item.cell_id,
            item.cell_plan_digest,
            item.system_id,
            item.modality_id,
            item.probe_class,
            item.expected_recognized,
            item.expected_distance,
            True,
        )
        for item in cell_plans
    )


def _same_distance(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return abs(left - right) <= _DISTANCE_TOLERANCE


def _execute_cell(
    plan: S1XIExecutionPlan,
    fixture: S1XCModalityFixture,
    formed_state: PPB1BankState,
    baseline: S1XCBaselinePrestate | None,
) -> S1XIRegisteredCellReceipt:
    frame_index = S1XC_PROBE_CLASSES.index(plan.probe_class)
    frame = fixture.probe_frames[frame_index]
    if plan.system_id == "ppb1":
        before = formed_state.digest()
        identity = _digest(_state_identity_payload(formed_state))
        finding = probe_s1wu_perceptual_state(
            fixture.config,
            formed_state,
            frame,
            f"probe.s1xi.{fixture.config.modality_id}.{plan.probe_class}",
        )
        after = formed_state.digest()
        finding_digest = finding.finding_digest
        recognized = finding.recognized
        distance = finding.match_distance
        state_present = True
        provenance = fixture.formation_history_digest
        storage_roles = 1
        stored_values = len(fixture.config.carrier_ids)
        raw_history = False
    else:
        before = None if baseline is None else baseline.digest()
        finding = probe_s1xc_baseline_read_only(
            plan.system_id, fixture.config, baseline, frame, plan.probe_class
        )
        after = None if baseline is None else baseline.digest()
        identity = None
        finding_digest = finding.finding_digest
        recognized = finding.recognized
        distance = finding.match_distance
        state_present = baseline is not None
        provenance = None if baseline is None else fixture.formation_history_digest
        storage_roles = 0 if baseline is None else 1
        stored_values = finding.stored_scalar_value_count
        raw_history = finding.raw_history_access_used
    values = {
        "cell_id": plan.cell_id,
        "cell_plan_digest": plan.cell_plan_digest,
        "system_id": plan.system_id,
        "modality_id": plan.modality_id,
        "probe_class": plan.probe_class,
        "finding_digest": finding_digest,
        "recognized": recognized,
        "nearest_distance": distance,
        "observed_state_present": state_present,
        "observed_state_digest_before": before,
        "observed_state_digest_after": after,
        "state_identity_digest": identity,
        "state_provenance_digest": provenance,
        "storage_role_count": storage_roles,
        "stored_scalar_value_count": stored_values,
        "raw_history_access_used": raw_history,
        "state_unchanged": before == after,
        "matches_prebound_expectation": (
            recognized == plan.expected_recognized
            and _same_distance(distance, plan.expected_distance)
        ),
    }
    return S1XIRegisteredCellReceipt(
        **values,
        cell_receipt_digest=_receipt_digest(
            {"run_contract_digest": S1XI_RUN_CONTRACT_DIGEST, **values}
        ),
    )


def _baseline_explanation(
    cells: tuple[S1XIRegisteredCellReceipt, ...],
) -> tuple[tuple[str, bool], ...]:
    candidate = {
        (cell.modality_id, cell.probe_class): cell
        for cell in cells
        if cell.system_id == "ppb1"
    }
    result = []
    for system in S1XC_SYSTEM_IDS[1:]:
        baseline = {
            (cell.modality_id, cell.probe_class): cell
            for cell in cells
            if cell.system_id == system
        }
        explains = baseline.keys() == candidate.keys() and all(
            baseline[key].recognized == expected.recognized
            and _same_distance(
                baseline[key].nearest_distance, expected.nearest_distance
            )
            for key, expected in candidate.items()
        )
        result.append((system, explains))
    return tuple(result)


def _execute_plan_set(
    *,
    registered: bool,
) -> S1XIRunResult:
    materialized = materialize_s1xc_fixture_registry()
    if registered:
        plans = _registered_plans(materialized.cell_plans)
        registry_digest = materialized.registry_digest
    else:
        plans = _substitute_plans(materialized.modalities)
        registry_digest = _digest(
            [
                {"cell_id": item.cell_id, "cell_plan_digest": item.cell_plan_digest}
                for item in plans
            ]
        )

    formed_by_modality = {}
    formation_receipts = []
    fixture_by_modality = {
        fixture.config.modality_id: fixture for fixture in materialized.modalities
    }
    for fixture in materialized.modalities:
        formed, receipt = _form_candidate(fixture)
        formed_by_modality[fixture.config.modality_id] = formed
        formation_receipts.append(receipt)
    baseline_by_role = {
        (item.modality_id, item.system_id): item
        for item in materialized.baseline_prestates
    }

    cells = tuple(
        _execute_cell(
            plan,
            fixture_by_modality[plan.modality_id],
            formed_by_modality[plan.modality_id],
            baseline_by_role.get((plan.modality_id, plan.system_id)),
        )
        for plan in plans
    )
    if tuple(cell.cell_id for cell in cells) != tuple(plan.cell_id for plan in plans):
        raise S1XIError(S1XI_INVALID_RUN, "cell order differs from plan order")
    explanations = _baseline_explanation(cells)
    candidate_pass_count = sum(
        cell.matches_prebound_expectation
        for cell in cells
        if cell.system_id == "ppb1"
    )

    if registered:
        method_valid = (
            len(cells) == 60
            and len({cell.cell_id for cell in cells}) == 60
            and registry_digest == S1XC_REGISTRY_DIGEST
        )
        if not method_valid:
            technical_decision = None
            baseline_decision = None
            final_decision = "METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION"
        elif candidate_pass_count != 10:
            technical_decision = "TECHNICAL_MEMORY_FUNCTION_FAIL"
            baseline_decision = None
            final_decision = technical_decision
        else:
            technical_decision = "TECHNICAL_MEMORY_FUNCTION_PASS"
            explained = any(value for _, value in explanations)
            baseline_decision = (
                "TECHNICAL_MEMORY_FUNCTION_PASS_BASELINE_EXPLAINED"
                if explained
                else "TECHNICAL_MEMORY_FUNCTION_PASS_UNEXPLAINED_ENGINEERING_DIFFERENCE"
            )
            final_decision = baseline_decision
    else:
        if (
            len(cells) != 24
            or candidate_pass_count != 4
            or not all(cell.matches_prebound_expectation for cell in cells)
        ):
            raise S1XIError(S1XI_INVALID_RUN, "substitute plan set did not pass")
        method_valid = True
        technical_decision = None
        baseline_decision = None
        final_decision = S1XI_SUBSTITUTE_FINAL

    values = {
        "run_contract_digest": S1XI_RUN_CONTRACT_DIGEST,
        "s1xc_source_digest": S1XI_S1XC_SOURCE_DIGEST,
        "s1wu_source_digest": S1XI_S1WU_SOURCE_DIGEST,
        "registry_digest": registry_digest,
        "materialization_digest": materialized.materialization_digest,
        "auditory_formation_receipt_digest": formation_receipts[
            0
        ].formation_receipt_digest,
        "visual_formation_receipt_digest": formation_receipts[
            1
        ].formation_receipt_digest,
        "ordered_cell_receipt_digests": tuple(
            cell.cell_receipt_digest for cell in cells
        ),
        "candidate_pass_cell_count": candidate_pass_count,
        "baseline_explanation_by_system": explanations,
        "method_valid": method_valid,
        "technical_function_decision": technical_decision,
        "baseline_explanation_decision": baseline_decision,
        "final_decision": final_decision,
    }
    matrix = S1XIRegisteredMatrixReceipt(
        **values,
        matrix_receipt_digest=_receipt_digest(values),
    )
    return S1XIRunResult(tuple(formation_receipts), cells, matrix)


def run_s1xi_substitute_contract() -> S1XIRunResult:
    """Run only the fixed 24-cell substitute plan set."""

    return _execute_plan_set(registered=False)


def run_s1xi_registered_matrix() -> S1XIRunResult:
    """Remain fail-closed until a later explicit execution authorization."""

    if not S1XI_REGISTERED_EXECUTION_ENABLED:
        raise S1XIError(
            S1XI_REGISTERED_EXECUTION_LOCKED,
            "registered sixty-cell execution is not authorized",
        )
    return _execute_plan_set(registered=True)
