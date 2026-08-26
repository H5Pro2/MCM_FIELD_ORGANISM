from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.local_adaptive_receptivity import (
    LocalAdaptiveReceptivityConfig,
    LocalReceptivityState,
    run_adaptive_receptivity_field,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_coupling_scheme_audit import (
    COUPLING_AUDIT_CONTACT_TICKS,
    COUPLING_AUDIT_DURATION_TICKS,
    COUPLING_AUDIT_PARTITION_COUNTS,
    COUPLING_AUDIT_SCHEMES,
    PublicAVLocalAdaptiveReceptivityCouplingSchemeError,
    _advance_gap_interval,
    _run_coupled_gap,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_partition_audit import (
    _component_vectors,
    _linf,
)
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field, _steps
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


class PublicAVLocalAdaptiveReceptivityCouplingSchemeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sequences = _sequences(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.dissipation = NeutralFieldDissipationConfig(0.0)
        cls.config = LocalAdaptiveReceptivityConfig(0.0)
        initial = _fresh_field(cls.sequences)
        cls.contact = run_adaptive_receptivity_field(
            initial, LocalReceptivityState.fresh(initial), cls.sequences,
            _steps(cls.sequences, 0, COUPLING_AUDIT_CONTACT_TICKS),
            cls.substrate, cls.afterimage, cls.config, cls.dissipation,
        )

    def test_preregistered_axes(self) -> None:
        self.assertEqual((2_000_000_000, 10_000_000_000, 20_000_000_000),
                         COUPLING_AUDIT_DURATION_TICKS)
        self.assertEqual((10, 20, 40, 80), COUPLING_AUDIT_PARTITION_COUNTS)
        self.assertEqual(("endpoint_energy", "midpoint_coupling"), COUPLING_AUDIT_SCHEMES)

    def test_midpoint_scheme_samples_exact_temporal_midpoint(self) -> None:
        _, _, sample_tick = _advance_gap_interval(
            self.contact.field, self.contact.receptivity, 500_000_000, 700_000_000,
            "midpoint_coupling", self.substrate, self.afterimage, self.config,
            self.dissipation,
        )
        self.assertEqual(600_000_000, sample_tick)
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityCouplingSchemeError):
            _advance_gap_interval(
                self.contact.field, self.contact.receptivity, 0, 3,
                "midpoint_coupling", self.substrate, self.afterimage, self.config,
                self.dissipation,
            )

    def test_alpha_zero_is_identity_and_field_control(self) -> None:
        start_layer = self.contact.field.layer.digest()
        start_values = self.contact.receptivity.values
        runs = {}
        for scheme in COUPLING_AUDIT_SCHEMES:
            runs[scheme] = _run_coupled_gap(
                self.contact.field, self.contact.receptivity, COUPLING_AUDIT_CONTACT_TICKS,
                2_000_000_000, 10, scheme, self.substrate, self.afterimage,
                self.config, self.dissipation,
            )
        endpoint = _component_vectors(runs["endpoint_energy"][0], runs["endpoint_energy"][1])
        midpoint = _component_vectors(runs["midpoint_coupling"][0], runs["midpoint_coupling"][1])
        for role in ("activation", "afterimage", "local_energy"):
            self.assertLess(_linf(endpoint[role], midpoint[role]), 1e-12)
        self.assertEqual((1.0,) * len(endpoint["receptivity"]), endpoint["receptivity"])
        self.assertEqual(start_layer, self.contact.field.layer.digest())
        self.assertEqual(start_values, self.contact.receptivity.values)

    def test_trace_bounds_and_energy_sample_times(self) -> None:
        config = LocalAdaptiveReceptivityConfig(1.0)
        initial = _fresh_field(self.sequences)
        contact = run_adaptive_receptivity_field(
            initial, LocalReceptivityState.fresh(initial), self.sequences,
            _steps(self.sequences, 0, COUPLING_AUDIT_CONTACT_TICKS),
            self.substrate, self.afterimage, config, self.dissipation,
        )
        _, receptivity, trace = _run_coupled_gap(
            contact.field, contact.receptivity, COUPLING_AUDIT_CONTACT_TICKS,
            2_000_000_000, 10, "midpoint_coupling", self.substrate,
            self.afterimage, config, self.dissipation,
        )
        self.assertEqual(10, len(trace))
        self.assertEqual(600_000_000, trace[0]["energy_sample_tick"])
        self.assertTrue(all(0.25 <= value <= 1.0 for value in receptivity.values))

    def test_source_locks_measurements_and_claims(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity_coupling_scheme_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"linf_to_own_80_partition"',
            '"linf_to_other_scheme_same_partition"',
            '"energy_sample_tick"',
            '"threshold_defined": False',
            '"preferred_scheme_selected": False',
            '"preferred_partition_selected": False',
            '"organization_claim_allowed": False',
            '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
