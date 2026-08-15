from __future__ import annotations

from dataclasses import fields
import inspect
from pathlib import Path
import unittest

import mcm_field_organism.dynamic_substrate_dts1_interference_audit as audit


class DTS1S1IKInterferenceAuditStructureTests(unittest.TestCase):
    def test_binds_source_cases_and_exact_double_budget(self) -> None:
        self.assertEqual(64, len(audit.S1_IK_SOURCE_S1IJ_CONTRACT_DIGEST))
        self.assertEqual(7, len(audit.S1_IK_CASE_IDS))
        self.assertEqual(24, audit.S1_IK_SINGLE_DIRECT_RESOURCE_CALLS)
        self.assertEqual(10, audit.S1_IK_SINGLE_TECHNICAL_FIELD_CALLS)
        self.assertEqual(48, audit.S1_IK_DOUBLE_DIRECT_RESOURCE_CALLS)
        self.assertEqual(20, audit.S1_IK_DOUBLE_TECHNICAL_FIELD_CALLS)

    def test_expected_metrics_bind_resource_and_field_directions(self) -> None:
        expected = dict(audit.S1_IK_EXPECTED)
        self.assertGreater(expected["middle_B_engagement_ABA"], 0.0)
        self.assertGreater(expected["prefinal_shared_free_gap"], expected["prefinal_shared_free_ABA"])
        self.assertGreater(expected["final_A_engagement_gap"], expected["final_A_engagement_ABA"])
        self.assertGreater(expected["A_edge_contrast_ABA"], expected["A_edge_contrast_gap"])
        self.assertGreater(expected["complete_zero_H_SH_separation"], audit.S1_IK_ROUNDOFF_FLOOR)

    def test_case_record_schema_covers_sequences_fields_checks_and_counts(self) -> None:
        names = {item.name for item in fields(audit.DTS1S1IKCaseRecord)}
        self.assertEqual(
            {"case_id", "sequence_records", "field_records", "exact_checks", "direct_resource_calls", "technical_field_calls"},
            names,
        )

    def test_execute_once_binds_all_seven_case_builders(self) -> None:
        source = inspect.getsource(audit._execute_once)
        for name in ("_run_c01", "_run_n01", "_run_n02", "_run_n03", "_run_n04", "_run_n05", "_run_n06"):
            self.assertIn(name, source)
        self.assertIn("research_field_steps", source)

    def test_double_entry_executes_exactly_two_complete_single_audits(self) -> None:
        source = inspect.getsource(audit.execute_dts1_s1ik_preregistered_double_audit)
        self.assertEqual(2, source.count("_execute_once()"))
        self.assertIn("repeat-receipt-mismatch", source)

    def test_resource_sequence_and_readout_poststates_are_separated(self) -> None:
        sequence_source = inspect.getsource(audit._run_sequence)
        case_source = inspect.getsource(audit._run_c01)
        self.assertIn("anatomy = result.next_anatomy", sequence_source)
        self.assertNotIn("anatomy =", case_source.split("_field_call", 1)[-1])

    def test_baselines_are_records_only_and_keep_e1_limit(self) -> None:
        source = inspect.getsource(audit._baseline_records)
        self.assertIn("INTERFERENCE_ALONE_NOT_DISTINCT_NO_EXECUTION", source)
        self.assertNotIn("run_", source)
        self.assertNotIn("execute_", source)

    def test_module_is_private_and_has_no_io_runtime_or_test_dependency(self) -> None:
        source = Path(audit.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "current_api",
            "runtime",
            "from tests",
            "import tests",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
