"""Passive GF_001 probe for fixed local field-effect baselines."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from statistics import fmean
from typing import Callable, Iterable

from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronOutput,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class GF001LocalFieldEffectProbeError(ValueError):
    """Raised when the passive run leaves its preregistered boundary."""


GF001_BASELINE_IDS = (
    "b0.receptor_projection",
    "b1.hold_state",
    "b2.symmetric_local_activation_mean",
    "b3.symmetric_contact_and_local_activation_mean",
)

GF001_BRANCH_IDS = (
    "original_inputs",
    "local_sample_ablation",
    "current_contact_ablation",
    "explicit_zero_contact",
    "missing_receptor",
    "sample_order_permutation",
    "neuron_order_permutation",
    "horizontal_geometry_reflection",
    "dock_row_exchange",
    "zero_source",
    "same_dock_locality",
    "cross_dock_locality",
    "observer_removal",
    "independent_rebuild",
)

_AUDITORY_GEOMETRY = "gf001.auditory.v1"
_VISUAL_GEOMETRY = "gf001.visual.v1"
_CLOCK_ID = "organism.gf001"
_SAMPLE_OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))
_POSITIONS = tuple((row, column) for row in range(2) for column in range(3))
_SOURCE = (
    (0.8, -0.2, 0.4),
    (-0.6, 0.3, 0.1),
)
_CONTACT = (
    (0.2, 0.0, -0.4),
    (0.5, -0.1, 0.7),
)
_ZERO = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_baseline_id(baseline_id: str) -> str:
    if baseline_id not in GF001_BASELINE_IDS:
        raise GF001LocalFieldEffectProbeError(
            f"unknown GF_001 baseline: {baseline_id}"
        )
    return baseline_id


def _frame(
    modality_id: str,
    values: tuple[float, float, float],
    *,
    branch_id: str,
    step: int,
) -> ReceptorContactFrame:
    geometry_id = {
        "auditory": _AUDITORY_GEOMETRY,
        "visual": _VISUAL_GEOMETRY,
    }[modality_id]
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=geometry_id,
        snapshot_id=f"{branch_id}.{modality_id}.snapshot.{step}",
        clock_id=f"{modality_id}.source",
        window_start_tick=step * 10,
        window_end_tick=(step + 1) * 10,
        carrier_ids=tuple(
            f"{modality_id}.carrier.{index}" for index in range(3)
        ),
        values=values,
    )


def _new_field_and_distributor(
    branch_id: str,
) -> tuple[SharedMCMField, ReceptorDistributor]:
    references = (
        _frame("auditory", _ZERO[0], branch_id=f"{branch_id}.reference", step=0),
        _frame("visual", _ZERO[1], branch_id=f"{branch_id}.reference", step=0),
    )
    field = build_shared_mcm_field(
        references,
        {
            "auditory": ReceptorDockAnatomy(
                modality_id="auditory",
                dock_id="dock.auditory",
                positions=((0, 0), (0, 1), (0, 2)),
            ),
            "visual": ReceptorDockAnatomy(
                modality_id="visual",
                dock_id="dock.visual",
                positions=((1, 0), (1, 1), (1, 2)),
            ),
        },
        sample_offsets=_SAMPLE_OFFSETS,
        geometry_id="organism.gf001.v1",
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", _AUDITORY_GEOMETRY)
    )
    distributor.attach(
        ReceptorDock("dock.visual", "visual", _VISUAL_GEOMETRY)
    )
    return field, distributor


def _transition(
    baseline_id: str,
    *,
    include_local: bool = True,
    include_contact: bool = True,
    reverse_samples: bool = False,
    observer: Callable[[MCMNeuronDrive], None] | None = None,
) -> Callable[[MCMNeuronDrive], MCMNeuronOutput]:
    baseline_id = _validate_baseline_id(baseline_id)

    def transition(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        if observer is not None:
            observer(drive)
        samples = drive.perception.local_samples
        if reverse_samples:
            samples = tuple(reversed(samples))
        local_values = (
            tuple(sample.activation for sample in samples)
            if include_local
            else ()
        )
        contact = (
            drive.perception.receptor_contact if include_contact else None
        )

        if baseline_id == "b0.receptor_projection":
            activation = 0.0 if contact is None else contact
        elif baseline_id == "b1.hold_state":
            activation = drive.previous.activation
        elif baseline_id == "b2.symmetric_local_activation_mean":
            activation = fmean(local_values) if local_values else 0.0
        else:
            values = (
                ((contact,) if contact is not None else ()) + local_values
            )
            activation = fmean(values) if values else 0.0
        return MCMNeuronOutput(activation=activation, afterimage=0.0)

    return transition


def _distribution(
    distributor: ReceptorDistributor,
    values: tuple[tuple[float, ...], tuple[float, ...]],
    *,
    branch_id: str,
    step: int,
    missing_modality: str | None = None,
):
    frames = tuple(
        _frame(
            modality_id,
            tuple(row),  # type: ignore[arg-type]
            branch_id=branch_id,
            step=step,
        )
        for modality_id, row in zip(
            ("auditory", "visual"),
            values,
            strict=True,
        )
        if modality_id != missing_modality
    )
    return distributor.distribute(
        frames,
        CommonFieldTime(_CLOCK_ID, step * 10, (step + 1) * 10),
    )


def _position_values(field: SharedMCMField) -> tuple[tuple[tuple[int, int], float], ...]:
    return tuple(
        sorted(
            (
                (neuron.position[0], neuron.position[1]),
                neuron.activation,
            )
            for neuron in field.layer.neurons
        )
    )


def _afterimage_values(
    field: SharedMCMField,
) -> tuple[tuple[tuple[int, int], float], ...]:
    return tuple(
        sorted(
            (
                (neuron.position[0], neuron.position[1]),
                neuron.afterimage,
            )
            for neuron in field.layer.neurons
        )
    )


@dataclass(frozen=True, slots=True)
class GF001BranchObservation:
    baseline_id: str
    branch_id: str
    activation_by_position: tuple[tuple[tuple[int, int], float], ...]
    afterimage_by_position: tuple[tuple[tuple[int, int], float], ...]
    observed_drive_count: int

    def canonical_payload(self) -> dict[str, object]:
        return {
            "baseline_id": self.baseline_id,
            "branch_id": self.branch_id,
            "activation_by_position": [
                [list(position), value]
                for position, value in self.activation_by_position
            ],
            "afterimage_by_position": [
                [list(position), value]
                for position, value in self.afterimage_by_position
            ],
            "observed_drive_count": self.observed_drive_count,
        }


@dataclass(frozen=True, slots=True)
class GF001LocalFieldEffectProbeResult:
    observations: tuple[GF001BranchObservation, ...]
    baseline_ids_exact: bool
    branch_ids_exact_per_baseline: bool
    receptor_projection_exact: bool
    hold_state_exact: bool
    effect_baselines_have_local_causal_contrast: bool
    local_ablation_removes_effect: bool
    current_contact_ablation_isolated: bool
    zero_and_missing_contact_are_distinct: bool
    sample_order_is_neutral: bool
    neuron_order_is_neutral: bool
    horizontal_reflection_is_equivariant: bool
    dock_exchange_is_equivariant: bool
    zero_source_is_quiet: bool
    same_dock_effect_is_present: bool
    cross_dock_effect_is_present: bool
    observer_is_neutral: bool
    independent_rebuild_is_exact: bool
    all_afterimages_are_zero: bool
    fixed_baselines_explain_all_outputs: bool
    input_frames_retained: bool = False
    writes_back: bool = False
    runtime_candidate_released: bool = False

    def digest(self) -> str:
        payload = {
            item.name: (
                [observation.canonical_payload() for observation in value]
                if item.name == "observations"
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }
        return _digest(payload)


def _run_branch(
    baseline_id: str,
    branch_id: str,
) -> GF001BranchObservation:
    field, distributor = _new_field_and_distributor(
        f"{baseline_id}.{branch_id}"
    )
    source = _SOURCE
    contact = _CONTACT
    include_local = True
    include_contact = True
    reverse_samples = False
    missing_modality = None
    observer_enabled = True

    if branch_id == "local_sample_ablation":
        include_local = False
    elif branch_id == "current_contact_ablation":
        include_contact = False
    elif branch_id == "explicit_zero_contact":
        contact = _ZERO
    elif branch_id == "missing_receptor":
        missing_modality = "visual"
    elif branch_id == "sample_order_permutation":
        reverse_samples = True
    elif branch_id == "horizontal_geometry_reflection":
        source = tuple(tuple(reversed(row)) for row in source)  # type: ignore[assignment]
        contact = tuple(tuple(reversed(row)) for row in contact)  # type: ignore[assignment]
    elif branch_id == "dock_row_exchange":
        source = (source[1], source[0])
        contact = (contact[1], contact[0])
    elif branch_id == "zero_source":
        source = _ZERO
        contact = _ZERO
    elif branch_id == "same_dock_locality":
        source = ((1.0, 0.0, 0.0), _ZERO[1])
        contact = _ZERO
    elif branch_id == "cross_dock_locality":
        source = (_ZERO[0], (0.0, 1.0, 0.0))
        contact = _ZERO
    elif branch_id == "observer_removal":
        observer_enabled = False
    elif branch_id not in (
        "original_inputs",
        "neuron_order_permutation",
        "independent_rebuild",
    ):
        raise GF001LocalFieldEffectProbeError(
            f"unknown GF_001 branch: {branch_id}"
        )

    field = field.advance(
        _distribution(
            distributor,
            source,
            branch_id=branch_id,
            step=0,
        ),
        _transition("b0.receptor_projection"),
    )
    observed_drives: list[MCMNeuronDrive] = []
    transition = _transition(
        baseline_id,
        include_local=include_local,
        include_contact=include_contact,
        reverse_samples=reverse_samples,
        observer=observed_drives.append if observer_enabled else None,
    )
    field = field.advance(
        _distribution(
            distributor,
            contact,
            branch_id=branch_id,
            step=1,
            missing_modality=missing_modality,
        ),
        transition,
    )

    if branch_id == "neuron_order_permutation":
        proposal = _transition(
            baseline_id,
            include_local=include_local,
            include_contact=include_contact,
            reverse_samples=reverse_samples,
        )
        forward = {
            drive.previous.position: proposal(drive).activation
            for drive in observed_drives
        }
        reverse = {
            drive.previous.position: proposal(drive).activation
            for drive in reversed(observed_drives)
        }
        if forward != reverse:
            raise GF001LocalFieldEffectProbeError(
                "neuron proposal order changed the fixed baseline"
            )

    return GF001BranchObservation(
        baseline_id=baseline_id,
        branch_id=branch_id,
        activation_by_position=_position_values(field),
        afterimage_by_position=_afterimage_values(field),
        observed_drive_count=len(observed_drives),
    )


def _values(observation: GF001BranchObservation) -> dict[tuple[int, int], float]:
    return dict(observation.activation_by_position)


def _equal(
    first: GF001BranchObservation,
    second: GF001BranchObservation,
) -> bool:
    return (
        first.activation_by_position == second.activation_by_position
        and first.afterimage_by_position == second.afterimage_by_position
    )


def _expected_original(
    baseline_id: str,
) -> dict[tuple[int, int], float]:
    result: dict[tuple[int, int], float] = {}
    for row, column in _POSITIONS:
        local_values = tuple(
            _SOURCE[source_row][source_column]
            for delta_row, delta_column in _SAMPLE_OFFSETS
            for source_row, source_column in (
                (row + delta_row, column + delta_column),
            )
            if 0 <= source_row < 2 and 0 <= source_column < 3
        )
        if baseline_id == "b0.receptor_projection":
            value = _CONTACT[row][column]
        elif baseline_id == "b1.hold_state":
            value = _SOURCE[row][column]
        elif baseline_id == "b2.symmetric_local_activation_mean":
            value = fmean(local_values) if local_values else 0.0
        else:
            value = fmean((_CONTACT[row][column],) + local_values)
        result[(row, column)] = value
    return result


def run_gf001_local_field_effect_probe(
    *,
    baseline_order: Iterable[str] = GF001_BASELINE_IDS,
    branch_order: Iterable[str] = GF001_BRANCH_IDS,
) -> GF001LocalFieldEffectProbeResult:
    """Run every preregistered branch without selecting a field transition."""

    baseline_ids = tuple(baseline_order)
    branch_ids = tuple(branch_order)
    if (
        len(baseline_ids) != len(GF001_BASELINE_IDS)
        or set(baseline_ids) != set(GF001_BASELINE_IDS)
    ):
        raise GF001LocalFieldEffectProbeError(
            "baseline_order must contain every preregistered baseline once"
        )
    if (
        len(branch_ids) != len(GF001_BRANCH_IDS)
        or set(branch_ids) != set(GF001_BRANCH_IDS)
    ):
        raise GF001LocalFieldEffectProbeError(
            "branch_order must contain every preregistered branch once"
        )

    observations = tuple(
        _run_branch(baseline_id, branch_id)
        for baseline_id in baseline_ids
        for branch_id in branch_ids
    )
    by_key = {
        (item.baseline_id, item.branch_id): item for item in observations
    }

    def branch(baseline_id: str, branch_id: str) -> GF001BranchObservation:
        return by_key[(baseline_id, branch_id)]

    b0_original = _values(branch("b0.receptor_projection", "original_inputs"))
    b1_original = _values(branch("b1.hold_state", "original_inputs"))
    source_by_position = {
        position: _SOURCE[position[0]][position[1]] for position in _POSITIONS
    }
    contact_by_position = {
        position: _CONTACT[position[0]][position[1]] for position in _POSITIONS
    }

    effect_contrasts = []
    for baseline_id in GF001_BASELINE_IDS[2:]:
        original = _values(branch(baseline_id, "original_inputs"))
        ablated = _values(branch(baseline_id, "local_sample_ablation"))
        effect_contrasts.append(
            any(original[position] != ablated[position] for position in _POSITIONS)
        )

    b3_zero = _values(
        branch(
            "b3.symmetric_contact_and_local_activation_mean",
            "explicit_zero_contact",
        )
    )
    b3_missing = _values(
        branch(
            "b3.symmetric_contact_and_local_activation_mean",
            "missing_receptor",
        )
    )
    equation_match = all(
        _values(branch(baseline_id, "original_inputs"))
        == _expected_original(baseline_id)
        for baseline_id in GF001_BASELINE_IDS
    ) and all(
        _values(branch(baseline_id, "local_sample_ablation"))
        == (
            {position: 0.0 for position in _POSITIONS}
            if baseline_id == "b2.symmetric_local_activation_mean"
            else contact_by_position
        )
        for baseline_id in GF001_BASELINE_IDS[2:]
    )

    reflection_ok = True
    exchange_ok = True
    for baseline_id in GF001_BASELINE_IDS:
        original = _values(branch(baseline_id, "original_inputs"))
        reflected = _values(
            branch(baseline_id, "horizontal_geometry_reflection")
        )
        exchanged = _values(branch(baseline_id, "dock_row_exchange"))
        reflection_ok = reflection_ok and all(
            reflected[(row, column)] == original[(row, 2 - column)]
            for row, column in _POSITIONS
        )
        exchange_ok = exchange_ok and all(
            exchanged[(row, column)] == original[(1 - row, column)]
            for row, column in _POSITIONS
        )

    controls = {
        "baseline_ids_exact": tuple(sorted(baseline_ids))
        == tuple(sorted(GF001_BASELINE_IDS)),
        "branch_ids_exact_per_baseline": all(
            {
                item.branch_id
                for item in observations
                if item.baseline_id == baseline_id
            }
            == set(GF001_BRANCH_IDS)
            for baseline_id in GF001_BASELINE_IDS
        ),
        "receptor_projection_exact": b0_original == contact_by_position,
        "hold_state_exact": b1_original == source_by_position,
        "effect_baselines_have_local_causal_contrast": all(effect_contrasts),
        "local_ablation_removes_effect": all(
            not _equal(
                branch(baseline_id, "original_inputs"),
                branch(baseline_id, "local_sample_ablation"),
            )
            for baseline_id in GF001_BASELINE_IDS[2:]
        ),
        "current_contact_ablation_isolated": (
            _equal(
                branch(
                    "b2.symmetric_local_activation_mean",
                    "original_inputs",
                ),
                branch(
                    "b2.symmetric_local_activation_mean",
                    "current_contact_ablation",
                ),
            )
            and not _equal(
                branch(
                    "b3.symmetric_contact_and_local_activation_mean",
                    "original_inputs",
                ),
                branch(
                    "b3.symmetric_contact_and_local_activation_mean",
                    "current_contact_ablation",
                ),
            )
        ),
        "zero_and_missing_contact_are_distinct": any(
            b3_zero[(1, column)] != b3_missing[(1, column)]
            for column in range(3)
        ),
        "sample_order_is_neutral": all(
            _equal(
                branch(baseline_id, "original_inputs"),
                branch(baseline_id, "sample_order_permutation"),
            )
            for baseline_id in GF001_BASELINE_IDS
        ),
        "neuron_order_is_neutral": all(
            _equal(
                branch(baseline_id, "original_inputs"),
                branch(baseline_id, "neuron_order_permutation"),
            )
            for baseline_id in GF001_BASELINE_IDS
        ),
        "horizontal_reflection_is_equivariant": reflection_ok,
        "dock_exchange_is_equivariant": exchange_ok,
        "zero_source_is_quiet": all(
            all(value == 0.0 for value in _values(
                branch(baseline_id, "zero_source")
            ).values())
            for baseline_id in GF001_BASELINE_IDS
        ),
        "same_dock_effect_is_present": all(
            _values(branch(baseline_id, "same_dock_locality"))[(0, 1)]
            != 0.0
            for baseline_id in GF001_BASELINE_IDS[2:]
        ),
        "cross_dock_effect_is_present": all(
            _values(branch(baseline_id, "cross_dock_locality"))[(0, 1)]
            != 0.0
            for baseline_id in GF001_BASELINE_IDS[2:]
        ),
        "observer_is_neutral": all(
            _equal(
                branch(baseline_id, "original_inputs"),
                branch(baseline_id, "observer_removal"),
            )
            and branch(baseline_id, "observer_removal").observed_drive_count
            == 0
            for baseline_id in GF001_BASELINE_IDS
        ),
        "independent_rebuild_is_exact": all(
            _equal(
                branch(baseline_id, "original_inputs"),
                branch(baseline_id, "independent_rebuild"),
            )
            for baseline_id in GF001_BASELINE_IDS
        ),
        "all_afterimages_are_zero": all(
            all(value == 0.0 for _, value in item.afterimage_by_position)
            for item in observations
        ),
        "fixed_baselines_explain_all_outputs": equation_match,
    }
    failed = tuple(name for name, passed in controls.items() if not passed)
    if failed:
        raise GF001LocalFieldEffectProbeError(
            f"GF_001 controls did not close exactly: {', '.join(failed)}"
        )

    return GF001LocalFieldEffectProbeResult(
        observations=tuple(
            sorted(
                observations,
                key=lambda item: (item.baseline_id, item.branch_id),
            )
        ),
        **controls,
    )


def gf001_local_field_effect_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            GF001BranchObservation,
            GF001LocalFieldEffectProbeResult,
        )
        for item in fields(contract)
    )
