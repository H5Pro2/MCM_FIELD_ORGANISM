from __future__ import annotations

from dataclasses import fields
import inspect
from pathlib import Path
import unittest

import mcm_field_organism.dynamic_substrate_dts1_attenuation_audit as audit


class DTS1S1IHAttenuationAuditStructureTests(unittest.TestCase):
    def test_binds_source_cases_and_exact_double_budget(self) -> None:
        self.assertEqual(64, len(audit.S1_IH_SOURCE_S1IG_CONTRACT_DIGEST))
        self.assertEqual(6, len(audit.S1_IH_CASE_IDS))
        self.assertEqual(8, audit.S1_IH_SINGLE_DIRECT_RESOURCE_CALLS)
        self.assertEqual(14, audit.S1_IH_SINGLE_TECHNICAL_FIELD_CALLS)
        self.assertEqual(16, audit.S1_IH_DOUBLE_DIRECT_RESOURCE_CALLS)
        self.assertEqual(28, audit.S1_IH_DOUBLE_TECHNICAL_FIELD_CALLS)

    def test_expected_metrics_bind_three_contacts_and_both_directions(self) -> None:
        expected = dict(audit.S1_IH_EXPECTED)
        self.assertGreater(expected["engagement_1"], expected["engagement_2"])
        self.assertGreater(expected["engagement_2"], expected["engagement_3"])
        self.assertGreater(expected["contrast_1"], expected["contrast_2"])
        self.assertGreater(expected["contrast_2"], expected["contrast_3"])
        self.assertGreater(expected["engagement_drop_2"], audit.S1_IH_ROUNDOFF_FLOOR)
        self.assertGreater(expected["contrast_drop_2"], audit.S1_IH_ROUNDOFF_FLOOR)

    def test_case_record_schema_covers_resource_field_checks_and_counts(self) -> None:
        names = {item.name for item in fields(audit.DTS1S1IHCaseRecord)}
        self.assertEqual(
            {"case_id", "contact_records", "field_records", "exact_checks", "direct_resource_calls", "technical_field_calls"},
            names,
        )

    def test_execute_once_binds_all_six_case_builders(self) -> None:
        source = inspect.getsource(audit._execute_once)
        for name in ("_run_c01", "_run_n01", "_run_n02", "_run_n03", "_run_n04", "_run_n05"):
            self.assertIn(name, source)
        self.assertIn("research_field_steps", source)

    def test_double_entry_executes_exactly_two_complete_single_audits(self) -> None:
        source = inspect.getsource(audit.execute_dts1_s1ih_preregistered_double_audit)
        self.assertEqual(2, source.count("_execute_once()"))
        self.assertIn("repeat-receipt-mismatch", source)

    def test_readout_poststate_cannot_enter_contact_train(self) -> None:
        source = inspect.getsource(audit._run_c01)
        self.assertIn("anatomy = resource_result.next_anatomy", source)
        self.assertNotIn("anatomy = field_result.anatomy", source)
        self.assertIn("snapshots.append(anatomy)", source)

    def test_baselines_are_records_only_and_keep_e1_limit(self) -> None:
        source = inspect.getsource(audit._baseline_records)
        self.assertIn("ATTENUATION_ALONE_NOT_DISTINCT_NO_EXECUTION", source)
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
