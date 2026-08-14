from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from mcm_field_organism.e1_common_probe_ec87_r2_ec46_complement_contract import (
    E1CommonProbeEC87R2EC46ComplementContractError,
    S1_EC87_EC86_REPORT_RELATIVE_PATH,
    build_e1_common_probe_ec87_r2_ec46_complement_contract,
)


class E1CommonProbeEC87R2EC46ComplementContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.acceptance = build_e1_common_probe_acceptance_contract()

    def test_r2_is_valid_partial_input_but_ec46_stays_blocked(self) -> None:
        result = build_e1_common_probe_ec87_r2_ec46_complement_contract(
            self.root, self.acceptance
        )
        self.assertEqual(("r2",), result.available_refinement_levels)
        self.assertEqual(("r4", "r8"), result.missing_refinement_levels)
        self.assertTrue(result.r2_null_controls_within_tolerance)
        self.assertTrue(result.r2_active_order_above_absolute_tolerance)
        self.assertFalse(result.ec46_decision_permitted)
        self.assertFalse(result.field_execution_permitted)

    def test_changed_ec86_report_fails_closed(self) -> None:
        source = self.root / S1_EC87_EC86_REPORT_RELATIVE_PATH
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / S1_EC87_EC86_REPORT_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            target.write_text(
                target.read_text(encoding="utf-8") + "\nmutation\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                E1CommonProbeEC87R2EC46ComplementContractError,
                "report changed",
            ):
                build_e1_common_probe_ec87_r2_ec46_complement_contract(
                    root, self.acceptance
                )

    def test_untyped_ec46_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeEC87R2EC46ComplementContractError, "typed EC46"
        ):
            build_e1_common_probe_ec87_r2_ec46_complement_contract(
                self.root, object()
            )

    def test_builder_calls_no_decider_execution_or_writer(self) -> None:
        source = inspect.getsource(
            build_e1_common_probe_ec87_r2_ec46_complement_contract
        )
        for forbidden in (
            "decide_common_probe_evidence(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "build_e1_common_probe_r2_ec84_atomic_return(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
