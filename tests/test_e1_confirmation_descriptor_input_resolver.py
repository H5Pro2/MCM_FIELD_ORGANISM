from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    build_e1_confirmation_descriptor_typed_inputs,
    prepare_e1_confirmation_descriptor_execution_bundle,
)
from mcm_field_organism.e1_confirmation_prepared_execution_bundle import (
    execute_prepared_bundle_synthetically,
)
from mcm_field_organism.e1_confirmation_typed_prepared_inputs import (
    S1_EC2_INPUT_ROLES,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationDescriptorInputResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = build_e1_confirmation_descriptor_typed_inputs(UPSTREAM)

    def test_builds_complete_descriptor_bound_input_set(self) -> None:
        descriptor_digest = self.inputs.corridor.digest()

        self.assertEqual(
            (descriptor_digest,) * 3,
            (
                self.inputs.history_ab_plans.research_descriptor_digest,
                self.inputs.history_ba_plans.research_descriptor_digest,
                self.inputs.probe_plans.research_descriptor_digest,
            ),
        )
        self.assertEqual(0, self.inputs.initial_field.layer.tick)
        self.assertIsNone(self.inputs.initial_field.last_distribution)
        self.assertIsNone(self.inputs.initial_field.substrate)
        self.assertTrue(
            all(
                item.binding == 0.0
                for item in self.inputs.initial_state.edge_bindings
            )
        )

    def test_resolver_source_has_no_legacy_corridor_builder(self) -> None:
        source = inspect.getsource(build_e1_confirmation_descriptor_typed_inputs)

        for forbidden in (
            "build_e1_refined_confirmation_contract",
            "E1RefinedConfirmationContract",
            ".report_path",
            "attempt_path",
            "lock_path",
            "e1_refined_confirmation_s1eb_once_v1",
        ):
            self.assertNotIn(forbidden, source)

    def test_each_top_level_builder_is_called_once(self) -> None:
        module = "mcm_field_organism.e1_confirmation_descriptor_input_resolver"
        with patch(
            module + ".build_e1_confirmation_research_corridor",
            wraps=__import__(
                module, fromlist=["build_e1_confirmation_research_corridor"]
            ).build_e1_confirmation_research_corridor,
        ) as corridor_builder, patch(
            module + ".build_e1_av_history_permutation",
            wraps=__import__(
                module, fromlist=["build_e1_av_history_permutation"]
            ).build_e1_av_history_permutation,
        ) as source_builder, patch(
            module + ".build_e1_confirmation_descriptor_refinement_plans",
            wraps=__import__(
                module,
                fromlist=["build_e1_confirmation_descriptor_refinement_plans"],
            ).build_e1_confirmation_descriptor_refinement_plans,
        ) as plan_builder:
            build_e1_confirmation_descriptor_typed_inputs(UPSTREAM)

        self.assertEqual(1, corridor_builder.call_count)
        self.assertEqual(1, source_builder.call_count)
        self.assertEqual(3, plan_builder.call_count)

    def test_direct_bundle_has_all_roles_and_crosses_synthetic_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            bundle = prepare_e1_confirmation_descriptor_execution_bundle(
                Path(directory), UPSTREAM
            )
            self.assertEqual(
                S1_EC2_INPUT_ROLES,
                tuple(role for role, _ in bundle.input_manifest),
            )
            receipt = execute_prepared_bundle_synthetically(
                bundle,
                lambda received: hashlib.sha256(
                    received.bundle_digest.encode("ascii")
                ).hexdigest(),
            )

            self.assertEqual(bundle.bundle_digest, receipt.bundle_digest)
            self.assertFalse(receipt.canonical_execution_permitted)

    def test_terminal_s1eb31_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            prepare_e1_confirmation_descriptor_execution_bundle(
                Path(directory), UPSTREAM
            )
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
