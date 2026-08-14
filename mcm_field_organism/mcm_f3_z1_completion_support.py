"""Completion-group decision support for the corrected Z1 Lauf 196 path."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .mcm_f3_z1_runner import MCMF3Z1TechnicalPacket
from .mcm_f3_z1_source import build_mcm_f3_z1_source
from .mcm_f3_z1_trajectory import MCMF3Z1Trajectory


class MCMF3Z1CompletionSupportError(ValueError):
    """Raised when decision support differs from fixed receptor completions."""


_ARM_IDS = (
    "a.reference",
    "a.partitioned",
    "a.stretched",
    "a.compressed",
    "a.reversed",
    "a.permuted",
    "b.independent",
)


@dataclass(frozen=True, slots=True)
class MCMF3Z1CompletionSupportArm:
    arm_id: str
    required_ticks: tuple[int, ...]
    full_sample_count: int
    decision_sample_count: int
    full_support_unchanged: bool

    def __post_init__(self) -> None:
        if self.arm_id not in _ARM_IDS:
            raise MCMF3Z1CompletionSupportError("unknown Z1 completion-support arm")
        if (
            len(self.required_ticks) < 2
            or self.required_ticks[0] != 0
            or any(
                later <= earlier
                for earlier, later in zip(self.required_ticks, self.required_ticks[1:])
            )
        ):
            raise MCMF3Z1CompletionSupportError("completion-support ticks are not ordered")
        if self.decision_sample_count != len(self.required_ticks):
            raise MCMF3Z1CompletionSupportError("decision support count changed")
        if self.full_sample_count < self.decision_sample_count:
            raise MCMF3Z1CompletionSupportError("decision support exceeds full trajectory")


@dataclass(frozen=True, slots=True)
class MCMF3Z1CompletionSupportAudit:
    support_id: str
    packet: MCMF3Z1TechnicalPacket
    arms: tuple[MCMF3Z1CompletionSupportArm, ...]
    controls: tuple[tuple[str, bool], ...]

    def __post_init__(self) -> None:
        if self.support_id != "mcm.f3.z1.completion-support.v1":
            raise MCMF3Z1CompletionSupportError("Z1 completion-support identity changed")
        if not isinstance(self.packet, MCMF3Z1TechnicalPacket):
            raise MCMF3Z1CompletionSupportError("completion support requires one packet")
        if tuple(item.arm_id for item in self.arms) != _ARM_IDS:
            raise MCMF3Z1CompletionSupportError("completion-support arm inventory changed")
        if tuple(name for name, _ in self.controls) != (
            "source_contracts_match",
            "all_required_ticks_present",
            "reference_partition_support_equal",
            "nonpartition_support_unchanged",
            "partition_empty_support_removed",
        ):
            raise MCMF3Z1CompletionSupportError("completion-support controls changed")


def mcm_f3_z1_completion_ticks(arm_id: str) -> tuple[int, ...]:
    """Return neutral start plus every fixed real receptor completion tick."""

    source = build_mcm_f3_z1_source()
    arm = source.arm(arm_id)
    audit = audit_asynchronous_receptor_events(arm.sequences)
    ticks = (arm.start_tick,) + tuple(
        item.completion_tick for item in audit.completion_groups
    )
    if len(ticks) != arm.completion_group_count + 1:
        raise MCMF3Z1CompletionSupportError("completion tick inventory changed")
    return ticks


def select_mcm_f3_z1_completion_support(
    trajectory: MCMF3Z1Trajectory,
    required_ticks: tuple[int, ...],
) -> MCMF3Z1Trajectory:
    """Select exact preregistered ticks without interpolation or value tests."""

    if not isinstance(trajectory, MCMF3Z1Trajectory):
        raise MCMF3Z1CompletionSupportError("support selection requires a trajectory")
    ticks = tuple(required_ticks)
    if len(set(ticks)) != len(ticks):
        raise MCMF3Z1CompletionSupportError("required support ticks must be unique")
    by_tick = {item.tick: item for item in trajectory.samples}
    missing = tuple(tick for tick in ticks if tick not in by_tick)
    if missing:
        raise MCMF3Z1CompletionSupportError(
            f"trajectory lacks required completion ticks: {missing[:3]}"
        )
    return MCMF3Z1Trajectory(tuple(by_tick[tick] for tick in ticks))


def apply_mcm_f3_z1_completion_support(
    packet: MCMF3Z1TechnicalPacket,
) -> MCMF3Z1CompletionSupportAudit:
    """Project a full technical packet onto source-defined decision support."""

    if not isinstance(packet, MCMF3Z1TechnicalPacket):
        raise MCMF3Z1CompletionSupportError("completion support requires one packet")
    source = build_mcm_f3_z1_source()
    expected_digests = tuple(
        (item.arm_id, item.execution_digest) for item in source.arms
    )
    source_contracts_match = packet.source_execution_digests == expected_digests
    required_by_arm = {
        arm.arm_id: mcm_f3_z1_completion_ticks(arm.arm_id) for arm in source.arms
    }
    projected = []
    all_required_ticks_present = True
    for item in packet.trajectories:
        try:
            decision = select_mcm_f3_z1_completion_support(
                item.trajectory,
                required_by_arm[item.arm_id],
            )
        except MCMF3Z1CompletionSupportError:
            all_required_ticks_present = False
            raise
        projected.append(replace(item, trajectory=decision))
    projected_packet = MCMF3Z1TechnicalPacket(
        packet.preregistration_id,
        packet.base_layer_digest,
        packet.source_execution_digests,
        tuple(projected),
        packet.controls,
    )

    arm_audits = []
    for arm_id in _ARM_IDS:
        original_items = tuple(item for item in packet.trajectories if item.arm_id == arm_id)
        projected_items = tuple(
            item for item in projected_packet.trajectories if item.arm_id == arm_id
        )
        full_counts = {len(item.trajectory.samples) for item in original_items}
        decision_counts = {len(item.trajectory.samples) for item in projected_items}
        if len(full_counts) != 1 or len(decision_counts) != 1:
            raise MCMF3Z1CompletionSupportError("support count differs between tasks")
        full_count = next(iter(full_counts))
        decision_count = next(iter(decision_counts))
        arm_audits.append(
            MCMF3Z1CompletionSupportArm(
                arm_id,
                required_by_arm[arm_id],
                full_count,
                decision_count,
                all(
                    before.trajectory == after.trajectory
                    for before, after in zip(original_items, projected_items, strict=True)
                ),
            )
        )
    by_arm = {item.arm_id: item for item in arm_audits}
    reference_partition_equal = (
        by_arm["a.reference"].required_ticks
        == by_arm["a.partitioned"].required_ticks
        and by_arm["a.reference"].decision_sample_count
        == by_arm["a.partitioned"].decision_sample_count
        == 92
    )
    nonpartition_unchanged = all(
        item.full_support_unchanged
        for item in arm_audits
        if item.arm_id != "a.partitioned"
    )
    partition_removed = (
        by_arm["a.partitioned"].full_sample_count == 183
        and by_arm["a.partitioned"].decision_sample_count == 92
        and not by_arm["a.partitioned"].full_support_unchanged
    )
    return MCMF3Z1CompletionSupportAudit(
        "mcm.f3.z1.completion-support.v1",
        projected_packet,
        tuple(arm_audits),
        (
            ("source_contracts_match", source_contracts_match),
            ("all_required_ticks_present", all_required_ticks_present),
            ("reference_partition_support_equal", reference_partition_equal),
            ("nonpartition_support_unchanged", nonpartition_unchanged),
            ("partition_empty_support_removed", partition_removed),
        ),
    )


def mcm_f3_z1_completion_support_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3Z1CompletionSupportArm, MCMF3Z1CompletionSupportAudit)
        for item in fields(cls)
    )
