"""S1-HI discrete DTS-1 resource anatomy without dynamics or field coupling."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math


class DTS1S1HIResourceAnatomyError(ValueError):
    """Raised when a DTS-1 anatomy or resource ledger is invalid."""


S1_HI_CONTRACT_ID = "dynamic-substrate.resource-anatomy.s1hi.v1"
S1_HI_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_HI_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HI_STORED_ROLES = (
    "fixed-positive-node-capacity",
    "conductive-bound-resource-per-existing-undirected-edge",
    "refractory-resource-per-existing-undirected-edge",
)
S1_HI_DERIVED_ROLES = (
    "free-node-resource-as-capacity-remainder",
    "local-node-ledger-from-half-shares-of-incident-edge-resources",
    "global-ledger-from-single-counted-undirected-edge-resources",
)
S1_HI_STRUCTURAL_DISTINCTIONS = (
    (
        "fixed-adapter",
        "stores fixed edge coefficients and has no finite three-role resource ledger",
    ),
    (
        "gain",
        "scales a response and has no conserved free-bound-refractory partition",
    ),
    (
        "fast-afterimage",
        "is part of the S/H field state and not an edge-resource compartment",
    ),
    (
        "integrator",
        "accumulates a signal and does not derive free capacity from an exact edge ledger",
    ),
    (
        "replay",
        "stores or replays input content while DTS-1 stores only content-free amounts",
    ),
)
S1_HI_INVALID_STATE_CLASSES = (
    "empty-or-duplicate-node-inventory",
    "nonpositive-or-nonfinite-node-capacity",
    "empty-duplicate-noncanonical-or-self-edge-inventory",
    "edge-endpoint-absent-from-node-inventory",
    "negative-or-nonfinite-conductive-bound-resource",
    "negative-or-nonfinite-refractory-resource",
    "incident-edge-allocation-exceeds-local-node-capacity",
    "stored-free-resource-duplicating-the-derived-ledger",
    "field-state-adapter-gain-integrator-or-replay-content-in-the-anatomy",
    "clipping-normalization-or-repair-of-an-invalid-state",
)
S1_HI_DECISION = "DTS1_DISCRETE_RESOURCE_ANATOMY_AND_LOCAL_IDENTITY_BOUND"


def _finite_nonnegative(value: object, role: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise DTS1S1HIResourceAnatomyError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1S1HIResourceAnatomyError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0 or (positive and result == 0.0):
        qualifier = "positive" if positive else "nonnegative"
        raise DTS1S1HIResourceAnatomyError(
            f"{role} must be finite and {qualifier}"
        )
    return result


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1NodeCapacity:
    """One fixed positive capacity at one existing field node."""

    node_id: str
    capacity: float

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id:
            raise DTS1S1HIResourceAnatomyError("node_id must be one nonempty string")
        object.__setattr__(
            self,
            "capacity",
            _finite_nonnegative(self.capacity, "capacity", positive=True),
        )


@dataclass(frozen=True, slots=True)
class DTS1EdgeResource:
    """The two stored resource roles on one canonical undirected edge."""

    first_node_id: str
    second_node_id: str
    conductive_bound: float
    refractory: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_node_id, str)
            or not self.first_node_id
            or not isinstance(self.second_node_id, str)
            or not self.second_node_id
            or self.first_node_id >= self.second_node_id
        ):
            raise DTS1S1HIResourceAnatomyError(
                "edge endpoints must be nonempty, distinct, and canonical"
            )
        object.__setattr__(
            self,
            "conductive_bound",
            _finite_nonnegative(self.conductive_bound, "conductive_bound"),
        )
        object.__setattr__(
            self,
            "refractory",
            _finite_nonnegative(self.refractory, "refractory"),
        )

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_node_id, self.second_node_id)


@dataclass(frozen=True, slots=True)
class DTS1NodeResourceLedger:
    """One derived local identity; no value in this ledger is an update rule."""

    node_id: str
    capacity: float
    free: float
    conductive_half_shares: float
    refractory_half_shares: float

    @property
    def accounted_total(self) -> float:
        return math.fsum(
            (self.free, self.conductive_half_shares, self.refractory_half_shares)
        )

    @property
    def residual(self) -> float:
        return self.capacity - self.accounted_total


@dataclass(frozen=True, slots=True)
class DTS1ResourceAnatomy:
    """Complete immutable DTS-1 anatomy with derived free resource only."""

    node_capacities: tuple[DTS1NodeCapacity, ...]
    edge_resources: tuple[DTS1EdgeResource, ...]

    def __post_init__(self) -> None:
        nodes = tuple(self.node_capacities)
        edges = tuple(self.edge_resources)
        if not nodes or any(not isinstance(item, DTS1NodeCapacity) for item in nodes):
            raise DTS1S1HIResourceAnatomyError(
                "DTS-1 anatomy requires a nonempty node inventory"
            )
        if not edges or any(not isinstance(item, DTS1EdgeResource) for item in edges):
            raise DTS1S1HIResourceAnatomyError(
                "DTS-1 anatomy requires a nonempty edge inventory"
            )
        node_ids = [item.node_id for item in nodes]
        edge_ids = [item.edge for item in edges]
        if len(set(node_ids)) != len(node_ids):
            raise DTS1S1HIResourceAnatomyError("node identities must be unique")
        if len(set(edge_ids)) != len(edge_ids):
            raise DTS1S1HIResourceAnatomyError("edge identities must be unique")
        known_nodes = set(node_ids)
        if any(set(edge) - known_nodes for edge in edge_ids):
            raise DTS1S1HIResourceAnatomyError(
                "every edge endpoint must belong to the node inventory"
            )
        object.__setattr__(
            self, "node_capacities", tuple(sorted(nodes, key=lambda item: item.node_id))
        )
        object.__setattr__(
            self, "edge_resources", tuple(sorted(edges, key=lambda item: item.edge))
        )
        self.local_ledgers()

    @property
    def edge_inventory_digest(self) -> str:
        return _digest(tuple(item.edge for item in self.edge_resources))

    def local_ledgers(self) -> tuple[DTS1NodeResourceLedger, ...]:
        """Derive the local conservation identity and reject over-allocation."""

        incident_conductive: dict[str, list[float]] = {
            item.node_id: [] for item in self.node_capacities
        }
        incident_refractory: dict[str, list[float]] = {
            item.node_id: [] for item in self.node_capacities
        }
        for edge in self.edge_resources:
            for node_id in edge.edge:
                incident_conductive[node_id].append(0.5 * edge.conductive_bound)
                incident_refractory[node_id].append(0.5 * edge.refractory)
        ledgers = []
        for node in self.node_capacities:
            conductive = math.fsum(incident_conductive[node.node_id])
            refractory = math.fsum(incident_refractory[node.node_id])
            allocated = math.fsum((conductive, refractory))
            if allocated > node.capacity:
                raise DTS1S1HIResourceAnatomyError(
                    f"incident edge resources exceed capacity at {node.node_id}"
                )
            ledgers.append(
                DTS1NodeResourceLedger(
                    node_id=node.node_id,
                    capacity=node.capacity,
                    free=node.capacity - allocated,
                    conductive_half_shares=conductive,
                    refractory_half_shares=refractory,
                )
            )
        return tuple(ledgers)

    @property
    def global_capacity(self) -> float:
        return math.fsum(item.capacity for item in self.node_capacities)

    @property
    def global_accounted_resource(self) -> float:
        free = math.fsum(item.free for item in self.local_ledgers())
        conductive = math.fsum(item.conductive_bound for item in self.edge_resources)
        refractory = math.fsum(item.refractory for item in self.edge_resources)
        return math.fsum((free, conductive, refractory))

    @property
    def global_residual(self) -> float:
        return self.global_capacity - self.global_accounted_resource


@dataclass(frozen=True, slots=True)
class DTS1S1HIAnatomyContract:
    contract_id: str
    source_s1hh_contract_digest: str
    candidate_id: str
    stored_roles: tuple[str, ...]
    derived_roles: tuple[str, ...]
    structural_distinctions: tuple[tuple[str, str], ...]
    invalid_state_classes: tuple[str, ...]
    free_resource_is_derived_not_stored: bool
    local_identity_bound: bool
    global_identity_follows_from_local_identity: bool
    equation_selected: bool
    parameters_selected: bool
    runtime_implemented: bool
    field_coupling_selected: bool
    functional_effect_proven: bool
    execution_permitted: bool
    field_steps_executed: int
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_HI_CONTRACT_ID
            or self.source_s1hh_contract_digest
            != S1_HI_SOURCE_S1HH_CONTRACT_DIGEST
            or self.candidate_id != S1_HI_CANDIDATE_ID
            or self.stored_roles != S1_HI_STORED_ROLES
            or self.derived_roles != S1_HI_DERIVED_ROLES
            or self.structural_distinctions != S1_HI_STRUCTURAL_DISTINCTIONS
            or self.invalid_state_classes != S1_HI_INVALID_STATE_CLASSES
            or any(
                value is not True
                for value in (
                    self.free_resource_is_derived_not_stored,
                    self.local_identity_bound,
                    self.global_identity_follows_from_local_identity,
                )
            )
            or any(
                value is not False
                for value in (
                    self.equation_selected,
                    self.parameters_selected,
                    self.runtime_implemented,
                    self.field_coupling_selected,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HI_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HIResourceAnatomyError(
                "S1-HI weakened the anatomy-only or no-dynamics boundary"
            )


def build_dts1_s1hi_anatomy_contract() -> DTS1S1HIAnatomyContract:
    """Bind anatomy and conservation only, without selecting dynamics."""

    values = {
        "contract_id": S1_HI_CONTRACT_ID,
        "source_s1hh_contract_digest": S1_HI_SOURCE_S1HH_CONTRACT_DIGEST,
        "candidate_id": S1_HI_CANDIDATE_ID,
        "stored_roles": S1_HI_STORED_ROLES,
        "derived_roles": S1_HI_DERIVED_ROLES,
        "structural_distinctions": S1_HI_STRUCTURAL_DISTINCTIONS,
        "invalid_state_classes": S1_HI_INVALID_STATE_CLASSES,
        "free_resource_is_derived_not_stored": True,
        "local_identity_bound": True,
        "global_identity_follows_from_local_identity": True,
        "equation_selected": False,
        "parameters_selected": False,
        "runtime_implemented": False,
        "field_coupling_selected": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HI_DECISION,
    }
    return DTS1S1HIAnatomyContract(**values, contract_digest=_digest(values))
