"""Passive numerical comparison of already-produced controlled probe snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable

from .shared_mcm_field import SharedMCMFieldSnapshot


class ControlledProbeComparisonError(ValueError):
    """Raised when two probe snapshots cannot be compared fairly."""


@dataclass(frozen=True, slots=True)
class ControlledProbeSnapshotComparison:
    """Technical distances only; this result carries no semantic role."""

    reference_id: str
    candidate_id: str
    same_geometry: bool
    same_clock: bool
    snapshot_digest_equal: bool
    activation_linf: float
    afterimage_linf: float
    substrate_mass_linf: float | None


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ControlledProbeComparisonError("snapshot vectors have different lengths")
    return max((abs(a - b) for a, b in zip(left, right, strict=True)), default=0.0)


def compare_controlled_probe_snapshots(
    reference_id: str,
    reference: SharedMCMFieldSnapshot,
    candidate_id: str,
    candidate: SharedMCMFieldSnapshot,
) -> ControlledProbeSnapshotComparison:
    """Compare two compatible probe snapshots without advancing either field."""

    if not isinstance(reference_id, str) or not reference_id:
        raise ControlledProbeComparisonError("reference_id must be non-empty")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ControlledProbeComparisonError("candidate_id must be non-empty")
    if not isinstance(reference, SharedMCMFieldSnapshot):
        raise ControlledProbeComparisonError("reference must be one field snapshot")
    if not isinstance(candidate, SharedMCMFieldSnapshot):
        raise ControlledProbeComparisonError("candidate must be one field snapshot")

    reference_neurons = reference.layer.neurons
    candidate_neurons = candidate.layer.neurons
    if tuple(item.neuron_id for item in reference_neurons) != tuple(
        item.neuron_id for item in candidate_neurons
    ):
        raise ControlledProbeComparisonError("snapshots must share neuron identities")
    if reference.geometry_id != candidate.geometry_id:
        raise ControlledProbeComparisonError("snapshots must share field geometry")

    reference_activation = tuple(item.activation for item in reference_neurons)
    candidate_activation = tuple(item.activation for item in candidate_neurons)
    reference_afterimage = tuple(item.afterimage for item in reference_neurons)
    candidate_afterimage = tuple(item.afterimage for item in candidate_neurons)

    substrate_mass_linf: float | None = None
    if reference.substrate is not None and candidate.substrate is not None:
        reference_mass = tuple(item.mass for item in reference.substrate.masses)
        candidate_mass = tuple(item.mass for item in candidate.substrate.masses)
        substrate_mass_linf = _linf(reference_mass, candidate_mass)
    elif reference.substrate is not None or candidate.substrate is not None:
        substrate_mass_linf = math.inf

    return ControlledProbeSnapshotComparison(
        reference_id=reference_id,
        candidate_id=candidate_id,
        same_geometry=reference.geometry_id == candidate.geometry_id,
        same_clock=reference.clock_id == candidate.clock_id,
        snapshot_digest_equal=reference.digest() == candidate.digest(),
        activation_linf=_linf(reference_activation, candidate_activation),
        afterimage_linf=_linf(reference_afterimage, candidate_afterimage),
        substrate_mass_linf=substrate_mass_linf,
    )


def compare_controlled_probe_baseline_set(
    reference: SharedMCMFieldSnapshot,
    baselines: Iterable[tuple[str, SharedMCMFieldSnapshot]],
) -> tuple[ControlledProbeSnapshotComparison, ...]:
    """Compare one probe reference against a fixed, labelled baseline set."""

    comparisons = tuple(
        compare_controlled_probe_snapshots(
            "reference",
            reference,
            baseline_id,
            snapshot,
        )
        for baseline_id, snapshot in baselines
    )
    if not comparisons:
        raise ControlledProbeComparisonError("baseline set must not be empty")
    if len({item.candidate_id for item in comparisons}) != len(comparisons):
        raise ControlledProbeComparisonError("baseline ids must be unique")
    return comparisons


__all__ = (
    "ControlledProbeComparisonError",
    "ControlledProbeSnapshotComparison",
    "compare_controlled_probe_snapshots",
    "compare_controlled_probe_baseline_set",
)
