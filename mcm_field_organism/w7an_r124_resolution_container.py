"""Additive W7-AN R1/R2/R4 CAP resolution container without evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .mcm_f3_runtime import MCMF3AdvanceDiagnostics
from .w7aa_p0_seven_path_consumer import W7AAP0SevenPathResult
from .w7ac_observer_seven_path_consumer import W7ACObserverSevenPathResult
from .w7ae_cap_seven_path_consumer import (
    W7AECAPProductionResult,
    W7AECAPSevenPathResult,
    consume_w7ae_cap_seven_path_plan,
)
from .w7ag_passive_cap_measurement_handoff import (
    W7AGPassiveCAPMeasurementHandoff,
    compose_w7ag_passive_cap_measurement_handoff,
)
from .w7ai_p0_zero_start_measurement_reference import (
    W7AIP0ZeroStartMeasurementReferences,
)
from .w7ak_cap_p0_raw_contrast_compositor import (
    W7AKRawContrastComposition,
    W7AKRawContrastPair,
    _build_pair,
    compose_w7ak_cap_p0_raw_contrasts,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import (
    W7YSevenPathSourcePlan,
    W7YSourceSegmentRef,
)


class W7ANResolutionContainerError(ValueError):
    """Raised when the additive resolution container leaves W7-AM."""


_CONTAINER_ID = "w7an.cap-r1-r2-r4-resolution-container.v1"
_RESOLUTIONS = (("r1", 1), ("r2", 2), ("r4", 4))
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_CANONICAL_CAP_DIGEST = (
    "b70a4b4563bb73d50685d1a8475376f0b00377d72369c030027f44f2725af013"
)
_CANONICAL_HANDOFF_DIGEST = (
    "898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8"
)
_CANONICAL_RAW_DIGEST = (
    "ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3"
)
_P0_REFERENCE_DIGEST = (
    "8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_nonnegative(value, role: str) -> float:
    if isinstance(value, bool):
        raise W7ANResolutionContainerError(f"{role} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise W7ANResolutionContainerError(
            f"{role} must be finite and nonnegative"
        )
    return result


def _witness_payload(
    resolution_id: str,
    refinement: int,
    scope: str,
    path_id: str,
    segment_digest: str,
    interval: tuple[int, int],
    production_digest: str,
    diagnostics: MCMF3AdvanceDiagnostics,
) -> dict[str, object]:
    return {
        "resolution_id": resolution_id,
        "refinement": refinement,
        "scope": scope,
        "path_id": path_id,
        "segment_digest": segment_digest,
        "interval": interval,
        "production_digest": production_digest,
        "method_id": diagnostics.method_id,
        "substep_count": diagnostics.substep_count,
        "safe_step_seconds": diagnostics.safe_step_seconds,
        "maximum_step_seconds": diagnostics.maximum_step_seconds,
    }


@dataclass(frozen=True, slots=True)
class W7ANIntegrationWitness:
    """External evidence for one actual CAP integration call."""

    resolution_id: str
    refinement: int
    scope: str
    path_id: str
    segment_digest: str
    interval: tuple[int, int]
    production_digest: str
    method_id: str
    substep_count: int
    safe_step_seconds: float
    maximum_step_seconds: float
    witness_digest: str

    def __post_init__(self) -> None:
        if (
            (self.resolution_id, self.refinement) not in _RESOLUTIONS
            or self.scope not in {"main", "probe", "measurement"}
            or self.path_id not in _PATH_IDS
            or not self.segment_digest
            or not self.production_digest
            or self.method_id != "ssprk33"
            or isinstance(self.substep_count, bool)
            or not isinstance(self.substep_count, int)
            or self.substep_count < 1
        ):
            raise W7ANResolutionContainerError(
                "integration witness binding is invalid"
            )
        start, end = self.interval
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or end <= start
        ):
            raise W7ANResolutionContainerError(
                "integration witness interval is invalid"
            )
        safe_step = _finite_nonnegative(
            self.safe_step_seconds,
            "safe_step_seconds",
        )
        maximum_step = _finite_nonnegative(
            self.maximum_step_seconds,
            "maximum_step_seconds",
        )
        diagnostics = MCMF3AdvanceDiagnostics(
            self.method_id,
            self.substep_count,
            self.refinement,
            safe_step,
            maximum_step,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        payload = _witness_payload(
            self.resolution_id,
            self.refinement,
            self.scope,
            self.path_id,
            self.segment_digest,
            self.interval,
            self.production_digest,
            diagnostics,
        )
        if self.witness_digest != _digest(payload):
            raise W7ANResolutionContainerError(
                "integration witness digest does not match its content"
            )
        object.__setattr__(self, "safe_step_seconds", safe_step)
        object.__setattr__(self, "maximum_step_seconds", maximum_step)


def _build_witness(
    resolution_id: str,
    refinement: int,
    scope: str,
    segment: W7YSourceSegmentRef,
    production: W7AECAPProductionResult,
    diagnostics: MCMF3AdvanceDiagnostics,
) -> W7ANIntegrationWitness:
    if (
        diagnostics.refinement != refinement
        or production.segment_digest != segment.segment_digest
        or production.interval != segment.interval
    ):
        raise W7ANResolutionContainerError(
            "runtime diagnostics differ from their production"
        )
    payload = _witness_payload(
        resolution_id,
        refinement,
        scope,
        segment.path_id,
        segment.segment_digest,
        segment.interval,
        production.production_digest,
        diagnostics,
    )
    return W7ANIntegrationWitness(
        resolution_id,
        refinement,
        scope,
        segment.path_id,
        segment.segment_digest,
        segment.interval,
        production.production_digest,
        diagnostics.method_id,
        diagnostics.substep_count,
        diagnostics.safe_step_seconds,
        diagnostics.maximum_step_seconds,
        _digest(payload),
    )


def _pair_container_payload(
    resolution_id: str,
    refinement: int,
    cap_handoff_digest: str,
    p0_reference_digest: str,
    pairs: tuple[W7AKRawContrastPair, ...],
    order_countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "resolution_id": resolution_id,
        "refinement": refinement,
        "cap_handoff_digest": cap_handoff_digest,
        "p0_reference_digest": p0_reference_digest,
        "pair_digests": tuple(item.raw_contrast_pair_digest for item in pairs),
        "order_countercontrol_digest": order_countercontrol_digest,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7ANResolutionPairContainer:
    """One resolution's 35 CAP/P0 pairs without convergence comparison."""

    resolution_id: str
    refinement: int
    cap_handoff_digest: str
    p0_reference_digest: str
    pairs: tuple[W7AKRawContrastPair, ...] = field(repr=False)
    order_countercontrol_digest: str
    evaluated: bool
    pair_container_digest: str

    def __post_init__(self) -> None:
        pairs = tuple(self.pairs)
        expected_roles = tuple(
            (path_id, checkpoint)
            for path_id in _PATH_IDS
            for checkpoint in range(5)
        )
        if (
            (self.resolution_id, self.refinement) not in _RESOLUTIONS
            or not self.cap_handoff_digest
            or self.p0_reference_digest != _P0_REFERENCE_DIGEST
            or tuple((item.path_id, item.checkpoint) for item in pairs)
            != expected_roles
            or not self.order_countercontrol_digest
            or self.evaluated is not False
        ):
            raise W7ANResolutionContainerError(
                "resolution pair container binding is invalid"
            )
        payload = _pair_container_payload(
            self.resolution_id,
            self.refinement,
            self.cap_handoff_digest,
            self.p0_reference_digest,
            pairs,
            self.order_countercontrol_digest,
        )
        if self.pair_container_digest != _digest(payload):
            raise W7ANResolutionContainerError(
                "resolution pair container digest differs"
            )
        object.__setattr__(self, "pairs", pairs)


def _build_pair_container(
    resolution_id: str,
    refinement: int,
    cap_handoff: W7AGPassiveCAPMeasurementHandoff,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
) -> W7ANResolutionPairContainer:
    cap_by_role = {
        (item.path_id, item.checkpoint): item
        for item in cap_handoff.measurements
    }
    p0_by_role = {
        (item.path_id, item.checkpoint): item
        for item in p0_references.references
    }
    roles = tuple(
        (path_id, checkpoint)
        for path_id in _PATH_IDS
        for checkpoint in range(5)
    )
    if tuple(cap_by_role) != roles or tuple(p0_by_role) != roles:
        raise W7ANResolutionContainerError(
            "resolution pair inventories differ"
        )
    pairs = tuple(
        _build_pair(cap_by_role[role], p0_by_role[role]) for role in roles
    )
    reversed_pairs = tuple(
        _build_pair(cap_by_role[role], p0_by_role[role])
        for role in reversed(roles)
    )
    actual = {
        (item.path_id, item.checkpoint): item.raw_contrast_pair_digest
        for item in pairs
    }
    if any(
        actual[(item.path_id, item.checkpoint)]
        != item.raw_contrast_pair_digest
        for item in reversed_pairs
    ):
        raise W7ANResolutionContainerError(
            "resolution pair order changed a result"
        )
    order_digest = _digest(
        {
            "canonical_pair_digests": tuple(
                item.raw_contrast_pair_digest for item in pairs
            ),
            "reverse_role_digests": tuple(
                actual[(item.path_id, item.checkpoint)]
                for item in reversed(pairs)
            ),
        }
    )
    payload = _pair_container_payload(
        resolution_id,
        refinement,
        cap_handoff.measurement_handoff_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
        pairs,
        order_digest,
    )
    return W7ANResolutionPairContainer(
        resolution_id,
        refinement,
        cap_handoff.measurement_handoff_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
        pairs,
        order_digest,
        False,
        _digest(payload),
    )


def _resolution_payload(
    resolution_id: str,
    refinement: int,
    plan_digest: str,
    cap_digest: str,
    production_witnesses: tuple[W7ANIntegrationWitness, ...],
    handoff_digest: str,
    measurement_witnesses: tuple[W7ANIntegrationWitness, ...],
    pair_container_digest: str,
    p0_reference_digest: str,
) -> dict[str, object]:
    return {
        "resolution_id": resolution_id,
        "refinement": refinement,
        "plan_digest": plan_digest,
        "cap_digest": cap_digest,
        "production_witness_digests": tuple(
            item.witness_digest for item in production_witnesses
        ),
        "handoff_digest": handoff_digest,
        "measurement_witness_digests": tuple(
            item.witness_digest for item in measurement_witnesses
        ),
        "pair_container_digest": pair_container_digest,
        "p0_reference_digest": p0_reference_digest,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7ANResolutionResult:
    """One complete CAP resolution with external integration evidence."""

    resolution_id: str
    refinement: int
    plan_digest: str
    cap_result: W7AECAPSevenPathResult = field(repr=False)
    production_witnesses: tuple[W7ANIntegrationWitness, ...] = field(repr=False)
    cap_handoff: W7AGPassiveCAPMeasurementHandoff = field(repr=False)
    measurement_witnesses: tuple[W7ANIntegrationWitness, ...] = field(repr=False)
    pair_container: W7ANResolutionPairContainer = field(repr=False)
    p0_references: W7AIP0ZeroStartMeasurementReferences = field(repr=False)
    evaluated: bool
    resolution_result_digest: str

    def __post_init__(self) -> None:
        production = tuple(self.production_witnesses)
        measurement = tuple(self.measurement_witnesses)
        if (
            (self.resolution_id, self.refinement) not in _RESOLUTIONS
            or self.cap_result.plan_digest != self.plan_digest
            or self.cap_handoff.plan_digest != self.plan_digest
            or self.cap_handoff.cap_consumption_digest
            != self.cap_result.cap_seven_path_consumption_digest
            or len(production) != 67
            or sum(item.scope == "main" for item in production) != 32
            or sum(item.scope == "probe" for item in production) != 35
            or len(measurement) != 35
            or any(item.scope != "measurement" for item in measurement)
            or any(
                item.resolution_id != self.resolution_id
                or item.refinement != self.refinement
                for item in production + measurement
            )
            or self.pair_container.resolution_id != self.resolution_id
            or self.pair_container.refinement != self.refinement
            or self.pair_container.cap_handoff_digest
            != self.cap_handoff.measurement_handoff_digest
            or self.p0_references.p0_zero_start_measurement_reference_digest
            != _P0_REFERENCE_DIGEST
            or self.pair_container.p0_reference_digest != _P0_REFERENCE_DIGEST
            or self.evaluated is not False
        ):
            raise W7ANResolutionContainerError(
                "resolution result binding is invalid"
            )
        payload = _resolution_payload(
            self.resolution_id,
            self.refinement,
            self.plan_digest,
            self.cap_result.cap_seven_path_consumption_digest,
            production,
            self.cap_handoff.measurement_handoff_digest,
            measurement,
            self.pair_container.pair_container_digest,
            _P0_REFERENCE_DIGEST,
        )
        if self.resolution_result_digest != _digest(payload):
            raise W7ANResolutionContainerError(
                "resolution result digest differs"
            )
        object.__setattr__(self, "production_witnesses", production)
        object.__setattr__(self, "measurement_witnesses", measurement)


def _build_resolution(
    resolution_id: str,
    refinement: int,
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
) -> W7ANResolutionResult:
    production_witnesses = []
    measurement_witnesses = []

    def observe_production(segment, production, diagnostics):
        production_witnesses.append(
            _build_witness(
                resolution_id,
                refinement,
                segment.branch_kind,
                segment,
                production,
                diagnostics,
            )
        )
        return None

    def observe_measurement(segment, production, diagnostics):
        measurement_witnesses.append(
            _build_witness(
                resolution_id,
                refinement,
                "measurement",
                segment,
                production,
                diagnostics,
            )
        )
        return None

    cap_result = consume_w7ae_cap_seven_path_plan(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        _refinement=refinement,
        _integration_observer=observe_production,
    )
    cap_handoff = compose_w7ag_passive_cap_measurement_handoff(
        adapter,
        family,
        authorization,
        plan,
        cap_result,
        _refinement=refinement,
        _integration_observer=observe_measurement,
    )
    pair_container = _build_pair_container(
        resolution_id,
        refinement,
        cap_handoff,
        p0_references,
    )
    production = tuple(production_witnesses)
    measurement = tuple(measurement_witnesses)
    payload = _resolution_payload(
        resolution_id,
        refinement,
        plan.seven_path_plan_digest,
        cap_result.cap_seven_path_consumption_digest,
        production,
        cap_handoff.measurement_handoff_digest,
        measurement,
        pair_container.pair_container_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
    )
    return W7ANResolutionResult(
        resolution_id,
        refinement,
        plan.seven_path_plan_digest,
        cap_result,
        production,
        cap_handoff,
        measurement,
        pair_container,
        p0_references,
        False,
        _digest(payload),
    )


def _container_payload(
    plan_digest: str,
    p0_reference_digest: str,
    resolutions: tuple[W7ANResolutionResult, ...],
    r1_compatibility_digest: str,
    start_separation_digest: str,
    substep_order_digest: str,
) -> dict[str, object]:
    return {
        "container_id": _CONTAINER_ID,
        "plan_digest": plan_digest,
        "p0_reference_digest": p0_reference_digest,
        "resolution_result_digests": tuple(
            item.resolution_result_digest for item in resolutions
        ),
        "r1_compatibility_digest": r1_compatibility_digest,
        "start_separation_digest": start_separation_digest,
        "substep_order_digest": substep_order_digest,
        "convergence_compared": False,
        "effect_floor_ready": False,
    }


@dataclass(frozen=True, slots=True)
class W7ANR124ResolutionContainer:
    """Complete additive R1/R2/R4 materialization without comparison."""

    container_id: str
    plan_digest: str
    p0_reference_digest: str
    resolutions: tuple[W7ANResolutionResult, ...] = field(repr=False)
    r1_compatibility_digest: str
    start_separation_digest: str
    substep_order_digest: str
    convergence_compared: bool
    effect_floor_ready: bool
    resolution_container_digest: str

    def __post_init__(self) -> None:
        resolutions = tuple(self.resolutions)
        if (
            self.container_id != _CONTAINER_ID
            or self.p0_reference_digest != _P0_REFERENCE_DIGEST
            or tuple(
                (item.resolution_id, item.refinement) for item in resolutions
            )
            != _RESOLUTIONS
            or any(item.plan_digest != self.plan_digest for item in resolutions)
            or len({id(item.p0_references) for item in resolutions}) != 1
            or not self.r1_compatibility_digest
            or not self.start_separation_digest
            or not self.substep_order_digest
            or self.convergence_compared is not False
            or self.effect_floor_ready is not False
        ):
            raise W7ANResolutionContainerError(
                "resolution container binding is invalid"
            )
        payload = _container_payload(
            self.plan_digest,
            self.p0_reference_digest,
            resolutions,
            self.r1_compatibility_digest,
            self.start_separation_digest,
            self.substep_order_digest,
        )
        if self.resolution_container_digest != _digest(payload):
            raise W7ANResolutionContainerError(
                "resolution container digest differs"
            )
        object.__setattr__(self, "resolutions", resolutions)


def _validate_w7an_canonical_inputs(
    plan: W7YSevenPathSourcePlan,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
    canonical_cap: W7AECAPSevenPathResult,
    canonical_handoff: W7AGPassiveCAPMeasurementHandoff,
    canonical_raw: W7AKRawContrastComposition,
) -> tuple[str, str, str, str]:
    if (
        canonical_cap.cap_seven_path_consumption_digest != _CANONICAL_CAP_DIGEST
        or canonical_handoff.measurement_handoff_digest
        != _CANONICAL_HANDOFF_DIGEST
        or canonical_raw.raw_contrast_composition_digest != _CANONICAL_RAW_DIGEST
        or p0_references.p0_zero_start_measurement_reference_digest
        != _P0_REFERENCE_DIGEST
        or any(
            item.plan_digest != plan.seven_path_plan_digest
            for item in (
                canonical_cap,
                canonical_handoff,
                canonical_raw,
                p0_references,
            )
        )
    ):
        raise W7ANResolutionContainerError(
            "resolution container canonical inputs differ"
        )
    return (
        canonical_cap.cap_seven_path_consumption_digest,
        canonical_handoff.measurement_handoff_digest,
        canonical_raw.raw_contrast_composition_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
    )


def _finalize_w7an_r124_resolution_results(
    plan: W7YSevenPathSourcePlan,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
    canonical_cap: W7AECAPSevenPathResult,
    canonical_handoff: W7AGPassiveCAPMeasurementHandoff,
    canonical_raw: W7AKRawContrastComposition,
    resolutions: tuple[W7ANResolutionResult, ...],
) -> W7ANR124ResolutionContainer:
    """Finalize three completed resolutions without another integration."""

    canonical_digests = _validate_w7an_canonical_inputs(
        plan,
        p0_references,
        canonical_cap,
        canonical_handoff,
        canonical_raw,
    )
    resolutions = tuple(resolutions)
    if (
        tuple(
            (item.resolution_id, item.refinement) for item in resolutions
        )
        != _RESOLUTIONS
        or any(item.plan_digest != plan.seven_path_plan_digest for item in resolutions)
        or any(item.p0_references is not p0_references for item in resolutions)
    ):
        raise W7ANResolutionContainerError(
            "completed resolution inventory differs"
        )
    r1 = resolutions[0]
    r1_raw = compose_w7ak_cap_p0_raw_contrasts(
        r1.cap_handoff,
        p0_references,
    )
    if (
        r1.cap_result.cap_seven_path_consumption_digest != _CANONICAL_CAP_DIGEST
        or r1.cap_handoff.measurement_handoff_digest
        != _CANONICAL_HANDOFF_DIGEST
        or r1_raw.raw_contrast_composition_digest != _CANONICAL_RAW_DIGEST
    ):
        raise W7ANResolutionContainerError(
            "explicit R1 path differs from canonical W7-AE/AG/AK"
        )
    r1_digest = _digest(
        {
            "cap_digest": _CANONICAL_CAP_DIGEST,
            "handoff_digest": _CANONICAL_HANDOFF_DIGEST,
            "raw_digest": _CANONICAL_RAW_DIGEST,
        }
    )
    starts = tuple(
        resolution.cap_result.path_results[0].initial_state
        for resolution in resolutions
    )
    if (
        len({item.state_digest for item in starts}) != 1
        or len({id(item) for item in starts}) != 3
        or len({id(item.field) for item in starts}) != 3
        or len({id(item.field.layer) for item in starts}) != 3
        or len({id(item.field.docks) for item in starts}) != 3
        or len({id(item.field.substrate) for item in starts}) != 3
    ):
        raise W7ANResolutionContainerError(
            "resolution starts are not equal and independent"
        )
    start_digest = _digest(
        {
            "state_digest": starts[0].state_digest,
            "resolution_ids": tuple(item.resolution_id for item in resolutions),
            "separate_states": True,
            "separate_fields": True,
        }
    )
    witness_maps = []
    for resolution in resolutions:
        witnesses = resolution.production_witnesses + resolution.measurement_witnesses
        witness_maps.append(
            {
                (
                    item.scope,
                    item.path_id,
                    item.segment_digest,
                    item.interval,
                ): item.substep_count
                for item in witnesses
            }
        )
    if tuple(witness_maps[0]) != tuple(witness_maps[1]) or tuple(
        witness_maps[1]
    ) != tuple(witness_maps[2]):
        raise W7ANResolutionContainerError(
            "resolution witness inventories differ"
        )
    if any(
        not (
            witness_maps[0][role]
            < witness_maps[1][role]
            < witness_maps[2][role]
        )
        for role in witness_maps[0]
    ):
        raise W7ANResolutionContainerError(
            "resolution substep counts are not strictly ordered"
        )
    substep_digest = _digest(
        {
            "roles": tuple(witness_maps[0]),
            "r1": tuple(witness_maps[0].values()),
            "r2": tuple(witness_maps[1].values()),
            "r4": tuple(witness_maps[2].values()),
        }
    )
    if canonical_digests != (
        canonical_cap.cap_seven_path_consumption_digest,
        canonical_handoff.measurement_handoff_digest,
        canonical_raw.raw_contrast_composition_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
    ):
        raise W7ANResolutionContainerError(
            "resolution container mutated a canonical input"
        )
    payload = _container_payload(
        plan.seven_path_plan_digest,
        _P0_REFERENCE_DIGEST,
        resolutions,
        r1_digest,
        start_digest,
        substep_digest,
    )
    return W7ANR124ResolutionContainer(
        _CONTAINER_ID,
        plan.seven_path_plan_digest,
        _P0_REFERENCE_DIGEST,
        resolutions,
        r1_digest,
        start_digest,
        substep_digest,
        False,
        False,
        _digest(payload),
    )


def compose_w7an_r124_resolution_container(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
    canonical_cap: W7AECAPSevenPathResult,
    canonical_handoff: W7AGPassiveCAPMeasurementHandoff,
    canonical_raw: W7AKRawContrastComposition,
) -> W7ANR124ResolutionContainer:
    """Materialize three isolated CAP resolutions against one P0 reference."""

    _validate_w7an_canonical_inputs(
        plan,
        p0_references,
        canonical_cap,
        canonical_handoff,
        canonical_raw,
    )
    resolutions = tuple(
        _build_resolution(
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
        for resolution_id, refinement in _RESOLUTIONS
    )
    return _finalize_w7an_r124_resolution_results(
        plan,
        p0_references,
        canonical_cap,
        canonical_handoff,
        canonical_raw,
        resolutions,
    )
