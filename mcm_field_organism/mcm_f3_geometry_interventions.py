"""Value-independent observer interventions for F3 geometry causality."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
import math

from .mcm_substrate_state import MCMSubstrateMass, MCMSubstrateState
from .shared_mcm_field import SharedMCMField


class MCMF3GeometryInterventionError(ValueError):
    """Raised when an intervention is not fixed by field geometry alone."""


@dataclass(frozen=True, slots=True)
class MCMF3GeometryContract:
    reflection_pairs: tuple[tuple[str, str], ...]
    reflection_digest: str
    left_mask_neuron_ids: tuple[str, ...]
    right_mask_neuron_ids: tuple[str, ...]
    left_mask_digest: str
    right_mask_digest: str

    def __post_init__(self) -> None:
        pairs = tuple(self.reflection_pairs)
        if not pairs or len({item[0] for item in pairs}) != len(pairs):
            raise MCMF3GeometryInterventionError("reflection must map every target once")
        if {item[0] for item in pairs} != {item[1] for item in pairs}:
            raise MCMF3GeometryInterventionError("reflection must be bijective")
        if set(self.left_mask_neuron_ids) & set(self.right_mask_neuron_ids):
            raise MCMF3GeometryInterventionError("local masks must be disjoint")
        if len(self.left_mask_neuron_ids) != len(self.right_mask_neuron_ids):
            raise MCMF3GeometryInterventionError("local masks require equal budgets")


def _digest(value: object) -> str:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def mcm_f3_geometry_contract(field: SharedMCMField) -> MCMF3GeometryContract:
    """Derive the fixed row reflection and visual half masks from geometry."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3GeometryInterventionError("geometry contract requires M")
    by_position = {item.position: item.neuron_id for item in field.layer.neurons}
    rows: dict[int, list[int]] = {}
    for row, column in by_position:
        rows.setdefault(row, []).append(column)
    pairs = []
    for row, columns_in in sorted(rows.items()):
        columns = sorted(columns_in)
        if columns != list(range(columns[0], columns[-1] + 1)):
            raise MCMF3GeometryInterventionError("every reflected row must be complete")
        for column in columns:
            target = by_position[(row, column)]
            source = by_position[(row, columns[0] + columns[-1] - column)]
            pairs.append((target, source))

    visual_rows = sorted(row for row in rows if row > min(rows))
    if not visual_rows:
        raise MCMF3GeometryInterventionError("visual rows are required")
    visual_columns = sorted({column for row in visual_rows for column in rows[row]})
    if len(visual_columns) % 2 != 0:
        raise MCMF3GeometryInterventionError("visual columns require equal halves")
    midpoint = len(visual_columns) // 2
    left_columns = set(visual_columns[:midpoint])
    right_columns = set(visual_columns[midpoint:])
    left = tuple(
        sorted(
            by_position[(row, column)]
            for row in visual_rows
            for column in rows[row]
            if column in left_columns
        )
    )
    right = tuple(
        sorted(
            by_position[(row, column)]
            for row in visual_rows
            for column in rows[row]
            if column in right_columns
        )
    )
    ordered_pairs = tuple(sorted(pairs))
    return MCMF3GeometryContract(
        reflection_pairs=ordered_pairs,
        reflection_digest=_digest(ordered_pairs),
        left_mask_neuron_ids=left,
        right_mask_neuron_ids=right,
        left_mask_digest=_digest(left),
        right_mask_digest=_digest(right),
    )


def permute_mcm_f3_mass_by_geometry(
    field: SharedMCMField,
    contract: MCMF3GeometryContract,
) -> SharedMCMField:
    """Reflect the complete M vector without changing its value multiset."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3GeometryInterventionError("M permutation requires a substrate")
    if contract != mcm_f3_geometry_contract(field):
        raise MCMF3GeometryInterventionError("geometry contract does not match field")
    mass = {item.neuron_id: item.mass for item in field.substrate.masses}
    permuted = tuple(
        MCMSubstrateMass(target, mass[source])
        for target, source in contract.reflection_pairs
    )
    return replace(
        field,
        substrate=MCMSubstrateState(
            field.substrate.arm,
            permuted,
            field.substrate.edge_inventory_digest,
        ),
    )


def neutralize_mcm_f3_local_mask_balanced(
    field: SharedMCMField,
    contract: MCMF3GeometryContract,
    *,
    target_mask: str,
) -> SharedMCMField:
    """Set one fixed half to uniform M and book its delta in the other half."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3GeometryInterventionError("local neutralization requires M")
    if contract != mcm_f3_geometry_contract(field):
        raise MCMF3GeometryInterventionError("geometry contract does not match field")
    if target_mask == "left":
        target = set(contract.left_mask_neuron_ids)
        control = set(contract.right_mask_neuron_ids)
    elif target_mask == "right":
        target = set(contract.right_mask_neuron_ids)
        control = set(contract.left_mask_neuron_ids)
    else:
        raise MCMF3GeometryInterventionError("target_mask must be left or right")

    mass = {item.neuron_id: item.mass for item in field.substrate.masses}
    neutral = field.substrate.arm.initial_total_mass / len(mass)
    booked_delta = math.fsum(mass[item] - neutral for item in target)
    control_delta = booked_delta / len(control)
    values = {}
    for neuron_id, value in mass.items():
        if neuron_id in target:
            values[neuron_id] = neutral
        elif neuron_id in control:
            values[neuron_id] = value + control_delta
        else:
            values[neuron_id] = value
    if any(not math.isfinite(value) or value < 0.0 for value in values.values()):
        raise MCMF3GeometryInterventionError(
            "balanced local neutralization left the nonnegative M domain"
        )
    substrate = MCMSubstrateState(
        field.substrate.arm,
        tuple(MCMSubstrateMass(key, value) for key, value in values.items()),
        field.substrate.edge_inventory_digest,
    )
    return replace(field, substrate=substrate)


def mcm_f3_geometry_interventions_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMF3GeometryContract))
