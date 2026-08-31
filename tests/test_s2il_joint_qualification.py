"""One-shot joint qualification of current S2-IC and S2-IK ParentSetV1."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tests import test_s2id_private_two_area_conflict_signal as s2id
from tests import test_s2ih_joint_qualification as s2ih
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_result_verifier as verifier


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2il-joint-qualification-20260831-01"
_DIGEST = "0" * 64
_MAX_OWNER = "a" * 96


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="ascii"))


def _artifact_digests(run_directory: Path) -> dict[str, str]:
    return {
        row.operation_id: hashlib.sha256(
            (run_directory / row.target_path).read_bytes()
        ).hexdigest()
        for row in fixtures.REGISTRY.rows
    }


def _event_size(
    index: int,
    operation_class: str,
    parent_count: int,
    input_payload: dict[str, object],
    *,
    external_parent_digest: str | None = None,
) -> int:
    if parent_count >= 2:
        parent_payload: dict[str, object] = {
            "internal_parent_projection_schema": fixtures.PARENT_SET_SCHEMA,
            "internal_parent_count": parent_count,
            "internal_parent_set_digest": _DIGEST,
        }
    else:
        parent_payload = {
            "internal_parent_result_digests": tuple(_DIGEST for _ in range(parent_count))
        }
    event = {
        "schema": recording.RECORDER_SCHEMA,
        "event_index": 2 * index - 1,
        "phase": "START",
        "operation_id": f"ie-op-{index:03d}",
        "operation_index": index,
        "operation_class": operation_class,
        "owner_id": _MAX_OWNER,
        "reservation_digest": _DIGEST,
        "previous_event_digest": _DIGEST,
        "payload": {
            **parent_payload,
            "external_parent_digest": external_parent_digest,
            "input": input_payload,
        },
    }
    event["event_digest"] = recording.canonical_digest(event)
    return len(recording.canonical_bytes(event))


def _artifact_size(index: int, result: dict[str, object]) -> int:
    envelope = {
        "schema": recording.RECORDER_SCHEMA,
        "operation_id": f"ie-op-{index:03d}",
        "owner_id": _MAX_OWNER,
        "reservation_digest": _DIGEST,
        "start_event_digest": _DIGEST,
        "artifact": {"result": result},
    }
    return len(recording.canonical_bytes(envelope))


def _result_event_size(index: int, operation_class: str, artifact_bytes: int) -> int:
    event = {
        "schema": recording.RECORDER_SCHEMA,
        "event_index": 2 * index,
        "phase": "RESULT",
        "operation_id": f"ie-op-{index:03d}",
        "operation_index": index,
        "operation_class": operation_class,
        "owner_id": _MAX_OWNER,
        "reservation_digest": _DIGEST,
        "previous_event_digest": _DIGEST,
        "payload": {"artifact_digest": _DIGEST, "artifact_bytes": artifact_bytes},
    }
    event["event_digest"] = recording.canonical_digest(event)
    return len(recording.canonical_bytes(event))


class S2ILJointQualificationTests(s2ih.S2IHJointQualificationTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2il-")
        cls.root = Path(cls._temporary.name).resolve()
        cls.valid_run = s2ih._complete_neutral_recording(
            cls.root, "s2il-neutral-complete-01"
        )

    def test_22_all_76_parent_sets_are_canonical_and_independently_reconstructed(self) -> None:
        events = tuple(
            json.loads(line)
            for line in (self.valid_run / "journal/operations.jsonl")
            .read_text(encoding="ascii")
            .splitlines()
        )
        artifact_digests = _artifact_digests(self.valid_run)
        manifest = _load_json(self.valid_run / "manifest.json")["artifact"]["result"]
        reservation = _load_json(self.valid_run / "reservation.json")["artifact"]["result"]
        execution_plan = manifest["execution_plan"]
        expected_rows = verifier._expected_rows()
        rows_by_id = {str(row["operation_id"]): row for row in expected_rows}
        compact_count = 0
        compact_references = 0
        for registry_row, verifier_row in zip(
            fixtures.REGISTRY.rows, expected_rows, strict=True
        ):
            parent_ids = tuple(
                item for item in registry_row.parent_operations if item.startswith("ie-op-")
            )
            if len(parent_ids) < 2:
                continue
            compact_count += 1
            compact_references += len(parent_ids)
            start = events[2 * (registry_row.index - 1)]
            start_payload = start["payload"]
            pairs = tuple((item, artifact_digests[item]) for item in parent_ids)
            parent_set = fixtures.materialize_parent_set(
                registry_row,
                fixtures.REGISTRY,
                reservation["reservation_digest"],
                pairs,
            )
            independent = verifier._reconstruct_parent_set(
                verifier_row,
                rows_by_id,
                artifact_digests,
                execution_plan["registry_bundle_digest"],
                reservation["reservation_digest"],
            )
            self.assertIsNotNone(independent)
            self.assertEqual(fixtures.PARENT_SET_SCHEMA, start_payload["internal_parent_projection_schema"])
            self.assertEqual(len(parent_ids), start_payload["internal_parent_count"])
            self.assertEqual(parent_set.parent_set_digest, independent[0])
            self.assertEqual(parent_set.parent_set_digest, start_payload["internal_parent_set_digest"])
            self.assertNotIn("internal_parent_result_digests", start_payload)
        self.assertEqual(76, compact_count)
        self.assertEqual(188, compact_references)

    def test_23_zero_and_single_parent_operations_keep_the_legacy_projection(self) -> None:
        events = tuple(
            json.loads(line)
            for line in (self.valid_run / "journal/operations.jsonl")
            .read_text(encoding="ascii")
            .splitlines()
        )
        legacy_count = 0
        for row in fixtures.REGISTRY.rows:
            parent_count = sum(item.startswith("ie-op-") for item in row.parent_operations)
            if parent_count >= 2:
                continue
            legacy_count += 1
            payload = events[2 * (row.index - 1)]["payload"]
            self.assertEqual({"internal_parent_result_digests"}, {
                key for key in payload if key.startswith("internal_parent_")
            })
            self.assertEqual(parent_count, len(payload["internal_parent_result_digests"]))
        self.assertEqual(107, legacy_count)

    def _materializer_fixture(self) -> tuple[fixtures.OperationRow, tuple[tuple[str, str], ...]]:
        child = fixtures.REGISTRY.rows[170]
        pairs = tuple(
            (item, fixtures.canonical_digest({"neutral-parent": item}))
            for item in child.parent_operations
            if item.startswith("ie-op-")
        )
        return child, pairs

    def _verifier_fixture(self) -> tuple[dict[str, object], dict[str, dict[str, object]], dict[str, str], str, str]:
        rows = verifier._expected_rows()
        rows_by_id = {str(row["operation_id"]): row for row in rows}
        child = rows_by_id["ie-op-171"]
        artifacts = {
            operation_id: fixtures.canonical_digest({"neutral-parent": operation_id})
            for operation_id in rows_by_id
        }
        return child, rows_by_id, artifacts, _DIGEST, fixtures.canonical_digest("reservation")

    def test_24_duplicate_parent_is_rejected_by_both_materializers(self) -> None:
        child, pairs = self._materializer_fixture()
        duplicate = pairs[:-1] + (pairs[0],)
        with self.assertRaises(fixtures.S2IGRegistryError):
            fixtures.materialize_parent_set(
                child, fixtures.REGISTRY, fixtures.canonical_digest("reservation"), duplicate
            )
        v_child, rows, artifacts, registry_digest, reservation = self._verifier_fixture()
        changed = dict(v_child)
        changed["parents"] = tuple(v_child["parents"][:-1]) + (v_child["parents"][0],)
        self.assertIsNone(
            verifier._reconstruct_parent_set(changed, rows, artifacts, registry_digest, reservation)
        )

    def test_25_missing_parent_is_rejected_by_both_materializers(self) -> None:
        child, pairs = self._materializer_fixture()
        with self.assertRaises(fixtures.S2IGRegistryError):
            fixtures.materialize_parent_set(
                child, fixtures.REGISTRY, fixtures.canonical_digest("reservation"), pairs[:-1]
            )
        v_child, rows, artifacts, registry_digest, reservation = self._verifier_fixture()
        del artifacts[v_child["parents"][0]]
        self.assertIsNone(
            verifier._reconstruct_parent_set(v_child, rows, artifacts, registry_digest, reservation)
        )

    def test_26_foreign_parent_is_rejected_by_both_materializers(self) -> None:
        child, pairs = self._materializer_fixture()
        foreign = pairs[:-1] + (("ie-op-999", fixtures.canonical_digest("foreign")),)
        with self.assertRaises(fixtures.S2IGRegistryError):
            fixtures.materialize_parent_set(
                child, fixtures.REGISTRY, fixtures.canonical_digest("reservation"), foreign
            )
        v_child, rows, artifacts, registry_digest, reservation = self._verifier_fixture()
        changed = dict(v_child)
        changed["parents"] = tuple(v_child["parents"][:-1]) + ("ie-op-999",)
        self.assertIsNone(
            verifier._reconstruct_parent_set(changed, rows, artifacts, registry_digest, reservation)
        )

    def test_27_later_parent_is_rejected_by_both_materializers(self) -> None:
        child, _ = self._materializer_fixture()
        late_child = replace(
            child,
            parent_operations=child.parent_operations[:-1] + ("ie-op-183",),
        )
        rows = list(fixtures.REGISTRY.rows)
        rows[170] = late_child
        late_registry = replace(fixtures.REGISTRY, rows=tuple(rows))
        pairs = tuple(
            (item, fixtures.canonical_digest({"neutral-parent": item}))
            for item in late_child.parent_operations
            if item.startswith("ie-op-")
        )
        with self.assertRaises(fixtures.S2IGRegistryError):
            fixtures.materialize_parent_set(
                late_child,
                late_registry,
                fixtures.canonical_digest("reservation"),
                pairs,
            )
        v_child, verifier_rows, artifacts, registry_digest, reservation = self._verifier_fixture()
        changed = dict(v_child)
        changed["parents"] = tuple(v_child["parents"][:-1]) + ("ie-op-183",)
        self.assertIsNone(
            verifier._reconstruct_parent_set(
                changed, verifier_rows, artifacts, registry_digest, reservation
            )
        )

    def test_28_op_171_maximum_owner_start_is_exactly_814_bytes(self) -> None:
        self.assertEqual(
            814,
            _event_size(
                171,
                "EXECUTION_EVIDENCE_SEAL",
                14,
                {"operation_count_before_seal": 170},
            ),
        )
        self.assertLess(814, fixtures.MAX_EVENT_BYTES)

    def test_29_all_envelopes_from_171_through_183_respect_the_bound_table(self) -> None:
        rows: list[tuple[int, str, int, dict[str, object], str | None, int, dict[str, object], int, int, int]] = []
        rows.append((171, "EXECUTION_EVIDENCE_SEAL", 14, {"operation_count_before_seal": 170}, None, 3072, {
            "schema": "s2ie.execution-evidence-package.v1",
            "execution_plan_digest": _DIGEST,
            "history_evidence_artifact_digests": [_DIGEST] * 6,
            "case_evidence_artifact_digests": [_DIGEST] * 8,
            "event_count_before_seal": 340,
            "last_execution_event_digest": _DIGEST,
            "evaluation_plan_digest": None,
        }, 814, 1692, 668))
        rows.append((172, "EVALUATION_RUN_BIND", 1, {"execution_package_artifact_digest": _DIGEST, "evaluation_plan_digest": _DIGEST}, _DIGEST, 1024, {
            "schema": "s2ie.evaluation-run-binding.v1",
            "execution_package_artifact_digest": _DIGEST,
            "evaluation_plan_digest": _DIGEST,
            "binding_digest": _DIGEST,
        }, 955, 708, 663))
        for index in range(173, 181):
            case_id = f"c{index - 172:02d}"
            rows.append((index, "CASE_EVALUATE", 2, {"case_id": case_id, "evaluation_binding_digest": _DIGEST}, None, 1536, {
                "schema": "s2ie.evaluation-finding.v1",
                "case_id": case_id,
                "evaluation_binding_digest": _DIGEST,
                "observed_status": "NO_APPLICABLE_CONTEXT",
                "expected_status": "NO_APPLICABLE_CONTEXT",
                "status_matches": True,
                "signal_equals_baseline": True,
                "read_only": True,
                "method_valid": True,
            }, 880, 709, 657))
        rows.extend((
            (181, "AGGREGATE_EVALUATION", 8, {"finding_count": 8}, None, 1280, {
                "schema": "s2ie.aggregate-finding.v1",
                "finding_artifact_digests": [_DIGEST] * 8,
                "all_expected": True,
                "direct_comparison_explains": True,
                "all_read_only": True,
            }, 794, 1064, 665),
            (182, "TERMINAL_PREPARE", 1, {"aggregate_artifact_digest": _DIGEST}, None, 1024, {
                "schema": "s2ie.terminal-finding.v1",
                "status": "COMPLETING",
                "functional_status": "S2IE_REAL_TWO_AREA_STATUS_FUNCTION_VALID_DIRECT_COMPARISON_EXPLAINS",
                "aggregate_artifact_digest": _DIGEST,
            }, 790, 630, 660),
            (183, "COMPLETION_MARKER_PUBLISH", 1, {"terminal_artifact_digest": _DIGEST}, None, 1024, {
                "schema": "s2ie.completion-marker.v1",
                "status": "COMPLETE",
                "operation_count": 183,
                "event_count": 366,
                "terminal_artifact_digest": _DIGEST,
            }, 798, 578, 669),
        ))
        self.assertEqual(tuple(range(171, 184)), tuple(item[0] for item in rows))
        for index, operation_class, parents, inputs, external, artifact_limit, result, expected_start, expected_artifact, expected_result in rows:
            start_size = _event_size(
                index,
                operation_class,
                parents,
                inputs,
                external_parent_digest=external,
            )
            artifact_size = _artifact_size(index, result)
            result_size = _result_event_size(index, operation_class, artifact_size)
            self.assertEqual(expected_start, start_size)
            self.assertEqual(expected_artifact, artifact_size)
            self.assertEqual(expected_result, result_size)
            self.assertLess(start_size, fixtures.MAX_EVENT_BYTES)
            self.assertLess(result_size, fixtures.MAX_EVENT_BYTES)
            self.assertLessEqual(artifact_size, artifact_limit)
        self.assertEqual((183, 366), (len(fixtures.REGISTRY.rows), fixtures.SUCCESS_EVENT_COUNT))


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(s2id.S2IDPrivateTwoAreaConflictSignalTests))
    suite.addTests(loader.loadTestsFromTestCase(S2ILJointQualificationTests))
    return suite


if __name__ == "__main__":
    unittest.main()
