"""S1-EC36 quantitative P0 schema and snapshot-only collector."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMFieldSnapshot


class E1RepetitionPilotQuantitativeP0SchemaError(ValueError):
    """Raised when S1-EC36 loses quantitative P0 observability."""


S1_EC36_SCHEMA_ID = "e1.repetition-pilot-quantitative-p0.s1ec36.v1"
S1_EC36_REFINEMENTS = ("r2", "r4", "r8")


def _finite_vector(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise E1RepetitionPilotQuantitativeP0SchemaError(
            f"S1-EC36 {role} must be one finite nonempty vector"
        )
    return result


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


@dataclass(frozen=True, slots=True)
class E1PilotQuantitativeP0Pair:
    schema_id: str
    contact_count: int
    refinement_id: str
    neuron_ids: tuple[str, ...]
    repeated_snapshot_digest: str
    continuous_snapshot_digest: str
    activation_contrast: tuple[float, ...]
    afterimage_contrast: tuple[float, ...]
    activation_linf: float
    afterimage_linf: float
    pair_digest: str

    def __post_init__(self) -> None:
        activation = _finite_vector(self.activation_contrast, "activation contrast")
        afterimage = _finite_vector(self.afterimage_contrast, "afterimage contrast")
        if (
            self.schema_id != S1_EC36_SCHEMA_ID
            or self.contact_count not in (1, 2)
            or self.refinement_id not in S1_EC36_REFINEMENTS
            or not self.neuron_ids
            or len(set(self.neuron_ids)) != len(self.neuron_ids)
            or len(activation) != len(self.neuron_ids)
            or len(afterimage) != len(self.neuron_ids)
            or len(self.repeated_snapshot_digest) != 64
            or len(self.continuous_snapshot_digest) != 64
            or self.activation_linf != _linf(activation)
            or self.afterimage_linf != _linf(afterimage)
        ):
            raise E1RepetitionPilotQuantitativeP0SchemaError(
                "S1-EC36 P0 pair changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "pair_digest"
        }
        if self.pair_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeP0SchemaError(
                "S1-EC36 P0 pair digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1PilotQuantitativeP0RefinementProfile:
    schema_id: str
    contact_count: int
    pair_digests: tuple[str, ...]
    activation_r2_r4_linf: float
    activation_r4_r8_linf: float
    afterimage_r2_r4_linf: float
    afterimage_r4_r8_linf: float
    fine_residual: float
    field_execution_performed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    profile_digest: str

    def __post_init__(self) -> None:
        residuals = (
            self.activation_r2_r4_linf,
            self.activation_r4_r8_linf,
            self.afterimage_r2_r4_linf,
            self.afterimage_r4_r8_linf,
        )
        if (
            self.schema_id != S1_EC36_SCHEMA_ID
            or self.contact_count not in (1, 2)
            or len(self.pair_digests) != 3
            or any(len(value) != 64 for value in self.pair_digests)
            or any(not math.isfinite(value) or value < 0.0 for value in residuals)
            or self.fine_residual != max(
                self.activation_r4_r8_linf,
                self.afterimage_r4_r8_linf,
            )
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeP0SchemaError(
                "S1-EC36 P0 refinement profile changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "profile_digest"
        }
        if self.profile_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeP0SchemaError(
                "S1-EC36 profile digest changed"
            )


def collect_quantitative_p0_pair(
    contact_count: int,
    refinement_id: str,
    repeated: SharedMCMFieldSnapshot,
    continuous: SharedMCMFieldSnapshot,
) -> E1PilotQuantitativeP0Pair:
    """Collect terminal P0 components from two already completed snapshots."""

    if not isinstance(repeated, SharedMCMFieldSnapshot) or not isinstance(
        continuous, SharedMCMFieldSnapshot
    ):
        raise E1RepetitionPilotQuantitativeP0SchemaError(
            "S1-EC36 requires two completed P0 snapshots"
        )
    repeated.__post_init__()
    continuous.__post_init__()
    if repeated.neuron_ids != continuous.neuron_ids:
        raise E1RepetitionPilotQuantitativeP0SchemaError(
            "S1-EC36 requires identical ordered P0 neuron inventories"
        )
    activation = tuple(
        left - right
        for left, right in zip(
            repeated.activation,
            continuous.activation,
            strict=True,
        )
    )
    afterimage = tuple(
        left - right
        for left, right in zip(
            repeated.afterimage,
            continuous.afterimage,
            strict=True,
        )
    )
    payload = {
        "schema_id": S1_EC36_SCHEMA_ID,
        "contact_count": contact_count,
        "refinement_id": refinement_id,
        "neuron_ids": repeated.neuron_ids,
        "repeated_snapshot_digest": repeated.digest(),
        "continuous_snapshot_digest": continuous.digest(),
        "activation_contrast": activation,
        "afterimage_contrast": afterimage,
        "activation_linf": _linf(activation),
        "afterimage_linf": _linf(afterimage),
    }
    return E1PilotQuantitativeP0Pair(
        **payload,
        pair_digest=_digest(payload),
    )


def build_quantitative_p0_refinement_profile(
    pairs: tuple[E1PilotQuantitativeP0Pair, ...],
) -> E1PilotQuantitativeP0RefinementProfile:
    """Build r2/r4/r8 component residuals without executing a field."""

    pairs = tuple(pairs)
    if (
        len(pairs) != 3
        or any(not isinstance(item, E1PilotQuantitativeP0Pair) for item in pairs)
        or tuple(item.refinement_id for item in pairs) != S1_EC36_REFINEMENTS
        or len({item.contact_count for item in pairs}) != 1
        or len({item.neuron_ids for item in pairs}) != 1
    ):
        raise E1RepetitionPilotQuantitativeP0SchemaError(
            "S1-EC36 requires one aligned r2/r4/r8 P0 trio"
        )
    for item in pairs:
        item.__post_init__()

    def distance(role: str, left: int, right: int) -> float:
        first = getattr(pairs[left], role)
        second = getattr(pairs[right], role)
        return _linf(tuple(
            value - reference
            for value, reference in zip(first, second, strict=True)
        ))

    values = {
        "schema_id": S1_EC36_SCHEMA_ID,
        "contact_count": pairs[0].contact_count,
        "pair_digests": tuple(item.pair_digest for item in pairs),
        "activation_r2_r4_linf": distance("activation_contrast", 0, 1),
        "activation_r4_r8_linf": distance("activation_contrast", 1, 2),
        "afterimage_r2_r4_linf": distance("afterimage_contrast", 0, 1),
        "afterimage_r4_r8_linf": distance("afterimage_contrast", 1, 2),
        "field_execution_performed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    values["fine_residual"] = max(
        values["activation_r4_r8_linf"],
        values["afterimage_r4_r8_linf"],
    )
    return E1PilotQuantitativeP0RefinementProfile(
        **values,
        profile_digest=_digest(values),
    )


def quantitative_p0_schema_roles() -> tuple[str, ...]:
    """Expose the retained roles for static runner integration checks."""

    return tuple(item.name for item in fields(E1PilotQuantitativeP0Pair))
