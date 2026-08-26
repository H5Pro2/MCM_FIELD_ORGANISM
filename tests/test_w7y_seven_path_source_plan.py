from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.mcm_f3_controlled_history_source import (
    mcm_f3_receptor_sequences_digest,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    W7YSevenPathSourcePlanError,
    build_w7y_seven_path_source_plan,
)


class W7YSevenPathSourcePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(
            cls.adapter,
            cls.family,
        )
        cls.plan = build_w7y_seven_path_source_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
        )

    def test_global_plan_bindings_and_digest_are_frozen(self) -> None:
        self.assertEqual("w7y.seven-path-source-plan.v1", self.plan.plan_id)
        self.assertEqual(self.adapter.matrix_digest, self.plan.matrix_digest)
        self.assertEqual(
            self.adapter.regions.region_digest,
            self.plan.region_digest,
        )
        self.assertEqual(
            self.family.symmetric_inventory_digest,
            self.plan.symmetric_inventory_digest,
        )
        self.assertEqual(
            self.authorization.authorization_digest,
            self.plan.authorization_digest,
        )
        self.assertEqual(
            "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32",
            self.plan.seven_path_plan_digest,
        )

    def test_exactly_seven_canonical_paths_are_present(self) -> None:
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            tuple(item.path_id for item in self.plan.paths),
        )
        self.assertEqual(7, len({item.path_plan_digest for item in self.plan.paths}))
        self.assertTrue(
            all(
                len(item.continuations) == 4 and len(item.checkpoints) == 5
                for item in self.plan.paths
            )
        )

    def test_prefix_and_continuation_roles_match_every_path(self) -> None:
        paths = {item.path_id: item for item in self.plan.paths}
        expected = {
            "ab": ("existing.a.combined", "existing.b.step"),
            "ag": ("existing.a.combined", "existing.g.step"),
            "ba": ("additive.b.combined", "additive.a.step"),
            "bg": ("additive.b.combined", "existing.g.step"),
            "ua": (None, "additive.a.step"),
            "ub": (None, "existing.b.step"),
            "ug": (None, "existing.g.step"),
        }
        for path_id, (prefix_role, continuation_role) in expected.items():
            path = paths[path_id]
            self.assertEqual(
                prefix_role,
                None if path.prefix is None else path.prefix.source_role,
            )
            self.assertEqual(
                tuple(f"{continuation_role}.{index}" for index in range(4)),
                tuple(item.source_role for item in path.continuations),
            )

    def test_main_timeline_is_contiguous_and_exact(self) -> None:
        expected = tuple(
            ((index + 4) * 1_000_000, (index + 5) * 1_000_000)
            for index in range(4)
        )
        for path in self.plan.paths:
            self.assertEqual(
                expected,
                tuple(item.interval for item in path.continuations),
            )
            if path.prefix is not None:
                self.assertEqual((0, 4_000_000), path.prefix.interval)

    def test_uniform_paths_have_no_materialized_source_segment(self) -> None:
        for path in self.plan.paths:
            if path.path_id.startswith("u"):
                self.assertIsNone(path.prefix)
                self.assertIsNotNone(path.uniform_start)
                self.assertEqual(4_000_000, path.uniform_start.tick)
                self.assertFalse(hasattr(path.uniform_start, "sequences"))
            else:
                self.assertIsNotNone(path.prefix)
                self.assertIsNone(path.uniform_start)

    def test_checkpoints_bind_main_predecessors_without_state_values(self) -> None:
        for path in self.plan.paths:
            first_predecessor = (
                path.prefix.segment_id
                if path.prefix is not None
                else path.uniform_start.start_id
            )
            self.assertEqual(
                first_predecessor,
                path.checkpoints[0].main_predecessor_id,
            )
            self.assertEqual(
                tuple(item.segment_id for item in path.continuations),
                tuple(
                    item.main_predecessor_id for item in path.checkpoints[1:]
                ),
            )
            self.assertTrue(
                all(not hasattr(item, "state") for item in path.checkpoints)
            )

    def test_each_checkpoint_has_one_isolated_probe_reference(self) -> None:
        for path in self.plan.paths:
            self.assertEqual(
                tuple(range(5)),
                tuple(item.checkpoint for item in path.checkpoints),
            )
            self.assertEqual(
                tuple((index + 4) * 1_000_000 for index in range(5)),
                tuple(item.tick for item in path.checkpoints),
            )
            for index, checkpoint in enumerate(path.checkpoints):
                self.assertEqual("probe", checkpoint.probe.branch_kind)
                self.assertEqual(
                    f"existing.probe.{index}",
                    checkpoint.probe.source_role,
                )
                self.assertEqual(
                    (checkpoint.tick, checkpoint.tick + 1_000_000),
                    checkpoint.probe.interval,
                )
                self.assertNotIn(
                    checkpoint.probe.segment_id,
                    {item.segment_id for item in path.continuations},
                )

    def test_additive_segments_carry_exact_authorization_roles(self) -> None:
        paths = {item.path_id: item for item in self.plan.paths}
        for path_id in ("ba", "bg"):
            self.assertEqual(
                "w7v.contact-b-prefix.combined.v1",
                paths[path_id].prefix.authorization_role_id,
            )
        for path_id in ("ba", "ua"):
            self.assertEqual(
                tuple(
                    f"w7v.contact-a-continuation.steps.v1.{index}"
                    for index in range(4)
                ),
                tuple(
                    item.authorization_role_id
                    for item in paths[path_id].continuations
                ),
            )
        self.assertTrue(
            all(
                checkpoint.probe.authorization_role_id is None
                for path in self.plan.paths
                for checkpoint in path.checkpoints
            )
        )

    def test_every_segment_reference_matches_its_actual_sequences(self) -> None:
        for path in self.plan.paths:
            segments = (
                (() if path.prefix is None else (path.prefix,))
                + path.continuations
                + tuple(item.probe for item in path.checkpoints)
            )
            for segment in segments:
                self.assertEqual(
                    segment.source_digest,
                    mcm_f3_receptor_sequences_digest(segment.sequences),
                )

    def test_repeated_build_is_exact_and_does_not_advance_the_field(self) -> None:
        before_field = self.adapter.initial_field
        before_layer = before_field.layer.digest()
        repeated = build_w7y_seven_path_source_plan(
            self.adapter,
            self.family,
            self.authorization,
        )

        self.assertEqual(
            self.plan.seven_path_plan_digest,
            repeated.seven_path_plan_digest,
        )
        self.assertEqual(self.plan.paths, repeated.paths)
        self.assertIs(before_field, self.adapter.initial_field)
        self.assertEqual(before_layer, self.adapter.initial_field.layer.digest())
        self.assertIsNone(self.adapter.initial_field.last_distribution)
        self.assertFalse(hasattr(self.plan, "run"))
        self.assertFalse(hasattr(self.plan, "execute"))

    def test_tampered_segment_checkpoint_and_path_digests_are_rejected(self) -> None:
        path = self.plan.paths[0]
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "segment digest",
        ):
            replace(path.prefix, segment_digest="changed")
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "checkpoint digest",
        ):
            replace(path.checkpoints[0], checkpoint_digest="changed")
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "path plan digest",
        ):
            replace(path, path_plan_digest="changed")
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "seven-path plan digest",
        ):
            replace(self.plan, seven_path_plan_digest="changed")

    def test_changed_sequences_and_wrong_inventory_objects_are_rejected(self) -> None:
        segment = self.plan.paths[0].prefix
        auditory, visual = segment.sequences
        changed = replace(auditory, frames=auditory.frames[:-1])
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "sequences differ",
        ):
            replace(segment, sequences=(changed, visual))
        with self.assertRaisesRegex(
            W7YSevenPathSourcePlanError,
            "requires one adapter",
        ):
            build_w7y_seven_path_source_plan(
                self.adapter,
                self.family,
                object(),
            )

    def test_module_is_not_reexported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        for name in ("build_w7y_seven_path_source_plan", "W7YPathPlan"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
