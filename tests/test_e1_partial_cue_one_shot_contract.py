from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_partial_cue_contract import (
    S1_CO_DECISIONS,
    build_e1_partial_cue_contract,
)
from mcm_field_organism.e1_partial_cue_one_shot_contract import (
    E1PartialCueOneShotContractError,
    S1_CR_RUNNER_INVENTORY_DIGEST,
    S1_CS_REPORT_FIELDS,
    prepare_e1_partial_cue_one_shot_contract,
)


class E1PartialCueOneShotContractTests(unittest.TestCase):
    def test_contract_binds_pristine_paths_digests_and_decisions(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_partial_cue_one_shot_contract(Path(directory))
            self.assertEqual("e1.partial-cue.s1ct.once.v1", contract.execution_id)
            self.assertEqual(build_e1_partial_cue_contract().digest(), contract.cue_contract_digest)
            self.assertEqual(S1_CR_RUNNER_INVENTORY_DIGEST, contract.runner_inventory_digest)
            self.assertEqual(S1_CS_REPORT_FIELDS, contract.report_fields)
            self.assertEqual(S1_CO_DECISIONS, contract.allowed_decisions)
            self.assertTrue(contract.execution_permitted)
            self.assertFalse(contract.execution_started)
            self.assertEqual(64, len(contract.digest()))

    def test_preparation_creates_no_file(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare_e1_partial_cue_one_shot_contract(root)
            self.assertEqual((), tuple(root.iterdir()))

    def test_any_used_path_blocks_preparation(self) -> None:
        for name in (
            "e1_partial_cue_s1ct_once_v1.json",
            "e1_partial_cue_s1ct_once_v1.attempt.json",
            "e1_partial_cue_s1ct_once_v1.lock",
        ):
            with self.subTest(name=name), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / name).write_text("used\n", encoding="ascii")
                with self.assertRaisesRegex(E1PartialCueOneShotContractError, "already used"):
                    prepare_e1_partial_cue_one_shot_contract(root)

    def test_contract_digest_is_deterministic_and_path_bound(self) -> None:
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            a = prepare_e1_partial_cue_one_shot_contract(Path(first))
            b = prepare_e1_partial_cue_one_shot_contract(Path(first))
            c = prepare_e1_partial_cue_one_shot_contract(Path(second))
            self.assertEqual(a.digest(), b.digest())
            self.assertNotEqual(a.digest(), c.digest())

    def test_changed_inventory_or_permission_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_partial_cue_one_shot_contract(Path(directory))
            with self.assertRaises(E1PartialCueOneShotContractError):
                replace(contract, runner_inventory_digest="0" * 64)
            with self.assertRaises(E1PartialCueOneShotContractError):
                replace(contract, execution_started=True)

    def test_preparation_has_no_execution_references(self) -> None:
        source = inspect.getsource(prepare_e1_partial_cue_one_shot_contract)
        self.assertNotIn("build_e1_partial_cue_runner_inventory", source)
        self.assertNotIn("compose_e1_partial_cue_result", source)
        self.assertNotIn("evaluate_e1_partial_cue_result", source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1PartialCueOneShotContract",
            "prepare_e1_partial_cue_one_shot_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
