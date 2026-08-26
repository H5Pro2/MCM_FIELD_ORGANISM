from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7r_p0_s_completion_producer import (
    W7RP0SCompletionProducerError,
    build_initial_w7r_p0_state,
    compose_w7r_observer_driver,
    produce_w7r_p0_s_completion_states,
)


class W7RP0SCompletionProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.source = cls.adapter.source
        cls.initial = build_initial_w7r_p0_state(cls.adapter, "ub", 4_000_000)
        cls.first = produce_w7r_p0_s_completion_states(
            cls.adapter,
            cls.source.contact_b_step_digests[0],
            cls.source.contact_b_steps[0],
            (4_000_000, 5_000_000),
            cls.initial,
        )

    def test_initial_state_is_zero_and_has_no_substrate(self) -> None:
        state = self.initial

        self.assertEqual(84, len(state.neuron_ids))
        self.assertEqual((0.0,) * 84, state.s_values)
        self.assertEqual((0.0,) * 84, state.h_values)
        self.assertIsNone(state.p0_field.substrate)
        self.assertIsNone(state.p0_field.development)
        self.assertIsNone(state.p0_field.last_distribution)

    def test_one_segment_assigns_every_event_and_emits_atomic_ticks(self) -> None:
        result = self.first

        self.assertEqual(
            sum(len(sequence.frames) for sequence in self.source.contact_b_steps[0]),
            result.assigned_event_count,
        )
        self.assertEqual(
            len(result.event_states),
            len({item.completion_tick for item in result.event_states}),
        )
        self.assertEqual(
            tuple(sorted(item.completion_tick for item in result.event_states)),
            tuple(item.completion_tick for item in result.event_states),
        )
        self.assertEqual(5_000_000, result.end_state.end_tick)
        self.assertEqual(1, result.end_state.p0_field.layer.tick)
        self.assertIsNone(result.end_state.p0_field.substrate)

    def test_w7p_driver_uses_event_states_and_exact_terminal_state(self) -> None:
        driver = compose_w7r_observer_driver(self.adapter, self.first)

        self.assertEqual(self.adapter.matrix_digest, driver.matrix_digest)
        self.assertEqual(self.first.source_digest, driver.source_digest)
        self.assertEqual(self.first.initial_state.s_values, driver.segments[0].s_values)
        self.assertEqual(self.first.end_state.s_values, driver.terminal_s_values)
        self.assertEqual(4_000_000, driver.segments[0].start_tick)
        self.assertEqual(5_000_000, driver.segments[-1].end_tick)

    def test_production_is_exactly_deterministic(self) -> None:
        repeated = produce_w7r_p0_s_completion_states(
            self.adapter,
            self.source.contact_b_step_digests[0],
            self.source.contact_b_steps[0],
            (4_000_000, 5_000_000),
            self.initial,
        )

        self.assertEqual(self.first.production_digest, repeated.production_digest)
        self.assertEqual(self.first.event_states, repeated.event_states)
        self.assertEqual(self.first.end_state.state_digest, repeated.end_state.state_digest)

    def test_modality_tuple_order_has_no_effect(self) -> None:
        reversed_result = produce_w7r_p0_s_completion_states(
            self.adapter,
            self.source.contact_b_step_digests[0],
            tuple(reversed(self.source.contact_b_steps[0])),
            (4_000_000, 5_000_000),
            self.initial,
        )

        self.assertEqual(self.first.production_digest, reversed_result.production_digest)
        self.assertEqual(self.first.event_states, reversed_result.event_states)

    def test_end_state_continues_the_next_source_segment(self) -> None:
        second = produce_w7r_p0_s_completion_states(
            self.adapter,
            self.source.contact_b_step_digests[1],
            self.source.contact_b_steps[1],
            (5_000_000, 6_000_000),
            self.first.end_state,
        )

        self.assertEqual(self.first.end_state.state_digest, second.initial_state.state_digest)
        self.assertEqual(6_000_000, second.end_state.end_tick)
        self.assertEqual(2, second.end_state.p0_field.layer.tick)
        self.assertNotEqual(second.initial_state.s_values, second.end_state.s_values)

    def test_source_digest_interval_and_path_binding_are_enforced(self) -> None:
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "not bound"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                "0" * 64,
                self.source.contact_b_steps[0],
                (4_000_000, 5_000_000),
                self.initial,
            )
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "continue"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.source.contact_b_step_digests[0],
                self.source.contact_b_steps[0],
                (4_000_001, 5_000_000),
                self.initial,
            )
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "source path"):
            build_initial_w7r_p0_state(self.adapter, "unknown", 0)

    def test_changed_sequences_are_rejected_before_runtime(self) -> None:
        auditory, visual = self.source.contact_b_steps[0]
        changed = replace(
            auditory,
            frames=auditory.frames[:-1],
        )
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "source digest"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.source.contact_b_step_digests[0],
                (changed, visual),
                (4_000_000, 5_000_000),
                self.initial,
            )

    def test_inputs_remain_unchanged(self) -> None:
        matrix_digest = self.adapter.matrix_digest
        state_digest = self.initial.state_digest
        source_digest = self.source.contact_b_step_digests[0]

        produce_w7r_p0_s_completion_states(
            self.adapter,
            source_digest,
            self.source.contact_b_steps[0],
            (4_000_000, 5_000_000),
            self.initial,
        )

        self.assertEqual(matrix_digest, self.adapter.matrix_digest)
        self.assertEqual(state_digest, self.initial.state_digest)
        self.assertEqual(source_digest, self.source.contact_b_step_digests[0])

    def test_private_observer_is_read_only_and_passive(self) -> None:
        samples = []

        def observe(tick, activation, afterimage):
            self.assertFalse(activation.flags.writeable)
            self.assertFalse(afterimage.flags.writeable)
            samples.append((tick, tuple(activation), tuple(afterimage)))
            return None

        observed = produce_w7r_p0_s_completion_states(
            self.adapter,
            self.source.contact_b_step_digests[0],
            self.source.contact_b_steps[0],
            (4_000_000, 5_000_000),
            self.initial,
            _state_observer=observe,
        )

        self.assertTrue(samples)
        self.assertEqual(5_000_000, samples[-1][0])
        self.assertEqual(self.first.production_digest, observed.production_digest)
        self.assertEqual(self.first.end_state.state_digest, observed.end_state.state_digest)

    def test_private_observer_must_not_return_state(self) -> None:
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "must not return"):
            produce_w7r_p0_s_completion_states(
                self.adapter,
                self.source.contact_b_step_digests[0],
                self.source.contact_b_steps[0],
                (4_000_000, 5_000_000),
                self.initial,
                _state_observer=lambda *_: True,
            )

    def test_tampered_state_and_production_digests_are_rejected(self) -> None:
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "state digest"):
            replace(self.initial, state_digest="changed")
        with self.assertRaisesRegex(W7RP0SCompletionProducerError, "production digest"):
            replace(self.first, production_digest="changed")

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "build_initial_w7r_p0_state"))
        self.assertFalse(hasattr(current_api, "produce_w7r_p0_s_completion_states"))


if __name__ == "__main__":
    unittest.main()
