from __future__ import annotations

import hashlib
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMLocalDevelopmentContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    advance_s1b_reciprocal_shared_field,
    attach_zero_mcm_local_development,
    build_shared_mcm_field,
)
from mcm_field_organism.s2_reference_runner import (
    S2_CONTROL_IDS,
    S2_METRIC_IDS,
    S2_PACKET_SCHEMA,
    S2ReferenceMeasurement,
    S2ReferenceRunnerError,
    S2ScalarMetric,
    S2TechnicalControl,
    assemble_s2_reference_packet,
    equalize_fast_state_for_probe,
    orchestrate_s2_reference_subset,
    project_s2_reference_packet,
)
from mcm_field_organism.s2_reference_worlds import build_s2_reference_tasks


EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"


def _source(values: tuple[float, float]) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        "visual",
        "visual.s2.runner.v1",
        "visual.s2.runner.snapshot.0",
        "visual.source",
        0,
        10,
        ("visual.carrier.0", "visual.carrier.1"),
        values,
    )


def _advanced_field():
    field = build_shared_mcm_field(
        (_source((0.0, 0.0)),),
        {
            "visual": ReceptorDockAnatomy(
                "visual", "dock.visual", ((0, 0), (0, 1))
            )
        },
        sample_offsets=((0, -1), (0, 1)),
    )
    field = attach_zero_mcm_local_development(
        field,
        MCMLocalDevelopmentContract(EQUATION_ID, 8.0, 0.25),
    )
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.visual", "visual", "visual.s2.runner.v1"))
    distribution = distributor.distribute(
        (_source((0.8, -0.2)),), CommonFieldTime("organism.s2", 0, 1000)
    )
    return advance_s1b_reciprocal_shared_field(
        field,
        distribution,
        MCMFieldStepTime("organism.s2", 0, 1000, 1000.0),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def _measurement(task) -> S2ReferenceMeasurement:
    digest = hashlib.sha256(task.task_id.encode("ascii")).hexdigest()
    return S2ReferenceMeasurement(
        task.task_id,
        task.world_id,
        task.model_id,
        task.intervention_id,
        digest,
        digest,
        digest,
        1,
        1,
        1,
        1,
        tuple(S2ScalarMetric(metric_id, 0.0) for metric_id in S2_METRIC_IDS),
        tuple(S2TechnicalControl(control_id, True) for control_id in S2_CONTROL_IDS),
    )


class S2ReferenceRunnerTests(unittest.TestCase):
    def test_fast_state_equalization_changes_only_s_and_h(self) -> None:
        field = _advanced_field()
        equalized = equalize_fast_state_for_probe(field)

        self.assertTrue(any(item.activation != 0.0 for item in field.layer.neurons))
        self.assertTrue(all(item.activation == 0.0 for item in equalized.layer.neurons))
        self.assertTrue(all(item.afterimage == 0.0 for item in equalized.layer.neurons))
        self.assertEqual(field.development, equalized.development)
        self.assertEqual(field.layer.tick, equalized.layer.tick)
        self.assertEqual(field.last_distribution, equalized.last_distribution)
        self.assertEqual(field.docks, equalized.docks)

    def test_subset_orchestration_checks_task_measurement_identity(self) -> None:
        tasks = build_s2_reference_tasks()[:3]
        observed = []

        def executor(task):
            observed.append(task.task_id)
            return _measurement(task)

        result = orchestrate_s2_reference_subset(tasks, executor)
        self.assertEqual(tuple(item.task_id for item in tasks), tuple(observed))
        self.assertEqual(tuple(item.task_id for item in tasks), tuple(item.task_id for item in result))

    def test_s2c_rejects_full_matrix_execution(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "full matrix"):
            orchestrate_s2_reference_subset(
                build_s2_reference_tasks(),
                lambda task: _measurement(task),
            )

    def test_packet_assembly_is_canonical_scalar_and_order_independent(self) -> None:
        tasks = build_s2_reference_tasks()
        measurements = tuple(_measurement(task) for task in tasks)
        first = assemble_s2_reference_packet(measurements, "a" * 64)
        second = assemble_s2_reference_packet(reversed(measurements), "a" * 64)
        payload = project_s2_reference_packet(first)

        self.assertEqual(S2_PACKET_SCHEMA, payload["schema"])
        self.assertEqual(152, payload["task_count"])
        self.assertTrue(payload["all_technical_controls_passed"])
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(first.digest(), payload["packet_digest"])
        self.assertNotIn("run_id", payload)
        self.assertNotIn("decision", payload)

    def test_failed_control_is_retained_without_a_research_decision(self) -> None:
        tasks = build_s2_reference_tasks()
        measurements = [_measurement(task) for task in tasks]
        first = measurements[0]
        controls = list(first.controls)
        controls[0] = S2TechnicalControl(controls[0].control_id, False)
        measurements[0] = S2ReferenceMeasurement(
            first.task_id,
            first.world_id,
            first.model_id,
            first.intervention_id,
            first.start_snapshot_digest,
            first.boundary_snapshot_digest,
            first.end_snapshot_digest,
            first.event_count,
            first.audio_hop_count,
            first.video_frame_count,
            first.field_tick_count,
            first.metrics,
            tuple(controls),
        )

        packet = assemble_s2_reference_packet(measurements, "b" * 64)
        self.assertFalse(packet.all_technical_controls_passed)
        self.assertNotIn("research_decision", packet.canonical_payload())


if __name__ == "__main__":
    unittest.main()
