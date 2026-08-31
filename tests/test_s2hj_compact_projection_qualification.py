"""One-shot neutral S2-HJ qualification of the three compact projections."""

from __future__ import annotations

import csv
from dataclasses import asdict, fields, MISSING
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2gb_private_perceptual_context_bundle as context_bundle
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gt_private_append_only_recorder as recording
from tools import _s2gt_private_fixture_registry as fixtures
from tools import _s2gt_private_result_verifier as verifier
from tools import _s2gt_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2hj-compact-projection-qualification-20260831-01"
ROLE_COUNTS = {"FORMATION": 52, "S2GC": 4, "S2GI": 4}
ROLE_LIMITS = {"FORMATION": 2_801, "S2GC": 3_174, "S2GI": 2_977}
REGISTRY_LIMIT = 4_096


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _digest(payload: object) -> str:
    return fixtures.canonical_digest(payload)


def _exact(cls: type, /, **values: object) -> object:
    """Create exact frozen dataclass evidence without invoking a domain function."""

    instance = object.__new__(cls)
    for item in fields(cls):
        if item.name in values:
            value = values[item.name]
        elif item.default is not MISSING:
            value = item.default
        elif item.default_factory is not MISSING:  # type: ignore[comparison-overlap]
            value = item.default_factory()  # type: ignore[misc]
        else:
            value = None
        object.__setattr__(instance, item.name, value)
    return instance


def _rows() -> dict[str, tuple[dict[str, str], ...]]:
    path = WORKSPACE_ROOT / "docs/S2GR_OPERATION_REGISTRY.csv"
    with path.open("r", encoding="ascii", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    return {
        "FORMATION": tuple(row for row in rows if row["operation_class"] == "COMPOSITE_FORMATION"),
        "S2GC": tuple(row for row in rows if row["operation_class"] == "S2GC_PROJECTION"),
        "S2GI": tuple(row for row in rows if row["operation_class"] == "S2GI_PROJECTION"),
    }


def _recorder(operation_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        plan=SimpleNamespace(
            plan_digest=_hash("s2hj.plan"),
            owner_id="s2hj-neutral-owner-" + "x" * 72,
        ),
        reservation_digest=_hash("s2hj.reservation"),
        pending_start=(operation_id, _hash(f"s2hj.start.{operation_id}")),
    )


def _envelope(recorder: SimpleNamespace, row: dict[str, str], receipt: object) -> dict[str, object]:
    return {
        "schema": recording.RECORDER_SCHEMA,
        "operation_id": row["operation_id"],
        "owner_id": recorder.plan.owner_id,
        "reservation_digest": recorder.reservation_digest,
        "start_event_digest": recorder.pending_start[1],
        "artifact": {"result": runner._canonical(receipt)},
    }


def _formation_sources(row: dict[str, str]) -> tuple[runner._BoundSource, coordinator.B4TSPM1StepResult]:
    suffix = f"{row['history']}.{row['source_ordinal']}"
    config_digest = _hash("s2hj.config")
    prestate_digest = _hash(f"s2hj.prestate.{suffix}")
    input_digest = _hash(f"s2hj.input.{suffix}")
    owner_prestate_digest = _hash(f"s2hj.owner.prestate.{suffix}")
    b4_digest = _hash(f"s2hj.b4.{suffix}")
    tspm_result_digest = _hash(f"s2hj.tspm.result.{suffix}")
    tspm_receipt_digest = _hash(f"s2hj.tspm.receipt.{suffix}")
    tspm_state_digest = _hash(f"s2hj.tspm.state.{suffix}")
    generation = int(row["source_ordinal"])
    event = "B4_APPENDED" if generation <= 9 else "B4_EVICTED_AND_APPENDED"
    counts = (26, 29, 0, 414, 468, 36, 12, 54, 497, 468, 74)
    ledger_payload = {
        "schema": coordinator.S2FS_SCHEMA,
        "operation": "FORMATION",
        "common_projection_terms": counts[0],
        "b4_functional_write_words": counts[1],
        "b4_functional_distance_terms": counts[2],
        "tspm_functional_write_words": counts[3],
        "tspm_functional_distance_terms": counts[4],
        "coordinator_validation_terms": counts[5],
        "coordinator_digest_operations": counts[6],
        "coordinator_write_words": counts[7],
        "total_functional_write_words": counts[8],
        "total_functional_distance_terms": counts[9],
        "total_control_terms": counts[10],
    }
    ledger_digest = _digest(ledger_payload)
    poststate_payload = {
        "schema": coordinator.S2FS_SCHEMA,
        "config_digest": config_digest,
        "generation": generation,
        "parent_state_digest": prestate_digest,
        "last_input_digest": input_digest,
        "b4_state_digest": b4_digest,
        "tspm_state_digest": tspm_state_digest,
    }
    poststate_digest = _digest(poststate_payload)
    step_payload = {
        "schema": coordinator.S2FS_SCHEMA,
        "config_digest": config_digest,
        "owner_prestate_digest": owner_prestate_digest,
        "input_digest": input_digest,
        "composite_prestate_digest": prestate_digest,
        "b4_event": event,
        "b4_slot_id": f"b4.slot.{(generation - 1) % 9:03d}",
        "b4_poststate_digest": b4_digest,
        "tspm_result_digest": tspm_result_digest,
        "tspm_receipt_digest": tspm_receipt_digest,
        "tspm_poststate_digest": tspm_state_digest,
        "resource_ledger_digest": ledger_digest,
        "composite_poststate_digest": poststate_digest,
    }
    step_digest = _digest(step_payload)
    owner_ids = (
        f"s2hj.owner.{suffix}",
        f"s2hj.authorization.{suffix}",
        f"s2hj.consumption.{suffix}",
    )
    owner_result_projection = {
        "schema": coordinator.S2FS_SCHEMA,
        "owner_id": owner_ids[0],
        "authorization_id": owner_ids[1],
        "consumption_id": owner_ids[2],
        "authorized_config_digest": config_digest,
        "authorized_prestate_digest": prestate_digest,
        "authorized_input_digest": input_digest,
        "status": "CONSUMED",
        "attempt_count": 1,
        "use_count": 1,
        "failure_code": None,
        "failure_digest": None,
    }
    result_payload = {
        "schema": coordinator.S2FS_SCHEMA,
        "poststate_digest": poststate_digest,
        "receipt_digest": step_digest,
        "resource_ledger_digest": ledger_digest,
        "owner_poststate_projection": owner_result_projection,
    }
    result_digest = _digest(result_payload)
    owner_payload = dict(owner_result_projection)
    owner_payload["committed_result_digest"] = result_digest
    owner_digest = _digest(owner_payload)

    bound = _exact(coordinator.B4TSPM1BoundInput, input_digest=input_digest)
    source = _exact(
        runner._BoundSource,
        role="FORMATION",
        source_id=f"s2hj.source.{suffix}",
        visual_fixture_id="neutral-visual",
        auditory_fixture_id="neutral-auditory",
        window_start=generation - 1,
        window_end=generation,
        envelope=None,
        bound=bound,
        raw_payload_retained=False,
        raw_sha256=_hash(f"s2hj.raw.{suffix}"),
        source_digest=_hash(f"s2hj.source.digest.{suffix}"),
    )
    receipt = SimpleNamespace(
        config_digest=config_digest,
        owner_prestate_digest=owner_prestate_digest,
        input_digest=input_digest,
        composite_prestate_digest=prestate_digest,
        b4_event=event,
        b4_slot_id=step_payload["b4_slot_id"],
        b4_poststate_digest=b4_digest,
        tspm_result_digest=tspm_result_digest,
        tspm_receipt_digest=tspm_receipt_digest,
        tspm_poststate_digest=tspm_state_digest,
        resource_ledger_digest=ledger_digest,
        composite_poststate_digest=poststate_digest,
        receipt_digest=step_digest,
    )
    ledger = SimpleNamespace(
        operation="FORMATION",
        common_projection_terms=counts[0],
        b4_functional_write_words=counts[1],
        b4_functional_distance_terms=counts[2],
        tspm_functional_write_words=counts[3],
        tspm_functional_distance_terms=counts[4],
        coordinator_validation_terms=counts[5],
        coordinator_digest_operations=counts[6],
        coordinator_write_words=counts[7],
        total_functional_write_words=counts[8],
        total_functional_distance_terms=counts[9],
        total_control_terms=counts[10],
        ledger_digest=ledger_digest,
    )
    owner = SimpleNamespace(
        owner_id=owner_ids[0],
        authorization_id=owner_ids[1],
        consumption_id=owner_ids[2],
        authorized_config_digest=config_digest,
        authorized_prestate_digest=prestate_digest,
        authorized_input_digest=input_digest,
        status="CONSUMED",
        attempt_count=1,
        use_count=1,
        committed_result_digest=result_digest,
        failure_code=None,
        failure_digest=None,
        owner_state_digest=owner_digest,
    )
    poststate = SimpleNamespace(
        generation=generation,
        parent_state_digest=prestate_digest,
        last_input_digest=input_digest,
        state_digest=poststate_digest,
    )
    result = _exact(
        coordinator.B4TSPM1StepResult,
        poststate=poststate,
        receipt=receipt,
        resource_ledger=ledger,
        owner_poststate=owner,
        result_digest=result_digest,
        schema=coordinator.S2FS_SCHEMA,
    )
    return source, result  # type: ignore[return-value]


def _context_sources(label: str) -> tuple[
    coordinator.B4TSPM1ReadOnlyFinding,
    context_bundle.ValidatedB4ShortSequenceEvidence,
    context_bundle.PerceptualContextBundle,
]:
    state_digest = _hash(f"s2hj.state.{label}")
    probe_digest = _hash(f"s2hj.probe.{label}")
    evidence_digest = _hash(f"s2hj.sequence.evidence.{label}")
    finding = _exact(
        coordinator.B4TSPM1ReadOnlyFinding,
        observed_state_digest=state_digest,
        probe_digest=probe_digest,
        b4_recent=SimpleNamespace(observed_state_digest=state_digest),
        prestate_digest=state_digest,
        poststate_digest=state_digest,
        finding_digest=_hash(f"s2hj.finding.{label}"),
        schema=coordinator.S2FS_SCHEMA,
    )
    sequence = _exact(
        context_bundle.ValidatedB4ShortSequenceEvidence,
        evidence_digest=evidence_digest,
        schema=context_bundle.S2GB_SCHEMA,
    )

    components = []
    specifications = (("AV_JOINT", 26), ("AV_JOINT", 26), ("AUDITORY", 8), ("VISUAL", 18))
    for index, (role, dimension) in enumerate(specifications):
        components.append(
            SimpleNamespace(
                component_role=role,
                component_digest=_hash(f"s2hj.component.{label}.{index}"),
                source_digest=_hash(f"s2hj.component.source.{label}.{index}"),
                values_digest=_hash(f"s2hj.component.values.{label}.{index}"),
                native_distances=None if index == 0 else ((0.0, 0.0) if dimension == 26 else (0.0,)),
                functional_distances=(0.0, 0.0) if dimension == 26 else (0.0,),
                support_count=None if index == 0 else 3,
                stable=None if index < 2 else True,
                last_selected_step=None if index == 0 else 4,
                formation_index=1 if index == 0 else None,
            )
        )
    candidates = (
        SimpleNamespace(candidate_digest=_hash(f"s2hj.candidate.{label}.0"), components=(components[0],)),
        SimpleNamespace(candidate_digest=_hash(f"s2hj.candidate.{label}.1"), components=(components[1],)),
        SimpleNamespace(candidate_digest=_hash(f"s2hj.candidate.{label}.2"), components=(components[2], components[3])),
    )
    roles = tuple(
        SimpleNamespace(
            status="AVAILABLE_COMPLETE",
            absence_reason=None,
            finding_digest=_hash(f"s2hj.role.{label}.{index}"),
            candidate=candidate,
        )
        for index, candidate in enumerate(candidates)
    )
    sequence_finding = SimpleNamespace(
        status="AVAILABLE",
        references=(SimpleNamespace(reference_digest=_hash(f"s2hj.reference.{label}.0")),),
        source_evidence_digest=evidence_digest,
        observed_b4_state_digest=state_digest,
        finding_digest=_hash(f"s2hj.sequence.finding.{label}"),
    )
    ledger = SimpleNamespace(
        validated_evidence_records=8,
        validated_digest_count=13,
        role_projection_count=3,
        candidate_count=3,
        component_count=4,
        value_count=78,
        sequence_reference_count=1,
        digest_operation_count=13,
        ledger_digest=_hash(f"s2hj.context.ledger.{label}"),
    )
    bundle = _exact(
        context_bundle.PerceptualContextBundle,
        contract_digest=context_bundle.S2GA_CONTRACT_DIGEST,
        binding_digest=_hash(f"s2hj.bundle.binding.{label}"),
        config_digest=_hash("s2hj.config"),
        composite_state_digest=state_digest,
        probe_digest=probe_digest,
        source_digest=_hash(f"s2hj.bundle.source.{label}"),
        role_findings=roles,
        sequence_finding=sequence_finding,
        resource_ledger=ledger,
        prestate_digest=state_digest,
        poststate_digest=state_digest,
        automatic_selection=None,
        bundle_digest=_hash(f"s2hj.bundle.{label}"),
        schema=context_bundle.S2GB_SCHEMA,
    )
    return finding, sequence, bundle  # type: ignore[return-value]


def _two_area_source(label: str, source_bundle: context_bundle.PerceptualContextBundle) -> two_area.TwoAreaContextBundle:
    recent, fast, slow = source_bundle.role_findings
    area_a = SimpleNamespace(
        area="A_RECENT",
        recent_content=recent,
        fast_internal=fast,
        short_sequence=source_bundle.sequence_finding,
        finding_digest=_hash(f"s2hj.area.a.{label}"),
    )
    area_b = SimpleNamespace(
        area="B_STABLE",
        stable_content=slow,
        finding_digest=_hash(f"s2hj.area.b.{label}"),
    )
    ledger = SimpleNamespace(
        validated_bundle_count=1,
        validated_role_count=3,
        candidate_reference_count=3,
        component_reference_count=4,
        value_reference_count=78,
        sequence_reference_count=1,
        area_projection_count=2,
        digest_operation_count=4,
        source_ledger_digest=source_bundle.resource_ledger.ledger_digest,
        ledger_digest=_hash(f"s2hj.two.area.ledger.{label}"),
    )
    return _exact(
        two_area.TwoAreaContextBundle,
        contract_digest=two_area.S2GH_CONTRACT_DIGEST,
        source_bundle_digest=source_bundle.bundle_digest,
        binding_digest=source_bundle.binding_digest,
        config_digest=source_bundle.config_digest,
        composite_state_digest=source_bundle.composite_state_digest,
        probe_digest=source_bundle.probe_digest,
        source_digest=source_bundle.source_digest,
        area_findings=(area_a, area_b),
        resource_ledger=ledger,
        prestate_digest=source_bundle.prestate_digest,
        poststate_digest=source_bundle.poststate_digest,
        automatic_selection=None,
        bundle_digest=_hash(f"s2hj.two.area.bundle.{label}"),
        schema=two_area.S2GI_SCHEMA,
    )  # type: ignore[return-value]


class S2HJCompactProjectionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.receipts: dict[str, list[object]] = {role: [] for role in ROLE_COUNTS}
        cls.sizes: dict[str, list[int]] = {role: [] for role in ROLE_COUNTS}
        cls.identities: list[tuple[int, int, str, str]] = []

        for row in cls.rows["FORMATION"]:
            recorder = _recorder(row["operation_id"])
            source, result = _formation_sources(row)
            before = repr(result)
            receipt = runner._compact_formation_receipt(
                recorder,
                row,
                source,
                _hash(f"s2hj.receptor.artifact.{row['operation_id']}"),
                result,
            )
            runner._validate_compact_envelope_size(
                recorder, row, receipt, runner.COMPACT_FORMATION_MAX_ARTIFACT_BYTES
            )
            cls.identities.append((id(result), id(result), before, repr(result)))
            cls.receipts["FORMATION"].append(receipt)
            cls.sizes["FORMATION"].append(len(recording._canonical_bytes(_envelope(recorder, row, receipt))))

        for row in cls.rows["S2GC"]:
            recorder = _recorder(row["operation_id"])
            finding, sequence, bundle = _context_sources(row["history"])
            before = repr(bundle)
            receipt = runner._compact_s2gc_receipt(
                recorder,
                row,
                _hash(f"s2hj.finding.artifact.{row['history']}"),
                finding,
                sequence,
                bundle,
            )
            runner._validate_compact_envelope_size(
                recorder, row, receipt, runner.COMPACT_S2GC_MAX_ARTIFACT_BYTES
            )
            cls.identities.append((id(bundle), id(bundle), before, repr(bundle)))
            cls.receipts["S2GC"].append(receipt)
            cls.sizes["S2GC"].append(len(recording._canonical_bytes(_envelope(recorder, row, receipt))))

        for row in cls.rows["S2GI"]:
            recorder = _recorder(row["operation_id"])
            _, _, source_bundle = _context_sources(row["history"])
            bundle = _two_area_source(row["history"], source_bundle)
            before = repr(bundle)
            receipt = runner._compact_s2gi_receipt(
                recorder,
                row,
                _hash(f"s2hj.s2gc.artifact.{row['history']}"),
                source_bundle,
                bundle,
            )
            runner._validate_compact_envelope_size(
                recorder, row, receipt, runner.COMPACT_S2GI_MAX_ARTIFACT_BYTES
            )
            cls.identities.append((id(bundle), id(bundle), before, repr(bundle)))
            cls.receipts["S2GI"].append(receipt)
            cls.sizes["S2GI"].append(len(recording._canonical_bytes(_envelope(recorder, row, receipt))))

    def test_01_exactly_60_registry_roles_are_materialized(self) -> None:
        self.assertEqual({role: len(rows) for role, rows in self.rows.items()}, ROLE_COUNTS)
        self.assertEqual(sum(len(items) for items in self.receipts.values()), 60)

    def test_02_all_actual_envelopes_fit_role_and_registry_limits(self) -> None:
        for role, sizes in self.sizes.items():
            self.assertTrue(sizes)
            self.assertLessEqual(max(sizes), ROLE_LIMITS[role])
            self.assertTrue(all(size < REGISTRY_LIMIT for size in sizes))
        print(
            "S2HJ_SIZE_SUMMARY="
            + json.dumps(
                {
                    role: {"count": len(sizes), "minimum": min(sizes), "maximum": max(sizes)}
                    for role, sizes in self.sizes.items()
                },
                sort_keys=True,
            )
        )

    def test_03_bound_maxima_and_registry_limit_are_unchanged(self) -> None:
        self.assertEqual(runner.COMPACT_FORMATION_MAX_ARTIFACT_BYTES, 2_801)
        self.assertEqual(runner.COMPACT_S2GC_MAX_ARTIFACT_BYTES, 3_174)
        self.assertEqual(runner.COMPACT_S2GI_MAX_ARTIFACT_BYTES, 2_977)
        self.assertEqual(runner.COMPACT_PROJECTION_MAX_ARTIFACT_BYTES, 3_200)
        self.assertTrue(all(int(row["output_max_bytes"]) == REGISTRY_LIMIT for rows in self.rows.values() for row in rows))

    def test_04_projection_and_source_receipt_digests_are_bound(self) -> None:
        for receipt in (item for items in self.receipts.values() for item in items):
            payload = asdict(receipt)
            projection_digest = payload.pop("projection_digest")
            self.assertEqual(projection_digest, _digest(payload))
        for receipt in self.receipts["FORMATION"]:
            self.assertRegex(receipt.owner_prestate_digest, r"^[0-9a-f]{64}$")
            self.assertRegex(receipt.receptor_receipt_artifact_digest, r"^[0-9a-f]{64}$")
        for receipt in self.receipts["S2GC"]:
            self.assertEqual(len(receipt.sequence_digests), 2)
        for receipt in self.receipts["S2GI"]:
            self.assertRegex(receipt.source_s2gc_artifact_digest, r"^[0-9a-f]{64}$")

    def test_05_full_in_memory_objects_remain_unchanged(self) -> None:
        self.assertEqual(len(self.identities), 60)
        self.assertTrue(all(before_id == after_id and before == after for before_id, after_id, before, after in self.identities))

    def test_06_valid_formation_receipt_passes_offline_validation(self) -> None:
        row = self.rows["FORMATION"][0]
        recorder = _recorder(row["operation_id"])
        receipt = self.receipts["FORMATION"][0]
        previous = _hash("s2hj.previous.formation")
        start = {
            "event_digest": recorder.pending_start[1],
            "payload": {
                "source_digest": receipt.source_digest,
                "receptor_receipt_digest": receipt.receptor_receipt_artifact_digest,
                "prestate_digest": receipt.composite_prestate_digest,
                "previous_formation_receipt_digest": previous,
            },
        }
        manifest = {"plan_digest": recorder.plan.plan_digest, "owner_id": recorder.plan.owner_id}
        reservation = {"reservation_digest": recorder.reservation_digest}
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "formation.json"
            target.write_bytes(recording._canonical_bytes(_envelope(recorder, row, receipt)))
            self.assertEqual(
                verifier._validate_compact_formation_receipt(
                    target, row, start, manifest, reservation, previous
                ),
                [],
            )

    def test_07_owner_prestate_digest_mutation_fails_closed(self) -> None:
        row = self.rows["FORMATION"][0]
        recorder = _recorder(row["operation_id"])
        receipt = asdict(self.receipts["FORMATION"][0])
        receipt["owner_prestate_digest"] = _hash("s2hj.foreign.owner.prestate")
        projection = dict(receipt)
        projection.pop("projection_digest")
        receipt["projection_digest"] = _digest(projection)
        start = {
            "event_digest": recorder.pending_start[1],
            "payload": {
                "source_digest": receipt["source_digest"],
                "receptor_receipt_digest": receipt["receptor_receipt_artifact_digest"],
                "prestate_digest": receipt["composite_prestate_digest"],
                "previous_formation_receipt_digest": None,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mutated-owner.json"
            target.write_bytes(recording._canonical_bytes(_envelope(recorder, row, receipt)))
            errors = verifier._validate_compact_formation_receipt(
                target,
                row,
                start,
                {"plan_digest": recorder.plan.plan_digest, "owner_id": recorder.plan.owner_id},
                {"reservation_digest": recorder.reservation_digest},
                None,
            )
        self.assertTrue(any("semantic digest differs" in error for error in errors))

    def test_08_sequence_evidence_digest_mutation_fails_closed(self) -> None:
        row = self.rows["S2GC"][0]
        recorder = _recorder(row["operation_id"])
        finding, sequence, bundle = _context_sources("sequence-mutation")
        mutated = _exact(
            context_bundle.ValidatedB4ShortSequenceEvidence,
            evidence_digest=_hash("s2hj.foreign.sequence.evidence"),
            schema=context_bundle.S2GB_SCHEMA,
        )
        with self.assertRaisesRegex(recording.S2GTRecordingError, "E007"):
            runner._compact_s2gc_receipt(
                recorder,
                row,
                _hash("s2hj.finding.artifact.sequence-mutation"),
                finding,
                mutated,  # type: ignore[arg-type]
                bundle,
            )
        self.assertNotEqual(sequence.evidence_digest, mutated.evidence_digest)

    def test_09_successor_chain_mutation_fails_closed(self) -> None:
        row = self.rows["FORMATION"][0]
        recorder = _recorder(row["operation_id"])
        receipt = self.receipts["FORMATION"][0]
        expected_previous = _hash("s2hj.expected.previous")
        start = {
            "event_digest": recorder.pending_start[1],
            "payload": {
                "source_digest": receipt.source_digest,
                "receptor_receipt_digest": receipt.receptor_receipt_artifact_digest,
                "prestate_digest": receipt.composite_prestate_digest,
                "previous_formation_receipt_digest": expected_previous,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mutated-successor.json"
            target.write_bytes(recording._canonical_bytes(_envelope(recorder, row, receipt)))
            errors = verifier._validate_compact_formation_receipt(
                target,
                row,
                start,
                {"plan_digest": recorder.plan.plan_digest, "owner_id": recorder.plan.owner_id},
                {"reservation_digest": recorder.reservation_digest},
                _hash("s2hj.foreign.previous"),
            )
        self.assertTrue(any("source binding differs" in error for error in errors))

    def test_10_parallel_lists_and_role_shapes_are_complete(self) -> None:
        for receipt in self.receipts["S2GC"]:
            lengths = {
                len(receipt.component_roles),
                len(receipt.component_digests),
                len(receipt.component_source_digests),
                len(receipt.component_values_digests),
                len(receipt.component_native_distances),
                len(receipt.component_functional_distances),
                len(receipt.component_support_counts),
                len(receipt.component_stable_flags),
                len(receipt.component_last_selected_steps),
                len(receipt.component_formation_indices),
            }
            self.assertEqual(lengths, {4})
        for receipt in self.receipts["S2GI"]:
            self.assertEqual(receipt.area_roles, ("A_RECENT", "B_STABLE"))
            self.assertEqual(len(receipt.area_finding_digests), 2)

    def test_11_budgets_error_contract_and_main_gate_are_unchanged(self) -> None:
        self.assertEqual(fixtures.MAX_SUCCESS_PATH_BYTES, 2_009_088)
        self.assertEqual(fixtures.MAX_FAILURE_PATH_BYTES, 2_045_952)
        self.assertEqual(fixtures.MAX_RUN_PATH_BYTES, 2_045_952)
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertEqual(len(_rows()["FORMATION"]), 52)

    def test_12_s2hc_remains_not_evaluable(self) -> None:
        failure = WORKSPACE_ROOT / "reports/s2hc-context-function-20260830-01/failure/run-failure.json"
        payload = json.loads(failure.read_text(encoding="ascii"))
        self.assertEqual(payload["status"], "NOT_EVALUABLE")
        self.assertEqual(payload["error_code"], "E008")


if __name__ == "__main__":
    unittest.main()
