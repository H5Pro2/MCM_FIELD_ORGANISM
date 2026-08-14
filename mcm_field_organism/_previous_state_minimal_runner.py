"""Locked private wiring for the preregistered previous-state minimal test."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class PreviousStateMinimalRunnerError(ValueError):
    """Raised when the locked research wiring violates its fixed contract."""


@dataclass(frozen=True, slots=True)
class _ContactSpec:
    modality_id: str
    geometry_id: str
    snapshot_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    carrier_ids: tuple[str, ...]
    values: tuple[float, ...]

    def canonical_payload(self) -> dict[str, object]:
        return {
            "carrier_ids": list(self.carrier_ids),
            "clock_id": self.clock_id,
            "geometry_id": self.geometry_id,
            "modality_id": self.modality_id,
            "snapshot_id": self.snapshot_id,
            "values": list(self.values),
            "window_end_tick": self.window_end_tick,
            "window_start_tick": self.window_start_tick,
        }


@dataclass(frozen=True, slots=True)
class _ArmWiring:
    run_id: str
    arm_id: str
    replicate: int
    history_id: str
    current_contact_id: str
    previous_state_operator: str | None


@dataclass(frozen=True, slots=True)
class _LockedRunnerManifest:
    input_a: tuple[_ContactSpec, ...]
    input_b: tuple[_ContactSpec, ...]
    input_c: tuple[_ContactSpec, ...]
    config_json: str
    input_digests: tuple[tuple[str, str], ...]
    arms: tuple[_ArmWiring, ...]
    measurement_points: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    execution_locked: bool = True
    field_construction_allowed: bool = False
    receptor_distribution_allowed: bool = False
    integrator_execution_allowed: bool = False
    effect_measurement_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.execution_locked:
            raise PreviousStateMinimalRunnerError("runner execution must remain locked")
        if any(
            (
                self.field_construction_allowed,
                self.receptor_distribution_allowed,
                self.integrator_execution_allowed,
                self.effect_measurement_allowed,
            )
        ):
            raise PreviousStateMinimalRunnerError("locked runner cannot release execution")
        config = json.loads(self.config_json)
        if "dissipation_config" not in config or config["dissipation_config"] is not None:
            raise PreviousStateMinimalRunnerError("dissipation_config must be explicit None")
        if self.config_json != _CONFIG_JSON:
            raise PreviousStateMinimalRunnerError("canonical config bytes changed")
        if self.arms != _EXPECTED_ARMS:
            raise PreviousStateMinimalRunnerError("fixed arm wiring changed")
        if self.measurement_points != ("M0", "M1", "M2", "M3"):
            raise PreviousStateMinimalRunnerError("measurement points must remain M0..M3")
        if self.abort_conditions != _ABORT_CONDITIONS:
            raise PreviousStateMinimalRunnerError("fixed abort conditions changed")
        expected = dict(_EXPECTED_DIGESTS)
        if self.input_digests != _EXPECTED_DIGESTS:
            raise PreviousStateMinimalRunnerError("fixed input digests changed")
        computed = _computed_digests(self)
        if computed != expected:
            raise PreviousStateMinimalRunnerError("fixed input payload changed")


_CARRIERS = ("carrier.0", "carrier.1", "carrier.2")


def _contact(
    snapshot_id: str,
    start_tick: int,
    end_tick: int,
    values: tuple[float, float, float],
) -> _ContactSpec:
    return _ContactSpec(
        modality_id="synthetic",
        geometry_id="synthetic.line3.v1",
        snapshot_id=snapshot_id,
        clock_id="source.synthetic.v1",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=_CARRIERS,
        values=values,
    )


_INPUT_A = (
    _contact("history.a.e1", 0, 10, (0.75, 0.0, 0.0)),
    _contact("history.a.e2", 10, 20, (0.0, 0.5, 0.0)),
    _contact("history.a.e3", 20, 30, (0.0, 0.0, 0.25)),
)
_INPUT_B = (
    _contact("history.b.e1", 0, 10, (0.0, 0.0, 0.75)),
    _contact("history.b.e2", 10, 20, (0.0, 0.5, 0.0)),
    _contact("history.b.e3", 20, 30, (0.25, 0.0, 0.0)),
)
_INPUT_C = (_contact("contact.c.e1", 30, 40, (0.2, -0.1, 0.4)),)

_CONFIG_PAYLOAD = {
    "afterimage_config": {"time_constant_seconds": 0.5},
    "common_clock_id": "organism.minimal.v1",
    "dissipation_config": None,
    "dock": {
        "dock_id": "dock.synthetic",
        "modality_id": "synthetic",
        "receptor_geometry_id": "synthetic.line3.v1",
    },
    "dock_anatomy": {
        "dock_id": "dock.synthetic",
        "modality_id": "synthetic",
        "positions": [[0], [1], [2]],
    },
    "field": {
        "field_id": "organism.mcm_field",
        "geometry_id": "organism.shared.v1",
        "layer_id": "organism.mcm_layer",
        "sample_offsets": [[-1], [1]],
    },
    "numeric_zero": 1e-12,
    "rtol": 0.0,
    "substrate_config": {"response_time_seconds": 1.0},
    "ticks_per_second": 10.0,
}


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


_CONFIG_JSON = _canonical_json(_CONFIG_PAYLOAD)
_EXPECTED_DIGESTS = (
    ("A", "2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998"),
    ("B", "66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31"),
    ("C", "81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3"),
    ("config", "fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a"),
    ("bundle", "2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0"),
)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _computed_digests(manifest: _LockedRunnerManifest) -> dict[str, str]:
    a = [item.canonical_payload() for item in manifest.input_a]
    b = [item.canonical_payload() for item in manifest.input_b]
    c = [item.canonical_payload() for item in manifest.input_c]
    config = json.loads(manifest.config_json)
    return {
        "A": _sha256(a),
        "B": _sha256(b),
        "C": _sha256(c),
        "config": _sha256(config),
        "bundle": _sha256({"a": a, "b": b, "c": c, "config": config}),
    }


_ARM_DEFINITIONS = (
    ("history_a.none", "A", None),
    ("history_b.none", "B", None),
    ("history_a.identity", "A", "identity"),
    ("history_b.identity", "B", "identity"),
    ("history_a.zero", "A", "zero"),
    ("history_b.zero", "B", "zero"),
    ("equalized_a.none", "A", None),
    ("equalized_b.none", "A", None),
    ("permuted_a.none", "B", None),
    ("permuted_b.none", "A", None),
    ("permuted_a.zero", "B", "zero"),
    ("permuted_b.zero", "A", "zero"),
)

_ABORT_CONDITIONS = (
    "source_or_hook_not_frozen",
    "dissipation_active_or_patch_not_isolated",
    "none_identity_not_bit_equal",
    "replicate_digest_mismatch",
    "replicate_count_or_fresh_field_invalid",
    "history_budget_duration_geometry_or_modality_mismatch",
    "current_contact_c_not_byte_equal",
    "generator_boundary_time_or_distribution_mismatch",
    "field_dynamics_or_measurement_path_changed",
    "nonfinite_or_normalized_domain_violation",
    "equalized_baseline_not_equal",
    "results_viewed_before_all_arms_complete",
)

_EXPECTED_ARMS = tuple(
    _ArmWiring(
        run_id=f"{arm_id}.r{replicate}",
        arm_id=arm_id,
        replicate=replicate,
        history_id=history_id,
        current_contact_id="C",
        previous_state_operator=operator,
    )
    for arm_id, history_id, operator in _ARM_DEFINITIONS
    for replicate in (1, 2)
)


def build_locked_previous_state_minimal_manifest() -> _LockedRunnerManifest:
    """Build only immutable wiring; this function cannot construct a field."""

    return _LockedRunnerManifest(
        input_a=_INPUT_A,
        input_b=_INPUT_B,
        input_c=_INPUT_C,
        config_json=_CONFIG_JSON,
        input_digests=_EXPECTED_DIGESTS,
        arms=_EXPECTED_ARMS,
        measurement_points=("M0", "M1", "M2", "M3"),
        abort_conditions=_ABORT_CONDITIONS,
    )


def execute_previous_state_minimal_runner(
    manifest: _LockedRunnerManifest,
) -> None:
    """Constructively retain the execution lock until a separate release."""

    if not isinstance(manifest, _LockedRunnerManifest):
        raise PreviousStateMinimalRunnerError("locked runner manifest is required")
    raise PreviousStateMinimalRunnerError("previous-state minimal run is not released")
