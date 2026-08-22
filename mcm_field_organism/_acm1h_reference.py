"""Private pure ACM-1H reference kernel for the four-node corridor."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Iterable

from .field_step_time import MCMFieldStepTime


ACM1H_SCHEMA_ID = "acm1h-reference-v1"
ACM1H_NODE_IDS = ("node-a", "node-b", "node-c", "node-d")
ACM1H_EDGES = (
    ("node-a", "node-b"),
    ("node-b", "node-c"),
    ("node-c", "node-d"),
)
ACM1H_MOTIFS = (
    ("m-left", (0, 1)),
    ("m-right", (1, 2)),
)
ACM1H_PARAMETER_CANDIDATES = tuple(
    (gamma_z, beta)
    for gamma_z in (0.25, 0.5, 1.0)
    for beta in (0.25, 0.5)
)

ACM1H_INVALID_CONFIG = "ACM1H_INVALID_CONFIG"
ACM1H_INVALID_FIELD_PRESTATE = "ACM1H_INVALID_FIELD_PRESTATE"
ACM1H_INVALID_STEP_TIME = "ACM1H_INVALID_STEP_TIME"
ACM1H_STEP_TIME_MISMATCH = "ACM1H_STEP_TIME_MISMATCH"
ACM1H_UNSUPPORTED_GEOMETRY = "ACM1H_UNSUPPORTED_GEOMETRY"
ACM1H_EDGE_INVENTORY_MISMATCH = "ACM1H_EDGE_INVENTORY_MISMATCH"
ACM1H_INVALID_Z_STATE = "ACM1H_INVALID_Z_STATE"
ACM1H_NONFINITE_PROPOSAL = "ACM1H_NONFINITE_PROPOSAL"
ACM1H_NEGATIVE_EDGE_RATE = "ACM1H_NEGATIVE_EDGE_RATE"
ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH = (
    "ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH"
)
ACM1H_ITERATION_ORDER_DEPENDENCE = "ACM1H_ITERATION_ORDER_DEPENDENCE"
ACM1H_ATOMIC_RESULT_REQUIRED = "ACM1H_ATOMIC_RESULT_REQUIRED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


class ACM1HReferenceError(ValueError):
    """One fail-closed ACM-1H contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _finite(value: object, role: str, code: str) -> float:
    if isinstance(value, bool):
        raise ACM1HReferenceError(code, f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ACM1HReferenceError(code, f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise ACM1HReferenceError(code, f"{role} must be finite")
    return result


def _identifier(value: object, role: str, code: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ACM1HReferenceError(code, f"{role} must be a technical identifier")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def acm1h_edge_inventory_digest() -> str:
    return _digest([list(edge) for edge in ACM1H_EDGES])


@dataclass(frozen=True, slots=True)
class ACM1HConfigRecord:
    gamma_z: float
    beta: float
    schema_id: str = ACM1H_SCHEMA_ID

    def __post_init__(self) -> None:
        if self.schema_id != ACM1H_SCHEMA_ID:
            raise ACM1HReferenceError(
                ACM1H_INVALID_CONFIG, "schema_id does not match ACM-1H v1"
            )
        gamma_z = _finite(self.gamma_z, "gamma_z", ACM1H_INVALID_CONFIG)
        beta = _finite(self.beta, "beta", ACM1H_INVALID_CONFIG)
        if gamma_z <= 0.0 or beta <= 0.0 or beta > 1.0:
            raise ACM1HReferenceError(
                ACM1H_INVALID_CONFIG,
                "gamma_z must be positive and beta must be in (0,1]",
            )
        object.__setattr__(self, "gamma_z", gamma_z)
        object.__setattr__(self, "beta", beta)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "gamma_z": self.gamma_z,
            "beta": self.beta,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ACM1HPrestateRecord:
    field_id: str
    geometry_id: str
    node_ids: tuple[str, ...]
    activations: tuple[float, ...]
    edge_rates_per_second: tuple[float, ...]
    motif_states: tuple[float, ...]
    edge_inventory_digest: str
    clock_id: str
    interval_start_tick: int
    interval_end_tick: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "field_id",
            _identifier(
                self.field_id, "field_id", ACM1H_INVALID_FIELD_PRESTATE
            ),
        )
        object.__setattr__(
            self,
            "geometry_id",
            _identifier(
                self.geometry_id, "geometry_id", ACM1H_INVALID_FIELD_PRESTATE
            ),
        )
        node_ids = tuple(self.node_ids)
        if node_ids != ACM1H_NODE_IDS:
            raise ACM1HReferenceError(
                ACM1H_UNSUPPORTED_GEOMETRY,
                "the first corridor requires node-a through node-d",
            )
        activations = tuple(
            _finite(value, "activation", ACM1H_INVALID_FIELD_PRESTATE)
            for value in self.activations
        )
        if len(activations) != 4 or any(abs(value) > 1.0 for value in activations):
            raise ACM1HReferenceError(
                ACM1H_INVALID_FIELD_PRESTATE,
                "four activations must stay in [-1,1]",
            )
        rates = tuple(
            _finite(value, "edge_rate", ACM1H_NEGATIVE_EDGE_RATE)
            for value in self.edge_rates_per_second
        )
        if len(rates) != 3 or any(value < 0.0 for value in rates):
            raise ACM1HReferenceError(
                ACM1H_NEGATIVE_EDGE_RATE,
                "three finite nonnegative edge rates are required",
            )
        states = tuple(
            _finite(value, "motif_state", ACM1H_INVALID_Z_STATE)
            for value in self.motif_states
        )
        if len(states) != 2 or any(abs(value) > 1.0 for value in states):
            raise ACM1HReferenceError(
                ACM1H_INVALID_Z_STATE,
                "two motif states must stay in [-1,1]",
            )
        if self.edge_inventory_digest != acm1h_edge_inventory_digest():
            raise ACM1HReferenceError(
                ACM1H_EDGE_INVENTORY_MISMATCH,
                "edge inventory digest differs from the four-node corridor",
            )
        clock_id = _identifier(
            self.clock_id, "clock_id", ACM1H_INVALID_FIELD_PRESTATE
        )
        if (
            isinstance(self.interval_start_tick, bool)
            or isinstance(self.interval_end_tick, bool)
            or not isinstance(self.interval_start_tick, int)
            or not isinstance(self.interval_end_tick, int)
            or self.interval_start_tick < 0
            or self.interval_end_tick <= self.interval_start_tick
        ):
            raise ACM1HReferenceError(
                ACM1H_INVALID_FIELD_PRESTATE,
                "prestate interval ticks must be positive and ordered",
            )
        object.__setattr__(self, "node_ids", node_ids)
        object.__setattr__(self, "activations", activations)
        object.__setattr__(self, "edge_rates_per_second", rates)
        object.__setattr__(self, "motif_states", states)
        object.__setattr__(self, "clock_id", clock_id)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "field_id": self.field_id,
            "geometry_id": self.geometry_id,
            "node_ids": list(self.node_ids),
            "activations": list(self.activations),
            "edge_rates_per_second": list(self.edge_rates_per_second),
            "motif_states": list(self.motif_states),
            "edge_inventory_digest": self.edge_inventory_digest,
            "clock_id": self.clock_id,
            "interval_start_tick": self.interval_start_tick,
            "interval_end_tick": self.interval_end_tick,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ACM1HEdgeFluxRecord:
    edges: tuple[tuple[str, str], ...]
    rates_per_second: tuple[float, ...]
    primary_flows_per_second: tuple[float, ...]
    prestate_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "edges": [list(edge) for edge in self.edges],
            "rates_per_second": list(self.rates_per_second),
            "primary_flows_per_second": list(self.primary_flows_per_second),
            "prestate_digest": self.prestate_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ACM1HMotifProposalRecord:
    motif_id: str
    edge_indices: tuple[int, int]
    joint_participation_per_second: float
    parity: int
    theta: float
    z_pre: float
    z_next: float
    factor: float
    prestate_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "motif_id": self.motif_id,
            "edge_indices": list(self.edge_indices),
            "joint_participation_per_second": self.joint_participation_per_second,
            "parity": self.parity,
            "theta": self.theta,
            "z_pre": self.z_pre,
            "z_next": self.z_next,
            "factor": self.factor,
            "prestate_digest": self.prestate_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ACM1HCompositionRecord:
    edge_factors: tuple[float, ...]
    composed_rates_per_second: tuple[float, ...]
    composed_flows_per_second: tuple[float, ...]
    shared_edge_factors: tuple[tuple[str, float], ...]
    generator: tuple[tuple[float, ...], ...]
    prestate_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "edge_factors": list(self.edge_factors),
            "composed_rates_per_second": list(self.composed_rates_per_second),
            "composed_flows_per_second": list(self.composed_flows_per_second),
            "shared_edge_factors": [list(item) for item in self.shared_edge_factors],
            "generator": [list(row) for row in self.generator],
            "prestate_digest": self.prestate_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ACM1HDecisionRecord:
    status: str
    error_code: str | None
    config_digest: str | None
    prestate_digest: str | None
    edge_fluxes: ACM1HEdgeFluxRecord | None
    motif_proposals: tuple[ACM1HMotifProposalRecord, ...]
    composition: ACM1HCompositionRecord | None

    def __post_init__(self) -> None:
        success = self.status == "COMPLETED"
        failure = self.status == "FAILED"
        if not (success or failure):
            raise ACM1HReferenceError(
                ACM1H_ATOMIC_RESULT_REQUIRED, "decision status is invalid"
            )
        complete = (
            self.error_code is None
            and self.config_digest is not None
            and self.prestate_digest is not None
            and self.edge_fluxes is not None
            and len(self.motif_proposals) == 2
            and self.composition is not None
        )
        empty_failure = (
            self.error_code is not None
            and self.config_digest is None
            and self.prestate_digest is None
            and self.edge_fluxes is None
            and not self.motif_proposals
            and self.composition is None
        )
        if (success and not complete) or (failure and not empty_failure):
            raise ACM1HReferenceError(
                ACM1H_ATOMIC_RESULT_REQUIRED,
                "decision must contain either one complete result or one error",
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "error_code": self.error_code,
            "config_digest": self.config_digest,
            "prestate_digest": self.prestate_digest,
            "edge_fluxes": (
                None if self.edge_fluxes is None else self.edge_fluxes.canonical_payload()
            ),
            "motif_proposals": [
                item.canonical_payload() for item in self.motif_proposals
            ],
            "composition": (
                None if self.composition is None else self.composition.canonical_payload()
            ),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _failed(code: str) -> ACM1HDecisionRecord:
    return ACM1HDecisionRecord("FAILED", code, None, None, None, (), None)


def _validate_step_time(
    prestate: ACM1HPrestateRecord, step_time: object
) -> MCMFieldStepTime:
    if not isinstance(step_time, MCMFieldStepTime):
        raise ACM1HReferenceError(
            ACM1H_INVALID_STEP_TIME, "one explicit MCMFieldStepTime is required"
        )
    if (
        step_time.clock_id != prestate.clock_id
        or step_time.start_tick != prestate.interval_start_tick
        or step_time.end_tick != prestate.interval_end_tick
    ):
        raise ACM1HReferenceError(
            ACM1H_STEP_TIME_MISMATCH,
            "step time differs from the prestate interval",
        )
    return step_time


def _edge_flux_record(prestate: ACM1HPrestateRecord) -> ACM1HEdgeFluxRecord:
    values = dict(zip(prestate.node_ids, prestate.activations, strict=True))
    flows = tuple(
        rate * (values[first] - values[second])
        for (first, second), rate in zip(
            ACM1H_EDGES, prestate.edge_rates_per_second, strict=True
        )
    )
    if any(not math.isfinite(value) for value in flows):
        raise ACM1HReferenceError(
            ACM1H_NONFINITE_PROPOSAL, "primary edge flow is non-finite"
        )
    return ACM1HEdgeFluxRecord(
        ACM1H_EDGES,
        prestate.edge_rates_per_second,
        flows,
        prestate.digest(),
    )


def _motif_proposal(
    motif_id: str,
    edge_indices: tuple[int, int],
    flows: tuple[float, ...],
    z_pre: float,
    elapsed_seconds: float,
    config: ACM1HConfigRecord,
    prestate_digest: str,
    *,
    write_enabled: bool,
    readout_enabled: bool,
) -> ACM1HMotifProposalRecord:
    first_flow, second_flow = (flows[index] for index in edge_indices)
    participation = min(abs(first_flow), abs(second_flow))
    if participation == 0.0:
        parity = 0
        theta = 0.0
        z_next = z_pre
        factor = 1.0
    else:
        parity = 1 if first_flow * second_flow > 0.0 else -1
        theta = 1.0 - math.exp(
            -config.gamma_z * participation * elapsed_seconds
        )
        z_next = (
            (1.0 - theta) * z_pre + theta * parity
            if write_enabled
            else z_pre
        )
        factor = (
            1.0 + config.beta * parity * z_pre
            if readout_enabled
            else 1.0
        )
    values = (participation, theta, z_next, factor)
    if any(not math.isfinite(value) for value in values):
        raise ACM1HReferenceError(
            ACM1H_NONFINITE_PROPOSAL, "motif proposal is non-finite"
        )
    if not (-1.0 <= z_next <= 1.0) or not (0.0 <= factor <= 2.0):
        raise ACM1HReferenceError(
            ACM1H_NONFINITE_PROPOSAL, "motif proposal left its invariant domain"
        )
    return ACM1HMotifProposalRecord(
        motif_id,
        edge_indices,
        participation,
        parity,
        theta,
        z_pre,
        z_next,
        factor,
        prestate_digest,
    )


def compose_acm1h_proposals(
    prestate: ACM1HPrestateRecord,
    edge_fluxes: ACM1HEdgeFluxRecord,
    proposals: Iterable[ACM1HMotifProposalRecord],
) -> ACM1HCompositionRecord:
    proposal_items = tuple(proposals)
    expected = dict(ACM1H_MOTIFS)
    if (
        len(proposal_items) != 2
        or {item.motif_id for item in proposal_items} != set(expected)
        or any(
            item.edge_indices != expected.get(item.motif_id)
            for item in proposal_items
        )
        or any(item.prestate_digest != prestate.digest() for item in proposal_items)
    ):
        raise ACM1HReferenceError(
            ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH,
            "composition requires both provenance-separated motif proposals",
        )
    factors = [1.0, 1.0, 1.0]
    shared = []
    for proposal in proposal_items:
        for edge_index in proposal.edge_indices:
            factors[edge_index] *= proposal.factor
        if 1 in proposal.edge_indices:
            shared.append((proposal.motif_id, proposal.factor))
    shared.sort(key=lambda item: item[0])
    reverse_shared_product = 1.0
    for _, factor in reversed(shared):
        reverse_shared_product *= factor
    if reverse_shared_product != factors[1]:
        raise ACM1HReferenceError(
            ACM1H_ITERATION_ORDER_DEPENDENCE,
            "shared edge factor depends on motif iteration order",
        )
    rates = tuple(
        factor * rate
        for factor, rate in zip(
            factors, edge_fluxes.rates_per_second, strict=True
        )
    )
    flows = tuple(
        factor * flow
        for factor, flow in zip(
            factors, edge_fluxes.primary_flows_per_second, strict=True
        )
    )
    if any(not math.isfinite(value) or value < 0.0 for value in rates):
        raise ACM1HReferenceError(
            ACM1H_NEGATIVE_EDGE_RATE, "composed edge rate is invalid"
        )
    generator = [[0.0] * 4 for _ in range(4)]
    for edge_index, rate in enumerate(rates):
        first = edge_index
        second = edge_index + 1
        generator[first][second] += rate
        generator[second][first] += rate
        generator[first][first] -= rate
        generator[second][second] -= rate
    result = ACM1HCompositionRecord(
        tuple(factors),
        rates,
        flows,
        tuple(shared),
        tuple(tuple(row) for row in generator),
        prestate.digest(),
    )
    return result


def run_acm1h_reference(
    config: object,
    prestate: object,
    step_time: object,
) -> ACM1HDecisionRecord:
    """Return one complete pure result or one fail-closed error record."""

    return _run_acm1h_reference(
        config,
        prestate,
        step_time,
        write_enabled=True,
        readout_enabled=True,
    )


def run_acm1h_readout_ablation(
    config: object,
    prestate: object,
    step_time: object,
) -> ACM1HDecisionRecord:
    """Advance z while keeping every ACM edge factor exactly neutral."""

    return _run_acm1h_reference(
        config,
        prestate,
        step_time,
        write_enabled=True,
        readout_enabled=False,
    )


def run_acm1h_write_ablation(
    config: object,
    prestate: object,
    step_time: object,
) -> ACM1HDecisionRecord:
    """Read the bound z prestate while holding it exactly unchanged."""

    return _run_acm1h_reference(
        config,
        prestate,
        step_time,
        write_enabled=False,
        readout_enabled=True,
    )


def _run_acm1h_reference(
    config: object,
    prestate: object,
    step_time: object,
    *,
    write_enabled: bool,
    readout_enabled: bool,
) -> ACM1HDecisionRecord:

    try:
        if not isinstance(config, ACM1HConfigRecord):
            raise ACM1HReferenceError(
                ACM1H_INVALID_CONFIG, "validated ACM1HConfigRecord required"
            )
        if not isinstance(prestate, ACM1HPrestateRecord):
            raise ACM1HReferenceError(
                ACM1H_INVALID_FIELD_PRESTATE,
                "validated ACM1HPrestateRecord required",
            )
        validated_time = _validate_step_time(prestate, step_time)
        edge_fluxes = _edge_flux_record(prestate)
        proposals = tuple(
            _motif_proposal(
                motif_id,
                edge_indices,
                edge_fluxes.primary_flows_per_second,
                prestate.motif_states[index],
                validated_time.elapsed_seconds,
                config,
                prestate.digest(),
                write_enabled=write_enabled,
                readout_enabled=readout_enabled,
            )
            for index, (motif_id, edge_indices) in enumerate(ACM1H_MOTIFS)
        )
        composition = compose_acm1h_proposals(
            prestate, edge_fluxes, proposals
        )
        return ACM1HDecisionRecord(
            "COMPLETED",
            None,
            config.digest(),
            prestate.digest(),
            edge_fluxes,
            proposals,
            composition,
        )
    except ACM1HReferenceError as exc:
        return _failed(exc.code)


def build_acm1h_off_generator(
    prestate: object, step_time: object
) -> tuple[tuple[float, ...], ...]:
    """Return only the unchanged primary generator without ACM state output."""

    if not isinstance(prestate, ACM1HPrestateRecord):
        raise ACM1HReferenceError(
            ACM1H_INVALID_FIELD_PRESTATE,
            "validated ACM1HPrestateRecord required",
        )
    _validate_step_time(prestate, step_time)
    generator = [[0.0] * 4 for _ in range(4)]
    for edge_index, rate in enumerate(prestate.edge_rates_per_second):
        first = edge_index
        second = edge_index + 1
        generator[first][second] += rate
        generator[second][first] += rate
        generator[first][first] -= rate
        generator[second][second] -= rate
    return tuple(tuple(row) for row in generator)


def advance_iag2_gain(
    gain: object,
    primary_flow_per_second: object,
    elapsed_seconds: object,
    gamma_g: object,
) -> float:
    """Advance the registered independent sign-blind IAG-2 gain."""

    current = _finite(gain, "gain", ACM1H_INVALID_FIELD_PRESTATE)
    flow = _finite(
        primary_flow_per_second,
        "primary_flow_per_second",
        ACM1H_INVALID_FIELD_PRESTATE,
    )
    elapsed = _finite(
        elapsed_seconds, "elapsed_seconds", ACM1H_INVALID_STEP_TIME
    )
    gamma = _finite(gamma_g, "gamma_g", ACM1H_INVALID_CONFIG)
    if not 0.0 <= current <= 1.0 or elapsed < 0.0 or gamma <= 0.0:
        raise ACM1HReferenceError(
            ACM1H_INVALID_CONFIG, "IAG-2 values leave their bound domain"
        )
    theta = 1.0 - math.exp(-gamma * abs(flow) * elapsed)
    result = (1.0 - theta) * current + theta
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ACM1HReferenceError(
            ACM1H_NONFINITE_PROPOSAL, "IAG-2 proposal is invalid"
        )
    return result
