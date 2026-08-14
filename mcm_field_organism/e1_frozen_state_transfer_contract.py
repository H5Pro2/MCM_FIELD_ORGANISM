"""Private S1-DK static contract for bounded frozen-state AV transfer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_a0_av_history_evidence_audit import (
    S1_DJ_DECISION,
    audit_e1_a0_av_history_evidence,
)
from .e1_av_history_permutation import build_e1_av_history_permutation


class E1FrozenStateTransferContractError(ValueError):
    """Raised when the narrow S1-DK transfer boundary is changed."""


S1_DJ_AUDIT_DIGEST = (
    "29dfe21e71206bd00210528f30a725c1e9377476209e8933d1391cfab942115b"
)
S1_DK_B_AB_DIGEST = (
    "bf93d871f6352f82bf0b4d1a0f2cbdc0a577d0f27d03cbc34cbd57ccc2754f86"
)
S1_DK_B_BA_DIGEST = (
    "354d65d02435c31fcad31b182ae78fb3cce0c88180c3f0d9a847cc8e368eb014"
)
S1_DK_PROBE_DIGEST = (
    "c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d"
)
S1_DK_ARMS = ("p0", "ab0", "ba0", "ab1", "ba1", "abf", "baf")
S1_DK_METRICS = (
    "d_pre_s",
    "d_pre_h",
    "d_active_s",
    "d_active_h",
    "d_ablation",
    "d_fixed_adapter",
    "d_probe_partition",
    "frozen_state_change",
)
S1_DK_DECISIONS = (
    "TECHNICALLY_UNDECIDABLE",
    "NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
    "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
)
S1_DK_REQUIRED_IDENTITIES = (
    "all_prefields_value_identical_and_object_separate",
    "p0_equals_ab0_equals_ba0_bit_exact",
    "ab1_equals_abf_bit_exact",
    "ba1_equals_baf_bit_exact",
    "b_ab_and_b_ba_unchanged_during_probe",
    "all_110_probe_supports_assigned_once",
    "coarse_and_split_probe_use_identical_source",
    "public_api_unchanged",
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _frame_payload(item) -> dict[str, object]:
    frame = item.frame
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "snapshot_id": frame.snapshot_id,
        "source_clock_id": frame.clock_id,
        "source_start_tick": frame.window_start_tick,
        "source_end_tick": frame.window_end_tick,
        "carrier_ids": list(frame.carrier_ids),
        "values": list(frame.values),
    }


def _probe_digest(sequences) -> str:
    return _digest(
        [
            {
                "modality_id": sequence.modality_id,
                "geometry_id": sequence.geometry_id,
                "clock_id": sequence.clock_id,
                "frames": [
                    {
                        "frame": _frame_payload(item),
                        "field_time": [
                            item.field_time.clock_id,
                            item.field_time.window_start_tick,
                            item.field_time.window_end_tick,
                        ],
                    }
                    for item in sequence.frames
                ],
            }
            for sequence in sequences
        ]
    )


def _fixed_probe_sequences():
    source = build_e1_av_history_permutation().history_ab
    result = []
    for sequence in source:
        frames = tuple(
            item
            for item in sequence.frames
            if item.field_time.window_end_tick <= 1_000_000
        )
        result.append(
            type(sequence)(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                frames,
            )
        )
    return tuple(result)


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferContract:
    contract_id: str
    evidence_decision: str
    evidence_audit_digest: str
    history_report_sha256: str
    history_result_sha256: str
    b_ab_digest: str
    b_ba_digest: str
    probe_digest: str
    probe_clock_id: str
    probe_start_tick: int
    probe_end_tick: int
    ticks_per_second: float
    auditory_frame_count: int
    visual_frame_count: int
    source_support_count: int
    field_node_count: int
    edge_count: int
    arms: tuple[str, ...]
    metrics: tuple[str, ...]
    decisions: tuple[str, ...]
    required_identities: tuple[str, ...]
    proposal_partitions: tuple[tuple[str, tuple[int, ...]], ...]
    response_time_seconds: float
    afterimage_time_constant_seconds: float
    backreaction_gain: float
    implementation_permitted: bool
    probe_execution_permitted: bool
    full_s1_dc_decision_permitted: bool
    history_cause_claim_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.contract_id != "e1.frozen-state-transfer.s1dk.v1":
            raise E1FrozenStateTransferContractError(
                "S1-DK contract identity changed"
            )
        if (
            self.evidence_decision != S1_DJ_DECISION
            or self.evidence_audit_digest != S1_DJ_AUDIT_DIGEST
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DJ evidence binding changed"
            )
        expected_digests = (
            S1_DK_B_AB_DIGEST,
            S1_DK_B_BA_DIGEST,
            S1_DK_PROBE_DIGEST,
        )
        if (self.b_ab_digest, self.b_ba_digest, self.probe_digest) != expected_digests:
            raise E1FrozenStateTransferContractError(
                "S1-DK state or probe digest changed"
            )
        if (
            self.probe_clock_id != "organism.e1.av-history"
            or self.probe_start_tick != 0
            or self.probe_end_tick != 1_000_000
            or self.ticks_per_second != 1_000_000.0
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DK probe time contract changed"
            )
        if (
            self.auditory_frame_count != 100
            or self.visual_frame_count != 10
            or self.source_support_count != 110
            or self.field_node_count != 84
            or self.edge_count != 145
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DK source or geometry inventory changed"
            )
        if self.arms != S1_DK_ARMS or self.metrics != S1_DK_METRICS:
            raise E1FrozenStateTransferContractError(
                "S1-DK arm or metric boundary changed"
            )
        if (
            self.decisions != S1_DK_DECISIONS
            or self.required_identities != S1_DK_REQUIRED_IDENTITIES
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DK decision or identity boundary changed"
            )
        if self.proposal_partitions != (
            ("coarse", (0, 1_000_000)),
            ("split", (0, 500_000, 1_000_000)),
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DK probe partition contract changed"
            )
        if (
            self.response_time_seconds != 1.0
            or self.afterimage_time_constant_seconds != 0.5
            or self.backreaction_gain != 0.5
        ):
            raise E1FrozenStateTransferContractError(
                "S1-DK field or adapter configuration changed"
            )
        if self.implementation_permitted is not True:
            raise E1FrozenStateTransferContractError(
                "S1-DK must permit only the next implementation"
            )
        forbidden = (
            self.probe_execution_permitted,
            self.full_s1_dc_decision_permitted,
            self.history_cause_claim_permitted,
            self.memory_claim_permitted,
            self.semantic_claim_permitted,
            self.organization_claim_permitted,
            self.topology_claim_permitted,
            self.self_regulation_claim_permitted,
            self.ai_claim_permitted,
        )
        if any(value is not False for value in forbidden):
            raise E1FrozenStateTransferContractError(
                "S1-DK cannot release a probe run or strong claim"
            )
        for role in (
            "evidence_audit_digest",
            "history_report_sha256",
            "history_result_sha256",
            "b_ab_digest",
            "b_ba_digest",
            "probe_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1FrozenStateTransferContractError(f"{role} is not SHA-256")

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def build_e1_frozen_state_transfer_contract(
    history_report_path: Path,
) -> E1FrozenStateTransferContract:
    """Bind states and probe source without invoking a field or probe role."""

    report_path = Path(history_report_path)
    evidence = audit_e1_a0_av_history_evidence(report_path)
    if evidence.audit_digest != S1_DJ_AUDIT_DIGEST:
        raise E1FrozenStateTransferContractError("S1-DJ audit digest changed")
    report = json.loads(report_path.read_text(encoding="ascii"))
    result = report["result"]
    b_ab_digest = _digest(result["b_ab"])
    b_ba_digest = _digest(result["b_ba"])
    if (b_ab_digest, b_ba_digest) != (
        S1_DK_B_AB_DIGEST,
        S1_DK_B_BA_DIGEST,
    ):
        raise E1FrozenStateTransferContractError(
            "published E1 state digest changed"
        )
    probe = _fixed_probe_sequences()
    probe_digest = _probe_digest(probe)
    if probe_digest != S1_DK_PROBE_DIGEST:
        raise E1FrozenStateTransferContractError(
            "fixed reduced AV probe digest changed"
        )
    return E1FrozenStateTransferContract(
        contract_id="e1.frozen-state-transfer.s1dk.v1",
        evidence_decision=evidence.decision,
        evidence_audit_digest=evidence.audit_digest,
        history_report_sha256=evidence.report_sha256,
        history_result_sha256=evidence.result_sha256,
        b_ab_digest=b_ab_digest,
        b_ba_digest=b_ba_digest,
        probe_digest=probe_digest,
        probe_clock_id="organism.e1.av-history",
        probe_start_tick=0,
        probe_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
        auditory_frame_count=len(probe[0].frames),
        visual_frame_count=len(probe[1].frames),
        source_support_count=sum(len(item.frames) for item in probe),
        field_node_count=84,
        edge_count=evidence.edge_count,
        arms=S1_DK_ARMS,
        metrics=S1_DK_METRICS,
        decisions=S1_DK_DECISIONS,
        required_identities=S1_DK_REQUIRED_IDENTITIES,
        proposal_partitions=(
            ("coarse", (0, 1_000_000)),
            ("split", (0, 500_000, 1_000_000)),
        ),
        response_time_seconds=1.0,
        afterimage_time_constant_seconds=0.5,
        backreaction_gain=0.5,
        implementation_permitted=True,
        probe_execution_permitted=False,
        full_s1_dc_decision_permitted=False,
        history_cause_claim_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
