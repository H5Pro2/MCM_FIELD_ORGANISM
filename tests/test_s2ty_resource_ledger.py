import unittest

from tools import _s2ty_resource_ledger as ledger


class Tests(unittest.TestCase):
    def test_planned_shape_has_bounded_dual_arm_native_peak(self):
        payload = ledger.native_payload(ledger.planned_shape())
        self.assertEqual((payload["pcm_window"], payload["raw_receptor_endpoint"], payload["materialized_half_queue"], payload["total"]), (19_200, 384, 8_448, 39_936))
        self.assertLessEqual(payload["total"], ledger.LIMITS["native_float64_payload"])

    def test_fft_workspace_and_python_administration_are_explicitly_separate(self):
        workspace = ledger.materializer_workspace()
        self.assertEqual(workspace["fft_workspace_lower_bound_bytes"], 1_939_992)
        self.assertEqual(workspace["python_administration"], "NOT_STATICALLY_BOUNDED")

    def test_success_and_failure_records_are_alternative_envelopes(self):
        result = ledger.ledger(
            ledger.planned_shape(),
            source_bytes=1_000,
            metadata_bytes=2_000,
            shared_bytes=3_000,
            success_record_bytes=4_000,
            failure_record_bytes=5_000,
            verification_bytes=6_000,
        )
        self.assertEqual(result["branches"]["success"]["total_bytes"], 16_000)
        self.assertEqual(result["branches"]["failure"]["total_bytes"], 17_000)

    def test_source_binding_is_required_before_a_run_budget_can_pass(self):
        with self.assertRaises(ledger.S2TYBudgetError) as raised:
            ledger.ledger(
                ledger.planned_shape(),
                source_bytes=None,
                metadata_bytes=0,
                shared_bytes=0,
                success_record_bytes=0,
                failure_record_bytes=0,
                verification_bytes=0,
            )
        self.assertEqual(raised.exception.code, "SOURCE_BINDING_UNRESOLVED")

    def test_boundary_and_overflow_report_full_failure_contributions(self):
        result = ledger.ledger(
            ledger.planned_shape(),
            source_bytes=0,
            metadata_bytes=ledger.LIMITS["metadata"],
            shared_bytes=ledger.LIMITS["shared"],
            success_record_bytes=ledger.LIMITS["record"],
            failure_record_bytes=ledger.LIMITS["record"],
            verification_bytes=ledger.LIMITS["verification"],
        )
        self.assertEqual(result["branches"]["failure"]["contributions"]["record"], ledger.LIMITS["record"])

        with self.assertRaises(ledger.S2TYBudgetError) as raised:
            ledger.ledger(
                ledger.planned_shape(),
                source_bytes=123,
                metadata_bytes=ledger.LIMITS["metadata"] + 1,
                shared_bytes=0,
                success_record_bytes=0,
                failure_record_bytes=1,
                verification_bytes=0,
            )
        self.assertEqual(raised.exception.code, "METADATA_LIMIT")
        self.assertEqual(raised.exception.details["branch"], "success")
        self.assertEqual((raised.exception.details["phase"], raised.exception.details["progress"]), ("PRESTART", 0))
        self.assertEqual(raised.exception.details["contributions"], {"sources": 123, "metadata": 65_537, "shared": 0, "verification": 0, "record": 0})

    def test_global_limit_is_enforced_when_local_classes_fit(self):
        with self.assertRaises(ledger.S2TYBudgetError) as raised:
            ledger.ledger(
                ledger.planned_shape(),
                source_bytes=ledger.LIMITS["total"] + 1,
                metadata_bytes=0,
                shared_bytes=0,
                success_record_bytes=0,
                failure_record_bytes=0,
                verification_bytes=0,
            )
        self.assertEqual(raised.exception.code, "TOTAL_LIMIT")
        self.assertEqual(raised.exception.details["contributions"], {"sources": 4_194_305, "metadata": 0, "shared": 0, "verification": 0, "record": 0})
