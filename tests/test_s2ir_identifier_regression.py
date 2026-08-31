"""Focused one-shot regression for the strict S2-IR runtime identifiers."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from tests import test_s2ih_joint_qualification as neutral
from tools import _s2ic_private_direct_two_area_conflict_baseline as direct_baseline
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2ic_private_two_area_conflict_signal as conflict_signal
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2ir-identifier-regression-20260901-01"
STRICT_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


def _case_fixture(
    case_id: str,
) -> tuple[
    object,
    object,
    signal_contract.TwoAreaConflictSignalInput,
    signal_contract.TwoAreaConflictSignalInput,
    runner.DualProbeCaseBinding,
    dict[str, int],
    runner._CaseRuntimeIdentifiers,
]:
    values = neutral._dual_fixture()
    probe = values[1]
    bundle = values[2]
    context_wrapper = values[5]
    signal_wrapper = values[6]
    identifiers = runner._case_runtime_identifiers(case_id)
    signal_input = signal_contract.TwoAreaConflictSignalInput.build(
        identifiers.signal_invocation_id,
        "SIGNAL",
        probe,
        bundle,
    )
    baseline_input = signal_contract.TwoAreaConflictSignalInput.build(
        identifiers.baseline_invocation_id,
        "DIRECT_BASELINE",
        probe,
        bundle,
    )
    binding, ledger = runner.bind_dual_probe_case(
        context_wrapper,
        signal_wrapper,
        bundle,
        signal_input,
        baseline_input,
    )
    return probe, bundle, signal_input, baseline_input, binding, ledger, identifiers


def _owners(
    binding: runner.DualProbeCaseBinding,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    baseline_input: signal_contract.TwoAreaConflictSignalInput,
    identifiers: runner._CaseRuntimeIdentifiers,
) -> tuple[
    runner.DualProbeCaseOwner,
    signal_contract.TwoAreaConflictSignalOwner,
    signal_contract.TwoAreaConflictSignalOwner,
]:
    return (
        runner.DualProbeCaseOwner(identifiers.dual_owner_id, binding),
        signal_contract.TwoAreaConflictSignalOwner(
            signal_contract.TwoAreaConflictOwnerPrestate.build(
                identifiers.signal_owner_id,
                signal_input,
            )
        ),
        signal_contract.TwoAreaConflictSignalOwner(
            signal_contract.TwoAreaConflictOwnerPrestate.build(
                identifiers.baseline_owner_id,
                baseline_input,
            )
        ),
    )


class S2IRIdentifierRegressionTests(unittest.TestCase):
    def test_01_registry_and_functional_scope_remain_exact(self) -> None:
        self.assertEqual((183, 366), (len(fixtures.REGISTRY.rows), fixtures.SUCCESS_EVENT_COUNT))
        self.assertEqual(6, len(fixtures.HISTORIES))
        self.assertEqual(38, sum(len(history.steps) for history in fixtures.HISTORIES))
        self.assertEqual(8, len(fixtures.FUNCTION_CASES))
        operation_ids = tuple(row.operation_id for row in fixtures.REGISTRY.rows)
        self.assertEqual(len(operation_ids), len(set(operation_ids)))
        self.assertTrue(all(STRICT_IDENTIFIER.fullmatch(value) for value in operation_ids))

    def test_02_all_formation_runtime_identifiers_are_valid_and_unique(self) -> None:
        identifiers = tuple(
            runner._formation_runtime_identifiers(history.history_id, step.ordinal)
            for history in fixtures.HISTORIES
            for step in history.steps
        )
        values = tuple(
            value
            for item in identifiers
            for value in (item.owner_id, item.authorization_id, item.consumption_id)
        )
        self.assertEqual((38, 114), (len(identifiers), len(values)))
        self.assertEqual(len(values), len(set(values)))
        self.assertTrue(all(STRICT_IDENTIFIER.fullmatch(value) for value in values))
        self.assertTrue(all("." not in value for value in values))

    def test_03_all_case_runtime_identifiers_are_valid_and_unique(self) -> None:
        identifiers = tuple(
            runner._case_runtime_identifiers(case.case_id)
            for case in fixtures.FUNCTION_CASES
        )
        values = tuple(
            value
            for item in identifiers
            for value in (
                item.signal_invocation_id,
                item.baseline_invocation_id,
                item.dual_owner_id,
                item.signal_owner_id,
                item.baseline_owner_id,
            )
        )
        self.assertEqual((8, 40), (len(identifiers), len(values)))
        self.assertEqual(len(values), len(set(values)))
        self.assertTrue(all(STRICT_IDENTIFIER.fullmatch(value) for value in values))
        self.assertTrue(all("." not in value for value in values))

    def test_04_complete_runtime_inventory_has_no_alias_or_fallback_path(self) -> None:
        formation_values = {
            value
            for history in fixtures.HISTORIES
            for step in history.steps
            for value in (
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).owner_id,
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).authorization_id,
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).consumption_id,
            )
        }
        case_values = {
            value
            for case in fixtures.FUNCTION_CASES
            for value in (
                runner._case_runtime_identifiers(case.case_id).signal_invocation_id,
                runner._case_runtime_identifiers(case.case_id).baseline_invocation_id,
                runner._case_runtime_identifiers(case.case_id).dual_owner_id,
                runner._case_runtime_identifiers(case.case_id).signal_owner_id,
                runner._case_runtime_identifiers(case.case_id).baseline_owner_id,
            )
        }
        self.assertEqual(154, len(formation_values | case_values))
        self.assertTrue(formation_values.isdisjoint(case_values))
        with self.assertRaises(runner.S2IGRunnerError):
            runner._strict_identifier("s2ig", "bad.part")
        with self.assertRaises(runner.S2IGRunnerError):
            runner._formation_runtime_identifiers("h-c", 5)
        with self.assertRaises(runner.S2IGRunnerError):
            runner._case_runtime_identifiers("c09")

    def test_05_all_eight_signal_and_baseline_call_sites_accept_bound_ids(self) -> None:
        observed_ids: set[str] = set()
        for case in fixtures.FUNCTION_CASES:
            probe, bundle, signal_input, baseline_input, binding, _, identifiers = _case_fixture(
                case.case_id
            )
            dual_owner, signal_owner, baseline_owner = _owners(
                binding,
                signal_input,
                baseline_input,
                identifiers,
            )
            before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
            signal_commit = conflict_signal.form_two_area_conflict_signal(
                probe,
                bundle,
                signal_input,
                signal_owner,
            )
            baseline_commit = direct_baseline.form_direct_two_area_conflict_baseline(
                probe,
                bundle,
                baseline_input,
                baseline_owner,
            )
            poststate = dual_owner.commit(
                binding,
                signal_commit.result.result_digest,
                baseline_commit.result.result_digest,
            )
            self.assertEqual(signal_commit.result.status, baseline_commit.result.status)
            self.assertEqual(before, (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest))
            self.assertEqual("CONSUMED", poststate.state)
            observed_ids.update(
                (
                    signal_input.invocation_id,
                    baseline_input.invocation_id,
                    dual_owner.prestate.owner_id,
                    signal_owner.prestate.owner_id,
                    baseline_owner.prestate.owner_id,
                )
            )
        self.assertEqual(40, len(observed_ids))

    def test_06_neutral_recorder_path_reaches_beyond_ie_op_117(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2ir-") as temporary:
            root = Path(temporary).resolve()
            plan, registry = runner.materialize_execution_plan(
                WORKSPACE_ROOT,
                QUALIFICATION_ID,
                "s2ir-identifier-regression-owner",
            )
            reserved = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
            self.assertIs(type(reserved), recording.AppendOnlyRunRecorder)
            recorder = reserved
            for index in range(3, 117):
                row = recorder.current_row()
                recorder.start(row.operation_id, {"neutral_prefix": True, "ordinal": index})
                recorder.finish(
                    row.operation_id,
                    {
                        "result": {
                            "schema": "s2ir.neutral-prefix.v1",
                            "operation_id": row.operation_id,
                            "ordinal": index,
                        }
                    },
                )

            probe, bundle, signal_input, baseline_input, binding, ledger, identifiers = _case_fixture(
                "c01"
            )
            dual_owner, signal_owner, baseline_owner = _owners(
                binding,
                signal_input,
                baseline_input,
                identifiers,
            )
            dual_record = runner._record(
                recorder,
                {
                    "case_plan_digest": binding.case_plan_digest,
                    "context_retrieval_probe_digest": binding.context_retrieval_probe_digest,
                    "masked_signal_probe_digest": binding.masked_signal_probe_digest,
                },
                lambda: (binding, dual_owner.prestate, signal_input, baseline_input),
                lambda result: {
                    "schema": "s2if.dual-probe-binding-receipt.v1",
                    "dual_probe_binding": runner._canonical(result[0]),
                    "owner_prestate": runner._canonical(result[1]),
                    "signal_input_digest": result[2].input_digest,
                    "baseline_input_digest": result[3].input_digest,
                    "source_ledger": ledger,
                    "source_ledger_digest": binding.source_ledger_digest,
                },
            )
            signal_record = runner._record(
                recorder,
                {"dual_probe_binding_digest": binding.dual_probe_binding_digest},
                lambda: conflict_signal.form_two_area_conflict_signal(
                    probe,
                    bundle,
                    signal_input,
                    signal_owner,
                ),
                runner._signal_result_receipt,
            )
            baseline_record = runner._record(
                recorder,
                {"dual_probe_binding_digest": binding.dual_probe_binding_digest},
                lambda: direct_baseline.form_direct_two_area_conflict_baseline(
                    probe,
                    bundle,
                    baseline_input,
                    baseline_owner,
                ),
                runner._signal_result_receipt,
            )
            owner_post = dual_owner.commit(
                binding,
                signal_record.value.result.result_digest,
                baseline_record.value.result.result_digest,
            )
            runner._record(
                recorder,
                {
                    "signal_result_digest": signal_record.value.result.result_digest,
                    "baseline_result_digest": baseline_record.value.result.result_digest,
                },
                lambda: owner_post,
                lambda value: runner._canonical(value),
            )
            self.assertEqual("ie-op-121", recorder.current_row().operation_id)
            self.assertEqual(240, recorder.event_count)
            self.assertEqual("ACTIVE", recorder.state)
            self.assertEqual("CONSUMED", dual_owner.state)
            self.assertTrue(dual_record.artifact_digest)

    def test_07_execution_plan_binds_the_corrected_runner_source(self) -> None:
        plan, _ = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2ir-source-binding-20260901-01",
            "s2ir-source-binding-owner",
        )
        source_digests = dict(plan.source_digests)
        runner_path = WORKSPACE_ROOT / "tools" / "_s2ig_private_runner.py"
        self.assertEqual(
            hashlib.sha256(runner_path.read_bytes()).hexdigest(),
            source_digests["tools/_s2ig_private_runner.py"],
        )

    def test_08_main_gate_remains_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


if __name__ == "__main__":
    unittest.main()
