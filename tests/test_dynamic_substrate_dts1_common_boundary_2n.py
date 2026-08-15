from __future__ import annotations

from dataclasses import replace
import ast
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.dynamic_substrate_dts1_common_boundary_2n import (
    DTS1CommonBoundary2NError,
    S1_JF_DECISION,
    apply_dts1_common_sh_boundary_2n,
    build_dts1_s1jf_implementation_receipt,
    canonical_dts1_common_boundary_2n_fixture,
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


class DTS1CommonBoundary2NTests(unittest.TestCase):
    def _field(self, size: int = 2):
        return with_fast_state(
            shared_field(size),
            tuple(0.1 * (index + 1) for index in range(size)),
            tuple(-0.1 * (index + 1) for index in range(size)),
        )

    def test_t01_builds_exact_immutable_fixture(self) -> None:
        fixture = canonical_dts1_common_boundary_2n_fixture()
        self.assertEqual("A_BOUNDARY_2N", fixture.role)
        self.assertEqual((-0.5, 0.5), fixture.activation)
        self.assertEqual((0.0, 0.0), fixture.afterimage)
        self.assertEqual((0.25,), fixture.expected_participation)

    def test_t02_applies_exact_two_node_sh_vector(self) -> None:
        output = apply_dts1_common_sh_boundary_2n(self._field(), "A_BOUNDARY_2N")
        self.assertEqual((-0.5, 0.5), tuple(values(output, "activation")))
        self.assertEqual((0.0, 0.0), tuple(values(output, "afterimage")))

    def test_t03_preserves_input_and_all_non_sh_neuron_fields(self) -> None:
        source = self._field()
        before = tuple(item.digest() for item in source.layer.neurons)
        output = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        self.assertEqual(before, tuple(item.digest() for item in source.layer.neurons))
        for old, new in zip(source.layer.neurons, output.layer.neurons, strict=True):
            self.assertEqual((old.neuron_id, old.field_id, old.modality_id, old.geometry_id, old.position), (new.neuron_id, new.field_id, new.modality_id, new.geometry_id, new.position))
            self.assertIs(old.perception, new.perception)

    def test_t04_preserves_m_state_by_identity(self) -> None:
        source = self._field()
        substrate = build_uniform_mcm_substrate(
            source.layer,
            MCMSubstrateArmContract("s1jf.test", 0.5, 0.25, 1.0),
        )
        source = replace(source, substrate=substrate)
        output = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        self.assertIs(substrate, output.substrate)

    def test_t05_preserves_l_state_by_identity(self) -> None:
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
        output = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        self.assertIs(development, output.development)

    def test_t06_preserves_field_shell_and_time(self) -> None:
        source = self._field()
        output = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        self.assertEqual(source.docks, output.docks)
        self.assertIs(source.last_distribution, output.last_distribution)
        self.assertEqual(tuple(item.tick for item in source.layer.neurons), tuple(item.tick for item in output.layer.neurons))
        self.assertEqual(source.layer.sample_offsets, output.layer.sample_offsets)

    def test_t07_rejects_unknown_or_nonstrict_role(self) -> None:
        for role in ("A_BOUNDARY", "a_boundary_2n", None, 1):
            with self.subTest(role=role), self.assertRaises(DTS1CommonBoundary2NError):
                apply_dts1_common_sh_boundary_2n(self._field(), role)

    def test_t08_rejects_non_two_node_geometry(self) -> None:
        for size in (3, 4):
            with self.subTest(size=size), self.assertRaises(DTS1CommonBoundary2NError):
                apply_dts1_common_sh_boundary_2n(self._field(size), "A_BOUNDARY_2N")

    def test_t09_is_deterministic_and_declaration_order_independent(self) -> None:
        source = self._field()
        reversed_field = replace(source, layer=replace(source.layer, neurons=tuple(reversed(source.layer.neurons))))
        first = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        second = apply_dts1_common_sh_boundary_2n(source, "A_BOUNDARY_2N")
        reversed_output = apply_dts1_common_sh_boundary_2n(reversed_field, "A_BOUNDARY_2N")
        self.assertEqual(tuple(values(first, "activation")), tuple(values(second, "activation")))
        self.assertEqual(tuple(values(first, "activation")), tuple(values(reversed_output, "activation")))

    def test_t10_has_no_model_resource_runtime_or_public_export(self) -> None:
        module_path = Path(inspect.getfile(apply_dts1_common_sh_boundary_2n))
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        forbidden = ("coupled_step", "dts1_step", "backreaction", "s2_reference", "mcm_f3_runtime")
        self.assertFalse(any(any(token in name for token in forbidden) for name in imports))
        self.assertFalse(hasattr(mcm_field_organism, "apply_dts1_common_sh_boundary_2n"))
        self.assertFalse(hasattr(current_api, "apply_dts1_common_sh_boundary_2n"))

    def test_t11_receipt_binds_implementation_without_execution(self) -> None:
        receipt = build_dts1_s1jf_implementation_receipt()
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 12)), receipt.matrix_case_ids)
        self.assertTrue(receipt.pure_two_node_boundary_implemented)
        self.assertFalse(receipt.three_node_s1iz_operator_changed)
        self.assertFalse(receipt.model_kernel_import_present)
        self.assertEqual((0, 0), (receipt.technical_field_steps_executed, receipt.research_field_steps_executed))
        self.assertEqual(S1_JF_DECISION, receipt.decision)


if __name__ == "__main__":
    unittest.main()
