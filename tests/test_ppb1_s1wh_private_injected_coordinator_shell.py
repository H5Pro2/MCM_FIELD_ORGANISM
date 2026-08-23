from __future__ import annotations

from dataclasses import fields
import inspect
import json
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wh_private_injected_coordinator_shell as s1wh
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXPECTED_RESULT_DIGEST = (
    "3528165dd9d68f1976059926b4061dd19c6b8cbfad90dc611d25dcaa56c69f4b"
)


class PPB1S1WHPrivateInjectedCoordinatorShellTests(unittest.TestCase):
    def adapter(self, adapter_id, stage, *, passed=True):
        return s1wh.S1WHInjectedStageAdapter(
            adapter_id,
            stage,
            passed,
        )

    def roles(self, *, resource_passed=True):
        root = s1wh.S1WGProductionArtifactRootResolver(
            "s1wh.injected.root",
            self.adapter("s1wh.injected.root", "H0B"),
        )
        resource = s1wh.S1WGProductionResourceObserverAdapter(
            "s1wh.injected.resource",
            self.adapter(
                "s1wh.injected.resource",
                "H0C",
                passed=resource_passed,
            ),
        )
        authorization = s1wh.S1WGExactProductionAuthorizationActivator(
            "s1wh.injected.authorization",
            self.adapter("s1wh.injected.authorization", "H0D"),
        )
        lock = s1wh.S1WGProductionLockTerminalAdapter(
            "s1wh.injected.lock",
            self.adapter("s1wh.injected.lock", "H0E"),
            self.adapter("s1wh.injected.lock", "H1"),
        )
        producer = s1wh.S1WGPrivateS1VQProducerResolver(
            "s1wh.injected.producer"
        )
        return resource, authorization, lock, producer, root

    def coordinator(self, **changes):
        return s1wh.S1WGPrivateProductionCoordinator(*self.roles(**changes))

    def test_injected_h0_h1_order_is_exact(self) -> None:
        result = self.coordinator().run_injected_h0_h1()
        self.assertEqual(
            s1wh.S1WH_H0_H1_ORDER,
            tuple(receipt.stage for receipt in result.receipts),
        )
        self.assertEqual(
            (
                "s1wh.injected.contract-validator",
                "s1wh.injected.root",
                "s1wh.injected.resource",
                "s1wh.injected.authorization",
                "s1wh.injected.lock",
                "s1wh.injected.lock",
            ),
            tuple(receipt.adapter_id for receipt in result.receipts),
        )

    def test_producer_resolver_has_no_callable_and_is_never_resolved(self) -> None:
        roles = self.roles()
        producer = roles[3]
        self.assertFalse(hasattr(producer, "resolve"))
        result = s1wh.S1WGPrivateProductionCoordinator(*roles).run_injected_h0_h1()
        self.assertEqual(0, result.producer_resolution_count)
        self.assertEqual(0, result.producer_call_count)
        self.assertEqual("H2_BLOCKED", result.next_stage)
        self.assertEqual(s1wh.S1WH_DECISION, result.decision)

    def test_result_is_canonical_and_deterministic(self) -> None:
        first = self.coordinator().run_injected_h0_h1()
        second = self.coordinator().run_injected_h0_h1()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_RESULT_DIGEST, first.result_digest)
        encoded = json.dumps(
            first.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(first.canonical_payload(), json.loads(encoded))

    def test_all_runtime_and_production_counters_are_zero(self) -> None:
        result = self.coordinator().run_injected_h0_h1()
        self.assertEqual(
            (0, 0, 0, 0, 0, 0, 0),
            (
                result.resource_probe_count,
                result.filesystem_write_count,
                result.authorization_instantiation_count,
                result.producer_resolution_count,
                result.producer_call_count,
                result.matrix_path_count,
                result.production_artifact_count,
            ),
        )
        self.assertEqual(
            s1wh.S1WH_PRODUCTION_ROOT_ROLE,
            result.production_root_role,
        )

    def test_failed_stage_stops_fail_closed(self) -> None:
        with self.assertRaises(s1wh.S1WHCoordinatorError) as raised:
            self.coordinator(resource_passed=False).run_injected_h0_h1()
        self.assertEqual(s1wh.S1WH_STAGE_FAILED, raised.exception.code)

    def test_wrong_stage_adapter_is_rejected_before_coordinator_run(self) -> None:
        with self.assertRaises(s1wh.S1WHCoordinatorError) as raised:
            s1wh.S1WGProductionArtifactRootResolver(
                "s1wh.injected.root",
                self.adapter("s1wh.injected.root", "H0C"),
            )
        self.assertEqual(s1wh.S1WH_INVALID_ROLE, raised.exception.code)

    def test_adapter_rejects_any_unexpected_invocation_stage(self) -> None:
        adapter = self.adapter("s1wh.injected.root", "H0B")
        with self.assertRaises(s1wh.S1WHCoordinatorError) as raised:
            adapter("H0C")
        self.assertEqual(s1wh.S1WH_STAGE_FAILED, raised.exception.code)

    def test_every_production_capability_flag_is_hard_disabled(self) -> None:
        cases = (
            lambda: s1wh.S1WGProductionResourceObserverAdapter(
                "s1wh.injected.noop",
                self.adapter("s1wh.injected.noop", "H0C"),
                True,
            ),
            lambda: s1wh.S1WGExactProductionAuthorizationActivator(
                "s1wh.injected.noop",
                self.adapter("s1wh.injected.noop", "H0D"),
                True,
            ),
            lambda: s1wh.S1WGProductionLockTerminalAdapter(
                "s1wh.injected.noop",
                self.adapter("s1wh.injected.noop", "H0E"),
                self.adapter("s1wh.injected.noop", "H1"),
                True,
            ),
            lambda: s1wh.S1WGPrivateS1VQProducerResolver(
                "s1wh.injected.noop",
                True,
            ),
            lambda: s1wh.S1WGProductionArtifactRootResolver(
                "s1wh.injected.noop",
                self.adapter("s1wh.injected.noop", "H0B"),
                True,
            ),
        )
        for build in cases:
            with self.subTest(build=build):
                with self.assertRaises(s1wh.S1WHCoordinatorError):
                    build()

    def test_incomplete_coordinator_role_set_is_rejected(self) -> None:
        resource, authorization, lock, producer, _ = self.roles()
        with self.assertRaises(s1wh.S1WHCoordinatorError):
            s1wh.S1WGPrivateProductionCoordinator(
                resource,
                authorization,
                lock,
                producer,
                object(),
            )

    def test_production_entry_and_runtime_imports_remain_blocked(self) -> None:
        with self.assertRaises(s1wh.S1WHCoordinatorError) as raised:
            s1wh.execute_s1wh_production_once()
        self.assertEqual(
            s1wh.S1WH_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )
        source = inspect.getsource(s1wh)
        for forbidden in (
            "import os",
            "from pathlib",
            "from tempfile",
            "from typing",
            "S1WAProductionAuthorization",
            "_execute_s1vq_corrected_matrix",
            "execute_s1vq_corrected_matrix",
            "SharedMCMField",
            "ReceptorContactFrame",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wh_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WGPrivateProductionCoordinator",
            "S1WGPrivateS1VQProducerResolver",
            "S1WHCoordinatorResult",
            "execute_s1wh_production_once",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
