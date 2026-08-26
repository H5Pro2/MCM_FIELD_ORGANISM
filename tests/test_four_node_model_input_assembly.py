from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism.four_node_fresh_factory import (
    FourNodeM4FreshState,
    FourNodeSubstrateFreshState,
    build_four_node_role_fresh_bundle,
)
from mcm_field_organism.four_node_fresh_manifest import load_four_node_fresh_manifest
from mcm_field_organism.four_node_model_input_assembly import (
    NATIVE_SUBSTRATE_COPY,
    PUBLIC_FIELD_IDENTITY,
    FourNodeModelInputAssemblyError,
    assemble_four_node_model_input,
)


MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "s1rk_four_node_fresh_manifest.json"
)
MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "mcm_field_organism"
    / "four_node_model_input_assembly.py"
)
ROLES = (
    "A0_CURRENT_CONTACT",
    "A1_FAST_SH",
    "A2_B1_FIXED_ADAPTER",
    "A2_B2_INTEGRATOR",
    "A2_B3_LOCAL_LEAKY",
    "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL",
    "A2_B6_CONST_V",
    "A3_NORM",
    "M1_PARALLEL_LEAK",
    "M2_DELAY",
    "M2_REPLAY",
    "M4_DTS1_T1",
    "M5_DIRECT",
)
SUBSTRATE_ROLES = frozenset(ROLES[4:8])


def _field_shell(field) -> tuple[object, ...]:
    return (
        field.field_id,
        field.geometry_id,
        field.layer.layer_id,
        field.layer.sample_offsets,
        field.layer.periodic_axes,
        field.docks,
        field.last_distribution,
        tuple(
            (
                item.neuron_id,
                item.position,
                item.activation,
                item.afterimage,
                item.perception,
            )
            for item in field.layer.neurons
        ),
    )


class FourNodeModelInputAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_four_node_fresh_manifest(MANIFEST_PATH)

    def _bundle(self, role: str):
        return build_four_node_role_fresh_bundle(self.manifest, role)

    def test_all_fourteen_roles_assemble_in_registered_order(self) -> None:
        assemblies = tuple(
            assemble_four_node_model_input(self._bundle(role)) for role in ROLES
        )
        self.assertEqual(ROLES, tuple(item.model_role for item in assemblies))
        self.assertEqual(14, len({item.adapter_surface_id for item in assemblies}))

    def test_a0_and_a1_keep_public_field_identity_and_no_private_state(self) -> None:
        for role in ROLES[:2]:
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertIs(assembly.public_fresh_field, bundle.public_field)
                self.assertIs(assembly.model_input_field, bundle.public_field)
                self.assertEqual(PUBLIC_FIELD_IDENTITY, assembly.field_embedding_mode)
                self.assertIsNone(assembly.native_private_state_or_none)
                self.assertIsNone(assembly.configuration_binding_or_none)
                self.assertIsNone(assembly.registered_private_digest_or_none)

    def test_all_non_substrate_roles_keep_the_public_field_identity(self) -> None:
        for role in tuple(item for item in ROLES if item not in SUBSTRATE_ROLES):
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertIs(assembly.model_input_field, bundle.public_field)
                self.assertIsNone(assembly.model_input_field.substrate)
                self.assertIsNone(assembly.model_input_field.development)
                self.assertEqual(PUBLIC_FIELD_IDENTITY, assembly.field_embedding_mode)

    def test_b3_through_b6_receive_only_a_new_native_substrate_field(self) -> None:
        for role in SUBSTRATE_ROLES:
            with self.subTest(role=role):
                bundle = self._bundle(role)
                private = bundle.private_state_or_none
                assembly = assemble_four_node_model_input(bundle)
                self.assertIsInstance(private.native_state, FourNodeSubstrateFreshState)
                self.assertIsNot(assembly.model_input_field, bundle.public_field)
                self.assertIsNone(bundle.public_field.substrate)
                self.assertIs(
                    assembly.model_input_field.substrate,
                    private.native_state.substrate,
                )
                self.assertIs(
                    assembly.native_private_state_or_none,
                    private.native_state,
                )
                self.assertIsNone(assembly.model_input_field.development)
                self.assertEqual(NATIVE_SUBSTRATE_COPY, assembly.field_embedding_mode)

    def test_b3_through_b6_preserve_every_public_field_identity(self) -> None:
        for role in SUBSTRATE_ROLES:
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertEqual(
                    _field_shell(bundle.public_field),
                    _field_shell(assembly.model_input_field),
                )

    def test_stateful_roles_expose_exact_factory_private_object_and_digest(self) -> None:
        for role in ROLES[2:]:
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertIs(
                    assembly.native_private_state_or_none,
                    bundle.private_state_or_none.native_state,
                )
                self.assertEqual(
                    bundle.private_state_or_none.configuration_binding,
                    assembly.configuration_binding_or_none,
                )
                self.assertEqual(
                    bundle.registered_private_digest_or_none,
                    assembly.registered_private_digest_or_none,
                )

    def test_edge_bridge_roles_preserve_separate_registered_and_native_digests(self) -> None:
        for role in (
            "A2_B3_LOCAL_LEAKY",
            "A2_B4_LINEAR_COUPLED",
            "A2_B5_F3_FULL",
            "A2_B6_CONST_V",
            "M4_DTS1_T1",
        ):
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertEqual(
                    bundle.private_state_or_none.registered_edge_inventory_digest_or_none,
                    assembly.registered_edge_inventory_digest_or_none,
                )
                self.assertEqual(
                    bundle.private_state_or_none.native_edge_inventory_digest_or_none,
                    assembly.native_edge_inventory_digest_or_none,
                )
                self.assertNotEqual(
                    assembly.registered_edge_inventory_digest_or_none,
                    assembly.native_edge_inventory_digest_or_none,
                )

    def test_m2_modes_preserve_separate_geometry_digest_roles(self) -> None:
        for role in ("M2_DELAY", "M2_REPLAY"):
            with self.subTest(role=role):
                bundle = self._bundle(role)
                assembly = assemble_four_node_model_input(bundle)
                self.assertEqual(
                    bundle.private_state_or_none.registered_geometry_digest_or_none,
                    assembly.registered_geometry_digest_or_none,
                )
                self.assertEqual(
                    bundle.private_state_or_none.native_geometry_digest_or_none,
                    assembly.native_geometry_digest_or_none,
                )
                self.assertNotEqual(
                    assembly.registered_geometry_digest_or_none,
                    assembly.native_geometry_digest_or_none,
                )

    def test_m4_remains_external_and_has_no_candidate_sidecar(self) -> None:
        bundle = self._bundle("M4_DTS1_T1")
        assembly = assemble_four_node_model_input(bundle)
        self.assertIsInstance(assembly.native_private_state_or_none, FourNodeM4FreshState)
        self.assertIsNone(
            assembly.native_private_state_or_none.candidate_sidecar_digest_or_none
        )
        self.assertIs(assembly.model_input_field, bundle.public_field)
        self.assertIsNone(assembly.model_input_field.substrate)

    def test_assembly_digest_is_deterministic_across_separate_fresh_builds(self) -> None:
        for role in ROLES:
            with self.subTest(role=role):
                first = assemble_four_node_model_input(self._bundle(role))
                second = assemble_four_node_model_input(self._bundle(role))
                self.assertEqual(first.assembly_digest, second.assembly_digest)
                self.assertEqual(64, len(first.assembly_digest))
                self.assertIsNot(first.public_fresh_field, second.public_fresh_field)
                if role in SUBSTRATE_ROLES:
                    self.assertIsNot(first.model_input_field, second.model_input_field)
                    self.assertIsNot(
                        first.model_input_field.substrate,
                        second.model_input_field.substrate,
                    )

    def test_assembly_record_is_immutable_and_digest_tamper_fails_closed(self) -> None:
        assembly = assemble_four_node_model_input(self._bundle("A0_CURRENT_CONTACT"))
        with self.assertRaises(FrozenInstanceError):
            assembly.model_role = "A1_FAST_SH"  # type: ignore[misc]
        with self.assertRaisesRegex(FourNodeModelInputAssemblyError, "MODEL_INPUT_DIGEST_INVALID"):
            replace(assembly, assembly_digest="0" * 64)

    def test_non_bundle_and_role_state_mismatch_fail_closed(self) -> None:
        with self.assertRaisesRegex(FourNodeModelInputAssemblyError, "MODEL_INPUT_BUNDLE_INVALID"):
            assemble_four_node_model_input({})  # type: ignore[arg-type]
        b1 = self._bundle("A2_B1_FIXED_ADAPTER")
        forged = replace(b1, model_role="A0_CURRENT_CONTACT")
        with self.assertRaisesRegex(FourNodeModelInputAssemblyError, "MODEL_INPUT_ROLE_STATE_INVALID"):
            assemble_four_node_model_input(forged)

    def test_private_manifest_digest_tamper_fails_closed(self) -> None:
        bundle = self._bundle("A2_B2_INTEGRATOR")
        forged = replace(bundle, registered_private_digest_or_none="0" * 64)
        with self.assertRaisesRegex(FourNodeModelInputAssemblyError, "MODEL_INPUT_ROLE_STATE_INVALID"):
            assemble_four_node_model_input(forged)

    def test_foreign_substrate_in_public_field_fails_closed(self) -> None:
        a0 = self._bundle("A0_CURRENT_CONTACT")
        b3 = self._bundle("A2_B3_LOCAL_LEAKY")
        foreign_field = replace(
            a0.public_field,
            substrate=b3.private_state_or_none.native_state.substrate,
        )
        forged = replace(a0, public_field=foreign_field)
        with self.assertRaisesRegex(FourNodeModelInputAssemblyError, "MODEL_INPUT_PUBLIC_FIELD_INVALID"):
            assemble_four_node_model_input(forged)

    def test_module_contains_no_model_kernel_or_orchestrator_import(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        forbidden = (
            "from .neutral_local_field_substrate import",
            "from .mcm_f3_runtime import",
            "from .dynamic_substrate_dts1_coupled_step import",
            "from .dynamic_substrate_dts1_private_baseline_adapters import",
            "from .dynamic_substrate_dts1_one_replica_orchestrator import",
        )
        for statement in forbidden:
            with self.subTest(statement=statement):
                self.assertNotIn(statement, source)


if __name__ == "__main__":
    unittest.main()
