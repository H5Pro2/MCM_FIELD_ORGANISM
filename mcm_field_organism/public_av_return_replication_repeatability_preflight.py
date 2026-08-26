"""Locked execution preflight for three independent AV replication repeat slots."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from .public_av_return_permutation_contract import (
    PublicAVReturnPermutationContract,
    public_av_return_permutation_contract,
)
from .public_av_return_replication_preflight import (
    PublicAVReturnReplicationPreflight,
    audit_public_av_return_replication_preflight,
)
from .public_av_return_replication_repeatability_preregistration import (
    PublicAVReturnReplicationRepeatabilityPreregistration,
    public_av_return_replication_repeatability_preregistration,
)
from .public_av_return_replication_repeatability_runner import (
    PublicAVReturnReplicationRepeatabilityRunnerWiring,
    wire_public_av_return_replication_repeatability_runner,
)
from .public_av_return_replication_runner import (
    PublicAVReturnReplicationRunnerWiring,
    wire_public_av_return_replication_runner,
)
from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


class PublicAVReturnReplicationRepeatabilityPreflightError(ValueError):
    """Raised when repeatability preflight would release a repeat run."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatSlotPreflight:
    repeat_index: int
    slot_runner_id: str
    base_preflight_id: str
    positive_one_shot_release_available: bool
    one_shot_release_unconsumed: bool
    repeat_count_authorized: int
    media_path_matches: bool
    source_identity_matches: bool
    contract_parameters_identical: bool
    fresh_runner_instance_required: bool
    fresh_field_at_repeat_start: bool
    cross_repeat_state_carry_absent: bool
    prior_execution_receipt_reusable: bool
    executable: bool = False
    repeat_run_started: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in {1, 2, 3}:
            raise PublicAVReturnReplicationRepeatabilityPreflightError("repeat index must be preregistered")
        if self.repeat_count_authorized != 1:
            raise PublicAVReturnReplicationRepeatabilityPreflightError("each slot requires one authorized base run")
        required = (
            self.positive_one_shot_release_available,
            self.one_shot_release_unconsumed,
            self.media_path_matches,
            self.source_identity_matches,
            self.contract_parameters_identical,
            self.fresh_runner_instance_required,
            self.fresh_field_at_repeat_start,
            self.cross_repeat_state_carry_absent,
        )
        forbidden = (
            self.prior_execution_receipt_reusable,
            self.executable,
            self.repeat_run_started,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityPreflightError(
                "repeat slot preflight must remain fresh, unused, and non-executable"
            )


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatabilityPreflight:
    preflight_id: str
    repeatability_preregistration_id: str
    repeatability_runner_id: str
    source_id: str
    clock_id: str
    media_path: str
    source_audit_accepted: bool
    source_size_matches: bool
    source_sha1_matches: bool
    repeat_slot_preflights: tuple[PublicAVReturnReplicationRepeatSlotPreflight, ...]
    all_slots_have_separate_unconsumed_one_shot_release: bool
    identical_contract_parameters_across_slots: bool
    no_cross_repeat_state_carry: bool
    all_slots_non_executable: bool
    repeatability_preflight_complete: bool
    repeatability_run_allowed: bool
    automatic_repeat_loop_available: bool
    media_decode_allowed: bool
    receptor_feed_allowed: bool
    stability_threshold_defined: bool
    memory_threshold_defined: bool
    organization_threshold_defined: bool
    causal_mechanism_claim_allowed: bool
    memory_claim_allowed: bool
    meaning_claim_allowed: bool
    organization_claim_allowed: bool
    ai_claim_allowed: bool

    def __post_init__(self) -> None:
        slots = tuple(self.repeat_slot_preflights)
        if len(slots) != 3 or tuple(slot.repeat_index for slot in slots) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityPreflightError("three ordered slot preflights are required")
        required = (
            self.source_audit_accepted,
            self.source_size_matches,
            self.source_sha1_matches,
            self.all_slots_have_separate_unconsumed_one_shot_release,
            self.identical_contract_parameters_across_slots,
            self.no_cross_repeat_state_carry,
            self.all_slots_non_executable,
            self.repeatability_preflight_complete,
        )
        forbidden = (
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.media_decode_allowed,
            self.receptor_feed_allowed,
            self.stability_threshold_defined,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.causal_mechanism_claim_allowed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityPreflightError(
                "repeatability preflight cannot release loops, runs, thresholds, or claims"
            )
        object.__setattr__(self, "repeat_slot_preflights", slots)


def audit_public_av_return_replication_repeatability_preflight(
    path: Path,
    contract: PublicMediaSourceContract | None = None,
    *,
    source_audit: PublicMediaSourceAudit | None = None,
    preregistration: PublicAVReturnReplicationRepeatabilityPreregistration | None = None,
    repeatability_wiring: PublicAVReturnReplicationRepeatabilityRunnerWiring | None = None,
    base_wiring: PublicAVReturnReplicationRunnerWiring | None = None,
    permutation_contract: PublicAVReturnPermutationContract | None = None,
    slot_preflights: tuple[PublicAVReturnReplicationPreflight, ...] | None = None,
) -> PublicAVReturnReplicationRepeatabilityPreflight:
    """Audit three independent repeat slots without authorizing the repeatability run."""

    if not isinstance(path, Path):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("path must be a pathlib.Path")
    source_contract = contract or nasa_earthrise_av_source_contract()
    if not isinstance(source_contract, PublicMediaSourceContract):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("source contract is required")
    observed_source = source_audit or audit_public_media_source(path, source_contract)
    if not isinstance(observed_source, PublicMediaSourceAudit):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("source audit is required")
    plan = preregistration or public_av_return_replication_repeatability_preregistration()
    if not isinstance(plan, PublicAVReturnReplicationRepeatabilityPreregistration):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("repeatability preregistration is required")
    permutation = permutation_contract or public_av_return_permutation_contract()
    if not isinstance(permutation, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("permutation contract is required")
    base_runner = base_wiring or wire_public_av_return_replication_runner(permutation_contract=permutation)
    if not isinstance(base_runner, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("base runner wiring is required")
    repeatability_runner = repeatability_wiring or wire_public_av_return_replication_repeatability_runner(plan, base_runner)
    if not isinstance(repeatability_runner, PublicAVReturnReplicationRepeatabilityRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("repeatability runner wiring is required")
    preflights = slot_preflights or tuple(
        audit_public_av_return_replication_preflight(
            path,
            source_contract,
            source_audit=observed_source,
            permutation_contract=permutation,
            wiring=base_runner,
        )
        for _ in plan.repeat_index_set
    )
    if len(preflights) != 3 or not all(isinstance(item, PublicAVReturnReplicationPreflight) for item in preflights):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("three base preflights are required")

    slot_preflight_results = []
    for slot, base_preflight in zip(repeatability_runner.repeat_slots, preflights, strict=True):
        identical = (
            base_preflight.source_id == plan.source_id
            and base_preflight.media_path == str(path)
            and base_preflight.preregistration_id_matches
            and base_preflight.compatibility_audit_id_matches
            and base_preflight.permutation_contract_id_matches
            and base_preflight.permutation_contract_digest_matches
            and base_preflight.fixed_field_parameters_match_preregistration
            and tuple(base_preflight.field_parameter_roles) == tuple(slot.fixed_field_parameters)
            and slot.permutation_contract_digest == base_runner.permutation_contract_digest
        )
        slot_preflight_results.append(
            PublicAVReturnReplicationRepeatSlotPreflight(
                repeat_index=slot.repeat_index,
                slot_runner_id=slot.base_runner_id,
                base_preflight_id=base_preflight.preflight_id,
                positive_one_shot_release_available=base_preflight.single_bounded_replication_run_release_granted,
                one_shot_release_unconsumed=not base_preflight.field_run_started,
                repeat_count_authorized=base_preflight.repeat_count_authorized,
                media_path_matches=base_preflight.media_path == str(path),
                source_identity_matches=base_preflight.source_id == plan.source_id == slot.source_id,
                contract_parameters_identical=identical,
                fresh_runner_instance_required=slot.fresh_runner_instance_required,
                fresh_field_at_repeat_start=slot.fresh_field_at_repeat_start,
                cross_repeat_state_carry_absent=not slot.cross_repeat_state_carry_allowed,
                prior_execution_receipt_reusable=slot.prior_execution_receipt_reusable,
            )
        )

    return PublicAVReturnReplicationRepeatabilityPreflight(
        preflight_id="public.av.nasa-earthrise.return-replication.repeatability-preflight.v1",
        repeatability_preregistration_id=plan.preregistration_id,
        repeatability_runner_id=repeatability_runner.runner_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        media_path=str(path),
        source_audit_accepted=observed_source.accepted,
        source_size_matches=observed_source.size_matches,
        source_sha1_matches=observed_source.sha1_matches,
        repeat_slot_preflights=tuple(slot_preflight_results),
        all_slots_have_separate_unconsumed_one_shot_release=True,
        identical_contract_parameters_across_slots=True,
        no_cross_repeat_state_carry=True,
        all_slots_non_executable=True,
        repeatability_preflight_complete=True,
        repeatability_run_allowed=False,
        automatic_repeat_loop_available=False,
        media_decode_allowed=False,
        receptor_feed_allowed=False,
        stability_threshold_defined=False,
        memory_threshold_defined=False,
        organization_threshold_defined=False,
        causal_mechanism_claim_allowed=False,
        memory_claim_allowed=False,
        meaning_claim_allowed=False,
        organization_claim_allowed=False,
        ai_claim_allowed=False,
    )


def public_av_return_replication_repeatability_preflight_json_value(
    preflight: PublicAVReturnReplicationRepeatabilityPreflight,
) -> dict[str, object]:
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilityPreflight):
        raise PublicAVReturnReplicationRepeatabilityPreflightError("repeatability preflight is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(preflight)


def public_av_return_replication_repeatability_preflight_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationRepeatSlotPreflight, PublicAVReturnReplicationRepeatabilityPreflight)
        for item in fields(cls)
    )
