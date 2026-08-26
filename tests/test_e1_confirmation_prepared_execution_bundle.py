from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_prepared_execution_bundle import (
    E1ConfirmationPreparedBundleError,
    E1PreparedRuntimeInput,
    S1_EC1_ATTEMPT,
    S1_EC1_LOCK,
    S1_EC1_REPORT,
    execute_prepared_bundle_synthetically,
    prepare_e1_confirmation_execution_bundle,
)


CANONICAL_TARGETS = (
    Path("reports/e1_refined_confirmation_s1eb_once_v1.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.attempt.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.lock"),
)


def _payload_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


class E1ConfirmationPreparedExecutionBundleTests(unittest.TestCase):
    def _prepare(self, directory: Path, calls: list[str], payload=None):
        value = {"corridor": "synthetic", "revision": 1} if payload is None else payload

        def resolver():
            calls.append("resolve")
            return (
                E1PreparedRuntimeInput(
                    role="corridor",
                    value=value,
                    prepared_digest=_payload_digest(value),
                    digest_reader=_payload_digest,
                ),
            )

        return prepare_e1_confirmation_execution_bundle(directory, resolver)

    def test_resolves_once_before_markers_and_passes_same_object(self) -> None:
        calls = []
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self._prepare(root, calls)
            prepared_value = bundle.value("corridor")

            def consumer(received):
                calls.append("consume")
                self.assertIs(received, bundle)
                self.assertIs(received.value("corridor"), prepared_value)
                self.assertTrue((root / S1_EC1_ATTEMPT).is_file())
                self.assertTrue((root / S1_EC1_LOCK).is_file())
                return _payload_digest({"consumed": received.bundle_digest})

            receipt = execute_prepared_bundle_synthetically(bundle, consumer)

            self.assertEqual(["resolve", "consume"], calls)
            self.assertTrue((root / S1_EC1_REPORT).is_file())
            self.assertFalse((root / S1_EC1_ATTEMPT).exists())
            self.assertFalse((root / S1_EC1_LOCK).exists())
            self.assertFalse(receipt.canonical_execution_permitted)

    def test_failure_after_attempt_retains_attempt_and_blocks_second_start(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self._prepare(root, [])

            def fail(_bundle):
                raise RuntimeError("synthetic consumer failure")

            with self.assertRaisesRegex(RuntimeError, "synthetic consumer failure"):
                execute_prepared_bundle_synthetically(bundle, fail)

            self.assertTrue((root / S1_EC1_ATTEMPT).is_file())
            self.assertFalse((root / S1_EC1_REPORT).exists())
            self.assertFalse((root / S1_EC1_LOCK).exists())
            with self.assertRaisesRegex(
                E1ConfirmationPreparedBundleError, "already used"
            ):
                execute_prepared_bundle_synthetically(
                    bundle, lambda _bundle: "0" * 64
                )

    def test_changed_input_fails_before_first_marker(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {"revision": 1}
            bundle = self._prepare(root, [], payload)
            payload["revision"] = 2

            with self.assertRaisesRegex(
                E1ConfirmationPreparedBundleError, "prepared input changed"
            ):
                execute_prepared_bundle_synthetically(
                    bundle, lambda _bundle: "0" * 64
                )

            self.assertEqual((), tuple(root.iterdir()))

    def test_consumer_mutation_fails_and_retains_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {"revision": 1}
            bundle = self._prepare(root, [], payload)

            def mutate(_bundle):
                payload["revision"] = 2
                return "0" * 64

            with self.assertRaisesRegex(
                E1ConfirmationPreparedBundleError, "prepared input changed"
            ):
                execute_prepared_bundle_synthetically(bundle, mutate)

            self.assertTrue((root / S1_EC1_ATTEMPT).is_file())
            self.assertFalse((root / S1_EC1_REPORT).exists())
            self.assertFalse((root / S1_EC1_LOCK).exists())

    def test_worker_source_has_no_resolver_or_canonical_entrypoint(self) -> None:
        source = inspect.getsource(execute_prepared_bundle_synthetically)

        for forbidden in (
            "resolver(",
            "build_e1_refined_confirmation_contract",
            "produce_e1_confirmation_canonical_formation",
            "run_e1_confirmation_canonical_seven_arm_probe",
        ):
            self.assertNotIn(forbidden, source)

    def test_synthetic_lifecycle_does_not_touch_terminal_s1eb31_targets(self) -> None:
        before = tuple(
            (path.exists(), _payload_digest(path.read_text(encoding="ascii")) if path.exists() else None)
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            bundle = self._prepare(Path(directory), [])
            execute_prepared_bundle_synthetically(
                bundle, lambda received: _payload_digest(received.input_manifest)
            )
        after = tuple(
            (path.exists(), _payload_digest(path.read_text(encoding="ascii")) if path.exists() else None)
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
