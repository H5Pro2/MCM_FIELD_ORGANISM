"""S1-EC99 typed zero-step adapters into the EC98 vector receipt."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91ProbeReceipt,
)
from .e1_common_probe_ec98_atomic_vector_receipt import (
    E1CommonProbeEC98AtomicVectorReceipt,
    E1CommonProbeEC98ProbeVectorInput,
    S1_EC98_REFINEMENTS,
    build_e1_common_probe_ec98_atomic_vector_receipt,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepProbeReceipt,
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC99TypedVectorInputAdapterError(ValueError):
    """Raised when typed probe receipts cannot enter EC98 without ambiguity."""


S1_EC99_ADAPTER_ID = "e1.common-probe-typed-vector-input-adapters.s1ec99.v1"
S1_EC99_FIXTURE_ID = "e1.common-probe-typed-vector-input-fixture.s1ec99.v1"


def _vector_input(
    refinement_id: str,
    receipt: E1PositiveStepProbeReceipt | E1CommonProbeEC91ProbeReceipt,
) -> E1CommonProbeEC98ProbeVectorInput:
    values = {
        "refinement_id": refinement_id,
        "role_id": receipt.role_id,
        "activation": receipt.activation,
        "afterimage": receipt.afterimage,
        "source_receipt_digest": receipt.receipt_digest,
    }
    return E1CommonProbeEC98ProbeVectorInput(
        **values, input_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC99TypedVectorAdapterResult:
    adapter_id: str
    source_receipt_digests: tuple[str, ...]
    vector_input_digests: tuple[str, ...]
    refinement_counts: tuple[tuple[str, int], ...]
    all_source_receipts_typed: bool
    all_roles_exact_once_per_refinement: bool
    common_vector_geometry: bool
    field_steps_executed: int
    persistence_performed: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    vector_receipt_digest: str
    result_digest: str
    inputs: tuple[E1CommonProbeEC98ProbeVectorInput, ...] = field(
        repr=False, compare=False
    )
    vector_receipt: E1CommonProbeEC98AtomicVectorReceipt = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "inputs", "vector_receipt"}
        }
        if (
            self.adapter_id != S1_EC99_ADAPTER_ID
            or len(self.source_receipt_digests) != 24
            or len(set(self.source_receipt_digests)) != 24
            or len(self.inputs) != 24
            or self.source_receipt_digests
            != tuple(item.source_receipt_digest for item in self.inputs)
            or self.vector_input_digests
            != tuple(item.input_digest for item in self.inputs)
            or self.refinement_counts != (("r2", 8), ("r4", 8), ("r8", 8))
            or any(
                value is not True
                for value in (
                    self.all_source_receipts_typed,
                    self.all_roles_exact_once_per_refinement,
                    self.common_vector_geometry,
                )
            )
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status != "EC98_INPUTS_ADAPTED_SYNTHETICALLY_NO_EXECUTION"
            or self.vector_receipt_digest != self.vector_receipt.receipt_digest
            or self.vector_receipt.source_input_digests != self.vector_input_digests
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC99TypedVectorInputAdapterError(
                "S1-EC99 adapter result changed or crossed zero-step scope"
            )


def adapt_e1_common_probe_ec99_typed_vector_inputs(
    r2_probes: tuple[E1PositiveStepProbeReceipt, ...],
    r4_r8_probes: tuple[E1CommonProbeEC91ProbeReceipt, ...],
) -> E1CommonProbeEC99TypedVectorAdapterResult:
    """Adapt 8 r2 and 16 r4/r8 receipts without calling a field runtime."""

    r2 = tuple(r2_probes)
    refined = tuple(r4_r8_probes)
    if (
        len(r2) != 8
        or not all(isinstance(item, E1PositiveStepProbeReceipt) for item in r2)
        or tuple(item.role_id for item in r2) != S1_EC45_PROBE_ROLES
        or len(refined) != 16
        or not all(
            isinstance(item, E1CommonProbeEC91ProbeReceipt) for item in refined
        )
        or tuple((item.refinement_id, item.role_id) for item in refined)
        != tuple(
            (refinement, role)
            for refinement in ("r4", "r8")
            for role in S1_EC45_PROBE_ROLES
        )
    ):
        raise E1CommonProbeEC99TypedVectorInputAdapterError(
            "S1-EC99 requires ordered typed r2 and r4/r8 probe receipts"
        )
    for item in (*r2, *refined):
        item.__post_init__()

    source_receipts = (*r2, *refined)
    source_digests = tuple(item.receipt_digest for item in source_receipts)
    if len(set(source_digests)) != 24:
        raise E1CommonProbeEC99TypedVectorInputAdapterError(
            "S1-EC99 requires 24 distinct source receipts"
        )
    inputs = tuple(
        _vector_input("r2", item) for item in r2
    ) + tuple(_vector_input(item.refinement_id, item) for item in refined)
    geometries = {
        (len(item.activation), len(item.afterimage)) for item in inputs
    }
    if len(geometries) != 1:
        raise E1CommonProbeEC99TypedVectorInputAdapterError(
            "S1-EC99 requires one common vector geometry"
        )
    vector_receipt = build_e1_common_probe_ec98_atomic_vector_receipt(inputs)
    values = {
        "adapter_id": S1_EC99_ADAPTER_ID,
        "source_receipt_digests": source_digests,
        "vector_input_digests": tuple(item.input_digest for item in inputs),
        "refinement_counts": tuple(
            (refinement, sum(item.refinement_id == refinement for item in inputs))
            for refinement in S1_EC98_REFINEMENTS
        ),
        "all_source_receipts_typed": True,
        "all_roles_exact_once_per_refinement": tuple(
            (item.refinement_id, item.role_id) for item in inputs
        )
        == tuple(
            (refinement, role)
            for refinement in S1_EC98_REFINEMENTS
            for role in S1_EC45_PROBE_ROLES
        ),
        "common_vector_geometry": len(geometries) == 1,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "EC98_INPUTS_ADAPTED_SYNTHETICALLY_NO_EXECUTION",
        "vector_receipt_digest": vector_receipt.receipt_digest,
    }
    return E1CommonProbeEC99TypedVectorAdapterResult(
        **values,
        result_digest=_digest(values),
        inputs=inputs,
        vector_receipt=vector_receipt,
    )


def _synthetic_receipt_vectors(
    refinement_id: str, role_id: str
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    scale = {"r2": 3.0, "r4": 2.0, "r8": 1.5}[refinement_id]
    direction = 1.0 if role_id.endswith("-ab") else -1.0
    family = S1_EC45_PROBE_ROLES.index(role_id) // 2 + 1
    activation = (direction * scale * family, scale / 10.0, -scale / 20.0)
    afterimage = (direction * scale * family / 2.0, scale / 20.0, -scale / 40.0)
    return activation, afterimage


def _synthetic_r2_receipt(role_id: str) -> E1PositiveStepProbeReceipt:
    route = dict(S1_EC63_ROLE_STATE_ROUTES)[role_id]
    activation, afterimage = _synthetic_receipt_vectors("r2", role_id)
    values = {
        "role_id": role_id,
        "binding_digest": _digest((S1_EC99_FIXTURE_ID, "r2", role_id, "binding")),
        "selected_state_role": route,
        "selected_state_digest": None
        if route is None
        else _digest((S1_EC99_FIXTURE_ID, "r2", route, "state")),
        "backreaction_enabled": route is not None
        and "probe-feedback-ablated" not in role_id,
        "activation": activation,
        "afterimage": afterimage,
        "accounted_field_steps": 200,
        "source_support_count": 110,
        "source_result_digest": _digest(
            (S1_EC99_FIXTURE_ID, "r2", role_id, "source")
        ),
        "execution_mode": "synthetic-contract",
    }
    return E1PositiveStepProbeReceipt(**values, receipt_digest=_digest(values))


def _synthetic_refined_receipt(
    refinement_id: str, role_id: str
) -> E1CommonProbeEC91ProbeReceipt:
    route = dict(S1_EC63_ROLE_STATE_ROUTES)[role_id]
    activation, afterimage = _synthetic_receipt_vectors(refinement_id, role_id)
    values = {
        "refinement_id": refinement_id,
        "role_id": role_id,
        "binding_digest": _digest(
            (S1_EC99_FIXTURE_ID, refinement_id, role_id, "binding")
        ),
        "selected_state_role": route,
        "selected_state_digest": None
        if route is None
        else _digest((S1_EC99_FIXTURE_ID, refinement_id, route, "state")),
        "backreaction_enabled": route is not None
        and "probe-feedback-ablated" not in role_id,
        "activation": activation,
        "afterimage": afterimage,
        "accounted_field_steps": {"r4": 400, "r8": 800}[refinement_id],
        "source_support_count": 110,
        "source_result_digest": _digest(
            (S1_EC99_FIXTURE_ID, refinement_id, role_id, "source")
        ),
        "execution_mode": "synthetic-typed-output",
    }
    return E1CommonProbeEC91ProbeReceipt(
        **values, receipt_digest=_digest(values)
    )


def run_e1_common_probe_ec99_synthetic_fixture(
) -> E1CommonProbeEC99TypedVectorAdapterResult:
    """Exercise both typed adapters with synthetic receipts and zero field steps."""

    r2 = tuple(_synthetic_r2_receipt(role) for role in S1_EC45_PROBE_ROLES)
    refined = tuple(
        _synthetic_refined_receipt(refinement, role)
        for refinement in ("r4", "r8")
        for role in S1_EC45_PROBE_ROLES
    )
    return adapt_e1_common_probe_ec99_typed_vector_inputs(r2, refined)
