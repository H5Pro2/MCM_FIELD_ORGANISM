"""S1-EC92 synthetic r4/r8 coordinator and atomic scalar reduction."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import math

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
)
from .e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91ProbeReceipt,
    E1CommonProbeEC91SyntheticFixtureResult,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_r2_ec80_scalar_contract import S1_EC80_CONTRAST_ROLE_PAIRS
from .e1_common_probe_real_wrappers import E1CommonProbeFreshField
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC92SyntheticCoordinatorError(ValueError):
    """Raised when EC92 loses routes, isolation, accounting, or atomicity."""


S1_EC92_COORDINATOR_ID = "e1.common-probe-r4-r8-synthetic-coordinator.s1ec92.v1"
S1_EC92_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC92_EC91_FIXTURE_DIGEST = (
    "e194525320e5b2e73667f9cb98e5523b80171d8023fe739c3d96107cba3c0dc7"
)
S1_EC92_EXPECTED_SCALARS = (
    (
        "r4",
        (
            ("p0-reset-order", 0.12, 0.012),
            ("e1-active-order", 0.12, 0.012),
            ("e1-probe-feedback-ablated-order", 0.12, 0.012),
            ("e1-formation-ablated-order", 0.12, 0.012),
            ("ab-active-vs-probe-feedback-ablated", 0.24, 0.024),
            ("ba-active-vs-probe-feedback-ablated", 0.24, 0.024),
        ),
    ),
    (
        "r8",
        (
            ("p0-reset-order", 0.24, 0.024),
            ("e1-active-order", 0.24, 0.024),
            ("e1-probe-feedback-ablated-order", 0.24, 0.024),
            ("e1-formation-ablated-order", 0.24, 0.024),
            ("ab-active-vs-probe-feedback-ablated", 0.48, 0.048),
            ("ba-active-vs-probe-feedback-ablated", 0.48, 0.048),
        ),
    ),
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or len(left) != len(right):
        raise E1CommonProbeEC92SyntheticCoordinatorError(
            "S1-EC92 requires equal nonempty vectors"
        )
    value = max(abs(a - b) for a, b in zip(left, right, strict=True))
    if not math.isfinite(value):
        raise E1CommonProbeEC92SyntheticCoordinatorError(
            "S1-EC92 requires finite scalar contrasts"
        )
    return round(value, 15)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC92ScalarReceipt:
    refinement_id: str
    source_fixture_digest: str
    source_probe_receipt_digests: tuple[str, ...]
    roles: tuple[str, ...]
    contrast_scalars: tuple[tuple[str, float, float], ...]
    probe_count: int
    all_roles_exact_once: bool
    field_execution_performed: bool
    raw_vectors_persisted: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        expected = dict(S1_EC92_EXPECTED_SCALARS).get(self.refinement_id)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            expected is None
            or self.source_fixture_digest != S1_EC92_EC91_FIXTURE_DIGEST
            or len(self.source_probe_receipt_digests) != 8
            or not all(_valid_digest(item) for item in self.source_probe_receipt_digests)
            or self.roles != S1_EC45_PROBE_ROLES
            or self.contrast_scalars != expected
            or self.probe_count != 8
            or self.all_roles_exact_once is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.raw_vectors_persisted,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.receipt_digest != _digest(payload)
        ):
            raise E1CommonProbeEC92SyntheticCoordinatorError(
                "S1-EC92 scalar receipt changed or crossed synthetic scope"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC92SyntheticCoordinatorResult:
    coordinator_id: str
    source_ec89_result_digest: str
    source_ec91_fixture_digest: str
    refinement_ids: tuple[str, ...]
    fresh_field_counts: tuple[tuple[str, int], ...]
    scalar_receipt_digests: tuple[tuple[str, str], ...]
    accounted_budgets: tuple[tuple[str, int], ...]
    all_routes_exact: bool
    all_fresh_fields_identical_and_object_separate: bool
    all_six_contrasts_exact: bool
    atomic_scalar_return: bool
    actual_field_steps_executed: int
    persistence_performed: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    result_digest: str
    fresh_fields: tuple[tuple[E1CommonProbeFreshField, ...], ...] = field(
        repr=False, compare=False
    )
    scalar_receipts: tuple[E1CommonProbeEC92ScalarReceipt, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "fresh_fields", "scalar_receipts"}
        }
        if (
            self.coordinator_id != S1_EC92_COORDINATOR_ID
            or self.source_ec89_result_digest != S1_EC92_EC89_RESULT_DIGEST
            or self.source_ec91_fixture_digest != S1_EC92_EC91_FIXTURE_DIGEST
            or self.refinement_ids != ("r4", "r8")
            or self.fresh_field_counts != (("r4", 8), ("r8", 8))
            or self.scalar_receipt_digests
            != tuple(
                (item.refinement_id, item.receipt_digest)
                for item in self.scalar_receipts
            )
            or self.accounted_budgets != (("r4", 6416), ("r8", 12832))
            or len(self.fresh_fields) != 2
            or any(len(items) != 8 for items in self.fresh_fields)
            or any(
                value is not True
                for value in (
                    self.all_routes_exact,
                    self.all_fresh_fields_identical_and_object_separate,
                    self.all_six_contrasts_exact,
                    self.atomic_scalar_return,
                )
            )
            or self.actual_field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC92SyntheticCoordinatorError(
                "S1-EC92 coordinator changed or crossed synthetic scope"
            )


def _reduce_scalars(
    refinement_id: str,
    probes: tuple[E1CommonProbeEC91ProbeReceipt, ...],
    source_fixture_digest: str,
) -> E1CommonProbeEC92ScalarReceipt:
    if tuple(item.role_id for item in probes) != S1_EC45_PROBE_ROLES:
        raise E1CommonProbeEC92SyntheticCoordinatorError(
            "S1-EC92 requires all eight ordered probe roles"
        )
    by_role = {item.role_id: item for item in probes}
    scalars = tuple(
        (
            name,
            _linf(by_role[left].activation, by_role[right].activation),
            _linf(by_role[left].afterimage, by_role[right].afterimage),
        )
        for name, left, right in S1_EC80_CONTRAST_ROLE_PAIRS
    )
    values = {
        "refinement_id": refinement_id,
        "source_fixture_digest": source_fixture_digest,
        "source_probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "roles": tuple(item.role_id for item in probes),
        "contrast_scalars": scalars,
        "probe_count": len(probes),
        "all_roles_exact_once": len(by_role) == 8,
        "field_execution_performed": False,
        "raw_vectors_persisted": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC92ScalarReceipt(
        **values, receipt_digest=_digest(values)
    )


def run_e1_common_probe_ec92_synthetic_coordinator(
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
    fixture: E1CommonProbeEC91SyntheticFixtureResult,
) -> E1CommonProbeEC92SyntheticCoordinatorResult:
    """Coordinate existing synthetic receipts without advancing any field."""

    if (
        not isinstance(handoffs, E1CommonProbeEC89R4R8ObjectHandoffSet)
        or handoffs.result_digest != S1_EC92_EC89_RESULT_DIGEST
        or not isinstance(fixture, E1CommonProbeEC91SyntheticFixtureResult)
        or fixture.result_digest != S1_EC92_EC91_FIXTURE_DIGEST
        or fixture.source_ec89_result_digest != handoffs.result_digest
    ):
        raise E1CommonProbeEC92SyntheticCoordinatorError(
            "S1-EC92 requires the exact matching EC89 and EC91 objects"
        )
    handoffs.__post_init__()
    fixture.__post_init__()

    fresh_sets = []
    scalar_receipts = []
    for handoff, probes in zip(handoffs.handoffs, fixture.probes, strict=True):
        fresh = tuple(
            E1CommonProbeFreshField(
                slot.binding.binding_digest,
                handoff.initial_field_digest,
                copy.deepcopy(handoff.initial_field),
            )
            for slot in handoff.resolved_slots
        )
        if any(
            item.binding_digest != slot.binding.binding_digest
            or item.field is handoff.initial_field
            or _initial_field_digest(item.field) != handoff.initial_field_digest
            for item, slot in zip(fresh, handoff.resolved_slots, strict=True)
        ):
            raise E1CommonProbeEC92SyntheticCoordinatorError(
                "S1-EC92 fresh-field isolation changed"
            )
        fresh_sets.append(fresh)
        scalar_receipts.append(
            _reduce_scalars(handoff.refinement_id, probes, fixture.result_digest)
        )

    fresh_tuple = tuple(fresh_sets)
    scalar_tuple = tuple(scalar_receipts)
    all_ids = [id(item.field) for items in fresh_tuple for item in items]
    values = {
        "coordinator_id": S1_EC92_COORDINATOR_ID,
        "source_ec89_result_digest": handoffs.result_digest,
        "source_ec91_fixture_digest": fixture.result_digest,
        "refinement_ids": handoffs.refinement_ids,
        "fresh_field_counts": tuple(
            (handoff.refinement_id, len(items))
            for handoff, items in zip(handoffs.handoffs, fresh_tuple, strict=True)
        ),
        "scalar_receipt_digests": tuple(
            (item.refinement_id, item.receipt_digest) for item in scalar_tuple
        ),
        "accounted_budgets": tuple(
            (item[0], item[3]) for item in fixture.accounted_budgets
        ),
        "all_routes_exact": all(
            tuple(item.role_id for item in probes) == handoff.role_ids
            for handoff, probes in zip(handoffs.handoffs, fixture.probes, strict=True)
        ),
        "all_fresh_fields_identical_and_object_separate": (
            len(set(all_ids)) == 16
            and all(
                _initial_field_digest(item.field) == handoff.initial_field_digest
                for handoff, items in zip(handoffs.handoffs, fresh_tuple, strict=True)
                for item in items
            )
        ),
        "all_six_contrasts_exact": tuple(
            (item.refinement_id, item.contrast_scalars) for item in scalar_tuple
        )
        == S1_EC92_EXPECTED_SCALARS,
        "atomic_scalar_return": len(scalar_tuple) == 2,
        "actual_field_steps_executed": 0,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC92SyntheticCoordinatorResult(
        **values,
        result_digest=_digest(values),
        fresh_fields=fresh_tuple,
        scalar_receipts=scalar_tuple,
    )
