from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_DURATION_TICKS,
)
from mcm_field_organism.public_av_local_adaptive_receptivity_coupling_scheme_audit import (
    COUPLING_AUDIT_SCHEMES,
)
from mcm_field_organism.public_av_receptivity_history_intervention_audit import (
    HISTORY_INTERVENTION_ALPHA_AXIS,
    HISTORY_INTERVENTION_ARM_IDS,
    HISTORY_INTERVENTION_PARTITION_COUNT,
    HISTORY_INTERVENTION_ROLES,
    PublicAVReceptivityHistoryInterventionError,
    _exact_trace_onset_interval,
    _require_identical_control,
    _require_event_timeline_digest,
    _second_contact_event_timeline,
    _validated_axes,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)
from tools.run_public_av_receptivity_history_intervention_shard import (
    _output_path,
    _parser,
    main,
)


class PublicAVReceptivityHistoryInterventionAuditTests(unittest.TestCase):
    @staticmethod
    def _sequence(modality: str, completions: tuple[int, ...]):
        frames = tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality,
                    f"{modality}.geometry",
                    f"{modality}.{index}",
                    "organism.test",
                    completion - 1,
                    completion,
                    (f"{modality}.carrier",),
                    (1.0,),
                ),
                CommonFieldTime("organism.test", completion - 1, completion),
            )
            for index, completion in enumerate(completions)
        )
        return ReceptorTimeSequence(
            modality, f"{modality}.geometry", "organism.test", frames
        )

    def test_axes_partition_and_time_order_are_fixed(self) -> None:
        self.assertEqual((0.5, 1.0), HISTORY_INTERVENTION_ALPHA_AXIS)
        self.assertEqual(
            ("endpoint_energy", "midpoint_coupling"), COUPLING_AUDIT_SCHEMES
        )
        self.assertEqual(
            (2_000_000_000, 10_000_000_000, 20_000_000_000),
            CAUCHY_AUDIT_DURATION_TICKS,
        )
        self.assertEqual(320, HISTORY_INTERVENTION_PARTITION_COUNT)
        self.assertEqual(
            (0.5, "endpoint_energy"),
            _validated_axes(0.5, "endpoint_energy"),
        )
        with self.assertRaises(PublicAVReceptivityHistoryInterventionError):
            _validated_axes(0.0, "endpoint_energy")

    def test_intervention_and_control_arms_are_explicit(self) -> None:
        self.assertEqual(
            (
                "carried_receptivity",
                "reset_receptivity",
                "identical_carried_control",
            ),
            HISTORY_INTERVENTION_ARM_IDS,
        )
        self.assertEqual(
            ("activation", "afterimage", "local_energy", "receptivity"),
            HISTORY_INTERVENTION_ROLES,
        )
        source = Path(
            "mcm_field_organism/public_av_receptivity_history_intervention_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            "reset_receptivity = LocalReceptivityState.fresh(gap_field)",
            '"field_start_shared_between_arms": True',
            '"active_update_rule_shared_between_arms": True',
            '"sensor_events_and_time_axis_shared_between_arms": True',
            '"arm_event_timeline_digests_identical": True',
            '"trace_onset_intervals"',
            '"carried_to_reset_start_linf"',
            '"carried_to_reset_trace"',
        ):
            self.assertIn(token, source)

    def test_identical_arm_control_requires_exact_zero(self) -> None:
        zero = {role: 0.0 for role in HISTORY_INTERVENTION_ROLES}
        _require_identical_control(zero)
        zero["activation"] = 1e-15
        with self.assertRaises(PublicAVReceptivityHistoryInterventionError):
            _require_identical_control(zero)

    def test_second_contact_events_are_ordered_and_digest_repeatable(self) -> None:
        sequences = (
            self._sequence("visual", (110, 130)),
            self._sequence("auditory", (110, 120)),
        )
        timeline, digest = _second_contact_event_timeline(sequences, 100)
        self.assertEqual(
            [
                {"sequence_index": 0, "sensor_path": "auditory", "elapsed_ticks": 10},
                {"sequence_index": 1, "sensor_path": "visual", "elapsed_ticks": 10},
                {"sequence_index": 2, "sensor_path": "auditory", "elapsed_ticks": 20},
                {"sequence_index": 3, "sensor_path": "visual", "elapsed_ticks": 30},
            ],
            timeline,
        )
        repeated_timeline, repeated_digest = _second_contact_event_timeline(
            sequences, 100
        )
        self.assertEqual(timeline, repeated_timeline)
        self.assertEqual(digest, repeated_digest)

    def test_event_timeline_guard_rejects_before_field_construction(self) -> None:
        sequences = (
            self._sequence("visual", (10,)),
            self._sequence("auditory", (20,)),
        )
        with patch(
            "mcm_field_organism.public_av_receptivity_history_intervention_audit._sequences",
            return_value=sequences,
        ) as sequence_builder, patch(
            "mcm_field_organism.public_av_receptivity_history_intervention_audit._fresh_field"
        ) as fresh_field:
            with self.assertRaisesRegex(
                PublicAVReceptivityHistoryInterventionError,
                "differs from preregistration",
            ):
                from mcm_field_organism.public_av_receptivity_history_intervention_audit import (
                    execute_public_av_receptivity_history_intervention_shard,
                )
                execute_public_av_receptivity_history_intervention_shard(
                    Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
                    nasa_earthrise_av_source_contract(),
                    0.5,
                    "endpoint_energy",
                    start_tick=500_000_000,
                    expected_event_timeline_digest="wrong",
                )
        sequence_builder.assert_called_once_with(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            sequence_builder.call_args.args[1],
            start_tick=500_000_000,
        )
        fresh_field.assert_not_called()

    def test_runner_rejects_disjoint_interval_without_digest(self) -> None:
        with patch(
            "tools.run_public_av_receptivity_history_intervention_shard."
            "execute_public_av_receptivity_history_intervention_shard"
        ) as execute:
            with self.assertRaisesRegex(ValueError, "requires an expected"):
                main([
                    "--alpha", "0.50",
                    "--scheme", "endpoint_energy",
                    "--start-tick", "500000000",
                ])
        execute.assert_not_called()

    def test_event_timeline_guard_accepts_exact_digest(self) -> None:
        sequences = (
            self._sequence("visual", (10,)),
            self._sequence("auditory", (20,)),
        )
        _, digest = _second_contact_event_timeline(sequences, 0)
        self.assertEqual(digest, _require_event_timeline_digest(sequences, digest))

    def test_trace_onset_maps_to_exact_event_interval_without_tolerance(self) -> None:
        trace = [
            {"elapsed_ticks": 10, "carried_to_reset_linf": {"activation": 0.0}},
            {"elapsed_ticks": 20, "carried_to_reset_linf": {"activation": 1e-15}},
        ]
        events = [
            {"sequence_index": 0, "sensor_path": "auditory", "elapsed_ticks": 10},
            {"sequence_index": 1, "sensor_path": "visual", "elapsed_ticks": 20},
        ]
        self.assertEqual(
            {
                "trace_index": 1,
                "interval_start_elapsed_ticks": 10,
                "interval_end_elapsed_ticks": 20,
                "event_sequence_indices": [1],
            },
            _exact_trace_onset_interval(trace, "activation", events),
        )

    def test_claims_and_selection_remain_disabled(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_receptivity_history_intervention_audit.py"
        ).read_text(encoding="utf-8")
        for token in (
            '"threshold_defined": False',
            '"preferred_alpha_selected": False',
            '"preferred_scheme_selected": False',
            '"memory_claim_allowed": False',
            '"meaning_claim_allowed": False',
            '"organization_claim_allowed": False',
            '"consciousness_claim_allowed": False',
            '"ai_claim_allowed": False',
        ):
            self.assertIn(token, source)

    def test_runner_has_atomic_alpha_schema_paths(self) -> None:
        args = _parser().parse_args(
            ["--alpha", "1.00", "--scheme", "midpoint_coupling"]
        )
        self.assertEqual(1.0, args.alpha)
        self.assertEqual("midpoint_coupling", args.scheme)
        self.assertEqual(
            Path(
                "reports/shards/public_av_receptivity_history_intervention_"
                "alpha_1_00_scheme_midpoint_coupling_v1.json"
            ),
            _output_path(1.0, "midpoint_coupling"),
        )
        self.assertEqual(0, args.start_tick)
        self.assertIsNone(args.expected_event_timeline_digest)
        self.assertEqual(
            Path(
                "reports/shards/public_av_receptivity_history_intervention_"
                "alpha_1_00_scheme_midpoint_coupling_"
                "source_ticks_500000000_1000000000_v1.json"
            ),
            _output_path(1.0, "midpoint_coupling", 500_000_000),
        )
        source = Path(
            "tools/run_public_av_receptivity_history_intervention_shard.py"
        ).read_text(encoding="utf-8")
        self.assertIn("NamedTemporaryFile", source)
        self.assertIn("temporary.replace(output)", source)


if __name__ == "__main__":
    unittest.main()
