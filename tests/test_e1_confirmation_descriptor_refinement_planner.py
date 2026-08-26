from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_av_history_permutation import (
    build_e1_av_history_permutation,
)
from mcm_field_organism.e1_confirmation_descriptor_refinement_planner import (
    E1ConfirmationDescriptorRefinementPlannerError,
    build_e1_confirmation_descriptor_refinement_plans,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
)
from mcm_field_organism.e1_confirmation_typed_prepared_inputs import (
    E1ConfirmationTypedPreparedInputsError,
    prepare_e1_confirmation_typed_execution_bundle,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
    _typed_inputs,
)


def _descriptor_plans(descriptor, source, probe):
    return (
        build_e1_confirmation_descriptor_refinement_plans(
            descriptor,
            source.history_ab,
            horizon_start_tick=0,
            horizon_end_tick=2_000_000,
            ticks_per_second=1_000_000.0,
        ),
        build_e1_confirmation_descriptor_refinement_plans(
            descriptor,
            source.history_ba,
            horizon_start_tick=0,
            horizon_end_tick=2_000_000,
            ticks_per_second=1_000_000.0,
        ),
        build_e1_confirmation_descriptor_refinement_plans(
            descriptor,
            probe,
            horizon_start_tick=0,
            horizon_end_tick=1_000_000,
            ticks_per_second=1_000_000.0,
        ),
    )


class E1ConfirmationDescriptorRefinementPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.legacy = _typed_inputs()
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        cls.source = build_e1_av_history_permutation()
        cls.probe = _fixed_probe_sequences()
        cls.ab, cls.ba, cls.probe_plans = _descriptor_plans(
            cls.descriptor, cls.source, cls.probe
        )

    def test_all_plan_fields_match_legacy_for_ab_ba_and_probe(self) -> None:
        pairs = (
            (self.ab, self.legacy.history_ab_plans),
            (self.ba, self.legacy.history_ba_plans),
            (self.probe_plans, self.legacy.probe_plans),
        )

        for current, legacy in pairs:
            self.assertEqual(
                tuple(asdict(item) for item in legacy.plans),
                tuple(asdict(item) for item in current.plans),
            )
            self.assertEqual(legacy.source_contact_digest, current.source_contact_digest)
            self.assertEqual(legacy.source_event_count, current.source_event_count)
            self.assertEqual(legacy.completion_ticks, current.completion_ticks)
            self.assertEqual(
                self.descriptor.digest(), current.research_descriptor_digest
            )

    def test_planner_builds_without_consulting_terminal_target_paths(self) -> None:
        before = tuple(path.exists() for path in CANONICAL_TARGETS)
        rebuilt = _descriptor_plans(self.descriptor, self.source, self.probe)

        self.assertEqual(
            (self.ab.digest(), self.ba.digest(), self.probe_plans.digest()),
            tuple(item.digest() for item in rebuilt),
        )
        self.assertEqual(before, tuple(path.exists() for path in CANONICAL_TARGETS))

    def test_s1ec2_accepts_only_complete_descriptor_plan_family(self) -> None:
        typed = replace(
            self.legacy,
            corridor=self.descriptor,
            history_ab_plans=self.ab,
            history_ba_plans=self.ba,
            probe_plans=self.probe_plans,
        )
        with TemporaryDirectory() as directory:
            bundle = prepare_e1_confirmation_typed_execution_bundle(
                Path(directory), lambda: typed
            )

            self.assertIs(self.ab, bundle.value("history_ab_plans"))
            self.assertIs(self.probe_plans, bundle.value("probe_plans"))

        with self.assertRaisesRegex(
            E1ConfirmationTypedPreparedInputsError,
            "cannot mix legacy and descriptor-bound plans",
        ):
            replace(typed, history_ab_plans=self.legacy.history_ab_plans)

    def test_invalid_horizon_fails_without_building_a_plan(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationDescriptorRefinementPlannerError,
            "clock or horizon is invalid",
        ):
            build_e1_confirmation_descriptor_refinement_plans(
                self.descriptor,
                self.source.history_ab,
                horizon_start_tick=2_000_000,
                horizon_end_tick=0,
                ticks_per_second=1_000_000.0,
            )


if __name__ == "__main__":
    unittest.main()
