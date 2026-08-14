from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_final_real_preflight import (
    audit_e1_common_probe_n2_r2_final_real_preflight,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_call_adapters import (
    audit_e1_common_probe_n2_r2_real_call_adapters,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    audit_e1_common_probe_n2_r2_real_mode_coordinator,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_preflight import (
    audit_e1_common_probe_protected_artifacts,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from tests.test_e1_common_probe_n2_r2_positive_step_coordinator_fixture import (
    E1CommonProbeN2R2PositiveStepCoordinatorFixtureTests,
)


class E1CommonProbeN2R2FinalRealPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2PositiveStepCoordinatorFixtureTests
        source.setUpClass()
        test = source(methodName="test_exact_positive_step_coordination_without_real_execution")
        formation, fresh, probe, _ = test._kernels()
        from mcm_field_organism.e1_common_probe_n2_r2_positive_step_coordinator_fixture import run_e1_common_probe_n2_r2_positive_step_coordinator_fixture
        cls.handoff = source.handoff
        cls.synthetic = run_e1_common_probe_n2_r2_positive_step_coordinator_fixture(
            cls.handoff,
            source_ec63_fixture_digest=source.receipts.result_digest,
            formation_kernel=formation,
            fresh_field_kernel=fresh,
            probe_kernel=probe,
        )
        cls.adapters = audit_e1_common_probe_n2_r2_real_call_adapters()
        cls.real = audit_e1_common_probe_n2_r2_real_mode_coordinator()
        cls.resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)
        cls.protected = audit_e1_common_probe_protected_artifacts(Path(__file__).resolve().parents[1])

    def _audit(self, resources=None):
        return audit_e1_common_probe_n2_r2_final_real_preflight(
            self.handoff,
            self.adapters,
            self.synthetic,
            self.real,
            self.resources if resources is None else resources,
            self.protected,
        )

    def test_all_technical_gates_ready_but_owner_release_missing(self) -> None:
        result = self._audit()
        self.assertTrue(result.technical_execution_ready)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.coordinator_execution_permitted)
        self.assertFalse(result.adapter_execution_permitted)
        self.assertEqual("TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT", result.decision)

    def test_low_memory_requires_technical_correction(self) -> None:
        result = self._audit(replace(self.resources, free_memory_bytes=4 * 1024**3 - 1))
        self.assertFalse(result.technical_execution_ready)
        self.assertEqual("KORREKTUR_TECHNISCHE_GATES", result.decision)

    def test_preflight_does_not_accept_authorization_or_invoke_real_path(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_final_real_preflight)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "build_e1_common_probe_real_fresh_field_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "owner_authorized",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
