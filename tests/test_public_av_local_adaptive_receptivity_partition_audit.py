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
from mcm_field_organism.public_av_local_adaptive_receptivity_partition_audit import (
    PARTITION_AUDIT_CONTACT_TICKS,
    PARTITION_AUDIT_COUNTS,
    PARTITION_AUDIT_DURATION_TICKS,
    PublicAVLocalAdaptiveReceptivityPartitionError,
    _component_vectors,
    _linf,
    _partition_ticks,
    _run_partitioned_gap,
)
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field, _steps
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


class PublicAVLocalAdaptiveReceptivityPartitionAuditTests(unittest.TestCase):
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
            _steps(cls.sequences, 0, PARTITION_AUDIT_CONTACT_TICKS),
            cls.substrate, cls.afterimage, cls.config, cls.dissipation,
        )

    def test_axes_are_fixed(self) -> None:
        self.assertEqual((2_000_000_000, 10_000_000_000, 20_000_000_000),
                         PARTITION_AUDIT_DURATION_TICKS)
        self.assertEqual((1, 2, 10, 20), PARTITION_AUDIT_COUNTS)

    def test_partition_ticks_are_equal_and_cover_exact_duration(self) -> None:
        intervals = _partition_ticks(500_000_000, 2_000_000_000, 20)
        self.assertEqual(20, len(intervals))
        self.assertEqual(500_000_000, intervals[0][0])
        self.assertEqual(2_500_000_000, intervals[-1][1])
        self.assertEqual({100_000_000}, {end - start for start, end in intervals})
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityPartitionError):
            _partition_ticks(0, 3, 2)

    def test_linf_requires_aligned_vectors(self) -> None:
        self.assertEqual(1.0, _linf((1.0, 3.0), (0.0, 3.0)))
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityPartitionError):
            _linf((1.0,), (1.0, 2.0))

    def test_alpha_zero_is_partition_semigroup_control_and_starts_are_immutable(self) -> None:
        start_layer = self.contact.field.layer.digest()
        start_values = self.contact.receptivity.values
        one = _run_partitioned_gap(
            self.contact.field, self.contact.receptivity, PARTITION_AUDIT_CONTACT_TICKS,
            2_000_000_000, 1, self.substrate, self.afterimage, self.config,
            self.dissipation,
        )
        two = _run_partitioned_gap(
            self.contact.field, self.contact.receptivity, PARTITION_AUDIT_CONTACT_TICKS,
            2_000_000_000, 2, self.substrate, self.afterimage, self.config,
            self.dissipation,
        )
        one_vectors = _component_vectors(one[0], one[1])
        two_vectors = _component_vectors(two[0], two[1])
        self.assertLess(_linf(one_vectors["activation"], two_vectors["activation"]), 1e-12)
        self.assertLess(_linf(one_vectors["afterimage"], two_vectors["afterimage"]), 1e-12)
        self.assertEqual((1.0,) * len(one[1].values), one[1].values)
        self.assertEqual(start_layer, self.contact.field.layer.digest())
        self.assertEqual(start_values, self.contact.receptivity.values)

    def test_source_preregisters_components_reference_and_claim_locks(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity_partition_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"activation"', '"afterimage"', '"local_energy"', '"receptivity"',
            '"start_layer_digest"', '"start_snapshot_digest"',
            '"linf_to_finest_partition"', '"threshold_defined": False',
            '"preferred_partition_selected": False',
            '"organization_claim_allowed": False', '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
