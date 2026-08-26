from __future__ import annotations

from dataclasses import fields, replace
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_research_corridor import (
    E1ConfirmationResearchCorridorError,
    S1_EC3_ATTEMPT,
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_typed_prepared_inputs import (
    prepare_e1_confirmation_typed_execution_bundle,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
    _typed_inputs,
)


class E1ConfirmationResearchCorridorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)

    def test_descriptor_has_no_path_or_execution_fields(self) -> None:
        names = {item.name for item in fields(self.descriptor)}

        for forbidden in (
            "upstream_report_path",
            "report_path",
            "attempt_path",
            "lock_path",
            "execution_id",
            "execution_started",
        ):
            self.assertNotIn(forbidden, names)

    def test_descriptor_builds_with_terminal_s1eb31_attempt_present(self) -> None:
        before = tuple(path.exists() for path in CANONICAL_TARGETS)
        rebuilt = build_e1_confirmation_research_corridor(UPSTREAM)

        self.assertEqual(self.descriptor.digest(), rebuilt.digest())
        self.assertEqual(before, tuple(path.exists() for path in CANONICAL_TARGETS))

    def test_run_contract_owns_only_new_temporary_paths(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            run = prepare_e1_confirmation_synthetic_run_contract(
                self.descriptor, root
            )

            self.assertEqual(self.descriptor.digest(), run.research_descriptor_digest)
            self.assertEqual(root.resolve(), Path(run.report_path).parent)
            self.assertFalse(run.canonical_execution_permitted)
            self.assertFalse(run.execution_started)

    def test_used_run_path_is_rejected_without_touching_it(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            attempt = root / S1_EC3_ATTEMPT
            attempt.write_text("used\n", encoding="ascii")

            with self.assertRaisesRegex(
                E1ConfirmationResearchCorridorError, "paths are used"
            ):
                prepare_e1_confirmation_synthetic_run_contract(
                    self.descriptor, root
                )

            self.assertEqual("used\n", attempt.read_text(encoding="ascii"))

    def test_s1ec2_accepts_descriptor_with_legacy_bound_plans(self) -> None:
        typed = replace(_typed_inputs(), corridor=self.descriptor)
        with TemporaryDirectory() as directory:
            bundle = prepare_e1_confirmation_typed_execution_bundle(
                Path(directory), lambda: typed
            )

            self.assertIs(self.descriptor, bundle.value("corridor"))
            self.assertEqual(
                self.descriptor.digest(),
                dict(bundle.input_manifest)["corridor"],
            )

    def test_descriptor_and_run_contract_do_not_touch_terminal_artifacts(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            prepare_e1_confirmation_synthetic_run_contract(
                self.descriptor, Path(directory)
            )
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
