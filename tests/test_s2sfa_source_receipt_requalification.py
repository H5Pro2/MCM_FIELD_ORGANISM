from __future__ import annotations

from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

import numpy as np

from mcm_field_organism.finite_video_path import VisualGridConfig, VisualReceptorContact, VisualReceptorState
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
        x = 160 + ((spec.ordinal - 1) % 4) * 320
        frame[405:675, x:x + 320, :] = (
            64 + (spec.ordinal * 7) % 128,
            96 + (spec.ordinal * 11) % 128,
            128 + (spec.ordinal * 13) % 96,
        )
        yield run.SourceFrame(
            frame_id=spec.frame_id,
            source_id=f"neutral-source-{spec.ordinal:02d}",
            recipe_digest=run._digest({"fixture": "source-receipt-requalification", "ordinal": spec.ordinal}),
            sequence_position=spec.ordinal,
            frame_index=spec.ordinal,
            frame=frame,
        )


class OrderedReceptor:
    def __init__(self) -> None:
        self.config = VisualGridConfig()
        self.values = tuple(index / 287.0 for index in range(288))

    def analyze(self, frame: np.ndarray, *, frame_index: int) -> VisualReceptorState:
        return VisualReceptorState(
            modality_id="visual",
            geometry_id=self.config.geometry_id,
            frame_index=frame_index,
            carrier_ids=self.config.carrier_ids,
            channel_values=self.values,
            contact=VisualReceptorContact.ACTIVE_LIGHT,
        )


class SFASourceReceiptRequalificationTests(unittest.TestCase):
    def test_channel_values_preserve_all_288_values_in_order(self) -> None:
        source = next(neutral_sources())
        receptor = OrderedReceptor()
        observations, receipts = run.observe_sources_once((source,), receptor=receptor)
        self.assertEqual(observations[source.frame_id], receptor.values)
        self.assertEqual(receipts[0].observation_digest, run._digest(list(receptor.values)))

    def test_success_path_reaches_record_verification_and_evaluation(self) -> None:
        observations, receipts = run.observe_sources_once(neutral_sources())
        record = run.run_materialized_once(
            run_id="source-receipt-requalified",
            plan_digest=run.PLAN_DIGEST,
            observations=observations,
            authorized=True,
            source_receipts=receipts,
            ledger=ledger(),
            error_reserve_bytes=512 * 1024,
        )
        self.assertEqual(record["status"], "RECORDING_COMPLETE")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.json"
            run.publish_record_once(record, output, ledger=ledger(), error_reserve_bytes=512 * 1024)
            self.assertTrue(output.is_file())
        verification = run.verify_read_only(record, ledger=ledger(), error_reserve_bytes=512 * 1024)
        evaluation = run.evaluate_verified(record, verification, ledger=ledger(), error_reserve_bytes=512 * 1024)
        self.assertTrue(verification["evaluation_allowed"])
        self.assertIn("additional_correct", evaluation)

    def test_missing_or_manipulated_receipts_stop_before_numerical_run(self) -> None:
        observations, receipts = run.observe_sources_once(neutral_sources())
        with self.assertRaisesRegex(run.SFAVisualRunError, "requires source receipts") as missing:
            run.run_materialized_once(
                run_id="missing-receipts-requalified",
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
                run_id="altered-receipts-requalified",
                plan_digest=run.PLAN_DIGEST,
                observations=observations,
                authorized=True,
                source_receipts=altered,
                ledger=ledger(),
                error_reserve_bytes=512 * 1024,
            )
        self.assertEqual(manipulated.exception.code, "SOURCE_BINDING_INVALID")


if __name__ == "__main__":
    unittest.main()
