from __future__ import annotations

import copy
import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_positive_step_coordinator_fixture import (
    E1CommonProbeN2R2PositiveStepCoordinatorFixtureError,
    run_e1_common_probe_n2_r2_positive_step_coordinator_fixture,
)
from mcm_field_organism.e1_common_probe_n2_r2_positive_step_receipt_contract import (
    build_e1_common_probe_n2_r2_positive_step_receipt_fixture,
)
from mcm_field_organism.e1_common_probe_real_wrappers import E1CommonProbeFreshField
from mcm_field_organism.e1_refined_chain_canonical_producer import _initial_field_digest
from tests.test_e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoffTests


class E1CommonProbeN2R2PositiveStepCoordinatorFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()
        cls.receipts = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(cls.handoff)

    def _kernels(self):
        formations = {item.state_role: item for item in self.receipts.formations}
        probes = {item.role_id: item for item in self.receipts.probes}
        calls = {"formation": [], "fresh": [], "probe": []}

        def formation(slot, initial_field, initial_state):
            calls["formation"].append((slot, initial_field, initial_state))
            return formations[slot.binding.state_role]

        def fresh(binding, initial_field):
            result = E1CommonProbeFreshField(
                binding.binding_digest,
                _initial_field_digest(initial_field),
                copy.deepcopy(initial_field),
            )
            calls["fresh"].append((binding, initial_field, result))
            return result

        def probe(slot, fresh_field, formation_receipt):
            calls["probe"].append((slot, fresh_field, formation_receipt))
            return probes[slot.binding.role_id]

        return formation, fresh, probe, calls

    def test_exact_positive_step_coordination_without_real_execution(self) -> None:
        formation, fresh, probe, calls = self._kernels()
        result = run_e1_common_probe_n2_r2_positive_step_coordinator_fixture(
            self.handoff,
            source_ec63_fixture_digest=self.receipts.result_digest,
            formation_kernel=formation,
            fresh_field_kernel=fresh,
            probe_kernel=probe,
        )
        self.assertEqual((4, 8, 8), tuple(len(calls[key]) for key in ("formation", "fresh", "probe")))
        self.assertEqual((1608, 1600, 3208), (
            result.accounted_formation_steps,
            result.accounted_probe_steps,
            result.accounted_total_steps,
        ))
        self.assertEqual(0, result.actual_field_steps_executed)
        self.assertFalse(result.real_adapter_execution_permitted)

    def test_p0_and_e1_receipts_are_routed_by_role(self) -> None:
        formation, fresh, probe, calls = self._kernels()
        result = run_e1_common_probe_n2_r2_positive_step_coordinator_fixture(
            self.handoff,
            source_ec63_fixture_digest=self.receipts.result_digest,
            formation_kernel=formation,
            fresh_field_kernel=fresh,
            probe_kernel=probe,
        )
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_backreaction_routes_exact)
        self.assertIsNone(calls["probe"][0][2])
        self.assertIsNone(calls["probe"][1][2])
        self.assertEqual("active-ab", calls["probe"][2][2].state_role)

    def test_untyped_formation_kernel_fails_closed(self) -> None:
        _, fresh, probe, _ = self._kernels()
        with self.assertRaises(E1CommonProbeN2R2PositiveStepCoordinatorFixtureError):
            run_e1_common_probe_n2_r2_positive_step_coordinator_fixture(
                self.handoff,
                source_ec63_fixture_digest=self.receipts.result_digest,
                formation_kernel=lambda *args: None,
                fresh_field_kernel=fresh,
                probe_kernel=probe,
            )

    def test_fixture_has_no_ec65_adapter_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_n2_r2_positive_step_coordinator_fixture)
        for forbidden in (
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "build_e1_common_probe_real_fresh_field_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
