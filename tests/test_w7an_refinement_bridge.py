from __future__ import annotations

import unittest

from mcm_field_organism.w7ae_cap_seven_path_consumer import (
    W7AECAPSevenPathConsumerError,
    _initial_state,
    _produce,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


class W7ANRefinementBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(cls.adapter, family)
        plan = build_w7y_seven_path_source_plan(
            cls.adapter,
            family,
            cls.authorization,
        )
        cls.segment = plan.paths[0].prefix
        cls.rows = []
        for refinement in (1, 2, 4):
            observed = []
            result = _produce(
                cls.adapter,
                cls.authorization,
                cls.segment,
                _initial_state(cls.adapter, "ab", 0),
                _refinement=refinement,
                _integration_observer=(
                    lambda segment, production, diagnostics, seen=observed: (
                        seen.append((segment, production, diagnostics))
                    )
                ),
            )
            cls.rows.append((refinement, result, observed[0]))
        cls.default = _produce(
            cls.adapter,
            cls.authorization,
            cls.segment,
            _initial_state(cls.adapter, "ab", 0),
        )

    def test_default_and_explicit_r1_are_digest_equal(self) -> None:
        self.assertEqual(
            self.default.production_digest,
            self.rows[0][1].production_digest,
        )

    def test_observer_receives_the_actual_production_binding(self) -> None:
        for refinement, result, observed in self.rows:
            segment, production, diagnostics = observed
            self.assertIs(segment, self.segment)
            self.assertIs(production, result)
            self.assertEqual(refinement, diagnostics.refinement)

    def test_substeps_are_exactly_ordered_for_the_frozen_segment(self) -> None:
        self.assertEqual(
            (394, 788, 1576),
            tuple(item[2][2].substep_count for item in self.rows),
        )

    def test_resolution_production_digests_are_distinct(self) -> None:
        self.assertEqual(3, len({item[1].production_digest for item in self.rows}))

    def test_invalid_private_refinement_is_rejected_before_runtime(self) -> None:
        for invalid in (0, 3, 5, True):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(
                    W7AECAPSevenPathConsumerError,
                    "one of 1, 2, or 4",
                ):
                    _produce(
                        self.adapter,
                        self.authorization,
                        self.segment,
                        _initial_state(self.adapter, "ab", 0),
                        _refinement=invalid,
                    )

    def test_bridge_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "compose_w7an_r124_resolution_container"))


if __name__ == "__main__":
    unittest.main()
