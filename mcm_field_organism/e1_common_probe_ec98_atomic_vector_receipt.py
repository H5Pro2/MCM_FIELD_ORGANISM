"""S1-EC98 corrected atomic vector receipt and synthetic fixture."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC98AtomicVectorReceiptError(ValueError):
    """Raised when EC98 loses vectors, geometry, controls, or closed scope."""


S1_EC98_CONTRACT_ID = "e1.common-probe-atomic-vector-receipt.s1ec98.v1"
S1_EC98_FIXTURE_ID = "e1.common-probe-atomic-vector-receipt-fixture.s1ec98.v1"
S1_EC98_REFINEMENTS = ("r2", "r4", "r8")
S1_EC98_CONTROL_PREFIXES = (
    "p0-reset",
    "e1-probe-feedback-ablated",
    "e1-formation-ablated",
)


def _finite_vector(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise E1CommonProbeEC98AtomicVectorReceiptError(
            f"S1-EC98 {role} must be one finite nonempty vector"
        )
    return result


def _difference(
    left: tuple[float, ...], right: tuple[float, ...]
) -> tuple[float, ...]:
    if len(left) != len(right):
        raise E1CommonProbeEC98AtomicVectorReceiptError(
            "S1-EC98 vector geometries differ"
        )
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC98ProbeVectorInput:
    refinement_id: str
    role_id: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    source_receipt_digest: str
    input_digest: str

    def __post_init__(self) -> None:
        activation = _finite_vector(self.activation, "activation")
        afterimage = _finite_vector(self.afterimage, "afterimage")
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "input_digest"
        }
        if (
            self.refinement_id not in S1_EC98_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or len(activation) != len(afterimage)
            or len(self.source_receipt_digest) != 64
            or self.input_digest != _digest(payload)
        ):
            raise E1CommonProbeEC98AtomicVectorReceiptError(
                "S1-EC98 vector input changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC98AtomicVectorReceipt:
    contract_id: str
    source_input_digests: tuple[str, ...]
    refinement_ids: tuple[str, ...]
    neuron_count: int
    active_order_vectors: tuple[
        tuple[str, tuple[float, ...], tuple[float, ...]], ...
    ]
    maximum_control_scalars: tuple[tuple[str, float, float], ...]
    source_probe_count: int
    all_roles_exact_once_per_refinement: bool
    common_vector_geometry: bool
    active_vector_count: int
    raw_role_vectors_retained: bool
    field_execution_performed: bool
    persistence_performed: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    receipt_digest: str

    def __post_init__(self) -> None:
        vectors = tuple(
            vector
            for _, activation, afterimage in self.active_order_vectors
            for vector in (activation, afterimage)
        )
        scalar_values = tuple(
            value
            for _, activation, afterimage in self.maximum_control_scalars
            for value in (activation, afterimage)
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            self.contract_id != S1_EC98_CONTRACT_ID
            or len(self.source_input_digests) != 24
            or len(set(self.source_input_digests)) != 24
            or self.refinement_ids != S1_EC98_REFINEMENTS
            or self.neuron_count < 1
            or tuple(item[0] for item in self.active_order_vectors)
            != S1_EC98_REFINEMENTS
            or len(vectors) != 6
            or any(len(item) != self.neuron_count for item in vectors)
            or tuple(item[0] for item in self.maximum_control_scalars)
            != S1_EC98_CONTROL_PREFIXES
            or any(not math.isfinite(value) or value < 0.0 for value in scalar_values)
            or self.source_probe_count != 24
            or any(
                value is not True
                for value in (
                    self.all_roles_exact_once_per_refinement,
                    self.common_vector_geometry,
                )
            )
            or self.active_vector_count != 6
            or any(
                value is not False
                for value in (
                    self.raw_role_vectors_retained,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status != "SIX_ACTIVE_ORDER_VECTORS_RETURNED_EC46_NOT_DECIDED"
            or self.receipt_digest != _digest(payload)
        ):
            raise E1CommonProbeEC98AtomicVectorReceiptError(
                "S1-EC98 atomic receipt changed or crossed scope"
            )


def build_e1_common_probe_ec98_atomic_vector_receipt(
    inputs: tuple[E1CommonProbeEC98ProbeVectorInput, ...],
) -> E1CommonProbeEC98AtomicVectorReceipt:
    """Reduce 24 existing probe inputs without executing or deciding a field."""

    samples = tuple(inputs)
    expected_order = tuple(
        (refinement, role)
        for refinement in S1_EC98_REFINEMENTS
        for role in S1_EC45_PROBE_ROLES
    )
    if (
        len(samples) != 24
        or tuple(
            (item.refinement_id, item.role_id)
            for item in samples
            if isinstance(item, E1CommonProbeEC98ProbeVectorInput)
        )
        != expected_order
    ):
        raise E1CommonProbeEC98AtomicVectorReceiptError(
            "S1-EC98 requires all 24 ordered typed probe inputs"
        )
    for item in samples:
        item.__post_init__()
    geometries = {
        (len(item.activation), len(item.afterimage)) for item in samples
    }
    if len(geometries) != 1:
        raise E1CommonProbeEC98AtomicVectorReceiptError(
            "S1-EC98 requires one common vector geometry"
        )
    neuron_count = next(iter(geometries))[0]
    by_key = {(item.refinement_id, item.role_id): item for item in samples}

    def order_vector(
        refinement: str, prefix: str, component: str
    ) -> tuple[float, ...]:
        return _difference(
            getattr(by_key[(refinement, f"{prefix}-ab")], component),
            getattr(by_key[(refinement, f"{prefix}-ba")], component),
        )

    active = tuple(
        (
            refinement,
            order_vector(refinement, "e1-active", "activation"),
            order_vector(refinement, "e1-active", "afterimage"),
        )
        for refinement in S1_EC98_REFINEMENTS
    )
    controls = tuple(
        (
            prefix,
            max(
                _linf(order_vector(refinement, prefix, "activation"))
                for refinement in S1_EC98_REFINEMENTS
            ),
            max(
                _linf(order_vector(refinement, prefix, "afterimage"))
                for refinement in S1_EC98_REFINEMENTS
            ),
        )
        for prefix in S1_EC98_CONTROL_PREFIXES
    )
    values = {
        "contract_id": S1_EC98_CONTRACT_ID,
        "source_input_digests": tuple(item.input_digest for item in samples),
        "refinement_ids": S1_EC98_REFINEMENTS,
        "neuron_count": neuron_count,
        "active_order_vectors": active,
        "maximum_control_scalars": controls,
        "source_probe_count": len(samples),
        "all_roles_exact_once_per_refinement": len(by_key) == 24,
        "common_vector_geometry": len(geometries) == 1,
        "active_vector_count": len(active) * 2,
        "raw_role_vectors_retained": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "SIX_ACTIVE_ORDER_VECTORS_RETURNED_EC46_NOT_DECIDED",
    }
    return E1CommonProbeEC98AtomicVectorReceipt(
        **values, receipt_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC98SyntheticFixtureResult:
    fixture_id: str
    source_input_digests: tuple[str, ...]
    vector_receipt_digest: str
    expected_active_order_vectors: tuple[
        tuple[str, tuple[float, ...], tuple[float, ...]], ...
    ]
    observed_active_order_vectors: tuple[
        tuple[str, tuple[float, ...], tuple[float, ...]], ...
    ]
    all_six_vectors_exact: bool
    controls_zero: bool
    field_steps_executed: int
    persistence_performed: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    result_digest: str
    receipt: E1CommonProbeEC98AtomicVectorReceipt = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "receipt"}
        }
        if (
            self.fixture_id != S1_EC98_FIXTURE_ID
            or self.source_input_digests != self.receipt.source_input_digests
            or self.vector_receipt_digest != self.receipt.receipt_digest
            or self.expected_active_order_vectors != self.observed_active_order_vectors
            or self.observed_active_order_vectors != self.receipt.active_order_vectors
            or self.all_six_vectors_exact is not True
            or self.controls_zero is not True
            or self.field_steps_executed != 0
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
            raise E1CommonProbeEC98AtomicVectorReceiptError(
                "S1-EC98 synthetic fixture changed"
            )


def run_e1_common_probe_ec98_synthetic_fixture(
) -> E1CommonProbeEC98SyntheticFixtureResult:
    """Prove vector retention and control reduction with zero field steps."""

    active_vectors = {
        "r2": ((3.0, -1.0, 0.5), (2.0, -0.5, 0.25)),
        "r4": ((2.0, -0.8, 0.4), (1.5, -0.4, 0.2)),
        "r8": ((1.5, -0.7, 0.35), (1.2, -0.35, 0.18)),
    }
    samples = []
    for refinement in S1_EC98_REFINEMENTS:
        for role in S1_EC45_PROBE_ROLES:
            activation = (0.0, 0.0, 0.0)
            afterimage = (0.0, 0.0, 0.0)
            if role == "e1-active-ab":
                activation, afterimage = active_vectors[refinement]
            values = {
                "refinement_id": refinement,
                "role_id": role,
                "activation": activation,
                "afterimage": afterimage,
                "source_receipt_digest": _digest(
                    (S1_EC98_FIXTURE_ID, refinement, role)
                ),
            }
            samples.append(
                E1CommonProbeEC98ProbeVectorInput(
                    **values, input_digest=_digest(values)
                )
            )
    inputs = tuple(samples)
    receipt = build_e1_common_probe_ec98_atomic_vector_receipt(inputs)
    expected = tuple(
        (refinement, *active_vectors[refinement])
        for refinement in S1_EC98_REFINEMENTS
    )
    values = {
        "fixture_id": S1_EC98_FIXTURE_ID,
        "source_input_digests": tuple(item.input_digest for item in inputs),
        "vector_receipt_digest": receipt.receipt_digest,
        "expected_active_order_vectors": expected,
        "observed_active_order_vectors": receipt.active_order_vectors,
        "all_six_vectors_exact": receipt.active_order_vectors == expected,
        "controls_zero": all(
            activation == 0.0 and afterimage == 0.0
            for _, activation, afterimage in receipt.maximum_control_scalars
        ),
        "field_steps_executed": 0,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC98SyntheticFixtureResult(
        **values, result_digest=_digest(values), receipt=receipt
    )
