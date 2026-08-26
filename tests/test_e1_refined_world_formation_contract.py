from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_refined_world_formation_contract import (
    E1RefinedWorldFormationContractError,
    S1_DS_DECISIONS,
    S1_DS_DECISION_RULES,
    S1_DS_METRICS,
    S1_DS_REFINEMENTS,
    S1_DS_REQUIRED_CONTROLS,
    build_e1_refined_world_formation_contract,
)


REPORT = Path("reports/e1_frozen_state_transfer_s1dn_once_v1.json")


class E1RefinedWorldFormationContractTests(unittest.TestCase):
    def test_contract_binds_source_time_geometry_and_refinements(self) -> None:
        contract = build_e1_refined_world_formation_contract(REPORT)

        self.assertEqual((0, 1_000_000, 2_000_000), (
            contract.history_start_tick,
            contract.history_split_tick,
            contract.history_end_tick,
        ))
        self.assertEqual((200, 20, 220), (
            contract.auditory_frame_count,
            contract.visual_frame_count,
            contract.source_support_count,
        ))
        self.assertEqual((84, 145), (contract.field_node_count, contract.edge_count))
        self.assertEqual(S1_DS_REFINEMENTS, contract.refinements)

    def test_contract_binds_controls_metrics_and_decisions(self) -> None:
        contract = build_e1_refined_world_formation_contract(REPORT)

        self.assertEqual(S1_DS_METRICS, contract.metrics)
        self.assertEqual(S1_DS_REQUIRED_CONTROLS, contract.required_controls)
        self.assertEqual(S1_DS_DECISIONS, contract.decisions)
        self.assertEqual(S1_DS_DECISION_RULES, contract.decision_rules)
        self.assertEqual(8.0, contract.numerical_signal_margin)

    def test_contract_releases_implementation_only(self) -> None:
        contract = build_e1_refined_world_formation_contract(REPORT)

        self.assertTrue(contract.implementation_permitted)
        for role in (
            "execution_permitted",
            "old_history_rerun_permitted",
            "old_transfer_rerun_permitted",
            "memory_claim_permitted",
            "semantic_claim_permitted",
            "organization_claim_permitted",
            "topology_claim_permitted",
            "self_regulation_claim_permitted",
            "ai_claim_permitted",
        ):
            self.assertFalse(getattr(contract, role))

    def test_contract_digest_is_repeatable_and_changes_fail_closed(self) -> None:
        first = build_e1_refined_world_formation_contract(REPORT)
        second = build_e1_refined_world_formation_contract(REPORT)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))
        with self.assertRaises(E1RefinedWorldFormationContractError):
            replace(first, execution_permitted=True)
        with self.assertRaises(E1RefinedWorldFormationContractError):
            replace(first, numerical_signal_margin=1.0)

    def test_changed_upstream_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["technical_status"] = "CHANGED"
            path = Path(directory) / REPORT.name
            path.write_text(json.dumps(changed) + "\n", encoding="ascii")
            with self.assertRaises(ValueError):
                build_e1_refined_world_formation_contract(path)

    def test_builder_is_nonexecuting_and_private(self) -> None:
        source = inspect.getsource(build_e1_refined_world_formation_contract)
        for forbidden in (
            "run_e1_asynchronous_field",
            "produce_e1_a0_av_histories",
            "execute_e1_frozen_state_transfer_one_shot",
            "advance_e1_local_edge_plasticity",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1RefinedWorldFormationContract",
            "build_e1_refined_world_formation_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
