from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_corrected_final_preflight import (
    audit_e1_common_probe_n2_r2_corrected_final_preflight,
)
from mcm_field_organism.e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
    E1CommonProbeN2R2DiagnosticOneShotContractError,
    prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_output_converters import (
    S1_EC70_FORMATION_DIAGNOSTIC_GATES,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)


class E1CommonProbeN2R2DiagnosticOneShotContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_corrected_final_preflight import (
            E1CommonProbeN2R2CorrectedFinalPreflightTests,
        )

        E1CommonProbeN2R2CorrectedFinalPreflightTests.setUpClass()
        source = E1CommonProbeN2R2CorrectedFinalPreflightTests()
        cls.source = source
        cls.preflight = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            source.source._audit(), source.integrity
        )

    def test_contract_binds_one_closed_diagnostic_attempt(self) -> None:
        contract = prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(
            self.preflight
        )

        self.assertEqual((1, 0), (
            contract.planned_execution_count,
            contract.authorized_execution_count,
        ))
        self.assertEqual(3208, contract.maximum_total_field_steps)
        self.assertEqual(402, contract.first_formation_arm_steps)
        self.assertEqual(
            S1_EC70_FORMATION_DIAGNOSTIC_GATES,
            contract.diagnostic_gate_names,
        )
        self.assertTrue(contract.stop_on_first_failed_diagnostic_gate)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.automatic_retry_permitted)

    def test_contract_requires_separated_reporting_and_forbids_claims(self) -> None:
        contract = prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(
            self.preflight
        )

        self.assertEqual(
            (
                "measurement",
                "technical-interpretation",
                "non-evidence",
                "open-assumptions",
            ),
            contract.report_sections,
        )
        self.assertFalse(contract.raw_output_persistence_permitted)
        self.assertFalse(contract.research_decision_permitted)
        self.assertFalse(contract.memory_claim_permitted)
        self.assertFalse(contract.field_time_claim_permitted)
        self.assertFalse(contract.organization_claim_permitted)
        self.assertFalse(contract.ai_claim_permitted)

    def test_unready_ec72_is_rejected(self) -> None:
        low_memory = E1PilotRealResourceSnapshot(
            4 * 1024**3 - 1,
            self.source.source.resources.free_disk_bytes,
        )
        unready = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            self.source.source._audit(resources=low_memory),
            self.source.integrity,
        )

        with self.assertRaisesRegex(
            E1CommonProbeN2R2DiagnosticOneShotContractError,
            "ready but unreleased EC72",
        ):
            prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(unready)

    def test_builder_accepts_no_authorization_and_calls_no_real_path(self) -> None:
        function = prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract
        self.assertEqual(("preflight",), tuple(inspect.signature(function).parameters))
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
