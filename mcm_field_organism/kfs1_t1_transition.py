"""Pure parameter-free KFS-1/T1 transition for one local edge ledger."""

from __future__ import annotations

from dataclasses import dataclass
import math


__all__ = (
    "KFS1T1TransitionError",
    "KFS1T1Ledger",
    "KFS1T1Transfers",
    "KFS1T1TransitionResult",
    "compute_kfs1_t1_edge_participation",
    "advance_kfs1_t1_edge",
)


class KFS1T1TransitionError(ValueError):
    """Raised before output when the closed local T1 prestate is invalid."""


def _finite(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise KFS1T1TransitionError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise KFS1T1TransitionError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise KFS1T1TransitionError(f"{role} must be finite")
    return 0.0 if result == 0.0 else result


def _nonnegative(value: object, role: str) -> float:
    result = _finite(value, role)
    if result < 0.0:
        raise KFS1T1TransitionError(f"{role} must be nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class KFS1T1Ledger:
    edge_id: str
    capacity: float
    free: float
    bound: float
    blocked: float

    def __post_init__(self) -> None:
        if not isinstance(self.edge_id, str) or not self.edge_id:
            raise KFS1T1TransitionError("edge_id must be a nonempty string")
        capacity = _nonnegative(self.capacity, "capacity")
        if capacity <= 0.0:
            raise KFS1T1TransitionError("capacity must be positive")
        free = _nonnegative(self.free, "free")
        bound = _nonnegative(self.bound, "bound")
        blocked = _nonnegative(self.blocked, "blocked")
        if math.fsum((free, bound, blocked)) != capacity:
            raise KFS1T1TransitionError(
                "free, bound, and blocked must exactly conserve capacity"
            )
        object.__setattr__(self, "capacity", capacity)
        object.__setattr__(self, "free", free)
        object.__setattr__(self, "bound", bound)
        object.__setattr__(self, "blocked", blocked)


@dataclass(frozen=True, slots=True)
class KFS1T1Transfers:
    bind: float
    block: float
    release: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "bind", _nonnegative(self.bind, "bind"))
        object.__setattr__(self, "block", _nonnegative(self.block, "block"))
        object.__setattr__(self, "release", _nonnegative(self.release, "release"))


@dataclass(frozen=True, slots=True)
class KFS1T1TransitionResult:
    participation: float
    target_bound: float
    pre_ledger: KFS1T1Ledger
    post_ledger: KFS1T1Ledger
    transfers: KFS1T1Transfers
    transition_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        participation = _nonnegative(self.participation, "participation")
        if participation > 1.0:
            raise KFS1T1TransitionError("participation must not exceed one")
        target = _nonnegative(self.target_bound, "target_bound")
        if not isinstance(self.pre_ledger, KFS1T1Ledger) or not isinstance(
            self.post_ledger, KFS1T1Ledger
        ):
            raise KFS1T1TransitionError("result requires complete pre/post ledgers")
        if self.pre_ledger.edge_id != self.post_ledger.edge_id:
            raise KFS1T1TransitionError("result ledgers must use one local edge")
        if not isinstance(self.transfers, KFS1T1Transfers):
            raise KFS1T1TransitionError("result requires complete transfers")
        transition_ids = tuple(self.transition_ids)
        allowed = {
            "LOCAL_CONTACT_BIND",
            "LOCAL_REFRACTORY_ENTRY",
            "LOCAL_REFRACTORY_RELEASE",
            "HOLD_FREE",
            "HOLD_BOUND",
            "HOLD_BLOCKED",
        }
        if not transition_ids or any(item not in allowed for item in transition_ids):
            raise KFS1T1TransitionError("result contains an unbound transition role")
        object.__setattr__(self, "participation", participation)
        object.__setattr__(self, "target_bound", target)
        object.__setattr__(self, "transition_ids", transition_ids)


def compute_kfs1_t1_edge_participation(
    first_fast_field_value: object,
    second_fast_field_value: object,
) -> float:
    """Return the bound symmetric local S observable without changing state."""

    first = _finite(first_fast_field_value, "first_fast_field_value")
    second = _finite(second_fast_field_value, "second_fast_field_value")
    if first < -1.0 or first > 1.0 or second < -1.0 or second > 1.0:
        raise KFS1T1TransitionError("fast field values must remain within [-1,1]")
    return ((first - second) / 2.0) ** 2


def _hold_ids(ledger: KFS1T1Ledger) -> tuple[str, ...]:
    result = []
    if ledger.free > 0.0:
        result.append("HOLD_FREE")
    if ledger.bound > 0.0:
        result.append("HOLD_BOUND")
    if ledger.blocked > 0.0:
        result.append("HOLD_BLOCKED")
    return tuple(result)


def advance_kfs1_t1_edge(
    pre_ledger: KFS1T1Ledger,
    first_fast_field_value: object,
    second_fast_field_value: object,
) -> KFS1T1TransitionResult:
    """Apply exactly one closed parameter-free T1 transition to one edge."""

    if not isinstance(pre_ledger, KFS1T1Ledger):
        raise KFS1T1TransitionError("pre_ledger must be KFS1T1Ledger")
    participation = compute_kfs1_t1_edge_participation(
        first_fast_field_value, second_fast_field_value
    )
    target = pre_ledger.capacity * participation

    bind = 0.0
    block = 0.0
    release = 0.0
    if participation > 0.0:
        if pre_ledger.bound < target:
            bind = min(pre_ledger.free, target - pre_ledger.bound)
        elif pre_ledger.bound > target:
            block = pre_ledger.bound - target
    else:
        block = pre_ledger.bound
        release = pre_ledger.blocked

    next_free = pre_ledger.free - bind + release
    next_bound = pre_ledger.bound + bind - block
    next_blocked = pre_ledger.blocked + block - release
    post_ledger = KFS1T1Ledger(
        edge_id=pre_ledger.edge_id,
        capacity=pre_ledger.capacity,
        free=next_free,
        bound=next_bound,
        blocked=next_blocked,
    )
    transfers = KFS1T1Transfers(bind=bind, block=block, release=release)

    transition_ids = []
    if bind > 0.0:
        transition_ids.append("LOCAL_CONTACT_BIND")
    if block > 0.0:
        transition_ids.append("LOCAL_REFRACTORY_ENTRY")
    if release > 0.0:
        transition_ids.append("LOCAL_REFRACTORY_RELEASE")
    if not transition_ids:
        transition_ids.extend(_hold_ids(post_ledger))

    return KFS1T1TransitionResult(
        participation=participation,
        target_bound=target,
        pre_ledger=pre_ledger,
        post_ledger=post_ledger,
        transfers=transfers,
        transition_ids=tuple(transition_ids),
    )
