from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    build_e1_common_probe_n2_r2_ec79_static_evaluation_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec82_coordinator_handoff import (
    build_e1_common_probe_r2_ec82_coordinator_handoff_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec83_one_shot_measurement_contract import (
    build_e1_common_probe_r2_ec83_one_shot_measurement_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec84_atomic_return import (
    E1CommonProbeR2EC84AtomicReturnError,
    build_e1_common_probe_r2_ec84_atomic_return,
)
from tests.test_e1_common_probe_r2_ec82_coordinator_handoff import (
    E1CommonProbeR2EC82CoordinatorHandoffTests,
)


class E1CommonProbeR2EC84AtomicReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeR2EC82CoordinatorHandoffTests.setUpClass()
        cls.completed = (
            E1CommonProbeR2EC82CoordinatorHandoffTests.typed_shape_fixture
        )
        cls.boundary = build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
            cls.root
        )
        cls.handoff = build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
            cls.root
        )
        cls.contract = build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
            cls.root, cls.handoff
        )

    def test_result_and_scalar_receipt_are_returned_together(self) -> None:
        result = build_e1_common_probe_r2_ec84_atomic_return(
            self.contract, self.handoff, self.boundary, self.completed
        )
        self.assertTrue(result.result_and_scalars_returned_together)
        self.assertEqual(
            result.coordinator_result_digest,
            result.scalar_receipt.source_result_digest,
        )
        self.assertEqual(6, result.scalar_contrast_count)
        self.assertFalse(result.additional_field_execution_performed)
        self.assertFalse(result.ec46_decision_permitted)

    def test_atomic_return_is_deterministic(self) -> None:
        first = build_e1_common_probe_r2_ec84_atomic_return(
            self.contract, self.handoff, self.boundary, self.completed
        )
        second = build_e1_common_probe_r2_ec84_atomic_return(
            self.contract, self.handoff, self.boundary, self.completed
        )
        self.assertEqual(first.return_digest, second.return_digest)

    def test_missing_completed_result_fails_before_any_return(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeR2EC84AtomicReturnError, "already completed"
        ):
            build_e1_common_probe_r2_ec84_atomic_return(
                self.contract, self.handoff, self.boundary, object()
            )

    def test_wrapper_calls_no_coordinator_decider_or_writer(self) -> None:
        source = inspect.getsource(build_e1_common_probe_r2_ec84_atomic_return)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
