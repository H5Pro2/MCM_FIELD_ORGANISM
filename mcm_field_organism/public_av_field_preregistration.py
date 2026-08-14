"""Fixed preregistration for a bounded passive public AV field comparison."""

from __future__ import annotations

from dataclasses import dataclass, fields


class PublicAVFieldPreregistrationError(ValueError):
    """Raised when a preregistration would authorize or bias a field result."""


@dataclass(frozen=True, slots=True)
class PublicAVFieldArmPlan:
    arm_id: str
    included_modalities: tuple[str, ...]
    partition_id: str
    reverse_sequence_declaration: bool
    fresh_field_required: bool

    def __post_init__(self) -> None:
        if not self.arm_id:
            raise PublicAVFieldPreregistrationError("arm_id must be non-empty")
        modalities = tuple(self.included_modalities)
        if any(item not in {"auditory", "visual"} for item in modalities):
            raise PublicAVFieldPreregistrationError("invalid included modality")
        if not modalities:
            raise PublicAVFieldPreregistrationError("every arm requires source support")
        if len(set(modalities)) != len(modalities):
            raise PublicAVFieldPreregistrationError("modalities must be unique")
        if self.partition_id not in {"coarse", "completion_fine"}:
            raise PublicAVFieldPreregistrationError("invalid partition_id")
        if not isinstance(self.reverse_sequence_declaration, bool) or not isinstance(
            self.fresh_field_required, bool
        ):
            raise PublicAVFieldPreregistrationError("arm flags must be boolean")
        if not self.fresh_field_required:
            raise PublicAVFieldPreregistrationError("every arm requires a fresh field")
        object.__setattr__(self, "included_modalities", modalities)


@dataclass(frozen=True, slots=True)
class PublicAVFieldPreregistration:
    preregistration_id: str
    source_id: str
    clock_id: str
    duration_limit_ticks: int
    auditory_input_digest: str
    visual_input_digest: str
    arms: tuple[PublicAVFieldArmPlan, ...]
    measured_roles: tuple[str, ...]
    required_invariants: tuple[str, ...]
    preregistration_complete: bool
    field_runner_implementation_allowed: bool = False
    field_run_allowed: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.preregistration_id or not self.source_id or not self.clock_id:
            raise PublicAVFieldPreregistrationError("technical identities are required")
        if self.duration_limit_ticks != 500_000_000:
            raise PublicAVFieldPreregistrationError("duration must remain fixed at 0.5 seconds")
        for digest in (self.auditory_input_digest, self.visual_input_digest):
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise PublicAVFieldPreregistrationError("input digests must be SHA-256")
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != len(arms):
            raise PublicAVFieldPreregistrationError("exactly six unique arms are required")
        expected = {
            "joint.coarse",
            "joint.fine",
            "joint.fine.reproduction",
            "joint.fine.permuted",
            "auditory_only.fine",
            "visual_only.fine",
        }
        if {arm.arm_id for arm in arms} != expected:
            raise PublicAVFieldPreregistrationError("required comparison arms are incomplete")
        if not self.measured_roles or not self.required_invariants:
            raise PublicAVFieldPreregistrationError("measurements and invariants are required")
        forbidden = {
            "label",
            "meaning",
            "reward",
            "target_topology",
            "desired_response",
        }
        if forbidden.intersection(self.measured_roles):
            raise PublicAVFieldPreregistrationError("content-directed measurements are forbidden")
        release_roles = (
            "field_runner_implementation_allowed",
            "field_run_allowed",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        )
        if not self.preregistration_complete or any(getattr(self, role) for role in release_roles):
            raise PublicAVFieldPreregistrationError(
                "preregistration cannot release implementation, runs, or claims"
            )
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))


def public_av_passive_field_preregistration() -> PublicAVFieldPreregistration:
    joint = ("auditory", "visual")
    arms = (
        PublicAVFieldArmPlan("joint.coarse", joint, "coarse", False, True),
        PublicAVFieldArmPlan("joint.fine", joint, "completion_fine", False, True),
        PublicAVFieldArmPlan(
            "joint.fine.reproduction", joint, "completion_fine", False, True
        ),
        PublicAVFieldArmPlan("joint.fine.permuted", joint, "completion_fine", True, True),
        PublicAVFieldArmPlan(
            "auditory_only.fine", ("auditory",), "completion_fine", False, True
        ),
        PublicAVFieldArmPlan(
            "visual_only.fine", ("visual",), "completion_fine", False, True
        ),
    )
    return PublicAVFieldPreregistration(
        preregistration_id="public.av.nasa-earthrise.passive-field.v1",
        source_id="public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
        clock_id="public.media.pts_ns",
        duration_limit_ticks=500_000_000,
        auditory_input_digest=(
            "501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f"
        ),
        visual_input_digest=(
            "86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93"
        ),
        arms=arms,
        measured_roles=(
            "source_event_count",
            "completion_group_count",
            "mixed_completion_group_count",
            "proposal_step_count",
            "final_completion_tick",
            "activation_vector",
            "afterimage_vector",
            "activation_linf_between_arms",
            "afterimage_linf_between_arms",
            "layer_digest",
            "snapshot_digest",
        ),
        required_invariants=(
            "fresh_identical_field_per_arm",
            "identical_field_parameters_per_arm",
            "identical_dock_geometry_per_arm",
            "no_initial_field_carryover",
            "no_receptor_or_field_feedback",
            "no_metadata_input",
            "no_raw_payload_output",
            "no_post_hoc_arm_or_measurement_change",
        ),
        preregistration_complete=True,
    )


def public_av_field_preregistration_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVFieldArmPlan, PublicAVFieldPreregistration)
        for item in fields(cls)
    )
