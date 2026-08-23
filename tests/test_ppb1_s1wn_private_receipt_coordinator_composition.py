from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wb_private_production_h0_types as s1wb
import mcm_field_organism._ppb1_s1wj_injected_root_resource_adapters as s1wj
import mcm_field_organism._ppb1_s1wl_private_authorization_validator_adapter as s1wl
import mcm_field_organism._ppb1_s1wn_private_receipt_coordinator_composition as s1wn
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXECUTION_ID = "ppb1.s1wn.injected.case-001"
EXPECTED_RESULT_DIGEST = (
    "f9f483634cdc1dbe7dd9730ba2eb81fd16645a6083fc42550da7d32f931ffdd0"
)


class PPB1S1WNPrivateReceiptCoordinatorCompositionTests(unittest.TestCase):
    def root_receipt(self, artifact="SYNTHETIC-VOLUME-C", temporary=None):
        temporary = artifact if temporary is None else temporary
        values = {
            "declared_production_relative_root": (
                s1wj.S1WJ_PRODUCTION_RELATIVE_ROOT
            ),
            "mirror_root_digest": hashlib.sha256(b"s1wn-mirror").hexdigest(),
            "artifact_volume_identity": artifact,
            "temporary_volume_identity": temporary,
            "same_volume": artifact == temporary,
            "mirror_only": True,
            "production_root_accessed": False,
            "filesystem_write_count": 0,
            "production_artifact_count": 0,
        }
        payload = {
            "schema_version": s1wj.S1WJ_SCHEMA_VERSION,
            "mode": s1wj.S1WJ_MODE,
            "contract_digest": s1wj.S1WJ_CONTRACT_DIGEST,
            **values,
        }
        return s1wj.S1WJRootMirrorReceipt(
            **values,
            receipt_digest=s1wj._digest(payload),
        )

    def resource_receipt(self, root=None, **changes):
        root = self.root_receipt() if root is None else root
        values = {
            "available_physical_memory_bytes": 3 * 1024**3,
            "artifact_volume_free_bytes": 2 * 1024**3,
            "atomic_replace_probe_passed": True,
            "artifact_paths_free": True,
        }
        values.update(changes)
        return s1wj.observe_s1wj_injected_resources(root, **values)

    def authorization_receipt(self, gate_digest, *, text=None):
        exact = s1wb.S1WB_AUTHORIZATION_TEMPLATE.format(
            execution_id=EXECUTION_ID,
            contract_digest=s1wb.S1WB_CONTRACT_DIGEST,
            resource_gate_digest=gate_digest,
        )
        return s1wl.validate_s1wl_injected_authorization_text(
            exact if text is None else text,
            EXECUTION_ID,
            gate_digest,
        )

    def chain(self):
        root = self.root_receipt()
        resource = self.resource_receipt(root)
        authorization = self.authorization_receipt(
            resource.gate.resource_gate_digest
        )
        return root, resource, authorization

    def test_exact_h0a_to_h1_order_stops_at_h2(self) -> None:
        result = s1wn.compose_s1wn_in_memory_h0_h1(*self.chain())
        self.assertEqual(
            ("H0A", "H0B", "H0C", "H0D", "H0E", "H1"),
            tuple(item.stage for item in result.coordinator_result.receipts),
        )
        self.assertEqual("H2_BLOCKED", result.coordinator_result.next_stage)
        self.assertFalse(result.ready_for_production_execution)

    def test_exact_adapter_roles_are_preserved(self) -> None:
        result = s1wn.compose_s1wn_in_memory_h0_h1(*self.chain())
        self.assertEqual(
            (
                "s1wh.injected.contract-validator",
                "s1wh.injected.root",
                "s1wh.injected.resource",
                "s1wh.injected.authorization",
                "s1wh.injected.lock",
                "s1wh.injected.lock",
            ),
            tuple(
                item.adapter_id for item in result.coordinator_result.receipts
            ),
        )

    def test_three_input_receipts_are_digest_bound(self) -> None:
        root, resource, authorization = self.chain()
        result = s1wn.compose_s1wn_in_memory_h0_h1(
            root,
            resource,
            authorization,
        )
        self.assertEqual(root.receipt_digest, result.root_receipt_digest)
        self.assertEqual(resource.receipt_digest, result.resource_receipt_digest)
        self.assertEqual(
            authorization.receipt_digest,
            result.authorization_validation_receipt_digest,
        )
        self.assertTrue(result.cross_receipt_binding_passed)
        self.assertEqual(
            (3, 6),
            (result.input_receipt_count, result.composed_stage_count),
        )

    def test_result_is_canonical_and_deterministic(self) -> None:
        chain = self.chain()
        first = s1wn.compose_s1wn_in_memory_h0_h1(*chain)
        second = s1wn.compose_s1wn_in_memory_h0_h1(*chain)
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_RESULT_DIGEST, first.result_digest)

    def test_one_in_memory_call_and_all_production_effects_zero(self) -> None:
        result = s1wn.compose_s1wn_in_memory_h0_h1(*self.chain())
        self.assertEqual(1, result.in_memory_coordinator_call_count)
        self.assertEqual(
            (0,) * 9,
            (
                result.operating_system_probe_count,
                result.filesystem_read_count,
                result.filesystem_write_count,
                result.execution_id_freshness_check_count,
                result.authorization_instantiation_count,
                result.producer_resolution_count,
                result.producer_call_count,
                result.matrix_path_count,
                result.production_artifact_count,
            ),
        )

    def test_root_resource_digest_mismatch_fails_closed(self) -> None:
        _, resource, authorization = self.chain()
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(
                self.root_receipt(artifact="SYNTHETIC-VOLUME-D"),
                resource,
                authorization,
            )

    def test_authorization_resource_digest_mismatch_fails_closed(self) -> None:
        root, resource, _ = self.chain()
        other = hashlib.sha256(b"other-gate").hexdigest()
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(
                root,
                resource,
                self.authorization_receipt(other),
            )

    def test_failed_volume_or_resource_gate_fails_closed(self) -> None:
        bad_root = self.root_receipt(temporary="SYNTHETIC-VOLUME-D")
        bad_resource = self.resource_receipt(bad_root)
        bad_authorization = self.authorization_receipt(
            bad_resource.gate.resource_gate_digest
        )
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(
                bad_root,
                bad_resource,
                bad_authorization,
            )

        root = self.root_receipt()
        low_resource = self.resource_receipt(
            root,
            available_physical_memory_bytes=0,
        )
        low_authorization = self.authorization_receipt(
            low_resource.gate.resource_gate_digest
        )
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(
                root,
                low_resource,
                low_authorization,
            )

    def test_rejected_authorization_text_fails_closed(self) -> None:
        root, resource, _ = self.chain()
        rejected = self.authorization_receipt(
            resource.gate.resource_gate_digest,
            text="ok weiter",
        )
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(root, resource, rejected)

    def test_result_tampering_fails_closed(self) -> None:
        result = s1wn.compose_s1wn_in_memory_h0_h1(*self.chain())
        with self.assertRaises(s1wn.S1WNCompositionError):
            replace(result, authorization_instantiation_count=1)

    def test_wrong_input_and_production_entry_fail_closed(self) -> None:
        root, resource, authorization = self.chain()
        with self.assertRaises(s1wn.S1WNCompositionError):
            s1wn.compose_s1wn_in_memory_h0_h1(
                object(),
                resource,
                authorization,
            )
        with self.assertRaises(s1wn.S1WNCompositionError) as raised:
            s1wn.execute_s1wn_production_once()
        self.assertEqual(
            s1wn.S1WN_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )

    def test_module_is_runtime_free_private_and_snapshot_neutral(self) -> None:
        source = inspect.getsource(s1wn)
        for forbidden in (
            "import os",
            "from pathlib",
            "from tempfile",
            "S1WAProductionAuthorization",
            "resolve_s1wj_injected_root_mirror",
            "observe_s1wj_injected_resources",
            "validate_s1wl_injected_authorization_text",
            "open(",
            "write_text(",
            "write_bytes(",
            "_execute_s1vq_corrected_matrix",
            "SharedMCMField",
            "ReceptorContactFrame",
        ):
            self.assertNotIn(forbidden, source)
        names = {
            "S1WNReceiptCompositionResult",
            "compose_s1wn_in_memory_h0_h1",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
