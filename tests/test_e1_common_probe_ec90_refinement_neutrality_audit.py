from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_ec90_refinement_neutrality_audit import (
    E1CommonProbeEC90RefinementNeutralityAuditError,
    S1_EC90_SOURCE_FILES,
    audit_e1_common_probe_ec90_refinement_neutrality,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC90RefinementNeutralityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()

    def test_audit_localizes_the_r4_r8_blocker(self) -> None:
        result = audit_e1_common_probe_ec90_refinement_neutrality(
            self.root, self.handoffs
        )
        self.assertTrue(result.wrapper_plan_selection_refinement_neutral)
        self.assertTrue(result.adapter_call_order_refinement_neutral)
        self.assertFalse(result.converter_step_validation_refinement_neutral)
        self.assertFalse(result.receipt_step_validation_refinement_neutral)
        self.assertFalse(result.synthetic_r4_r8_route_available)
        self.assertTrue(result.generalized_extension_required)
        self.assertFalse(result.field_execution_permitted)

    def test_changed_registered_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "mcm_field_organism"
            source_root.mkdir()
            for name, _ in S1_EC90_SOURCE_FILES:
                shutil.copyfile(self.root / "mcm_field_organism" / name, source_root / name)
            changed = source_root / S1_EC90_SOURCE_FILES[2][0]
            changed.write_text(changed.read_text(encoding="utf-8") + "\n# mutation\n", encoding="utf-8")
            with self.assertRaisesRegex(
                E1CommonProbeEC90RefinementNeutralityAuditError, "source changed"
            ):
                audit_e1_common_probe_ec90_refinement_neutrality(root, self.handoffs)

    def test_audit_calls_no_wrapper_adapter_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_ec90_refinement_neutrality)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
