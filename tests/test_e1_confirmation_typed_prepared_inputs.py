from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_av_history_permutation import (
    build_e1_av_history_permutation,
)
from mcm_field_organism.e1_confirmation_prepared_execution_bundle import (
    execute_prepared_bundle_synthetically,
)
from mcm_field_organism.e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from mcm_field_organism.e1_confirmation_typed_prepared_inputs import (
    E1ConfirmationTypedPreparedInputs,
    E1ConfirmationTypedPreparedInputsError,
    S1_EC2_INPUT_ROLES,
    prepare_e1_confirmation_typed_execution_bundle,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
)
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    _fresh_canonical_field,
)
from mcm_field_organism.e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
S1_EB_NAMES = {
    "e1_refined_confirmation_s1eb_once_v1.json",
    "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    "e1_refined_confirmation_s1eb_once_v1.lock",
}
CANONICAL_TARGETS = tuple(REPORTS / name for name in sorted(S1_EB_NAMES))


def _typed_inputs() -> E1ConfirmationTypedPreparedInputs:
    original_exists = Path.exists

    def preserve_terminal_attempt(path: Path) -> bool:
        if path.name in S1_EB_NAMES:
            return False
        return original_exists(path)

    with patch.object(Path, "exists", preserve_terminal_attempt):
        corridor = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)
    source = build_e1_av_history_permutation()
    ab = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    probe = _fixed_probe_sequences()
    probe_plans = build_e1_confirmation_refinement_plans(
        corridor,
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    field = _fresh_canonical_field(source)
    state = build_neutral_e1_state(
        field.layer,
        E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 1.5, 0.25, 0.5),
    )
    return E1ConfirmationTypedPreparedInputs(
        corridor=corridor,
        av_permutation=source,
        history_ab_plans=ab,
        history_ba_plans=ba,
        probe_sequences=probe,
        probe_plans=probe_plans,
        initial_field=field,
        initial_state=state,
    )


class E1ConfirmationTypedPreparedInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = _typed_inputs()

    def test_binds_all_typed_roles_once_and_preserves_identity(self) -> None:
        calls = []

        def resolver():
            calls.append("resolve")
            return self.inputs

        with TemporaryDirectory() as directory:
            bundle = prepare_e1_confirmation_typed_execution_bundle(
                Path(directory), resolver
            )

            self.assertEqual(["resolve"], calls)
            self.assertEqual(
                S1_EC2_INPUT_ROLES,
                tuple(role for role, _ in bundle.input_manifest),
            )
            for role in S1_EC2_INPUT_ROLES:
                self.assertIs(bundle.value(role), getattr(self.inputs, role))

    def test_typed_bundle_crosses_attempt_without_reconstruction(self) -> None:
        with TemporaryDirectory() as directory:
            bundle = prepare_e1_confirmation_typed_execution_bundle(
                Path(directory), lambda: self.inputs
            )

            def consumer(received):
                return hashlib.sha256(received.bundle_digest.encode("ascii")).hexdigest()

            receipt = execute_prepared_bundle_synthetically(bundle, consumer)

            self.assertEqual(bundle.bundle_digest, receipt.bundle_digest)
            self.assertFalse(receipt.canonical_execution_permitted)

    def test_swapped_history_plan_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationTypedPreparedInputsError,
            "history_ab source and plans do not match",
        ):
            replace(self.inputs, history_ab_plans=self.inputs.history_ba_plans)

    def test_non_neutral_state_is_rejected(self) -> None:
        first = self.inputs.initial_state.edge_bindings[0]
        changed_binding = replace(first, binding=0.1)
        changed_state = replace(
            self.inputs.initial_state,
            edge_bindings=(changed_binding,)
            + self.inputs.initial_state.edge_bindings[1:],
        )

        with self.assertRaisesRegex(
            E1ConfirmationTypedPreparedInputsError,
            "neutral initial field and E1 state",
        ):
            replace(self.inputs, initial_state=changed_state)

    def test_synthetic_adapter_does_not_touch_terminal_s1eb31_targets(self) -> None:
        before = tuple(
            (path.exists(), hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None)
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            prepare_e1_confirmation_typed_execution_bundle(
                Path(directory), lambda: self.inputs
            )
        after = tuple(
            (path.exists(), hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None)
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
