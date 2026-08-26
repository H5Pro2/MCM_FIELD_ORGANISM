from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_executor_adapter import (
    E1CanonicalRefinedChainExecutorAdapterError,
    execute_e1_canonical_refined_chain_one_shot,
    execute_mirrored_e1_canonical_refined_chain_one_shot,
    prepare_e1_canonical_executor_adapter,
)
from mcm_field_organism.e1_refined_chain_one_shot_contract import (
    prepare_e1_refined_chain_one_shot_contract,
)
from tests.test_e1_refined_chain_one_shot_execution import synthetic_result
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1CanonicalRefinedChainExecutorAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM, TARGETS
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()
        TARGETS = tuple(REPORTS / path.name for path in TARGETS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_mirror_publishes_canonical_report_shape_once(self) -> None:
        adapter = prepare_e1_canonical_executor_adapter(REPORTS, UPSTREAM)
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = execute_mirrored_e1_canonical_refined_chain_one_shot(
                adapter, contract, synthetic_result, root
            )
            report = json.loads(Path(receipt.report_path).read_text(encoding="ascii"))

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertTrue(receipt.mirror_only)
            self.assertFalse((root / adapter.attempt_name).exists())
            self.assertFalse((root / adapter.lock_name).exists())
            with self.assertRaisesRegex(
                E1CanonicalRefinedChainExecutorAdapterError, "already used"
            ):
                execute_mirrored_e1_canonical_refined_chain_one_shot(
                    adapter, contract, synthetic_result, root
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        adapter = prepare_e1_canonical_executor_adapter(REPORTS, UPSTREAM)
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            def fail():
                raise RuntimeError("mirror started failure")

            with self.assertRaisesRegex(RuntimeError, "started failure"):
                execute_mirrored_e1_canonical_refined_chain_one_shot(
                    adapter, contract, fail, root
                )
            self.assertTrue((root / adapter.attempt_name).exists())
            self.assertFalse((root / adapter.lock_name).exists())
            with self.assertRaisesRegex(
                E1CanonicalRefinedChainExecutorAdapterError, "already used"
            ):
                execute_mirrored_e1_canonical_refined_chain_one_shot(
                    adapter, contract, synthetic_result, root
                )

    def test_invalid_prestart_inputs_create_no_marker(self) -> None:
        adapter = prepare_e1_canonical_executor_adapter(REPORTS, UPSTREAM)
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(E1CanonicalRefinedChainExecutorAdapterError):
                execute_mirrored_e1_canonical_refined_chain_one_shot(
                    adapter, contract, None, root
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_canonical_entrypoint_remains_locked(self) -> None:
        adapter = prepare_e1_canonical_executor_adapter(REPORTS, UPSTREAM)
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with self.assertRaisesRegex(
            E1CanonicalRefinedChainExecutorAdapterError, "remains locked"
        ):
            execute_e1_canonical_refined_chain_one_shot(
                adapter, contract, synthetic_result
            )

    def test_project_paths_remain_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        prepare_e1_canonical_executor_adapter(REPORTS, UPSTREAM)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1CanonicalExecutorAdapterBinding",
            "execute_mirrored_e1_canonical_refined_chain_one_shot",
            "execute_e1_canonical_refined_chain_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
