"""Finite private S1-IE execution of the preregistered S1-ID audit."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .dynamic_substrate_dts1_coupled_step import (
    DTS1CoupledFastFieldStepResult,
    advance_dts1_coupled_fast_shared_field,
)
from .dynamic_substrate_dts1_step import DTS1StepRates
from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from .dynamic_substrate_s1hz_free_refractory_intervention_contract import (
    S1_HZ_BASELINE_COUNTERPREDICTIONS,
)
from .field_step_time import MCMFieldStepTime
from .mcm_substrate_state import mcm_substrate_edge_inventory
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class DTS1CausalFieldReadoutAuditError(ValueError):
    """Raised when the closed S1-IE audit result is internally invalid."""


S1_IE_AUDIT_ID = "dynamic-substrate.causal-field-readout-audit.s1ie.v1"
S1_IE_SOURCE_S1ID_CONTRACT_DIGEST = (
    "aeadd736c2d8a1982a2b37d874494542603b67586852c78d081eca69ae187750"
)
S1_IE_CASE_IDS = (
    "C01_ACTIVE_TWO_SUBSTEP_READOUT",
    "N01_EQUAL_PARTITION_TWO_SUBSTEP_REPEAT",
    "N02_A0_TWO_SUBSTEP_CONTROL",
    "N03_FROZEN_INITIAL_ADAPTER_CONTROL",
    "N04_MATCHED_ZERO_H_CONTROL",
)
S1_IE_F_HIGH = "F_HIGH_MORE_FREE_LESS_REFRACTORY"
S1_IE_R_HIGH = "R_HIGH_LESS_FREE_MORE_REFRACTORY"
S1_IE_EXPECTED = (
    ("b1_F_HIGH", 0.5980601362608484),
    ("b1_R_HIGH", 0.48929858810763766),
    ("contrast_1", 0.3653670481054693),
    ("adapter_2_F_HIGH", 1.299030068130424),
    ("adapter_2_R_HIGH", 1.2446492940538187),
    ("contrast_2_F_HIGH", 0.06045337407166922),
    ("contrast_2_R_HIGH", 0.06383190638930979),
    ("contrast_margin", 0.0033785323176405632),
    ("complete_SH_separation", 0.0016892661588202816),
)
S1_IE_ROUNDOFF_FLOOR = 1.1368683772161603e-13
S1_IE_SINGLE_AUDIT_FIELD_CALLS = 20
S1_IE_DOUBLE_AUDIT_FIELD_CALLS = 40
S1_IE_PASS = "PASS_DTS1_TWO_SUBSTEP_CAUSAL_FIELD_READOUT"
S1_IE_STOPP = "STOPP_DTS1_TWO_SUBSTEP_CAUSAL_FIELD_READOUT"

_INITIAL_S = (-1.0, 1.0)
_INITIAL_H_MAIN = (-0.2, 0.2)
_INITIAL_H_ZERO = (0.0, 0.0)
_CONTACT = (0.0, 0.0)
_CAPACITY = 1.0
_CONDUCTIVE = 0.4
_F_REFRACTORY = 0.2
_R_REFRACTORY = 0.8
_TICKS_PER_SECOND = 2.0
_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
_DISSIPATION_CONFIG = NeutralFieldDissipationConfig(0.0)
_DTS1_RATES = DTS1StepRates(0.4, 0.3, 0.2)
_BASELINE_VALUE = "STATE_SPACE_DISTINCT_NO_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1CausalFieldReadoutAuditError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1CausalFieldReadoutAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1CausalFieldReadoutAuditError(
            f"{role} must be finite and nonnegative"
        )
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1IEStepRecord:
    arm_id: str
    substep: int
    field_vector: tuple[float, ...]
    anatomy_digest: str
    adapter_rates: tuple[float, ...]
    participation: tuple[float, ...]
    transfer_vector: tuple[float, ...]
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if not isinstance(self.arm_id, str) or not self.arm_id:
            raise DTS1CausalFieldReadoutAuditError("step arm_id must be nonempty")
        if self.substep not in (1, 2):
            raise DTS1CausalFieldReadoutAuditError("step index must be one or two")
        if len(self.field_vector) != 4 or any(
            not math.isfinite(value) for value in self.field_vector
        ):
            raise DTS1CausalFieldReadoutAuditError(
                "step requires one complete finite two-node S/H vector"
            )
        if not isinstance(self.anatomy_digest, str) or len(self.anatomy_digest) != 64:
            raise DTS1CausalFieldReadoutAuditError(
                "step anatomy digest must be one SHA-256 value"
            )
        if len(self.adapter_rates) != 1 or len(self.participation) != 1:
            raise DTS1CausalFieldReadoutAuditError(
                "step requires one adapter rate and one participation"
            )
        if len(self.transfer_vector) != 3:
            raise DTS1CausalFieldReadoutAuditError(
                "step requires one complete transfer triple"
            )
        for role, vector in (
            ("adapter_rates", self.adapter_rates),
            ("participation", self.participation),
            ("transfer_vector", self.transfer_vector),
        ):
            if any(not math.isfinite(value) or value < 0.0 for value in vector):
                raise DTS1CausalFieldReadoutAuditError(
                    f"step {role} must be finite and nonnegative"
                )
        object.__setattr__(
            self,
            "maximum_local_ledger_residual",
            _finite_nonnegative(
                self.maximum_local_ledger_residual,
                "maximum_local_ledger_residual",
            ),
        )
        object.__setattr__(
            self,
            "global_ledger_residual",
            _finite_nonnegative(
                self.global_ledger_residual,
                "global_ledger_residual",
            ),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "substep": self.substep,
            "field_vector": list(self.field_vector),
            "anatomy_digest": self.anatomy_digest,
            "adapter_rates": list(self.adapter_rates),
            "participation": list(self.participation),
            "transfer_vector": list(self.transfer_vector),
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1IECaseRecord:
    case_id: str
    step_records: tuple[DTS1S1IEStepRecord, ...]
    exact_checks: tuple[tuple[str, bool], ...]
    technical_field_calls: int

    def __post_init__(self) -> None:
        if self.case_id not in S1_IE_CASE_IDS:
            raise DTS1CausalFieldReadoutAuditError("unknown S1-IE case")
        if len(self.step_records) != 4:
            raise DTS1CausalFieldReadoutAuditError(
                "each S1-IE case requires two arms and two substeps"
            )
        if tuple(record.substep for record in self.step_records) != (1, 1, 2, 2):
            raise DTS1CausalFieldReadoutAuditError(
                "S1-IE case step records are out of causal order"
            )
        if not self.exact_checks or any(
            not isinstance(value, bool) for _, value in self.exact_checks
        ):
            raise DTS1CausalFieldReadoutAuditError(
                "S1-IE exact checks must be complete booleans"
            )
        if self.technical_field_calls != 4:
            raise DTS1CausalFieldReadoutAuditError(
                "each S1-IE case requires exactly four field calls"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "step_records": [
                record.canonical_payload() for record in self.step_records
            ],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "technical_field_calls": self.technical_field_calls,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1IESingleAuditResult:
    case_records: tuple[DTS1S1IECaseRecord, ...]
    primary_metrics: tuple[tuple[str, float], ...]
    baseline_records: tuple[tuple[str, str], ...]
    technical_field_calls: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            tuple(record.case_id for record in self.case_records) != S1_IE_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics)
            != tuple(name for name, _ in S1_IE_EXPECTED)
            or self.baseline_records != _baseline_records()
            or self.technical_field_calls != S1_IE_SINGLE_AUDIT_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IE_PASS, S1_IE_STOPP)
            or (self.decision == S1_IE_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1CausalFieldReadoutAuditError(
                "single S1-IE audit result is incomplete or inconsistent"
            )
        object.__setattr__(
            self,
            "primary_metrics",
            tuple(
                (name, _finite_nonnegative(value, name))
                for name, value in self.primary_metrics
            ),
        )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "case_records": [
                record.canonical_payload() for record in self.case_records
            ],
            "primary_metrics": [list(metric) for metric in self.primary_metrics],
            "baseline_records": [list(record) for record in self.baseline_records],
            "technical_field_calls": self.technical_field_calls,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["receipt_digest"] = self.receipt_digest
        return payload


@dataclass(frozen=True, slots=True)
class DTS1S1IEDoubleAuditResult:
    audit_id: str
    source_s1id_contract_digest: str
    case_records: tuple[DTS1S1IECaseRecord, ...]
    primary_metrics: tuple[tuple[str, float], ...]
    roundoff_floor: float
    baseline_records: tuple[tuple[str, str], ...]
    first_receipt_digest: str
    repeat_receipt_digest: str
    repeated_receipts_identical: bool
    technical_field_calls: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    audit_receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            self.audit_id != S1_IE_AUDIT_ID
            or self.source_s1id_contract_digest != S1_IE_SOURCE_S1ID_CONTRACT_DIGEST
            or tuple(record.case_id for record in self.case_records) != S1_IE_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics)
            != tuple(name for name, _ in S1_IE_EXPECTED)
            or self.roundoff_floor != S1_IE_ROUNDOFF_FLOOR
            or self.baseline_records != _baseline_records()
            or self.repeated_receipts_identical
            != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.technical_field_calls != S1_IE_DOUBLE_AUDIT_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IE_PASS, S1_IE_STOPP)
            or (self.decision == S1_IE_PASS)
            != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(payload)
        ):
            raise DTS1CausalFieldReadoutAuditError(
                "double S1-IE audit result violates the preregistered boundary"
            )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1id_contract_digest": self.source_s1id_contract_digest,
            "case_records": [
                record.canonical_payload() for record in self.case_records
            ],
            "primary_metrics": [list(metric) for metric in self.primary_metrics],
            "roundoff_floor": self.roundoff_floor,
            "baseline_records": [list(record) for record in self.baseline_records],
            "first_receipt_digest": self.first_receipt_digest,
            "repeat_receipt_digest": self.repeat_receipt_digest,
            "repeated_receipts_identical": self.repeated_receipts_identical,
            "technical_field_calls": self.technical_field_calls,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["audit_receipt_digest"] = self.audit_receipt_digest
        return payload


def _reference_frame(snapshot_id: str) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=snapshot_id,
        clock_id="synthetic.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=("auditory.carrier.0", "auditory.carrier.1"),
        values=_CONTACT,
    )


def _initial_field(afterimage: tuple[float, float]) -> SharedMCMField:
    field = build_shared_mcm_field(
        (_reference_frame("s1ie.reference"),),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(
        replace(
            neuron,
            activation=_INITIAL_S[index],
            afterimage=afterimage[index],
        )
        for index, neuron in enumerate(field.layer.neurons)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _anatomy(field: SharedMCMField, refractory: float) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(
            DTS1NodeCapacity(neuron.neuron_id, _CAPACITY)
            for neuron in field.layer.neurons
        ),
        (
            DTS1EdgeResource(
                *mcm_substrate_edge_inventory(field.layer)[0],
                _CONDUCTIVE,
                refractory,
            ),
        ),
    )


def _distribution(start_tick: int, end_tick: int):
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.line.v1"))
    return distributor.distribute(
        (_reference_frame(f"s1ie.contact.{start_tick}.{end_tick}"),),
        CommonFieldTime("organism.s1ie", start_tick, end_tick),
    )


def _step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.s1ie",
        start_tick,
        end_tick,
        _TICKS_PER_SECOND,
    )


def _anatomy_digest(anatomy: DTS1ResourceAnatomy) -> str:
    payload = {
        "nodes": [[item.node_id, item.capacity] for item in anatomy.node_capacities],
        "edges": [
            [
                item.first_node_id,
                item.second_node_id,
                item.conductive_bound,
                item.refractory,
            ]
            for item in anatomy.edge_resources
        ],
    }
    return _digest(payload)


def _field_vector(field: SharedMCMField) -> tuple[float, ...]:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return tuple(
        [neuron.activation for neuron in neurons]
        + [neuron.afterimage for neuron in neurons]
    )


def _contrast(field: SharedMCMField) -> float:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return neurons[1].activation - neurons[0].activation


def _maximum_difference(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        raise DTS1CausalFieldReadoutAuditError(
            "field separation requires complete equal vectors"
        )
    return max(abs(first - second) for first, second in zip(left, right, strict=True))


def _maximum_local_residual(anatomy: DTS1ResourceAnatomy) -> float:
    return max((abs(item.residual) for item in anatomy.local_ledgers()), default=0.0)


def _record(
    arm_id: str,
    substep: int,
    result: DTS1CoupledFastFieldStepResult,
) -> DTS1S1IEStepRecord:
    transfer = result.resource_transfers[0]
    return DTS1S1IEStepRecord(
        arm_id=arm_id,
        substep=substep,
        field_vector=_field_vector(result.field),
        anatomy_digest=_anatomy_digest(result.anatomy),
        adapter_rates=tuple(
            item.rate_per_second for item in result.applied_adapter.edge_rates
        ),
        participation=tuple(item.participation for item in result.participations),
        transfer_vector=(transfer.engagement, transfer.turnover, transfer.recovery),
        maximum_local_ledger_residual=_maximum_local_residual(result.anatomy),
        global_ledger_residual=abs(result.anatomy.global_residual),
    )


def _call(
    field: SharedMCMField,
    anatomy: DTS1ResourceAnatomy,
    start_tick: int,
    end_tick: int,
    counter: list[int],
    *,
    enabled: bool,
) -> DTS1CoupledFastFieldStepResult:
    counter[0] += 1
    return advance_dts1_coupled_fast_shared_field(
        field,
        anatomy,
        _distribution(start_tick, end_tick),
        _step(start_tick, end_tick),
        _SUBSTRATE_CONFIG,
        _AFTERIMAGE_CONFIG,
        _DTS1_RATES,
        _DISSIPATION_CONFIG,
        backreaction_enabled=enabled,
    )


def _near(value: float, expected: float) -> bool:
    return abs(value - expected) <= S1_IE_ROUNDOFF_FLOOR


def _case(
    case_id: str,
    results: tuple[
        DTS1CoupledFastFieldStepResult,
        DTS1CoupledFastFieldStepResult,
        DTS1CoupledFastFieldStepResult,
        DTS1CoupledFastFieldStepResult,
    ],
    arm_ids: tuple[str, str],
    checks: tuple[tuple[str, bool], ...],
) -> DTS1S1IECaseRecord:
    return DTS1S1IECaseRecord(
        case_id=case_id,
        step_records=(
            _record(arm_ids[0], 1, results[0]),
            _record(arm_ids[1], 1, results[1]),
            _record(arm_ids[0], 2, results[2]),
            _record(arm_ids[1], 2, results[3]),
        ),
        exact_checks=checks,
        technical_field_calls=4,
    )


def _run_c01(counter: list[int]) -> tuple[DTS1S1IECaseRecord, tuple[tuple[str, float], ...]]:
    field = _initial_field(_INITIAL_H_MAIN)
    f0 = _anatomy(field, _F_REFRACTORY)
    r0 = _anatomy(field, _R_REFRACTORY)
    f1 = _call(field, f0, 0, 1, counter, enabled=True)
    r1 = _call(field, r0, 0, 1, counter, enabled=True)
    f2 = _call(f1.field, f1.anatomy, 1, 2, counter, enabled=True)
    r2 = _call(r1.field, r1.anatomy, 1, 2, counter, enabled=True)
    b1_f = f1.anatomy.edge_resources[0].conductive_bound
    b1_r = r1.anatomy.edge_resources[0].conductive_bound
    contrast_1_f = _contrast(f1.field)
    contrast_1_r = _contrast(r1.field)
    adapter_2_f = f2.applied_adapter.edge_rates[0].rate_per_second
    adapter_2_r = r2.applied_adapter.edge_rates[0].rate_per_second
    contrast_2_f = _contrast(f2.field)
    contrast_2_r = _contrast(r2.field)
    separation = _maximum_difference(_field_vector(f2.field), _field_vector(r2.field))
    metrics = (
        ("b1_F_HIGH", b1_f),
        ("b1_R_HIGH", b1_r),
        ("contrast_1", contrast_1_f),
        ("adapter_2_F_HIGH", adapter_2_f),
        ("adapter_2_R_HIGH", adapter_2_r),
        ("contrast_2_F_HIGH", contrast_2_f),
        ("contrast_2_R_HIGH", contrast_2_r),
        ("contrast_margin", contrast_2_r - contrast_2_f),
        ("complete_SH_separation", separation),
    )
    expected = dict(S1_IE_EXPECTED)
    checks = (
        ("substep_1_adapter_bit_exact", f1.applied_adapter == r1.applied_adapter),
        ("substep_1_field_bit_exact", _field_vector(f1.field) == _field_vector(r1.field)),
        ("substep_1_b1_expected_and_directed", _near(b1_f, expected["b1_F_HIGH"]) and _near(b1_r, expected["b1_R_HIGH"]) and b1_f > b1_r),
        ("substep_1_contrast_expected", _near(contrast_1_f, expected["contrast_1"]) and contrast_1_f == contrast_1_r),
        ("substep_2_field_prestate_bit_exact", _field_vector(f1.field) == _field_vector(r1.field)),
        ("substep_2_adapter_expected_and_directed", _near(adapter_2_f, expected["adapter_2_F_HIGH"]) and _near(adapter_2_r, expected["adapter_2_R_HIGH"]) and adapter_2_f > adapter_2_r),
        ("substep_2_contrast_expected_and_directed", _near(contrast_2_f, expected["contrast_2_F_HIGH"]) and _near(contrast_2_r, expected["contrast_2_R_HIGH"]) and contrast_2_f < contrast_2_r),
        ("substep_2_separation_expected_and_above_floor", _near(separation, expected["complete_SH_separation"]) and separation > S1_IE_ROUNDOFF_FLOOR),
    )
    return _case(S1_IE_CASE_IDS[0], (f1, r1, f2, r2), (S1_IE_F_HIGH, S1_IE_R_HIGH), checks), metrics


def _run_n01(counter: list[int]) -> DTS1S1IECaseRecord:
    field = _initial_field(_INITIAL_H_MAIN)
    anatomy = _anatomy(field, _F_REFRACTORY)
    a1 = _call(field, anatomy, 0, 1, counter, enabled=True)
    b1 = _call(field, anatomy, 0, 1, counter, enabled=True)
    a2 = _call(a1.field, a1.anatomy, 1, 2, counter, enabled=True)
    b2 = _call(b1.field, b1.anatomy, 1, 2, counter, enabled=True)
    return _case(
        S1_IE_CASE_IDS[1],
        (a1, b1, a2, b2),
        (S1_IE_F_HIGH, S1_IE_F_HIGH),
        (("complete_pair_results_bit_exact", a1 == b1 and a2 == b2),),
    )


def _run_n02(counter: list[int]) -> DTS1S1IECaseRecord:
    field = _initial_field(_INITIAL_H_MAIN)
    f0 = _anatomy(field, _F_REFRACTORY)
    r0 = _anatomy(field, _R_REFRACTORY)
    f1 = _call(field, f0, 0, 1, counter, enabled=False)
    r1 = _call(field, r0, 0, 1, counter, enabled=False)
    f2 = _call(f1.field, f1.anatomy, 1, 2, counter, enabled=False)
    r2 = _call(r1.field, r1.anatomy, 1, 2, counter, enabled=False)
    return _case(
        S1_IE_CASE_IDS[2],
        (f1, r1, f2, r2),
        (S1_IE_F_HIGH, S1_IE_R_HIGH),
        (
            ("A0_substep_1_field_bit_exact", _field_vector(f1.field) == _field_vector(r1.field)),
            ("A0_substep_2_field_bit_exact", _field_vector(f2.field) == _field_vector(r2.field)),
            ("A0_adapters_base_rate", all(item.rate_per_second == 1.0 for result in (f1, r1, f2, r2) for item in result.applied_adapter.edge_rates)),
        ),
    )


def _run_n03(counter: list[int]) -> DTS1S1IECaseRecord:
    field = _initial_field(_INITIAL_H_MAIN)
    f0 = _anatomy(field, _F_REFRACTORY)
    r0 = _anatomy(field, _R_REFRACTORY)
    f1 = _call(field, f0, 0, 1, counter, enabled=True)
    r1 = _call(field, r0, 0, 1, counter, enabled=True)
    f2 = _call(f1.field, f0, 1, 2, counter, enabled=True)
    r2 = _call(r1.field, r0, 1, 2, counter, enabled=True)
    return _case(
        S1_IE_CASE_IDS[3],
        (f1, r1, f2, r2),
        (S1_IE_F_HIGH, S1_IE_R_HIGH),
        (
            ("frozen_substep_1_field_bit_exact", _field_vector(f1.field) == _field_vector(r1.field)),
            ("frozen_substep_2_field_bit_exact", _field_vector(f2.field) == _field_vector(r2.field)),
            ("frozen_b0_adapters_bit_exact", f1.applied_adapter == r1.applied_adapter and f2.applied_adapter == r2.applied_adapter),
        ),
    )


def _run_n04(counter: list[int]) -> DTS1S1IECaseRecord:
    field = _initial_field(_INITIAL_H_ZERO)
    f0 = _anatomy(field, _F_REFRACTORY)
    r0 = _anatomy(field, _R_REFRACTORY)
    f1 = _call(field, f0, 0, 1, counter, enabled=True)
    r1 = _call(field, r0, 0, 1, counter, enabled=True)
    f2 = _call(f1.field, f1.anatomy, 1, 2, counter, enabled=True)
    r2 = _call(r1.field, r1.anatomy, 1, 2, counter, enabled=True)
    expected = dict(S1_IE_EXPECTED)
    contrast_f = _contrast(f2.field)
    contrast_r = _contrast(r2.field)
    separation = _maximum_difference(_field_vector(f2.field), _field_vector(r2.field))
    return _case(
        S1_IE_CASE_IDS[4],
        (f1, r1, f2, r2),
        (S1_IE_F_HIGH, S1_IE_R_HIGH),
        (
            ("zero_H_substep_1_field_bit_exact", _field_vector(f1.field) == _field_vector(r1.field)),
            ("zero_H_substep_2_adapter_directed", f2.applied_adapter.edge_rates[0].rate_per_second > r2.applied_adapter.edge_rates[0].rate_per_second),
            ("zero_H_contrast_expected_and_directed", _near(contrast_f, expected["contrast_2_F_HIGH"]) and _near(contrast_r, expected["contrast_2_R_HIGH"]) and contrast_f < contrast_r),
            ("zero_H_separation_expected_and_above_floor", _near(separation, expected["complete_SH_separation"]) and separation > S1_IE_ROUNDOFF_FLOOR),
        ),
    )


def _baseline_records() -> tuple[tuple[str, str], ...]:
    return tuple(
        (baseline_id, _BASELINE_VALUE)
        for baseline_id, _ in S1_HZ_BASELINE_COUNTERPREDICTIONS
    )


def _execute_once() -> _DTS1S1IESingleAuditResult:
    counter = [0]
    c01, metrics = _run_c01(counter)
    cases = (
        c01,
        _run_n01(counter),
        _run_n02(counter),
        _run_n03(counter),
        _run_n04(counter),
    )
    reasons = []
    if counter[0] != S1_IE_SINGLE_AUDIT_FIELD_CALLS:
        reasons.append("technical-field-call-count-drift")
    if any(not value for case in cases for _, value in case.exact_checks):
        reasons.append("preregistered-causal-or-control-check-failed")
    if any(
        max(record.maximum_local_ledger_residual, record.global_ledger_residual)
        > S1_IE_ROUNDOFF_FLOOR
        for case in cases
        for record in case.step_records
    ):
        reasons.append("resource-ledger-residual-exceeds-floor")
    if any(
        abs(value - dict(S1_IE_EXPECTED)[name]) > S1_IE_ROUNDOFF_FLOOR
        for name, value in metrics
    ):
        reasons.append("primary-metric-deviates-from-preregistration")
    decision = S1_IE_PASS if not reasons else S1_IE_STOPP
    values = {
        "case_records": cases,
        "primary_metrics": metrics,
        "baseline_records": _baseline_records(),
        "technical_field_calls": counter[0],
        "research_field_steps": 0,
        "stopp_reasons": tuple(reasons),
        "decision": decision,
    }
    digest_payload = {
        **values,
        "case_records": [case.canonical_payload() for case in cases],
        "primary_metrics": [list(metric) for metric in metrics],
        "baseline_records": [list(record) for record in values["baseline_records"]],
        "stopp_reasons": list(values["stopp_reasons"]),
    }
    return _DTS1S1IESingleAuditResult(
        **values,
        receipt_digest=_digest(digest_payload),
    )


def execute_dts1_s1ie_preregistered_double_audit() -> DTS1S1IEDoubleAuditResult:
    """Execute exactly two deterministic 20-call technical field audits."""

    first = _execute_once()
    repeated = _execute_once()
    repeat_equal = first.receipt_digest == repeated.receipt_digest
    reasons = list(first.stopp_reasons)
    if repeated.stopp_reasons != first.stopp_reasons:
        reasons.append("repeat-stopp-reasons-differ")
    if not repeat_equal:
        reasons.append("repeated-receipt-digest-mismatch")
    decision = S1_IE_PASS if not reasons and repeat_equal else S1_IE_STOPP
    values = {
        "audit_id": S1_IE_AUDIT_ID,
        "source_s1id_contract_digest": S1_IE_SOURCE_S1ID_CONTRACT_DIGEST,
        "case_records": first.case_records,
        "primary_metrics": first.primary_metrics,
        "roundoff_floor": S1_IE_ROUNDOFF_FLOOR,
        "baseline_records": first.baseline_records,
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeated.receipt_digest,
        "repeated_receipts_identical": repeat_equal,
        "technical_field_calls": first.technical_field_calls + repeated.technical_field_calls,
        "research_field_steps": 0,
        "stopp_reasons": tuple(dict.fromkeys(reasons)),
        "decision": decision,
    }
    digest_payload = {
        **values,
        "case_records": [case.canonical_payload() for case in first.case_records],
        "primary_metrics": [list(metric) for metric in first.primary_metrics],
        "baseline_records": [list(record) for record in first.baseline_records],
        "stopp_reasons": list(values["stopp_reasons"]),
    }
    return DTS1S1IEDoubleAuditResult(
        **values,
        audit_receipt_digest=_digest(digest_payload),
    )
