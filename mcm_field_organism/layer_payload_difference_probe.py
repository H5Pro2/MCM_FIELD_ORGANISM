"""Field-wise localization of distance-zero layer digest differences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contact_reproduction_probe import ContactArm, contact_arms, execute_contact_arm


@dataclass(frozen=True, slots=True)
class PayloadDifference:
    path: str
    baseline_value: object
    contact_value: object


@dataclass(frozen=True, slots=True)
class LayerDistanceComparison:
    research_id: str
    contact_arm_id: str
    gap: int
    activation_equal: bool
    afterimage_equal: bool
    layer_digest_equal: bool
    snapshot_digest_equal: bool
    layer_differences: tuple[PayloadDifference, ...]


@dataclass(frozen=True, slots=True)
class LayerPayloadDifferenceResult:
    comparisons: tuple[LayerDistanceComparison, ...]
    distance_zero_difference_paths: tuple[str, ...]
    distance_one_difference_paths: tuple[str, ...]
    differences_localized: bool


def _differences(left: Any, right: Any, path: str = "layer") -> tuple[PayloadDifference, ...]:
    if isinstance(left, dict) and isinstance(right, dict):
        keys = sorted(set(left) | set(right))
        return tuple(
            difference
            for key in keys
            for difference in _differences(left.get(key), right.get(key), f"{path}.{key}")
        )
    if isinstance(left, list) and isinstance(right, list):
        size = max(len(left), len(right))
        return tuple(
            difference
            for index in range(size)
            for difference in _differences(
                left[index] if index < len(left) else None,
                right[index] if index < len(right) else None,
                f"{path}[{index}]",
            )
        )
    if left != right:
        return (PayloadDifference(path, left, right),)
    return ()


def _minimal_pair(research_id: str) -> tuple[ContactArm, ContactArm]:
    gap_zero = tuple(arm for arm in contact_arms(research_id) if arm.gap == 0)
    selectors = {
        "033": lambda arm: arm.arm_id == "single",
        "035": lambda arm: arm.arm_id == "s0.2.g0.single",
        "036": lambda arm: arm.arm_id == "g0.aba.canonical",
        "037": lambda arm: arm.arm_id == "g0.aba.canonical",
        "038": lambda arm: arm.arm_id.startswith("g0.mixed."),
        "039": lambda arm: arm.arm_id == "g0.canonical.0",
    }
    contact = next(arm for arm in gap_zero if selectors[research_id](arm))
    baseline = next(
        arm
        for arm in gap_zero
        if "null" in arm.arm_id
        and len(arm.history) == len(contact.history)
        and arm.probe == contact.probe
    )
    return baseline, contact


def run_layer_payload_difference_probe() -> LayerPayloadDifferenceResult:
    comparisons = []
    for research_id in ("033", "035", "036", "037", "038", "039"):
        baseline, contact = _minimal_pair(research_id)
        for gap in (0, 1):
            baseline_arm = ContactArm(f"l163.{research_id}.null.g{gap}", baseline.history, gap, baseline.probe)
            contact_arm = ContactArm(f"l163.{research_id}.contact.g{gap}", contact.history, gap, contact.probe)
            baseline_snapshot = execute_contact_arm(research_id, baseline_arm)
            contact_snapshot = execute_contact_arm(research_id, contact_arm)
            baseline_layer = baseline_snapshot.canonical_payload()["layer"]
            contact_layer = contact_snapshot.canonical_payload()["layer"]
            comparisons.append(
                LayerDistanceComparison(
                    research_id=research_id,
                    contact_arm_id=contact.arm_id,
                    gap=gap,
                    activation_equal=baseline_snapshot.activation == contact_snapshot.activation,
                    afterimage_equal=baseline_snapshot.afterimage == contact_snapshot.afterimage,
                    layer_digest_equal=baseline_snapshot.layer.digest() == contact_snapshot.layer.digest(),
                    snapshot_digest_equal=baseline_snapshot.digest() == contact_snapshot.digest(),
                    layer_differences=_differences(baseline_layer, contact_layer),
                )
            )
    zero_paths = tuple(sorted({item.path for comparison in comparisons if comparison.gap == 0 for item in comparison.layer_differences}))
    one_paths = tuple(sorted({item.path for comparison in comparisons if comparison.gap == 1 for item in comparison.layer_differences}))
    return LayerPayloadDifferenceResult(
        comparisons=tuple(comparisons),
        distance_zero_difference_paths=zero_paths,
        distance_one_difference_paths=one_paths,
        differences_localized=bool(zero_paths) and not one_paths,
    )
