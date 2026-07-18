from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    EvidenceLevel,
    FORBIDDEN_GF001_ROLES,
    GF001LocalFieldEffectMethodology,
    GF001MethodologyError,
    REQUIRED_GF001_BRANCHES,
    REQUIRED_GF001_CONTROL_BASELINES,
    REQUIRED_GF001_EFFECT_BASELINES,
    REQUIRED_GF001_MEASUREMENTS,
    REQUIRED_GF001_STOP_CONDITIONS,
    RuntimePermission,
    gf001_methodology_public_roles,
    reference_gf001_local_field_effect_methodology,
)


class GF001LocalFieldEffectMethodologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.method = reference_gf001_local_field_effect_methodology()

    def test_reference_method_is_preregistered_reproducible_and_immutable(
        self,
    ) -> None:
        second = reference_gf001_local_field_effect_methodology()
        self.assertEqual(self.method, second)
        self.assertEqual(self.method.digest(), second.digest())
        self.assertEqual("preregistered", self.method.status)
        self.assertEqual(
            RuntimePermission.CONTRACT_ONLY,
            self.method.runtime_permission,
        )
        self.assertEqual(EvidenceLevel.E2, self.method.evidence_target)
        with self.assertRaises(FrozenInstanceError):
            self.method.status = "gelaufen"  # type: ignore[misc]

    def test_geometry_separates_same_and_cross_dock_locality(self) -> None:
        self.assertEqual((2, 3), self.method.geometry_shape)
        self.assertEqual(
            (("dock.auditory", 0), ("dock.visual", 1)),
            self.method.dock_rows,
        )
        self.assertEqual(
            ((-1, 0), (0, -1), (0, 1), (1, 0)),
            self.method.sample_offsets,
        )
        self.assertIn("same_dock_locality", self.method.branches)
        self.assertIn("cross_dock_locality", self.method.branches)

    def test_all_baselines_branches_measurements_and_stops_are_required(
        self,
    ) -> None:
        self.assertTrue(
            REQUIRED_GF001_CONTROL_BASELINES.issubset(
                self.method.control_baselines
            )
        )
        self.assertTrue(
            REQUIRED_GF001_EFFECT_BASELINES.issubset(
                self.method.effect_baselines
            )
        )
        self.assertTrue(REQUIRED_GF001_BRANCHES.issubset(self.method.branches))
        self.assertTrue(
            REQUIRED_GF001_MEASUREMENTS.issubset(self.method.measurements)
        )
        self.assertTrue(
            REQUIRED_GF001_STOP_CONDITIONS.issubset(
                self.method.stop_conditions
            )
        )

    def test_method_has_no_runtime_selection_or_writeback(self) -> None:
        self.assertTrue(self.method.synthetic_only)
        self.assertFalse(self.method.writes_back)
        self.assertFalse(self.method.selects_runtime_candidate)
        for role in (
            "previous_self_state_feedback",
            "afterimage_update",
            "adaptive_parameter",
            "relationship_state",
            "learning_rule",
            "semantic_label",
        ):
            self.assertIn(role, self.method.forbidden_roles)

    def test_required_method_parts_cannot_be_removed(self) -> None:
        changes = (
            ("control_baselines", "b0.receptor_projection"),
            ("effect_baselines", "b2.symmetric_local_activation_mean"),
            ("branches", "observer_removal"),
            ("measurements", "local_sample_causal_contrast"),
            ("stop_conditions", "same_tick_state_is_read"),
            ("forbidden_roles", "adaptive_parameter"),
        )
        for field_name, removed in changes:
            values = tuple(
                value
                for value in getattr(self.method, field_name)
                if value != removed
            )
            with self.subTest(field_name=field_name), self.assertRaises(
                GF001MethodologyError
            ):
                replace(self.method, **{field_name: values})

    def test_geometry_and_scope_cannot_be_relaxed(self) -> None:
        invalid_changes = (
            {"geometry_shape": (3, 3)},
            {"sample_offsets": ((-1, 0), (1, 0))},
            {"synthetic_only": False},
            {"writes_back": True},
            {"selects_runtime_candidate": True},
            {"runtime_permission": RuntimePermission.PASSIVE_AVAILABLE},
            {"evidence_target": EvidenceLevel.E3},
        )
        for change in invalid_changes:
            with self.subTest(change=change), self.assertRaises(
                GF001MethodologyError
            ):
                replace(self.method, **change)

    def test_public_contract_contains_no_transition_parameters(self) -> None:
        forbidden_fields = {
            "weight",
            "threshold",
            "decay_rate",
            "learning_rate",
            "activation_equation",
            "memory",
            "topology",
        }
        self.assertTrue(
            forbidden_fields.isdisjoint(gf001_methodology_public_roles())
        )
        self.assertTrue(
            FORBIDDEN_GF001_ROLES.issubset(self.method.forbidden_roles)
        )
        self.assertIsInstance(self.method, GF001LocalFieldEffectMethodology)


if __name__ == "__main__":
    unittest.main()
