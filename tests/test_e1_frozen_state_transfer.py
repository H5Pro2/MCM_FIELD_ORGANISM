from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer import (
    E1FrozenStateTransferError,
    E1FrozenStateTransferResult,
    SyntheticE1FrozenStateSource,
    load_e1_frozen_states,
    run_synthetic_e1_frozen_state_transfer_arms,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import S1_DK_ARMS
from mcm_field_organism.e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_frozen_transient_probe import nonuniform_state, probe_inputs


REPORT = Path("reports/e1_a0_av_history_s1di_once_v1.json")


def synthetic_source():
    field, _, _ = probe_inputs()
    left = nonuniform_state(field)
    first = left.edge_bindings[0]
    right = E1LocalEdgePlasticityState(
        contract=left.contract,
        edge_bindings=(
            E1EdgeBinding(
                first.first_neuron_id,
                first.second_neuron_id,
                first.binding * 0.25,
            ),
        ),
        edge_inventory_digest=left.edge_inventory_digest,
    )
    return SyntheticE1FrozenStateSource("synthetic-s1dl-only", left, right)


class E1FrozenStateTransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field, self.distribution, self.transient_inputs = probe_inputs()
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def run_synthetic(self) -> E1FrozenStateTransferResult:
        return run_synthetic_e1_frozen_state_transfer_arms(
            synthetic_source(),
            lambda: probe_inputs()[0],
            self.distribution,
            self.transient_inputs,
            self.substrate,
            self.afterimage,
        )

    def test_loader_reconstructs_the_published_states_without_probe(self) -> None:
        loaded = load_e1_frozen_states(REPORT)

        self.assertEqual(145, len(loaded.b_ab.edge_bindings))
        self.assertEqual(145, len(loaded.b_ba.edge_bindings))
        self.assertNotEqual(loaded.b_ab, loaded.b_ba)
        self.assertFalse(loaded.contract.probe_execution_permitted)
        self.assertEqual(
            "4574cf1caae3792a3721249dac73b4a589062051bb944fcf2f43f317b4e347f8",
            loaded.contract.digest(),
        )

    def test_synthetic_compositor_runs_all_seven_control_arms(self) -> None:
        result = self.run_synthetic()

        self.assertEqual(S1_DK_ARMS, tuple(item.arm_id for item in result.arms))
        self.assertEqual(0.0, result.d_ablation)
        self.assertEqual(0.0, result.d_fixed_adapter)
        self.assertEqual(0.0, result.frozen_state_change)
        self.assertGreater(max(result.d_active_s, result.d_active_h), 0.0)

    def test_ablated_and_fixed_adapter_snapshot_identities_hold(self) -> None:
        result = self.run_synthetic()

        p0 = result.by_id("p0").field.snapshot().digest()
        self.assertEqual(p0, result.by_id("ab0").field.snapshot().digest())
        self.assertEqual(p0, result.by_id("ba0").field.snapshot().digest())
        self.assertEqual(
            result.by_id("ab1").field.snapshot().digest(),
            result.by_id("abf").field.snapshot().digest(),
        )
        self.assertEqual(
            result.by_id("ba1").field.snapshot().digest(),
            result.by_id("baf").field.snapshot().digest(),
        )

    def test_frozen_state_objects_are_reused_without_change(self) -> None:
        source = synthetic_source()
        result = run_synthetic_e1_frozen_state_transfer_arms(
            source,
            lambda: probe_inputs()[0],
            self.distribution,
            self.transient_inputs,
            self.substrate,
            self.afterimage,
        )

        for arm_id in ("ab0", "ab1", "abf"):
            self.assertIs(source.b_ab, result.by_id(arm_id).frozen_state)
        for arm_id in ("ba0", "ba1", "baf"):
            self.assertIs(source.b_ba, result.by_id(arm_id).frozen_state)

    def test_factory_must_return_fresh_identical_fields(self) -> None:
        source = synthetic_source()
        with self.assertRaisesRegex(E1FrozenStateTransferError, "fresh field"):
            run_synthetic_e1_frozen_state_transfer_arms(
                source,
                lambda: self.field,
                self.distribution,
                self.transient_inputs,
                self.substrate,
                self.afterimage,
            )

    def test_canonical_loaded_states_cannot_enter_synthetic_runner(self) -> None:
        loaded = load_e1_frozen_states(REPORT)
        calls = 0

        def forbidden_factory():
            nonlocal calls
            calls += 1
            return probe_inputs()[0]

        with self.assertRaisesRegex(E1FrozenStateTransferError, "only a synthetic"):
            run_synthetic_e1_frozen_state_transfer_arms(
                loaded,  # type: ignore[arg-type]
                forbidden_factory,
                self.distribution,
                self.transient_inputs,
                self.substrate,
                self.afterimage,
            )
        self.assertEqual(0, calls)

    def test_result_fails_closed_when_control_residual_is_relabelled(self) -> None:
        result = self.run_synthetic()

        with self.assertRaisesRegex(E1FrozenStateTransferError, "identity failed"):
            replace(result, d_ablation=1e-12)
        with self.assertRaisesRegex(E1FrozenStateTransferError, "identity failed"):
            replace(result, d_fixed_adapter=1e-12)
        with self.assertRaisesRegex(E1FrozenStateTransferError, "state changed"):
            replace(result, frozen_state_change=1e-12)

    def test_loader_runner_and_result_roles_remain_private(self) -> None:
        source = inspect.getsource(load_e1_frozen_states)
        for forbidden in (
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_fixed_e1_adapter_fast_shared_field_transient",
            "run_e1_asynchronous_field",
            "produce_e1_a0_av_histories",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "LoadedE1FrozenStates",
            "SyntheticE1FrozenStateSource",
            "E1FrozenStateTransferResult",
            "load_e1_frozen_states",
            "run_synthetic_e1_frozen_state_transfer_arms",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
