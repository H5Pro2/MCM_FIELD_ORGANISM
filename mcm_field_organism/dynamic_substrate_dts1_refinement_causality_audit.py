"""Finite private S1-HY execution of the preregistered S1-HX audit."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

import numpy as np

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
from .dynamic_substrate_s1hx_refinement_causality_audit_contract import (
    S1_HX_PARTITIONS,
)
from .field_step_time import MCMFieldStepTime
from .mcm_substrate_state import mcm_substrate_edge_inventory
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class DTS1RefinementCausalityAuditError(ValueError):
    """Raised when the closed S1-HY audit result is internally invalid."""


S1_HY_AUDIT_ID = "dynamic-substrate.refinement-causality-audit.s1hy.v1"
S1_HY_SOURCE_S1HX_CONTRACT_DIGEST = (
    "168ab2c291fa6e0dca658e3b308c8c1879a988a652d60d19c29a98fefad2938e"
)
S1_HY_SCENARIO_IDS = (
    "C01_P0_A0_EXACT_REFINEMENT_CONTROL",
    "C02_ZERO_BINDING_CAUSAL_LATENCY",
    "C03_ACTIVE_COMPLETE_PAIR_REFINEMENT",
)
S1_HY_PARTITIONS = S1_HX_PARTITIONS
S1_HY_LATENCY_BOUNDS = (1.0, 0.5, 0.25)
S1_HY_SINGLE_EXECUTION_STEPS = 70
S1_HY_DOUBLE_EXECUTION_STEPS = 140
S1_HY_PASS = "PASS_DTS1_SYNTHETIC_REFINEMENT_AND_CAUSALITY"
S1_HY_STOPP = "STOPP_DTS1_SYNTHETIC_REFINEMENT_OR_CAUSALITY"

_TOTAL_TICKS = 8
_TICKS_PER_SECOND = 4.0
_INITIAL_S = (-0.8, 0.1, 0.7)
_INITIAL_H = (0.2, -0.1, 0.3)
_CONTACT = (0.9, -0.2, 0.4)
_CAPACITIES = (1.0, 1.0, 1.0)
_ACTIVE_RESOURCES = ((0.2, 0.1), (0.4, 0.2))
_ZERO_RESOURCES = ((0.0, 0.0), (0.0, 0.0))
_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
_DISSIPATION_CONFIG = NeutralFieldDissipationConfig(0.0)
_DTS1_RATES = DTS1StepRates(0.4, 0.3, 0.2)
_EPSILON_MULTIPLIER = 512.0


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
        raise DTS1RefinementCausalityAuditError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1RefinementCausalityAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1RefinementCausalityAuditError(
            f"{role} must be finite and nonnegative"
        )
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1HYScenarioRecord:
    scenario_id: str
    partitions: tuple[int, ...]
    latency_bounds: tuple[float, ...]
    level_pair_vectors: tuple[tuple[int, tuple[float, ...]], ...]
    exact_checks: tuple[tuple[str, bool], ...]
    numeric_metrics: tuple[tuple[str, float], ...]
    resource_states_valid: bool
    technical_field_steps: int

    def __post_init__(self) -> None:
        if self.scenario_id not in S1_HY_SCENARIO_IDS:
            raise DTS1RefinementCausalityAuditError("unknown S1-HY scenario")
        if self.partitions != S1_HY_PARTITIONS:
            raise DTS1RefinementCausalityAuditError(
                "scenario partitions must be exactly 2,4,8"
            )
        if self.latency_bounds != S1_HY_LATENCY_BOUNDS:
            raise DTS1RefinementCausalityAuditError(
                "scenario latency bounds must be exactly 1.0,0.5,0.25"
            )
        if tuple(level for level, _ in self.level_pair_vectors) != self.partitions:
            raise DTS1RefinementCausalityAuditError(
                "scenario requires one canonical pair vector per level"
            )
        vector_lengths = {len(vector) for _, vector in self.level_pair_vectors}
        if len(vector_lengths) != 1 or next(iter(vector_lengths), 0) == 0:
            raise DTS1RefinementCausalityAuditError(
                "scenario pair vectors must be complete and equally sized"
            )
        if any(
            not math.isfinite(value)
            for _, vector in self.level_pair_vectors
            for value in vector
        ):
            raise DTS1RefinementCausalityAuditError(
                "scenario pair vectors must be finite"
            )
        if not self.exact_checks or any(
            not isinstance(value, bool) for _, value in self.exact_checks
        ):
            raise DTS1RefinementCausalityAuditError(
                "scenario exact checks must be complete booleans"
            )
        metrics = tuple(
            (name, _finite_nonnegative(value, name))
            for name, value in self.numeric_metrics
        )
        if not isinstance(self.resource_states_valid, bool):
            raise DTS1RefinementCausalityAuditError(
                "scenario resource validity must be boolean"
            )
        expected_steps = 28 if self.scenario_id != S1_HY_SCENARIO_IDS[2] else 14
        if self.technical_field_steps != expected_steps:
            raise DTS1RefinementCausalityAuditError(
                "scenario technical step count differs from preregistration"
            )
        object.__setattr__(self, "numeric_metrics", metrics)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "scenario_id": self.scenario_id,
            "partitions": list(self.partitions),
            "latency_bounds": list(self.latency_bounds),
            "level_pair_vectors": [
                [level, list(vector)] for level, vector in self.level_pair_vectors
            ],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "numeric_metrics": [
                [name, value] for name, value in self.numeric_metrics
            ],
            "resource_states_valid": self.resource_states_valid,
            "technical_field_steps": self.technical_field_steps,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1HYSingleAuditResult:
    scenario_records: tuple[DTS1S1HYScenarioRecord, ...]
    active_r_n_2n: float
    active_r_2n_4n: float
    roundoff_floor: float
    technical_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            tuple(item.scenario_id for item in self.scenario_records)
            != S1_HY_SCENARIO_IDS
            or self.technical_field_steps != S1_HY_SINGLE_EXECUTION_STEPS
            or self.decision not in (S1_HY_PASS, S1_HY_STOPP)
            or (self.decision == S1_HY_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1RefinementCausalityAuditError(
                "single S1-HY audit result is incomplete or inconsistent"
            )
        for role in ("active_r_n_2n", "active_r_2n_4n", "roundoff_floor"):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "scenario_records": [
                item.canonical_payload() for item in self.scenario_records
            ],
            "active_r_n_2n": self.active_r_n_2n,
            "active_r_2n_4n": self.active_r_2n_4n,
            "roundoff_floor": self.roundoff_floor,
            "technical_field_steps": self.technical_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["receipt_digest"] = self.receipt_digest
        return payload


@dataclass(frozen=True, slots=True)
class DTS1S1HYDoubleAuditResult:
    audit_id: str
    source_s1hx_contract_digest: str
    scenario_records: tuple[DTS1S1HYScenarioRecord, ...]
    active_r_n_2n: float
    active_r_2n_4n: float
    roundoff_floor: float
    first_receipt_digest: str
    repeat_receipt_digest: str
    repeated_receipts_identical: bool
    technical_field_steps: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    audit_receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            self.audit_id != S1_HY_AUDIT_ID
            or self.source_s1hx_contract_digest
            != S1_HY_SOURCE_S1HX_CONTRACT_DIGEST
            or tuple(item.scenario_id for item in self.scenario_records)
            != S1_HY_SCENARIO_IDS
            or self.repeated_receipts_identical
            != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.technical_field_steps != S1_HY_DOUBLE_EXECUTION_STEPS
            or self.research_field_steps != 0
            or self.decision not in (S1_HY_PASS, S1_HY_STOPP)
            or (self.decision == S1_HY_PASS)
            != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(payload)
        ):
            raise DTS1RefinementCausalityAuditError(
                "double S1-HY audit result violates the preregistered boundary"
            )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1hx_contract_digest": self.source_s1hx_contract_digest,
            "scenario_records": [
                item.canonical_payload() for item in self.scenario_records
            ],
            "active_r_n_2n": self.active_r_n_2n,
            "active_r_2n_4n": self.active_r_2n_4n,
            "roundoff_floor": self.roundoff_floor,
            "first_receipt_digest": self.first_receipt_digest,
            "repeat_receipt_digest": self.repeat_receipt_digest,
            "repeated_receipts_identical": self.repeated_receipts_identical,
            "technical_field_steps": self.technical_field_steps,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["audit_receipt_digest"] = self.audit_receipt_digest
        return payload


def _reference_frame(snapshot_id: str, values: tuple[float, ...]) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=snapshot_id,
        clock_id="synthetic.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(f"auditory.carrier.{index}" for index in range(3)),
        values=values,
    )


def _initial_field() -> SharedMCMField:
    field = build_shared_mcm_field(
        (_reference_frame("s1hy.reference", (0.0, 0.0, 0.0)),),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,), (2,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(
        replace(
            neuron,
            activation=_INITIAL_S[index],
            afterimage=_INITIAL_H[index],
        )
        for index, neuron in enumerate(field.layer.neurons)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _initial_anatomy(
    field: SharedMCMField,
    resources: tuple[tuple[float, float], ...],
) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(
            DTS1NodeCapacity(neuron.neuron_id, capacity)
            for neuron, capacity in zip(
                field.layer.neurons,
                _CAPACITIES,
                strict=True,
            )
        ),
        tuple(
            DTS1EdgeResource(*edge, conductive, refractory)
            for edge, (conductive, refractory) in zip(
                mcm_substrate_edge_inventory(field.layer),
                resources,
                strict=True,
            )
        ),
    )


def _distribution(start_tick: int, end_tick: int, snapshot_id: str):
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", "auditory.line.v1")
    )
    return distributor.distribute(
        (_reference_frame(snapshot_id, _CONTACT),),
        CommonFieldTime("organism.s1hy", start_tick, end_tick),
    )


def _step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.s1hy",
        start_tick,
        end_tick,
        _TICKS_PER_SECOND,
    )


def _pair_vector(
    field: SharedMCMField,
    anatomy: DTS1ResourceAnatomy,
) -> tuple[float, ...]:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    capacities = {item.node_id: item.capacity for item in anatomy.node_capacities}
    conductive = []
    refractory = []
    for edge in anatomy.edge_resources:
        denominator = 2.0 * min(
            capacities[edge.first_node_id],
            capacities[edge.second_node_id],
        )
        conductive.append(edge.conductive_bound / denominator)
        refractory.append(edge.refractory / denominator)
    return tuple(
        [item.activation for item in neurons]
        + [item.afterimage for item in neurons]
        + conductive
        + refractory
    )


def _maximum_difference(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        raise DTS1RefinementCausalityAuditError(
            "residual requires two complete equally sized vectors"
        )
    return max(abs(first - second) for first, second in zip(left, right, strict=True))


def _roundoff_floor(vectors: tuple[tuple[float, ...], ...]) -> float:
    scale = max(1.0, *(abs(value) for vector in vectors for value in vector))
    return _EPSILON_MULTIPLIER * float(np.finfo(np.float64).eps) * scale


def _resource_valid(result: DTS1CoupledFastFieldStepResult) -> bool:
    anatomy = result.anatomy
    scale = max(1.0, anatomy.global_capacity)
    tolerance = _EPSILON_MULTIPLIER * float(np.finfo(np.float64).eps) * scale
    local = max((abs(item.residual) for item in anatomy.local_ledgers()), default=0.0)
    return (
        math.isfinite(local)
        and math.isfinite(anatomy.global_residual)
        and local <= tolerance
        and abs(anatomy.global_residual) <= tolerance
    )


def _run_c01(counter: list[int]) -> DTS1S1HYScenarioRecord:
    vectors = []
    exact = True
    resource_valid = True
    for partitions in S1_HY_PARTITIONS:
        p0_field = _initial_field()
        a0_field = _initial_field()
        a0_anatomy = _initial_anatomy(a0_field, _ACTIVE_RESOURCES)
        step_ticks = _TOTAL_TICKS // partitions
        for index in range(partitions):
            start = index * step_ticks
            end = (index + 1) * step_ticks
            world = _distribution(start, end, f"s1hy.c01.p{partitions}.s{index}")
            interval = _step(start, end)
            p0_field = advance_neutral_fast_shared_field(
                p0_field,
                world,
                interval,
                _SUBSTRATE_CONFIG,
                _AFTERIMAGE_CONFIG,
                _DISSIPATION_CONFIG,
            )
            counter[0] += 1
            result = advance_dts1_coupled_fast_shared_field(
                a0_field,
                a0_anatomy,
                world,
                interval,
                _SUBSTRATE_CONFIG,
                _AFTERIMAGE_CONFIG,
                _DTS1_RATES,
                _DISSIPATION_CONFIG,
                backreaction_enabled=False,
            )
            counter[0] += 1
            a0_field, a0_anatomy = result.field, result.anatomy
            exact = exact and (
                p0_field.snapshot().digest() == a0_field.snapshot().digest()
            )
            resource_valid = resource_valid and _resource_valid(result)
        vectors.append((partitions, _pair_vector(a0_field, a0_anatomy)))
    return DTS1S1HYScenarioRecord(
        scenario_id=S1_HY_SCENARIO_IDS[0],
        partitions=S1_HY_PARTITIONS,
        latency_bounds=S1_HY_LATENCY_BOUNDS,
        level_pair_vectors=tuple(vectors),
        exact_checks=(("P0_A0_every_substep_bit_exact", exact),),
        numeric_metrics=(),
        resource_states_valid=resource_valid,
        technical_field_steps=28,
    )


def _run_c02(counter: list[int]) -> DTS1S1HYScenarioRecord:
    vectors = []
    first_field_exact = True
    first_resource_exact = True
    positive_binding = True
    resource_valid = True
    separations = []
    above_floor = True
    for partitions in S1_HY_PARTITIONS:
        a0_field = _initial_field()
        a1_field = _initial_field()
        a0_anatomy = _initial_anatomy(a0_field, _ZERO_RESOURCES)
        a1_anatomy = _initial_anatomy(a1_field, _ZERO_RESOURCES)
        step_ticks = _TOTAL_TICKS // partitions
        for index in range(partitions):
            start = index * step_ticks
            end = (index + 1) * step_ticks
            world = _distribution(start, end, f"s1hy.c02.p{partitions}.s{index}")
            interval = _step(start, end)
            a0_result = advance_dts1_coupled_fast_shared_field(
                a0_field,
                a0_anatomy,
                world,
                interval,
                _SUBSTRATE_CONFIG,
                _AFTERIMAGE_CONFIG,
                _DTS1_RATES,
                _DISSIPATION_CONFIG,
                backreaction_enabled=False,
            )
            counter[0] += 1
            a1_result = advance_dts1_coupled_fast_shared_field(
                a1_field,
                a1_anatomy,
                world,
                interval,
                _SUBSTRATE_CONFIG,
                _AFTERIMAGE_CONFIG,
                _DTS1_RATES,
                _DISSIPATION_CONFIG,
                backreaction_enabled=True,
            )
            counter[0] += 1
            if index == 0:
                first_field_exact = first_field_exact and (
                    a0_result.field.snapshot().digest()
                    == a1_result.field.snapshot().digest()
                )
                first_resource_exact = first_resource_exact and (
                    a0_result.anatomy == a1_result.anatomy
                    and a0_result.resource_transfers == a1_result.resource_transfers
                )
                positive_binding = positive_binding and any(
                    item.conductive_bound > 0.0
                    for item in a1_result.anatomy.edge_resources
                )
            resource_valid = (
                resource_valid
                and _resource_valid(a0_result)
                and _resource_valid(a1_result)
            )
            a0_field, a0_anatomy = a0_result.field, a0_result.anatomy
            a1_field, a1_anatomy = a1_result.field, a1_result.anatomy
        a0_vector = _pair_vector(a0_field, a0_anatomy)
        a1_vector = _pair_vector(a1_field, a1_anatomy)
        field_components = 2 * len(a0_field.layer.neurons)
        separation = _maximum_difference(
            a0_vector[:field_components],
            a1_vector[:field_components],
        )
        floor = _roundoff_floor(
            (a0_vector[:field_components], a1_vector[:field_components])
        )
        separations.append(separation)
        above_floor = above_floor and separation > floor
        vectors.append((partitions, a1_vector))
    return DTS1S1HYScenarioRecord(
        scenario_id=S1_HY_SCENARIO_IDS[1],
        partitions=S1_HY_PARTITIONS,
        latency_bounds=S1_HY_LATENCY_BOUNDS,
        level_pair_vectors=tuple(vectors),
        exact_checks=(
            ("first_field_exact", first_field_exact),
            ("first_resource_exact", first_resource_exact),
            ("positive_new_binding", positive_binding),
            ("later_field_separation_above_floor", above_floor),
            ("latency_bounds_halve", S1_HY_LATENCY_BOUNDS == (1.0, 0.5, 0.25)),
        ),
        numeric_metrics=tuple(
            (f"final_field_separation_p{partitions}", separation)
            for partitions, separation in zip(
                S1_HY_PARTITIONS,
                separations,
                strict=True,
            )
        ),
        resource_states_valid=resource_valid,
        technical_field_steps=28,
    )


def _run_c03(counter: list[int]) -> DTS1S1HYScenarioRecord:
    vectors = []
    resource_valid = True
    for partitions in S1_HY_PARTITIONS:
        field = _initial_field()
        anatomy = _initial_anatomy(field, _ACTIVE_RESOURCES)
        step_ticks = _TOTAL_TICKS // partitions
        for index in range(partitions):
            start = index * step_ticks
            end = (index + 1) * step_ticks
            result = advance_dts1_coupled_fast_shared_field(
                field,
                anatomy,
                _distribution(start, end, f"s1hy.c03.p{partitions}.s{index}"),
                _step(start, end),
                _SUBSTRATE_CONFIG,
                _AFTERIMAGE_CONFIG,
                _DTS1_RATES,
                _DISSIPATION_CONFIG,
                backreaction_enabled=True,
            )
            counter[0] += 1
            resource_valid = resource_valid and _resource_valid(result)
            field, anatomy = result.field, result.anatomy
        vectors.append((partitions, _pair_vector(field, anatomy)))
    return DTS1S1HYScenarioRecord(
        scenario_id=S1_HY_SCENARIO_IDS[2],
        partitions=S1_HY_PARTITIONS,
        latency_bounds=S1_HY_LATENCY_BOUNDS,
        level_pair_vectors=tuple(vectors),
        exact_checks=(("all_active_pair_states_valid", resource_valid),),
        numeric_metrics=(),
        resource_states_valid=resource_valid,
        technical_field_steps=14,
    )


def _execute_once() -> _DTS1S1HYSingleAuditResult:
    counter = [0]
    scenarios = (_run_c01(counter), _run_c02(counter), _run_c03(counter))
    active_vectors = tuple(vector for _, vector in scenarios[2].level_pair_vectors)
    r_n_2n = _maximum_difference(active_vectors[0], active_vectors[1])
    r_2n_4n = _maximum_difference(active_vectors[1], active_vectors[2])
    floor = _roundoff_floor(active_vectors)
    reasons = []
    if counter[0] != S1_HY_SINGLE_EXECUTION_STEPS:
        reasons.append("technical-field-step-count-mismatch")
    if any(not all(value for _, value in item.exact_checks) for item in scenarios):
        reasons.append("exact-or-causal-identity-failed")
    if any(not item.resource_states_valid for item in scenarios):
        reasons.append("resource-state-validity-failed")
    if r_n_2n <= floor:
        reasons.append("active-coarse-fine-residual-at-or-below-floor")
    if r_2n_4n >= r_n_2n:
        reasons.append("active-fine-residual-not-strictly-smaller")
    decision = S1_HY_PASS if not reasons else S1_HY_STOPP
    values = {
        "scenario_records": scenarios,
        "active_r_n_2n": r_n_2n,
        "active_r_2n_4n": r_2n_4n,
        "roundoff_floor": floor,
        "technical_field_steps": counter[0],
        "stopp_reasons": tuple(reasons),
        "decision": decision,
    }
    digest_payload = {
        "scenario_records": [item.canonical_payload() for item in scenarios],
        "active_r_n_2n": r_n_2n,
        "active_r_2n_4n": r_2n_4n,
        "roundoff_floor": floor,
        "technical_field_steps": counter[0],
        "stopp_reasons": reasons,
        "decision": decision,
    }
    return _DTS1S1HYSingleAuditResult(
        **values,
        receipt_digest=_digest(digest_payload),
    )


def execute_dts1_s1hy_preregistered_double_audit() -> DTS1S1HYDoubleAuditResult:
    """Execute exactly two deterministic 70-step synthetic audits atomically."""

    first = _execute_once()
    repeated = _execute_once()
    repeat_equal = first.receipt_digest == repeated.receipt_digest
    reasons = list(first.stopp_reasons)
    if repeated.stopp_reasons != first.stopp_reasons:
        reasons.append("repeat-stopp-reasons-differ")
    if not repeat_equal:
        reasons.append("repeated-receipt-digest-mismatch")
    decision = S1_HY_PASS if not reasons and repeat_equal else S1_HY_STOPP
    values = {
        "audit_id": S1_HY_AUDIT_ID,
        "source_s1hx_contract_digest": S1_HY_SOURCE_S1HX_CONTRACT_DIGEST,
        "scenario_records": first.scenario_records,
        "active_r_n_2n": first.active_r_n_2n,
        "active_r_2n_4n": first.active_r_2n_4n,
        "roundoff_floor": first.roundoff_floor,
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeated.receipt_digest,
        "repeated_receipts_identical": repeat_equal,
        "technical_field_steps": (
            first.technical_field_steps + repeated.technical_field_steps
        ),
        "research_field_steps": 0,
        "stopp_reasons": tuple(dict.fromkeys(reasons)),
        "decision": decision,
    }
    digest_payload = {
        **values,
        "scenario_records": [
            item.canonical_payload() for item in first.scenario_records
        ],
        "stopp_reasons": list(values["stopp_reasons"]),
    }
    return DTS1S1HYDoubleAuditResult(
        **values,
        audit_receipt_digest=_digest(digest_payload),
    )
