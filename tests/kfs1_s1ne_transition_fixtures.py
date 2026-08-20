"""Independent S1-NE transition bytes and expected static outcomes."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from tests.kfs1_s1nb_fixtures import (
    ANATOMY_DIGEST,
    EDGE_ID,
    EXPOSURE_HISTORY_DIGEST,
    FIELD_REFERENCE_DIGEST,
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identity(label: str) -> str:
    return _sha(label.encode("ascii"))


def _digest(record: dict[str, Any], field: str) -> str:
    return _sha(_canonical({key: value for key, value in record.items() if key != field}))


def _ledger(free: int, bound: int, blocked: int, capacity: int = 1) -> dict[str, Any]:
    ledger: dict[str, Any] = {
        "edge_id": EDGE_ID,
        "capacity": capacity,
        "free": free,
        "bound": bound,
        "blocked": blocked,
    }
    ledger["resource_account_digest"] = _digest(ledger, "resource_account_digest")
    return ledger


TRIGGERS = {
    "LOCAL_CONTACT_BIND": (
        "LOCAL_CONTACT_OBSERVATION",
        _identity("kfs1.trigger.contact.01"),
        "interval:contact:01",
    ),
    "LOCAL_BOUND_RELEASE": (
        "LOCAL_BOUND_RELEASE_OBSERVATION",
        _identity("kfs1.trigger.bound-release.01"),
        "interval:bound-release:01",
    ),
    "LOCAL_REFRACTORY_ENTRY": (
        "LOCAL_BOUND_COMPLETION_OBSERVATION",
        _identity("kfs1.trigger.bound-completion.01"),
        "interval:refractory-entry:01",
    ),
    "LOCAL_REFRACTORY_RELEASE": (
        "LOCAL_BLOCKED_RELEASE_OBSERVATION",
        _identity("kfs1.trigger.blocked-release.01"),
        "interval:blocked-release:01",
    ),
}


def _event(
    transition_id: str,
    source: str,
    target: str,
    pre: dict[str, Any],
    post: dict[str, Any],
    amount: int,
    *,
    ordinal: int = 1,
    prior_event_digest: str | None = None,
    event_suffix: str | None = None,
) -> dict[str, Any]:
    hold = transition_id.startswith("HOLD_")
    trigger_class, trigger_digest, interval_id = (
        ("NO_TRIGGER", None, f"interval:{transition_id.lower()}:01")
        if hold
        else TRIGGERS[transition_id]
    )
    record: dict[str, Any] = {
        "schema_id": "kfs1_transition_record",
        "schema_version": "s1nd.v1",
        "candidate_id": "KFS-1",
        "event_id": f"event:{event_suffix or transition_id.lower()}:{ordinal:02d}",
        "transition_id": transition_id,
        "edge_id": EDGE_ID,
        "field_interval_id": interval_id,
        "event_ordinal": ordinal,
        "source_role": source,
        "target_role": target,
        "transfer_amount": amount,
        "pre_ledger": deepcopy(pre),
        "post_ledger": deepcopy(post),
        "anatomy_digest": ANATOMY_DIGEST,
        "field_reference_digest": FIELD_REFERENCE_DIGEST,
        "exposure_history_digest": EXPOSURE_HISTORY_DIGEST,
        "trigger_class": trigger_class,
        "trigger_observation_digest": trigger_digest,
        "prior_event_digest": prior_event_digest,
    }
    record["event_digest"] = _digest(record, "event_digest")
    return record


POSITIVE_EVENTS = {
    "V_LOCAL_CONTACT_BIND": _event("LOCAL_CONTACT_BIND", "free", "bound", _ledger(1, 0, 0), _ledger(0, 1, 0), 1),
    "V_LOCAL_BOUND_RELEASE": _event("LOCAL_BOUND_RELEASE", "bound", "free", _ledger(0, 1, 0), _ledger(1, 0, 0), 1),
    "V_LOCAL_REFRACTORY_ENTRY": _event("LOCAL_REFRACTORY_ENTRY", "bound", "blocked", _ledger(0, 1, 0), _ledger(0, 0, 1), 1),
    "V_LOCAL_REFRACTORY_RELEASE": _event("LOCAL_REFRACTORY_RELEASE", "blocked", "free", _ledger(0, 0, 1), _ledger(1, 0, 0), 1),
    "V_HOLD_FREE": _event("HOLD_FREE", "free", "free", _ledger(1, 0, 0), _ledger(1, 0, 0), 0),
    "V_HOLD_BOUND": _event("HOLD_BOUND", "bound", "bound", _ledger(0, 1, 0), _ledger(0, 1, 0), 0),
    "V_HOLD_BLOCKED": _event("HOLD_BLOCKED", "blocked", "blocked", _ledger(0, 0, 1), _ledger(0, 0, 1), 0),
}


def _changed(base: dict[str, Any], path: tuple[Any, ...], value: Any, *, finalize: bool = True) -> dict[str, Any]:
    record = deepcopy(base)
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    if finalize:
        record["event_digest"] = _digest(record, "event_digest")
    return record


def _without(base: dict[str, Any], key: str) -> dict[str, Any]:
    record = deepcopy(base)
    del record[key]
    return record


BASE = POSITIVE_EVENTS["V_LOCAL_CONTACT_BIND"]
_unknown_schema = _changed(BASE, ("schema_version",), "s1nd.v2")
_missing_field = _without(BASE, "candidate_id")
_noncanonical_raw = json.dumps(BASE, ensure_ascii=False, indent=2).encode("utf-8")
_unknown_transition = _changed(BASE, ("transition_id",), "LOCAL_UNKNOWN")
_role_pair = _changed(BASE, ("source_role",), "blocked")
_invalid_amount = _changed(BASE, ("transfer_amount",), 0)
_pre_invalid = deepcopy(BASE)
_pre_invalid["pre_ledger"] = _ledger(2, 0, 0)
_pre_invalid["event_digest"] = _digest(_pre_invalid, "event_digest")
_post_invalid = deepcopy(BASE)
_post_invalid["post_ledger"] = _ledger(0, 2, 0)
_post_invalid["event_digest"] = _digest(_post_invalid, "event_digest")
_edge_mismatch = _changed(BASE, ("edge_id",), "edge:wrong")
_capacity_changed = deepcopy(BASE)
_capacity_changed["post_ledger"] = _ledger(1, 1, 0, capacity=2)
_capacity_changed["event_digest"] = _digest(_capacity_changed, "event_digest")
_conservation = deepcopy(BASE)
_conservation["post_ledger"] = _ledger(0, 0, 1)
_conservation["event_digest"] = _digest(_conservation, "event_digest")
_trigger = _changed(BASE, ("trigger_observation_digest",), _identity("wrong-trigger"))
_field = _changed(BASE, ("field_reference_digest",), _identity("wrong-field"))
_anatomy = _changed(BASE, ("anatomy_digest",), _identity("wrong-anatomy"))
_exposure = _changed(BASE, ("exposure_history_digest",), _identity("wrong-exposure"))
_order = _changed(BASE, ("event_ordinal",), 2)
_event_digest = _changed(BASE, ("event_digest",), "0" * 64, finalize=False)
_forbidden = _changed(BASE, ("raw_data",), [1, 2, 3])


@dataclass(frozen=True)
class TransitionFixture:
    fixture_id: str
    raw_bytes: bytes
    input_bytes_digest: str
    failure_reasons: tuple[str, ...]
    computed_record_digest: str


def _fixture(
    fixture_id: str,
    record: dict[str, Any],
    failures: tuple[str, ...] = (),
    *,
    raw_bytes: bytes | None = None,
    computable: bool = True,
) -> TransitionFixture:
    raw = _canonical(record) if raw_bytes is None else raw_bytes
    computed = _digest(record, "event_digest") if computable else "not_computable"
    return TransitionFixture(
        fixture_id,
        raw,
        _sha(raw),
        tuple(sorted(failures)),
        computed,
    )


TRANSITION_FIXTURES = (
    *(_fixture(name, record) for name, record in POSITIVE_EVENTS.items()),
    _fixture("I_UNKNOWN_SCHEMA", _unknown_schema, ("UNKNOWN_TRANSITION_SCHEMA_OR_VERSION",)),
    _fixture("I_MISSING_FIELD", _missing_field, ("MISSING_OR_UNKNOWN_TRANSITION_FIELD",), computable=False),
    _fixture("I_NONCANONICAL", BASE, ("NONCANONICAL_TRANSITION_SERIALIZATION",), raw_bytes=_noncanonical_raw),
    _fixture("I_UNKNOWN_TRANSITION", _unknown_transition, ("UNKNOWN_TRANSITION_ID",)),
    _fixture("I_ROLE_PAIR", _role_pair, ("TRANSITION_ROLE_PAIR_MISMATCH",)),
    _fixture("I_INVALID_AMOUNT", _invalid_amount, ("INVALID_TRANSFER_AMOUNT",)),
    _fixture("I_PRE_LEDGER", _pre_invalid, ("PRE_LEDGER_INVALID",)),
    _fixture("I_POST_LEDGER", _post_invalid, ("POST_LEDGER_INVALID",)),
    _fixture("I_EDGE", _edge_mismatch, ("EDGE_ID_MISMATCH",)),
    _fixture("I_CAPACITY", _capacity_changed, ("CAPACITY_CHANGED",)),
    _fixture("I_CONSERVATION", _conservation, ("LOCAL_CONSERVATION_MISMATCH",)),
    _fixture("I_TRIGGER", _trigger, ("TRIGGER_BINDING_MISMATCH",)),
    _fixture("I_FIELD", _field, ("FIELD_REFERENCE_MISMATCH",)),
    _fixture("I_ANATOMY", _anatomy, ("ANATOMY_DIGEST_MISMATCH",)),
    _fixture("I_EXPOSURE", _exposure, ("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",)),
    _fixture("I_ORDER", _order, ("EVENT_ORDER_OR_PREDECESSOR_MISMATCH",)),
    _fixture("I_EVENT_DIGEST", _event_digest, ("EVENT_DIGEST_MISMATCH",)),
    _fixture("I_FORBIDDEN", _forbidden, ("FORBIDDEN_TRANSITION_PAYLOAD_PRESENT",), computable=False),
)
TRANSITION_EXPECTATIONS = {fixture.fixture_id: fixture for fixture in TRANSITION_FIXTURES}

CHAIN_FIRST = POSITIVE_EVENTS["V_LOCAL_CONTACT_BIND"]
CHAIN_SECOND = _event(
    "LOCAL_REFRACTORY_ENTRY",
    "bound",
    "blocked",
    CHAIN_FIRST["post_ledger"],
    _ledger(0, 0, 1),
    1,
    ordinal=2,
    prior_event_digest=CHAIN_FIRST["event_digest"],
    event_suffix="chain-refractory",
)
CHAIN_BROKEN = _changed(CHAIN_SECOND, ("prior_event_digest",), "0" * 64)

assert len(POSITIVE_EVENTS) == 7
assert len(TRANSITION_FIXTURES) == 25
assert len(TRANSITION_EXPECTATIONS) == 25
