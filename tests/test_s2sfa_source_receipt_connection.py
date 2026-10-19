from __future__ import annotations

from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools import _s2sfa_private_visual_run as run


def ledger() -> tuple[run.LedgerEntry, ...]:
    return (
        run.LedgerEntry("references", 512 * 1024),
        run.LedgerEntry("qualification", 512 * 1024),
        run.LedgerEntry("verification", 256 * 1024),
        run.LedgerEntry("evaluation", 128 * 1024),
    )


def neutral_sources() -> object:
    for spec in run.PLAN:
        frame = np.empty((1080, 1920, 3), dtype=np.uint8)
        frame[:, :, :] = (16 + spec.ordinal % 32, 40 + (spec.ordinal * 3) % 48, 72 + (spec.ordinal * 5) % 80)
        frame[405:675, 160 + ((spec.ordinal - 1) % 4) * 320:480 + ((spec.ordinal - 1) % 4) * 320, :] = (
            64 + (spec.ordinal * 7) % 128,
            96 + (spec.ordinal * 11) % 128,
            128 + (spec.ordinal * 13) % 96,
        )
        yield run.SourceFrame(
            frame_id=spec.frame_id,
            source_id=f"neutral-source-{spec.ordinal:02d}",
            recipe_digest=run._digest({"fixture": "source-receipt", "ordinal": spec.ordinal}),
            sequence_position=spec.ordinal,
            frame_index=spec.ordinal,
            frame=frame,
        )


class FailingReceptor:
    def analyze(self, frame: np.ndarray, *, frame_index: int) -> object:
        raise RuntimeError(f"neutral failure after hash at {frame_index}")


class SFASourceReceiptConnectionTests(unittest.TestCase):
    def test_neutral_source_to_record_verification_and_evaluation(self) -> None:
        observations, receipts = run.observe_sources_once(neutral_sources())
        record = run.run_materialized_once(
            run_id="source-receipt-neutral",
            plan_digest=run.PLAN_DIGEST,
            observations=observations,
            authorized=True,
            source_receipts=receipts,
            ledger=ledger(),
            error_reserve_bytes=512 * 1024,
        )
        self.assertEqual(record["status"], "RECORDING_COMPLETE")
        self.assertEqual(len(record["source_receipts"]), 32)
        self.assertTrue(all(item["status"] == "ANALYZED" for item in record["source_receipts"]))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.json"
            run.publish_record_once(record, output, ledger=ledger(), error_reserve_bytes=512 * 1024)
            self.assertTrue(output.is_file())
        verification = run.verify_read_only(record, ledger=ledger(), error_reserve_bytes=512 * 1024)
        evaluation = run.evaluate_verified(record, verification, ledger=ledger(), error_reserve_bytes=512 * 1024)
        self.assertTrue(verification["evaluation_allowed"])
        self.assertIn("losses", evaluation)

    def test_missing_or_manipulated_receipts_stop_before_numerical_run(self) -> None:
        observations, receipts = run.observe_sources_once(neutral_sources())
        with self.assertRaisesRegex(run.SFAVisualRunError, "requires source receipts") as missing:
            run.run_materialized_once(
                run_id="missing-receipts",
                plan_digest=run.PLAN_DIGEST,
                observations=observations,
                authorized=True,
                source_receipts=None,
                ledger=ledger(),
                error_reserve_bytes=512 * 1024,
            )
        self.assertEqual(missing.exception.code, "SOURCE_RECEIPTS_REQUIRED")
        altered = (replace(receipts[0], observation_digest="0" * 64), *receipts[1:])
        with self.assertRaisesRegex(run.SFAVisualRunError, "does not bind its observation") as manipulated:
            run.run_materialized_once(
                run_id="altered-receipts",
                plan_digest=run.PLAN_DIGEST,
                observations=observations,
                authorized=True,
                source_receipts=altered,
                ledger=ledger(),
                error_reserve_bytes=512 * 1024,
            )
        self.assertEqual(manipulated.exception.code, "SOURCE_BINDING_INVALID")

    def test_failure_after_hash_retains_only_hashed_receipt(self) -> None:
        source = next(neutral_sources())
        with self.assertRaises(run.SFAVisualSourceError) as caught:
            run.observe_sources_once((source,), receptor=FailingReceptor())
        error = caught.exception
        self.assertEqual(error.progress, 0)
        self.assertEqual(error.receipts[0].status, "HASHED_NOT_ANALYZED")
        record = run._source_failure_record(
            run_id="source-receipt-failure",
            plan_digest=run.PLAN_DIGEST,
            source_error=error,
            ledger=ledger(),
            error_reserve_bytes=512 * 1024,
        )
        verification = run.verify_read_only(record, ledger=ledger(), error_reserve_bytes=512 * 1024)
        self.assertEqual(record["status"], "INCOMPLETE")
        self.assertEqual(verification["status"], "INCOMPLETE_ACCEPTED")


if __name__ == "__main__":
    unittest.main()
