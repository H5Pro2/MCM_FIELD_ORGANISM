from __future__ import annotations

from dataclasses import replace
import ast
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.dynamic_substrate_dts1_common_boundary import (
    DTS1CommonBoundaryError,
    S1_IZ_DECISION,
    apply_dts1_common_sh_boundary,
    build_dts1_s1iz_implementation_receipt,
    canonical_dts1_common_boundary_fixtures,
)
from mcm_field_organism.mcm_local_development_state import (
    MCMLocalDevelopmentContract,
    build_zero_mcm_local_development,
)
from mcm_field_organism.mcm_substrate_state import (
    MCMSubstrateArmContract,
    build_uniform_mcm_substrate,
)
from tests.test_neutral_fast_afterimage import shared_field, values, with_fast_state


class DTS1CommonBoundaryTests(unittest.TestCase):
    def _field(self, size: int = 3):
        return with_fast_state(
            shared_field(size),
            tuple(0.1 * (index + 1) for index in range(size)),
            tuple(-0.1 * (index + 1) for index in range(size)),
        )

    def test_t01_builds_exact_four_immutable_fixtures(self) -> None:
        fixtures = canonical_dts1_common_boundary_fixtures()
        self.assertEqual(("A_BOUNDARY", "B_BOUNDARY", "GAP_BOUNDARY", "PROBE_BOUNDARY"), tuple(item.role for item in fixtures))
        self.assertEqual((0.25, 0.0), fixtures[0].expected_participation)
        self.assertEqual((0.0, 0.25), fixtures[1].expected_participation)

    def test_t02_through_t05_apply_each_exact_sh_vector(self) -> None:
        source = self._field()
        for fixture in canonical_dts1_common_boundary_fixtures():
            with self.subTest(role=fixture.role):
                output = apply_dts1_common_sh_boundary(source, fixture.role)
                self.assertEqual(fixture.activation, tuple(values(output, "activation")))
                self.assertEqual(fixture.afterimage, tuple(values(output, "afterimage")))

    def test_t06_preserves_input_and_all_non_sh_neuron_fields(self) -> None:
        source = self._field()
        before = tuple(item.digest() for item in source.layer.neurons)
        output = apply_dts1_common_sh_boundary(source, "A_BOUNDARY")
        self.assertEqual(before, tuple(item.digest() for item in source.layer.neurons))
        for old, new in zip(source.layer.neurons, output.layer.neurons, strict=True):
            self.assertEqual(old.neuron_id, new.neuron_id)
            self.assertEqual(old.field_id, new.field_id)
            self.assertEqual(old.modality_id, new.modality_id)
            self.assertEqual(old.geometry_id, new.geometry_id)
            self.assertEqual(old.position, new.position)
            self.assertIs(old.perception, new.perception)

    def test_t07_preserves_m_state_by_identity(self) -> None:
        source = self._field()
        substrate = build_uniform_mcm_substrate(
            source.layer,
            MCMSubstrateArmContract("s1iz.test", 0.5, 0.25, 1.0),
        )
        source = replace(source, substrate=substrate)
        output = apply_dts1_common_sh_boundary(source, "B_BOUNDARY")
        self.assertIs(substrate, output.substrate)

    def test_t08_preserves_l_state_by_identity(self) -> None:
        source = self._field()
        development = build_zero_mcm_local_development(
            source.layer,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                0.25,
            ),
        )
        source = replace(source, development=development)
        output = apply_dts1_common_sh_boundary(source, "GAP_BOUNDARY")
        self.assertIs(development, output.development)

    def test_t09_preserves_field_shell_components_and_time(self) -> None:
        source = self._field()
        output = apply_dts1_common_sh_boundary(source, "PROBE_BOUNDARY")
        self.assertEqual(source.docks, output.docks)
        self.assertIs(source.last_distribution, output.last_distribution)
        self.assertEqual(tuple(item.tick for item in source.layer.neurons), tuple(item.tick for item in output.layer.neurons))
        self.assertEqual(source.layer.sample_offsets, output.layer.sample_offsets)

    def test_t10_rejects_unknown_or_nonstrict_role(self) -> None:
        for role in ("A", "a_boundary", None, 1):
            with self.subTest(role=role), self.assertRaises(DTS1CommonBoundaryError):
                apply_dts1_common_sh_boundary(self._field(), role)

    def test_t11_rejects_non_three_node_geometry(self) -> None:
        for size in (2, 4):
            with self.subTest(size=size), self.assertRaises(DTS1CommonBoundaryError):
                apply_dts1_common_sh_boundary(self._field(size), "A_BOUNDARY")

    def test_t12_is_deterministic_and_declaration_order_independent(self) -> None:
        source = self._field()
        reversed_field = replace(source, layer=replace(source.layer, neurons=tuple(reversed(source.layer.neurons))))
        first = apply_dts1_common_sh_boundary(source, "B_BOUNDARY")
        second = apply_dts1_common_sh_boundary(source, "B_BOUNDARY")
        reversed_output = apply_dts1_common_sh_boundary(reversed_field, "B_BOUNDARY")
        self.assertEqual(tuple(values(first, "activation")), tuple(values(second, "activation")))
        self.assertEqual(tuple(values(first, "activation")), tuple(values(reversed_output, "activation")))

    def test_t13_has_no_model_resource_runtime_or_public_export(self) -> None:
        module_path = Path(inspect.getfile(apply_dts1_common_sh_boundary))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        forbidden = ("coupled_step", "dts1_step", "backreaction", "s2_reference", "mcm_f3_runtime")
        self.assertFalse(any(any(token in name for token in forbidden) for name in imports))
        self.assertFalse(hasattr(mcm_field_organism, "apply_dts1_common_sh_boundary"))
        self.assertFalse(hasattr(current_api, "apply_dts1_common_sh_boundary"))

    def test_t14_receipt_binds_implementation_without_execution(self) -> None:
        receipt = build_dts1_s1iz_implementation_receipt()
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 15)), receipt.matrix_case_ids)
        self.assertTrue(receipt.pure_boundary_operator_implemented)
        self.assertFalse(receipt.model_kernel_import_present)
        self.assertFalse(receipt.resource_step_import_present)
        self.assertEqual((0, 0), (receipt.technical_field_steps_executed, receipt.research_field_steps_executed))
        self.assertEqual(S1_IZ_DECISION, receipt.decision)


if __name__ == "__main__":
    unittest.main()
