from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_corrected_final_preflight import (
    audit_e1_common_probe_n2_r2_corrected_final_preflight,
)
from mcm_field_organism.e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
    prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract,
)
from mcm_field_organism.e1_common_probe_n2_r2_ec75_synthetic_route import (
    run_e1_common_probe_n2_r2_ec75_synthetic_route,
)
from mcm_field_organism.e1_common_probe_n2_r2_ec77_final_release_gate import (
    E1CommonProbeN2R2EC77FinalReleaseGateError,
    S1_EC77_EC74_REPORT_RELATIVE_PATH,
    prepare_e1_common_probe_n2_r2_ec77_final_release_gate,
)


class E1CommonProbeN2R2EC77FinalReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_corrected_final_preflight import (
            E1CommonProbeN2R2CorrectedFinalPreflightTests,
        )

        E1CommonProbeN2R2CorrectedFinalPreflightTests.setUpClass()
        source = E1CommonProbeN2R2CorrectedFinalPreflightTests()
        cls.project_root = Path(__file__).resolve().parents[1]
        cls.preflight = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            source.source._audit(), source.integrity
        )
        cls.contract = prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(
            cls.preflight
        )
        cls.route = run_e1_common_probe_n2_r2_ec75_synthetic_route(
            source.source.handoff
        )

    def test_gate_is_ready_to_request_but_remains_closed(self) -> None:
        gate = prepare_e1_common_probe_n2_r2_ec77_final_release_gate(
            self.project_root, self.route, self.preflight, self.contract
        )

        self.assertTrue(gate.technical_one_shot_request_ready)
        self.assertTrue(gate.prior_ec74_authorization_consumed)
        self.assertFalse(gate.owner_authorization_present)
        self.assertFalse(gate.execution_permitted)
        self.assertFalse(gate.automatic_retry_permitted)

    def test_changed_ec74_report_fails_closed(self) -> None:
        source = self.project_root / S1_EC77_EC74_REPORT_RELATIVE_PATH
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / S1_EC77_EC74_REPORT_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            target.write_text(
                target.read_text(encoding="utf-8") + "\nsynthetic mutation\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                E1CommonProbeN2R2EC77FinalReleaseGateError,
                "evidence is incomplete",
            ):
                prepare_e1_common_probe_n2_r2_ec77_final_release_gate(
                    root, self.route, self.preflight, self.contract
                )

    def test_gate_rejects_missing_typed_inputs(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeN2R2EC77FinalReleaseGateError,
            "validated EC76, EC72, and EC73",
        ):
            prepare_e1_common_probe_n2_r2_ec77_final_release_gate(
                self.project_root, None, self.preflight, self.contract
            )

    def test_gate_accepts_no_authorization_and_calls_no_real_path(self) -> None:
        function = prepare_e1_common_probe_n2_r2_ec77_final_release_gate
        self.assertEqual(
            ("project_root", "route", "preflight", "contract"),
            tuple(inspect.signature(function).parameters),
        )
        source = inspect.getsource(function)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "owner_authorized",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
