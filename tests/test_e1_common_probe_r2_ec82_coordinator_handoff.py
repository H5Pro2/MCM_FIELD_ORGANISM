from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec75_synthetic_route import (
    run_e1_common_probe_n2_r2_ec75_synthetic_route,
)
from mcm_field_organism.e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    build_e1_common_probe_n2_r2_ec79_static_evaluation_contract,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    S1_EC67_COORDINATOR_ID,
    S1_EC67_EC65_AUDIT_DIGEST,
    S1_EC67_EC66_FIXTURE_DIGEST,
)
from mcm_field_organism.e1_common_probe_r2_ec82_coordinator_handoff import (
    E1CommonProbeR2EC82CoordinatorHandoffError,
    S1_EC82_SOURCE_FILES,
    build_e1_common_probe_r2_ec82_coordinator_handoff_contract,
    reduce_e1_common_probe_r2_ec82_completed_result,
)
from mcm_field_organism.e1_refined_formation_runner import _digest
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeR2EC82CoordinatorHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()
        route = run_e1_common_probe_n2_r2_ec75_synthetic_route(handoff)
        values = {
            "coordinator_id": S1_EC67_COORDINATOR_ID,
            "source_handoff_digest": handoff.handoff_digest,
            "source_ec65_audit_digest": S1_EC67_EC65_AUDIT_DIGEST,
            "source_ec66_fixture_digest": S1_EC67_EC66_FIXTURE_DIGEST,
            "execution_mode": "real-wrapper",
            "roles": handoff.roles,
            "formation_state_roles": handoff.formation_state_roles,
            "formation_receipt_digests": route.formation_receipt_digests,
            "probe_receipt_digests": route.probe_receipt_digests,
            "formation_count": 4,
            "fresh_field_count": 8,
            "probe_count": 8,
            "accounted_formation_steps": 1608,
            "accounted_probe_steps": 1600,
            "accounted_total_steps": 3208,
            "actual_field_steps_executed": 3208,
            "all_state_routes_exact": True,
            "all_backreaction_routes_exact": True,
            "all_fresh_fields_identical_and_object_separate": True,
            "all_formation_states_object_separate": True,
            "preflight_and_owner_released": True,
            "persistence_performed": False,
            "research_decision_permitted": False,
            "ec46_decision_permitted": False,
            "memory_claim_permitted": False,
        }
        cls.typed_shape_fixture = E1CommonProbeN2R2RealModeCoordinatorResult(
            **values,
            result_digest=_digest(values),
            formations=route.formations,
            fresh_fields=route.fresh_fields,
            probes=route.probes,
        )
        cls.boundary = build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
            cls.root
        )

    def test_contract_binds_sources_and_remains_closed(self) -> None:
        contract = build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
            self.root
        )
        self.assertEqual(2, len(contract.source_digests))
        self.assertFalse(contract.coordinator_execution_permitted)
        self.assertFalse(contract.owner_authorization_present)

    def test_completed_typed_shape_reduces_to_ec80(self) -> None:
        contract = build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
            self.root
        )
        reduced = reduce_e1_common_probe_r2_ec82_completed_result(
            contract, self.boundary, self.typed_shape_fixture
        )
        self.assertEqual(6, len(reduced.contrast_scalars))
        self.assertEqual(
            self.typed_shape_fixture.result_digest, reduced.source_result_digest
        )
        self.assertFalse(reduced.ec46_decision_permitted)

    def test_changed_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "mcm_field_organism"
            source_root.mkdir()
            for name, _ in S1_EC82_SOURCE_FILES:
                shutil.copyfile(self.root / "mcm_field_organism" / name, source_root / name)
            changed = source_root / S1_EC82_SOURCE_FILES[1][0]
            changed.write_text(changed.read_text(encoding="utf-8") + "\n# mutation\n", encoding="utf-8")
            with self.assertRaises(E1CommonProbeR2EC82CoordinatorHandoffError):
                build_e1_common_probe_r2_ec82_coordinator_handoff_contract(root)

    def test_handoff_calls_no_coordinator_decider_or_writer(self) -> None:
        source = inspect.getsource(reduce_e1_common_probe_r2_ec82_completed_result)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
