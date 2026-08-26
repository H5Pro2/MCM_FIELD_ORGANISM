from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_320_confirmation import (
    CONFIRMATION_ALPHA_AXIS,
    CONFIRMATION_PARTITION_COUNTS,
    _validated_confirmation_alpha,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_DURATION_TICKS,
    PublicAVLocalAdaptiveReceptivityCauchyConvergenceError,
    _cauchy_records,
)
from tools.run_public_av_local_adaptive_receptivity_cauchy_320_confirmation_shard import (
    _output_path,
    _parser,
)


class PublicAVLocalAdaptiveReceptivityCauchy320ConfirmationTests(unittest.TestCase):
    def test_confirmation_axes_are_preregistered(self) -> None:
        self.assertEqual((0.5, 1.0), CONFIRMATION_ALPHA_AXIS)
        self.assertEqual((80, 160, 320), CONFIRMATION_PARTITION_COUNTS)
        self.assertEqual(
            (2_000_000_000, 10_000_000_000, 20_000_000_000),
            CAUCHY_AUDIT_DURATION_TICKS,
        )
        self.assertEqual(0.5, _validated_confirmation_alpha(0.5))
        self.assertEqual(1.0, _validated_confirmation_alpha(1.0))
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityCauchyConvergenceError):
            _validated_confirmation_alpha(0.0)

    def test_pairs_and_quotient_null_handling_are_unchanged(self) -> None:
        roles = ("activation", "afterimage", "local_energy", "receptivity")
        vectors = {
            80: {role: (4.0,) for role in roles},
            160: {role: (2.0,) for role in roles},
            320: {role: (1.0,) for role in roles},
        }
        records = _cauchy_records(vectors)
        self.assertEqual([(80, 160), (160, 320)], [
            (item["coarse_partition_count"], item["fine_partition_count"])
            for item in records
        ])
        self.assertEqual(2.0, records[0]["refinement_quotient_to_next_pair"]["receptivity"])
        self.assertIsNone(records[1]["refinement_quotient_to_next_pair"])

        zero_vectors = {
            count: {role: (1.0,) for role in roles}
            for count in CONFIRMATION_PARTITION_COUNTS
        }
        self.assertIsNone(
            _cauchy_records(zero_vectors)[0]["refinement_quotient_to_next_pair"]["receptivity"]
        )

    def test_runner_restricts_alpha_and_uses_atomic_shard_paths(self) -> None:
        self.assertEqual(0.5, _parser().parse_args(["--alpha", "0.50"]).alpha)
        with self.assertRaises(SystemExit):
            _parser().parse_args(["--alpha", "0.00"])
        self.assertEqual(
            Path("reports/shards/public_av_local_adaptive_receptivity_"
                 "cauchy_320_confirmation_alpha_1_00_v1.json"),
            _output_path(1.0),
        )
        source = Path(
            "tools/run_public_av_local_adaptive_receptivity_cauchy_320_confirmation_shard.py"
        ).read_text(encoding="utf-8")
        self.assertIn("NamedTemporaryFile", source)
        self.assertIn("temporary.replace(output)", source)

    def test_source_preserves_components_starts_and_disables_decisions(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity_cauchy_320_confirmation.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"start_layer_digest"',
            '"start_snapshot_digest"',
            '"linf_to_other_scheme_same_partition"',
            '"successive_cauchy_comparisons"',
            '"threshold_defined": False',
            '"convergence_order_selected": False',
            '"preferred_scheme_selected": False',
            '"preferred_partition_selected": False',
            '"organization_claim_allowed": False',
            '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
