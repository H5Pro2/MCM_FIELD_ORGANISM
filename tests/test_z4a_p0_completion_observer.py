from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    advance_neutral_fast_shared_field_transient,
    build_shared_mcm_field,
    handoff_receptor_completion_groups,
    map_proposal_batch_to_transient_docks,
    project_transient_docks_to_neuron_inputs,
)
from mcm_field_organism.z4a_component_trajectory import Z4ATrajectoryObserver


def frame(index: int, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        "synthetic",
        "synthetic.geometry.v1",
        f"synthetic.snapshot.{index}",
        "synthetic.source",
        index,
        index + 1,
        ("synthetic.carrier.0",),
        (value,),
    )


def sequence(completions=((2, 0.8), (4, -0.3), (5, 0.4))):
    return ReceptorTimeSequence(
        "synthetic",
        "synthetic.geometry.v1",
        "z4a.synthetic",
        tuple(
            OrganismTimedReceptorFrame(
                frame(index, value),
                CommonFieldTime("z4a.synthetic", tick - 1, tick),
            )
            for index, (tick, value) in enumerate(completions)
        ),
    )


def fresh_field():
    return build_shared_mcm_field(
        (frame(100, 0.0),),
        {
            "synthetic": ReceptorDockAnatomy(
                "synthetic",
                "dock.synthetic",
                ((0,),),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def execute(completions=((2, 0.8), (4, -0.3), (5, 0.4)), observer=None):
    field = fresh_field()
    step = MCMFieldStepTime("z4a.synthetic", 0, 6, 10.0)
    current_handoff = handoff_receptor_completion_groups(
        (sequence(completions),),
        (step,),
    )
    batch = current_handoff.batches[0]
    dock_trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
    inputs = project_transient_docks_to_neuron_inputs(
        dock_trajectory,
        field.docks,
    )
    result = advance_neutral_fast_shared_field_transient(
        field,
        ReceptorDistribution(CommonFieldTime("z4a.synthetic", 0, 6), ()),
        inputs,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        _state_observer=observer,
    )
    return field, result


class Z4AP0CompletionObserverTests(unittest.TestCase):
    def test_observer_reports_completions_and_distinct_proposal_end(self) -> None:
        observed = []
        _, result = execute(observer=lambda tick, s, h: observed.append((tick, s, h)))
        self.assertEqual((2, 4, 5, 6), tuple(item[0] for item in observed))
        np.testing.assert_array_equal(
            observed[-1][1],
            np.asarray([item.activation for item in result.layer.neurons]),
        )
        np.testing.assert_array_equal(
            observed[-1][2],
            np.asarray([item.afterimage for item in result.layer.neurons]),
        )

    def test_completion_at_proposal_end_is_reported_once(self) -> None:
        ticks = []
        execute(
            completions=((2, 0.8), (6, 0.4)),
            observer=lambda tick, _s, _h: ticks.append(tick),
        )
        self.assertEqual((2, 6), tuple(ticks))

    def test_observer_on_off_and_mutation_preserve_final_snapshot(self) -> None:
        _, unobserved = execute()

        def mutating_observer(_tick, activation, afterimage):
            activation[:] = 99.0
            afterimage[:] = -99.0

        _, observed = execute(observer=mutating_observer)
        self.assertEqual(
            unobserved.snapshot().digest(),
            observed.snapshot().digest(),
        )

    def test_callback_adapts_to_role_variable_p0_trajectory(self) -> None:
        initial = fresh_field()
        trajectory_observer = Z4ATrajectoryObserver(
            "p0.exact",
            0,
            (
                (
                    "activation",
                    tuple(item.activation for item in initial.layer.neurons),
                ),
                (
                    "afterimage",
                    tuple(item.afterimage for item in initial.layer.neurons),
                ),
            ),
        )

        def adapter(tick, activation, afterimage):
            trajectory_observer(
                tick,
                (("activation", activation), ("afterimage", afterimage)),
            )

        _, result = execute(observer=adapter)
        trajectory = trajectory_observer.trajectory()
        self.assertEqual("p0.exact", trajectory.model_id)
        self.assertEqual((0, 2, 4, 5, 6), tuple(s.tick for s in trajectory.samples))
        self.assertEqual(("activation", "afterimage"), trajectory.component_ids)
        self.assertIsNone(result.substrate)

    def test_invalid_observer_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            NeutralLocalFieldSubstrateError,
            "observer must be callable",
        ):
            execute(observer=object())


if __name__ == "__main__":
    unittest.main()
