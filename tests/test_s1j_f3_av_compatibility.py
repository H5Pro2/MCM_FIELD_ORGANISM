from __future__ import annotations

import unittest

from mcm_field_organism._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_VISUAL_CONFIG,
    build_synthetic_av_field,
    synthetic_av_sequences,
)
from mcm_field_organism.mcm_f3_runtime import activate_mcm_f3_field
from mcm_field_organism.s1j_f3_av_compatibility import (
    S1J_ACTIVE_ARM,
    S1J_SUPPORT_TICKS,
    advance_s1j_f3_av_sequences,
    run_s1j_f3_av_compatibility,
    s1j_f3_av_compatibility_public_roles,
)
from mcm_field_organism.shared_mcm_field import restore_shared_mcm_field


def _sequences(phase_id: str, start_tick: int, *, active: bool):
    auditory = tuple(
        (0.8 if index == 0 else -0.2) if active else 0.0
        for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
    )
    visual = tuple(
        (0.6 if index == 5 else 0.0) if active else 0.0
        for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
    )
    return synthetic_av_sequences(
        phase_id,
        start_tick,
        start_tick + S1J_SUPPORT_TICKS,
        auditory,
        visual,
    )


class S1JF3AVCompatibilityTests(unittest.TestCase):
    def test_fixed_matrix_preserves_all_technical_invariants(self) -> None:
        result = run_s1j_f3_av_compatibility()

        self.assertTrue(result.p0_matches_neutral_fast)
        self.assertEqual(
            result.neutral_fast_endpoint_digest,
            result.p0.fast_state_projection_digest,
        )
        for arm in (
            result.active,
            result.linear_baseline,
            result.eta_null,
            result.p0,
        ):
            with self.subTest(arm=arm.coupling_id):
                self.assertEqual(26, arm.field_neuron_count)
                self.assertEqual(4, arm.source_event_count)
                self.assertGreaterEqual(arm.minimum_mass, 0.0)
                self.assertAlmostEqual(1.0, arm.total_mass, places=12)
                self.assertLessEqual(arm.activation_linf, 1.0)
                self.assertLessEqual(arm.afterimage_linf, 1.0)
        self.assertEqual(("p0.exact", "p0.exact"), result.p0.method_ids)
        self.assertEqual(("ssprk33", "ssprk33"), result.active.method_ids)
        self.assertGreater(result.active.mass_deviation_linf, 0.0)
        self.assertGreater(result.linear_baseline.mass_deviation_linf, 0.0)
        self.assertGreater(result.eta_null.mass_deviation_linf, 0.0)
        self.assertEqual(0.0, result.p0.mass_deviation_linf)

    def test_contact_changes_m_only_after_later_field_time(self) -> None:
        contact = _sequences("s1j.causality.contact", 0, active=True)
        field = activate_mcm_f3_field(
            build_synthetic_av_field(contact),
            S1J_ACTIVE_ARM,
        )
        first = advance_s1j_f3_av_sequences(field, contact)
        uniform = 1.0 / 26.0

        self.assertTrue(
            all(item.mass == uniform for item in first.field.substrate.masses)
        )
        null = _sequences(
            "s1j.causality.null",
            S1J_SUPPORT_TICKS,
            active=False,
        )
        second = advance_s1j_f3_av_sequences(first.field, null)
        self.assertTrue(
            any(item.mass != uniform for item in second.field.substrate.masses)
        )

    def test_schema_two_restore_has_exact_same_next_av_boundary(self) -> None:
        contact = _sequences("s1j.restore.contact", 0, active=True)
        initial = activate_mcm_f3_field(
            build_synthetic_av_field(contact),
            S1J_ACTIVE_ARM,
        )
        first = advance_s1j_f3_av_sequences(initial, contact).field
        restored = restore_shared_mcm_field(first.snapshot())
        null = _sequences(
            "s1j.restore.null",
            S1J_SUPPORT_TICKS,
            active=False,
        )

        uninterrupted = advance_s1j_f3_av_sequences(first, null).field
        resumed = advance_s1j_f3_av_sequences(restored, null).field

        self.assertEqual(
            uninterrupted.snapshot().digest(),
            resumed.snapshot().digest(),
        )

    def test_result_contract_contains_no_claim_or_raw_world_roles(self) -> None:
        roles = set(s1j_f3_av_compatibility_public_roles())
        self.assertTrue(
            {
                "world",
                "video",
                "audio",
                "image",
                "sample",
                "label",
                "reward",
                "identity",
                "meaning",
                "memory",
                "topology",
                "observer",
                "writeback",
            }.isdisjoint(roles)
        )
        result = run_s1j_f3_av_compatibility()
        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.learning_claim_allowed)
        self.assertFalse(result.organization_claim_allowed)
        self.assertFalse(result.topology_claim_allowed)
        self.assertFalse(result.semantics_claim_allowed)
        self.assertFalse(result.ai_claim_allowed)


if __name__ == "__main__":
    unittest.main()
