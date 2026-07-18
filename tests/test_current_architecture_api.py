from __future__ import annotations

import unittest

import mcm_field_organism as organism


class CurrentArchitectureAPITests(unittest.TestCase):
    def test_current_shared_field_contracts_are_public(self) -> None:
        required = {
            "CommonFieldTime",
            "ReceptorContactFrame",
            "ReceptorContractError",
            "ReceptorNeuronDockMap",
            "ReceptorDistributor",
            "ReceptorDock",
            "SharedMCMField",
            "SharedMCMFieldSnapshot",
            "SharedFieldSessionResult",
            "SharedFieldSessionWindow",
            "restore_shared_mcm_field",
            "run_shared_mcm_field_session",
            "assemble_shared_mcm_field",
            "capture_finite_audio_video_field",
            "capture_live_audio_video_field",
            "OrganismTimedReceptorFrame",
            "ReceptorTimeAlignmentAudit",
            "audit_receptor_time_alignment",
            "capture_live_audio_video_time_audit",
            "TransientDockTrajectory",
            "map_proposal_batch_to_transient_docks",
            "TransientNeuronInputSet",
            "project_transient_docks_to_neuron_inputs",
            "PassiveFieldSegmentationComparison",
            "compare_passive_field_segmentations",
            "contact_free_boundary_distribution",
            "PassiveDriveRole",
            "PassiveLocalDrive",
            "adapt_passive_local_transition",
            "compare_passive_field_role_ablations",
            "fixed_leaky_local_afterimage_baseline",
            "PassiveReceptorRateComparison",
            "PassiveFutureEventCausalityComparison",
            "compare_passive_receptor_rate",
            "compare_passive_future_event_causality",
            "PassiveSimultaneousOrderComparison",
            "compare_passive_simultaneous_order",
            "PassiveFieldGeometryComparison",
            "PassiveCarrierReflection",
            "PassiveNeuronReflection",
            "compare_passive_field_reflection",
        }
        self.assertTrue(required.issubset(set(organism.__all__)))
        for name in required:
            self.assertTrue(hasattr(organism, name), name)

    def test_former_multifield_architecture_is_not_package_api(self) -> None:
        historical = {
            "SensorMCMField",
            "SensorMCMFieldError",
            "MCMDistributor",
            "MCMFieldWindow",
            "MultimodalPatternChecker",
            "MultimodalPatternResult",
            "VisualMCMInterface",
            "FiniteMultimodalFieldResult",
            "SensorFieldAnatomy",
            "assemble_multimodal_field_constellation",
        }
        self.assertTrue(historical.isdisjoint(set(organism.__all__)))
        for name in historical:
            self.assertFalse(hasattr(organism, name), name)

    def test_neutral_receptor_contracts_do_not_come_from_legacy_field(self) -> None:
        for name in (
            "CommonFieldTime",
            "ReceptorContactFrame",
            "ReceptorContractError",
            "ReceptorNeuronDockMap",
        ):
            value = getattr(organism, name)
            self.assertEqual(
                "mcm_field_organism.receptor_contract",
                value.__module__,
            )


if __name__ == "__main__":
    unittest.main()
