from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism.four_node_exposure_fixture import (
    ALIGN,
    CHECKPOINT,
    INTERVAL,
    FourNodeExposureFixtureError,
    build_four_node_exposure_fixture,
    validate_four_node_exposure_fixture,
)
from mcm_field_organism.four_node_fresh_matrix_registration import (
    FourNodeFreshMatrixRegistration,
    load_four_node_fresh_matrix_registration,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = load_four_node_fresh_matrix_registration(
    ROOT / "reports" / "s1sd_four_node_fresh_matrix_registration.json"
)


def _fixture():
    return build_four_node_exposure_fixture(REGISTRATION)


def _plan(role: str):
    return next(item for item in _fixture().plans if item.replica_role == role)


def _intervals(role: str):
    return tuple(
        event.interval_or_none
        for event in _plan(role).events
        if event.event_kind == INTERVAL
    )


class FourNodeExposureFixtureTests(unittest.TestCase):
    def test_fixture_has_registered_axis_and_counts(self) -> None:
        fixture = _fixture()
        self.assertEqual(17, len(fixture.plans))
        self.assertEqual(127, fixture.model_interval_count_per_role)
        self.assertEqual(17, fixture.align_count_per_role)
        self.assertEqual(40, fixture.checkpoint_count_per_role)
        self.assertEqual("U_FRESH_B_EARLY", fixture.plans[-2].replica_role)
        self.assertEqual("U_FRESH_B_LATE", fixture.plans[-1].replica_role)

    def test_fixture_is_deterministic_and_immutable(self) -> None:
        first = _fixture()
        second = _fixture()
        self.assertEqual(first, second)
        self.assertEqual(
            "ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e",
            first.fixture_digest,
        )
        with self.assertRaises(FrozenInstanceError):
            first.plans = ()  # type: ignore[misc]

    def test_contact_alphabet_and_clock_are_exact(self) -> None:
        expected = {
            "A_CONTACT": (0.0, 0.5, 0.0, 0.0),
            "B_CONTACT": (0.5, 0.0, 0.0, 0.0),
            "C_CONTACT": (0.0, 0.0, 0.0, 0.5),
            "PROBE_A_CONTACT": (0.0, 0.25, 0.0, 0.0),
            "PROBE_B_CONTACT": (0.25, 0.0, 0.0, 0.0),
        }
        seen = {}
        for plan in _fixture().plans:
            for event in plan.events:
                interval = event.interval_or_none
                if event.event_kind != INTERVAL or interval is None:
                    continue
                self.assertEqual("mcm.s1sf.field", interval.step_time.clock_id)
                self.assertEqual(10, interval.step_time.elapsed_ticks)
                self.assertEqual(1.0, interval.step_time.elapsed_seconds)
                if interval.payload_role != "ZERO_CONTACT":
                    frame = interval.distribution.contacts[0].frame
                    seen[interval.payload_role] = frame.values
        self.assertEqual(expected, seen)

    def test_zero_contact_has_no_frame(self) -> None:
        zero_intervals = tuple(
            interval
            for role in ("F_G", "I_GAP", "R_EARLY", "R_LATE")
            for interval in _intervals(role)
            if interval.payload_role == "ZERO_CONTACT"
        )
        self.assertTrue(zero_intervals)
        self.assertTrue(all(not item.distribution.contacts for item in zero_intervals))

    def test_snapshot_ids_exclude_plan_and_model_labels(self) -> None:
        for plan in _fixture().plans:
            for event in plan.events:
                interval = event.interval_or_none
                if interval is None or not interval.distribution.contacts:
                    continue
                snapshot = interval.distribution.contacts[0].frame.snapshot_id
                self.assertTrue(snapshot.startswith("s1sf."))
                self.assertNotIn(plan.replica_role.lower(), snapshot)
                self.assertNotIn("model", snapshot)

    def test_t_prefixes_are_exact_and_f_is_distinct(self) -> None:
        early = _intervals("T_EARLY")[:-1]
        later = _intervals("T_LATER")[:-1]
        formation = _intervals("F_A")[:-1]
        self.assertEqual(
            tuple(item.interval_digest for item in early),
            tuple(item.interval_digest for item in later[:2]),
        )
        self.assertEqual(2, len(early))
        self.assertEqual(3, len(formation))
        self.assertEqual(4, len(later))

    def test_f_and_interference_load_matching_is_exact(self) -> None:
        f_a = _intervals("F_A")[:-1]
        f_c = _intervals("F_C")[:-1]
        self.assertEqual(len(f_a), len(f_c))
        self.assertEqual(
            [item.step_time for item in f_a],
            [item.step_time for item in f_c],
        )
        local = _intervals("I_LOCAL")[4:6]
        remote = _intervals("I_REMOTE")[4:6]
        self.assertEqual(
            [item.step_time for item in local],
            [item.step_time for item in remote],
        )

    def test_c_plans_add_only_passive_competition_checkpoints(self) -> None:
        for c_role, i_role in (
            ("C_LOCAL", "I_LOCAL"),
            ("C_REMOTE", "I_REMOTE"),
            ("C_GAP", "I_GAP"),
        ):
            c_plan = _plan(c_role)
            i_plan = _plan(i_role)
            self.assertEqual(
                tuple(item.interval_digest for item in _intervals(c_role)),
                tuple(item.interval_digest for item in _intervals(i_role)),
            )
            extra = tuple(
                event.checkpoint_role_or_none
                for event in c_plan.events
                if event.event_kind == CHECKPOINT
            )
            self.assertEqual(
                ("PRE_COMPETITION", "POST_COMPETITION", "ALIGNED_PRE_PROBE", "POST_PROBE_READOUT"),
                extra,
            )
            self.assertEqual(2, i_plan.checkpoint_count)

    def test_release_gap_is_distinct_and_prefix_ordered(self) -> None:
        middle = tuple(
            item for item in _intervals("I_GAP") if item.payload_role == "ZERO_CONTACT"
        )
        early = tuple(
            item for item in _intervals("R_EARLY") if item.payload_role == "ZERO_CONTACT"
        )
        late = tuple(
            item for item in _intervals("R_LATE") if item.payload_role == "ZERO_CONTACT"
        )
        self.assertEqual((2, 3, 6), (len(middle), len(early), len(late)))
        self.assertEqual(
            tuple(item.interval_digest for item in early),
            tuple(item.interval_digest for item in late[:3]),
        )

    def test_u_early_and_late_pairs_share_b_and_probe_inputs(self) -> None:
        for history_role, fresh_role, b_start, probe_start in (
            ("U_EARLY", "U_FRESH_B_EARLY", 70, 90),
            ("U_RELEASED", "U_FRESH_B_LATE", 100, 120),
        ):
            history = _intervals(history_role)
            fresh = _intervals(fresh_role)
            history_tail = tuple(
                item for item in history if item.step_time.start_tick >= b_start
            )
            fresh_tail = tuple(
                item for item in fresh if item.step_time.start_tick >= b_start
            )
            self.assertEqual(
                tuple(item.interval_digest for item in history_tail),
                tuple(item.interval_digest for item in fresh_tail),
            )
            self.assertEqual(probe_start, history_tail[-1].step_time.start_tick)

    def test_align_and_checkpoint_events_are_time_free(self) -> None:
        for plan in _fixture().plans:
            aligns = tuple(event for event in plan.events if event.event_kind == ALIGN)
            self.assertEqual(1, len(aligns))
            target = aligns[0].align_target_or_none
            self.assertIsNotNone(target)
            self.assertEqual((0.0, 0.0, 0.0, 0.0), target.activation)
            self.assertIsNone(aligns[0].interval_or_none)
            for event in plan.events:
                if event.event_kind == CHECKPOINT:
                    self.assertIsNone(event.interval_or_none)

    def test_validator_accepts_only_the_canonical_fixture(self) -> None:
        fixture = _fixture()
        self.assertIsNone(validate_four_node_exposure_fixture(fixture, REGISTRATION))
        changed_plan = replace(fixture.plans[0], replica_role="CHANGED")
        changed = replace(fixture, plans=(changed_plan,) + fixture.plans[1:])
        with self.assertRaisesRegex(
            FourNodeExposureFixtureError,
            "FOUR_NODE_EXPOSURE_FIXTURE_PLAN_AXIS_INVALID",
        ):
            validate_four_node_exposure_fixture(changed, REGISTRATION)

    def test_invalid_registration_is_rejected(self) -> None:
        forged = FourNodeFreshMatrixRegistration({"registration_digest": "0" * 64})
        with self.assertRaisesRegex(
            FourNodeExposureFixtureError,
            "FOUR_NODE_EXPOSURE_FIXTURE_REGISTRATION_INVALID",
        ):
            build_four_node_exposure_fixture(forged)


if __name__ == "__main__":
    unittest.main()
