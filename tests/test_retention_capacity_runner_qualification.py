"""Eight neutral qualification tests for the locked retention runner path."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism import _tspm1_private as tspm1
from tools import _retention_capacity_fixtures as fixture_types
from tools import _retention_capacity_recording as recording
from tools import _retention_capacity_result_verifier as result_verifier
from tools import _retention_capacity_runner as runner


def _pattern(pattern_id: str, cells: tuple[int, ...]) -> fixture_types.PatternFixture:
    return fixture_types.PatternFixture(
        pattern_id,
        "qualification",
        cells,
        (0.0,) * 8,
        tuple(value / 255.0 for value in cells for _ in range(3)),
    )


Q_ALPHA = _pattern("qalpha", (180, 60, 180, 60, 180, 60))
Q_BETA = _pattern("qbeta", (60, 180, 60, 180, 60, 180))


def _expectation(step: int, event: str, ppb_calls: int) -> fixture_types.FastStepExpectation:
    return fixture_types.FastStepExpectation(step, event, ppb_calls)


Q_STORY = fixture_types.StoryFixture(
    "qstory",
    (),
    (),
    (
        _expectation(1, "FAST_CREATED", 0),
        _expectation(2, "FAST_UPDATED", 1),
    ),
    1,
)


class _CaptureRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def emit(self, kind: str, payload: dict[str, object]) -> str:
        previous = self.events[-1]["event_digest"] if self.events else None
        body = {
            "index": len(self.events),
            "previous_event_digest": previous,
            "kind": kind,
            "payload": payload,
        }
        event_digest = recording.digest(body)
        self.events.append({**body, "event_digest": event_digest})
        return event_digest


def _context() -> runner._RunContext:
    profile, config = runner._profile_and_config()
    return runner._RunContext(
        _CaptureRecorder(),
        profile,
        config,
        runner._world(),
        runner.LocalChannelGridReceptor(runner._VISUAL_CONFIG),
    )


def _sample(
    context: runner._RunContext,
    *,
    arm_id: str,
    ordinal: int,
    pattern: fixture_types.PatternFixture,
    start: int,
    phase: str = "exposure",
) -> runner._BoundPerceptualInput:
    return runner._analyze_input(
        context,
        arm_id=arm_id,
        story_id="qstory",
        phase=phase,
        operation_ordinal=ordinal,
        window_start=start,
        window_end=start + 1,
        pattern=pattern,
    )


def _one_b4_path():
    context = _context()
    initial = runner._fresh_b4_state()
    sample = _sample(context, arm_id="B4", ordinal=1, pattern=Q_ALPHA, start=0)
    poststate = runner._advance_b4(context, initial, sample, story_id="qstory", step=1)
    return context, initial, poststate, sample


def _two_step_tspm_path():
    context = _context()
    initial = tspm1.initial_tspm1_composite_state(context.tspm_config)
    first_sample = _sample(context, arm_id="TSPM1", ordinal=1, pattern=Q_ALPHA, start=0)
    first = runner._advance_tspm1(context, initial, first_sample, story=Q_STORY, step=1)
    second_sample = _sample(context, arm_id="TSPM1", ordinal=2, pattern=Q_ALPHA, start=1)
    second = runner._advance_tspm1(context, first, second_sample, story=Q_STORY, step=2)
    return context, initial, first, second


def _recording_plan(run_id: str) -> recording.RecordingPlan:
    return recording.RecordingPlan(
        run_id,
        "retention.capacity.qualification.v1",
        (("qualification.source", "1" * 64),),
        "2" * 64,
    )


class RetentionCapacityRunnerQualificationTests(unittest.TestCase):
    def test_01_main_scope_and_execution_gate_remain_fixed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertEqual((146, 170, 16, 316, 1296), runner._EXPECTED_COUNTS)
        self.assertEqual(1296, recording.EXPECTED_TOTAL_EVENTS)
        self.assertEqual(1296, sum(recording.EXPECTED_EVENT_COUNTS.values()))
        with self.assertRaises(recording.RetentionRecordingError):
            recording.RecordingPlan(
                "qualification.invalid",
                "retention.capacity.qualification.v1",
                (("qualification.source", "1" * 64),),
                "2" * 64,
                event_count=12,
            )

    def test_02_small_real_b4_path_starts_fresh(self) -> None:
        context, initial, poststate, sample = _one_b4_path()
        self.assertEqual(0, initial.accepted_count)
        self.assertEqual(1, poststate.accepted_count)
        self.assertEqual(Q_ALPHA.av_values, sample.av_values)
        occupied = tuple(entry for entry in poststate.entries if entry.occupied)
        self.assertEqual(1, len(occupied))
        self.assertEqual((Q_ALPHA.av_values, 1), (occupied[0].values, occupied[0].formation_index))
        self.assertEqual(
            ["IMAGE_ANALYSIS_START", "IMAGE_ANALYSIS_RESULT", "STATE_OPERATION_START", "STATE_OPERATION_RESULT"],
            [event["kind"] for event in context.recorder.events],
        )

    def test_03_small_real_tspm_path_separates_fast_and_slow(self) -> None:
        context, initial, first, second = _two_step_tspm_path()
        self.assertEqual((0, 0, 0), (
            initial.fast_state.accepted_exposure_count,
            initial.auditory_ppb1_state.accepted_step_count,
            initial.visual_ppb1_state.accepted_step_count,
        ))
        self.assertEqual((1, 0, 0), (
            first.fast_state.accepted_exposure_count,
            first.auditory_ppb1_state.accepted_step_count,
            first.visual_ppb1_state.accepted_step_count,
        ))
        self.assertEqual((2, 1, 1), (
            second.fast_state.accepted_exposure_count,
            second.auditory_ppb1_state.accepted_step_count,
            second.visual_ppb1_state.accepted_step_count,
        ))
        fast = tuple(slot for slot in second.fast_state.slots if slot.occupied)
        auditory = tuple(slot for slot in second.auditory_ppb1_state.slots if slot.occupied)
        visual = tuple(slot for slot in second.visual_ppb1_state.slots if slot.occupied)
        self.assertEqual((1, 1, 1), (len(fast), len(auditory), len(visual)))
        self.assertEqual((2, 1, 1), (
            fast[0].support_count,
            auditory[0].support_count,
            visual[0].support_count,
        ))
        self.assertIs(context.recorder.events[-1]["payload"]["visual_slow_transition"]["stable"], False)

    def test_04_b4_probe_is_read_only(self) -> None:
        context, _, state, _ = _one_b4_path()
        before = runner.comparison._digest(runner.comparison._canonical(state))
        probe_sample = _sample(
            context,
            arm_id="B4",
            ordinal=1,
            pattern=Q_ALPHA,
            start=1000,
            phase="probe",
        )
        finding = runner._probe_b4(
            context,
            state,
            probe_sample,
            story_id="qstory",
            checkpoint=1,
            probe_ordinal=1,
        )
        after = runner.comparison._digest(runner.comparison._canonical(state))
        self.assertTrue(finding.recognized)
        self.assertEqual(before, after)
        self.assertEqual(finding.prestate_digest, finding.poststate_digest)

    def test_05_tspm_probe_is_read_only_with_separate_components(self) -> None:
        context, _, _, state = _two_step_tspm_path()
        before = state.composite_state_digest
        probe_sample = _sample(
            context,
            arm_id="TSPM1",
            ordinal=1,
            pattern=Q_ALPHA,
            start=1000,
            phase="probe",
        )
        finding = runner._probe_tspm1(
            context,
            state,
            probe_sample,
            story_id="qstory",
            checkpoint=2,
            probe_ordinal=1,
        )
        self.assertEqual(before, state.composite_state_digest)
        self.assertEqual(finding.prestate_digest, finding.poststate_digest)
        self.assertEqual(finding.prestate_component_digests, finding.poststate_component_digests)
        self.assertTrue(finding.native_fast_recognized)
        self.assertEqual("SLOW_NOT_RECOGNIZED", finding.auditory_slow.native_status)
        self.assertEqual("SLOW_NOT_RECOGNIZED", finding.visual_slow.native_status)

    def test_06_event_order_chain_bindings_and_input_boundary(self) -> None:
        context, _, _, _ = _one_b4_path()
        events = context.recorder.events
        self.assertEqual(
            ["IMAGE_ANALYSIS_START", "IMAGE_ANALYSIS_RESULT", "STATE_OPERATION_START", "STATE_OPERATION_RESULT"],
            [event["kind"] for event in events],
        )
        for index, event in enumerate(events):
            self.assertEqual(index, event["index"])
            self.assertEqual(events[index - 1]["event_digest"] if index else None, event["previous_event_digest"])
        self.assertEqual(events[0]["event_digest"], events[1]["payload"]["start_event_digest"])
        self.assertEqual(events[2]["event_digest"], events[3]["payload"]["start_event_digest"])
        operator_input = events[2]["payload"]["operator_input"]
        self.assertEqual({"values", "formation_index"}, set(operator_input))
        self.assertNotIn("pattern_id", operator_input)
        self.assertFalse(any("expected" in key for key in operator_input))

    def test_07_incomplete_recording_and_directory_reuse_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = _recording_plan("qualification.incomplete")
            recorder = recording.PrivateEvidenceRecorder(root, plan)
            recorder.emit("IMAGE_ANALYSIS_START", {"qualification": True})
            with self.assertRaises(recording.RetentionRecordingError):
                recorder.finalize({"functional_assessment": None})
            recorder.leave_not_evaluable()
            finding = result_verifier.verify_recorded_result(root / plan.run_id)
            self.assertEqual("NOT_EVALUABLE", finding.status)
            with self.assertRaises(FileExistsError):
                recording.PrivateEvidenceRecorder(root, plan)

    def test_08_complete_bound_recording_verifies_and_tampering_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = _recording_plan("qualification.complete")
            recorder = recording.PrivateEvidenceRecorder(root, plan)
            for index in range(316):
                start = recorder.emit("IMAGE_ANALYSIS_START", {"qualification_index": index})
                recorder.emit("IMAGE_ANALYSIS_RESULT", {"start_event_digest": start})
            for index in range(316):
                start = recorder.emit(
                    "STATE_OPERATION_START",
                    {"qualification_index": index, "operator_input": {"values_digest": "3" * 64}},
                )
                recorder.emit(
                    "STATE_OPERATION_RESULT",
                    {
                        "operation": "QUALIFICATION_EVENT",
                        "start_event_digest": start,
                        "prestate_digest": "4" * 64,
                        "poststate_digest": "4" * 64,
                    },
                )
            for index in range(16):
                start = recorder.emit("SEQUENCE_STATUS_START", {"qualification_index": index})
                recorder.emit(
                    "SEQUENCE_STATUS_RESULT",
                    {"start_event_digest": start, "state_transition_called": False},
                )
            completed = recorder.finalize({"functional_assessment": None, "qualification_only": True})
            self.assertEqual("RECORDING_COMPLETE", result_verifier.verify_recorded_result(completed).status)

            tampered = root / "qualification.tampered"
            missing = root / "qualification.missing"
            shutil.copytree(completed, tampered)
            shutil.copytree(completed, missing)
            result_path = tampered / "result.json"
            result = json.loads(result_path.read_text(encoding="ascii"))
            result["technical_status"] = "ALTERED"
            result_path.write_text(json.dumps(result, sort_keys=True), encoding="ascii")
            (missing / "terminal.json").unlink()
            self.assertEqual("NOT_EVALUABLE", result_verifier.verify_recorded_result(tampered).status)
            self.assertEqual("NOT_EVALUABLE", result_verifier.verify_recorded_result(missing).status)


if __name__ == "__main__":
    unittest.main()
