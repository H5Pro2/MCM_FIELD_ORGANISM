"""Neutral qualification for the private S2-JZ variation boundary."""

from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools import _s2jz_perceptual_variation_result_verifier as verifier
from tools import _s2jz_perceptual_variation_runner as runner
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2jz_perceptual_variation_fixtures import (
    FIXTURE_RECIPE_DIGEST,
    FIXTURE_ROLES,
    S2JZFixtureStream,
)
from tools._s2jz_perceptual_variation_measurement import (
    direct_l1_prototype_baseline,
    measure_receptor_distance,
    measure_transition,
    state_slot_projection,
    validate_variation_measurements,
)


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2jz-qualification-20260902-01"


def _selected(slot_id: str) -> dict[str, object]:
    return {"slot_id": slot_id}


def _baseline(stable: bool) -> dict[str, object]:
    support = 3 if stable else 1
    payload = {
        "state_digest": "a" * 64,
        "fixture_digest": "b" * 64,
        "fast_thresholds": [0.2, 0.2],
        "slow_thresholds": [0.2, 0.2],
        "fast": [{"slot_id": "fast", "auditory_distance": 0.0, "visual_distance": 0.0}],
        "auditory_slow": [{"slot_id": "auditory", "support": support, "distance": 0.0}],
        "visual_slow": [{"slot_id": "visual", "support": support, "distance": 0.0}],
    }
    return {**payload, "baseline_digest": runner._digest(payload)}


def _probe(role: str, stable: bool, fast_slot: str) -> dict[str, object]:
    return {
        "evaluation_role": role,
        "probe_digest": "1" * 64,
        "finding_digest": "2" * 64,
        "prestate_digest": "3" * 64,
        "poststate_digest": "3" * 64,
        "b4_selected": _selected("b4"),
        "fast_selected": _selected(fast_slot),
        "auditory_slow_selected": _selected("auditory") if stable else None,
        "visual_slow_selected": _selected("visual") if stable else None,
        "native_tspm_finding_digest": "4" * 64,
        "ledger_digest": "5" * 64,
        "baseline": _baseline(stable),
        "baseline_agrees": True,
    }


def _valid_stories() -> list[dict[str, object]]:
    stories = []
    for index, (story_id, formation_roles, probe_roles) in enumerate(runner.HISTORIES):
        stable = story_id != "g4"
        if stable:
            auditory_slow = [["auditory", 3, 4, "6" * 64]]
            visual_slow = [["visual", 3, 4, "7" * 64]]
            fast = [["fast", 4, 4, "8" * 64]]
        else:
            auditory_slow = [["auditory-0", 1, 2, "6" * 64], ["auditory-1", 1, 4, "7" * 64]]
            visual_slow = [["visual-0", 1, 2, "8" * 64], ["visual-1", 1, 4, "9" * 64]]
            fast = [["fast-0", 2, 2, "a" * 64], ["fast-1", 2, 4, "b" * 64]]
        probes = [
            _probe(role, stable, f"fast-{probe_index}" if not stable else "fast")
            for probe_index, role in enumerate(probe_roles)
        ]
        stories.append({
            "story_id": story_id,
            "story_owner_id": f"s2jz-neutral-story-owner-{index}",
            "initial_generation": 0,
            "initial_state_digest": "0" * 64,
            "formations": [{"evaluation_role": role} for role in formation_roles],
            "final_state": {
                "generation": 4,
                "state_digest": "c" * 64,
                "b4": [],
                "fast": fast,
                "auditory_slow": auditory_slow,
                "visual_slow": visual_slow,
            },
            "probes": probes,
        })
    return stories


def _complete_record(preflight: list[dict[str, object]]) -> dict[str, object]:
    chain = runner._OperationChain([])
    for role in verifier.EXPECTED_ROLES:
        chain.append(role, {"neutral_evidence_digest": "d" * 64})
    stories = _valid_stories()
    payload = {
        "schema": runner.S2JZ_RESULT_SCHEMA,
        "run_id": QUALIFICATION_ID,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": runner.source_hashes(ROOT),
        "fixture_recipe_digest": FIXTURE_RECIPE_DIGEST,
        "preflight_measurements": preflight,
        "plan": {
            "histories": [[sid, list(formations), list(probes)] for sid, formations, probes in runner.HISTORIES],
            "formation_count": 20,
            "probe_count": 9,
            "memory_operation_count": 116,
            "baseline_call_count": 29,
            "memory_l1_limit": 153_120,
            "raw_payload_retained": False,
            "field_read": False,
            "thresholds_changed": False,
        },
        "operations": chain.records,
        "stories": stories,
        "functional_evaluation": runner.evaluate_story_evidence(stories),
        "last_operation_digest": chain.previous_digest,
    }
    return runner._seal(payload)


def _write_record(root: Path, record: dict[str, object]) -> Path:
    directory = root / str(record["run_id"])
    directory.mkdir()
    runner._atomic_write(directory / "result.json", record)
    return directory


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = deepcopy(record)
    payload.pop("record_digest", None)
    return runner._seal(payload)


class S2JZPerceptualVariationQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = build_s2jw_default_live_profile()
        cls.limits = build_s2jv_ledger_limits(cls.profile)
        cls.config = coordinator.build_s2jv_coordinator_config(
            tspm_config=cls.profile.tspm_config,
            b4_capacity=cls.profile.b4_capacity,
            ledger_limits=cls.limits,
        )
        stream = S2JZFixtureStream(cls.profile, "s2jz-neutral-qualification-clock")
        cls.fixtures = tuple(stream.materialize(role, index) for index, role in enumerate(FIXTURE_ROLES))
        cls.measurements = validate_variation_measurements(tuple(
            measure_receptor_distance(cls.fixtures[0], fixture) for fixture in cls.fixtures
        ))
        cls.preflight = [
            item.payload_without_digest() | {"measurement_digest": item.measurement_digest}
            for item in cls.measurements
        ]

    def test_01_main_gate_is_closed_and_full_run_is_rejected(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertIsNone(runner.AUTHORIZED_RUN_ID)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(runner.S2JZRunnerError):
                runner.run_main_once(Path(temporary).resolve(), ROOT, QUALIFICATION_ID)

    def test_02_bound_history_and_cost_scope_is_exact(self) -> None:
        self.assertEqual((5, 20, 9, 116, 29, 153_120), (
            len(runner.HISTORIES),
            runner.FORMATION_COUNT,
            runner.PROBE_COUNT,
            runner.MEMORY_OPERATION_COUNT,
            runner.BASELINE_CALL_COUNT,
            runner.MEMORY_L1_LIMIT,
        ))
        self.assertEqual(116, len(verifier.EXPECTED_ROLES))

    def test_03_all_real_fixture_roles_reduce_to_default_live_dimensions(self) -> None:
        self.assertEqual(FIXTURE_ROLES, tuple(item.role for item in self.fixtures))
        self.assertTrue(all(
            len(item.pair.auditory.timed_frame.frame.values) == 48
            and len(item.pair.visual.timed_frame.frame.values) == 288
            for item in self.fixtures
        ))
        self.assertFalse(any(hasattr(item, "pixel_bytes") or hasattr(item, "pcm_bytes") for item in self.fixtures))

    def test_04_a1_distance_comes_from_materialized_receptor_values(self) -> None:
        a1 = next(item for item in self.measurements if item.candidate_role == "A1")
        recomputed = measure_receptor_distance(self.fixtures[0], self.fixtures[3])
        print(f"S2JZ_ACTUAL_A1_AUDITORY_L1={a1.auditory_distance:.17g}")
        self.assertEqual(a1.measurement_digest, recomputed.measurement_digest)
        self.assertGreater(a1.auditory_distance, 0.0)
        self.assertLess(a1.auditory_distance, 0.01)
        self.assertEqual(0.0, a1.visual_distance)

    def test_05_visual_and_combined_variations_match_frozen_intervals(self) -> None:
        by_role = {item.candidate_role: item for item in self.measurements}
        self.assertTrue(math.isclose(by_role["V1"].visual_distance, 2.0 / 255.0, rel_tol=0.0, abs_tol=1e-15))
        self.assertEqual(by_role["A1"].auditory_distance, by_role["C1"].auditory_distance)
        self.assertEqual(by_role["V1"].visual_distance, by_role["C1"].visual_distance)

    def test_06_exact_control_and_distractor_are_separated(self) -> None:
        by_role = {item.candidate_role: item for item in self.measurements}
        self.assertEqual((0.0, 0.0), (by_role["E0"].auditory_distance, by_role["E0"].visual_distance))
        self.assertGreater(by_role["Z1"].auditory_distance, 0.02)
        self.assertGreater(by_role["Z1"].visual_distance, 0.2)

    def test_07_fresh_histories_use_separate_objects_not_distinct_digest_claims(self) -> None:
        states = [coordinator.initial_s2jv_composite_state(self.config) for _ in range(5)]
        self.assertEqual(1, len({state.state_digest for state in states}))
        self.assertEqual(5, len({id(state) for state in states}))
        self.assertTrue(all(state.generation == 0 for state in states))
        self.assertTrue(runner.evaluate_story_evidence(_valid_stories())["claims"]["five_fresh_histories"])

    def test_08_one_atomic_step_and_probe_preserve_read_only_state(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.fixtures[0].pair)
        owner = coordinator.S2JVFormationOwner(
            "s2jz-neutral-owner",
            "s2jz-neutral-authorization",
            "s2jz-neutral-consumption",
            self.config.config_digest,
            state.state_digest,
            source.input_digest,
        )
        result = coordinator.advance_s2jv_atomic(config=self.config, prestate=state, source=source, owner=owner)
        transition = measure_transition(state, result)
        probe = coordinator.bind_s2jv_probe(config=self.config, source=self.fixtures[1].pair)
        finding = read_only.probe_s2jv_composite_read_only(config=self.config, state=result.poststate, probe=probe)
        self.assertEqual((state.state_digest, result.poststate.state_digest), (
            transition["prestate_digest"], transition["poststate_digest"]
        ))
        self.assertEqual((result.poststate.state_digest, result.poststate.state_digest), (
            finding.prestate_digest, finding.poststate_digest
        ))

    def test_09_projection_and_direct_baseline_do_not_mutate_state(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        before = state.state_digest
        projection = state_slot_projection(state)
        baseline = direct_l1_prototype_baseline(self.config, state, self.fixtures[0])
        self.assertEqual((before, before, 0, []), (
            state.state_digest, projection["state_digest"], projection["generation"], baseline["fast"]
        ))

    def test_10_complete_synthetic_record_is_independently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), _complete_record(self.preflight))
            finding = verifier.verify_s2jz_result(directory.resolve(), ROOT)
        self.assertEqual(("RECORDING_COMPLETE", "S2JY_VARIATION_IDENTITY_CONFIRMED", 116), (
            finding.status, finding.functional_status, finding.operation_count
        ))

    def test_11_functional_deviation_remains_evaluable_falsification(self) -> None:
        record = _complete_record(self.preflight)
        record["stories"][0]["probes"][0]["fast_selected"] = None
        record["stories"][0]["probes"][0]["baseline_agrees"] = False
        record["functional_evaluation"] = runner.evaluate_story_evidence(record["stories"])
        record = _reseal(record)
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jz_result(directory.resolve(), ROOT)
        self.assertEqual(("RECORDING_COMPLETE", "S2JY_VARIATION_IDENTITY_FALSIFIED"), (
            finding.status, finding.functional_status
        ))

    def test_12_tampering_raw_payload_and_overwrite_fail_closed(self) -> None:
        record = _complete_record(self.preflight)
        record["preflight_measurements"][3]["measurement_digest"] = "0" * 64
        record["raw_payload"] = "forbidden"
        record = _reseal(record)
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jz_result(directory.resolve(), ROOT)
            with self.assertRaises(runner.S2JZRunnerError):
                runner._atomic_write(directory / "result.json", record)
        self.assertEqual("NOT_EVALUABLE", finding.status)


if __name__ == "__main__":
    unittest.main()
