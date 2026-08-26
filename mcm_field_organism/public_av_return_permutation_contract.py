"""Observer-side contract for the public AV replication permutation arm."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .public_av_return_replication_preregistration import (
    PublicAVReturnReplicationPreregistration,
    public_av_return_replication_preregistration,
)


class PublicAVReturnPermutationContractError(ValueError):
    """Raised when the permutation arm is not fully specified."""


@dataclass(frozen=True, slots=True)
class PublicAVModalityPermutationMapping:
    modality_id: str
    frame_count: int
    mapping_id: str
    source_rank_to_time_slot_rank: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.modality_id not in {"auditory", "visual"}:
            raise PublicAVReturnPermutationContractError("invalid modality")
        if self.frame_count not in {41, 15}:
            raise PublicAVReturnPermutationContractError("unexpected frame count")
        mapping = tuple(self.source_rank_to_time_slot_rank)
        if len(mapping) != self.frame_count:
            raise PublicAVReturnPermutationContractError("mapping length must match frame count")
        if set(mapping) != set(range(self.frame_count)):
            raise PublicAVReturnPermutationContractError("mapping must be bijective")
        if mapping != tuple(reversed(range(self.frame_count))):
            raise PublicAVReturnPermutationContractError("permutation must be deterministic rank reversal")
        if self.mapping_id != f"{self.modality_id}.reverse_rank.v1":
            raise PublicAVReturnPermutationContractError("mapping_id changed")
        object.__setattr__(self, "source_rank_to_time_slot_rank", mapping)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "frame_count": self.frame_count,
            "mapping_id": self.mapping_id,
            "source_rank_to_time_slot_rank": list(self.source_rank_to_time_slot_rank),
        }


@dataclass(frozen=True, slots=True)
class PublicAVPermutationEventTimeContract:
    clock_id: str
    stage_two_interval_ticks: tuple[int, int]
    stage_two_tick_offset: int
    time_slot_rule: str
    overlap_policy: str

    def __post_init__(self) -> None:
        if self.clock_id != "public.media.pts_ns":
            raise PublicAVReturnPermutationContractError("clock_id changed")
        if self.stage_two_interval_ticks != (600_000_000, 1_100_000_000):
            raise PublicAVReturnPermutationContractError("stage-two interval changed")
        if self.stage_two_tick_offset != 600_000_000:
            raise PublicAVReturnPermutationContractError("stage-two tick offset changed")
        if self.time_slot_rule != "preserve_original_sorted_time_slots_per_modality":
            raise PublicAVReturnPermutationContractError("time-slot rule changed")
        if self.overlap_policy != "no_new_overlap_no_time_jitter_no_resampling":
            raise PublicAVReturnPermutationContractError("overlap policy changed")
        object.__setattr__(self, "stage_two_interval_ticks", tuple(self.stage_two_interval_ticks))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "clock_id": self.clock_id,
            "stage_two_interval_ticks": list(self.stage_two_interval_ticks),
            "stage_two_tick_offset": self.stage_two_tick_offset,
            "time_slot_rule": self.time_slot_rule,
            "overlap_policy": self.overlap_policy,
        }


@dataclass(frozen=True, slots=True)
class PublicAVReturnPermutationContract:
    contract_id: str
    preregistration_id: str
    arm_id: str
    source_sequence_id: str
    permuted_sequence_id: str
    source_stage_sequence_digest: tuple[str, str]
    modality_mappings: tuple[PublicAVModalityPermutationMapping, ...]
    event_time_contract: PublicAVPermutationEventTimeContract
    auditory_permuted_sequence_digest: str
    visual_permuted_sequence_digest: str
    contract_digest: str
    fully_specified: bool
    runner_implementation_allowed: bool = False
    replication_run_allowed: bool = False
    artificial_media_events_introduced: bool = False
    field_parameters_changed: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.arm_id != "control.stage_two_order_permuted":
            raise PublicAVReturnPermutationContractError("contract is only for the permuted arm")
        if self.source_sequence_id != "public.av.nasa-earthrise.0p5s.reduced.v1":
            raise PublicAVReturnPermutationContractError("source sequence changed")
        if self.permuted_sequence_id != "public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1":
            raise PublicAVReturnPermutationContractError("permuted sequence changed")
        mappings = tuple(self.modality_mappings)
        if {item.modality_id for item in mappings} != {"auditory", "visual"}:
            raise PublicAVReturnPermutationContractError("auditory and visual mappings are required")
        for digest in (
            *self.source_stage_sequence_digest,
            self.auditory_permuted_sequence_digest,
            self.visual_permuted_sequence_digest,
            self.contract_digest,
        ):
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise PublicAVReturnPermutationContractError("all contract digests must be SHA-256")
        if not self.fully_specified:
            raise PublicAVReturnPermutationContractError("permutation contract must be complete")
        forbidden = (
            self.runner_implementation_allowed,
            self.replication_run_allowed,
            self.artificial_media_events_introduced,
            self.field_parameters_changed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnPermutationContractError(
                "permutation contract cannot release runner, run, events, parameters, or claims"
            )
        object.__setattr__(self, "source_stage_sequence_digest", tuple(self.source_stage_sequence_digest))
        object.__setattr__(self, "modality_mappings", mappings)

    def canonical_payload(self, *, include_digests: bool = True) -> dict[str, object]:
        payload = {
            "contract_id": self.contract_id,
            "preregistration_id": self.preregistration_id,
            "arm_id": self.arm_id,
            "source_sequence_id": self.source_sequence_id,
            "permuted_sequence_id": self.permuted_sequence_id,
            "source_stage_sequence_digest": list(self.source_stage_sequence_digest),
            "modality_mappings": [item.canonical_payload() for item in self.modality_mappings],
            "event_time_contract": self.event_time_contract.canonical_payload(),
        }
        if include_digests:
            payload.update(
                {
                    "auditory_permuted_sequence_digest": self.auditory_permuted_sequence_digest,
                    "visual_permuted_sequence_digest": self.visual_permuted_sequence_digest,
                    "contract_digest": self.contract_digest,
                }
            )
        return payload


def _sha256(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _permuted_digest(
    source_digest: str,
    mapping: PublicAVModalityPermutationMapping,
    event_time: PublicAVPermutationEventTimeContract,
) -> str:
    return _sha256(
        {
            "source_digest": source_digest,
            "mapping": mapping.canonical_payload(),
            "event_time_contract": event_time.canonical_payload(),
        }
    )


def public_av_return_permutation_contract(
    preregistration: PublicAVReturnReplicationPreregistration | None = None,
) -> PublicAVReturnPermutationContract:
    plan = preregistration or public_av_return_replication_preregistration()
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnPermutationContractError("replication preregistration is required")
    auditory = PublicAVModalityPermutationMapping(
        "auditory",
        41,
        "auditory.reverse_rank.v1",
        tuple(reversed(range(41))),
    )
    visual = PublicAVModalityPermutationMapping(
        "visual",
        15,
        "visual.reverse_rank.v1",
        tuple(reversed(range(15))),
    )
    event_time = PublicAVPermutationEventTimeContract(
        "public.media.pts_ns",
        (600_000_000, 1_100_000_000),
        600_000_000,
        "preserve_original_sorted_time_slots_per_modality",
        "no_new_overlap_no_time_jitter_no_resampling",
    )
    auditory_digest = _permuted_digest(plan.stage_sequence_digest[0], auditory, event_time)
    visual_digest = _permuted_digest(plan.stage_sequence_digest[1], visual, event_time)
    base_payload = {
        "contract_id": "public.av.nasa-earthrise.return-replication.permutation-contract.v1",
        "preregistration_id": plan.preregistration_id,
        "arm_id": "control.stage_two_order_permuted",
        "source_sequence_id": "public.av.nasa-earthrise.0p5s.reduced.v1",
        "permuted_sequence_id": "public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1",
        "source_stage_sequence_digest": list(plan.stage_sequence_digest),
        "modality_mappings": [auditory.canonical_payload(), visual.canonical_payload()],
        "event_time_contract": event_time.canonical_payload(),
        "auditory_permuted_sequence_digest": auditory_digest,
        "visual_permuted_sequence_digest": visual_digest,
    }
    return PublicAVReturnPermutationContract(
        contract_id=base_payload["contract_id"],
        preregistration_id=plan.preregistration_id,
        arm_id="control.stage_two_order_permuted",
        source_sequence_id="public.av.nasa-earthrise.0p5s.reduced.v1",
        permuted_sequence_id="public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1",
        source_stage_sequence_digest=plan.stage_sequence_digest,
        modality_mappings=(auditory, visual),
        event_time_contract=event_time,
        auditory_permuted_sequence_digest=auditory_digest,
        visual_permuted_sequence_digest=visual_digest,
        contract_digest=_sha256(base_payload),
        fully_specified=True,
    )


def public_av_return_permutation_contract_json_value(
    contract: PublicAVReturnPermutationContract,
) -> dict[str, object]:
    if not isinstance(contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnPermutationContractError("permutation contract is required")
    return contract.canonical_payload()


def public_av_return_permutation_contract_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            PublicAVModalityPermutationMapping,
            PublicAVPermutationEventTimeContract,
            PublicAVReturnPermutationContract,
        )
        for item in fields(cls)
    )
