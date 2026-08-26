"""Pure S1-NI T1/DTS-1 comparison over the bound seven-event sequence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .dynamic_substrate_dts1_step import (
    DTS1EdgeParticipation,
    DTS1StepRates,
    compute_dts1_closed_prestate_step,
)
from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from .kfs1_t1_transition import KFS1T1Ledger, advance_kfs1_t1_edge


S1_NI_EVENTS = (
    ("K1_CONTACT", -1.0, 1.0, 1.0),
    ("K2_REPEAT", -1.0, 1.0, 1.0),
    ("N1_ENTRY", 0.0, 0.0, 0.0),
    ("K3_BLOCKED_CONTACT", -1.0, 1.0, 1.0),
    ("N2_RELEASE", 0.0, 0.0, 0.0),
    ("N3_FREE_HOLD", 0.0, 0.0, 0.0),
    ("K4_REBIND", -1.0, 1.0, 1.0),
)
S1_NI_T1_EXPECTED = (
    ((0.0, 1.0, 0.0), (1.0, 0.0, 0.0)),
    ((0.0, 1.0, 0.0), (0.0, 0.0, 0.0)),
    ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0)),
    ((0.0, 0.0, 1.0), (0.0, 0.0, 0.0)),
    ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    ((0.0, 1.0, 0.0), (1.0, 0.0, 0.0)),
)
S1_NI_DTS1_PROFILES = (
    ("DTS1_REGISTERED", DTS1StepRates(0.4, 0.3, 0.2), (1, 2, 4, 8)),
    ("DTS1_STATIC_ZERO", DTS1StepRates(0.0, 0.0, 0.0), (1,)),
)
S1_NI_LEDGER_TOLERANCE = 1.1368683772161603e-13
S1_NI_DECISION_SWITCHED = "T1_DTS1_SWITCHED_VARIANT_ONLY"
S1_NI_DECISION_REPRODUCED = "T1_REPRODUCED_BY_REGISTERED_DTS1"
S1_NI_DECISION_DISTINCT = "T1_LOCAL_LEDGER_DISTINCT_FIELD_EFFECT_OPEN"


class KFS1S1NIComparisonError(ValueError):
    """Raised without a partial result when the closed comparison is invalid."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_tuple(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in result):
        raise KFS1S1NIComparisonError(f"{role} must remain finite")
    return result


@dataclass(frozen=True, slots=True)
class KFS1S1NIBoundary:
    event_index: int
    event_id: str
    participation: float
    ledger: tuple[float, float, float]
    transfers: tuple[float, float, float]
    maximum_local_ledger_residual: float
    global_ledger_residual: float
    state_digest: str

    def __post_init__(self) -> None:
        if self.event_index < 1 or self.event_index > len(S1_NI_EVENTS):
            raise KFS1S1NIComparisonError("event_index is outside the bound sequence")
        if self.event_id != S1_NI_EVENTS[self.event_index - 1][0]:
            raise KFS1S1NIComparisonError("event identity is outside the bound sequence")
        expected_p = S1_NI_EVENTS[self.event_index - 1][3]
        if self.participation != expected_p:
            raise KFS1S1NIComparisonError("boundary participation changed")
        ledger = _finite_tuple(tuple(self.ledger), "ledger")
        transfers = _finite_tuple(tuple(self.transfers), "transfers")
        if len(ledger) != 3 or len(transfers) != 3:
            raise KFS1S1NIComparisonError("boundary requires two complete triples")
        if any(value < 0.0 for value in ledger + transfers):
            raise KFS1S1NIComparisonError("boundary values must be nonnegative")
        if abs(math.fsum(ledger) - 1.0) > S1_NI_LEDGER_TOLERANCE:
            raise KFS1S1NIComparisonError("boundary ledger does not conserve resource")
        for role in ("maximum_local_ledger_residual", "global_ledger_residual"):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise KFS1S1NIComparisonError(f"{role} must be finite and nonnegative")
            object.__setattr__(self, role, value)
        if self.state_digest != _digest({"ledger": ledger}):
            raise KFS1S1NIComparisonError("state digest does not identify the ledger")
        object.__setattr__(self, "ledger", ledger)
        object.__setattr__(self, "transfers", transfers)


@dataclass(frozen=True, slots=True)
class KFS1S1NIArm:
    arm_id: str
    refinement: int
    boundaries: tuple[KFS1S1NIBoundary, ...]

    def __post_init__(self) -> None:
        boundaries = tuple(self.boundaries)
        if not self.arm_id or self.refinement not in (1, 2, 4, 8):
            raise KFS1S1NIComparisonError("invalid comparison arm")
        if tuple(item.event_index for item in boundaries) != tuple(range(1, 8)):
            raise KFS1S1NIComparisonError("arm must contain all seven boundaries")
        object.__setattr__(self, "boundaries", boundaries)


@dataclass(frozen=True, slots=True)
class KFS1S1NIComparisonResult:
    t1_arm: KFS1S1NIArm
    dts1_arms: tuple[KFS1S1NIArm, ...]
    equivalent_arm_ids: tuple[str, ...]
    switched_dts1_variant_exact: bool
    t1_transition_calls: int
    dts1_substep_calls: int
    field_steps_executed: int
    decision: str
    result_digest: str

    def __post_init__(self) -> None:
        arms = tuple(self.dts1_arms)
        expected_ids = (
            "DTS1_REGISTERED:r1",
            "DTS1_REGISTERED:r2",
            "DTS1_REGISTERED:r4",
            "DTS1_REGISTERED:r8",
            "DTS1_STATIC_ZERO:r1",
        )
        if self.t1_arm.arm_id != "KFS1_T1" or self.t1_arm.refinement != 1:
            raise KFS1S1NIComparisonError("result requires the bound T1 arm")
        if tuple(arm.arm_id for arm in arms) != expected_ids:
            raise KFS1S1NIComparisonError("result DTS-1 arm set changed")
        if self.t1_transition_calls != 7 or self.dts1_substep_calls != 112:
            raise KFS1S1NIComparisonError("result call budget changed")
        if self.field_steps_executed != 0:
            raise KFS1S1NIComparisonError("field execution is forbidden")
        expected_decision = (
            S1_NI_DECISION_REPRODUCED
            if self.equivalent_arm_ids
            else S1_NI_DECISION_SWITCHED
            if self.switched_dts1_variant_exact
            else S1_NI_DECISION_DISTINCT
        )
        if self.decision != expected_decision:
            raise KFS1S1NIComparisonError("decision does not follow the contract")
        payload = {
            "t1": _arm_payload(self.t1_arm),
            "dts1": tuple(_arm_payload(arm) for arm in arms),
            "equivalent_arm_ids": tuple(self.equivalent_arm_ids),
            "switched_dts1_variant_exact": self.switched_dts1_variant_exact,
            "t1_transition_calls": self.t1_transition_calls,
            "dts1_substep_calls": self.dts1_substep_calls,
            "field_steps_executed": self.field_steps_executed,
            "decision": self.decision,
        }
        if self.result_digest != _digest(payload):
            raise KFS1S1NIComparisonError("result digest mismatch")
        object.__setattr__(self, "dts1_arms", arms)
        object.__setattr__(self, "equivalent_arm_ids", tuple(self.equivalent_arm_ids))


def _boundary_payload(boundary: KFS1S1NIBoundary) -> dict[str, object]:
    return {
        "event_index": boundary.event_index,
        "event_id": boundary.event_id,
        "participation": boundary.participation,
        "ledger": boundary.ledger,
        "transfers": boundary.transfers,
        "maximum_local_ledger_residual": boundary.maximum_local_ledger_residual,
        "global_ledger_residual": boundary.global_ledger_residual,
        "state_digest": boundary.state_digest,
    }


def _arm_payload(arm: KFS1S1NIArm) -> dict[str, object]:
    return {
        "arm_id": arm.arm_id,
        "refinement": arm.refinement,
        "boundaries": tuple(_boundary_payload(item) for item in arm.boundaries),
    }


def _boundary(
    index: int,
    ledger: tuple[float, float, float],
    transfers: tuple[float, float, float],
    local_residual: float = 0.0,
    global_residual: float = 0.0,
) -> KFS1S1NIBoundary:
    event_id, _first, _second, participation = S1_NI_EVENTS[index - 1]
    ledger = tuple(ledger)
    return KFS1S1NIBoundary(
        event_index=index,
        event_id=event_id,
        participation=participation,
        ledger=ledger,
        transfers=tuple(transfers),
        maximum_local_ledger_residual=local_residual,
        global_ledger_residual=global_residual,
        state_digest=_digest({"ledger": ledger}),
    )


def _run_t1() -> KFS1S1NIArm:
    ledger = KFS1T1Ledger("edge:a:b", 1.0, 1.0, 0.0, 0.0)
    boundaries = []
    for index, (_event_id, first, second, _participation) in enumerate(
        S1_NI_EVENTS, start=1
    ):
        result = advance_kfs1_t1_edge(ledger, first, second)
        values = (
            result.post_ledger.free,
            result.post_ledger.bound,
            result.post_ledger.blocked,
        )
        transfers = (
            result.transfers.bind,
            result.transfers.block,
            result.transfers.release,
        )
        if (values, transfers) != S1_NI_T1_EXPECTED[index - 1]:
            raise KFS1S1NIComparisonError("T1_LEDGER_INVALID")
        boundaries.append(_boundary(index, values, transfers))
        ledger = result.post_ledger
    return KFS1S1NIArm("KFS1_T1", 1, tuple(boundaries))


def _initial_dts1() -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        node_capacities=(DTS1NodeCapacity("a", 0.5), DTS1NodeCapacity("b", 0.5)),
        edge_resources=(DTS1EdgeResource("a", "b", 0.0, 0.0),),
    )


def _run_dts1_arm(
    profile_id: str,
    rates: DTS1StepRates,
    refinement: int,
) -> KFS1S1NIArm:
    anatomy = _initial_dts1()
    boundaries = []
    for index, (_event_id, _first, _second, participation) in enumerate(
        S1_NI_EVENTS, start=1
    ):
        transfer_terms = [[], [], []]
        maximum_local_residual = 0.0
        maximum_global_residual = 0.0
        for _ in range(refinement):
            result = compute_dts1_closed_prestate_step(
                anatomy,
                (DTS1EdgeParticipation("a", "b", participation),),
                1.0 / refinement,
                rates,
            )
            transfer = result.edge_transfers[0]
            transfer_terms[0].append(transfer.engagement)
            transfer_terms[1].append(transfer.turnover)
            transfer_terms[2].append(transfer.recovery)
            maximum_local_residual = max(
                maximum_local_residual, result.maximum_local_ledger_residual
            )
            maximum_global_residual = max(
                maximum_global_residual, result.global_ledger_residual
            )
            anatomy = result.next_anatomy
        edge = anatomy.edge_resources[0]
        free_total = math.fsum(item.free for item in anatomy.local_ledgers())
        boundaries.append(
            _boundary(
                index,
                (free_total, edge.conductive_bound, edge.refractory),
                tuple(math.fsum(items) for items in transfer_terms),
                maximum_local_residual,
                maximum_global_residual,
            )
        )
    return KFS1S1NIArm(
        f"{profile_id}:r{refinement}", refinement, tuple(boundaries)
    )


def _component_equivalent(observed: float, expected: float) -> bool:
    if expected == 0.0:
        return observed == 0.0
    return abs(observed - expected) <= S1_NI_LEDGER_TOLERANCE


def _arms_equivalent(t1: KFS1S1NIArm, dts1: KFS1S1NIArm) -> bool:
    for expected, observed in zip(t1.boundaries, dts1.boundaries, strict=True):
        for observed_value, expected_value in zip(
            observed.ledger + observed.transfers,
            expected.ledger + expected.transfers,
            strict=True,
        ):
            if not _component_equivalent(observed_value, expected_value):
                return False
    return True


def _switched_dts1_reproduces_t1(t1: KFS1S1NIArm) -> bool:
    pre = (1.0, 0.0, 0.0)
    for event, boundary in zip(S1_NI_EVENTS, t1.boundaries, strict=True):
        participation = event[3]
        free, bound, blocked = pre
        if participation == 1.0:
            transfers = (free, 0.0, 0.0)
        elif participation == 0.0:
            transfers = (0.0, bound, blocked)
        else:
            return False
        engage, turnover, recovery = transfers
        post = (
            free - engage + recovery,
            bound + engage - turnover,
            blocked + turnover - recovery,
        )
        if post != boundary.ledger or transfers != boundary.transfers:
            return False
        pre = post
    return True


def run_kfs1_s1ni_sequence_comparison() -> KFS1S1NIComparisonResult:
    """Execute the closed local matrix once; no field or runtime is touched."""

    t1_arm = _run_t1()
    dts1_arms = tuple(
        _run_dts1_arm(profile_id, rates, refinement)
        for profile_id, rates, refinements in S1_NI_DTS1_PROFILES
        for refinement in refinements
    )
    equivalent = tuple(
        arm.arm_id for arm in dts1_arms if _arms_equivalent(t1_arm, arm)
    )
    switched = _switched_dts1_reproduces_t1(t1_arm)
    decision = (
        S1_NI_DECISION_REPRODUCED
        if equivalent
        else S1_NI_DECISION_SWITCHED
        if switched
        else S1_NI_DECISION_DISTINCT
    )
    payload = {
        "t1": _arm_payload(t1_arm),
        "dts1": tuple(_arm_payload(arm) for arm in dts1_arms),
        "equivalent_arm_ids": equivalent,
        "switched_dts1_variant_exact": switched,
        "t1_transition_calls": 7,
        "dts1_substep_calls": 112,
        "field_steps_executed": 0,
        "decision": decision,
    }
    return KFS1S1NIComparisonResult(
        t1_arm=t1_arm,
        dts1_arms=dts1_arms,
        equivalent_arm_ids=equivalent,
        switched_dts1_variant_exact=switched,
        t1_transition_calls=7,
        dts1_substep_calls=112,
        field_steps_executed=0,
        decision=decision,
        result_digest=_digest(payload),
    )
