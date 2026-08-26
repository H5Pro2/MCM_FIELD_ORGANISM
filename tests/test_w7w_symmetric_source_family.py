from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.mcm_f3_controlled_history_source import (
    _combine_phase_sequences,
    mcm_f3_receptor_sequences_digest,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7r_p0_s_completion_producer import (
    W7RP0SCompletionProducerError,
    build_initial_w7r_p0_state,
    produce_w7r_p0_s_completion_states,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    W7WSymmetricSourceFamilyError,
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
    w7w_base_source_inventory_digest,
)


def _intervals(steps) -> tuple[tuple[int, int], ...]:
    return tuple(
        (
            min(
                item.field_time.window_start_tick
                for sequence in step
                for item in sequence.frames
            ),
            max(
                item.field_time.window_end_tick
                for sequence in step
                for item in sequence.frames
            ),
        )
        for step in steps
    )


class W7WSymmetricSourceFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(
            cls.adapter,
            cls.family,
        )

    def test_additive_steps_have_exact_intervals_and_counts(self) -> None:
        self.assertEqual(
            (
                (0, 1_000_000),
                (1_000_000, 2_000_000),
                (2_000_000, 3_000_000),
                (3_000_000, 4_000_000),
            ),
            _intervals(self.family.b_prefix_steps),
        )
        self.assertEqual(
            (
                (4_000_000, 5_000_000),
                (5_000_000, 6_000_000),
                (6_000_000, 7_000_000),
                (7_000_000, 8_000_000),
            ),
            _intervals(self.family.a_continuation_steps),
        )
        self.assertEqual(4, len(self.family.b_prefix_step_digests))
        self.assertEqual(4, len(self.family.a_continuation_step_digests))

    def test_combined_b_prefix_is_lossless(self) -> None:
        combined = _combine_phase_sequences(self.family.b_prefix_steps)

        self.assertEqual(self.family.b_prefix, combined)
        self.assertEqual(
            self.family.b_prefix_digest,
            mcm_f3_receptor_sequences_digest(combined),
        )
        for modality_index in range(2):
            self.assertEqual(
                sum(
                    len(step[modality_index].frames)
                    for step in self.family.b_prefix_steps
                ),
                len(self.family.b_prefix[modality_index].frames),
            )

    def test_technical_support_matches_without_value_equality(self) -> None:
        self.assertTrue(self.family.prefix_support_matches)
        self.assertTrue(self.family.continuation_support_matches)
        self.assertNotEqual(
            self.adapter.source.contact_a_digest,
            self.family.b_prefix_digest,
        )
        self.assertNotEqual(
            self.adapter.source.contact_b_step_digests,
            self.family.a_continuation_step_digests,
        )

    def test_snapshot_namespaces_are_distinct(self) -> None:
        existing = {
            item.frame.snapshot_id
            for sequence in self.adapter.source.contact_a
            for item in sequence.frames
        }
        additive = {
            item.frame.snapshot_id
            for sequence in self.family.b_prefix
            for item in sequence.frames
        }

        self.assertTrue(additive)
        self.assertFalse(existing & additive)
        self.assertTrue(
            all(item.startswith("w7v.contact-b-prefix.") for item in additive)
        )

    def test_existing_matrix_regions_and_source_inventory_remain_frozen(self) -> None:
        self.assertEqual(
            "a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a",
            self.adapter.matrix_digest,
        )
        self.assertEqual(
            "e88fd217abd969af87e28d4e0faee7364930f6fc3a1f0d21cd908874ca51bbf2",
            self.adapter.regions.region_digest,
        )
        self.assertEqual(
            self.family.base_source_inventory_digest,
            w7w_base_source_inventory_digest(self.adapter.source),
        )

    def test_seven_path_inventory_is_complete_and_unique(self) -> None:
        paths = {item.path_id: item for item in self.family.paths}

        self.assertEqual(
            {"ab", "ag", "ba", "bg", "ua", "ub", "ug"},
            set(paths),
        )
        self.assertEqual(
            (self.family.b_prefix_digest,),
            paths["ba"].prefix_digests,
        )
        self.assertEqual(
            self.family.a_continuation_step_digests,
            paths["ua"].continuation_digests,
        )
        self.assertEqual((), paths["ug"].prefix_digests)
        self.assertTrue(
            all(
                item.probe_digests == self.adapter.source.probe_digests
                for item in paths.values()
            )
        )

    def test_family_and_authorization_are_exactly_deterministic(self) -> None:
        repeated_family = build_w7w_symmetric_source_family(self.adapter)
        repeated_authorization = build_w7w_source_authorization(
            self.adapter,
            repeated_family,
        )

        self.assertEqual(
            self.family.symmetric_inventory_digest,
            repeated_family.symmetric_inventory_digest,
        )
        self.assertEqual(
            self.authorization.authorization_digest,
            repeated_authorization.authorization_digest,
        )
        self.assertEqual(9, len(self.authorization.roles))

    def test_w7r_accepts_one_explicitly_authorized_additive_segment(self) -> None:
        initial = build_initial_w7r_p0_state(self.adapter, "ua", 4_000_000)
        result = produce_w7r_p0_s_completion_states(
            self.adapter,
            self.family.a_continuation_step_digests[0],
            self.family.a_continuation_steps[0],
            (4_000_000, 5_000_000),
            initial,
            source_authorization=self.authorization,
        )

        self.assertEqual("ua", result.source_path_id)
        self.assertEqual(5_000_000, result.end_state.end_tick)
        self.assertEqual(
            self.family.a_continuation_step_digests[0],
            result.source_digest,
        )

    def test_w7r_keeps_additive_sources_closed_without_authorization(self) -> None:
        initial = build_initial_w7r_p0_state(self.adapter, "ua", 4_000_000)

        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "not bound"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.family.a_continuation_step_digests[0],
                self.family.a_continuation_steps[0],
                (4_000_000, 5_000_000),
                initial,
            )

    def test_w7r_rejects_wrong_additive_path_and_interval(self) -> None:
        wrong_path = build_initial_w7r_p0_state(self.adapter, "ab", 4_000_000)
        with self.assertRaisesRegex(
            W7RP0SCompletionProducerError,
            "path or interval",
        ):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.family.a_continuation_step_digests[0],
                self.family.a_continuation_steps[0],
                (4_000_000, 5_000_000),
                wrong_path,
                source_authorization=self.authorization,
            )

        wrong_interval = build_initial_w7r_p0_state(self.adapter, "ba", 1_000_000)
        with self.assertRaisesRegex(
            W7RP0SCompletionProducerError,
            "path or interval",
        ):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.family.b_prefix_step_digests[0],
                self.family.b_prefix_steps[0],
                (1_000_000, 2_000_000),
                wrong_interval,
                source_authorization=self.authorization,
            )

    def test_changed_sequence_and_tampered_bindings_are_rejected(self) -> None:
        initial = build_initial_w7r_p0_state(self.adapter, "ua", 4_000_000)
        auditory, visual = self.family.a_continuation_steps[0]
        changed = replace(auditory, frames=auditory.frames[:-1])
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "source digest"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.family.a_continuation_step_digests[0],
                (changed, visual),
                (4_000_000, 5_000_000),
                initial,
                source_authorization=self.authorization,
            )
        with self.assertRaisesRegex(
            W7WSymmetricSourceFamilyError,
            "authorization digest",
        ):
            replace(self.authorization, authorization_digest="changed")
        with self.assertRaisesRegex(
            W7WSymmetricSourceFamilyError,
            "inventory digest",
        ):
            replace(self.family, symmetric_inventory_digest="changed")

    def test_w7w_is_not_reexported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        for name in (
            "build_w7w_symmetric_source_family",
            "build_w7w_source_authorization",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
