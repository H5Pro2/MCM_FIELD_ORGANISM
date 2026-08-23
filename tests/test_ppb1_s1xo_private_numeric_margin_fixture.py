from __future__ import annotations

from dataclasses import fields, replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xo_private_numeric_margin_fixture as s1xo
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BUNDLE_DIGEST = (
    "58a4e4d213914296900f30a3696cef38a3687526ef6986a1ac795467fdbcc0c8"
)


class PPB1S1XOPrivateNumericMarginFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = s1xo.build_s1xo_numeric_margin_fixture()

    def test_bundle_is_deterministic_and_contract_bound(self) -> None:
        second = s1xo.build_s1xo_numeric_margin_fixture()
        self.assertEqual(self.bundle, second)
        self.assertEqual(EXPECTED_BUNDLE_DIGEST, self.bundle.bundle_digest)
        self.assertEqual(
            "cff21269c4981ffe7439de49e3eee35bd71528ed464f6f75937d1e9a192628b6",
            s1xo.S1XO_CONTRACT_DIGEST,
        )

    def test_two_modalities_have_exact_private_dimensions(self) -> None:
        auditory, visual = self.bundle.modalities
        self.assertEqual(
            ("auditory", 12), (auditory.modality_id, auditory.carrier_count)
        )
        self.assertEqual(("visual", 72), (visual.modality_id, visual.carrier_count))

    def test_behavioral_inventory_and_expected_mask_are_exact(self) -> None:
        for fixture in self.bundle.modalities:
            self.assertEqual(s1xo.S1XO_PROBE_CLASSES, fixture.probe_classes)
            self.assertEqual(s1xo.S1XO_EXPECTED_MASK, fixture.expected_recognition)
            self.assertEqual(5, len(fixture.computed_distances))

    def test_production_metric_distances_equal_bound_binary_values(self) -> None:
        for fixture in self.bundle.modalities:
            self.assertEqual(fixture.probe_values, fixture.computed_distances)
            self.assertTrue(
                all(
                    float.fromhex(value.hex()) == value
                    for value in fixture.probe_values
                )
            )

    def test_behavioral_values_stay_on_bound_threshold_side_with_margin(self) -> None:
        for fixture in self.bundle.modalities:
            self.assertNotIn(fixture.match_threshold, fixture.computed_distances)
            self.assertGreaterEqual(
                fixture.match_threshold - fixture.computed_distances[2],
                fixture.minimum_threshold_separation,
            )
            self.assertGreaterEqual(
                fixture.computed_distances[3] - fixture.match_threshold,
                fixture.minimum_threshold_separation,
            )
            self.assertEqual(
                fixture.expected_recognition,
                tuple(
                    value <= fixture.match_threshold
                    for value in fixture.computed_distances
                ),
            )

    def test_threshold_operator_cases_are_separate_and_exact(self) -> None:
        self.assertEqual(6, len(self.bundle.threshold_operator_cases))
        for offset in (0, 3):
            below, equal, above = self.bundle.threshold_operator_cases[
                offset : offset + 3
            ]
            self.assertEqual(
                ("below", "equal", "above"),
                (below.position, equal.position, above.position),
            )
            self.assertLess(below.distance, below.threshold)
            self.assertEqual(equal.distance, equal.threshold)
            self.assertGreater(above.distance, above.threshold)
            self.assertEqual(
                (True, True, False),
                tuple(
                    item.expected_recognized for item in (below, equal, above)
                ),
            )

    def test_three_frozen_slotted_types_have_no_decision_or_field_roles(self) -> None:
        expected = {
            s1xo.S1XOModalityNumericFixture: 9,
            s1xo.S1XOThresholdOperatorCase: 6,
            s1xo.S1XONumericMarginFixtureBundle: 3,
        }
        for kind, count in expected.items():
            self.assertEqual(count, len(fields(kind)))
            self.assertTrue(kind.__dataclass_params__.frozen)
            names = {item.name for item in fields(kind)}
            self.assertTrue(
                names.isdisjoint(
                    {
                        "poststate",
                        "memory_decision",
                        "technical_function_decision",
                        "field_feedback",
                        "semantic_label",
                    }
                )
            )

    def test_digest_or_numeric_tampering_fails_closed(self) -> None:
        auditory = self.bundle.modalities[0]
        with self.assertRaises(s1xo.S1XONumericFixtureError):
            replace(auditory, fixture_digest="0" * 64)
        with self.assertRaises(s1xo.S1XONumericFixtureError):
            replace(auditory, computed_distances=(0.0,) * 5)
        with self.assertRaises(s1xo.S1XONumericFixtureError):
            replace(auditory, expected_recognition=(True,) * 5)
        with self.assertRaises(s1xo.S1XONumericFixtureError):
            replace(self.bundle.threshold_operator_cases[0], position="equal")

    def test_source_uses_metric_but_no_state_probe_runner_or_io(self) -> None:
        source = inspect.getsource(s1xo)
        self.assertIn("normalized_mean_l1_distance", source)
        for forbidden in (
            "initial_ppb1_bank_state",
            "advance_ppb1_bank",
            "probe_s1wu_perceptual_state",
            "materialize_s1xc_fixture_registry",
            "run_s1xi_registered_matrix",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production_adapter",
            "production_coordinator",
            "run_production",
        ):
            self.assertNotIn(forbidden, source)

    def test_module_remains_private_and_unexported(self) -> None:
        self.assertNotIn("S1XONumericMarginFixtureBundle", mcm_field_organism.__all__)
        self.assertFalse(hasattr(current_api, "build_s1xo_numeric_margin_fixture"))
        self.assertNotIn("build_s1xo_numeric_margin_fixture", ROOT_LAZY_EXPORTS)

    def test_historical_sources_remain_byte_identical(self) -> None:
        expected = {
            "mcm_field_organism/_ppb1_s1xc_fixture_registry.py": (
                "d22543d4c442c25fefde7719458c2b3a3c4abfbc7adbac3d1ec4c263a5c324b9"
            ),
            "mcm_field_organism/_ppb1_s1xi_private_full_runner.py": (
                "edd81cfb9fa0207d8771a50727cd139092bdb8e089442ab2a430f629043c045d"
            ),
        }
        import hashlib

        for relative, digest in expected.items():
            self.assertEqual(
                digest,
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
