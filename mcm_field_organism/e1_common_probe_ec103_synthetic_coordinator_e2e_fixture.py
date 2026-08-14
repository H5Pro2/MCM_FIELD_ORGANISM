"""S1-EC103 synthetic EC67/EC96 -> EC102 -> EC100 -> EC98 fixture."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
    E1CommonProbeEC96RefinementResult,
    S1_EC96_EC89_RESULT_DIGEST,
    S1_EC96_RESULT_ID,
)
from .e1_common_probe_ec99_typed_vector_input_adapters import (
    _synthetic_r2_receipt,
    _synthetic_refined_receipt,
)
from .e1_common_probe_ec101_coordinator_integration_gate import (
    audit_e1_common_probe_ec101_coordinator_integration_gate,
)
from .e1_common_probe_ec102_coordinator_result_extractor import (
    E1CommonProbeEC102CoordinatorResultExtraction,
    extract_e1_common_probe_ec102_coordinator_results,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    S1_EC67_COORDINATOR_ID,
    S1_EC67_EC59_HANDOFF_DIGEST,
    S1_EC67_EC65_AUDIT_DIGEST,
    S1_EC67_EC66_FIXTURE_DIGEST,
)
from .e1_common_probe_r2_ec80_scalar_contract import (
    S1_EC80_CONTRAST_ROLE_PAIRS,
)
from .e1_common_probe_real_binding_contract import (
    S1_EC52_FORMATION_STATE_ROLES,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError(ValueError):
    """Raised when the synthetic coordinator fixture leaves its closed scope."""


S1_EC103_FIXTURE_ID = "e1.common-probe-coordinator-e2e-fixture.s1ec103.v1"
S1_EC103_CHAIN = ("EC67/EC96", "EC102", "EC100", "EC99", "EC98")
S1_EC103_EXPECTED_ACTIVE_VECTORS = (
    ("r2", (12.0, 0.0, 0.0), (6.0, 0.0, 0.0)),
    ("r4", (8.0, 0.0, 0.0), (4.0, 0.0, 0.0)),
    ("r8", (6.0, 0.0, 0.0), (3.0, 0.0, 0.0)),
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC103SyntheticFormationDigest:
    """Minimal inert formation reference required by result-container metadata."""

    receipt_digest: str

    def __post_init__(self) -> None:
        if len(self.receipt_digest) != 64:
            raise E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError(
                "S1-EC103 synthetic formation digest changed"
            )


def build_e1_common_probe_ec103_synthetic_r2_result(
) -> E1CommonProbeN2R2RealModeCoordinatorResult:
    """Build one inert but contract-valid EC67 result container."""

    probes = tuple(_synthetic_r2_receipt(role) for role in S1_EC45_PROBE_ROLES)
    formations = tuple(
        E1CommonProbeEC103SyntheticFormationDigest(
            _digest((S1_EC103_FIXTURE_ID, "r2", role))
        )
        for role in S1_EC52_FORMATION_STATE_ROLES
    )
    values = {
        "coordinator_id": S1_EC67_COORDINATOR_ID,
        "source_handoff_digest": S1_EC67_EC59_HANDOFF_DIGEST,
        "source_ec65_audit_digest": S1_EC67_EC65_AUDIT_DIGEST,
        "source_ec66_fixture_digest": S1_EC67_EC66_FIXTURE_DIGEST,
        "execution_mode": "real-wrapper",
        "roles": S1_EC45_PROBE_ROLES,
        "formation_state_roles": S1_EC52_FORMATION_STATE_ROLES,
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "formation_count": 4,
        "fresh_field_count": 8,
        "probe_count": 8,
        "accounted_formation_steps": 1608,
        "accounted_probe_steps": 1600,
        "accounted_total_steps": 3208,
        "actual_field_steps_executed": 3208,
        "all_state_routes_exact": True,
        "all_backreaction_routes_exact": True,
        "all_fresh_fields_identical_and_object_separate": True,
        "all_formation_states_object_separate": True,
        "preflight_and_owner_released": True,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2RealModeCoordinatorResult(
        **values,
        result_digest=_digest(values),
        formations=formations,  # type: ignore[arg-type]
        fresh_fields=tuple(object() for _ in range(8)),  # type: ignore[arg-type]
        probes=probes,
    )


def build_e1_common_probe_ec103_synthetic_refinement_result(
    refinement_id: str,
) -> E1CommonProbeEC96RefinementResult:
    """Build one inert r4 or r8 result with complete typed probe receipts."""

    if refinement_id not in {"r4", "r8"}:
        raise E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError(
            "S1-EC103 supports exactly r4 and r8"
        )
    probes = tuple(
        _synthetic_refined_receipt(refinement_id, role)
        for role in S1_EC45_PROBE_ROLES
    )
    formations = tuple(
        E1CommonProbeEC103SyntheticFormationDigest(
            _digest((S1_EC103_FIXTURE_ID, refinement_id, role))
        )
        for role in S1_EC52_FORMATION_STATE_ROLES
    )
    formation_steps, probe_steps, total_steps = {
        "r4": (3216, 3200, 6416),
        "r8": (6432, 6400, 12832),
    }[refinement_id]
    values = {
        "refinement_id": refinement_id,
        "handoff_digest": _digest((S1_EC103_FIXTURE_ID, refinement_id, "handoff")),
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "contrast_scalars": tuple(
            (name, 0.0, 0.0) for name, _, _ in S1_EC80_CONTRAST_ROLE_PAIRS
        ),
        "formation_steps": formation_steps,
        "probe_steps": probe_steps,
        "total_steps": total_steps,
        "all_routes_exact": True,
        "all_fresh_fields_identical_and_object_separate": True,
    }
    return E1CommonProbeEC96RefinementResult(
        **values,
        result_digest=_digest(values),
        formations=formations,  # type: ignore[arg-type]
        probes=probes,
    )


def build_e1_common_probe_ec103_synthetic_r4_r8_result(
    refinements: tuple[E1CommonProbeEC96RefinementResult, ...] | None = None,
) -> E1CommonProbeEC96AtomicResult:
    """Build the complete inert EC96 result container in caller-supplied order."""

    items = refinements or (
        build_e1_common_probe_ec103_synthetic_refinement_result("r4"),
        build_e1_common_probe_ec103_synthetic_refinement_result("r8"),
    )
    values = {
        "result_id": S1_EC96_RESULT_ID,
        "source_handoff_set_digest": S1_EC96_EC89_RESULT_DIGEST,
        "source_gate_digest": _digest((S1_EC103_FIXTURE_ID, "gate")),
        "authorization_digest": _digest((S1_EC103_FIXTURE_ID, "authorization")),
        "immediate_resource_digest": _digest((S1_EC103_FIXTURE_ID, "resources")),
        "immediate_free_memory_bytes": 6 * 1024**3,
        "immediate_free_disk_bytes": 200 * 1024**3,
        "refinement_ids": ("r4", "r8"),
        "refinement_result_digests": tuple(item.result_digest for item in items),
        "total_field_steps": 19248,
        "resource_gate_passed_before_first_adapter": True,
        "authorization_consumed": True,
        "exactly_once_completed": True,
        "atomic_scalar_return": True,
        "persistence_performed": False,
        "retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC96AtomicResult(
        **values, result_digest=_digest(values), refinements=items
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC103SyntheticCoordinatorE2EFixtureResult:
    fixture_id: str
    chain: tuple[str, ...]
    source_result_digests: tuple[str, ...]
    extraction_digest: str
    source_probe_count: int
    source_accounted_field_steps: int
    fixture_field_steps_executed: int
    all_probe_identities_preserved: bool
    all_24_source_digests_bound: bool
    exact_active_vectors: bool
    ec98_active_order_vectors: tuple[
        tuple[str, tuple[float, ...], tuple[float, ...]], ...
    ]
    persistence_performed: bool
    retry_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    result_digest: str
    extraction: E1CommonProbeEC102CoordinatorResultExtraction = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "extraction"}
        }
        receipt = self.extraction.ec100_handoff.vector_receipt
        if (
            self.fixture_id != S1_EC103_FIXTURE_ID
            or self.chain != S1_EC103_CHAIN
            or self.source_result_digests != self.extraction.source_result_digests
            or self.extraction_digest != self.extraction.result_digest
            or self.source_probe_count != 24
            or self.source_accounted_field_steps != 22456
            or self.fixture_field_steps_executed != 0
            or self.all_probe_identities_preserved is not True
            or self.all_24_source_digests_bound is not True
            or self.exact_active_vectors is not True
            or self.ec98_active_order_vectors != S1_EC103_EXPECTED_ACTIVE_VECTORS
            or self.ec98_active_order_vectors != receipt.active_order_vectors
            or len(receipt.source_input_digests) != 24
            or len(set(receipt.source_input_digests)) != 24
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
            or self.status != "SYNTHETIC_EC67_EC96_TO_EC98_CHAIN_CLOSED_NO_EXECUTION"
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError(
                "S1-EC103 end-to-end fixture changed or crossed closed scope"
            )


def run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture(
) -> E1CommonProbeEC103SyntheticCoordinatorE2EFixtureResult:
    """Exercise the complete extraction and vector path without a field runtime."""

    r2 = build_e1_common_probe_ec103_synthetic_r2_result()
    r4_r8 = build_e1_common_probe_ec103_synthetic_r4_r8_result()
    extraction = extract_e1_common_probe_ec102_coordinator_results(
        audit_e1_common_probe_ec101_coordinator_integration_gate(), r2, r4_r8
    )
    source_probes = (
        *r2.probes,
        *(probe for refinement in r4_r8.refinements for probe in refinement.probes),
    )
    forwarded = (
        *extraction.ec100_handoff.source_bundle.r2_probes,
        *extraction.ec100_handoff.source_bundle.r4_r8_probes,
    )
    receipt = extraction.ec100_handoff.vector_receipt
    values = {
        "fixture_id": S1_EC103_FIXTURE_ID,
        "chain": S1_EC103_CHAIN,
        "source_result_digests": (r2.result_digest, r4_r8.result_digest),
        "extraction_digest": extraction.result_digest,
        "source_probe_count": len(source_probes),
        "source_accounted_field_steps": extraction.source_accounted_field_steps,
        "fixture_field_steps_executed": 0,
        "all_probe_identities_preserved": all(
            source is target
            for source, target in zip(source_probes, forwarded, strict=True)
        ),
        "all_24_source_digests_bound": (
            extraction.extracted_probe_receipt_digests
            == extraction.ec100_handoff.source_receipt_digests
            and len(set(extraction.extracted_probe_receipt_digests)) == 24
        ),
        "exact_active_vectors": (
            receipt.active_order_vectors == S1_EC103_EXPECTED_ACTIVE_VECTORS
        ),
        "ec98_active_order_vectors": receipt.active_order_vectors,
        "persistence_performed": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "SYNTHETIC_EC67_EC96_TO_EC98_CHAIN_CLOSED_NO_EXECUTION",
    }
    return E1CommonProbeEC103SyntheticCoordinatorE2EFixtureResult(
        **values, result_digest=_digest(values), extraction=extraction
    )
