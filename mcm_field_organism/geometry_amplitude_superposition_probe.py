"""Passive superposition audit across contact geometry and amplitude."""

from __future__ import annotations

from dataclasses import dataclass

from .controlled_endogenous_source import controlled_multiscale_endogenous_source
from .endogenous_external_overlap_null_probe import (
    _difference,
    _run_branch,
    _vectors,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import ReceptorContactFrame
from .shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field


GEOMETRY_CASES = (
    ("near", (1, 0)),
    ("far", (2, 1)),
    ("opposite", (-1, 0)),
    ("transverse", (1, 1)),
)

AMPLITUDE_SCALE_PAIRS = (
    (0.25, 0.25),
    (1.0, 0.25),
    (0.25, 1.0),
    (1.0, 1.0),
    (1.5, 0.5),
    (0.5, 1.0),
    (1.5, 1.0),
    (-1.0, 1.0),
    (1.0, -1.0),
)


@dataclass(frozen=True, slots=True)
class GeometryAmplitudeSuperpositionCase:
    geometry_id: str
    external_position: tuple[int, int]
    external_scale: float
    endogenous_scale: float
    activation_error: float
    afterimage_error: float
    sources_nonzero: bool
    exact_linear_superposition: bool


@dataclass(frozen=True, slots=True)
class GeometryAmplitudeSuperpositionResult:
    cases: tuple[GeometryAmplitudeSuperpositionCase, ...]
    maximum_activation_error: float
    maximum_afterimage_error: float
    all_sources_nonzero: bool
    all_cases_additive: bool
    source_states_preserved: bool
    observer_writeback_performed: bool
    runtime_changed: bool


def _scaled_frames(
    frames: tuple[ReceptorContactFrame, ...],
    scale: float,
    suffix: str,
) -> tuple[ReceptorContactFrame, ...]:
    return tuple(
        ReceptorContactFrame(
            modality_id=frame.modality_id,
            geometry_id=frame.geometry_id,
            snapshot_id=f"{frame.snapshot_id}.{suffix}",
            clock_id=frame.clock_id,
            window_start_tick=frame.window_start_tick,
            window_end_tick=frame.window_end_tick,
            carrier_ids=frame.carrier_ids,
            values=tuple(scale * value for value in frame.values),
        )
        for frame in frames
    )


def _external_frames(count: int, scale: float) -> tuple[ReceptorContactFrame, ...]:
    values = (0.6, -0.3, 0.45, -0.15, 0.3, -0.45, 0.15, -0.6)
    if count != len(values):
        raise ValueError("controlled horizons must match")
    return tuple(
        ReceptorContactFrame(
            modality_id="external.controlled",
            geometry_id="external.controlled.v1",
            snapshot_id=f"external.controlled.geometry-amplitude.{index}",
            clock_id="external.controlled",
            window_start_tick=index,
            window_end_tick=index + 1,
            carrier_ids=("x0",),
            values=(scale * value,),
        )
        for index, value in enumerate(values)
    )


def _initial_field(endogenous, external, external_position):
    return build_shared_mcm_field(
        (endogenous, external),
        {
            endogenous.modality_id: ReceptorDockAnatomy(
                endogenous.modality_id,
                "dock.endogenous.controlled",
                ((0, 0), (0, 1)),
            ),
            external.modality_id: ReceptorDockAnatomy(
                external.modality_id,
                "dock.external.controlled",
                (external_position,),
            ),
        },
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )


def run_geometry_amplitude_superposition_probe(
    *, tolerance: float = 1e-12
) -> GeometryAmplitudeSuperpositionResult:
    """Run preregistered four-arm comparisons without changing field dynamics."""

    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    source = controlled_multiscale_endogenous_source()
    source_digest = source.digest()
    base_endogenous = source.frames()
    cases = []
    initial_digests_preserved = True

    for geometry_id, external_position in GEOMETRY_CASES:
        for external_scale, endogenous_scale in AMPLITUDE_SCALE_PAIRS:
            endogenous = _scaled_frames(
                base_endogenous,
                endogenous_scale,
                f"scale-{endogenous_scale}",
            )
            external = _external_frames(len(endogenous), external_scale)
            initial = _initial_field(endogenous[0], external[0], external_position)
            initial_digest = initial.layer.digest()
            branches = tuple(
                _run_branch(
                    initial,
                    endogenous,
                    external,
                    use_endogenous=use_endogenous,
                    use_external=use_external,
                    substrate_config=substrate,
                    afterimage_config=afterimage,
                )
                for use_endogenous, use_external in (
                    (True, True),
                    (False, True),
                    (True, False),
                    (False, False),
                )
            )
            joint, external_only, endogenous_only, contact_free = map(
                _vectors, branches
            )
            external_signature = _difference(external_only, contact_free)
            endogenous_signature = _difference(endogenous_only, contact_free)
            expected_activation = tuple(
                free + ext + end
                for free, ext, end in zip(
                    contact_free[0],
                    external_signature.activation,
                    endogenous_signature.activation,
                    strict=True,
                )
            )
            expected_afterimage = tuple(
                free + ext + end
                for free, ext, end in zip(
                    contact_free[1],
                    external_signature.afterimage,
                    endogenous_signature.afterimage,
                    strict=True,
                )
            )
            activation_error = max(
                abs(actual - expected)
                for actual, expected in zip(
                    joint[0], expected_activation, strict=True
                )
            )
            afterimage_error = max(
                abs(actual - expected)
                for actual, expected in zip(
                    joint[1], expected_afterimage, strict=True
                )
            )
            cases.append(
                GeometryAmplitudeSuperpositionCase(
                    geometry_id=geometry_id,
                    external_position=external_position,
                    external_scale=external_scale,
                    endogenous_scale=endogenous_scale,
                    activation_error=activation_error,
                    afterimage_error=afterimage_error,
                    sources_nonzero=(
                        external_signature.activation_l2 > tolerance
                        and endogenous_signature.activation_l2 > tolerance
                    ),
                    exact_linear_superposition=(
                        activation_error <= tolerance
                        and afterimage_error <= tolerance
                    ),
                )
            )
            initial_digests_preserved &= initial.layer.digest() == initial_digest

    return GeometryAmplitudeSuperpositionResult(
        cases=tuple(cases),
        maximum_activation_error=max(case.activation_error for case in cases),
        maximum_afterimage_error=max(case.afterimage_error for case in cases),
        all_sources_nonzero=all(case.sources_nonzero for case in cases),
        all_cases_additive=all(case.exact_linear_superposition for case in cases),
        source_states_preserved=(
            initial_digests_preserved and source.digest() == source_digest
        ),
        observer_writeback_performed=False,
        runtime_changed=False,
    )
