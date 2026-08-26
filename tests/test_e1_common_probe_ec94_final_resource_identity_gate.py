from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_ec91_refinement_receipts_converters import (
    run_e1_common_probe_ec91_synthetic_fixture,
)
from mcm_field_organism.e1_common_probe_ec92_synthetic_r4_r8_coordinator import (
    run_e1_common_probe_ec92_synthetic_coordinator,
)
from mcm_field_organism.e1_common_probe_ec93_r4_r8_real_adapter_preflight import (
    build_e1_common_probe_ec93_r4_r8_real_adapter_preflight,
)
from mcm_field_organism.e1_common_probe_ec94_final_resource_identity_gate import (
    audit_e1_common_probe_ec94_final_resource_identity_gate,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_preflight import (
    audit_e1_common_probe_protected_artifacts,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC94FinalResourceIdentityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()
        cls.fixture = run_e1_common_probe_ec91_synthetic_fixture(cls.handoffs)
        cls.coordinator = run_e1_common_probe_ec92_synthetic_coordinator(
            cls.handoffs, cls.fixture
        )
        cls.preflight = build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
            cls.handoffs, cls.fixture, cls.coordinator
        )
        cls.resources = E1PilotRealResourceSnapshot(
            6 * 1024**3, 200 * 1024**3
        )
        cls.protected = audit_e1_common_probe_protected_artifacts(
            Path(__file__).resolve().parents[1]
        )

    def _audit(self, resources=None):
        return audit_e1_common_probe_ec94_final_resource_identity_gate(
            self.handoffs,
            self.coordinator,
            self.preflight,
            self.resources if resources is None else resources,
            self.protected,
        )

    def test_all_technical_gates_ready_but_owner_authorization_missing(self) -> None:
        result = self._audit()
        self.assertTrue(result.technical_execution_ready)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.coordinator_execution_permitted)
        self.assertEqual(
            "TECHNISCH_BEREIT_NEUE_R4_R8_EINMALLAUFFREIGABE_FEHLT",
            result.decision,
        )

    def test_low_memory_requires_correction(self) -> None:
        resources = replace(
            self.resources, free_memory_bytes=4 * 1024**3 - 1
        )
        result = self._audit(resources)
        self.assertFalse(result.technical_execution_ready)
        self.assertEqual("KORREKTUR_R4_R8_TECHNISCHE_GATES", result.decision)

    def test_identity_inventory_is_exact(self) -> None:
        result = self._audit()
        self.assertEqual(
            (2, 16, 16, 8, 16),
            (
                result.handoff_object_count,
                result.resolved_slot_object_count,
                result.binding_object_count,
                result.formation_slot_reference_count,
                result.fresh_field_object_count,
            ),
        )

    def test_gate_invokes_no_adapter_wrapper_field_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec94_final_resource_identity_gate
        )
        for forbidden in (
            "run_e1_common_probe_ec93_formation_receipt_adapter(",
            "run_e1_common_probe_ec93_probe_receipt_adapter(",
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
