from __future__ import annotations

import ast
import inspect
import json
import math
import unittest

import numpy as np

from mcm_field_organism import dynamic_substrate_dts1_refinement_causality_audit as audit
from mcm_field_organism.dynamic_substrate_s1hx_refinement_causality_audit_contract import (
    S1_HX_PARTITIONS,
    build_dts1_s1hx_refinement_causality_audit_contract,
)


class DTS1RefinementCausalityAuditTests(unittest.TestCase):
    def test_s1hx_source_and_closed_execution_budget_are_fixed(self) -> None:
        source = build_dts1_s1hx_refinement_causality_audit_contract()
        self.assertEqual(
            audit.S1_HY_SOURCE_S1HX_CONTRACT_DIGEST,
            source.contract_digest,
        )
        self.assertEqual(audit.S1_HY_PARTITIONS, S1_HX_PARTITIONS)
        self.assertEqual(audit.S1_HY_PARTITIONS, (2, 4, 8))
        self.assertEqual(audit.S1_HY_LATENCY_BOUNDS, (1.0, 0.5, 0.25))
        self.assertEqual(audit.S1_HY_SINGLE_EXECUTION_STEPS, 70)
        self.assertEqual(audit.S1_HY_DOUBLE_EXECUTION_STEPS, 140)

    def test_double_entry_has_exactly_two_direct_single_audit_calls(self) -> None:
        tree = ast.parse(inspect.getsource(audit.execute_dts1_s1hy_preregistered_double_audit))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_execute_once"
        ]
        loops = [node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]
        self.assertEqual(len(calls), 2)
        self.assertEqual(loops, [])

    def test_fixture_pair_vector_is_complete_and_capacity_normalized(self) -> None:
        field = audit._initial_field()
        anatomy = audit._initial_anatomy(field, ((0.2, 0.1), (0.4, 0.2)))
        self.assertEqual(
            audit._pair_vector(field, anatomy),
            (-0.8, 0.1, 0.7, 0.2, -0.1, 0.3, 0.1, 0.2, 0.05, 0.1),
        )

    def test_residual_is_maximum_absolute_component_difference(self) -> None:
        self.assertEqual(
            audit._maximum_difference((1.0, -2.0, 0.5), (0.75, -1.0, 0.0)),
            1.0,
        )
        with self.assertRaises(audit.DTS1RefinementCausalityAuditError):
            audit._maximum_difference((1.0,), ())

    def test_roundoff_floor_uses_preregistered_scale_rule(self) -> None:
        vectors = ((-4.0, 2.0), (1.0, -3.0))
        expected = 512.0 * float(np.finfo(np.float64).eps) * 4.0
        self.assertEqual(audit._roundoff_floor(vectors), expected)
        self.assertTrue(math.isfinite(expected))

    def test_invalid_resource_state_is_representable_for_atomic_stopp(self) -> None:
        record = audit.DTS1S1HYScenarioRecord(
            scenario_id=audit.S1_HY_SCENARIO_IDS[0],
            partitions=audit.S1_HY_PARTITIONS,
            latency_bounds=audit.S1_HY_LATENCY_BOUNDS,
            level_pair_vectors=tuple((level, (0.0,)) for level in audit.S1_HY_PARTITIONS),
            exact_checks=(("control", True),),
            numeric_metrics=(("residual", 0.0),),
            resource_states_valid=False,
            technical_field_steps=28,
        )
        self.assertFalse(record.resource_states_valid)
        json.dumps(record.canonical_payload(), allow_nan=False, sort_keys=True)

    def test_module_is_private_and_contains_no_io_or_test_dependency(self) -> None:
        source = inspect.getsource(audit)
        self.assertNotIn("from tests", source)
        self.assertNotIn("import tests", source)
        self.assertNotIn("open(", source)
        self.assertNotIn("Path(", source)


if __name__ == "__main__":
    unittest.main()
