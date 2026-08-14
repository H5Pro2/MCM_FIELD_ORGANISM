"""S1-EC63 positive-step receipt contract for the bounded n2/r2 run."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_real_binding_contract import S1_EC52_FORMATION_STATE_ROLES
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_formation_runner import _digest, _state_payload


class E1CommonProbeN2R2PositiveStepReceiptContractError(ValueError):
    """Raised when EC63 changes the bounded positive-step receipt contract."""


S1_EC63_CONTRACT_ID = "e1.common-probe-n2-r2-positive-step-receipts.s1ec63.v1"
S1_EC63_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC63_EXECUTION_MODES = ("synthetic-contract", "real-wrapper")
S1_EC63_ROLE_STATE_ROUTES = (
    ("p0-reset-ab", None),
    ("p0-reset-ba", None),
    ("e1-active-ab", "active-ab"),
    ("e1-active-ba", "active-ba"),
    ("e1-probe-feedback-ablated-ab", "active-ab"),
    ("e1-probe-feedback-ablated-ba", "active-ba"),
    ("e1-formation-ablated-ab", "formation-ablated-ab"),
    ("e1-formation-ablated-ba", "formation-ablated-ba"),
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1PositiveStepFormationReceipt:
    state_role: str
    output_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)
    output_state_digest: str
    accounted_field_steps: int
    source_result_digest: str
    execution_mode: str
    receipt_digest: str

    def __post_init__(self) -> None:
        values = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"output_state", "receipt_digest"}
        }
        if (
            self.state_role not in S1_EC52_FORMATION_STATE_ROLES
            or not isinstance(self.output_state, E1LocalEdgePlasticityState)
            or self.output_state_digest != _digest(_state_payload(self.output_state))
            or self.accounted_field_steps != 402
            or not _valid_digest(self.source_result_digest)
            or self.execution_mode not in S1_EC63_EXECUTION_MODES
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeN2R2PositiveStepReceiptContractError(
                "S1-EC63 formation receipt changed"
            )


@dataclass(frozen=True, slots=True)
class E1PositiveStepProbeReceipt:
    role_id: str
    binding_digest: str
    selected_state_role: str | None
    selected_state_digest: str | None
    backreaction_enabled: bool
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    accounted_field_steps: int
    source_support_count: int
    source_result_digest: str
    execution_mode: str
    receipt_digest: str

    def __post_init__(self) -> None:
        route = dict(S1_EC63_ROLE_STATE_ROUTES).get(self.role_id, "missing")
        values = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            self.role_id not in S1_EC45_PROBE_ROLES
            or route != self.selected_state_role
            or not _valid_digest(self.binding_digest)
            or (self.selected_state_digest is None) is not (self.selected_state_role is None)
            or (self.selected_state_digest is not None and not _valid_digest(self.selected_state_digest))
            or self.backreaction_enabled is not (
                self.selected_state_role is not None
                and "probe-feedback-ablated" not in self.role_id
            )
            or not self.activation
            or len(self.activation) != len(self.afterimage)
            or self.accounted_field_steps != 200
            or self.source_support_count < 1
            or not _valid_digest(self.source_result_digest)
            or self.execution_mode not in S1_EC63_EXECUTION_MODES
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeN2R2PositiveStepReceiptContractError(
                "S1-EC63 probe receipt changed"
            )


@dataclass(frozen=True, slots=True)
class E1PositiveStepReceiptContractFixtureResult:
    contract_id: str
    source_handoff_digest: str
    execution_mode: str
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    formation_count: int
    probe_count: int
    accounted_formation_steps: int
    accounted_probe_steps: int
    accounted_total_steps: int
    actual_field_steps_executed: int
    all_role_routes_exact: bool
    all_positive_step_bounds_exact: bool
    real_wrapper_adapter_implementation_permitted: bool
    real_wrapper_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1PositiveStepFormationReceipt, ...] = field(repr=False, compare=False)
    probes: tuple[E1PositiveStepProbeReceipt, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        metadata = _fixture_metadata(self)
        if (
            self.contract_id != S1_EC63_CONTRACT_ID
            or self.source_handoff_digest != S1_EC63_EC59_HANDOFF_DIGEST
            or self.execution_mode != "synthetic-contract"
            or (self.formation_count, self.probe_count) != (4, 8)
            or self.formation_receipt_digests != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests != tuple(item.receipt_digest for item in self.probes)
            or (self.accounted_formation_steps, self.accounted_probe_steps, self.accounted_total_steps) != (1608, 1600, 3208)
            or self.actual_field_steps_executed != 0
            or any(value is not True for value in (
                self.all_role_routes_exact,
                self.all_positive_step_bounds_exact,
                self.real_wrapper_adapter_implementation_permitted,
            ))
            or any(value is not False for value in (
                self.real_wrapper_execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2PositiveStepReceiptContractError(
                "S1-EC63 fixture changed or crossed synthetic scope"
            )


def _fixture_metadata(
    result: E1PositiveStepReceiptContractFixtureResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in (
            "contract_id",
            "source_handoff_digest",
            "execution_mode",
            "formation_receipt_digests",
            "probe_receipt_digests",
            "formation_count",
            "probe_count",
            "accounted_formation_steps",
            "accounted_probe_steps",
            "accounted_total_steps",
            "actual_field_steps_executed",
            "all_role_routes_exact",
            "all_positive_step_bounds_exact",
            "real_wrapper_adapter_implementation_permitted",
            "real_wrapper_execution_permitted",
            "persistence_performed",
            "research_decision_permitted",
            "memory_claim_permitted",
        )
    }


def build_e1_common_probe_n2_r2_positive_step_receipt_fixture(
    handoff: E1CommonProbeN2R2ObjectHandoff,
) -> E1PositiveStepReceiptContractFixtureResult:
    """Build synthetic positive-step receipts without invoking any kernel."""

    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC63_EC59_HANDOFF_DIGEST
    ):
        raise E1CommonProbeN2R2PositiveStepReceiptContractError(
            "S1-EC63 requires the exact EC59 handoff"
        )
    handoff.__post_init__()
    formations = []
    states = {}
    for role in handoff.formation_state_roles:
        state = copy.deepcopy(handoff.initial_state)
        values = {
            "state_role": role,
            "output_state_digest": _digest(_state_payload(state)),
            "accounted_field_steps": 402,
            "source_result_digest": _digest(("synthetic-contract", role, 402)),
            "execution_mode": "synthetic-contract",
        }
        receipt = E1PositiveStepFormationReceipt(
            **values,
            output_state=state,
            receipt_digest=_digest(values),
        )
        formations.append(receipt)
        states[role] = receipt
    probes = []
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    for slot in handoff.resolved_slots:
        state_role = routes[slot.binding.role_id]
        state_digest = None if state_role is None else states[state_role].output_state_digest
        values = {
            "role_id": slot.binding.role_id,
            "binding_digest": slot.binding.binding_digest,
            "selected_state_role": state_role,
            "selected_state_digest": state_digest,
            "backreaction_enabled": slot.binding.backreaction_enabled,
            "activation": (0.0, 0.0, 0.0),
            "afterimage": (0.0, 0.0, 0.0),
            "accounted_field_steps": 200,
            "source_support_count": slot.probe_plan.handoff.source_event_count,
            "source_result_digest": _digest(("synthetic-contract", slot.binding.role_id, 200)),
            "execution_mode": "synthetic-contract",
        }
        probes.append(E1PositiveStepProbeReceipt(**values, receipt_digest=_digest(values)))
    values = {
        "contract_id": S1_EC63_CONTRACT_ID,
        "source_handoff_digest": handoff.handoff_digest,
        "execution_mode": "synthetic-contract",
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "formation_count": len(formations),
        "probe_count": len(probes),
        "accounted_formation_steps": sum(item.accounted_field_steps for item in formations),
        "accounted_probe_steps": sum(item.accounted_field_steps for item in probes),
        "accounted_total_steps": sum(item.accounted_field_steps for item in (*formations, *probes)),
        "actual_field_steps_executed": 0,
        "all_role_routes_exact": tuple((item.role_id, item.selected_state_role) for item in probes) == S1_EC63_ROLE_STATE_ROUTES,
        "all_positive_step_bounds_exact": all(item.accounted_field_steps == 402 for item in formations) and all(item.accounted_field_steps == 200 for item in probes),
        "real_wrapper_adapter_implementation_permitted": True,
        "real_wrapper_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1PositiveStepReceiptContractFixtureResult(
        **values,
        result_digest=_digest(values),
        formations=tuple(formations),
        probes=tuple(probes),
    )
