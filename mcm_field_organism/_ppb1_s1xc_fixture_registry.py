"""Private pure S1-XC fixtures, registry and read-only baseline findings."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
    PPB1ReferenceError,
    _digest,
    _input_projection,
    _validate_frame,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from .receptor_contract import ReceptorContactFrame


S1XC_SCHEMA_VERSION = "ppb1.s1xc.private-fixture-registry.v1"
S1XC_PARENT_AUDIT_DIGEST = (
    "e6aa23306023106dc56b1cfa85970547c76d249d0c8d428149506c6d341ff903"
)
S1XC_INVALID_MATERIALIZATION = "S1XC_INVALID_MATERIALIZATION"
S1XC_INVALID_BASELINE_PROBE = "S1XC_INVALID_BASELINE_PROBE"

S1XC_MODALITY_IDS = ("auditory", "visual")
S1XC_SYSTEM_IDS = (
    "ppb1",
    "no-memory",
    "replay",
    "static-prototype",
    "moving-state",
    "last-vector-distance",
)
S1XC_BASELINE_SYSTEM_IDS = S1XC_SYSTEM_IDS[1:]
S1XC_PROBE_CLASSES = (
    "exact-positive",
    "near-positive",
    "boundary-positive",
    "near-negative",
    "distinct-negative",
)
S1XC_REGISTRY_DIGEST = (
    "77d9437ce497bf298029c0b017cbb91df7f92a06d678c500d09319158b52668d"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PROBE_VALUES = {
    "auditory": (0.0, 0.1, 0.2, 0.3, 0.6),
    "visual": (0.0, 0.05, 0.1, 0.2, 0.5),
}
_EXPECTED_MASK = (True, True, True, False, False)


class S1XCError(ValueError):
    """One fail-closed S1-XC fixture or read-only baseline violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _frame_digest(frame: ReceptorContactFrame) -> str:
    return _digest(_input_projection(frame))


@dataclass(frozen=True, slots=True)
class S1XCModalityFixture:
    config: PPB1BankConfig
    source_clock_id: str
    formation_frames: tuple[ReceptorContactFrame, ...]
    formation_history_digest: str
    candidate_prestate: PPB1BankState
    candidate_state_identity_digest: str
    probe_frames: tuple[ReceptorContactFrame, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.config, PPB1BankConfig)
            or self.config.modality_id not in S1XC_MODALITY_IDS
            or len(self.formation_frames) != 3
            or len(self.probe_frames) != 5
            or not _valid_digest(self.formation_history_digest)
            or not _valid_digest(self.candidate_state_identity_digest)
        ):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "invalid modality fixture anatomy"
            )
        if self.candidate_prestate.accepted_step_count != 3:
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "candidate prestate must bind three contacts"
            )
        if (
            self.candidate_prestate.config_digest != self.config.digest()
            or self.candidate_prestate.source_clock_id != self.source_clock_id
            or self.candidate_prestate.last_source_window_end_tick != 3
            or _digest(_state_identity_payload(self.candidate_prestate))
            != self.candidate_state_identity_digest
        ):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION,
                "candidate prestate identity does not match its fixture",
            )


@dataclass(frozen=True, slots=True)
class S1XCBaselinePrestate:
    system_id: str
    modality_id: str
    dimension: int
    formation_history_digest: str
    vectors: tuple[tuple[float, ...], ...]
    trace: tuple[float, ...] | None
    stored_scalar_value_count: int
    raw_history_access_used: bool

    def __post_init__(self) -> None:
        if (
            self.system_id not in S1XC_BASELINE_SYSTEM_IDS
            or self.system_id == "no-memory"
            or self.modality_id not in S1XC_MODALITY_IDS
            or isinstance(self.dimension, bool)
            or not isinstance(self.dimension, int)
            or self.dimension <= 0
            or not _valid_digest(self.formation_history_digest)
            or isinstance(self.stored_scalar_value_count, bool)
            or not isinstance(self.stored_scalar_value_count, int)
            or self.stored_scalar_value_count < 0
            or not isinstance(self.raw_history_access_used, bool)
        ):
            raise S1XCError(S1XC_INVALID_MATERIALIZATION, "invalid baseline identity")
        for vector in self.vectors:
            if len(vector) != self.dimension or any(
                not math.isfinite(value) or abs(value) > 1.0 for value in vector
            ):
                raise S1XCError(
                    S1XC_INVALID_MATERIALIZATION, "invalid baseline vector anatomy"
                )
        if self.trace is not None and (
            len(self.trace) != self.dimension
            or any(
                not math.isfinite(value) or abs(value) > 1.0
                for value in self.trace
            )
        ):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "invalid baseline trace"
            )
        expected = sum(len(vector) for vector in self.vectors)
        if self.trace is not None:
            expected += len(self.trace)
        if self.stored_scalar_value_count != expected:
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "baseline storage count mismatch"
            )
        valid_anatomy = {
            "replay": len(self.vectors) == 3
            and self.trace is None
            and self.raw_history_access_used,
            "static-prototype": len(self.vectors) == 1
            and self.trace is None
            and not self.raw_history_access_used,
            "moving-state": not self.vectors
            and self.trace is not None
            and not self.raw_history_access_used,
            "last-vector-distance": len(self.vectors) == 1
            and self.trace is None
            and not self.raw_history_access_used,
        }
        if not valid_anatomy[self.system_id]:
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION,
                "baseline state does not match its information role",
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1XC_SCHEMA_VERSION,
            "system_id": self.system_id,
            "modality_id": self.modality_id,
            "dimension": self.dimension,
            "formation_history_digest": self.formation_history_digest,
            "vectors": [list(vector) for vector in self.vectors],
            "trace": None if self.trace is None else list(self.trace),
            "stored_scalar_value_count": self.stored_scalar_value_count,
            "raw_history_access_used": self.raw_history_access_used,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class S1XCCellPlan:
    cell_id: str
    system_id: str
    modality_id: str
    probe_class: str
    config_digest: str | None
    formation_history_digest: str | None
    frozen_prestate_digest: str | None
    state_identity_digest: str | None
    probe_frame_digest: str
    expected_recognized: bool
    expected_distance: float | None
    observed_state_present: bool
    storage_role_count: int
    stored_scalar_value_count: int
    raw_history_access_used: bool
    cell_plan_digest: str

    def __post_init__(self) -> None:
        if (
            self.cell_id != f"s1xa.{self.modality_id}.{self.system_id}.{self.probe_class}"
            or self.system_id not in S1XC_SYSTEM_IDS
            or self.modality_id not in S1XC_MODALITY_IDS
            or self.probe_class not in S1XC_PROBE_CLASSES
            or not _valid_digest(self.probe_frame_digest)
            or not isinstance(self.expected_recognized, bool)
            or not isinstance(self.observed_state_present, bool)
            or isinstance(self.storage_role_count, bool)
            or not isinstance(self.storage_role_count, int)
            or self.storage_role_count < 0
            or isinstance(self.stored_scalar_value_count, bool)
            or not isinstance(self.stored_scalar_value_count, int)
            or self.stored_scalar_value_count < 0
            or not isinstance(self.raw_history_access_used, bool)
        ):
            raise S1XCError(S1XC_INVALID_MATERIALIZATION, "invalid cell plan")
        if self.expected_distance is not None and (
            not math.isfinite(self.expected_distance)
            or self.expected_distance < 0.0
            or self.expected_distance > 2.0
        ):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION,
                "expected distance must be finite and bounded",
            )
        for digest in (
            self.config_digest,
            self.formation_history_digest,
            self.frozen_prestate_digest,
            self.state_identity_digest,
        ):
            if digest is not None and not _valid_digest(digest):
                raise S1XCError(
                    S1XC_INVALID_MATERIALIZATION, "invalid optional cell digest"
                )
        if self.cell_plan_digest != _digest(self.payload_without_digest()):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "cell plan digest mismatch"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XC_SCHEMA_VERSION,
            "parent_audit_digest": S1XC_PARENT_AUDIT_DIGEST,
            "cell_id": self.cell_id,
            "system_id": self.system_id,
            "modality_id": self.modality_id,
            "probe_class": self.probe_class,
            "config_digest": self.config_digest,
            "formation_history_digest": self.formation_history_digest,
            "frozen_prestate_digest": self.frozen_prestate_digest,
            "state_identity_digest": self.state_identity_digest,
            "probe_frame_digest": self.probe_frame_digest,
            "expected_recognized": self.expected_recognized,
            "expected_distance": self.expected_distance,
            "observed_state_present": self.observed_state_present,
            "storage_role_count": self.storage_role_count,
            "stored_scalar_value_count": self.stored_scalar_value_count,
            "raw_history_access_used": self.raw_history_access_used,
        }


@dataclass(frozen=True, slots=True)
class S1XCMaterialization:
    modalities: tuple[S1XCModalityFixture, ...]
    baseline_prestates: tuple[S1XCBaselinePrestate, ...]
    cell_plans: tuple[S1XCCellPlan, ...]
    registry_digest: str
    materialization_digest: str

    def __post_init__(self) -> None:
        if (
            len(self.modalities) != 2
            or len(self.baseline_prestates) != 8
            or len(self.cell_plans) != 60
            or len({cell.cell_id for cell in self.cell_plans}) != 60
            or self.registry_digest != S1XC_REGISTRY_DIGEST
            or not _valid_digest(self.materialization_digest)
        ):
            raise S1XCError(
                S1XC_INVALID_MATERIALIZATION, "materialization is incomplete"
            )


@dataclass(frozen=True, slots=True)
class S1XCBaselineFinding:
    system_id: str
    modality_id: str
    probe_class: str
    observed_prestate_digest: str | None
    probe_frame_digest: str
    recognized: bool
    match_distance: float | None
    stored_scalar_value_count: int
    raw_history_access_used: bool
    finding_digest: str

    def __post_init__(self) -> None:
        if (
            self.system_id not in S1XC_BASELINE_SYSTEM_IDS
            or self.modality_id not in S1XC_MODALITY_IDS
            or self.probe_class not in S1XC_PROBE_CLASSES
            or not _valid_digest(self.probe_frame_digest)
            or not isinstance(self.recognized, bool)
            or isinstance(self.stored_scalar_value_count, bool)
            or not isinstance(self.stored_scalar_value_count, int)
            or self.stored_scalar_value_count < 0
            or not isinstance(self.raw_history_access_used, bool)
        ):
            raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "invalid finding")
        if self.system_id == "no-memory":
            if (
                self.observed_prestate_digest is not None
                or self.match_distance is not None
                or self.recognized
            ):
                raise S1XCError(
                    S1XC_INVALID_BASELINE_PROBE, "no-memory requires an empty finding"
                )
        elif not _valid_digest(self.observed_prestate_digest) or self.match_distance is None:
            raise S1XCError(
                S1XC_INVALID_BASELINE_PROBE, "stateful baseline requires distance"
            )
        if self.match_distance is not None and (
            not math.isfinite(self.match_distance)
            or self.match_distance < 0.0
            or self.match_distance > 2.0
        ):
            raise S1XCError(
                S1XC_INVALID_BASELINE_PROBE, "distance must be finite and bounded"
            )
        if self.finding_digest != _digest(self.payload_without_digest()):
            raise S1XCError(
                S1XC_INVALID_BASELINE_PROBE, "finding digest mismatch"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XC_SCHEMA_VERSION,
            "parent_audit_digest": S1XC_PARENT_AUDIT_DIGEST,
            "system_id": self.system_id,
            "modality_id": self.modality_id,
            "probe_class": self.probe_class,
            "observed_prestate_digest": self.observed_prestate_digest,
            "probe_frame_digest": self.probe_frame_digest,
            "recognized": self.recognized,
            "match_distance": self.match_distance,
            "stored_scalar_value_count": self.stored_scalar_value_count,
            "raw_history_access_used": self.raw_history_access_used,
        }


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.2, 0.1, 3, 512),
        PPB1ModalityParameters(4, 0.1, 0.1, 3, 128),
    )


def _modality_fixture(config: PPB1BankConfig) -> S1XCModalityFixture:
    modality = config.modality_id
    clock = f"clock.s1xa.{modality}"
    zero = (0.0,) * len(config.carrier_ids)
    formation = tuple(
        ReceptorContactFrame(
            modality,
            config.geometry_id,
            f"receptor.s1xa.{modality}.formation.{index}",
            clock,
            index - 1,
            index,
            config.carrier_ids,
            zero,
        )
        for index in range(1, 4)
    )
    history_digest = _digest([_input_projection(frame) for frame in formation])
    slots = (
        PPB1PrototypeSlot(f"{config.bank_id}.slot.000", True, zero, 3, 3),
        *(
            PPB1PrototypeSlot.free(f"{config.bank_id}.slot.{index:03d}")
            for index in range(1, config.capacity)
        ),
    )
    prestate = PPB1BankState(config.bank_id, config.digest(), 3, clock, 3, slots)
    probes = tuple(
        ReceptorContactFrame(
            modality,
            config.geometry_id,
            f"receptor.s1xa.{modality}.probe.{probe_class}",
            clock,
            4,
            5,
            config.carrier_ids,
            (value,) * len(config.carrier_ids),
        )
        for probe_class, value in zip(
            S1XC_PROBE_CLASSES, _PROBE_VALUES[modality], strict=True
        )
    )
    return S1XCModalityFixture(
        config,
        clock,
        formation,
        history_digest,
        prestate,
        _digest(_state_identity_payload(prestate)),
        probes,
    )


def _baseline_prestates(fixture: S1XCModalityFixture) -> tuple[S1XCBaselinePrestate, ...]:
    dimension = len(fixture.config.carrier_ids)
    zero = (0.0,) * dimension
    return (
        S1XCBaselinePrestate(
            "replay",
            fixture.config.modality_id,
            dimension,
            fixture.formation_history_digest,
            (zero, zero, zero),
            None,
            3 * dimension,
            True,
        ),
        S1XCBaselinePrestate(
            "static-prototype",
            fixture.config.modality_id,
            dimension,
            fixture.formation_history_digest,
            (zero,),
            None,
            dimension,
            False,
        ),
        S1XCBaselinePrestate(
            "moving-state",
            fixture.config.modality_id,
            dimension,
            fixture.formation_history_digest,
            (),
            zero,
            dimension,
            False,
        ),
        S1XCBaselinePrestate(
            "last-vector-distance",
            fixture.config.modality_id,
            dimension,
            fixture.formation_history_digest,
            (zero,),
            None,
            dimension,
            False,
        ),
    )


def _registry_digest() -> str:
    records = [
        {
            "cell_id": f"s1xa.{modality}.{system}.{probe}",
            "modality_id": modality,
            "system_id": system,
            "probe_class": probe,
        }
        for modality in S1XC_MODALITY_IDS
        for system in S1XC_SYSTEM_IDS
        for probe in S1XC_PROBE_CLASSES
    ]
    return _digest(records)


def materialize_s1xc_fixture_registry() -> S1XCMaterialization:
    """Build all bound plans without advancing or probing any system."""

    binding = bind_ppb1_receptor_profile("controlled", _parameters())
    modalities = tuple(
        _modality_fixture(config)
        for config in (binding.auditory_config, binding.visual_config)
    )
    prestates = tuple(
        state for fixture in modalities for state in _baseline_prestates(fixture)
    )
    prestate_by_role = {
        (state.modality_id, state.system_id): state for state in prestates
    }
    cells = []
    for fixture in modalities:
        dimension = len(fixture.config.carrier_ids)
        for system in S1XC_SYSTEM_IDS:
            baseline = prestate_by_role.get((fixture.config.modality_id, system))
            for index, (probe_class, frame) in enumerate(
                zip(S1XC_PROBE_CLASSES, fixture.probe_frames, strict=True)
            ):
                is_no_memory = system == "no-memory"
                is_candidate = system == "ppb1"
                prestate_digest = (
                    fixture.candidate_prestate.digest()
                    if is_candidate
                    else None if baseline is None else baseline.digest()
                )
                multiplier = 0 if is_no_memory else 3 if system == "replay" else 1
                values = {
                    "cell_id": f"s1xa.{fixture.config.modality_id}.{system}.{probe_class}",
                    "system_id": system,
                    "modality_id": fixture.config.modality_id,
                    "probe_class": probe_class,
                    "config_digest": None if is_no_memory else fixture.config.digest(),
                    "formation_history_digest": (
                        None if is_no_memory else fixture.formation_history_digest
                    ),
                    "frozen_prestate_digest": prestate_digest,
                    "state_identity_digest": (
                        fixture.candidate_state_identity_digest
                        if is_candidate
                        else None
                    ),
                    "probe_frame_digest": _frame_digest(frame),
                    "expected_recognized": False if is_no_memory else _EXPECTED_MASK[index],
                    "expected_distance": (
                        None
                        if is_no_memory
                        else _PROBE_VALUES[fixture.config.modality_id][index]
                    ),
                    "observed_state_present": not is_no_memory,
                    "storage_role_count": 0 if is_no_memory else 1,
                    "stored_scalar_value_count": multiplier * dimension,
                    "raw_history_access_used": system == "replay",
                }
                cells.append(S1XCCellPlan(**values, cell_plan_digest=_digest({
                    "schema_version": S1XC_SCHEMA_VERSION,
                    "parent_audit_digest": S1XC_PARENT_AUDIT_DIGEST,
                    **values,
                })))
    payload = {
        "schema_version": S1XC_SCHEMA_VERSION,
        "parent_audit_digest": S1XC_PARENT_AUDIT_DIGEST,
        "profile_binding_digest": binding.digest(),
        "modality_config_digests": [fixture.config.digest() for fixture in modalities],
        "formation_history_digests": [fixture.formation_history_digest for fixture in modalities],
        "candidate_prestate_digests": [
            fixture.candidate_prestate.digest() for fixture in modalities
        ],
        "baseline_prestate_digests": [state.digest() for state in prestates],
        "cell_plan_digests": [cell.cell_plan_digest for cell in cells],
        "registry_digest": _registry_digest(),
    }
    return S1XCMaterialization(
        modalities,
        prestates,
        tuple(cells),
        _registry_digest(),
        _digest(payload),
    )


def probe_s1xc_baseline_read_only(
    system_id: str,
    config: PPB1BankConfig,
    prestate: S1XCBaselinePrestate | None,
    frame: ReceptorContactFrame,
    probe_class: str,
) -> S1XCBaselineFinding:
    """Return one baseline finding without returning or changing state."""

    if system_id not in S1XC_BASELINE_SYSTEM_IDS or probe_class not in S1XC_PROBE_CLASSES:
        raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "unknown baseline or probe")
    try:
        validated = _validate_frame(config, frame)
    except PPB1ReferenceError as exc:
        raise S1XCError(S1XC_INVALID_BASELINE_PROBE, exc.detail) from exc
    if validated.window_start_tick != 4 or validated.window_end_tick != 5:
        raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "probe window must be 4..5")

    before = None if prestate is None else prestate.digest()
    distance = None
    recognized = False
    stored = 0
    raw_history = False
    if system_id == "no-memory":
        if prestate is not None:
            raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "no-memory must not receive state")
    else:
        if (
            not isinstance(prestate, S1XCBaselinePrestate)
            or prestate.system_id != system_id
            or prestate.modality_id != config.modality_id
            or prestate.dimension != len(config.carrier_ids)
        ):
            raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "baseline state mismatch")
        candidates = prestate.vectors
        if system_id == "moving-state":
            candidates = () if prestate.trace is None else (prestate.trace,)
        if not candidates:
            raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "baseline has no comparison state")
        distance = min(
            normalized_mean_l1_distance(validated.values, candidate)
            for candidate in candidates
        )
        recognized = distance <= config.match_threshold
        stored = prestate.stored_scalar_value_count
        raw_history = prestate.raw_history_access_used

    if prestate is not None and prestate.digest() != before:
        raise S1XCError(S1XC_INVALID_BASELINE_PROBE, "read-only probe changed state")
    values = {
        "system_id": system_id,
        "modality_id": config.modality_id,
        "probe_class": probe_class,
        "observed_prestate_digest": before,
        "probe_frame_digest": _frame_digest(validated),
        "recognized": recognized,
        "match_distance": distance,
        "stored_scalar_value_count": stored,
        "raw_history_access_used": raw_history,
    }
    payload = {
        "schema_version": S1XC_SCHEMA_VERSION,
        "parent_audit_digest": S1XC_PARENT_AUDIT_DIGEST,
        **values,
    }
    return S1XCBaselineFinding(**values, finding_digest=_digest(payload))
