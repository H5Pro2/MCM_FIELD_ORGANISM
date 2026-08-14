from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    E1CommonProbeN2R2EC79StaticEvaluationContractError,
    S1_EC79_EC78_REPORT_RELATIVE_PATH,
    build_e1_common_probe_n2_r2_ec79_static_evaluation_contract,
)


class E1CommonProbeN2R2EC79StaticEvaluationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]

    def test_exact_report_yields_closed_evaluation_boundary(self) -> None:
        contract = build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
            self.project_root
        )

        self.assertEqual((4, 8, 8, 3208), (
            contract.completed_formation_count,
            contract.completed_fresh_field_count,
            contract.completed_probe_count,
            contract.completed_field_steps,
        ))
        self.assertEqual(("r2",), contract.available_refinement_levels)
        self.assertEqual(("r2", "r4", "r8"), contract.required_refinement_levels)
        self.assertFalse(contract.quantitative_probe_vectors_retained)
        self.assertFalse(contract.quantitative_decision_permitted)

    def test_changed_ec78_report_fails_closed(self) -> None:
        source = self.project_root / S1_EC79_EC78_REPORT_RELATIVE_PATH
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / S1_EC79_EC78_REPORT_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            target.write_text(
                target.read_text(encoding="utf-8") + "\nsynthetic mutation\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                E1CommonProbeN2R2EC79StaticEvaluationContractError,
                "report changed",
            ):
                build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(root)

    def test_untyped_acceptance_contract_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeN2R2EC79StaticEvaluationContractError,
            "typed EC46",
        ):
            build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
                self.project_root, acceptance=object()
            )

    def test_contract_builder_calls_no_execution_or_writer(self) -> None:
        source = inspect.getsource(
            build_e1_common_probe_n2_r2_ec79_static_evaluation_contract
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
