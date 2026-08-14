"""Parametric reproduction of synthetic contact studies 032 through 039."""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import re

from .mcm_neuron_layer import receptor_projection_baseline
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMFieldSnapshot,
    build_shared_mcm_field,
)


_GAPS = (0, 1, 2, 4, 8)
_OFFSETS = ((0, -1), (0, 1))
_CLOCK_ID = "organism.contact.reproduction"


@dataclass(frozen=True, slots=True)
class ContactArm:
    arm_id: str
    history: tuple[tuple[float, ...], ...]
    gap: int
    probe: tuple[float, ...]
    reverse_declaration: bool = False


@dataclass(frozen=True, slots=True)
class ArmMeasurement:
    arm_id: str
    gap: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    layer_digest: str
    snapshot_digest: str


@dataclass(frozen=True, slots=True)
class ResearchReproductionResult:
    research_id: str
    combination_count: int
    baseline_count: int
    max_activation_error: float
    max_afterimage_error: float
    unequal_layer_digest_count: int
    unequal_snapshot_digest_count: int
    expected_probe: tuple[float, ...]
    all_probe_activations_expected: bool
    all_afterimages_zero: bool
    deterministic_reproduction: bool


def _zero(size: int) -> tuple[float, ...]:
    return (0.0,) * size


def _padded(events: tuple[tuple[float, ...], ...], windows: int) -> tuple[tuple[float, ...], ...]:
    size = len(events[0])
    output = [_zero(size) for _ in range(windows)]
    for index, event in enumerate(events):
        output[index * 2] = event
    return tuple(output)


def _arms_032() -> tuple[ContactArm, ...]:
    z = (0.0, 0.0)
    c = (0.8, 0.3)
    p = (0.6, 0.4)
    return (
        ContactArm("null", (z, z), 1, p),
        ContactArm("single", (z, c), 1, p),
        ContactArm("repeat", (c, c), 1, p),
        ContactArm("reproduction", (c, c), 1, p),
        ContactArm("permutation", (c, c), 1, p, True),
    )


def _arms_033() -> tuple[ContactArm, ...]:
    return tuple(
        ContactArm(arm.arm_id, arm.history, gap, arm.probe, arm.reverse_declaration)
        for gap in _GAPS
        for arm in _arms_032()
    )


def _arms_034() -> tuple[ContactArm, ...]:
    z = _zero(4)
    p = (0.6, 0.4, 0.2, 0.1)
    histories = {
        "null": (z, z),
        "single": (z, (0.8, 0.0, 0.0, 0.0)),
        "same": ((0.8, 0.0, 0.0, 0.0),) * 2,
        "changing": ((0.8, 0.0, 0.0, 0.0), (0.0, 0.8, 0.0, 0.0)),
        "overlap": ((0.4, 0.4, 0.0, 0.0), (0.0, 0.4, 0.4, 0.0)),
        "disjoint": ((0.4, 0.4, 0.0, 0.0), (0.0, 0.0, 0.4, 0.4)),
    }
    direct = [ContactArm(name, history, 1, p) for name, history in histories.items()]
    reverse = [
        ContactArm(f"{name}.permutation", history, 1, p, True)
        for name, history in histories.items()
        if name != "null"
    ]
    return tuple(direct + reverse)


def _arms_035() -> tuple[ContactArm, ...]:
    p = (0.6, 0.4)
    arms = []
    for strength in (0.2, 0.5, 0.9):
        z, c = _zero(2), (strength, strength)
        for gap in _GAPS:
            prefix = f"s{strength}.g{gap}"
            arms.extend((
                ContactArm(f"{prefix}.null", (z, z), gap, p),
                ContactArm(f"{prefix}.single", (z, c), gap, p),
                ContactArm(f"{prefix}.repeat", (c, c), gap, p),
                ContactArm(f"{prefix}.reproduction", (c, c), gap, p),
                ContactArm(f"{prefix}.permutation", (c, c), gap, p, True),
            ))
    return tuple(arms)


def _sequence_histories(windows: int) -> tuple[tuple[str, tuple[tuple[float, ...], ...]], ...]:
    z = _zero(3)
    a, b, c = (0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.5)
    place = (lambda events: tuple(events) + (z,) * (windows - len(events))) if windows == 3 else (lambda events: _padded(events, windows))
    items = [("null", (z,) * windows), ("a", place((a,))), ("aa", place((a, a))), ("aba.canonical", place((a, b, a)))]
    for index, events in enumerate(sorted(set(itertools.permutations((a, b, a))))):
        items.append((f"aba.{index}", place(events)))
    for index, events in enumerate(itertools.permutations((a, b, c))):
        items.append((f"abc.{index}", place(events)))
    items.append(("aba.reproduction", place((a, b, a))))
    return tuple(items)


def _arms_sequence(research_id: str) -> tuple[ContactArm, ...]:
    windows = 3 if research_id == "036" else 5
    probe = (0.6, 0.0, 0.0)
    return tuple(
        ContactArm(f"g{gap}.{name}", history, gap, probe)
        for gap in _GAPS
        for name, history in _sequence_histories(windows)
    )


def _arms_038() -> tuple[ContactArm, ...]:
    z, p = _zero(3), (0.6, 0.0, 0.0)
    histories = [("null", (z,) * 5)]
    for strength in (0.2, 0.5, 0.9):
        event = (strength, 0.0, 0.0)
        histories.append((f"single.{strength}", _padded((event,), 5)))
        histories.append((f"repeat.{strength}", _padded((event, event), 5)))
    for docks in itertools.permutations(range(3)):
        for strengths in itertools.permutations((0.2, 0.5, 0.9)):
            events = tuple(
                tuple(strengths[index] if cell == dock else 0.0 for cell in range(3))
                for index, dock in enumerate(docks)
            )
            histories.append((f"mixed.{docks}.{strengths}", _padded(events, 5)))
    canonical = ((0.2, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.9))
    histories.append(("canonical.reproduction", _padded(canonical, 5)))
    return tuple(ContactArm(f"g{gap}.{name}", history, gap, p) for gap in _GAPS for name, history in histories)


def _arms_039() -> tuple[ContactArm, ...]:
    z, p = _zero(3), (0.6, 0.0, 0.0)
    histories = [("null", (z,) * 7)]
    events = {(dock, sign): tuple(sign * 0.9 if i == dock else 0.0 for i in range(3)) for dock in range(3) for sign in (-1, 1)}
    for key, event in events.items():
        histories.append((f"single.{key}", _padded((event,), 7)))
        histories.append((f"repeat.{key}", _padded((event, event), 7)))
    index = 0
    for left, right in itertools.permutations(range(3), 2):
        for signs in ((1, -1), (-1, 1)):
            histories.append((f"opposite.{index}", _padded((events[left, signs[0]], events[right, signs[1]]), 7)))
            index += 1
    canonical = (events[0, 1], events[1, -1], events[1, 1], events[2, -1])
    inverse = (events[0, -1], events[1, 1], events[1, -1], events[2, 1])
    for label, sequence in (("canonical", canonical), ("inverse", inverse)):
        for index, permutation in enumerate(itertools.permutations(sequence)):
            histories.append((f"{label}.{index}", _padded(permutation, 7)))
    histories.append(("canonical.reproduction", _padded(canonical, 7)))
    return tuple(ContactArm(f"g{gap}.{name}", history, gap, p) for gap in _GAPS for name, history in histories)


def contact_arms(research_id: str) -> tuple[ContactArm, ...]:
    builders = {"032": _arms_032, "033": _arms_033, "034": _arms_034, "035": _arms_035, "036": lambda: _arms_sequence("036"), "037": lambda: _arms_sequence("037"), "038": _arms_038, "039": _arms_039}
    try:
        return builders[research_id]()
    except KeyError as exc:
        raise ValueError(f"unsupported research id: {research_id}") from exc


def execute_contact_arm(
    research_id: str,
    arm: ContactArm,
) -> SharedMCMFieldSnapshot:
    """Execute one fresh synthetic arm and return its open runtime snapshot."""
    size = len(arm.probe)
    order = tuple(reversed(range(size))) if arm.reverse_declaration else tuple(range(size))
    references = tuple(
        ReceptorContactFrame(f"modality.{i}", f"geometry.{i}", f"reference.{i}", f"source.{i}", 0, 10, (f"carrier.{i}",), (0.0,))
        for i in order
    )
    anatomies = {f"modality.{i}": ReceptorDockAnatomy(f"modality.{i}", f"dock.{i}", ((0, i),)) for i in order}
    field = build_shared_mcm_field(references, anatomies, sample_offsets=_OFFSETS)
    distributor = ReceptorDistributor()
    for i in order:
        distributor.attach(ReceptorDock(f"dock.{i}", f"modality.{i}", f"geometry.{i}"))

    safe_arm_id = re.sub(r"[^a-z0-9_.-]", ".", arm.arm_id.lower())
    steps = arm.history + (_zero(size),) * arm.gap + (arm.probe,)
    for step, values in enumerate(steps):
        frames = tuple(
            ReceptorContactFrame(f"modality.{i}", f"geometry.{i}", f"r{research_id}.{safe_arm_id}.s{step}.m{i}", f"source.{i}", step * 10, (step + 1) * 10, (f"carrier.{i}",), (values[i],))
            for i in order
        )
        distribution = distributor.distribute(frames, CommonFieldTime(_CLOCK_ID, step * 10, (step + 1) * 10))
        field = field.advance(distribution, receptor_projection_baseline)
    return field.snapshot()


def _measure(research_id: str, arm: ContactArm) -> ArmMeasurement:
    snapshot = execute_contact_arm(research_id, arm)
    return ArmMeasurement(
        arm.arm_id,
        arm.gap,
        snapshot.activation,
        snapshot.afterimage,
        snapshot.layer.digest(),
        snapshot.digest(),
    )


def run_contact_reproduction(research_id: str) -> ResearchReproductionResult:
    arms = contact_arms(research_id)
    measurements = tuple(_measure(research_id, arm) for arm in arms)
    baselines = {}
    for arm, measurement in zip(arms, measurements):
        key = (arm.gap, arm.probe, len(arm.history))
        if ".null" in arm.arm_id or arm.arm_id == "null":
            baselines[key] = measurement
    errors_a, errors_i, unequal_layer, unequal_snapshot = [], [], 0, 0
    for arm, measurement in zip(arms, measurements):
        baseline = baselines[(arm.gap, arm.probe, len(arm.history))]
        errors_a.extend(abs(a - b) for a, b in zip(measurement.activation, baseline.activation))
        errors_i.extend(abs(a - b) for a, b in zip(measurement.afterimage, baseline.afterimage))
        unequal_layer += measurement.layer_digest != baseline.layer_digest
        unequal_snapshot += measurement.snapshot_digest != baseline.snapshot_digest
    repeated = tuple(_measure(research_id, arm) for arm in arms)
    return ResearchReproductionResult(
        research_id=research_id,
        combination_count=len(arms),
        baseline_count=len(baselines),
        max_activation_error=max(errors_a, default=0.0),
        max_afterimage_error=max(errors_i, default=0.0),
        unequal_layer_digest_count=unequal_layer,
        unequal_snapshot_digest_count=unequal_snapshot,
        expected_probe=arms[0].probe,
        all_probe_activations_expected=all(
            measurement.activation == arm.probe
            for arm, measurement in zip(arms, measurements)
        ),
        all_afterimages_zero=all(measurement.afterimage == _zero(len(measurement.afterimage)) for measurement in measurements),
        deterministic_reproduction=measurements == repeated,
    )


def run_all_contact_reproductions() -> tuple[ResearchReproductionResult, ...]:
    return tuple(run_contact_reproduction(research_id) for research_id in ("032", "033", "034", "035", "036", "037", "038", "039"))
