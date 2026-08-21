"""Canonical synchronous S1-SF exposure fixture without model execution."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json

from .field_step_time import MCMFieldStepTime
from .four_node_fresh_matrix_registration import (
    FourNodeFreshMatrixRegistration,
    FourNodeFreshMatrixRegistrationError,
    parse_four_node_fresh_matrix_registration,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution


class FourNodeExposureFixtureError(ValueError):
    """Raised when an S1-SF fixture identity or relationship differs."""


INTERVAL = "INTERVAL"
ALIGN = "ALIGN_READOUT_SH"
CHECKPOINT = "CHECKPOINT"

_SCHEMA_ID = "mcm.s1sf.four-node-exposure-fixture.v1"
_SOURCE_CONTRACT_ID = "S1-SF"
_FIELD_CLOCK = "mcm.s1sf.field"
_SOURCE_CLOCK = "mcm.s1sf.source"
_TICKS_PER_SECOND = 10.0
_INTERVAL_TICKS = 10
_MODALITY = "technical-control"
_GEOMETRY = "mcm.s1rf.receptor.4n"
_DOCK = "dock.s1rf.technical-control.4n"
_CARRIERS = ("carrier-a", "carrier-b", "carrier-c", "carrier-d")
_ZERO = (0.0, 0.0, 0.0, 0.0)
_VALUES = {
    "A_CONTACT": (0.0, 0.5, 0.0, 0.0),
    "B_CONTACT": (0.5, 0.0, 0.0, 0.0),
    "C_CONTACT": (0.0, 0.0, 0.0, 0.5),
    "PROBE_A_CONTACT": (0.0, 0.25, 0.0, 0.0),
    "PROBE_B_CONTACT": (0.25, 0.0, 0.0, 0.0),
}
_REPLICA_ROLES = (
    "F_A",
    "F_C",
    "F_G",
    "T_EARLY",
    "T_LATER",
    "I_LOCAL",
    "I_REMOTE",
    "I_GAP",
    "C_LOCAL",
    "C_REMOTE",
    "C_GAP",
    "R_EARLY",
    "R_LATE",
    "U_RELEASED",
    "U_EARLY",
    "U_FRESH_B_EARLY",
    "U_FRESH_B_LATE",
)


def _fail(code: str, detail: str) -> None:
    raise FourNodeExposureFixtureError(f"{code}: {detail}")


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value)}
    _fail("FOUR_NODE_EXPOSURE_FIXTURE_DIGEST_INVALID", "canonical object differs")


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class FourNodeExposureInterval:
    payload_role: str
    distribution: ReceptorDistribution
    step_time: MCMFieldStepTime
    interval_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeAlignTarget:
    field_tick: int
    receptor_contact: tuple[float, float, float, float]
    activation: tuple[float, float, float, float]
    afterimage: tuple[float, float, float, float]
    target_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeExposureEvent:
    event_kind: str
    interval_or_none: FourNodeExposureInterval | None
    align_target_or_none: FourNodeAlignTarget | None
    checkpoint_role_or_none: str | None
    checkpoint_tick_or_none: int | None
    event_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeExposurePlan:
    position: int
    replica_role: str
    events: tuple[FourNodeExposureEvent, ...]
    model_interval_count: int
    checkpoint_count: int
    terminal_tick: int
    plan_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeExposureFixture:
    schema_id: str
    source_contract_id: str
    matrix_registration_digest: str
    plans: tuple[FourNodeExposurePlan, ...]
    model_interval_count_per_role: int
    align_count_per_role: int
    checkpoint_count_per_role: int
    fixture_digest: str


def _interval(payload_role: str, start_tick: int) -> FourNodeExposureEvent:
    end_tick = start_tick + _INTERVAL_TICKS
    field_time = CommonFieldTime(_FIELD_CLOCK, start_tick, end_tick)
    if payload_role == "ZERO_CONTACT":
        distribution = ReceptorDistribution(field_time, ())
    else:
        try:
            values = _VALUES[payload_role]
        except KeyError as exc:
            _fail("FOUR_NODE_EXPOSURE_FIXTURE_INTERVAL_INVALID", str(exc))
        snapshot_role = payload_role.lower().replace("_", "-")
        frame = ReceptorContactFrame(
            modality_id=_MODALITY,
            geometry_id=_GEOMETRY,
            snapshot_id=f"s1sf.{snapshot_role}.{start_tick}.{end_tick}",
            clock_id=_SOURCE_CLOCK,
            window_start_tick=start_tick,
            window_end_tick=end_tick,
            carrier_ids=_CARRIERS,
            values=values,
        )
        distribution = ReceptorDistribution(
            field_time,
            (DistributedReceptorContact(_DOCK, frame),),
        )
    step = MCMFieldStepTime(_FIELD_CLOCK, start_tick, end_tick, _TICKS_PER_SECOND)
    interval_payload = {
        "payload_role": payload_role,
        "distribution": distribution.canonical_payload(),
        "step_time": {
            "clock_id": step.clock_id,
            "start_tick": step.start_tick,
            "end_tick": step.end_tick,
            "ticks_per_second": step.ticks_per_second,
        },
    }
    interval = FourNodeExposureInterval(
        payload_role,
        distribution,
        step,
        _digest(interval_payload),
    )
    return FourNodeExposureEvent(
        INTERVAL,
        interval,
        None,
        None,
        None,
        _digest({"event_kind": INTERVAL, "interval_digest": interval.interval_digest}),
    )


def _intervals(payload_role: str, count: int, start_tick: int) -> tuple[FourNodeExposureEvent, ...]:
    return tuple(
        _interval(payload_role, start_tick + index * _INTERVAL_TICKS)
        for index in range(count)
    )


def _align(field_tick: int) -> FourNodeExposureEvent:
    target_payload = {
        "field_tick": field_tick,
        "receptor_contact": _ZERO,
        "activation": _ZERO,
        "afterimage": _ZERO,
    }
    target = FourNodeAlignTarget(field_tick, _ZERO, _ZERO, _ZERO, _digest(target_payload))
    return FourNodeExposureEvent(
        ALIGN,
        None,
        target,
        None,
        None,
        _digest({"event_kind": ALIGN, "target_digest": target.target_digest}),
    )


def _checkpoint(role: str, field_tick: int) -> FourNodeExposureEvent:
    return FourNodeExposureEvent(
        CHECKPOINT,
        None,
        None,
        role,
        field_tick,
        _digest(
            {
                "event_kind": CHECKPOINT,
                "checkpoint_role": role,
                "field_tick": field_tick,
            }
        ),
    )


def _readout(
    field_tick: int,
    probe_role: str,
) -> tuple[FourNodeExposureEvent, ...]:
    return (
        _align(field_tick),
        _checkpoint("ALIGNED_PRE_PROBE", field_tick),
        _interval(probe_role, field_tick),
        _checkpoint("POST_PROBE_READOUT", field_tick + _INTERVAL_TICKS),
    )


def _plan(
    position: int,
    role: str,
    events: tuple[FourNodeExposureEvent, ...],
) -> FourNodeExposurePlan:
    intervals = tuple(item for item in events if item.event_kind == INTERVAL)
    checkpoints = tuple(item for item in events if item.event_kind == CHECKPOINT)
    terminal_tick = max(
        item.interval_or_none.step_time.end_tick
        for item in intervals
        if item.interval_or_none is not None
    )
    payload = {
        "position": position,
        "replica_role": role,
        "event_digests": tuple(item.event_digest for item in events),
        "model_interval_count": len(intervals),
        "checkpoint_count": len(checkpoints),
        "terminal_tick": terminal_tick,
    }
    return FourNodeExposurePlan(
        position,
        role,
        events,
        len(intervals),
        len(checkpoints),
        terminal_tick,
        _digest(payload),
    )


def _build_plans() -> tuple[FourNodeExposurePlan, ...]:
    a2 = _intervals("A_CONTACT", 2, 0)
    a3 = _intervals("A_CONTACT", 3, 0)
    a4 = _intervals("A_CONTACT", 4, 0)
    c3 = _intervals("C_CONTACT", 3, 0)
    z3_initial = _intervals("ZERO_CONTACT", 3, 0)
    b2_middle = _intervals("B_CONTACT", 2, 40)
    c2_middle = _intervals("C_CONTACT", 2, 40)
    z2_middle = _intervals("ZERO_CONTACT", 2, 40)
    z3_gap = _intervals("ZERO_CONTACT", 3, 40)
    z6_gap = _intervals("ZERO_CONTACT", 6, 40)
    z7_fresh = _intervals("ZERO_CONTACT", 7, 0)
    z10_fresh = _intervals("ZERO_CONTACT", 10, 0)

    raw = (
        ("F_A", a3 + _readout(30, "PROBE_A_CONTACT")),
        ("F_C", c3 + _readout(30, "PROBE_A_CONTACT")),
        ("F_G", z3_initial + _readout(30, "PROBE_A_CONTACT")),
        ("T_EARLY", a2 + _readout(20, "PROBE_A_CONTACT")),
        ("T_LATER", a4 + _readout(40, "PROBE_A_CONTACT")),
        ("I_LOCAL", a4 + b2_middle + _readout(60, "PROBE_A_CONTACT")),
        ("I_REMOTE", a4 + c2_middle + _readout(60, "PROBE_A_CONTACT")),
        ("I_GAP", a4 + z2_middle + _readout(60, "PROBE_A_CONTACT")),
        (
            "C_LOCAL",
            a4
            + (_checkpoint("PRE_COMPETITION", 40),)
            + b2_middle
            + (_checkpoint("POST_COMPETITION", 60),)
            + _readout(60, "PROBE_A_CONTACT"),
        ),
        (
            "C_REMOTE",
            a4
            + (_checkpoint("PRE_COMPETITION", 40),)
            + c2_middle
            + (_checkpoint("POST_COMPETITION", 60),)
            + _readout(60, "PROBE_A_CONTACT"),
        ),
        (
            "C_GAP",
            a4
            + (_checkpoint("PRE_COMPETITION", 40),)
            + z2_middle
            + (_checkpoint("POST_COMPETITION", 60),)
            + _readout(60, "PROBE_A_CONTACT"),
        ),
        ("R_EARLY", a4 + z3_gap + _readout(70, "PROBE_A_CONTACT")),
        ("R_LATE", a4 + z6_gap + _readout(100, "PROBE_A_CONTACT")),
        (
            "U_RELEASED",
            a4 + z6_gap + _intervals("B_CONTACT", 2, 100) + _readout(120, "PROBE_B_CONTACT"),
        ),
        (
            "U_EARLY",
            a4 + z3_gap + _intervals("B_CONTACT", 2, 70) + _readout(90, "PROBE_B_CONTACT"),
        ),
        (
            "U_FRESH_B_EARLY",
            z7_fresh + _intervals("B_CONTACT", 2, 70) + _readout(90, "PROBE_B_CONTACT"),
        ),
        (
            "U_FRESH_B_LATE",
            z10_fresh + _intervals("B_CONTACT", 2, 100) + _readout(120, "PROBE_B_CONTACT"),
        ),
    )
    return tuple(
        _plan(position, role, events)
        for position, (role, events) in enumerate(raw, start=1)
    )


def _validated_registration(
    registration: FourNodeFreshMatrixRegistration,
) -> FourNodeFreshMatrixRegistration:
    if not isinstance(registration, FourNodeFreshMatrixRegistration):
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_REGISTRATION_INVALID", "registration type differs")
    try:
        raw = json.dumps(
            _thaw(registration.root),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        validated = parse_four_node_fresh_matrix_registration(raw)
    except (FourNodeFreshMatrixRegistrationError, TypeError, ValueError) as exc:
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_REGISTRATION_INVALID", str(exc))
    if validated.replica_roles != _REPLICA_ROLES:
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_PLAN_AXIS_INVALID", "registration axis differs")
    return validated


def build_four_node_exposure_fixture(
    registration: FourNodeFreshMatrixRegistration,
) -> FourNodeExposureFixture:
    """Build the immutable 17-plan fixture without invoking a model."""

    validated = _validated_registration(registration)
    plans = _build_plans()
    interval_count = sum(item.model_interval_count for item in plans)
    align_count = sum(
        event.event_kind == ALIGN
        for plan in plans
        for event in plan.events
    )
    checkpoint_count = sum(item.checkpoint_count for item in plans)
    payload = {
        "schema_id": _SCHEMA_ID,
        "source_contract_id": _SOURCE_CONTRACT_ID,
        "matrix_registration_digest": validated.registration_digest,
        "plan_digests": tuple(item.plan_digest for item in plans),
        "model_interval_count_per_role": interval_count,
        "align_count_per_role": align_count,
        "checkpoint_count_per_role": checkpoint_count,
    }
    return FourNodeExposureFixture(
        _SCHEMA_ID,
        _SOURCE_CONTRACT_ID,
        validated.registration_digest,
        plans,
        interval_count,
        align_count,
        checkpoint_count,
        _digest(payload),
    )


def validate_four_node_exposure_fixture(
    fixture: FourNodeExposureFixture,
    registration: FourNodeFreshMatrixRegistration,
) -> None:
    """Require exact equality to the canonical S1-SF expansion."""

    if not isinstance(fixture, FourNodeExposureFixture):
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_SHAPE_INVALID", "fixture type differs")
    expected = build_four_node_exposure_fixture(registration)
    if (
        fixture.schema_id != _SCHEMA_ID
        or fixture.source_contract_id != _SOURCE_CONTRACT_ID
        or fixture.matrix_registration_digest != expected.matrix_registration_digest
    ):
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_REGISTRATION_INVALID", "fixture identity differs")
    if len(fixture.plans) != 17:
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_CARDINALITY_INVALID", "plan count differs")
    if tuple((item.position, item.replica_role) for item in fixture.plans) != tuple(
        enumerate(_REPLICA_ROLES, start=1)
    ):
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_PLAN_AXIS_INVALID", "plan axis differs")
    if (
        fixture.model_interval_count_per_role != 127
        or fixture.align_count_per_role != 17
        or fixture.checkpoint_count_per_role != 40
    ):
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_CARDINALITY_INVALID", "fixture counts differ")
    if fixture.fixture_digest != expected.fixture_digest:
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_DIGEST_INVALID", "fixture digest differs")
    if fixture != expected:
        _fail("FOUR_NODE_EXPOSURE_FIXTURE_EVENT_ORDER_INVALID", "fixture expansion differs")
