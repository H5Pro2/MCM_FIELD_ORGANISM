"""Private one-use formation consumer for bound active receptor batches."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from threading import Lock

from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    initial_ppb1_bank_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import (
    S1WQPerceptualTransitionRecord,
    advance_s1wq_perceptual_state,
)
from .receptor_contract import technical_identifier


PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION = (
    "ppb1.private.active-batch-formation-consumer.v1"
)
PPB1_ACTIVE_BATCH_FORMATION_INVALID_INPUT = (
    "PPB1_ACTIVE_BATCH_FORMATION_INVALID_INPUT"
)
PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED = (
    "PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED"
)
PPB1_ACTIVE_BATCH_FORMATION_OWNER_BUSY = (
    "PPB1_ACTIVE_BATCH_FORMATION_OWNER_BUSY"
)
PPB1_ACTIVE_BATCH_FORMATION_OWNER_TERMINAL = (
    "PPB1_ACTIVE_BATCH_FORMATION_OWNER_TERMINAL"
)
PPB1_ACTIVE_BATCH_FORMATION_ATTEMPT_FAILED = (
    "PPB1_ACTIVE_BATCH_FORMATION_ATTEMPT_FAILED"
)
PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED = (
    "PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_STABLE_STATUSES = {"AUTHORIZED", "CONSUMED", "FAILED"}


class PPB1ActiveBatchFormationError(ValueError):
    """One fail-closed private formation-consumer violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise PPB1ActiveBatchFormationError(
            PPB1_ACTIVE_BATCH_FORMATION_INVALID_INPUT,
            str(exc),
        ) from exc


@dataclass(frozen=True, slots=True)
class PPB1ActiveBatchFormationOwnerSnapshot:
    owner_id: str
    authorization_id: str
    consumption_id: str
    authorized_envelope_digest: str
    authorized_profile_binding_digest: str
    authorized_auditory_fresh_prestate_digest: str
    authorized_visual_fresh_prestate_digest: str
    status: str
    attempt_count: int
    use_count: int
    generation: int
    committed_result_digest: str | None
    failure_code: str | None
    failure_digest: str | None
    owner_state_digest: str

    def __post_init__(self) -> None:
        for role in ("owner_id", "authorization_id", "consumption_id"):
            _identifier(getattr(self, role), role)
        digest_roles = (
            self.authorized_envelope_digest,
            self.authorized_profile_binding_digest,
            self.authorized_auditory_fresh_prestate_digest,
            self.authorized_visual_fresh_prestate_digest,
            self.owner_state_digest,
        )
        valid_shape = (
            self.status in _STABLE_STATUSES
            and all(_valid_digest(value) for value in digest_roles)
            and self.attempt_count in {0, 1}
            and self.use_count in {0, 1}
            and self.generation in {0, 1}
        )
        if not valid_shape or not self._status_shape_is_valid():
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                "owner snapshot shape is invalid",
            )
        if self.owner_state_digest != _digest(self.payload_without_digest()):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                "owner snapshot digest mismatch",
            )

    def _status_shape_is_valid(self) -> bool:
        if self.status == "AUTHORIZED":
            return (
                (self.attempt_count, self.use_count, self.generation) == (0, 0, 0)
                and self.committed_result_digest is None
                and self.failure_code is None
                and self.failure_digest is None
            )
        if self.status == "CONSUMED":
            return (
                (self.attempt_count, self.use_count, self.generation) == (1, 1, 1)
                and _valid_digest(self.committed_result_digest)
                and self.failure_code is None
                and self.failure_digest is None
            )
        return (
            (self.attempt_count, self.use_count, self.generation) == (1, 0, 1)
            and self.committed_result_digest is None
            and isinstance(self.failure_code, str)
            and bool(self.failure_code)
            and _valid_digest(self.failure_digest)
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
            "owner_id": self.owner_id,
            "authorization_id": self.authorization_id,
            "consumption_id": self.consumption_id,
            "authorized_envelope_digest": self.authorized_envelope_digest,
            "authorized_profile_binding_digest": (
                self.authorized_profile_binding_digest
            ),
            "authorized_auditory_fresh_prestate_digest": (
                self.authorized_auditory_fresh_prestate_digest
            ),
            "authorized_visual_fresh_prestate_digest": (
                self.authorized_visual_fresh_prestate_digest
            ),
            "status": self.status,
            "attempt_count": self.attempt_count,
            "use_count": self.use_count,
            "generation": self.generation,
            "committed_result_digest": self.committed_result_digest,
            "failure_code": self.failure_code,
            "failure_digest": self.failure_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "owner_state_digest": self.owner_state_digest,
        }

    def result_projection_payload(self) -> dict[str, object]:
        payload = self.payload_without_digest()
        payload.pop("committed_result_digest")
        return payload


@dataclass(frozen=True, slots=True)
class PPB1ActiveBatchFormationStepReceipt:
    schedule_index: int
    modality_id: str
    snapshot_id: str
    timed_frame_provenance_digest: str
    input_projection_digest: str
    prestate_digest: str
    poststate_digest: str
    transition_record_digest: str
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schedule_index, bool)
            or not isinstance(self.schedule_index, int)
            or self.schedule_index < 0
            or self.modality_id not in {"auditory", "visual"}
            or not isinstance(self.snapshot_id, str)
            or not self.snapshot_id
            or not all(
                _valid_digest(value)
                for value in (
                    self.timed_frame_provenance_digest,
                    self.input_projection_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                    self.transition_record_digest,
                    self.receipt_digest,
                )
            )
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                "formation step receipt is invalid",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
            "schedule_index": self.schedule_index,
            "modality_id": self.modality_id,
            "snapshot_id": self.snapshot_id,
            "timed_frame_provenance_digest": (
                self.timed_frame_provenance_digest
            ),
            "input_projection_digest": self.input_projection_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "transition_record_digest": self.transition_record_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "receipt_digest": self.receipt_digest}


@dataclass(frozen=True, slots=True)
class PPB1ActiveBatchFormationResult:
    consumption_id: str
    authorization_prestate_digest: str
    envelope_digest: str
    profile_binding_digest: str
    auditory_prestate_digest: str
    visual_prestate_digest: str
    ordered_schedule_digest: str
    ordered_step_receipts: tuple[PPB1ActiveBatchFormationStepReceipt, ...]
    auditory_poststate: PPB1BankState
    visual_poststate: PPB1BankState
    auditory_transition_records: tuple[S1WQPerceptualTransitionRecord, ...]
    visual_transition_records: tuple[S1WQPerceptualTransitionRecord, ...]
    authorization_poststate: PPB1ActiveBatchFormationOwnerSnapshot
    formation_result_digest: str

    def __post_init__(self) -> None:
        _identifier(self.consumption_id, "consumption_id")
        receipts = tuple(self.ordered_step_receipts)
        auditory_records = tuple(self.auditory_transition_records)
        visual_records = tuple(self.visual_transition_records)
        source_digests = (
            self.authorization_prestate_digest,
            self.envelope_digest,
            self.profile_binding_digest,
            self.auditory_prestate_digest,
            self.visual_prestate_digest,
            self.ordered_schedule_digest,
        )
        receipt_record_digests = tuple(
            item.transition_record_digest for item in receipts
        )
        transition_record_digests = tuple(
            item.record_digest for item in auditory_records + visual_records
        )
        if (
            not isinstance(self.auditory_poststate, PPB1BankState)
            or not isinstance(self.visual_poststate, PPB1BankState)
            or not isinstance(
                self.authorization_poststate,
                PPB1ActiveBatchFormationOwnerSnapshot,
            )
            or self.authorization_poststate.status != "CONSUMED"
            or self.authorization_poststate.consumption_id != self.consumption_id
            or self.authorization_poststate.authorized_envelope_digest
            != self.envelope_digest
            or self.authorization_poststate.authorized_profile_binding_digest
            != self.profile_binding_digest
            or self.authorization_poststate.authorized_auditory_fresh_prestate_digest
            != self.auditory_prestate_digest
            or self.authorization_poststate.authorized_visual_fresh_prestate_digest
            != self.visual_prestate_digest
            or self.authorization_poststate.committed_result_digest
            != self.formation_result_digest
            or not all(_valid_digest(value) for value in source_digests)
            or len(receipts) != len(auditory_records) + len(visual_records)
            or tuple(item.schedule_index for item in receipts)
            != tuple(range(len(receipts)))
            or sorted(receipt_record_digests)
            != sorted(transition_record_digests)
            or self.auditory_poststate.accepted_step_count
            != len(auditory_records)
            or self.visual_poststate.accepted_step_count != len(visual_records)
            or any(
                type(item) is not PPB1ActiveBatchFormationStepReceipt
                for item in receipts
            )
            or any(
                type(item) is not S1WQPerceptualTransitionRecord
                for item in auditory_records + visual_records
            )
            or not _valid_digest(self.formation_result_digest)
            or self.formation_result_digest != _digest(self.payload_without_digest())
        ):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                "formation result is incomplete or digest-inconsistent",
            )
        object.__setattr__(self, "ordered_step_receipts", receipts)
        object.__setattr__(self, "auditory_transition_records", auditory_records)
        object.__setattr__(self, "visual_transition_records", visual_records)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
            "consumption_id": self.consumption_id,
            "authorization_prestate_digest": self.authorization_prestate_digest,
            "envelope_digest": self.envelope_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "auditory_prestate_digest": self.auditory_prestate_digest,
            "visual_prestate_digest": self.visual_prestate_digest,
            "ordered_schedule_digest": self.ordered_schedule_digest,
            "ordered_step_receipt_digests": [
                item.receipt_digest for item in self.ordered_step_receipts
            ],
            "auditory_poststate_digest": self.auditory_poststate.digest(),
            "visual_poststate_digest": self.visual_poststate.digest(),
            "auditory_transition_record_digests": [
                item.record_digest for item in self.auditory_transition_records
            ],
            "visual_transition_record_digests": [
                item.record_digest for item in self.visual_transition_records
            ],
            "authorization_poststate": (
                self.authorization_poststate.result_projection_payload()
            ),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "formation_result_digest": self.formation_result_digest,
        }


def _snapshot_values(
    owner: PPB1ActiveBatchFormationConsumerOwner,
) -> dict[str, object]:
    return {
        "owner_id": owner._owner_id,
        "authorization_id": owner._authorization_id,
        "consumption_id": owner._consumption_id,
        "authorized_envelope_digest": owner._authorized_envelope_digest,
        "authorized_profile_binding_digest": (
            owner._authorized_profile_binding_digest
        ),
        "authorized_auditory_fresh_prestate_digest": (
            owner._authorized_auditory_fresh_prestate_digest
        ),
        "authorized_visual_fresh_prestate_digest": (
            owner._authorized_visual_fresh_prestate_digest
        ),
        "status": owner._status,
        "attempt_count": owner._attempt_count,
        "use_count": owner._use_count,
        "generation": owner._generation,
        "committed_result_digest": owner._committed_result_digest,
        "failure_code": owner._failure_code,
        "failure_digest": owner._failure_digest,
    }


def _make_snapshot(
    owner: PPB1ActiveBatchFormationConsumerOwner,
) -> PPB1ActiveBatchFormationOwnerSnapshot:
    values = _snapshot_values(owner)
    payload = {
        "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
        **values,
    }
    return PPB1ActiveBatchFormationOwnerSnapshot(
        **values,
        owner_state_digest=_digest(payload),
    )


def _require_fresh_state(
    config: PPB1BankConfig,
    state: object,
    modality_id: str,
) -> PPB1BankState:
    if type(state) is not PPB1BankState:
        raise PPB1ActiveBatchFormationError(
            PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
            f"{modality_id} prestate must be an exact PPB1BankState",
        )
    expected = initial_ppb1_bank_state(config)
    if state.digest() != expected.digest():
        raise PPB1ActiveBatchFormationError(
            PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
            f"{modality_id} prestate is not the exact fresh state",
        )
    return state


def _build_schedule(
    envelope: PPB1ActiveReceptorBatchEnvelope,
) -> tuple[tuple[str, PPB1ActiveReceptorTimedFrameBinding], ...]:
    candidates = [
        ("auditory", index, item)
        for index, item in enumerate(envelope.auditory_stream.timed_frames)
    ] + [
        ("visual", index, item)
        for index, item in enumerate(envelope.visual_stream.timed_frames)
    ]
    schedule = sorted(
        candidates,
        key=lambda value: (
            value[2].field_window_end_tick,
            value[2].field_window_start_tick,
            0 if value[0] == "auditory" else 1,
            value[2].snapshot_id,
        ),
    )
    for modality_id in ("auditory", "visual"):
        indices = [index for modality, index, _ in schedule if modality == modality_id]
        if indices != sorted(indices):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
                f"{modality_id} schedule does not preserve source order",
            )
    pairs = [(modality, item.snapshot_id) for modality, _, item in schedule]
    provenance = [item.timed_frame_provenance_digest for _, _, item in schedule]
    if len(set(pairs)) != len(pairs) or len(set(provenance)) != len(provenance):
        raise PPB1ActiveBatchFormationError(
            PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
            "schedule contains duplicate frame identity or provenance",
        )
    return tuple((modality, item) for modality, _, item in schedule)


class PPB1ActiveBatchFormationConsumerOwner:
    """Private authority for one preregistered terminal formation attempt."""

    def __init__(
        self,
        owner_id: str,
        authorization_id: str,
        consumption_id: str,
        authorized_envelope_digest: str,
        authorized_profile_binding_digest: str,
        authorized_auditory_fresh_prestate_digest: str,
        authorized_visual_fresh_prestate_digest: str,
    ) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        self._authorization_id = _identifier(
            authorization_id,
            "authorization_id",
        )
        self._consumption_id = _identifier(consumption_id, "consumption_id")
        digest_values = (
            authorized_envelope_digest,
            authorized_profile_binding_digest,
            authorized_auditory_fresh_prestate_digest,
            authorized_visual_fresh_prestate_digest,
        )
        if not all(_valid_digest(value) for value in digest_values):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_INVALID_INPUT,
                "authorized source roles must be SHA-256 digests",
            )
        self._authorized_envelope_digest = authorized_envelope_digest
        self._authorized_profile_binding_digest = (
            authorized_profile_binding_digest
        )
        self._authorized_auditory_fresh_prestate_digest = (
            authorized_auditory_fresh_prestate_digest
        )
        self._authorized_visual_fresh_prestate_digest = (
            authorized_visual_fresh_prestate_digest
        )
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._use_count = 0
        self._generation = 0
        self._committed_result_digest: str | None = None
        self._failure_code: str | None = None
        self._failure_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> PPB1ActiveBatchFormationOwnerSnapshot:
        with self._lock:
            return _make_snapshot(self)

    def _preflight(
        self,
        envelope: object,
        profile: object,
        auditory_prestate: object,
        visual_prestate: object,
    ) -> tuple[
        PPB1ActiveReceptorBatchEnvelope,
        PPB1ReceptorProfileBinding,
        PPB1BankState,
        PPB1BankState,
        tuple[tuple[str, PPB1ActiveReceptorTimedFrameBinding], ...],
    ]:
        if (
            type(envelope) is not PPB1ActiveReceptorBatchEnvelope
            or type(profile) is not PPB1ReceptorProfileBinding
        ):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
                "exact envelope and profile binding types are required",
            )
        auditory = _require_fresh_state(
            profile.auditory_config,
            auditory_prestate,
            "auditory",
        )
        visual = _require_fresh_state(
            profile.visual_config,
            visual_prestate,
            "visual",
        )
        if (
            envelope.envelope_digest != self._authorized_envelope_digest
            or profile.digest() != self._authorized_profile_binding_digest
            or auditory.digest()
            != self._authorized_auditory_fresh_prestate_digest
            or visual.digest() != self._authorized_visual_fresh_prestate_digest
            or envelope.profile_binding_digest != profile.digest()
            or envelope.profile_id != profile.profile_id
            or envelope.parameter_digest != profile.parameter_digest
            or envelope.auditory_stream.bank_config_digest
            != profile.auditory_config.digest()
            or envelope.visual_stream.bank_config_digest
            != profile.visual_config.digest()
        ):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
                "authorized envelope, profile or fresh state binding mismatch",
            )
        return envelope, profile, auditory, visual, _build_schedule(envelope)

    def consume_once(
        self,
        envelope: object,
        profile: object,
        auditory_fresh_prestate: object,
        visual_fresh_prestate: object,
    ) -> PPB1ActiveBatchFormationResult:
        if not self._lock.acquire(blocking=False):
            raise PPB1ActiveBatchFormationError(
                PPB1_ACTIVE_BATCH_FORMATION_OWNER_BUSY,
                "formation owner already has an active call",
            )
        try:
            if self._status != "AUTHORIZED":
                raise PPB1ActiveBatchFormationError(
                    PPB1_ACTIVE_BATCH_FORMATION_OWNER_TERMINAL,
                    f"formation owner is terminal: {self._status}",
                )
            bound = self._preflight(
                envelope,
                profile,
                auditory_fresh_prestate,
                visual_fresh_prestate,
            )
            bound_envelope, bound_profile, auditory, visual, schedule = bound
            authorization_prestate_digest = _make_snapshot(self).owner_state_digest
            source_digests = (
                bound_envelope.envelope_digest,
                bound_profile.digest(),
                auditory.digest(),
                visual.digest(),
            )
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            try:
                result_values = self._advance_schedule(
                    bound_envelope,
                    bound_profile,
                    auditory,
                    visual,
                    schedule,
                    authorization_prestate_digest,
                )
                if source_digests != (
                    bound_envelope.envelope_digest,
                    bound_profile.digest(),
                    auditory.digest(),
                    visual.digest(),
                ):
                    raise PPB1ActiveBatchFormationError(
                        PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                        "formation inputs changed during consumption",
                    )
                body_digest = _digest(result_values["result_payload"])
                self._status = "CONSUMED"
                self._use_count = 1
                self._generation = 1
                self._committed_result_digest = body_digest
                authorization_poststate = _make_snapshot(self)
                result = PPB1ActiveBatchFormationResult(
                    **result_values["result_fields"],
                    authorization_poststate=authorization_poststate,
                    formation_result_digest=body_digest,
                )
                return result
            except Exception as exc:
                if self._status == "CONSUMED":
                    self._status = "IN_PROGRESS"
                    self._use_count = 0
                    self._committed_result_digest = None
                failure_code = getattr(
                    exc,
                    "code",
                    PPB1_ACTIVE_BATCH_FORMATION_ATTEMPT_FAILED,
                )
                self._status = "FAILED"
                self._generation = 1
                self._failure_code = str(failure_code)
                self._failure_digest = _digest(
                    {
                        "schema_version": (
                            PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION
                        ),
                        "owner_id": self._owner_id,
                        "authorization_id": self._authorization_id,
                        "consumption_id": self._consumption_id,
                        "failure_code": self._failure_code,
                        "exception_type": type(exc).__name__,
                    }
                )
                raise PPB1ActiveBatchFormationError(
                    PPB1_ACTIVE_BATCH_FORMATION_ATTEMPT_FAILED,
                    "formation attempt failed without publishing a result",
                ) from exc
        finally:
            self._lock.release()

    def _advance_schedule(
        self,
        envelope: PPB1ActiveReceptorBatchEnvelope,
        profile: PPB1ReceptorProfileBinding,
        auditory_prestate: PPB1BankState,
        visual_prestate: PPB1BankState,
        schedule: tuple[tuple[str, PPB1ActiveReceptorTimedFrameBinding], ...],
        authorization_prestate_digest: str,
    ) -> dict[str, object]:
        states = {"auditory": auditory_prestate, "visual": visual_prestate}
        configs = {
            "auditory": profile.auditory_config,
            "visual": profile.visual_config,
        }
        records: dict[str, list[S1WQPerceptualTransitionRecord]] = {
            "auditory": [],
            "visual": [],
        }
        receipts: list[PPB1ActiveBatchFormationStepReceipt] = []
        for schedule_index, (modality_id, binding) in enumerate(schedule):
            prestate = states[modality_id]
            step = advance_s1wq_perceptual_state(
                configs[modality_id],
                prestate,
                binding.timed_frame.frame,
            )
            if (
                step.reference_readout.input_digest
                != binding.ppb1_input_projection_digest
                or step.transition.input_digest
                != binding.ppb1_input_projection_digest
                or step.transition.prestate_digest != prestate.digest()
                or step.transition.poststate_digest != step.poststate.digest()
            ):
                raise PPB1ActiveBatchFormationError(
                    PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                    "lifecycle step does not match bound frame provenance",
                )
            receipt_values = {
                "schedule_index": schedule_index,
                "modality_id": modality_id,
                "snapshot_id": binding.snapshot_id,
                "timed_frame_provenance_digest": (
                    binding.timed_frame_provenance_digest
                ),
                "input_projection_digest": binding.ppb1_input_projection_digest,
                "prestate_digest": prestate.digest(),
                "poststate_digest": step.poststate.digest(),
                "transition_record_digest": step.transition.record_digest,
            }
            receipt_payload = {
                "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
                **receipt_values,
            }
            receipts.append(
                PPB1ActiveBatchFormationStepReceipt(
                    **receipt_values,
                    receipt_digest=_digest(receipt_payload),
                )
            )
            states[modality_id] = step.poststate
            records[modality_id].append(step.transition)
        schedule_payload = [
            {
                "modality_id": modality_id,
                "timed_frame_provenance_digest": (
                    binding.timed_frame_provenance_digest
                ),
            }
            for modality_id, binding in schedule
        ]
        final_checks = (
            (
                states["auditory"],
                envelope.auditory_stream,
                records["auditory"],
            ),
            (
                states["visual"],
                envelope.visual_stream,
                records["visual"],
            ),
        )
        for state, stream, modality_records in final_checks:
            last = stream.timed_frames[-1]
            if (
                state.accepted_step_count != stream.frame_count
                or len(modality_records) != stream.frame_count
                or state.source_clock_id != stream.source_clock_id
                or state.last_source_window_end_tick
                != last.source_window_end_tick
            ):
                raise PPB1ActiveBatchFormationError(
                    PPB1_ACTIVE_BATCH_FORMATION_ATOMIC_RESULT_REQUIRED,
                    "final modality state does not match its complete stream",
                )
        fields = {
            "consumption_id": self._consumption_id,
            "authorization_prestate_digest": authorization_prestate_digest,
            "envelope_digest": envelope.envelope_digest,
            "profile_binding_digest": profile.digest(),
            "auditory_prestate_digest": auditory_prestate.digest(),
            "visual_prestate_digest": visual_prestate.digest(),
            "ordered_schedule_digest": _digest(schedule_payload),
            "ordered_step_receipts": tuple(receipts),
            "auditory_poststate": states["auditory"],
            "visual_poststate": states["visual"],
            "auditory_transition_records": tuple(records["auditory"]),
            "visual_transition_records": tuple(records["visual"]),
        }
        projection = {
            "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
            "owner_id": self._owner_id,
            "authorization_id": self._authorization_id,
            "consumption_id": self._consumption_id,
            "authorized_envelope_digest": self._authorized_envelope_digest,
            "authorized_profile_binding_digest": (
                self._authorized_profile_binding_digest
            ),
            "authorized_auditory_fresh_prestate_digest": (
                self._authorized_auditory_fresh_prestate_digest
            ),
            "authorized_visual_fresh_prestate_digest": (
                self._authorized_visual_fresh_prestate_digest
            ),
            "status": "CONSUMED",
            "attempt_count": 1,
            "use_count": 1,
            "generation": 1,
            "failure_code": None,
            "failure_digest": None,
        }
        payload = {
            "schema_version": PPB1_ACTIVE_BATCH_FORMATION_SCHEMA_VERSION,
            "consumption_id": fields["consumption_id"],
            "authorization_prestate_digest": authorization_prestate_digest,
            "envelope_digest": fields["envelope_digest"],
            "profile_binding_digest": fields["profile_binding_digest"],
            "auditory_prestate_digest": fields["auditory_prestate_digest"],
            "visual_prestate_digest": fields["visual_prestate_digest"],
            "ordered_schedule_digest": fields["ordered_schedule_digest"],
            "ordered_step_receipt_digests": [
                item.receipt_digest for item in receipts
            ],
            "auditory_poststate_digest": states["auditory"].digest(),
            "visual_poststate_digest": states["visual"].digest(),
            "auditory_transition_record_digests": [
                item.record_digest for item in records["auditory"]
            ],
            "visual_transition_record_digests": [
                item.record_digest for item in records["visual"]
            ],
            "authorization_poststate": projection,
        }
        return {"result_fields": fields, "result_payload": payload}


def prepare_ppb1_active_batch_formation_consumer_owner(
    owner_id: str,
    authorization_id: str,
    consumption_id: str,
    authorized_envelope_digest: str,
    authorized_profile_binding_digest: str,
    authorized_auditory_fresh_prestate_digest: str,
    authorized_visual_fresh_prestate_digest: str,
) -> PPB1ActiveBatchFormationConsumerOwner:
    return PPB1ActiveBatchFormationConsumerOwner(
        owner_id,
        authorization_id,
        consumption_id,
        authorized_envelope_digest,
        authorized_profile_binding_digest,
        authorized_auditory_fresh_prestate_digest,
        authorized_visual_fresh_prestate_digest,
    )
