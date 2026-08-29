"""Twelve neutral S2-FW qualification tests for the locked S2-FV boundary."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2fv_private_recording as recording
from tools import _s2fv_private_result_verifier as result_verifier
from tools import _s2fv_private_runner as runner
from tools import _visual_sequence_memory_probe as sequence_probe


QUALIFICATION_RUN_ID = "s2fw-neutral-qualification-20260829-01"


def _profile():
    return bind_ppb1_receptor_profile(
        "browser",
        PPB1ProfileParameters(
            PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
            PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
        ),
    )


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.s2fw.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(config, values: tuple[float, ...]) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.s2fw.{config.modality_id}.{index:03d}",
                "synthetic.s2fw.organism-clock",
                index * 10,
                (index + 1) * 10,
                config.carrier_ids,
                tuple(value for _ in config.carrier_ids),
            ),
            CommonFieldTime(
                "synthetic.s2fw.field-clock",
                index * 10,
                (index + 1) * 10,
            ),
        )
        for index, value in enumerate(values)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "synthetic.s2fw.field-clock",
        frames,
    )


def _neutral_fixture():
    profile = _profile()
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    config = coordinator.build_coordinator_config(tspm_config)
    world = _world()
    batch = BrowserReceptorSequenceBatch(
        world.contract_id,
        world.digest(),
        (
            _sequence(profile.auditory_config, (0.1, 0.12)),
            _sequence(profile.visual_config, (0.3, 0.32)),
        ),
    )
    envelope = bind_ppb1_active_receptor_batch(
        "binding.s2fw.neutral",
        world,
        batch,
        profile,
    )
    return config, envelope


def _bound_input(config, envelope, index: int = 0):
    return coordinator.bind_coordinator_input(
        config,
        envelope,
        envelope.auditory_stream.timed_frames[index],
        envelope.visual_stream.timed_frames[index],
    )


def _bound_probe(config, envelope, index: int = 1):
    return coordinator.bind_coordinator_probe(
        config,
        envelope,
        envelope.auditory_stream.timed_frames[index],
        envelope.visual_stream.timed_frames[index],
    )


def _fresh_b4_state():
    return runner.comparison._B4State(
        0,
        tuple(
            runner.comparison._FIFOEntry(f"b4.slot.{index:03d}", False, (), None)
            for index in range(9)
        ),
    )


def _one_step_paths():
    config, envelope = _neutral_fixture()
    source = _bound_input(config, envelope)
    composite_initial = coordinator.initial_composite_state(config)
    composite_owner = coordinator.B4TSPM1CoordinatorOwner(
        "s2fw.owner.composite",
        "s2fw.authorization.composite",
        "s2fw.consumption.composite",
        config.config_digest,
        composite_initial.state_digest,
        source.input_digest,
    )
    composite = composite_owner.consume_once(config, composite_initial, source).poststate

    b4_initial = _fresh_b4_state()
    b4, _, _ = runner.comparison._advance_b4(b4_initial, source.av_values, 1)

    tspm_initial = tspm1.initial_tspm1_composite_state(config.tspm_config)
    tspm_owner = tspm1.TSPM1CoordinatorOwner(
        "s2fw.owner.tspm",
        "s2fw.authorization.tspm",
        "s2fw.consumption.tspm",
        config.tspm_config.config_binding_digest,
        tspm_initial.composite_state_digest,
        source.tspm_exposure.exposure_digest,
    )
    tspm = tspm_owner.consume_once(
        config.tspm_config,
        tspm_initial,
        source.tspm_exposure,
    ).poststate
    return config, envelope, source, composite_initial, composite, b4_initial, b4, tspm_initial, tspm


def _recording_plan(run_id: str) -> recording.S2FVRecordingPlan:
    return recording.S2FVRecordingPlan(
        run_id,
        "s2fw.neutral.qualification.v1",
        (("qualification.source", "1" * 64),),
        "2" * 64,
        "3" * 64,
    )


def _emit_operation(
    recorder: recording.S2FVAppendOnlyRecorder,
    operation_index: int,
    operation: str,
    operation_id: str,
    source_digest: str,
    result_payload: dict[str, object],
) -> None:
    start = recorder.emit(
        f"{operation}_START",
        {
            "operation_id": operation_id,
            "operation_index": operation_index,
            "source_digest": source_digest,
        },
    )
    recorder.emit(
        f"{operation}_RESULT",
        {
            "operation_id": operation_id,
            "operation_index": operation_index,
            "source_digest": source_digest,
            "start_event_digest": start,
            **result_payload,
        },
    )


def _complete_synthetic_recording(root: Path, run_id: str) -> Path:
    recorder = recording.S2FVAppendOnlyRecorder(root, _recording_plan(run_id))
    operation_index = 0
    for ordinal in range(1, 25):
        _emit_operation(
            recorder,
            operation_index,
            "RECEPTOR_ANALYSIS",
            f"s2fw.receptor.{ordinal:03d}",
            recording.digest(["receptor", ordinal]),
            {"qualification_only": True},
        )
        operation_index += 1
    for step in range(1, 19):
        source_digest = recording.digest(["formation", step])
        for arm in ("COMPOSITE", "B4", "TSPM1"):
            _emit_operation(
                recorder,
                operation_index,
                "FORMATION",
                f"s2fw.formation.{step:03d}.{arm.lower()}",
                source_digest,
                {"step": step, "arm": arm},
            )
            operation_index += 1
    for step in range(1, 19):
        state_digest = recording.digest(["identity", step])
        _emit_operation(
            recorder,
            operation_index,
            "COMPONENT_IDENTITY",
            f"s2fw.identity.{step:03d}",
            recording.digest(["identity-source", step]),
            {
                "step": step,
                "identity_valid": True,
                "prestate_digest": state_digest,
                "poststate_digest": state_digest,
            },
        )
        operation_index += 1
    sequence_state = recording.digest("neutral-sequence-state")
    _emit_operation(
        recorder,
        operation_index,
        "SEQUENCE_PROBE",
        "s2fw.sequence.001",
        recording.digest("neutral-sequence-source"),
        {
            "prestate_digest": sequence_state,
            "poststate_digest": sequence_state,
            "tspm_sequence_status": "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
            "automatic_view_selection": None,
        },
    )
    operation_index += 1
    for fixture_id in ("neutral.probe.alpha", "neutral.probe.beta"):
        source_digest = recording.digest(["content", fixture_id])
        for arm in ("COMPOSITE", "B4", "TSPM1"):
            state_digest = recording.digest(["content-state", fixture_id, arm])
            _emit_operation(
                recorder,
                operation_index,
                "CONTENT_PROBE",
                f"s2fw.content.{fixture_id}.{arm.lower()}",
                source_digest,
                {
                    "arm": arm,
                    "probe_fixture_id": fixture_id,
                    "prestate_digest": state_digest,
                    "poststate_digest": state_digest,
                    "automatic_view_selection": None,
                },
            )
            operation_index += 1
    if operation_index != 103:
        raise AssertionError("neutral operation inventory differs")
    return recorder.finalize(
        {
            "schema": recording.EVIDENCE_PACKAGE_SCHEMA,
            "operation_count": 103,
            "event_count": 206,
            "automatic_view_selection": None,
            "tspm_sequence_status": "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
            "functional_assessment": None,
            "qualification_only": True,
        }
    )


class S2FWNeutralRunnerRecordingVerifierQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name)
        cls.completed = _complete_synthetic_recording(cls.root, QUALIFICATION_RUN_ID)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_01_main_gate_is_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(runner.S2FVRunnerError):
                runner.run_main_once(Path(temporary), "s2fw.gate.must-remain-closed")
            self.assertEqual((), tuple(Path(temporary).iterdir()))

    def test_02_plan_and_source_binding_are_exact(self) -> None:
        plan = runner.materialize_recording_plan("s2fw.plan.qualification")
        self.assertEqual((24, 54, 18, 1, 6, 103, 206), (
            plan.receptor_analysis_count,
            plan.formation_count,
            plan.component_identity_count,
            plan.sequence_probe_count,
            plan.content_probe_count,
            plan.operation_count,
            plan.event_count,
        ))
        roles = {role for role, _ in plan.source_digests}
        self.assertEqual(11, len(roles))
        self.assertIn("runner.source", roles)
        self.assertIn("recording.source", roles)
        self.assertIn("verifier.source", roles)
        self.assertEqual(runner.fixtures.FIXTURE_DIGEST, plan.fixture_digest)

    def test_03_neutral_receptor_analysis(self) -> None:
        image = np.zeros((80, 120, 3), dtype=np.uint8)
        image[:40, :40, :] = 96
        image[40:, 80:, :] = 192
        image.setflags(write=False)
        receptor = runner.LocalChannelGridReceptor(runner._VISUAL_CONFIG)
        finding = receptor.analyze(image, frame_index=0)
        self.assertEqual(18, len(finding.channel_values))
        self.assertEqual(0.0, finding.channel_values[3])
        self.assertEqual(192 / 255.0, finding.channel_values[-1])
        self.assertFalse(image.flags.writeable)

    def test_04_neutral_composite_b4_and_tspm_advance_once(self) -> None:
        path = _one_step_paths()
        _, _, source, composite_initial, composite, b4_initial, b4, tspm_initial, tspm = path
        self.assertEqual((0, 0, 0), (
            composite_initial.generation,
            b4_initial.accepted_count,
            tspm_initial.generation,
        ))
        self.assertEqual((1, 1, 1), (composite.generation, b4.accepted_count, tspm.generation))
        self.assertEqual(source.input_digest, composite.last_input_digest)

    def test_05_composite_components_equal_standalone_components(self) -> None:
        _, _, _, _, composite, _, b4, _, tspm = _one_step_paths()
        self.assertEqual(
            runner._b4_digest(composite.b4_state),
            runner._b4_digest(b4),
        )
        self.assertEqual(
            composite.tspm_state.composite_state_digest,
            tspm.composite_state_digest,
        )

    def test_06_neutral_sequence_probe_is_read_only(self) -> None:
        state = _fresh_b4_state()
        values = tuple((0.0,) * 8 + (level,) * 18 for level in (0.0, 0.3, 0.6, 0.9))
        for index, offered in enumerate(values, start=1):
            state, _, _ = runner.comparison._advance_b4(state, offered, index)
        before = runner._b4_digest(state)
        finding = sequence_probe.probe_visual_sequence_read_only(state, values)
        self.assertTrue(finding["ordered"]["recognized"])
        self.assertTrue(finding["order_blind"]["recognized"])
        self.assertEqual(before, runner._b4_digest(state))

    def test_07_neutral_content_probe_preserves_state(self) -> None:
        config, envelope, _, _, composite, _, _, _, _ = _one_step_paths()
        probe = _bound_probe(config, envelope)
        before = composite.state_digest
        finding = coordinator.probe_composite_read_only(config, composite, probe)
        self.assertEqual(("B4_RECENT", "TSPM_FAST", "TSPM_SLOW"), finding.roles)
        self.assertEqual(before, finding.prestate_digest)
        self.assertEqual(before, finding.poststate_digest)
        self.assertEqual(before, composite.state_digest)

    def test_08_valid_synthetic_recording_has_exact_103_206_inventory(self) -> None:
        events = (self.completed / "events.jsonl").read_text(encoding="ascii").splitlines()
        self.assertEqual(206, len(events))
        terminal = json.loads((self.completed / "terminal.json").read_text(encoding="ascii"))
        self.assertEqual(206, terminal["event_count"])
        self.assertEqual("COMPLETE_RECORDING", terminal["technical_status"])
        self.assertEqual(
            {"manifest.json", "events.jsonl", "evidence.json", "terminal.json", "COMPLETE"},
            {path.name for path in self.completed.iterdir()},
        )

    def test_09_independent_verifier_accepts_complete_recording(self) -> None:
        finding = result_verifier.verify_s2fv_result(self.completed)
        self.assertEqual("RECORDING_COMPLETE", finding.status)
        self.assertEqual((103, 206), (finding.operation_count, finding.event_count))
        self.assertEqual((), finding.issues)

    def test_10_wrong_order_count_or_operation_id_is_rejected(self) -> None:
        for role in ("order", "count", "operation-id"):
            with self.subTest(role=role):
                target = self.root / f"s2fw.mutated.{role}"
                shutil.copytree(self.completed, target)
                event_path = target / "events.jsonl"
                lines = event_path.read_text(encoding="ascii").splitlines()
                if role == "order":
                    lines[0], lines[1] = lines[1], lines[0]
                elif role == "count":
                    lines.pop()
                else:
                    event = json.loads(lines[2])
                    event["payload"]["operation_id"] = json.loads(lines[0])["payload"]["operation_id"]
                    lines[2] = json.dumps(event, sort_keys=True, separators=(",", ":"))
                event_path.write_text("\n".join(lines) + "\n", encoding="ascii")
                self.assertEqual(
                    "NOT_EVALUABLE",
                    result_verifier.verify_s2fv_result(target).status,
                )

    def test_11_tampered_digest_file_or_completion_marker_is_rejected(self) -> None:
        digest_target = self.root / "s2fw.mutated.digest"
        file_target = self.root / "s2fw.mutated.file"
        marker_target = self.root / "s2fw.mutated.marker"
        for target in (digest_target, file_target, marker_target):
            shutil.copytree(self.completed, target)
        manifest = json.loads((digest_target / "manifest.json").read_text(encoding="ascii"))
        manifest["configuration_digest"] = "f" * 64
        (digest_target / "manifest.json").write_text(json.dumps(manifest), encoding="ascii")
        (file_target / "unexpected.txt").write_text("unexpected", encoding="ascii")
        marker = json.loads((marker_target / "COMPLETE").read_text(encoding="ascii"))
        marker["terminal_digest"] = "e" * 64
        (marker_target / "COMPLETE").write_text(json.dumps(marker), encoding="ascii")
        for target in (digest_target, file_target, marker_target):
            self.assertEqual("NOT_EVALUABLE", result_verifier.verify_s2fv_result(target).status)

    def test_12_partial_reuse_and_overwrite_fail_closed(self) -> None:
        plan = _recording_plan("s2fw.partial.qualification")
        recorder = recording.S2FVAppendOnlyRecorder(self.root, plan)
        recorder.emit(
            "RECEPTOR_ANALYSIS_START",
            {
                "operation_id": "s2fw.partial.operation",
                "operation_index": 0,
                "source_digest": "4" * 64,
            },
        )
        with self.assertRaises(recording.S2FVRecordingError):
            recorder.finalize({"schema": recording.EVIDENCE_PACKAGE_SCHEMA})
        recorder.leave_not_evaluable("S2FW_PARTIAL_RECORDING")
        with self.assertRaises(recording.S2FVRecordingError):
            recorder.emit("RECEPTOR_ANALYSIS_RESULT", {})
        with self.assertRaises(FileExistsError):
            recording.S2FVAppendOnlyRecorder(self.root, plan)
        finding = result_verifier.verify_s2fv_result(self.root / plan.run_id)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertFalse((self.root / plan.run_id / "COMPLETE").exists())


if __name__ == "__main__":
    unittest.main()
