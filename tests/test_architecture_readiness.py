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
        boundary = reference_architecture_plan().boundary("mcm.distributor")
        with self.assertRaises(FrozenInstanceError):
            boundary.stateful = True  # type: ignore[misc]

    def test_distributor_is_passive_and_accepts_only_completed_mcm_fields(self) -> None:
        distributor = reference_architecture_plan().boundary("mcm.distributor")
        self.assertEqual(("mcm_field_window",), distributor.accepts)
        self.assertEqual(("distributed_mcm_constellation",), distributor.emits)
        self.assertFalse(distributor.stateful)
        self.assertFalse(distributor.writes_back)

    def test_reflection_relationship_memory_and_topology_are_closed(self) -> None:
        plan = reference_architecture_plan()
        expected = {
            "memory.developed_topology",
            "reflection.boundary",
            "tactile.mcm_field",
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

    def test_relationship_persistence_is_contract_only_without_runtime_writeback(self) -> None:
        boundary = reference_architecture_plan().boundary("memory.relationship_history")
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, boundary.permission)
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

    def test_sensory_paths_remain_separate_before_distribution(self) -> None:
        plan = reference_architecture_plan()
        for modality in ("auditory", "visual", "tactile"):
            receptor = plan.boundary(f"{modality}.receptor")
            field = plan.boundary(f"{modality}.mcm_field")
            self.assertEqual(BoundaryKind.RECEPTOR, receptor.kind)
            self.assertEqual(BoundaryKind.SENSOR_FIELD, field.kind)
            self.assertIn(receptor.boundary_id, field.depends_on)
            self.assertEqual(("mcm_field_window",), field.emits)

    def test_visual_interface_is_e2_while_field_dynamics_stay_contract_only(self) -> None:
        plan = reference_architecture_plan()
        receptor = plan.boundary("visual.receptor")
        field = plan.boundary("visual.mcm_field")
        self.assertEqual(RuntimePermission.PASSIVE_AVAILABLE, receptor.permission)
        self.assertEqual(EvidenceLevel.E2, receptor.evidence)
        self.assertEqual(("finite_video_frames",), receptor.accepts)
        self.assertEqual(("visual_receptor_state",), receptor.emits)
        self.assertFalse(receptor.stateful)
        self.assertFalse(receptor.writes_back)
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, field.permission)
        self.assertEqual(EvidenceLevel.E2, field.evidence)
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
            BoundaryKind.SENSOR_FIELD,
            RuntimePermission.RESEARCH_CLOSED,
            EvidenceLevel.E0,
            depends_on=("missing.boundary",),
        )
        with self.assertRaises(ArchitecturePlanError):
            ArchitectureReadinessPlan((dependent,))


if __name__ == "__main__":
    unittest.main()
