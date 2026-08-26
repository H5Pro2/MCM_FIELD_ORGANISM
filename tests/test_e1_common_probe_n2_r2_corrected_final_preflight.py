from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_corrected_final_preflight import (
    audit_e1_common_probe_n2_r2_corrected_final_preflight,
)
from mcm_field_organism.e1_common_probe_n2_r2_source_integrity_preflight import (
    S1_EC71_EXPECTED_SOURCE_DIGESTS,
    audit_e1_common_probe_n2_r2_source_integrity,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
class E1CommonProbeN2R2CorrectedFinalPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_final_real_preflight import (
            E1CommonProbeN2R2FinalRealPreflightTests,
        )

        E1CommonProbeN2R2FinalRealPreflightTests.setUpClass()
        cls.source = E1CommonProbeN2R2FinalRealPreflightTests(
            methodName="test_all_technical_gates_ready_but_owner_release_missing"
        )
        cls.integrity = audit_e1_common_probe_n2_r2_source_integrity()

    def test_ec68_and_ec71_are_ready_but_execution_stays_blocked(self) -> None:
        result = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            self.source._audit(), self.integrity
        )

        self.assertTrue(result.technical_execution_ready)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.coordinator_execution_permitted)
        self.assertFalse(result.adapter_execution_permitted)
        self.assertFalse(result.retry_permitted)
        self.assertEqual(
            "TECHNISCH_BEREIT_QUELLGEBUNDEN_NEUE_EINMALLAUFFREIGABE_FEHLT",
            result.decision,
        )

    def test_changed_registered_source_blocks_overall_readiness(self) -> None:
        source_root = Path(__file__).resolve().parents[1] / "mcm_field_organism"
        with tempfile.TemporaryDirectory() as directory:
            target_root = Path(directory)
            for name, _ in S1_EC71_EXPECTED_SOURCE_DIGESTS:
                shutil.copyfile(source_root / name, target_root / name)
            changed = target_root / S1_EC71_EXPECTED_SOURCE_DIGESTS[1][0]
            changed.write_text(
                changed.read_text(encoding="utf-8") + "\n# synthetic mutation\n",
                encoding="utf-8",
            )
            changed_integrity = audit_e1_common_probe_n2_r2_source_integrity(
                target_root
            )

        result = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            self.source._audit(), changed_integrity
        )
        self.assertFalse(result.technical_execution_ready)
        self.assertEqual("KORREKTUR_GESAMTPREFLIGHT_GATES", result.decision)
        self.assertFalse(result.retry_permitted)

    def test_failed_ec68_resource_gate_blocks_overall_readiness(self) -> None:
        low_memory = E1PilotRealResourceSnapshot(
            4 * 1024**3 - 1,
            self.source.resources.free_disk_bytes,
        )
        result = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            self.source._audit(resources=low_memory), self.integrity
        )

        self.assertFalse(result.technical_execution_ready)
        self.assertEqual("KORREKTUR_GESAMTPREFLIGHT_GATES", result.decision)

    def test_preflight_accepts_no_release_and_calls_no_real_path(self) -> None:
        function = audit_e1_common_probe_n2_r2_corrected_final_preflight
        self.assertEqual(
            ("technical", "source_integrity"),
            tuple(inspect.signature(function).parameters),
        )
        source = inspect.getsource(function)
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
