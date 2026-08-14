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
from mcm_field_organism.e1_common_probe_r2_ec81_nonzero_fixture import (
    S1_EC81_EXPECTED_SCALARS,
    run_e1_common_probe_r2_ec81_nonzero_fixture,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeR2EC81NonzeroFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()
        cls.source = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(
            handoff
        )
        cls.boundary = (
            build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
                Path(__file__).resolve().parents[1]
            )
        )

    def test_all_six_nonzero_contrasts_are_exact(self) -> None:
        result = run_e1_common_probe_r2_ec81_nonzero_fixture(
            self.boundary, self.source.probes
        )

        self.assertEqual(S1_EC81_EXPECTED_SCALARS, result.observed_scalars)
        self.assertTrue(result.all_six_contrasts_exact)
        self.assertTrue(result.activation_afterimage_separate)
        self.assertEqual(0, result.actual_field_steps_executed)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_r2_ec81_nonzero_fixture(
            self.boundary, self.source.probes
        )
        second = run_e1_common_probe_r2_ec81_nonzero_fixture(
            self.boundary, self.source.probes
        )
        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(first.scalar_receipt_digest, second.scalar_receipt_digest)

    def test_source_has_no_field_path_decider_or_writer(self) -> None:
        source = inspect.getsource(run_e1_common_probe_r2_ec81_nonzero_fixture)
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
