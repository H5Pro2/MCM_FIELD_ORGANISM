from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec102_coordinator_result_extractor import (
    E1CommonProbeEC102CoordinatorResultExtractorError,
    extract_e1_common_probe_ec102_coordinator_results,
)
from mcm_field_organism.e1_common_probe_ec103_synthetic_coordinator_e2e_fixture import (
    E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError,
    S1_EC103_EXPECTED_ACTIVE_VECTORS,
    build_e1_common_probe_ec103_synthetic_r2_result,
    build_e1_common_probe_ec103_synthetic_r4_r8_result,
    build_e1_common_probe_ec103_synthetic_refinement_result,
    run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture,
)
from mcm_field_organism.e1_common_probe_ec101_coordinator_integration_gate import (
    audit_e1_common_probe_ec101_coordinator_integration_gate,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1CommonProbeEC103SyntheticCoordinatorE2EFixtureTests(unittest.TestCase):
    def test_complete_chain_preserves_sources_and_exact_vectors(self) -> None:
        result = run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture()
        self.assertEqual(24, result.source_probe_count)
        self.assertEqual(22456, result.source_accounted_field_steps)
        self.assertEqual(0, result.fixture_field_steps_executed)
        self.assertTrue(result.all_probe_identities_preserved)
        self.assertTrue(result.all_24_source_digests_bound)
        self.assertEqual(S1_EC103_EXPECTED_ACTIVE_VECTORS, result.ec98_active_order_vectors)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture()
        second = run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture()
        self.assertEqual(first.result_digest, second.result_digest)

    def test_swapped_refinements_fail_closed(self) -> None:
        swapped = build_e1_common_probe_ec103_synthetic_r4_r8_result(
            (
                build_e1_common_probe_ec103_synthetic_refinement_result("r8"),
                build_e1_common_probe_ec103_synthetic_refinement_result("r4"),
            )
        )
        with self.assertRaises(E1CommonProbeEC102CoordinatorResultExtractorError):
            extract_e1_common_probe_ec102_coordinator_results(
                audit_e1_common_probe_ec101_coordinator_integration_gate(),
                build_e1_common_probe_ec103_synthetic_r2_result(),
                swapped,
            )

    def test_reused_probe_object_fails_closed(self) -> None:
        r4 = build_e1_common_probe_ec103_synthetic_refinement_result("r4")
        probes = (r4.probes[0], r4.probes[0], *r4.probes[2:])
        values = {
            name: getattr(r4, name)
            for name in r4.__dataclass_fields__
            if name not in {"result_digest", "formations", "probes"}
        }
        values["probe_receipt_digests"] = tuple(item.receipt_digest for item in probes)
        bad_r4 = type(r4)(
            **values,
            result_digest=_digest(values),
            formations=r4.formations,
            probes=probes,
        )
        with self.assertRaises(E1CommonProbeEC102CoordinatorResultExtractorError):
            extract_e1_common_probe_ec102_coordinator_results(
                audit_e1_common_probe_ec101_coordinator_integration_gate(),
                build_e1_common_probe_ec103_synthetic_r2_result(),
                build_e1_common_probe_ec103_synthetic_r4_r8_result(
                    (
                        bad_r4,
                        build_e1_common_probe_ec103_synthetic_refinement_result("r8"),
                    )
                ),
            )

    def test_changed_fixture_result_fails_closed(self) -> None:
        result = run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture()
        with self.assertRaises(E1CommonProbeEC103SyntheticCoordinatorE2EFixtureError):
            replace(result, fixture_field_steps_executed=1)

    def test_fixture_does_not_call_coordinator_kernel_decider_or_writer(self) -> None:
        source = inspect.getsource(
            run_e1_common_probe_ec103_synthetic_coordinator_e2e_fixture
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
