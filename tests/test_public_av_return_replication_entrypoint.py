from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_replication_entrypoint import (
    PublicAVReturnReplicationEntrypoint,
    PublicAVReturnReplicationEntrypointError,
    public_av_return_replication_entrypoint_public_roles,
)
from mcm_field_organism.public_av_return_replication_preflight import (
    audit_public_av_return_replication_preflight,
)
from mcm_field_organism.public_av_return_replication_runner import (
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class PublicAVReturnReplicationEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = nasa_earthrise_av_source_contract()
        cls.source_audit = audit_public_media_source(MEDIA, cls.contract)
        cls.wiring = wire_public_av_return_replication_runner()
        cls.preflight = audit_public_av_return_replication_preflight(
            MEDIA, cls.contract, source_audit=cls.source_audit, wiring=cls.wiring,
        )

    def test_positive_preflight_invokes_executor_exactly_once(self) -> None:
        calls = []
        gate = PublicAVReturnReplicationEntrypoint(lambda path, contract, wiring: calls.append((path, contract, wiring)) or "result")
        result, receipt = gate.start_once(MEDIA, self.contract, self.wiring, self.preflight)
        self.assertEqual("result", result)
        self.assertEqual(1, len(calls))
        self.assertTrue(gate.consumed)
        self.assertTrue(receipt.execution_completed)

    def test_second_start_is_rejected_without_second_executor_call(self) -> None:
        calls = []
        gate = PublicAVReturnReplicationEntrypoint(lambda *_: calls.append(True))
        gate.start_once(MEDIA, self.contract, self.wiring, self.preflight)
        with self.assertRaisesRegex(PublicAVReturnReplicationEntrypointError, "already consumed"):
            gate.start_once(MEDIA, self.contract, self.wiring, self.preflight)
        self.assertEqual(1, len(calls))

    def test_failed_executor_still_consumes_release(self) -> None:
        def fail(*_):
            raise RuntimeError("executor failure")
        gate = PublicAVReturnReplicationEntrypoint(fail)
        with self.assertRaisesRegex(RuntimeError, "executor failure"):
            gate.start_once(MEDIA, self.contract, self.wiring, self.preflight)
        self.assertTrue(gate.consumed)

    def test_changed_path_or_preflight_blocks_before_executor(self) -> None:
        calls = []
        gate = PublicAVReturnReplicationEntrypoint(lambda *_: calls.append(True))
        with self.assertRaisesRegex(PublicAVReturnReplicationEntrypointError, "path differs"):
            gate.start_once(Path("different.mp4"), self.contract, self.wiring, self.preflight)
        blocked = replace(self.preflight, single_bounded_replication_run_release_granted=False, source_audit_accepted=False)
        with self.assertRaisesRegex(PublicAVReturnReplicationEntrypointError, "not released"):
            gate.start_once(MEDIA, self.contract, self.wiring, blocked)
        self.assertEqual([], calls)

    def test_public_receipt_roles_exclude_claim_scores_and_payloads(self) -> None:
        forbidden = {"samples", "pixels", "memory_score", "organization_score", "field_state", "reward", "label"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_entrypoint_public_roles()))


if __name__ == "__main__":
    unittest.main()
