from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_post_handoff_preflight import (
    audit_e1_common_probe_n2_r2_post_handoff_preflight,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_preflight import (
    audit_e1_common_probe_protected_artifacts,
)
from mcm_field_organism.e1_common_probe_real_wrappers import (
    audit_e1_common_probe_real_wrappers,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeN2R2PostHandoffPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()
        cls.wrappers = audit_e1_common_probe_real_wrappers()
        cls.resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)
        cls.protected = audit_e1_common_probe_protected_artifacts(Path(__file__).resolve().parents[1])

    def test_object_handoff_is_ready_but_execution_coordinator_is_missing(self) -> None:
        result = audit_e1_common_probe_n2_r2_post_handoff_preflight(
            self.handoff, self.wrappers, self.resources, self.protected
        )
        self.assertTrue(result.object_handoff_ready)
        self.assertFalse(result.real_execution_coordinator_implemented)
        self.assertTrue(result.real_execution_coordinator_implementation_permitted)
        self.assertFalse(result.technical_execution_ready)
        self.assertFalse(result.fixture_execution_permitted)
        self.assertEqual("KORREKTUR_REAL_EXECUTION_COORDINATOR_MISSING", result.decision)

    def test_step_plan_remains_exactly_bounded(self) -> None:
        result = audit_e1_common_probe_n2_r2_post_handoff_preflight(
            self.handoff, self.wrappers, self.resources, self.protected
        )
        self.assertEqual((1608, 1600, 3208), (
            result.planned_formation_steps,
            result.planned_probe_steps,
            result.planned_total_steps,
        ))

    def test_low_memory_cannot_become_ready(self) -> None:
        result = audit_e1_common_probe_n2_r2_post_handoff_preflight(
            self.handoff,
            self.wrappers,
            replace(self.resources, free_memory_bytes=4 * 1024**3 - 1),
            self.protected,
        )
        self.assertFalse(result.technical_execution_ready)

    def test_preflight_has_no_execution_authorization_or_write_path(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_post_handoff_preflight)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "build_e1_common_probe_fresh_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "owner_authorized",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
