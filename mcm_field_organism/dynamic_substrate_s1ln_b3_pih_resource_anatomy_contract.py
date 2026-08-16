"""S1-LN static C10 resource anatomy and conservation contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from .dynamic_substrate_s1hi_resource_anatomy import (
    build_dts1_s1hi_anatomy_contract,
)
from .dynamic_substrate_s1hh_function_falsification_contract import (
    S1_HH_CANDIDATE_ID as S1_HH_CANDIDATE_ID,
)
from .dynamic_substrate_s1lm_b3_pih_case_selection_contract import (
    build_dts1_s1lm_b3_pih_case_selection_contract,
    S1_LM_CASE_ID,
    S1_LM_DECISION,
    S1_LM_SEQUENCE_KEY,
    S1_LM_SEQUENCE_RECORD,
    S1_LM_TARGET_CASE_RECORD,
    S1_LM_TARGET_REPLICA_IDS,
)


class DTS1S1LNResourceAnatomyContractError(ValueError):
    """Raised when S1-LN static anatomy boundary is weakened."""


S1_LN_CONTRACT_ID = "dynamic-substrate.c10-resource-anatomy-and-conservation.s1ln.v1"
S1_LN_SOURCE_S1HI_CONTRACT_DIGEST = (
    "35110510a4b9d08a24f60557faf9b83b26b416bdf893112d42801ef5a16c7ede"
)
S1_LN_CASE_ID = S1_LM_CASE_ID
S1_LN_BASELINE = "B3"
S1_LN_PROFILE = "P_IH_ATTENUATION"
S1_LN_GEOMETRY = "TWO_NODE_OPEN_LINE"
S1_LN_NODE_CAPACITIES = (
    ("node-a", 0.5),
    ("node-b", 0.5),
)
S1_LN_EDGE_ROLES = (
    ("node-a", "node-b", 0.20, 0.10),
)
S1_LN_ROLE_DEFINITIONS = (
    "free: node-local residual capacity after incident edge roles",
    "conductive-bound: explicit edge role that can alter local coupling",
    "refractory: explicit edge role not immediately available for engagement",
)
S1_LN_EDGE_BALANCE_RULES = (
    "edge roles are stored as conductive-bound and refractory per canonical edge",
    "each endpoint gets half of incident conductive-bound and half of incident refractory",
    "free is derived per node as capacity minus half-share incident roles",
    "role accounting is per-edge and per-endpoint explicit",
)
S1_LN_GLOBAL_BALANCE_RULES = (
    "global capacity = sum(node capacities)",
    "global accounted = sum(derived free + all stored edge roles)",
    "global residual must be zero",
)
S1_LN_FORBIDDEN_STATES = (
    "empty-or-duplicate-node-inventory",
    "empty-duplicate-edge-inventory",
    "noncanonical-or-self-edge",
    "negative-or-nonfinite-node-capacity",
    "negative-or-nonfinite-edge-role",
    "incident-edge-allocation-exceeds-node-capacity",
    "stored-free-resource-duplicates-derived-ledger",
    "baseline-profiling-state-in-anatomy-identity",
    "nonfinite-local-or-global-balance",
)
S1_LN_STRUCTURAL_DISTINCTIONS = (
    ("fixed-adapter", "fixed coefficients only, no finite free/conductive/refractory partition"),
    ("gain", "response scaling only, not a local finite resource ledger"),
    ("fast-afterimage", "field residue only, no local three-role finite source"),
    ("integrator", "accumulates response, no derived free source"),
    ("replay", "stores/replays input while anatomy remains content-free"),
)
S1_LN_FORBIDDEN_CLAIMS = (
    "memory",
    "learning",
    "organism",
    "consciousness",
    "understanding",
    "awareness",
    "feeling",
)
S1_LN_DECISION = "C10_B3_P_IH_RESOURCE_ANATOMY_AND_CONSERVATION_BOUND_NO_DYNAMICS"


def _finite_nonnegative(value: object, role: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise DTS1S1LNResourceAnatomyContractError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1S1LNResourceAnatomyContractError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result) or result < 0.0 or (positive and result == 0.0):
        qualifier = "positive" if positive else "nonnegative"
        raise DTS1S1LNResourceAnatomyContractError(
            f"{role} must be finite and {qualifier}"
        )
    return result


def _derive_local_ledgers(
    node_capacities: tuple[tuple[str, float], ...],
    edge_roles: tuple[tuple[str, str, float, float], ...],
) -> tuple[tuple[str, float, float, float, float], ...]:
    nodes = tuple(
        (node, _finite_nonnegative(capacity, "node capacity", positive=True))
        for node, capacity in node_capacities
    )
    if not nodes:
        raise DTS1S1LNResourceAnatomyContractError("S1-LN requires non-empty nodes")
    node_ids = [node for node, _ in nodes]
    if len(set(node_ids)) != len(node_ids):
        raise DTS1S1LNResourceAnatomyContractError("nodes must be unique")

    edges = []
    for first, second, conductive_bound, refractory in edge_roles:
        if (
            not isinstance(first, str)
            or not isinstance(second, str)
            or not first
            or not second
            or first == second
        ):
            raise DTS1S1LNResourceAnatomyContractError(
                "edge endpoints must be non-empty and distinct"
            )
        if first > second:
            first, second = second, first
        edges.append(
            (
                first,
                second,
                _finite_nonnegative(conductive_bound, "conductive-bound"),
                _finite_nonnegative(refractory, "refractory"),
            )
        )
    if not edges:
        raise DTS1S1LNResourceAnatomyContractError("C10 requires at least one edge")
    ordered_edges = sorted(edges)
    if len(set((first, second) for first, second, *_ in ordered_edges)) != len(
        ordered_edges
    ):
        raise DTS1S1LNResourceAnatomyContractError("duplicate edges are not allowed")

    node_set = set(node_ids)
    for first, second, _, _ in ordered_edges:
        if first not in node_set or second not in node_set:
            raise DTS1S1LNResourceAnatomyContractError(
                "edge endpoint must be present in node inventory"
            )

    endpoint_conductive: dict[str, float] = {node: 0.0 for node in node_ids}
    endpoint_refractory: dict[str, float] = {node: 0.0 for node in node_ids}
    for first, second, conductive_bound, refractory in ordered_edges:
        for node in (first, second):
            endpoint_conductive[node] += 0.5 * conductive_bound
            endpoint_refractory[node] += 0.5 * refractory

    ledgers: list[tuple[str, float, float, float, float]] = []
    for node, capacity in nodes:
        conductive_half = endpoint_conductive[node]
        refractory_half = endpoint_refractory[node]
        free = capacity - (conductive_half + refractory_half)
        if free < -1e-15:
            raise DTS1S1LNResourceAnatomyContractError(
                f"incident allocation exceeds node capacity at {node}"
            )
        ledgers.append((node, capacity, free, conductive_half, refractory_half))

    return tuple(ledgers)


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


S1_LN_LOCAL_LEDGERS = _derive_local_ledgers(S1_LN_NODE_CAPACITIES, S1_LN_EDGE_ROLES)
S1_LN_GLOBAL_CAPACITY = math.fsum(item[1] for item in S1_LN_LOCAL_LEDGERS)
S1_LN_GLOBAL_ACCOUNTED = math.fsum(
    (
        *(item[2] for item in S1_LN_LOCAL_LEDGERS),
        *(conductive + refractory for _, _, conductive, refractory in S1_LN_EDGE_ROLES),
    )
)


def _almost_zero(value: float, *, tolerance: float = 1e-12) -> bool:
    return abs(value) <= tolerance


@dataclass(frozen=True, slots=True)
class DTS1S1LNResourceAnatomyContract:
    contract_id: str
    source_s1hi_contract_digest: str
    source_s1lm_contract_digest: str
    source_s1lm_decision: str
    candidate_id: str
    candidate_case: str
    candidate_baseline: str
    candidate_profile: str
    candidate_geometry: str
    reference_case_record: tuple[object, ...]
    reference_sequence: tuple[object, ...]
    reference_replica_ids: tuple[str, ...]
    source_s1lm_sequence_key: str
    node_capacity_records: tuple[tuple[str, float], ...]
    edge_resource_roles: tuple[tuple[str, str, float, float], ...]
    derived_local_ledgers: tuple[tuple[str, float, float, float, float], ...]
    role_definitions: tuple[str, ...]
    edge_balance_rules: tuple[str, ...]
    global_balance_rules: tuple[str, ...]
    structural_distinctions: tuple[tuple[str, str], ...]
    forbidden_states: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    local_identity_bound: bool
    global_identity_bound: bool
    free_resource_is_derived_not_stored: bool
    equation_selected: bool
    parameters_selected: bool
    runtime_implemented: bool
    field_coupling_selected: bool
    dynamic_functional_effect_selected: bool
    execution_permitted: bool
    claims_permitted: bool
    field_steps_executed: int
    candidate_count: int
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_LN_CONTRACT_ID
            or self.source_s1hi_contract_digest != S1_LN_SOURCE_S1HI_CONTRACT_DIGEST
            or self.source_s1lm_decision != S1_LM_DECISION
            or self.candidate_id != S1_HH_CANDIDATE_ID
            or self.candidate_case != S1_LN_CASE_ID
            or self.candidate_baseline != S1_LN_BASELINE
            or self.candidate_profile != S1_LN_PROFILE
            or self.candidate_geometry != S1_LN_GEOMETRY
            or self.reference_case_record != S1_LM_TARGET_CASE_RECORD
            or self.reference_sequence != S1_LM_SEQUENCE_RECORD
            or self.reference_replica_ids != S1_LM_TARGET_REPLICA_IDS
            or self.source_s1lm_sequence_key != S1_LM_SEQUENCE_KEY
            or self.node_capacity_records != S1_LN_NODE_CAPACITIES
            or self.edge_resource_roles != S1_LN_EDGE_ROLES
            or self.derived_local_ledgers != S1_LN_LOCAL_LEDGERS
            or self.role_definitions != S1_LN_ROLE_DEFINITIONS
            or self.edge_balance_rules != S1_LN_EDGE_BALANCE_RULES
            or self.global_balance_rules != S1_LN_GLOBAL_BALANCE_RULES
            or self.structural_distinctions != S1_LN_STRUCTURAL_DISTINCTIONS
            or self.forbidden_states != S1_LN_FORBIDDEN_STATES
            or self.forbidden_claims != S1_LN_FORBIDDEN_CLAIMS
            or self.candidate_count != 1
            or any(
                value is not True
                for value in (self.local_identity_bound, self.global_identity_bound, self.free_resource_is_derived_not_stored)
            )
            or any(
                value is not False
                for value in (
                    self.equation_selected,
                    self.parameters_selected,
                    self.runtime_implemented,
                    self.field_coupling_selected,
                    self.dynamic_functional_effect_selected,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_LN_DECISION
            or not _almost_zero(self.global_balance_gap())
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LNResourceAnatomyContractError(
                "S1-LN weakened the static C10 resource-anatomy boundary"
            )

    def global_balance_gap(self) -> float:
        # free residual + stored edge roles must equal global capacity
        return (
            sum(item[2] for item in self.derived_local_ledgers)
            + sum(item[2] + item[3] for item in self.edge_resource_roles)
            - self.node_capacity_sum()
        )

    def node_capacity_sum(self) -> float:
        return math.fsum(capacity for _, capacity in self.node_capacity_records)


def build_dts1_s1ln_b3_pih_resource_anatomy_contract() -> DTS1S1LNResourceAnatomyContract:
    """Bind C10 anatomy and conservation only; no dynamics and no execution."""

    s1lm = build_dts1_s1lm_b3_pih_case_selection_contract()
    s1hi = build_dts1_s1hi_anatomy_contract()
    values = {
        "contract_id": S1_LN_CONTRACT_ID,
        "source_s1hi_contract_digest": s1hi.contract_digest,
        "source_s1lm_contract_digest": s1lm.contract_digest,
        "source_s1lm_decision": s1lm.decision,
        "candidate_id": S1_HH_CANDIDATE_ID,
        "candidate_case": S1_LM_CASE_ID,
        "candidate_baseline": S1_LN_BASELINE,
        "candidate_profile": S1_LN_PROFILE,
        "candidate_geometry": S1_LN_GEOMETRY,
        "reference_case_record": S1_LM_TARGET_CASE_RECORD,
        "reference_sequence": S1_LM_SEQUENCE_RECORD,
        "reference_replica_ids": S1_LM_TARGET_REPLICA_IDS,
        "source_s1lm_sequence_key": S1_LM_SEQUENCE_KEY,
        "node_capacity_records": S1_LN_NODE_CAPACITIES,
        "edge_resource_roles": S1_LN_EDGE_ROLES,
        "derived_local_ledgers": S1_LN_LOCAL_LEDGERS,
        "role_definitions": S1_LN_ROLE_DEFINITIONS,
        "edge_balance_rules": S1_LN_EDGE_BALANCE_RULES,
        "global_balance_rules": S1_LN_GLOBAL_BALANCE_RULES,
        "structural_distinctions": S1_LN_STRUCTURAL_DISTINCTIONS,
        "forbidden_states": S1_LN_FORBIDDEN_STATES,
        "forbidden_claims": S1_LN_FORBIDDEN_CLAIMS,
        "local_identity_bound": True,
        "global_identity_bound": True,
        "free_resource_is_derived_not_stored": True,
        "equation_selected": False,
        "parameters_selected": False,
        "runtime_implemented": False,
        "field_coupling_selected": False,
        "dynamic_functional_effect_selected": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "field_steps_executed": 0,
        "candidate_count": 1,
        "decision": S1_LN_DECISION,
    }
    return DTS1S1LNResourceAnatomyContract(**values, contract_digest=_digest(values))

