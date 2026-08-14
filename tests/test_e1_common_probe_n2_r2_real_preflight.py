from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_real_preflight import audit_e1_common_probe_n2_r2_real_preflight, audit_e1_common_probe_protected_artifacts
from mcm_field_organism.e1_common_probe_n2_r2_runner_fixture import run_e1_common_probe_n2_r2_runner_fixture
from mcm_field_organism.e1_common_probe_real_binding_contract import build_e1_common_probe_real_binding_contract
from mcm_field_organism.e1_common_probe_real_wrappers import audit_e1_common_probe_real_wrappers
from mcm_field_organism.e1_common_probe_small_real_result_audit import audit_e1_common_probe_small_real_result
from mcm_field_organism.e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot


class E1CommonProbeN2R2RealPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_e1_common_probe_real_binding_contract()
        cls.wrappers = audit_e1_common_probe_real_wrappers()
        cls.audit = audit_e1_common_probe_small_real_result()
        cls.fixture = run_e1_common_probe_n2_r2_runner_fixture(cls.contract, cls.audit)
        cls.resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)
        cls.protected = audit_e1_common_probe_protected_artifacts(Path(__file__).resolve().parents[1])

    def test_real_execution_adapter_is_still_missing(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_preflight(self.contract, self.wrappers, self.audit, self.fixture, self.resources, self.protected)
        self.assertFalse(result.technical_execution_ready)
        self.assertFalse(result.real_execution_adapter_implemented)
        self.assertTrue(result.real_execution_adapter_implementation_permitted)
        self.assertFalse(result.fixture_execution_permitted)
        self.assertEqual("KORREKTUR_REAL_EXECUTION_ADAPTER_MISSING", result.decision)

    def test_low_memory_requires_correction(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_preflight(self.contract, self.wrappers, self.audit, self.fixture, replace(self.resources, free_memory_bytes=4 * 1024**3 - 1), self.protected)
        self.assertFalse(result.technical_execution_ready)
        self.assertEqual("KORREKTUR_REAL_EXECUTION_ADAPTER_MISSING", result.decision)

    def test_preflight_does_not_execute_or_accept_authorization(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_real_preflight)
        for forbidden in ("run_e1_common_probe_real_formation_wrapper", "run_e1_common_probe_real_probe_wrapper", "owner_authorized", "write_text", "write_bytes", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
