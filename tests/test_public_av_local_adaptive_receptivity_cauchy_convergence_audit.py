from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_DURATION_TICKS,
    CAUCHY_AUDIT_PARTITION_COUNTS,
    PublicAVLocalAdaptiveReceptivityCauchyConvergenceError,
    _cauchy_records,
    _numeric_ratio,
    _successive_pairs,
    _validated_alpha_axis,
)
from tools.run_public_av_local_adaptive_receptivity_cauchy_convergence_shard import (
    _alpha_slug,
    _output_path,
    _parser,
)


class PublicAVLocalAdaptiveReceptivityCauchyConvergenceAuditTests(unittest.TestCase):
    def test_axes_and_successive_pairs_are_preregistered(self) -> None:
        self.assertEqual((2_000_000_000, 10_000_000_000, 20_000_000_000),
                         CAUCHY_AUDIT_DURATION_TICKS)
        self.assertEqual((20, 40, 80, 160), CAUCHY_AUDIT_PARTITION_COUNTS)
        self.assertEqual(((20, 40), (40, 80), (80, 160)), _successive_pairs())
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityCauchyConvergenceError):
            _successive_pairs((20, 40, 100))

    def test_numeric_ratio_has_explicit_zero_handling(self) -> None:
        self.assertEqual(4.0, _numeric_ratio(2.0, 0.5))
        self.assertIsNone(_numeric_ratio(0.0, 0.0))

    def test_shard_selection_is_exactly_one_preregistered_alpha(self) -> None:
        self.assertEqual((0.0,), _validated_alpha_axis(0.0))
        self.assertEqual((0.5,), _validated_alpha_axis(0.5))
        self.assertEqual((1.0,), _validated_alpha_axis(1.0))
        with self.assertRaises(PublicAVLocalAdaptiveReceptivityCauchyConvergenceError):
            _validated_alpha_axis(0.25)
        self.assertEqual(0.5, _parser().parse_args(["--alpha", "0.50"]).alpha)
        with self.assertRaises(SystemExit):
            _parser().parse_args(["--alpha", "0.25"])

    def test_cauchy_records_keep_components_and_do_not_decide_order(self) -> None:
        vectors = {
            20: {role: (4.0,) for role in ("activation", "afterimage", "local_energy", "receptivity")},
            40: {role: (2.0,) for role in ("activation", "afterimage", "local_energy", "receptivity")},
            80: {role: (1.0,) for role in ("activation", "afterimage", "local_energy", "receptivity")},
            160: {role: (0.5,) for role in ("activation", "afterimage", "local_energy", "receptivity")},
        }
        records = _cauchy_records(vectors)
        self.assertEqual(3, len(records))
        self.assertEqual(2.0, records[0]["linf_distance"]["receptivity"])
        self.assertEqual(2.0, records[0]["refinement_quotient_to_next_pair"]["receptivity"])
        self.assertIsNone(records[-1]["refinement_quotient_to_next_pair"])

    def test_source_locks_controls_and_disables_decisions(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity_cauchy_convergence_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"successive_cauchy_comparisons"',
            '"refinement_quotient_to_next_pair"',
            '"linf_to_other_scheme_same_partition"',
            '"threshold_defined": False',
            '"convergence_order_selected": False',
            '"preferred_scheme_selected": False',
            '"preferred_partition_selected": False',
            '"organization_claim_allowed": False',
            '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)

    def test_runner_preregisters_atomic_report_path(self) -> None:
        source = Path(
            "tools/run_public_av_local_adaptive_receptivity_cauchy_convergence_audit.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'reports/public_av_local_adaptive_receptivity_cauchy_convergence_audit_v1.json',
            source,
        )
        self.assertIn("NamedTemporaryFile", source)
        self.assertIn("temporary.replace(OUTPUT)", source)

    def test_shard_runner_uses_atomic_alpha_specific_paths(self) -> None:
        self.assertEqual("0_00", _alpha_slug(0.0))
        self.assertEqual("0_50", _alpha_slug(0.5))
        self.assertEqual("1_00", _alpha_slug(1.0))
        self.assertEqual(
            Path("reports/shards/public_av_local_adaptive_receptivity_"
                 "cauchy_convergence_alpha_0_50_v1.json"),
            _output_path(0.5),
        )
        source = Path(
            "tools/run_public_av_local_adaptive_receptivity_cauchy_convergence_shard.py"
        ).read_text(encoding="utf-8")
        self.assertIn("NamedTemporaryFile", source)
        self.assertIn("temporary.replace(output)", source)


if __name__ == "__main__":
    unittest.main()
