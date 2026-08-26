"""Pure isolated DTS-1 closed-prestate step.

This private module has no field, runtime, persistence, or public API wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re

from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1ResourceAnatomy,
)


class DTS1StepError(ValueError):
    """Raised before output when a pure DTS-1 step is invalid."""


S1_HP_IMPLEMENTATION_ID = "dynamic-substrate.pure-step.s1hp.v1"
S1_HP_SOURCE_S1HO_CONTRACT_DIGEST = (
    "7b653c88704f144678f2c9f8fb15e37b695a8fd518034cf261707337e0f5d870"
)
S1_HP_DECISION = "DTS1_PURE_STEP_IMPLEMENTED_TECHNICALLY_ACCEPTED"
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1StepError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1StepError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1StepError(f"{role} must be finite and nonnegative")
    return result


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _anatomy_digest(anatomy: DTS1ResourceAnatomy) -> str:
    return _digest(
        {
            "node_capacities": tuple(
                (item.node_id, item.capacity) for item in anatomy.node_capacities
            ),
            "edge_resources": tuple(
                (
                    item.first_node_id,
                    item.second_node_id,
                    item.conductive_bound,
                    item.refractory,
                )
                for item in anatomy.edge_resources
            ),
        }
    )


@dataclass(frozen=True, slots=True)
class DTS1StepRates:
    """Three explicit global content-free rates for one synthetic step."""

    binding_rate: float
    turnover_rate: float
    recovery_rate: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "binding_rate",
            _finite_nonnegative(self.binding_rate, "binding_rate"),
        )
        object.__setattr__(
            self,
            "turnover_rate",
            _finite_nonnegative(self.turnover_rate, "turnover_rate"),
        )
        object.__setattr__(
            self,
            "recovery_rate",
            _finite_nonnegative(self.recovery_rate, "recovery_rate"),
        )


@dataclass(frozen=True, slots=True)
class DTS1EdgeParticipation:
    """One externally supplied S1-HK participation on a canonical edge."""

    first_node_id: str
    second_node_id: str
    participation: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_node_id, str)
            or not self.first_node_id
            or not isinstance(self.second_node_id, str)
            or not self.second_node_id
            or self.first_node_id >= self.second_node_id
        ):
            raise DTS1StepError(
                "participation edge endpoints must be nonempty and canonical"
            )
        value = _finite_nonnegative(self.participation, "participation")
        if value > 1.0:
            raise DTS1StepError("participation must not exceed one")
        object.__setattr__(self, "participation", value)

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_node_id, self.second_node_id)


@dataclass(frozen=True, slots=True)
class DTS1EdgeTransfer:
    """Passive transfer ledger for one canonical edge and one step."""

    first_node_id: str
    second_node_id: str
    engagement: float
    turnover: float
    recovery: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_node_id, str)
            or not self.first_node_id
            or not isinstance(self.second_node_id, str)
            or not self.second_node_id
            or self.first_node_id >= self.second_node_id
        ):
            raise DTS1StepError(
                "transfer edge endpoints must be nonempty and canonical"
            )
        for role in ("engagement", "turnover", "recovery"):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_node_id, self.second_node_id)


@dataclass(frozen=True, slots=True)
class DTS1StepResult:
    """One complete new anatomy plus passive transfer diagnostics."""

    next_anatomy: DTS1ResourceAnatomy
    edge_transfers: tuple[DTS1EdgeTransfer, ...]
    input_anatomy_digest: str
    output_anatomy_digest: str
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if not isinstance(self.next_anatomy, DTS1ResourceAnatomy):
            raise DTS1StepError("result requires one complete DTS-1 anatomy")
        transfers = tuple(self.edge_transfers)
        if not transfers or any(
            not isinstance(item, DTS1EdgeTransfer) for item in transfers
        ):
            raise DTS1StepError("result requires one complete transfer ledger")
        edges = tuple(item.edge for item in transfers)
        anatomy_edges = tuple(item.edge for item in self.next_anatomy.edge_resources)
        if len(set(edges)) != len(edges) or tuple(sorted(edges)) != anatomy_edges:
            raise DTS1StepError("result transfer ledger must match anatomy edges")
        for role in ("input_anatomy_digest", "output_anatomy_digest"):
            value = getattr(self, role)
            if not isinstance(value, str) or not _DIGEST_PATTERN.fullmatch(value):
                raise DTS1StepError(f"{role} must be one lowercase SHA-256 digest")
        if self.output_anatomy_digest != _anatomy_digest(self.next_anatomy):
            raise DTS1StepError("output_anatomy_digest must identify next_anatomy")
        for role in ("maximum_local_ledger_residual", "global_ledger_residual"):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )
        object.__setattr__(self, "edge_transfers", tuple(sorted(transfers, key=lambda x: x.edge)))


@dataclass(frozen=True, slots=True)
class DTS1S1HPImplementationReceipt:
    implementation_id: str
    source_s1ho_contract_digest: str
    matrix_case_ids: tuple[str, ...]
    pure_step_implemented: bool
    existing_s1hi_anatomy_reused: bool
    field_import_present: bool
    runtime_integration_present: bool
    parameter_corridor_selected: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_HP_IMPLEMENTATION_ID
            or self.source_s1ho_contract_digest
            != S1_HP_SOURCE_S1HO_CONTRACT_DIGEST
            or self.matrix_case_ids
            != tuple(f"T{index:02d}" for index in range(1, 18))
            or self.pure_step_implemented is not True
            or self.existing_s1hi_anatomy_reused is not True
            or any(
                value is not False
                for value in (
                    self.field_import_present,
                    self.runtime_integration_present,
                    self.parameter_corridor_selected,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HP_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1StepError("S1-HP implementation receipt boundary weakened")


def build_dts1_s1hp_implementation_receipt() -> DTS1S1HPImplementationReceipt:
    """Return the static acceptance receipt; this executes no step."""

    values = {
        "implementation_id": S1_HP_IMPLEMENTATION_ID,
        "source_s1ho_contract_digest": S1_HP_SOURCE_S1HO_CONTRACT_DIGEST,
        "matrix_case_ids": tuple(f"T{index:02d}" for index in range(1, 18)),
        "pure_step_implemented": True,
        "existing_s1hi_anatomy_reused": True,
        "field_import_present": False,
        "runtime_integration_present": False,
        "parameter_corridor_selected": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HP_DECISION,
    }
    return DTS1S1HPImplementationReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def compute_dts1_closed_prestate_step(
    anatomy: DTS1ResourceAnatomy,
    edge_participations: tuple[DTS1EdgeParticipation, ...],
    elapsed_time: object,
    rates: DTS1StepRates,
) -> DTS1StepResult:
    """Compute one pure S1-HN map from one complete closed prestate."""

    if not isinstance(anatomy, DTS1ResourceAnatomy):
        raise DTS1StepError("step requires one valid DTS-1 anatomy")
    interval = _finite_nonnegative(elapsed_time, "elapsed_time")
    if not isinstance(rates, DTS1StepRates):
        raise DTS1StepError("step requires one DTS1StepRates value")

    try:
        participations = tuple(edge_participations)
    except TypeError as exc:
        raise DTS1StepError(
            "step requires an iterable complete participation ledger"
        ) from exc
    if not participations or any(
        not isinstance(item, DTS1EdgeParticipation) for item in participations
    ):
        raise DTS1StepError("step requires a complete participation ledger")
    participation_edges = tuple(item.edge for item in participations)
    if len(set(participation_edges)) != len(participation_edges):
        raise DTS1StepError("participation edge identities must be unique")
    anatomy_edges = tuple(item.edge for item in anatomy.edge_resources)
    if tuple(sorted(participation_edges)) != anatomy_edges:
        raise DTS1StepError("participations must match the complete anatomy edges")
    participation_by_edge = {
        item.edge: item.participation for item in participations
    }

    free_by_node = {item.node_id: item.free for item in anatomy.local_ledgers()}
    alpha_bind = -math.expm1(-rates.binding_rate * interval)
    alpha_turn = -math.expm1(-rates.turnover_rate * interval)
    alpha_rec = -math.expm1(-rates.recovery_rate * interval)

    offers: dict[tuple[str, str], float] = {}
    demand_terms: dict[str, list[float]] = {
        item.node_id: [] for item in anatomy.node_capacities
    }
    for edge in anatomy.edge_resources:
        first, second = edge.edge
        offer = _finite_nonnegative(
            alpha_bind
            * participation_by_edge[edge.edge]
            * 2.0
            * min(free_by_node[first], free_by_node[second]),
            "engagement_offer",
        )
        offers[edge.edge] = offer
        demand_terms[first].append(0.5 * offer)
        demand_terms[second].append(0.5 * offer)

    demands: dict[str, float] = {}
    admissions: dict[str, float] = {}
    try:
        for node_id, terms in demand_terms.items():
            demand = math.fsum(terms)
            demands[node_id] = _finite_nonnegative(demand, "node_demand")
            admissions[node_id] = (
                1.0
                if demand == 0.0
                else min(1.0, free_by_node[node_id] / demand)
            )
    except OverflowError as exc:
        raise DTS1StepError("node demand must remain finite") from exc

    transfers = []
    next_edges = []
    for edge in anatomy.edge_resources:
        first, second = edge.edge
        engagement = _finite_nonnegative(
            offers[edge.edge] * min(admissions[first], admissions[second]),
            "engagement",
        )
        turnover = _finite_nonnegative(
            alpha_turn * edge.conductive_bound,
            "turnover",
        )
        recovery = _finite_nonnegative(
            alpha_rec * edge.refractory,
            "recovery",
        )
        transfers.append(
            DTS1EdgeTransfer(
                first,
                second,
                engagement,
                turnover,
                recovery,
            )
        )
        try:
            next_edges.append(
                DTS1EdgeResource(
                    first,
                    second,
                    edge.conductive_bound + engagement - turnover,
                    edge.refractory + turnover - recovery,
                )
            )
        except ValueError as exc:
            raise DTS1StepError("atomic edge commit produced an invalid state") from exc

    try:
        next_anatomy = DTS1ResourceAnatomy(
            node_capacities=anatomy.node_capacities,
            edge_resources=tuple(next_edges),
        )
    except ValueError as exc:
        raise DTS1StepError("atomic anatomy commit violated the resource ledger") from exc

    local_residuals = tuple(
        abs(item.residual) for item in next_anatomy.local_ledgers()
    )
    maximum_local_residual = max(local_residuals, default=0.0)
    global_residual = abs(next_anatomy.global_residual)
    return DTS1StepResult(
        next_anatomy=next_anatomy,
        edge_transfers=tuple(transfers),
        input_anatomy_digest=_anatomy_digest(anatomy),
        output_anatomy_digest=_anatomy_digest(next_anatomy),
        maximum_local_ledger_residual=maximum_local_residual,
        global_ledger_residual=global_residual,
    )
