"""One-shot S2-HB qualification of the compact S2-HA receptor receipt."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tools import _s2gt_private_append_only_recorder as recording
from tools import _s2gt_private_fixture_registry as fixtures
from tools import _s2gt_private_result_verifier as verifier
from tools import _s2gt_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2hb-compact-receipt-qualification-20260830-01"
RECEPTOR_CLASSES = {
    "FORMATION_RECEPTOR_ANALYSIS",
    "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS",
    "CONSUMER_RECEPTOR_ANALYSIS",
}
FORBIDDEN_RECEIPT_FIELDS = {
    "envelope",
    "auditory_stream",
    "visual_stream",
    "timed_frames",
    "carrier_ids",
    "auditory_values",
    "visual_values",
    "av_values",
    "tspm_exposure",
    "tspm_probe",
}


def _canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("ascii")


def _source_arguments(row: dict[str, str]) -> tuple[str, str, str, int, int, str]:
    operation_class = row["operation_class"]
    history_id = row["history"]
    ordinal = int(row["source_ordinal"])
    if operation_class == "FORMATION_RECEPTOR_ANALYSIS":
        history = next(item for item in fixtures.HISTORIES if item.history_id == history_id)
        step = history.steps[ordinal - 1]
        return (
            f"s2gt.{history_id}.formation.{ordinal:02d}",
            step.visual_fixture_id,
            step.auditory_fixture_id,
            step.window_start,
            step.window_end,
            "FORMATION",
        )
    if operation_class == "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS":
        history = next(item for item in fixtures.HISTORIES if item.history_id == history_id)
        return (
            f"s2gt.{history_id}.probe.full.01",
            history.full_probe_visual_id,
            history.full_probe_auditory_id,
            13,
            14,
            "READ_ONLY",
        )
    if operation_class == "CONSUMER_RECEPTOR_ANALYSIS":
        return ("s2gt.shared.consumer.01", "J1-T", "Q0", 14, 15, "READ_ONLY")
    raise AssertionError("non-receptor operation supplied")


def _load_events(directory: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (directory / "journal/operations.jsonl")
        .read_text(encoding="ascii")
        .splitlines()
    ]


class S2HBCompactReceptorReceiptQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._temporary.cleanup)
        cls.runtime = runner._runtime()
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            QUALIFICATION_ID,
            "s2gw-run-owner",
        )
        reserved = recording.AppendOnlyRunRecorder.reserve(
            Path(cls._temporary.name),
            plan,
            registry,
        )
        if type(reserved) is not recording.AppendOnlyRunRecorder:
            raise AssertionError("S2-HB qualification reservation failed")
        cls.recorder = reserved
        cls.registry = registry
        cls.recorded_sources: list[runner._RecordedReceptorSource] = []
        cls.source_identity_preserved: list[bool] = []

        while cls.recorder.next_operation_index <= fixtures.SUCCESS_OPERATION_COUNT:
            row = cls.recorder._row()
            operation_id = row["operation_id"]
            if row["operation_class"] in RECEPTOR_CLASSES:
                arguments = _source_arguments(row)
                holder: dict[str, runner._BoundSource] = {}

                def materialize(
                    bound_arguments: tuple[str, str, str, int, int, str] = arguments,
                ) -> runner._BoundSource:
                    source = runner._analyze(cls.runtime, *bound_arguments)
                    holder["source"] = source
                    return source

                recorded = runner._record_receptor(
                    cls.recorder,
                    row["operation_class"],
                    {
                        "qualification_id": QUALIFICATION_ID,
                        "source_id": arguments[0],
                    },
                    materialize,
                    history=row["history"],
                    source_ordinal=row["source_ordinal"],
                )
                cls.recorded_sources.append(recorded)
                cls.source_identity_preserved.append(recorded.source is holder["source"])
                continue

            start_payload: dict[str, object] = {
                "qualification_id": QUALIFICATION_ID,
                "neutral_operation": operation_id,
            }
            previous_row = registry.operation_rows[int(row["index"]) - 2]
            if previous_row["operation_class"] in RECEPTOR_CLASSES:
                previous = cls.recorded_sources[-1]
                start_payload.update(
                    {
                        "receptor_receipt_digest": previous.receptor_receipt_digest,
                        "source_digest": previous.source.source_digest,
                    }
                )
            cls.recorder.start(operation_id, start_payload)
            cls.recorder.finish(
                operation_id,
                {
                    "qualification_id": QUALIFICATION_ID,
                    "neutral_result": operation_id,
                },
            )

        cls.run_directory = cls.recorder.run_directory
        cls.events = _load_events(cls.run_directory)
        cls.receptor_rows = tuple(
            row
            for row in registry.operation_rows
            if row["operation_class"] in RECEPTOR_CLASSES
        )

    def test_01_all_57_compact_receipt_projections(self) -> None:
        self.assertEqual(len(self.recorded_sources), 57)
        self.assertEqual(len(self.receptor_rows), 57)
        for row in self.receptor_rows:
            artifact = json.loads(
                (self.run_directory / row["target_path"]).read_text(encoding="ascii")
            )
            receipt = artifact["artifact"]["result"]
            self.assertEqual(receipt["schema"], runner.COMPACT_RECEPTOR_RECEIPT_SCHEMA)
            self.assertEqual(receipt["operation_id"], row["operation_id"])
            self.assertEqual(set(receipt), verifier.COMPACT_RECEPTOR_RECEIPT_FIELDS)

    def test_02_all_receipt_sizes_are_within_bound_range(self) -> None:
        sizes = [
            (self.run_directory / row["target_path"]).stat().st_size
            for row in self.receptor_rows
        ]
        self.assertEqual((min(sizes), max(sizes)), (2_747, 2_765))
        self.assertTrue(all(size < 4_096 for size in sizes))

    def test_03_full_objects_are_not_serialized_into_receipts(self) -> None:
        for row in self.receptor_rows:
            artifact = json.loads(
                (self.run_directory / row["target_path"]).read_text(encoding="ascii")
            )
            receipt = artifact["artifact"]["result"]
            self.assertTrue(FORBIDDEN_RECEIPT_FIELDS.isdisjoint(receipt))
            self.assertTrue(
                all(not isinstance(value, (dict, list)) for value in receipt.values())
            )

    def test_04_full_in_memory_source_identity_is_unchanged(self) -> None:
        self.assertEqual(len(self.source_identity_preserved), 57)
        self.assertTrue(all(self.source_identity_preserved))
        self.assertTrue(
            all(type(item.source) is runner._BoundSource for item in self.recorded_sources)
        )

    def test_05_receipt_digest_is_bound_by_direct_successor(self) -> None:
        by_operation_phase = {
            (str(event["operation_id"]), str(event["phase"])): event
            for event in self.events
        }
        for row, recorded in zip(self.receptor_rows, self.recorded_sources):
            result = by_operation_phase[(row["operation_id"], "RESULT")]
            successor = by_operation_phase[(row["successor"], "START")]
            payload = successor["payload"]
            self.assertEqual(
                payload["receptor_receipt_digest"],
                recorded.receptor_receipt_digest,
            )
            self.assertEqual(payload["source_digest"], recorded.source.source_digest)
            self.assertEqual(
                successor["previous_event_digest"],
                result["event_digest"],
            )

    def test_06_verifier_accepts_valid_compact_receipts(self) -> None:
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, self.run_directory)
        self.assertEqual(finding.status, "RECORDING_COMPLETE")
        self.assertEqual(finding.errors, ())
        self.assertEqual((finding.operation_count, finding.event_count), (139, 278))

    def test_07_verifier_rejects_tampered_and_full_receipts(self) -> None:
        for suffix, field, value in (
            ("tampered", "unexpected_field", True),
            ("full", "envelope", {"auditory_stream": {"timed_frames": []}}),
        ):
            with tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary) / f"s2hb-{suffix}"
                shutil.copytree(self.run_directory, copied)
                target = copied / self.receptor_rows[0]["target_path"]
                artifact = json.loads(target.read_text(encoding="ascii"))
                artifact["artifact"]["result"][field] = value
                target.write_bytes(_canonical_bytes(artifact))
                finding = verifier.verify_run_read_only(WORKSPACE_ROOT, copied)
                self.assertEqual(finding.status, "NOT_EVALUABLE")

    def test_08_e008_is_forwarded_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan, registry = runner.materialize_execution_plan(
                WORKSPACE_ROOT,
                "s2hb-e008-forwarding",
                "s2gw-run-owner",
            )
            recorder = recording.AppendOnlyRunRecorder.reserve(
                Path(temporary), plan, registry
            )
            self.assertIs(type(recorder), recording.AppendOnlyRunRecorder)
            error = recording.S2GTRecordingError(
                "E008", "registered resource limit was exceeded"
            )
            self.assertEqual(runner._failure_code_for_exception(recorder, error), "E008")
            recorder.fail("E008", "op-0002")
            receipt = json.loads(
                (recorder.run_directory / "failure/run-failure.json").read_text(
                    encoding="ascii"
                )
            )
            self.assertEqual(receipt["error_code"], "E008")

    def test_09_phase_invalid_and_unclassified_errors_are_mapped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan, registry = runner.materialize_execution_plan(
                WORKSPACE_ROOT,
                "s2hb-error-mapping",
                "s2gw-run-owner",
            )
            recorder = recording.AppendOnlyRunRecorder.reserve(
                Path(temporary), plan, registry
            )
            self.assertIs(type(recorder), recording.AppendOnlyRunRecorder)
            recorder.state = "EVALUATING"
            phase_invalid = recording.S2GTRecordingError(
                "E006", "input source binding is invalid"
            )
            self.assertEqual(
                runner._failure_code_for_exception(recorder, phase_invalid), "E002"
            )
            self.assertEqual(
                runner._failure_code_for_exception(
                    recorder,
                    recording.S2GTRecordingError("E999", "unregistered"),
                ),
                "E009",
            )
            self.assertEqual(
                runner._failure_code_for_exception(recorder, RuntimeError("neutral")),
                "E009",
            )

    def test_10_main_gate_blocks_all_main_histories(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with mock.patch.object(runner, "_execute") as execute:
            with self.assertRaisesRegex(runner.S2GTRunnerError, "not authorized"):
                runner.run_main_once(
                    WORKSPACE_ROOT,
                    WORKSPACE_ROOT,
                    "s2hb-main-history-blocked",
                    "s2gw-run-owner",
                    runner.build_evaluation_plan_seal(),
                )
            execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
