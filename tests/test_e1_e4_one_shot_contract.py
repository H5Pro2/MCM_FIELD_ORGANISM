from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_e4_execution import E1_E4_EXECUTION_CONTRACT_DIGEST
from mcm_field_organism.e1_e4_one_shot_contract import (
    E1_E4_ONE_SHOT_DECISIONS,
    E1_E4_ONE_SHOT_REPORT_FIELDS,
    E1_E4_RUNNER_INVENTORY_DIGEST,
    E1E4OneShotContract,
    E1E4OneShotContractError,
    prepare_e1_e4_one_shot_contract,
)


class E1E4OneShotContractTests(unittest.TestCase):
    def test_contract_binds_pristine_sibling_paths_and_digests(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_e4_one_shot_contract(Path(directory))

            self.assertEqual("e1.e4.s1cn.once.v1", contract.execution_id)
            self.assertEqual(E1_E4_RUNNER_INVENTORY_DIGEST, contract.runner_inventory_digest)
            self.assertEqual(E1_E4_EXECUTION_CONTRACT_DIGEST, contract.execution_contract_digest)
            self.assertEqual(E1_E4_ONE_SHOT_REPORT_FIELDS, contract.report_fields)
            self.assertEqual(E1_E4_ONE_SHOT_DECISIONS, contract.allowed_decisions)
            self.assertTrue(contract.execution_permitted)
            self.assertFalse(contract.execution_started)
            self.assertEqual(64, len(contract.digest()))
            self.assertEqual(
                1,
                len(
                    {
                        Path(contract.report_path).parent,
                        Path(contract.attempt_path).parent,
                        Path(contract.lock_path).parent,
                    }
                ),
            )

    def test_preparation_has_no_filesystem_side_effect(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_e4_one_shot_contract(root)

            self.assertEqual((), tuple(root.iterdir()))
            self.assertFalse(Path(contract.report_path).exists())

    def test_any_used_one_shot_path_blocks_preparation(self) -> None:
        for name in (
            "e1_e4_s1cn_once_v1.json",
            "e1_e4_s1cn_once_v1.attempt.json",
            "e1_e4_s1cn_once_v1.lock",
        ):
            with self.subTest(name=name), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / name).write_text("used\n", encoding="ascii")
                with self.assertRaisesRegex(E1E4OneShotContractError, "already used"):
                    prepare_e1_e4_one_shot_contract(root)

    def test_contract_digest_is_deterministic_and_path_bound(self) -> None:
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            first_contract = prepare_e1_e4_one_shot_contract(Path(first))
            repeated = prepare_e1_e4_one_shot_contract(Path(first))
            second_contract = prepare_e1_e4_one_shot_contract(Path(second))

            self.assertEqual(first_contract.digest(), repeated.digest())
            self.assertNotEqual(first_contract.digest(), second_contract.digest())

    def test_changed_inventory_digest_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            original = prepare_e1_e4_one_shot_contract(Path(directory))
            values = {
                name: getattr(original, name)
                for name in original.__dataclass_fields__
            }
            values["runner_inventory_digest"] = "0" * 64
            with self.assertRaisesRegex(E1E4OneShotContractError, "inventory"):
                E1E4OneShotContract(**values)

    def test_static_preparation_does_not_reference_execution_functions(self) -> None:
        source = inspect.getsource(prepare_e1_e4_one_shot_contract)
        self.assertNotIn("build_e1_e4_runner_inventory", source)
        self.assertNotIn("compose_e1_e4_run_result", source)
        self.assertNotIn("evaluate_e1_e4_run", source)

    def test_module_remains_private(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "E1E4OneShotContract"))
        self.assertFalse(hasattr(current_api, "E1E4OneShotContract"))


if __name__ == "__main__":
    unittest.main()
