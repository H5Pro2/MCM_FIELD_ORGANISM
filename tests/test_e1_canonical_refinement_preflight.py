from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refinement_preflight import (
    E1CanonicalRefinementPreflightError,
    S1_DT_IMPLEMENTATION_DIGEST,
    S1_DU_STEP_COUNTS,
    current_s1_dt_implementation_digest,
    prepare_e1_canonical_refinement_preflight,
)


REPORT = Path("reports/e1_frozen_state_transfer_s1dn_once_v1.json")


class E1CanonicalRefinementPreflightTests(unittest.TestCase):
    def test_preflight_binds_canonical_counts_and_step_grids(self) -> None:
        result = prepare_e1_canonical_refinement_preflight(REPORT)

        self.assertEqual(220, result.source_event_count_per_history)
        self.assertEqual(200, result.completion_count_per_history)
        self.assertEqual(S1_DU_STEP_COUNTS, result.step_counts)
        self.assertTrue(result.completion_ticks_equal)
        self.assertTrue(result.step_grids_equal)

    def test_same_world_inventory_and_integrals_are_preserved(self) -> None:
        result = prepare_e1_canonical_refinement_preflight(REPORT)

        self.assertTrue(result.payload_inventories_equal)
        self.assertTrue(result.support_inventories_equal)
        self.assertTrue(result.organism_slot_inventories_equal)
        self.assertTrue(result.contact_integrals_equal)
        self.assertEqual(14.328373475671894, result.source_signed_integral)
        self.assertEqual(14.328373475671894, result.source_absolute_integral)
        self.assertEqual(3.293282702508704, result.source_quadratic_integral)

    def test_ordered_ab_ba_paths_remain_distinct(self) -> None:
        result = prepare_e1_canonical_refinement_preflight(REPORT)

        self.assertTrue(result.ordered_contact_paths_different)
        self.assertNotEqual(
            result.ab_source_contact_digest,
            result.ba_source_contact_digest,
        )
        self.assertNotEqual(result.ab_plan_digest, result.ba_plan_digest)

    def test_source_digest_and_preflight_digest_are_repeatable(self) -> None:
        first = prepare_e1_canonical_refinement_preflight(REPORT)
        second = prepare_e1_canonical_refinement_preflight(REPORT)

        self.assertEqual(S1_DT_IMPLEMENTATION_DIGEST, current_s1_dt_implementation_digest())
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_preflight_releases_implementation_only(self) -> None:
        result = prepare_e1_canonical_refinement_preflight(REPORT)

        self.assertTrue(result.implementation_permitted)
        with self.assertRaises(E1CanonicalRefinementPreflightError):
            replace(result, execution_permitted=True)
        with self.assertRaises(E1CanonicalRefinementPreflightError):
            replace(result, memory_claim_permitted=True)

    def test_changed_upstream_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["technical_status"] = "CHANGED"
            path = Path(directory) / REPORT.name
            path.write_text(json.dumps(changed) + "\n", encoding="ascii")
            with self.assertRaises(ValueError):
                prepare_e1_canonical_refinement_preflight(path)

    def test_preflight_has_no_field_execution_and_remains_private(self) -> None:
        source = inspect.getsource(prepare_e1_canonical_refinement_preflight)
        for forbidden in (
            "run_e1_asynchronous_field",
            "advance_e1_local_edge_plasticity",
            "produce_e1_a0_av_histories",
            "execute_e1_frozen_state_transfer_one_shot",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1CanonicalRefinementPreflight",
            "prepare_e1_canonical_refinement_preflight",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
