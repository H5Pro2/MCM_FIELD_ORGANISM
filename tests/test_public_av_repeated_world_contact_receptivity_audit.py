from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.local_adaptive_receptivity import (
    LocalAdaptiveReceptivityError,
    LocalReceptivityState,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_DURATION_TICKS,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_coupling_scheme_audit import (
    COUPLING_AUDIT_SCHEMES,
)
from mcm_field_organism.public_av_repeated_world_contact_receptivity_audit import (
    REPEATED_CONTACT_ALPHA_AXIS,
    REPEATED_CONTACT_ARM_IDS,
    REPEATED_CONTACT_MEASUREMENT_ROLES,
    REPEATED_CONTACT_PARTITION_COUNT,
    PublicAVRepeatedWorldContactReceptivityError,
    _validate_identity_control_differences,
    _validated_axes,
)
from tools.run_public_av_repeated_world_contact_receptivity_shard import (
    _output_path,
    _parser,
)


class PublicAVRepeatedWorldContactReceptivityAuditTests(unittest.TestCase):
    def test_axes_and_time_order_are_preregistered(self) -> None:
        self.assertEqual((0.0, 0.5, 1.0), REPEATED_CONTACT_ALPHA_AXIS)
        self.assertEqual(("endpoint_energy", "midpoint_coupling"), COUPLING_AUDIT_SCHEMES)
        self.assertEqual(320, REPEATED_CONTACT_PARTITION_COUNT)
        self.assertEqual(
            (2_000_000_000, 10_000_000_000, 20_000_000_000),
            CAUCHY_AUDIT_DURATION_TICKS,
        )
        self.assertEqual((0.5, "endpoint_energy"), _validated_axes(0.5, "endpoint_energy"))
        self.assertEqual((0.0, "endpoint_energy"), _validated_axes(0.0, "endpoint_energy"))
        with self.assertRaises(PublicAVRepeatedWorldContactReceptivityError):
            _validated_axes(0.25, "endpoint_energy")

    def test_zero_alpha_is_an_exact_identity_invariant(self) -> None:
        differences = {
            role: 0.0 for role in REPEATED_CONTACT_MEASUREMENT_ROLES
        }
        self.assertTrue(_validate_identity_control_differences(0.0, differences))
        self.assertFalse(_validate_identity_control_differences(0.5, differences))
        differences["activation"] = 1e-15
        with self.assertRaises(PublicAVRepeatedWorldContactReceptivityError):
            _validate_identity_control_differences(0.0, differences)

    def test_arms_preserve_baseline_isolation(self) -> None:
        self.assertEqual(
            ("continued_adaptive", "frozen_receptivity_baseline"),
            REPEATED_CONTACT_ARM_IDS,
        )
        source = Path(
            "mcm_field_organism/public_av_repeated_world_contact_receptivity_audit.py"
        ).read_text(encoding="utf-8")
        self.assertIn("gap_field, gap_receptivity, shifted, second_steps", source)
        self.assertIn("adaptive_config, dissipation", source)
        self.assertIn("frozen_config, dissipation", source)
        self.assertIn('"second_contact_start_shared_between_arms": True', source)
        self.assertIn('"frozen_baseline_updates_receptivity": False', source)

    def test_components_bounds_and_claims_are_explicit(self) -> None:
        self.assertEqual(
            ("activation", "afterimage", "local_energy", "receptivity"),
            REPEATED_CONTACT_MEASUREMENT_ROLES,
        )
        source = Path(
            "mcm_field_organism/public_av_repeated_world_contact_receptivity_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"gap_trace"', '"adaptive_to_frozen_linf"',
            '"measurement_roles"',
            '"threshold_defined": False', '"preferred_scheme_selected": False',
            '"memory_claim_allowed": False', '"meaning_claim_allowed": False',
            '"organization_claim_allowed": False',
            '"consciousness_claim_allowed": False', '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)

    def test_receptivity_bounds_are_enforced_for_audit_states(self) -> None:
        state = LocalReceptivityState(("n0", "n1"), (0.25, 1.0))
        self.assertEqual((0.25, 1.0), state.values)
        with self.assertRaises(LocalAdaptiveReceptivityError):
            LocalReceptivityState(("n0",), (0.249999,))
        with self.assertRaises(LocalAdaptiveReceptivityError):
            LocalReceptivityState(("n0",), (1.000001,))

    def test_runner_uses_alpha_schema_atomic_paths(self) -> None:
        args = _parser().parse_args(
            ["--alpha", "1.00", "--scheme", "midpoint_coupling"]
        )
        self.assertEqual(1.0, args.alpha)
        self.assertEqual("midpoint_coupling", args.scheme)
        self.assertEqual(
            Path("reports/shards/public_av_repeated_world_contact_receptivity_"
                 "alpha_1_00_scheme_midpoint_coupling_v1.json"),
            _output_path(1.0, "midpoint_coupling"),
        )
        zero_args = _parser().parse_args(
            ["--alpha", "0.00", "--scheme", "endpoint_energy"]
        )
        self.assertEqual(0.0, zero_args.alpha)
        self.assertEqual(
            Path("reports/shards/public_av_repeated_world_contact_receptivity_"
                 "alpha_0_00_scheme_endpoint_energy_v1.json"),
            _output_path(0.0, "endpoint_energy"),
        )
        source = Path(
            "tools/run_public_av_repeated_world_contact_receptivity_shard.py"
        ).read_text(encoding="utf-8")
        self.assertIn("NamedTemporaryFile", source)
        self.assertIn("temporary.replace(output)", source)


if __name__ == "__main__":
    unittest.main()
