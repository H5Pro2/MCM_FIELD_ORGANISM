from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_chain_composition import (
    compose_synthetic_e1_confirmation_chain,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    S1_EB4_REPORT_FIELDS,
)
from mcm_field_organism.e1_confirmation_synthetic_executor import (
    E1ConfirmationSyntheticExecutorError,
    execute_synthetic_e1_confirmation_once,
)
from tests.test_e1_confirmation_chain_composition import _chain_inputs


def _inputs():
    contract, formation, probes = _chain_inputs()

    def producer():
        return compose_synthetic_e1_confirmation_chain(
            contract,
            formation,
            probes,
        )

    return contract, producer


class E1ConfirmationSyntheticExecutorTests(unittest.TestCase):
    def test_synthetic_result_publishes_once_outside_project_targets(self) -> None:
        contract, producer = _inputs()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = execute_synthetic_e1_confirmation_once(
                contract,
                producer,
                root,
            )
            report = json.loads(
                Path(receipt.report_path).read_text(encoding="ascii")
            )

            self.assertEqual(S1_EB4_REPORT_FIELDS, tuple(report))
            self.assertEqual(
                "NUMERICALLY_UNDECIDABLE",
                receipt.technical_decision,
            )
            self.assertTrue(receipt.synthetic_only)
            self.assertFalse((root / (
                "e1_confirmation_s1eb8_synthetic_once_v1.attempt.json"
            )).exists())
            self.assertFalse((root / (
                "e1_confirmation_s1eb8_synthetic_once_v1.lock"
            )).exists())
            with self.assertRaisesRegex(
                E1ConfirmationSyntheticExecutorError,
                "already used",
            ):
                execute_synthetic_e1_confirmation_once(
                    contract,
                    producer,
                    root,
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        contract, _ = _inputs()
        with TemporaryDirectory() as directory:
            root = Path(directory)

            def fail():
                raise RuntimeError("synthetic started failure")

            with self.assertRaisesRegex(RuntimeError, "started failure"):
                execute_synthetic_e1_confirmation_once(contract, fail, root)
            attempt = root / (
                "e1_confirmation_s1eb8_synthetic_once_v1.attempt.json"
            )
            self.assertTrue(attempt.exists())
            self.assertFalse((root / (
                "e1_confirmation_s1eb8_synthetic_once_v1.lock"
            )).exists())
            with self.assertRaisesRegex(
                E1ConfirmationSyntheticExecutorError,
                "already used",
            ):
                execute_synthetic_e1_confirmation_once(contract, fail, root)

    def test_invalid_result_retains_attempt(self) -> None:
        contract, _ = _inputs()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1ConfirmationSyntheticExecutorError,
                "invalid result",
            ):
                execute_synthetic_e1_confirmation_once(
                    contract,
                    lambda: object(),
                    root,
                )
            self.assertTrue((root / (
                "e1_confirmation_s1eb8_synthetic_once_v1.attempt.json"
            )).exists())

    def test_noncallable_and_registered_target_fail_before_attempt(self) -> None:
        contract, producer = _inputs()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1ConfirmationSyntheticExecutorError,
                "not callable",
            ):
                execute_synthetic_e1_confirmation_once(contract, None, root)
            self.assertEqual((), tuple(root.iterdir()))
        with self.assertRaisesRegex(
            E1ConfirmationSyntheticExecutorError,
            "registered target directory",
        ):
            execute_synthetic_e1_confirmation_once(
                contract,
                producer,
                Path(contract.report_path).parent,
            )

    def test_registered_s1eb_paths_remain_free(self) -> None:
        contract, producer = _inputs()
        targets = tuple(Path(value) for value in contract._target_path_values())
        before = tuple(path.exists() for path in targets)
        with TemporaryDirectory() as directory:
            execute_synthetic_e1_confirmation_once(
                contract,
                producer,
                Path(directory),
            )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in targets))

    def test_executor_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationSyntheticReceipt",
            "execute_synthetic_e1_confirmation_once",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
