"""Private atomic consumer for one AVPC-1 auditory-cued visual readout."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._avpc1_audio_only_probe_envelope import (
    AVPC1PrivateAuditoryOnlyProbeEnvelope,
)
from ._avpc1_bounded_relation import (
    AVPC1BoundedRelationError,
    AVPC1BoundedRelationState,
    AVPC1ReadOnlyRelationFinding,
    probe_avpc1_bounded_relation_read_only,
)
from ._avpc1_visual_prototype_resolver import (
    AVPC1ReadOnlyVisualPrototypeState,
    AVPC1VisualPrototypeResolverError,
    resolve_avpc1_visual_prototype_state,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankState
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
)
from .receptor_contract import technical_identifier


AVPC1_ATOMIC_READOUT_SCHEMA_VERSION = (
    "avpc1.private.atomic-auditory-cued-visual-readout.v1"
)
AVPC1_ATOMIC_READOUT_CONTRACT_DIGEST = (
    "14afa8c9c8fc78173fe54f907dfee8b1e74dda7b59195c5f84e3a8ea5f232f97"
)
AVPC1_ATOMIC_READOUT_PREFLIGHT_DIGEST = (
    "cf77e3add3206dbb6cdb6850cd112358e90dad50c95c157750401396149a8537"
)
AVPC1_ATOMIC_READOUT_INVALID_INPUT = "AVPC1_ATOMIC_READOUT_INVALID_INPUT"
AVPC1_ATOMIC_READOUT_SOURCE_MISMATCH = "AVPC1_ATOMIC_READOUT_SOURCE_MISMATCH"
AVPC1_ATOMIC_READOUT_RELATION_FAILURE = "AVPC1_ATOMIC_READOUT_RELATION_FAILURE"
AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH = (
    "AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH"
)
AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE = (
    "AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE"
)
AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED = (
    "AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED"
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class AVPC1AtomicReadoutConsumerError(ValueError):
    """One fail-closed private atomic readout violation."""

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
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_INVALID_INPUT,
            str(exc),
        ) from exc


def _visual_bank_identity_digest(state: PPB1BankState) -> str:
    return _digest(_state_identity_payload(state))


def _relation_finding_payload(
    finding: AVPC1ReadOnlyRelationFinding,
) -> dict[str, object]:
    return {
        **finding.payload_without_digest(),
        "finding_digest": finding.finding_digest,
    }


@dataclass(frozen=True, slots=True)
class AVPC1AtomicAuditoryCuedVisualReadoutOutcome:
    consumer_id: str
    audio_only_envelope_digest: str
    auditory_finding_digest: str
    relation_state_identity_digest: str
    observed_relation_state_digest: str
    profile_binding_digest: str
    visual_bank_state_identity_digest: str
    visual_bank_state_digest: str
    result_role: str
    relation_finding: AVPC1ReadOnlyRelationFinding
    visual_prototype_state: AVPC1ReadOnlyVisualPrototypeState | None
    outcome_digest: str
    schema_version: str = AVPC1_ATOMIC_READOUT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            consumer_id = technical_identifier(self.consumer_id, "consumer_id")
        except ValueError as exc:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                "outcome consumer identifier is invalid",
            ) from exc
        source_digests = (
            self.audio_only_envelope_digest,
            self.auditory_finding_digest,
            self.relation_state_identity_digest,
            self.observed_relation_state_digest,
            self.profile_binding_digest,
            self.visual_bank_state_identity_digest,
            self.visual_bank_state_digest,
            self.outcome_digest,
        )
        if (
            self.schema_version != AVPC1_ATOMIC_READOUT_SCHEMA_VERSION
            or not all(_valid_digest(value) for value in source_digests)
            or type(self.relation_finding) is not AVPC1ReadOnlyRelationFinding
            or self.result_role != self.relation_finding.result_role
            or self.audio_only_envelope_digest
            != self.relation_finding.audio_only_envelope_digest
            or self.auditory_finding_digest
            != self.relation_finding.auditory_finding_digest
            or self.relation_state_identity_digest
            != self.relation_finding.relation_state_identity_digest
            or self.observed_relation_state_digest
            != self.relation_finding.observed_relation_state_digest
            or self.visual_bank_state_digest
            != self.relation_finding.frozen_visual_bank_state_digest
        ):
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                "outcome does not bind one complete relation finding",
            )
        if self.result_role == "MATCH":
            visual = self.visual_prototype_state
            if (
                type(visual) is not AVPC1ReadOnlyVisualPrototypeState
                or visual.relation_finding_digest
                != self.relation_finding.finding_digest
                or visual.relation_state_identity_digest
                != self.relation_state_identity_digest
                or visual.observed_relation_state_digest
                != self.observed_relation_state_digest
                or visual.profile_binding_digest != self.profile_binding_digest
                or visual.visual_bank_state_identity_digest
                != self.visual_bank_state_identity_digest
                or visual.visual_bank_state_digest != self.visual_bank_state_digest
                or visual.visual_prototype_identity_digest
                != self.relation_finding.visual_prototype_identity_digest
            ):
                raise AVPC1AtomicReadoutConsumerError(
                    AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                    "match outcome does not bind one exact visual state",
                )
        elif self.result_role in {"NO_MATCH", "NO_MATCH_CONFLICT"}:
            if (
                self.visual_prototype_state is not None
                or self.relation_finding.visual_prototype_identity_digest is not None
            ):
                raise AVPC1AtomicReadoutConsumerError(
                    AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                    "negative outcome must not contain a visual state",
                )
        else:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                "outcome result role is invalid",
            )
        object.__setattr__(self, "consumer_id", consumer_id)
        if self.outcome_digest != _digest(self.payload_without_digest()):
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
                "outcome digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        visual = self.visual_prototype_state
        return {
            "schema_version": self.schema_version,
            "contract_digest": AVPC1_ATOMIC_READOUT_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_ATOMIC_READOUT_PREFLIGHT_DIGEST,
            "consumer_id": self.consumer_id,
            "audio_only_envelope_digest": self.audio_only_envelope_digest,
            "auditory_finding_digest": self.auditory_finding_digest,
            "relation_state_identity_digest": self.relation_state_identity_digest,
            "observed_relation_state_digest": self.observed_relation_state_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "visual_bank_state_identity_digest": (
                self.visual_bank_state_identity_digest
            ),
            "visual_bank_state_digest": self.visual_bank_state_digest,
            "result_role": self.result_role,
            "relation_finding": _relation_finding_payload(
                self.relation_finding
            ),
            "visual_prototype_state": (
                None if visual is None else visual.canonical_payload()
            ),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "outcome_digest": self.outcome_digest,
        }


def _source_snapshot(
    envelope: AVPC1PrivateAuditoryOnlyProbeEnvelope,
    auditory_finding: S1WUReadOnlyPerceptualFinding,
    relation_state: AVPC1BoundedRelationState,
    visual_bank_state: PPB1BankState,
    profile: PPB1ReceptorProfileBinding,
) -> tuple[str, ...]:
    return (
        envelope.envelope_digest,
        auditory_finding.finding_digest,
        relation_state.state_identity_digest,
        relation_state.state_digest,
        relation_state.relation_history_partition_digest,
        profile.digest(),
        profile.auditory_config.digest(),
        profile.visual_config.digest(),
        _visual_bank_identity_digest(visual_bank_state),
        visual_bank_state.digest(),
    )


def _validate_initial_sources(
    envelope: AVPC1PrivateAuditoryOnlyProbeEnvelope,
    auditory_finding: S1WUReadOnlyPerceptualFinding,
    relation_state: AVPC1BoundedRelationState,
    visual_bank_state: PPB1BankState,
    profile: PPB1ReceptorProfileBinding,
) -> None:
    auditory_digest = profile.auditory_config.digest()
    visual_digest = profile.visual_config.digest()
    visual_identity = _visual_bank_identity_digest(visual_bank_state)
    if (
        profile.digest() != relation_state.profile_binding_digest
        or envelope.profile_id != profile.profile_id
        or envelope.profile_binding_digest != profile.digest()
        or envelope.parameter_digest != profile.parameter_digest
        or not auditory_finding.recognized
        or auditory_finding.modality_id != "auditory"
        or auditory_finding.probe_input_digest
        != envelope.auditory_input_projection_digest
        or auditory_finding.bank_config_digest != auditory_digest
        or auditory_finding.bank_config_digest
        != relation_state.auditory_bank_config_digest
        or auditory_finding.observed_bank_state_digest
        != envelope.auditory_bank_state_digest
        or auditory_finding.observed_bank_state_digest
        != relation_state.auditory_bank_state_digest
        or auditory_finding.state_identity_digest
        != envelope.auditory_bank_state_identity_digest
        or auditory_finding.state_identity_digest
        != relation_state.auditory_bank_state_identity_digest
        or auditory_finding.selected_prototype_digest is None
        or auditory_finding.selected_prototype_digest
        not in relation_state.auditory_prototype_inventory
        or envelope.auditory_bank_config_digest != auditory_digest
        or envelope.relation_history_partition_digest
        != relation_state.relation_history_partition_digest
        or relation_state.visual_bank_config_digest != visual_digest
        or visual_bank_state.config_digest != visual_digest
        or visual_identity != relation_state.visual_bank_state_identity_digest
        or visual_bank_state.digest() != relation_state.visual_bank_state_digest
    ):
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_SOURCE_MISMATCH,
            "consumer inputs do not bind one read-only AVPC-1 source set",
        )


def consume_avpc1_auditory_cued_visual_readout(
    consumer_id: str,
    relation_probe_id: str,
    visual_resolver_id: str,
    audio_only_envelope: AVPC1PrivateAuditoryOnlyProbeEnvelope,
    auditory_finding: S1WUReadOnlyPerceptualFinding,
    relation_state: AVPC1BoundedRelationState,
    visual_bank_state: PPB1BankState,
    profile: PPB1ReceptorProfileBinding,
) -> AVPC1AtomicAuditoryCuedVisualReadoutOutcome:
    """Return one complete read-only relation and optional visual state."""

    exact_inputs = (
        (audio_only_envelope, AVPC1PrivateAuditoryOnlyProbeEnvelope),
        (auditory_finding, S1WUReadOnlyPerceptualFinding),
        (relation_state, AVPC1BoundedRelationState),
        (visual_bank_state, PPB1BankState),
        (profile, PPB1ReceptorProfileBinding),
    )
    if not all(type(value) is expected for value, expected in exact_inputs):
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_INVALID_INPUT,
            "exact envelope, finding, relation, visual state and profile required",
        )
    consumer_id = _identifier(consumer_id, "consumer_id")
    relation_probe_id = _identifier(relation_probe_id, "relation_probe_id")
    visual_resolver_id = _identifier(visual_resolver_id, "visual_resolver_id")
    before = _source_snapshot(
        audio_only_envelope,
        auditory_finding,
        relation_state,
        visual_bank_state,
        profile,
    )
    _validate_initial_sources(
        audio_only_envelope,
        auditory_finding,
        relation_state,
        visual_bank_state,
        profile,
    )
    try:
        relation_finding = probe_avpc1_bounded_relation_read_only(
            relation_probe_id,
            audio_only_envelope,
            auditory_finding,
            relation_state,
            visual_bank_state,
            profile,
        )
    except AVPC1BoundedRelationError as exc:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_RELATION_FAILURE,
            exc.detail,
        ) from exc
    if (
        type(relation_finding) is not AVPC1ReadOnlyRelationFinding
        or relation_finding.probe_id != relation_probe_id
        or relation_finding.audio_only_envelope_digest
        != audio_only_envelope.envelope_digest
        or relation_finding.auditory_finding_digest
        != auditory_finding.finding_digest
        or relation_finding.relation_state_identity_digest
        != relation_state.state_identity_digest
        or relation_finding.observed_relation_state_digest
        != relation_state.state_digest
        or relation_finding.frozen_visual_bank_state_digest
        != visual_bank_state.digest()
    ):
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
            "relation child output does not bind the consumer attempt",
        )
    relation_slots = tuple(
        slot
        for slot in relation_state.slots
        if slot.auditory_key_digest
        == auditory_finding.selected_prototype_digest
    )
    if len(relation_slots) > 1:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
            "auditory key identifies multiple relation slots",
        )
    if not relation_slots:
        expected_relation = ("NO_MATCH", None, None)
    else:
        relation_slot = relation_slots[0]
        if relation_slot.status == "PENDING":
            expected_relation = ("NO_MATCH", relation_slot.slot_id, None)
        elif relation_slot.status == "CONFLICTED":
            expected_relation = (
                "NO_MATCH_CONFLICT",
                relation_slot.slot_id,
                None,
            )
        elif relation_slot.status == "STABLE":
            expected_relation = (
                "MATCH",
                relation_slot.slot_id,
                relation_slot.visual_target_digest,
            )
        else:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
                "auditory key identifies an invalid relation slot",
            )
    observed_relation = (
        relation_finding.result_role,
        relation_finding.selected_relation_slot_id,
        relation_finding.visual_prototype_identity_digest,
    )
    if observed_relation != expected_relation:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
            "relation child role, slot or target does not bind the source state",
        )
    if relation_finding.result_role == "MATCH":
        if relation_finding.visual_prototype_identity_digest is None:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
                "match relation has no visual target",
            )
        try:
            visual_state = resolve_avpc1_visual_prototype_state(
                visual_resolver_id,
                relation_finding,
                relation_state,
                profile,
                visual_bank_state,
            )
        except AVPC1VisualPrototypeResolverError as exc:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
                exc.detail,
            ) from exc
        if type(visual_state) is not AVPC1ReadOnlyVisualPrototypeState:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
                "visual child output has the wrong type",
            )
        visual_config = profile.visual_config
        matching_slots = tuple(
            slot
            for slot in visual_bank_state.slots
            if slot.slot_id == visual_state.visual_prototype_slot_id
        )
        if (
            visual_state.resolver_id != visual_resolver_id
            or visual_state.relation_finding_digest
            != relation_finding.finding_digest
            or visual_state.visual_prototype_identity_digest
            != relation_finding.visual_prototype_identity_digest
            or visual_state.relation_state_identity_digest
            != relation_state.state_identity_digest
            or visual_state.observed_relation_state_digest
            != relation_state.state_digest
            or visual_state.profile_binding_digest != profile.digest()
            or visual_state.visual_bank_config_digest != visual_config.digest()
            or visual_state.visual_bank_config_digest
            != relation_state.visual_bank_config_digest
            or visual_state.visual_bank_state_identity_digest
            != _visual_bank_identity_digest(visual_bank_state)
            or visual_state.visual_bank_state_digest
            != visual_bank_state.digest()
            or visual_state.modality_id != "visual"
            or visual_state.geometry_id != visual_config.geometry_id
            or visual_state.carrier_ids != visual_config.carrier_ids
            or len(matching_slots) != 1
        ):
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
                "visual child output does not bind the consumer attempt",
            )
        selected_slot = matching_slots[0]
        if (
            not selected_slot.occupied
            or selected_slot.support_count is None
            or selected_slot.support_count < visual_config.stable_after
            or selected_slot.prototype_values != visual_state.prototype_values
            or selected_slot.support_count != visual_state.support_count
        ):
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
                "visual child output does not bind the frozen stable bank slot",
            )
    elif relation_finding.result_role in {"NO_MATCH", "NO_MATCH_CONFLICT"}:
        if relation_finding.visual_prototype_identity_digest is not None:
            raise AVPC1AtomicReadoutConsumerError(
                AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
                "negative relation unexpectedly contains a visual target",
            )
        visual_state = None
    else:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
            "relation child output role is outside the contract",
        )
    values = {
        "consumer_id": consumer_id,
        "audio_only_envelope_digest": audio_only_envelope.envelope_digest,
        "auditory_finding_digest": auditory_finding.finding_digest,
        "relation_state_identity_digest": relation_state.state_identity_digest,
        "observed_relation_state_digest": relation_state.state_digest,
        "profile_binding_digest": profile.digest(),
        "visual_bank_state_identity_digest": _visual_bank_identity_digest(
            visual_bank_state
        ),
        "visual_bank_state_digest": visual_bank_state.digest(),
        "result_role": relation_finding.result_role,
        "relation_finding": relation_finding,
        "visual_prototype_state": visual_state,
    }
    payload = {
        "schema_version": AVPC1_ATOMIC_READOUT_SCHEMA_VERSION,
        "contract_digest": AVPC1_ATOMIC_READOUT_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_ATOMIC_READOUT_PREFLIGHT_DIGEST,
        **{
            key: (
                _relation_finding_payload(value)
                if key == "relation_finding"
                else None
                if key == "visual_prototype_state" and value is None
                else value.canonical_payload()
                if key == "visual_prototype_state"
                else value
            )
            for key, value in values.items()
        },
    }
    outcome = AVPC1AtomicAuditoryCuedVisualReadoutOutcome(
        **values,
        outcome_digest=_digest(payload),
    )
    after = _source_snapshot(
        audio_only_envelope,
        auditory_finding,
        relation_state,
        visual_bank_state,
        profile,
    )
    if after != before:
        raise AVPC1AtomicReadoutConsumerError(
            AVPC1_ATOMIC_READOUT_ATOMIC_RESULT_REQUIRED,
            "consumer source changed during atomic readout",
        )
    return outcome
