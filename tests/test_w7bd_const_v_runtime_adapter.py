from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import (
    W7BCConstVTrajectoryContractError,
    build_w7bc_const_v_r124_trajectory_contract,
)
from mcm_field_organism.w7bd_const_v_runtime_adapter import (
    W7BDConstVRuntimeAdapterError,
    advance_w7bd_const_v_transient,
    build_w7bd_const_v_runtime_adapter,
    prepare_w7bd_const_v_initial_field,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7n_capacity_function_baselines import (
    compute_w7n_coupling_baseline,
)


class W7BDConstVRuntimeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_w7m_capacity_function_matrix_adapter()
        cls.contract = build_w7bc_const_v_r124_trajectory_contract()
        cls.adapter = build_w7bd_const_v_runtime_adapter(
            cls.matrix,
            cls.contract,
        )

    def test_adapter_binds_only_the_registered_const_v_spec(self) -> None:
        self.assertEqual("const-v", self.adapter.baseline_spec.model_id)
        self.assertEqual("w7n.const-v", self.adapter.arm_id)
        self.assertEqual(1.0, self.adapter.substrate_config.response_time_seconds)
        self.assertEqual(0.5, self.adapter.afterimage_config.time_constant_seconds)
        self.assertEqual(0.0, self.adapter.dissipation_per_second)
        self.assertEqual(
            "read-only-copies-and-no-return",
            self.adapter.state_observer_policy,
        )
        self.assertFalse(self.adapter.public_export_allowed)
        self.assertEqual(
            "496a795531ce61222fdfea7571f6c34079d5a6f1eb52b56798970a5de3e458db",
            self.adapter.adapter_digest,
        )

    def test_initial_state_replaces_cap_arm_before_runtime(self) -> None:
        initial = prepare_w7bd_const_v_initial_field(self.matrix, self.adapter)

        self.assertIsNot(initial, self.matrix.initial_field)
        self.assertIsNot(initial.substrate, self.matrix.initial_field.substrate)
        self.assertEqual("w7n.const-v", initial.substrate.arm.arm_id)
        self.assertEqual(0.5, initial.substrate.arm.lambda_sm_per_second)
        self.assertEqual(0.5, initial.substrate.arm.kappa)
        self.assertEqual(1.0, initial.substrate.arm.eta)
        self.assertEqual(
            self.matrix.initial_field.substrate.masses,
            initial.substrate.masses,
        )
        self.assertEqual("w7m.cap", self.matrix.initial_field.substrate.arm.arm_id)

    def test_injected_kernel_matches_canonical_w7n_derivative(self) -> None:
        initial = prepare_w7bd_const_v_initial_field(self.matrix, self.adapter)
        expected = compute_w7n_coupling_baseline(
            self.adapter.baseline_spec,
            initial.layer,
            initial.substrate,
        )
        sentinel = object()

        with patch(
            "mcm_field_organism.w7bd_const_v_runtime_adapter."
            "advance_mcm_f3_shared_field_transient",
            return_value=sentinel,
        ) as runtime:
            observed = advance_w7bd_const_v_transient(
                self.adapter,
                initial,
                object(),
                object(),
                refinement=2,
            )

        self.assertIs(sentinel, observed)
        args = runtime.call_args.args
        kwargs = runtime.call_args.kwargs
        self.assertIs(initial, args[0])
        self.assertIsNone(args[5])
        self.assertEqual(2, kwargs["refinement"])
        self.assertIsNone(kwargs["_state_observer"])
        actual = kwargs["_coupling_calculator"](
            initial.layer,
            initial.substrate,
        )
        self.assertEqual(expected, actual)

    def test_cap_arm_is_rejected_at_runtime_boundary(self) -> None:
        with self.assertRaises(W7BDConstVRuntimeAdapterError):
            advance_w7bd_const_v_transient(
                self.adapter,
                self.matrix.initial_field,
                object(),
                object(),
                refinement=1,
            )

    def test_contract_or_adapter_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7BCConstVTrajectoryContractError):
            replace(self.contract, model_id="cap")
        with self.assertRaises(W7BDConstVRuntimeAdapterError):
            replace(self.adapter, dissipation_per_second=0.1)

    def test_adapter_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7bd_const_v_runtime_adapter")
        )
        self.assertFalse(
            hasattr(current_api, "advance_w7bd_const_v_transient")
        )


if __name__ == "__main__":
    unittest.main()
