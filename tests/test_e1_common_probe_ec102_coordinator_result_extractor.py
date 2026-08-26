from __future__ import annotations

from dataclasses import dataclass
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
    E1CommonProbeEC96RefinementResult,
    S1_EC96_EC89_RESULT_DIGEST,
    S1_EC96_RESULT_ID,
)
from mcm_field_organism.e1_common_probe_ec99_typed_vector_input_adapters import (
    _synthetic_r2_receipt,
    _synthetic_refined_receipt,
)
from mcm_field_organism.e1_common_probe_ec101_coordinator_integration_gate import (
    audit_e1_common_probe_ec101_coordinator_integration_gate,
)
from mcm_field_organism.e1_common_probe_ec102_coordinator_result_extractor import (
    E1CommonProbeEC102CoordinatorResultExtractorError,
    extract_e1_common_probe_ec102_coordinator_results,
)
from mcm_field_organism.e1_common_probe_identifiability_contract import (
    S1_EC45_PROBE_ROLES,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    S1_EC67_COORDINATOR_ID,
    S1_EC67_EC59_HANDOFF_DIGEST,
    S1_EC67_EC65_AUDIT_DIGEST,
    S1_EC67_EC66_FIXTURE_DIGEST,
)
from mcm_field_organism.e1_common_probe_r2_ec80_scalar_contract import (
    S1_EC80_CONTRAST_ROLE_PAIRS,
)
from mcm_field_organism.e1_common_probe_real_binding_contract import (
    S1_EC52_FORMATION_STATE_ROLES,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


@dataclass(frozen=True)
class _DigestOnly:
    receipt_digest: str


def _r2_result() -> E1CommonProbeN2R2RealModeCoordinatorResult:
    probes = tuple(_synthetic_r2_receipt(role) for role in S1_EC45_PROBE_ROLES)
    formations = tuple(_DigestOnly(_digest(("ec102", "r2", index))) for index in range(4))
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


def _refinement(refinement_id: str) -> E1CommonProbeEC96RefinementResult:
    probes = tuple(
        _synthetic_refined_receipt(refinement_id, role)
        for role in S1_EC45_PROBE_ROLES
    )
    formations = tuple(
        _DigestOnly(_digest(("ec102", refinement_id, index))) for index in range(4)
    )
    steps = {"r4": (3216, 3200, 6416), "r8": (6432, 6400, 12832)}[
        refinement_id
    ]
    values = {
        "refinement_id": refinement_id,
        "handoff_digest": _digest(("ec102", refinement_id, "handoff")),
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "contrast_scalars": tuple(
            (name, 0.0, 0.0) for name, _, _ in S1_EC80_CONTRAST_ROLE_PAIRS
        ),
        "formation_steps": steps[0],
        "probe_steps": steps[1],
        "total_steps": steps[2],
        "all_routes_exact": True,
        "all_fresh_fields_identical_and_object_separate": True,
    }
    return E1CommonProbeEC96RefinementResult(
        **values,
        result_digest=_digest(values),
        formations=formations,  # type: ignore[arg-type]
        probes=probes,
    )


def _r4_r8_result(
    refinements: tuple[E1CommonProbeEC96RefinementResult, ...] | None = None,
) -> E1CommonProbeEC96AtomicResult:
    items = refinements or (_refinement("r4"), _refinement("r8"))
    values = {
        "result_id": S1_EC96_RESULT_ID,
        "source_handoff_set_digest": S1_EC96_EC89_RESULT_DIGEST,
        "source_gate_digest": _digest(("ec102", "gate")),
        "authorization_digest": _digest(("ec102", "authorization")),
        "immediate_resource_digest": _digest(("ec102", "resources")),
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


class E1CommonProbeEC102CoordinatorResultExtractorTests(unittest.TestCase):
    def test_complete_results_are_forwarded_by_identity(self) -> None:
        r2 = _r2_result()
        refined = _r4_r8_result()
        result = extract_e1_common_probe_ec102_coordinator_results(
            audit_e1_common_probe_ec101_coordinator_integration_gate(), r2, refined
        )
        self.assertEqual((("r2", 8), ("r4", 8), ("r8", 8)), result.extracted_probe_counts)
        self.assertEqual(22456, result.source_accounted_field_steps)
        self.assertTrue(result.same_objects_forwarded_to_ec100)
        self.assertEqual(0, result.extractor_field_steps_executed)

    def test_result_is_deterministic(self) -> None:
        first = extract_e1_common_probe_ec102_coordinator_results(
            audit_e1_common_probe_ec101_coordinator_integration_gate(),
            _r2_result(),
            _r4_r8_result(),
        )
        second = extract_e1_common_probe_ec102_coordinator_results(
            audit_e1_common_probe_ec101_coordinator_integration_gate(),
            _r2_result(),
            _r4_r8_result(),
        )
        self.assertEqual(first.result_digest, second.result_digest)

    def test_swapped_refinements_fail_closed(self) -> None:
        with self.assertRaises(E1CommonProbeEC102CoordinatorResultExtractorError):
            extract_e1_common_probe_ec102_coordinator_results(
                audit_e1_common_probe_ec101_coordinator_integration_gate(),
                _r2_result(),
                _r4_r8_result((_refinement("r8"), _refinement("r4"))),
            )

    def test_reused_probe_object_fails_closed(self) -> None:
        r4 = _refinement("r4")
        bad_probes = (r4.probes[0], r4.probes[0], *r4.probes[2:])
        values = {
            name: getattr(r4, name)
            for name in r4.__dataclass_fields__
            if name not in {"result_digest", "formations", "probes"}
        }
        values["probe_receipt_digests"] = tuple(item.receipt_digest for item in bad_probes)
        bad_r4 = E1CommonProbeEC96RefinementResult(
            **values,
            result_digest=_digest(values),
            formations=r4.formations,
            probes=bad_probes,
        )
        with self.assertRaises(E1CommonProbeEC102CoordinatorResultExtractorError):
            extract_e1_common_probe_ec102_coordinator_results(
                audit_e1_common_probe_ec101_coordinator_integration_gate(),
                _r2_result(),
                _r4_r8_result((bad_r4, _refinement("r8"))),
            )

    def test_extractor_does_not_call_coordinator_kernel_decider_or_writer(self) -> None:
        source = inspect.getsource(extract_e1_common_probe_ec102_coordinator_results)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_probe_wrapper(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
