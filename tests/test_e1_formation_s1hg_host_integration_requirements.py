from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1hf_five_component_total_preflight as fixture

from mcm_field_organism.e1_formation_s1hg_host_integration_requirements import (
    E1FormationS1HGHostIntegrationRequirementsError,
    S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS,
    S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS,
    S1_HG_REQUIRED_HOST_OPERATIONS,
    audit_e1_formation_s1hg_host_integration_requirements,
)


class E1FormationS1HGHostIntegrationRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = fixture.E1FormationS1HFFiveComponentTotalPreflightTests
        source.setUpClass()
        cls.preflight = source()._audit()

    def _audit(self):
        return audit_e1_formation_s1hg_host_integration_requirements(
            self.preflight
        )

    def test_all_ten_host_requirement_checks_pass(self) -> None:
        contract = self._audit()
        self.assertEqual(10, len(contract.checks))
        self.assertTrue(all(value for _, value in contract.checks))
        self.assertEqual(
            self.preflight.preflight_digest,
            contract.source_s1hf_preflight_digest,
        )

    def test_event_and_capability_schemas_bind_exact_route(self) -> None:
        contract = self._audit()
        self.assertEqual(
            S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS,
            contract.required_external_event_fields,
        )
        self.assertEqual(
            S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS,
            contract.required_host_capability_fields,
        )
        for field_name in (
            "source_external_event_digest",
            "authorization_digest",
            "run_id",
            "gate_digest",
            "binding_digest",
            "batch_index",
            "carrier_digest",
            "kernel_entrypoint_id",
        ):
            self.assertIn(field_name, contract.required_host_capability_fields)

    def test_host_operations_preserve_atomic_order(self) -> None:
        contract = self._audit()
        self.assertEqual(
            S1_HG_REQUIRED_HOST_OPERATIONS,
            contract.required_host_operations,
        )
        consume = contract.required_host_operations.index(
            "consume-capability-inside-host-owned-kernel-boundary"
        )
        kernel = contract.required_host_operations.index(
            "perform-exactly-one-production-kernel-call-and-one-field-step"
        )
        self.assertEqual(consume + 1, kernel)

    def test_external_provider_and_execution_remain_absent(self) -> None:
        contract = self._audit()
        self.assertFalse(contract.external_host_provider_present)
        self.assertFalse(contract.authenticated_origin_verifier_connected)
        self.assertFalse(contract.host_capability_factory_connected)
        self.assertFalse(contract.production_kernel_boundary_connected)
        self.assertFalse(contract.host_capability_issued)
        self.assertFalse(contract.authorization_request_ready)
        self.assertFalse(contract.execution_permitted)
        self.assertEqual((0, 0), (
            contract.adapter_calls,
            contract.field_steps_executed,
        ))

    def test_opening_host_or_execution_flags_fails_closed(self) -> None:
        contract = self._audit()
        for field_name in (
            "external_host_provider_present",
            "authenticated_origin_verifier_connected",
            "host_capability_factory_connected",
            "production_kernel_boundary_connected",
            "host_capability_issued",
            "authorization_request_ready",
            "execution_permitted",
        ):
            with self.assertRaises(
                E1FormationS1HGHostIntegrationRequirementsError
            ):
                replace(contract, **{field_name: True})

    def test_audit_calls_no_sensitive_path_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1hg_host_integration_requirements
        )
        for forbidden in (
            "bind_e1_formation_s1hb_external_owner_authorization(",
            "issue_e1_formation_s1hc_real_single_use_token(",
            "_seal_e1_formation_s1hd_real_adapter_call_receipt(",
            "run_e1_formation_s1he_gated_single_batch_adapter_synthetically(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
