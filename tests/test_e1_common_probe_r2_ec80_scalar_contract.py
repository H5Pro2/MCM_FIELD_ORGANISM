from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    build_e1_common_probe_n2_r2_ec79_static_evaluation_contract,
)
from mcm_field_organism.e1_common_probe_n2_r2_positive_step_receipt_contract import (
    build_e1_common_probe_n2_r2_positive_step_receipt_fixture,
)
from mcm_field_organism.e1_common_probe_r2_ec80_scalar_contract import (
    E1CommonProbeR2EC80ScalarContractError,
    build_e1_common_probe_r2_ec80_scalar_receipt,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeR2EC80ScalarContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()
        cls.fixture = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(
            handoff
        )
        cls.boundary = (
            build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
                Path(__file__).resolve().parents[1]
            )
        )

    def test_eight_receipts_reduce_to_six_two_component_scalars(self) -> None:
        result = build_e1_common_probe_r2_ec80_scalar_receipt(
            self.boundary,
            self.fixture.probes,
            source_result_digest=self.fixture.result_digest,
        )

        self.assertEqual(8, result.probe_count)
        self.assertEqual(6, len(result.contrast_scalars))
        self.assertTrue(result.all_roles_exact_once)
        self.assertTrue(
            all(
                activation == 0.0 and afterimage == 0.0
                for _, activation, afterimage in result.contrast_scalars
            )
        )
        self.assertFalse(result.ec46_decision_permitted)
        self.assertFalse(result.field_execution_performed)

    def test_receipt_is_deterministic(self) -> None:
        first = build_e1_common_probe_r2_ec80_scalar_receipt(
            self.boundary,
            self.fixture.probes,
            source_result_digest=self.fixture.result_digest,
        )
        second = build_e1_common_probe_r2_ec80_scalar_receipt(
            self.boundary,
            self.fixture.probes,
            source_result_digest=self.fixture.result_digest,
        )
        self.assertEqual(first.receipt_digest, second.receipt_digest)

    def test_missing_or_reordered_role_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeR2EC80ScalarContractError, "eight ordered"
        ):
            build_e1_common_probe_r2_ec80_scalar_receipt(
                self.boundary,
                tuple(reversed(self.fixture.probes)),
                source_result_digest=self.fixture.result_digest,
            )

    def test_builder_calls_no_field_path_decider_or_writer(self) -> None:
        source = inspect.getsource(build_e1_common_probe_r2_ec80_scalar_receipt)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
