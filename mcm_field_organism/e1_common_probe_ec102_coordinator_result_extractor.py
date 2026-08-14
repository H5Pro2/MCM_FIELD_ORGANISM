"""S1-EC102 fail-closed extraction from completed coordinators into EC100."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
)
from .e1_common_probe_ec100_atomic_vector_handoff import (
    E1CommonProbeEC100AtomicVectorHandoffResult,
    build_e1_common_probe_ec100_atomic_vector_handoff,
    build_e1_common_probe_ec100_source_bundle,
)
from .e1_common_probe_ec101_coordinator_integration_gate import (
    E1CommonProbeEC101CoordinatorIntegrationGate,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC102CoordinatorResultExtractorError(ValueError):
    """Raised when completed coordinator results cannot safely enter EC100."""


S1_EC102_EXTRACTOR_ID = "e1.common-probe-coordinator-result-extractor.s1ec102.v1"
S1_EC102_EC101_DECISION = (
    "COORDINATOR_OUTPUTS_COMPATIBLE_EC100_INTEGRATION_GATE_CLOSED"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC102CoordinatorResultExtraction:
    extractor_id: str
    source_gate_digest: str
    r2_result_digest: str
    r4_r8_result_digest: str
    source_result_digests: tuple[str, ...]
    extracted_refinement_ids: tuple[str, ...]
    extracted_probe_counts: tuple[tuple[str, int], ...]
    extracted_probe_receipt_digests: tuple[str, ...]
    source_accounted_field_steps: int
    all_source_results_complete: bool
    all_probe_objects_distinct: bool
    all_probe_receipts_distinct: bool
    exact_role_order: bool
    same_objects_forwarded_to_ec100: bool
    ec100_handoff_digest: str
    extractor_field_steps_executed: int
    persistence_performed: bool
    retry_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    result_digest: str
    gate: E1CommonProbeEC101CoordinatorIntegrationGate = field(
        repr=False, compare=False
    )
    r2_result: E1CommonProbeN2R2RealModeCoordinatorResult = field(
        repr=False, compare=False
    )
    r4_r8_result: E1CommonProbeEC96AtomicResult = field(
        repr=False, compare=False
    )
    ec100_handoff: E1CommonProbeEC100AtomicVectorHandoffResult = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "result_digest",
                "gate",
                "r2_result",
                "r4_r8_result",
                "ec100_handoff",
            }
        }
        probes = (
            *self.r2_result.probes,
            *(probe for refinement in self.r4_r8_result.refinements for probe in refinement.probes),
        )
        if (
            self.extractor_id != S1_EC102_EXTRACTOR_ID
            or self.source_gate_digest != self.gate.gate_digest
            or self.gate.decision != S1_EC102_EC101_DECISION
            or self.r2_result_digest != self.r2_result.result_digest
            or self.r4_r8_result_digest != self.r4_r8_result.result_digest
            or self.source_result_digests
            != (self.r2_result.result_digest, self.r4_r8_result.result_digest)
            or self.extracted_refinement_ids != ("r2", "r4", "r8")
            or self.extracted_probe_counts != (("r2", 8), ("r4", 8), ("r8", 8))
            or self.extracted_probe_receipt_digests
            != tuple(item.receipt_digest for item in probes)
            or self.source_accounted_field_steps != 22456
            or any(
                value is not True
                for value in (
                    self.all_source_results_complete,
                    self.all_probe_objects_distinct,
                    self.all_probe_receipts_distinct,
                    self.exact_role_order,
                    self.same_objects_forwarded_to_ec100,
                )
            )
            or self.ec100_handoff_digest != self.ec100_handoff.result_digest
            or tuple(self.ec100_handoff.source_bundle.r2_probes)
            != tuple(self.r2_result.probes)
            or tuple(self.ec100_handoff.source_bundle.r4_r8_probes)
            != tuple(probes[8:])
            or any(
                forwarded is not original
                for forwarded, original in zip(
                    (
                        *self.ec100_handoff.source_bundle.r2_probes,
                        *self.ec100_handoff.source_bundle.r4_r8_probes,
                    ),
                    probes,
                    strict=True,
                )
            )
            or self.extractor_field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.retry_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status != "COORDINATOR_RESULTS_EXTRACTED_TO_EC100_NO_EXECUTION"
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC102CoordinatorResultExtractorError(
                "S1-EC102 extraction changed or crossed closed scope"
            )


def extract_e1_common_probe_ec102_coordinator_results(
    gate: E1CommonProbeEC101CoordinatorIntegrationGate,
    r2_result: E1CommonProbeN2R2RealModeCoordinatorResult,
    r4_r8_result: E1CommonProbeEC96AtomicResult,
) -> E1CommonProbeEC102CoordinatorResultExtraction:
    """Extract completed result objects without invoking either coordinator."""

    if (
        not isinstance(gate, E1CommonProbeEC101CoordinatorIntegrationGate)
        or gate.decision != S1_EC102_EC101_DECISION
        or gate.coordinator_execution_permitted
        or not isinstance(r2_result, E1CommonProbeN2R2RealModeCoordinatorResult)
        or not isinstance(r4_r8_result, E1CommonProbeEC96AtomicResult)
    ):
        raise E1CommonProbeEC102CoordinatorResultExtractorError(
            "S1-EC102 requires the closed EC101 gate and typed completed results"
        )
    gate.__post_init__()
    r2_result.__post_init__()
    r4_r8_result.__post_init__()
    if tuple(item.refinement_id for item in r4_r8_result.refinements) != ("r4", "r8"):
        raise E1CommonProbeEC102CoordinatorResultExtractorError(
            "S1-EC102 requires ordered r4 and r8 refinement results"
        )
    for refinement in r4_r8_result.refinements:
        refinement.__post_init__()

    r2_probes = tuple(r2_result.probes)
    refined_probes = tuple(
        probe for refinement in r4_r8_result.refinements for probe in refinement.probes
    )
    all_probes = (*r2_probes, *refined_probes)
    for probe in all_probes:
        probe.__post_init__()
    expected_refined_order = tuple(
        (refinement, role)
        for refinement in ("r4", "r8")
        for role in S1_EC45_PROBE_ROLES
    )
    exact_role_order = (
        tuple(item.role_id for item in r2_probes) == S1_EC45_PROBE_ROLES
        and tuple((item.refinement_id, item.role_id) for item in refined_probes)
        == expected_refined_order
    )
    object_ids = tuple(id(item) for item in all_probes)
    receipt_digests = tuple(item.receipt_digest for item in all_probes)
    if (
        len(r2_probes) != 8
        or len(refined_probes) != 16
        or not exact_role_order
        or len(set(object_ids)) != 24
        or len(set(receipt_digests)) != 24
        or r2_result.actual_field_steps_executed != 3208
        or r4_r8_result.total_field_steps != 19248
        or not r4_r8_result.exactly_once_completed
        or r2_result.persistence_performed
        or r4_r8_result.persistence_performed
    ):
        raise E1CommonProbeEC102CoordinatorResultExtractorError(
            "S1-EC102 source results are incomplete, reordered, or reused"
        )

    source = build_e1_common_probe_ec100_source_bundle(r2_probes, refined_probes)
    handoff = build_e1_common_probe_ec100_atomic_vector_handoff(source)
    forwarded = (*source.r2_probes, *source.r4_r8_probes)
    values = {
        "extractor_id": S1_EC102_EXTRACTOR_ID,
        "source_gate_digest": gate.gate_digest,
        "r2_result_digest": r2_result.result_digest,
        "r4_r8_result_digest": r4_r8_result.result_digest,
        "source_result_digests": (r2_result.result_digest, r4_r8_result.result_digest),
        "extracted_refinement_ids": ("r2", "r4", "r8"),
        "extracted_probe_counts": (("r2", 8), ("r4", 8), ("r8", 8)),
        "extracted_probe_receipt_digests": receipt_digests,
        "source_accounted_field_steps": (
            r2_result.actual_field_steps_executed + r4_r8_result.total_field_steps
        ),
        "all_source_results_complete": True,
        "all_probe_objects_distinct": len(set(object_ids)) == 24,
        "all_probe_receipts_distinct": len(set(receipt_digests)) == 24,
        "exact_role_order": exact_role_order,
        "same_objects_forwarded_to_ec100": all(
            left is right for left, right in zip(forwarded, all_probes, strict=True)
        ),
        "ec100_handoff_digest": handoff.result_digest,
        "extractor_field_steps_executed": 0,
        "persistence_performed": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "COORDINATOR_RESULTS_EXTRACTED_TO_EC100_NO_EXECUTION",
    }
    return E1CommonProbeEC102CoordinatorResultExtraction(
        **values,
        result_digest=_digest(values),
        gate=gate,
        r2_result=r2_result,
        r4_r8_result=r4_r8_result,
        ec100_handoff=handoff,
    )
