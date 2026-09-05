"""Private transient two-view integration owned by the A_RECENT boundary."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from tools import _s2ly_private_two_view_projection as projection
from tools import _s2lz_private_open_set_comparison as open_set


SCHEMA = "s2ma.private-arecent-two-view-integration.v1"
AREA_ROLE = "A_RECENT"
MAX_VIEWS = 2
MAX_TICK_GAP = 1


class S2MAIntegrationError(RuntimeError):
    """Transient A_RECENT evidence is invalid or already consumed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MAIntegrationError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class ARecentObservedLookV1:
    owner_id: str
    case_plan_digest: str
    source_observation_digest: str
    source_id: str
    payload_sha256: str
    geometry_digest: str
    tick: int
    mask_id: str
    mask_digest: str
    observed_positions: tuple[int, ...]
    observed_values: tuple[float, ...]
    observed_values_digest: str
    source_values_digest: str
    field_contact_digest: str | None

    def __post_init__(self) -> None:
        _require(type(self.owner_id) is str and len(self.owner_id) >= 8, "owner differs")
        for value in (self.case_plan_digest, self.source_observation_digest, self.payload_sha256, self.geometry_digest, self.mask_digest, self.observed_values_digest, self.source_values_digest):
            _require(type(value) is str and len(value) == 64, "digest binding differs")
        _require(type(self.source_id) is str and len(self.source_id) >= 8, "source id differs")
        _require(type(self.tick) is int and self.tick >= 0, "native tick differs")
        _require(self.mask_id in {"VIEW_A_96", "VIEW_B_96"}, "mask role differs")
        _require(type(self.observed_positions) is tuple and len(self.observed_positions) == 96 and len(set(self.observed_positions)) == 96, "positions differ")
        _require(all(type(item) is int and 0 <= item < 288 for item in self.observed_positions), "position domain differs")
        _require(type(self.observed_values) is tuple and len(self.observed_values) == 96, "values differ")
        _require(all(type(item) is float and math.isfinite(item) and 0.0 <= item <= 1.0 for item in self.observed_values), "value domain differs")
        _require(self.observed_values_digest == _digest(list(self.observed_values)), "observed values digest differs")
        _require(self.field_contact_digest is None or (type(self.field_contact_digest) is str and len(self.field_contact_digest) == 64), "field sibling digest differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2ma.arecent-observed-look.v1",
            "owner_id": self.owner_id,
            "case_plan_digest": self.case_plan_digest,
            "source_observation_digest": self.source_observation_digest,
            "source_id": self.source_id,
            "payload_sha256": self.payload_sha256,
            "geometry_digest": self.geometry_digest,
            "tick": self.tick,
            "mask_id": self.mask_id,
            "mask_digest": self.mask_digest,
            "observed_positions": list(self.observed_positions),
            "observed_values": list(self.observed_values),
            "observed_values_digest": self.observed_values_digest,
            "source_values_digest": self.source_values_digest,
            "field_contact_digest": self.field_contact_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class ARecentTwoViewResultV1:
    status: str
    selected_model_id: str | None
    reason: str
    clear_cause: str | None
    first_look_digest: str
    second_look_digest: str | None
    open_set_decision_digest: str | None
    field_contact_digests: tuple[str, ...]
    window_discarded: bool
    retained_for_b_stable: bool

    def __post_init__(self) -> None:
        _require(self.status in {"PENDING", "ADMITTED", "ABSTAINED"}, "result status differs")
        _require(type(self.reason) is str and bool(self.reason), "result reason differs")
        _require(type(self.first_look_digest) is str and len(self.first_look_digest) == 64, "first look digest differs")
        _require(self.second_look_digest is None or (type(self.second_look_digest) is str and len(self.second_look_digest) == 64), "second look digest differs")
        _require(self.open_set_decision_digest is None or (type(self.open_set_decision_digest) is str and len(self.open_set_decision_digest) == 64), "decision digest differs")
        _require(type(self.field_contact_digests) is tuple and all(type(item) is str and len(item) == 64 for item in self.field_contact_digests), "field bindings differ")
        _require(self.retained_for_b_stable is False, "B_STABLE retention is forbidden")
        _require((self.status == "PENDING") != self.window_discarded, "window lifecycle differs")
        _require((self.status == "ADMITTED") == (self.selected_model_id is not None), "model admission differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "area_role": AREA_ROLE,
            "status": self.status,
            "selected_model_id": self.selected_model_id,
            "reason": self.reason,
            "clear_cause": self.clear_cause,
            "first_look_digest": self.first_look_digest,
            "second_look_digest": self.second_look_digest,
            "open_set_decision_digest": self.open_set_decision_digest,
            "field_contact_digests": list(self.field_contact_digests),
            "window_discarded": self.window_discarded,
            "retained_for_b_stable": self.retained_for_b_stable,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


class ARecentTransientTwoViewIntegrator:
    def __init__(
        self,
        *,
        geometry_digest: str,
        view_a_mask_digest: str,
        view_b_mask_digest: str,
        union_mask_digest: str,
        union_positions: tuple[int, ...],
        model_envelopes: dict[str, tuple[tuple[float, ...], float]],
    ) -> None:
        for value in (geometry_digest, view_a_mask_digest, view_b_mask_digest, union_mask_digest):
            _require(type(value) is str and len(value) == 64, "integrator binding differs")
        _require(type(union_positions) is tuple and len(union_positions) == 192 and len(set(union_positions)) == 192, "union positions differ")
        _require(type(model_envelopes) is dict and bool(model_envelopes), "model envelopes differ")
        self._geometry_digest = geometry_digest
        self._view_a_mask_digest = view_a_mask_digest
        self._view_b_mask_digest = view_b_mask_digest
        self._union_mask_digest = union_mask_digest
        self._union_positions = union_positions
        self._model_envelopes = dict(model_envelopes)
        self._pending: ARecentObservedLookV1 | None = None
        self._consumed_owners: set[str] = set()

    @property
    def pending_count(self) -> int:
        return 1 if self._pending is not None else 0

    def _validate_common(self, look: ARecentObservedLookV1) -> None:
        _require(type(look) is ARecentObservedLookV1, "look role differs")
        _require(look.owner_id not in self._consumed_owners, "event owner is already consumed")
        self._consumed_owners.add(look.owner_id)

    def process(self, look: ARecentObservedLookV1) -> ARecentTwoViewResultV1:
        self._validate_common(look)
        expected_mask = self._view_a_mask_digest if look.mask_id == "VIEW_A_96" else self._view_b_mask_digest
        if look.geometry_digest != self._geometry_digest or look.mask_digest != expected_mask:
            first = self._pending
            self._pending = None
            field_digests = tuple(item for item in ((first.field_contact_digest if first is not None else None), look.field_contact_digest) if item is not None)
            return ARecentTwoViewResultV1(
                status="ABSTAINED", selected_model_id=None, reason="PAIR_INCOMPATIBLE_NO_UNION",
                clear_cause="GEOMETRY_OR_MASK_BINDING_CONFLICT", first_look_digest=(first.digest() if first is not None else look.digest()),
                second_look_digest=(look.digest() if first is not None else None), open_set_decision_digest=None,
                field_contact_digests=field_digests, window_discarded=True, retained_for_b_stable=False,
            )
        if self._pending is None:
            if look.mask_id != "VIEW_A_96":
                return ARecentTwoViewResultV1(
                    status="ABSTAINED", selected_model_id=None, reason="PAIR_INCOMPATIBLE_NO_UNION", clear_cause="FIRST_ROLE_NOT_VIEW_A",
                    first_look_digest=look.digest(), second_look_digest=None, open_set_decision_digest=None,
                    field_contact_digests=tuple(item for item in (look.field_contact_digest,) if item is not None), window_discarded=True, retained_for_b_stable=False,
                )
            self._pending = look
            return ARecentTwoViewResultV1(
                status="PENDING", selected_model_id=None, reason="WAITING_FOR_SECOND_VIEW", clear_cause=None,
                first_look_digest=look.digest(), second_look_digest=None, open_set_decision_digest=None,
                field_contact_digests=tuple(item for item in (look.field_contact_digest,) if item is not None), window_discarded=False, retained_for_b_stable=False,
            )

        first = self._pending
        self._pending = None
        same_source = first.source_id == look.source_id
        same_payload = first.payload_sha256 == look.payload_sha256 and first.source_values_digest == look.source_values_digest
        same_case = first.case_plan_digest == look.case_plan_digest
        correct_roles = first.mask_id == "VIEW_A_96" and look.mask_id == "VIEW_B_96"
        tick_gap = look.tick - first.tick
        compatible = same_source and same_payload and same_case and correct_roles and 0 < tick_gap <= MAX_TICK_GAP
        compatibility_payload = {
            "case_plan_digest": first.case_plan_digest,
            "view_a_observation_digest": first.source_observation_digest,
            "view_b_observation_digest": look.source_observation_digest,
            "same_source_id": same_source,
            "same_payload_digest": same_payload,
            "tick_gap": tick_gap,
            "maximum_tick_gap": MAX_TICK_GAP,
            "compatible": compatible,
        }
        compatibility_digest = _digest(compatibility_payload)
        field_digests = tuple(item for item in (first.field_contact_digest, look.field_contact_digest) if item is not None)
        if not compatible:
            if not same_source or not same_payload:
                cause = "SOURCE_OR_PAYLOAD_CHANGED"
            elif not same_case:
                cause = "CASE_BINDING_CHANGED"
            elif not correct_roles:
                cause = "MASK_SEQUENCE_CONFLICT"
            else:
                cause = "WINDOW_EXPIRED"
            decision = open_set._pair_abstention("PAIR_INCOMPATIBLE_NO_UNION", compatibility_digest)
        else:
            _require(first.observed_positions + look.observed_positions == self._union_positions, "union position binding differs")
            union_values = first.observed_values + look.observed_values
            union_view = projection.ObservedVisualViewV1(
                mask_id="UNION_192",
                mask_digest=self._union_mask_digest,
                source_values_digest=first.source_values_digest,
                observed_positions=self._union_positions,
                observed_values=union_values,
                observed_values_digest=projection._digest(list(union_values)),
            )
            form = projection.project_mask_conditioned_form(union_view)
            decision = open_set._open_set_decision(form.values, self._model_envelopes)
            cause = "EVALUATED_AND_DISCARDED"
        return ARecentTwoViewResultV1(
            status=str(decision["status"]), selected_model_id=decision["selected_model_id"], reason=str(decision["reason"]), clear_cause=cause,
            first_look_digest=first.digest(), second_look_digest=look.digest(), open_set_decision_digest=str(decision["decision_digest"]),
            field_contact_digests=field_digests, window_discarded=True, retained_for_b_stable=False,
        )


__all__: tuple[str, ...] = ()
