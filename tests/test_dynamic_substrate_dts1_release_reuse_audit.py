from __future__ import annotations

from dataclasses import fields
import inspect
from pathlib import Path
import unittest

import mcm_field_organism.dynamic_substrate_dts1_release_reuse_audit as audit


class DTS1S1INReleaseReuseAuditStructureTests(unittest.TestCase):
    def test_binds_source_cases_and_exact_double_budget(self) -> None:
        self.assertEqual(64, len(audit.S1_IN_SOURCE_S1IM_CONTRACT_DIGEST))
        self.assertEqual(8, len(audit.S1_IN_CASE_IDS))
        self.assertEqual((18, 10), (audit.S1_IN_SINGLE_DIRECT_RESOURCE_CALLS, audit.S1_IN_SINGLE_TECHNICAL_FIELD_CALLS))
        self.assertEqual((36, 20), (audit.S1_IN_DOUBLE_DIRECT_RESOURCE_CALLS, audit.S1_IN_DOUBLE_TECHNICAL_FIELD_CALLS))

    def test_expected_metrics_bind_release_reuse_and_field_directions(self) -> None:
        expected = dict(audit.S1_IN_EXPECTED)
        self.assertGreater(expected["shared_free_release_margin"], audit.S1_IN_ROUNDOFF_FLOOR)
        self.assertGreater(expected["additional_B_engagement_margin"], audit.S1_IN_ROUNDOFF_FLOOR)
        self.assertGreater(expected["B_edge_contrast_off_minus_on"], audit.S1_IN_ROUNDOFF_FLOOR)
        self.assertGreater(expected["complete_zero_H_SH_separation"], audit.S1_IN_ROUNDOFF_FLOOR)

    def test_case_record_schema_covers_traces_fields_checks_and_counts(self) -> None:
        self.assertEqual(
            {"case_id", "trace_records", "field_records", "exact_checks", "direct_resource_calls", "technical_field_calls"},
            {item.name for item in fields(audit.DTS1S1INCaseRecord)},
        )

    def test_execute_once_binds_all_eight_case_builders(self) -> None:
        source = inspect.getsource(audit._execute_once)
        for name in ("_run_c01", "_run_n01", "_run_n02", "_run_n03", "_run_n04", "_run_n05", "_run_n06", "_run_n07"):
            self.assertIn(name, source)
        self.assertIn("research_field_steps", source)

    def test_double_entry_executes_exactly_two_complete_single_audits(self) -> None:
        source = inspect.getsource(audit.execute_dts1_s1in_preregistered_double_audit)
        self.assertEqual(2, source.count("_execute_once()"))
        self.assertIn("repeat-receipt-mismatch", source)

    def test_fixed_control_uses_one_common_prerelease_adapter(self) -> None:
        source = inspect.getsource(audit._run_n06)
        self.assertEqual(1, source.count("compute_dts1_edge_rates"))
        self.assertEqual(2, source.count("_fixed_field_record"))

    def test_baselines_are_records_only_and_keep_e1_limit(self) -> None:
        source = inspect.getsource(audit._baseline_records)
        self.assertIn("RELEASE_REUSE_ALONE_NOT_DISTINCT_NO_EXECUTION", source)
        self.assertNotIn("run_", source)
        self.assertNotIn("execute_", source)

    def test_module_is_private_and_has_no_io_runtime_or_test_dependency(self) -> None:
        source = Path(audit.__file__).read_text(encoding="utf-8")
        for forbidden in ("current_api", "runtime", "from tests", "import tests", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
