from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_executor import (
    E1ConfirmationCanonicalExecutorError,
    _execute_bound_report_synthetically,
    execute_e1_confirmation_canonical_once,
)
from mcm_field_organism.e1_confirmation_canonical_report_handoff import (
    prepare_e1_confirmation_canonical_report_handoff,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    S1_EB4_REPORT_FIELDS,
)
from tests.test_e1_confirmation_canonical_report_handoff import _inputs


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationCanonicalExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.result_handoff, cls.result = _inputs()
        cls.report_handoff = prepare_e1_confirmation_canonical_report_handoff(
            cls.binding, cls.chain, cls.result_handoff, cls.result
        )

    def test_synthetic_adapter_publishes_complete_report_temporarily(self):
        with TemporaryDirectory() as directory:
            receipt = _execute_bound_report_synthetically(
                self.chain,
                self.report_handoff,
                self.result,
                Path(directory),
            )
            report = json.loads(
                Path(receipt.report_path).read_text(encoding="ascii")
            )

            self.assertEqual(S1_EB4_REPORT_FIELDS, tuple(report))
            self.assertEqual(self.result.result_digest, receipt.result_sha256)
            self.assertEqual(
                "NUMERICALLY_UNDECIDABLE", receipt.technical_decision
            )

    def test_synthetic_adapter_enforces_exactly_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _execute_bound_report_synthetically(
                self.chain, self.report_handoff, self.result, root
            )

            with self.assertRaises(E1ConfirmationCanonicalExecutorError):
                _execute_bound_report_synthetically(
                    self.chain, self.report_handoff, self.result, root
                )

    def test_synthetic_adapter_rejects_registered_directory_before_write(self):
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalExecutorError,
            "registered targets",
        ):
            _execute_bound_report_synthetically(
                self.chain,
                self.report_handoff,
                self.result,
                Path(self.chain.report_path).parent,
            )

    def test_invalid_result_fails_before_synthetic_write(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1ConfirmationCanonicalExecutorError,
                "does not match",
            ):
                _execute_bound_report_synthetically(
                    self.chain, self.report_handoff, object(), root
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_canonical_entrypoint_stops_before_any_writer(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalExecutorError,
            "remain locked",
        ):
            execute_e1_confirmation_canonical_once(
                self.binding,
                self.chain,
                self.report_handoff,
                self.result,
            )

    def test_canonical_entrypoint_contains_no_writer_call(self) -> None:
        source = inspect.getsource(execute_e1_confirmation_canonical_once)
        for forbidden in (
            "execute_synthetic_e1_confirmation_once(",
            "_atomic_publish(",
            "_exclusive_marker(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_registered_paths_stay_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        with TemporaryDirectory() as directory:
            _execute_bound_report_synthetically(
                self.chain,
                self.report_handoff,
                self.result,
                Path(directory),
            )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalExecutorError",
            "execute_e1_confirmation_canonical_once",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
