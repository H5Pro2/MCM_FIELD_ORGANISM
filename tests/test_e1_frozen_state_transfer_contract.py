from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    E1FrozenStateTransferContractError,
    S1_DK_ARMS,
    S1_DK_B_AB_DIGEST,
    S1_DK_B_BA_DIGEST,
    S1_DK_DECISIONS,
    S1_DK_METRICS,
    S1_DK_PROBE_DIGEST,
    build_e1_frozen_state_transfer_contract,
)


REPORT = Path("reports/e1_a0_av_history_s1di_once_v1.json")


class E1FrozenStateTransferContractTests(unittest.TestCase):
    def test_published_states_are_bound_to_the_narrow_transfer_contract(self) -> None:
        contract = build_e1_frozen_state_transfer_contract(REPORT)

        self.assertEqual(
            "FULL_S1_DC_BLOCKED_NARROW_STATE_TRANSFER_ONLY",
            contract.evidence_decision,
        )
        self.assertEqual(S1_DK_B_AB_DIGEST, contract.b_ab_digest)
        self.assertEqual(S1_DK_B_BA_DIGEST, contract.b_ba_digest)
        self.assertEqual(S1_DK_PROBE_DIGEST, contract.probe_digest)
        self.assertEqual((100, 10, 110), (
            contract.auditory_frame_count,
            contract.visual_frame_count,
            contract.source_support_count,
        ))
        self.assertEqual((84, 145), (contract.field_node_count, contract.edge_count))
        self.assertEqual(S1_DK_ARMS, contract.arms)
        self.assertEqual(S1_DK_METRICS, contract.metrics)
        self.assertEqual(S1_DK_DECISIONS, contract.decisions)
        self.assertTrue(contract.implementation_permitted)
        self.assertFalse(contract.probe_execution_permitted)
        self.assertFalse(contract.full_s1_dc_decision_permitted)

    def test_contract_digest_is_deterministic(self) -> None:
        first = build_e1_frozen_state_transfer_contract(REPORT)
        second = build_e1_frozen_state_transfer_contract(REPORT)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_execution_and_strong_claims_fail_closed(self) -> None:
        contract = build_e1_frozen_state_transfer_contract(REPORT)

        for change in (
            {"probe_execution_permitted": True},
            {"full_s1_dc_decision_permitted": True},
            {"history_cause_claim_permitted": True},
            {"memory_claim_permitted": True},
            {"ai_claim_permitted": True},
        ):
            with self.assertRaisesRegex(
                E1FrozenStateTransferContractError,
                "cannot release",
            ):
                replace(contract, **change)

    def test_changed_or_missing_history_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(Exception, "missing"):
                build_e1_frozen_state_transfer_contract(root / "missing.json")

            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["d_state"] = 0.0
            changed_path = root / "changed.json"
            changed_path.write_text(
                json.dumps(changed, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(Exception, "report digest"):
                build_e1_frozen_state_transfer_contract(changed_path)

    def test_builder_has_no_field_history_or_probe_execution_reference(self) -> None:
        source = inspect.getsource(build_e1_frozen_state_transfer_contract)
        for forbidden in (
            "produce_e1_a0_av_histories",
            "run_e1_asynchronous_field",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_fixed_e1_adapter_fast_shared_field_transient",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1FrozenStateTransferContract",
            "build_e1_frozen_state_transfer_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
