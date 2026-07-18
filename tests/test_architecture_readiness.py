from __future__ import annotations

from dataclasses import FrozenInstanceError
from itertools import permutations
import unittest

from mcm_field_organism import (
    ArchitectureBoundary,
    ArchitecturePlanError,
    ArchitectureReadinessPlan,
    BoundaryKind,
    EvidenceLevel,
    RuntimePermission,
    reference_architecture_plan,
)


class ArchitectureReadinessTests(unittest.TestCase):
    def test_reference_plan_is_canonical_and_reproducible(self) -> None:
        first = reference_architecture_plan()
        second = reference_architecture_plan()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(
            tuple(sorted(boundary.boundary_id for boundary in first.boundaries)),
            tuple(boundary.boundary_id for boundary in first.boundaries),
        )

    def test_plan_digest_is_independent_of_declaration_order(self) -> None:
        source = tuple(
            boundary
            for boundary in reference_architecture_plan().boundaries
            if not boundary.depends_on
        )
        digests = {ArchitectureReadinessPlan(order).digest() for order in permutations(source)}
        self.assertEqual(1, len(digests))

    def test_boundaries_are_immutable(self) -> None:
        boundary = reference_architecture_plan().boundary("receptor.distributor")
        with self.assertRaises(FrozenInstanceError):
            boundary.stateful = True  # type: ignore[misc]

    def test_distributor_is_before_the_field_and_remains_passive(self) -> None:
        distributor = reference_architecture_plan().boundary(
            "receptor.distributor"
        )
        self.assertEqual(BoundaryKind.RECEPTOR_DISTRIBUTOR, distributor.kind)
        self.assertEqual(("receptor_contact_frame",), distributor.accepts)
        self.assertEqual(("distributed_receptor_contact",), distributor.emits)
        self.assertFalse(distributor.stateful)
        self.assertFalse(distributor.writes_back)

    def test_shared_field_is_one_stateful_runtime_boundary(self) -> None:
        field = reference_architecture_plan().boundary("mcm.shared_field")
        self.assertEqual(BoundaryKind.SHARED_FIELD, field.kind)
        self.assertEqual(RuntimePermission.PASSIVE_AVAILABLE, field.permission)
        self.assertEqual(("distributed_receptor_contact",), field.accepts)
        self.assertEqual(("shared_mcm_field_state",), field.emits)
        self.assertEqual(("receptor.distributor",), field.depends_on)
        self.assertTrue(field.stateful)
        self.assertFalse(field.writes_back)

    def test_reflection_topology_and_semantic_resonance_are_closed(self) -> None:
        plan = reference_architecture_plan()
        expected = {
            "field.semantic_resonance",
            "field.topology_memory",
            "reflection.boundary",
            "tactile.receptor",
        }
        self.assertEqual(expected, set(plan.research_closed))
        for boundary_id in expected:
            boundary = plan.boundary(boundary_id)
            self.assertEqual(EvidenceLevel.E0, boundary.evidence)
            self.assertFalse(boundary.writes_back)

    def test_offline_recovery_is_only_a_boundary_contract(self) -> None:
        recovery = reference_architecture_plan().boundary("offline.recovery_boundary")
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, recovery.permission)
        self.assertEqual(("reduced_world_contact",), recovery.accepts)
        self.assertEqual((), recovery.emits)
        self.assertFalse(recovery.stateful)
        self.assertEqual(("field.energy_resource_boundary",), recovery.depends_on)

    def test_topology_memory_is_closed_without_runtime_writeback(self) -> None:
        boundary = reference_architecture_plan().boundary("field.topology_memory")
        self.assertEqual(RuntimePermission.RESEARCH_CLOSED, boundary.permission)
        self.assertEqual(EvidenceLevel.E0, boundary.evidence)
        self.assertEqual(
            {
                "repeated_local_joint_field_effect",
                "prior_local_field_organization",
                "local_available_resource",
            },
            set(boundary.accepts),
        )
        self.assertEqual(("changed_local_field_disposition",), boundary.emits)
        self.assertTrue(boundary.stateful)
        self.assertFalse(boundary.writes_back)

    def test_sensory_self_regulation_is_contract_only_without_device_control(
        self,
    ) -> None:
        boundary = reference_architecture_plan().boundary(
            "sensory.self_regulation"
        )
        self.assertEqual(BoundaryKind.RECEPTOR, boundary.kind)
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, boundary.permission)
        self.assertEqual(EvidenceLevel.E0, boundary.evidence)
        self.assertEqual(
            {
                "local_receptor_history",
                "local_field_consequence",
                "local_available_resource",
                "reduced_world_contact",
            },
            set(boundary.accepts),
        )
        self.assertEqual(
            ("candidate_local_receptor_disposition",),
            boundary.emits,
        )
        self.assertTrue(boundary.stateful)
        self.assertFalse(boundary.writes_back)
        self.assertIn("field.self_regulation", boundary.depends_on)
        payload = str(boundary.canonical_payload())
        for forbidden in (
            "device_volume",
            "microphone_gain",
            "target_loudness",
            "global_controller",
        ):
            self.assertNotIn(forbidden, payload)

    def test_mcm_self_regulation_is_a_separate_closed_field_contract(
        self,
    ) -> None:
        boundary = reference_architecture_plan().boundary(
            "field.self_regulation"
        )
        self.assertEqual(BoundaryKind.FIELD_CAPABILITY, boundary.kind)
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, boundary.permission)
        self.assertEqual(EvidenceLevel.E0, boundary.evidence)
        self.assertEqual(
            {
                "prior_local_field_history",
                "prior_internal_field_activity",
                "local_available_resource",
                "reduced_world_contact",
            },
            set(boundary.accepts),
        )
        self.assertEqual(
            ("candidate_local_field_disposition",),
            boundary.emits,
        )
        self.assertEqual(
            {
                "mcm.shared_field",
                "field.energy_resource_boundary",
            },
            set(boundary.depends_on),
        )
        self.assertTrue(boundary.stateful)
        self.assertFalse(boundary.writes_back)

    def test_wake_and_offline_share_one_energy_resource_boundary(self) -> None:
        plan = reference_architecture_plan()
        boundary = plan.boundary("field.energy_resource_boundary")
        self.assertEqual(BoundaryKind.ENERGY_RESOURCE, boundary.kind)
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, boundary.permission)
        self.assertEqual(EvidenceLevel.E0, boundary.evidence)
        self.assertEqual(
            {
                "current_world_contact",
                "prior_internal_field_activity",
                "prior_mcm_afterimage",
                "local_available_resource",
            },
            set(boundary.accepts),
        )
        self.assertEqual((), boundary.emits)
        self.assertFalse(boundary.stateful)
        self.assertFalse(boundary.writes_back)

        payload = str(plan.canonical_payload())
        for forbidden_gain in ("wake_gain", "offline_gain", "reflection_gain"):
            self.assertNotIn(forbidden_gain, payload)

    def test_sensory_paths_remain_separate_only_up_to_receptor_distribution(self) -> None:
        plan = reference_architecture_plan()
        for modality in ("auditory", "visual", "tactile"):
            receptor = plan.boundary(f"{modality}.receptor")
            self.assertEqual(BoundaryKind.RECEPTOR, receptor.kind)
        distributor = plan.boundary("receptor.distributor")
        self.assertEqual(
            {
                "auditory.receptor",
                "visual.receptor",
                "tactile.receptor",
            },
            set(distributor.depends_on),
        )
        self.assertNotIn(
            "sensor_field",
            {boundary.kind.value for boundary in plan.boundaries},
        )

    def test_visual_interface_is_e2_while_shared_field_stays_e1(self) -> None:
        plan = reference_architecture_plan()
        receptor = plan.boundary("visual.receptor")
        field = plan.boundary("mcm.shared_field")
        self.assertEqual(RuntimePermission.PASSIVE_AVAILABLE, receptor.permission)
        self.assertEqual(EvidenceLevel.E2, receptor.evidence)
        self.assertEqual(("finite_video_frames",), receptor.accepts)
        self.assertEqual(("visual_receptor_state",), receptor.emits)
        self.assertFalse(receptor.stateful)
        self.assertFalse(receptor.writes_back)
        self.assertEqual(RuntimePermission.PASSIVE_AVAILABLE, field.permission)
        self.assertEqual(EvidenceLevel.E1, field.evidence)
        self.assertTrue(field.stateful)
        self.assertFalse(field.writes_back)

    def test_forbidden_runtime_roles_are_rejected(self) -> None:
        for role in (
            "semantic_label",
            "pattern_class",
            "reward",
            "target_topology",
            "raw_episode",
            "observer_writeback",
        ):
            with self.subTest(role=role), self.assertRaises(ArchitecturePlanError):
                ArchitectureBoundary(
                    "invalid.boundary",
                    BoundaryKind.MEMORY,
                    RuntimePermission.RESEARCH_CLOSED,
                    EvidenceLevel.E0,
                    emits=(role,),
                )

    def test_closed_boundary_cannot_write_back(self) -> None:
        with self.assertRaises(ArchitecturePlanError):
            ArchitectureBoundary(
                "reflection.invalid",
                BoundaryKind.REFLECTION,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                writes_back=True,
            )

    def test_unknown_dependency_and_duplicate_ids_are_rejected(self) -> None:
        boundary = ArchitectureBoundary(
            "one.boundary",
            BoundaryKind.RECEPTOR,
            RuntimePermission.CONTRACT_ONLY,
            EvidenceLevel.E0,
        )
        with self.assertRaises(ArchitecturePlanError):
            ArchitectureReadinessPlan((boundary, boundary))
        dependent = ArchitectureBoundary(
            "two.boundary",
            BoundaryKind.SHARED_FIELD,
            RuntimePermission.RESEARCH_CLOSED,
            EvidenceLevel.E0,
            depends_on=("missing.boundary",),
        )
        with self.assertRaises(ArchitecturePlanError):
            ArchitectureReadinessPlan((dependent,))


if __name__ == "__main__":
    unittest.main()
