from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vq_corrected_matrix import S1VQMatrixResult
from mcm_field_organism._ppb1_s1vt_result_pipeline import (
    compose_s1vt_arm_records,
    evaluate_s1vt_composition,
    seal_s1vt_matrix_result,
)
import mcm_field_organism._ppb1_s1vw_synthetic_one_shot_handoff as s1vw
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot

from tests.test_ppb1_s1vt_result_pipeline import constructed_receipts


class PPB1S1VWSyntheticOneShotHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipts = constructed_receipts()
        cls.matrix = seal_s1vt_matrix_result(cls.receipts)
        cls.composition = compose_s1vt_arm_records(cls.matrix)
        cls.evaluation = evaluate_s1vt_composition(cls.composition)
        cls.legacy = S1VQMatrixResult(
            s1vw.S1VW_CORRECTED_PLAN_DIGEST,
            cls.receipts,
            s1vw.S1VW_EXPECTED_CALL_COUNT,
            tuple(
                (receipt.path.path_id, receipt.repeat_comparison_digest())
                for receipt in cls.receipts
                if receipt.path.repeat_id == "R1"
            ),
        )

    def synthetic_root(self, temporary: str) -> Path:
        root = Path(temporary) / "s1vw-synthetic-artifacts"
        root.mkdir()
        return root

    def test_h0_to_h7_success_is_atomic_and_complete(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            token = s1vw.S1VWSyntheticAuthorizationToken(
                "s1vw.synthetic.success"
            )
            calls = []

            outcome = s1vw.run_s1vw_synthetic_once(
                token, lambda: calls.append("producer") or self.legacy, root
            )

            self.assertIsInstance(outcome, s1vw.S1VWSuccessOutcome)
            self.assertEqual(["producer"], calls)
            self.assertTrue(token.consumed)
            self.assertEqual(528, len(outcome.matrix_result.receipts))
            self.assertEqual(48, len(outcome.composition_result.arms))
            self.assertEqual(
                outcome.terminal_digest,
                outcome.canonical_payload()["terminal_digest"],
            )
            paths = tuple(root.iterdir())
            self.assertEqual(2, len(paths))
            self.assertTrue(any(path.name.endswith(".lock.json") for path in paths))
            success = next(
                path for path in paths if path.name.endswith(".success.json")
            )
            payload = json.loads(success.read_text(encoding="utf-8"))
            self.assertEqual("SUCCESS", payload["status"])
            self.assertEqual(outcome.terminal_digest, payload["terminal_digest"])
            self.assertFalse(any(path.suffix == ".tmp" for path in paths))

    def test_durable_lock_rejects_retry_before_producer(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            execution_id = "s1vw.synthetic.no-retry"
            first = s1vw.S1VWSyntheticAuthorizationToken(execution_id)
            s1vw.run_s1vw_synthetic_once(first, lambda: self.legacy, root)
            calls = []
            second = s1vw.S1VWSyntheticAuthorizationToken(execution_id)

            with self.assertRaises(s1vw.S1VWOrchestratorError):
                s1vw.run_s1vw_synthetic_once(
                    second, lambda: calls.append("called") or self.legacy, root
                )

            self.assertEqual([], calls)
            self.assertFalse(second.consumed)

    def test_consumed_token_cannot_be_reused(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            token = s1vw.S1VWSyntheticAuthorizationToken(
                "s1vw.synthetic.consumed"
            )
            s1vw.run_s1vw_synthetic_once(token, lambda: self.legacy, root)
            with self.assertRaises(s1vw.S1VWOrchestratorError) as raised:
                s1vw.run_s1vw_synthetic_once(token, lambda: self.legacy, root)
            self.assertEqual(
                s1vw.S1VW_INVALID_SYNTHETIC_INPUT, raised.exception.code
            )

    def test_h2_producer_failure_seals_only_error(self) -> None:
        def failed_producer():
            raise RuntimeError("synthetic producer failure")

        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            token = s1vw.S1VWSyntheticAuthorizationToken(
                "s1vw.synthetic.h2-stage"
            )
            outcome = s1vw.run_s1vw_synthetic_once(token, failed_producer, root)
            self.assert_error(root, outcome, "H2", "PRODUCER_FAILED", "H1")

    def test_h3_rejects_incomplete_legacy_result(self) -> None:
        incomplete = S1VQMatrixResult(
            s1vw.S1VW_CORRECTED_PLAN_DIGEST, (), 0, ()
        )
        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            outcome = s1vw.run_s1vw_synthetic_once(
                s1vw.S1VWSyntheticAuthorizationToken(
                    "s1vw.synthetic.h3-stage"
                ),
                lambda: incomplete,
                root,
            )
            self.assert_error(root, outcome, "H3", "LEGACY_RESULT_INVALID", "H2")

    def test_h4_h5_and_h6_are_distinct_fail_closed_boundaries(self) -> None:
        failures = (
            (
                "h4",
                {
                    "seal_adapter": lambda receipts: (
                        _ for _ in ()
                    ).throw(RuntimeError())
                },
                "H4",
                "S1VT_SEAL_FAILED",
                "H3",
            ),
            (
                "h5",
                {
                    "seal_adapter": lambda receipts: self.matrix,
                    "compose_adapter": lambda matrix: (
                        _ for _ in ()
                    ).throw(RuntimeError()),
                },
                "H5",
                "S1VT_COMPOSITION_FAILED",
                "H4",
            ),
            (
                "h6",
                {
                    "seal_adapter": lambda receipts: self.matrix,
                    "compose_adapter": lambda matrix: self.composition,
                    "evaluate_adapter": lambda composition: (
                        _ for _ in ()
                    ).throw(RuntimeError()),
                },
                "H6",
                "S1VT_EVALUATION_FAILED",
                "H5",
            ),
        )
        for suffix, adapters, stage, code, completed in failures:
            with self.subTest(stage=stage), TemporaryDirectory() as temporary:
                root = self.synthetic_root(temporary)
                outcome = s1vw.run_s1vw_synthetic_once(
                    s1vw.S1VWSyntheticAuthorizationToken(
                        f"s1vw.synthetic.{suffix}-stage"
                    ),
                    lambda: self.legacy,
                    root,
                    **adapters,
                )
                self.assert_error(root, outcome, stage, code, completed)

    def test_h7_publication_failure_never_exposes_partial_result(self) -> None:
        def failed_publisher(target, temporary, counterpart, payload):
            raise OSError("synthetic publication failure")

        with TemporaryDirectory() as temporary:
            root = self.synthetic_root(temporary)
            outcome = s1vw.run_s1vw_synthetic_once(
                s1vw.S1VWSyntheticAuthorizationToken("s1vw.synthetic.h7-stage"),
                lambda: self.legacy,
                root,
                seal_adapter=lambda receipts: self.matrix,
                compose_adapter=lambda matrix: self.composition,
                evaluate_adapter=lambda composition: self.evaluation,
                publisher=failed_publisher,
            )
            self.assertIsInstance(outcome, s1vw.S1VWErrorOutcome)
            self.assertEqual("H7", outcome.error_stage)
            self.assertEqual("TERMINAL_PUBLICATION_FAILED", outcome.error_code)
            self.assertFalse(outcome.partial_result_exposed)
            self.assertEqual(1, len(tuple(root.iterdir())))
            self.assertTrue(next(root.iterdir()).name.endswith(".lock.json"))

    def test_non_test_artifact_root_is_rejected_before_consumption(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "wrong-root"
            root.mkdir()
            token = s1vw.S1VWSyntheticAuthorizationToken(
                "s1vw.synthetic.wrong-root"
            )
            calls = []
            with self.assertRaises(s1vw.S1VWOrchestratorError):
                s1vw.run_s1vw_synthetic_once(
                    token, lambda: calls.append(True) or self.legacy, root
                )
            self.assertFalse(token.consumed)
            self.assertEqual([], calls)
            self.assertEqual([], list(root.iterdir()))

        with TemporaryDirectory(dir=Path.cwd()) as local_temporary:
            root = Path(local_temporary) / "s1vw-synthetic-artifacts"
            root.mkdir()
            token = s1vw.S1VWSyntheticAuthorizationToken(
                "s1vw.synthetic.local-root"
            )
            with self.assertRaises(s1vw.S1VWOrchestratorError):
                s1vw.run_s1vw_synthetic_once(
                    token, lambda: self.legacy, root
                )
            self.assertFalse(token.consumed)

    def test_production_entrypoint_is_unconditionally_blocked(self) -> None:
        with self.assertRaises(s1vw.S1VWOrchestratorError) as raised:
            s1vw.execute_s1vw_production_once()
        self.assertEqual(
            s1vw.S1VW_PRODUCTION_EXECUTION_BLOCKED, raised.exception.code
        )

    def test_s1vw_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1VWSyntheticAuthorizationToken",
            "S1VWSuccessOutcome",
            "S1VWErrorOutcome",
            "run_s1vw_synthetic_once",
            "execute_s1vw_production_once",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertFalse(
            any(name.startswith("s1vw") for name in SharedMCMFieldSnapshot.__slots__)
        )

    def test_orchestrator_has_no_real_matrix_body_or_time_dependency(self) -> None:
        source = inspect.getsource(s1vw)
        forbidden = (
            "_execute_s1vq_corrected_matrix",
            "execute_s1vq_corrected_matrix",
            "SharedMCMField",
            "ReceptorContactFrame",
            "datetime",
            "time.time",
            "system_time",
        )
        for value in forbidden:
            self.assertNotIn(value, source)

    def assert_error(self, root, outcome, stage, code, completed) -> None:
        self.assertIsInstance(outcome, s1vw.S1VWErrorOutcome)
        self.assertEqual(stage, outcome.error_stage)
        self.assertEqual(code, outcome.error_code)
        self.assertEqual(completed, outcome.last_completed_stage)
        self.assertFalse(outcome.partial_result_exposed)
        paths = tuple(root.iterdir())
        self.assertEqual(2, len(paths))
        self.assertFalse(any(path.name.endswith(".success.json") for path in paths))
        error = next(path for path in paths if path.name.endswith(".error.json"))
        payload = json.loads(error.read_text(encoding="utf-8"))
        self.assertEqual("ERROR", payload["status"])
        self.assertNotIn("matrix_result", payload)
        self.assertNotIn("composition_result", payload)
        self.assertNotIn("evaluation_result", payload)


if __name__ == "__main__":
    unittest.main()
