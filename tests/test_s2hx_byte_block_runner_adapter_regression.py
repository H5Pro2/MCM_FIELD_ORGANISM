"""Focused one-shot regression for the S2-HU byte-block adapter."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2hq_private_byte_block_conflict_fixture as byte_fixture
from tools import _s2hu_private_append_only_recorder as recording
from tools import _s2hu_private_fixture_registry as fixtures
from tools import _s2hu_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2hx-byte-block-adapter-20260831-01"


def _advance_neutral_prefix(
    output_root: Path,
    run_id: str,
) -> recording.AppendOnlyRunRecorder:
    plan, registry = runner.materialize_execution_plan(
        WORKSPACE_ROOT,
        run_id,
        f"{run_id}-owner",
    )
    reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
    if type(reserved) is recording.StartBlocked:
        raise AssertionError("focused adapter path could not reserve its run")
    recorder = reserved
    for expected_index in (2, 3, 4):
        row = recorder.current_row()
        if row.index != expected_index:
            raise AssertionError("neutral prefix operation differs")
        recorder.start(
            row.operation_id,
            {"qualification_id": QUALIFICATION_ID, "neutral_prefix": expected_index},
        )
        if expected_index == 2:
            result: dict[str, object] = {
                "execution_plan": plan.payload(),
                "registry_source_digest": registry.source_digest,
                "registry_bundle_digest": registry.bundle_digest,
                "execution_fixture_digest": fixtures.EXECUTION_FIXTURE_DIGEST,
            }
        else:
            result = {
                "schema": "s2hx.neutral-prefix.v1",
                "qualification_id": QUALIFICATION_ID,
                "operation_index": expected_index,
            }
        recorder.finish(row.operation_id, {"result": result})
    return recorder


class S2HXByteBlockRunnerAdapterRegression(unittest.TestCase):
    def test_real_q0_q1_runner_adapter_reaches_hs_op_005(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory(prefix="s2hx-") as temporary:
            output_root = Path(temporary).resolve()
            for ordinal, visual_id in enumerate(("q0", "q1"), 1):
                with self.subTest(visual_id=visual_id):
                    recorder = _advance_neutral_prefix(
                        output_root,
                        f"s2hx-{visual_id}-adapter-01",
                    )
                    row = recorder.current_row()
                    self.assertEqual((5, "hs-op-005"), (row.index, row.operation_id))
                    fixture = byte_fixture.VISUAL_BY_ID[visual_id]
                    expected = fixture.receptor_values
                    self.assertIs(type(expected), tuple)
                    self.assertEqual(18, len(expected))
                    self.assertTrue(all(type(value) is float for value in expected))

                    recorder.start(
                        row.operation_id,
                        {
                            "qualification_id": QUALIFICATION_ID,
                            "visual_fixture_id": visual_id,
                        },
                    )
                    runtime = runner._runtime()
                    source = runner._analyze(
                        runtime,
                        "s2hu.h0.formation.01",
                        visual_id,
                        "mq",
                        0,
                        1,
                        "FORMATION",
                    )
                    self.assertIs(type(source.bound), coordinator.B4TSPM1BoundInput)
                    self.assertEqual(expected, source.bound.visual_values)
                    self.assertEqual(expected, source.bound.av_values[8:])
                    receipt = runner._receptor_receipt(source)
                    self.assertEqual(
                        fixtures.canonical_digest(list(expected)),
                        receipt["visual_values_digest"],
                    )
                    self.assertEqual(source.bound.input_digest, receipt["bound_digest"])
                    self.assertEqual(fixture.raw_sha256, receipt["raw_image_sha256"])
                    recorder.finish(row.operation_id, {"result": receipt})
                    self.assertEqual(6, recorder.next_operation_index)
                    self.assertEqual(10, recorder.event_count)
                    self.assertFalse(
                        (recorder.run_directory / "receipts/hs-op-006.json").exists()
                    )
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


if __name__ == "__main__":
    unittest.main()
