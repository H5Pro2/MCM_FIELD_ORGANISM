from __future__ import annotations

import ast
import inspect
import textwrap
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
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC93R4R8RealAdapterPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()
        cls.fixture = run_e1_common_probe_ec91_synthetic_fixture(cls.handoffs)
        cls.coordinator = run_e1_common_probe_ec92_synthetic_coordinator(
            cls.handoffs, cls.fixture
        )

    def test_all_compatibility_checks_pass_but_execution_stays_closed(self) -> None:
        result = build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
            self.handoffs, self.fixture, self.coordinator
        )
        self.assertTrue(all(value for _, value in result.checks))
        self.assertEqual(19248, result.maximum_total_field_steps)
        self.assertTrue(result.new_owner_authorization_required)
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.real_execution_permitted)

    def test_preflight_is_deterministic(self) -> None:
        first = build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
            self.handoffs, self.fixture, self.coordinator
        )
        second = build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
            self.handoffs, self.fixture, self.coordinator
        )
        self.assertEqual(first.preflight_digest, second.preflight_digest)

    def test_preflight_does_not_call_real_adapters_or_wrappers(self) -> None:
        source = inspect.getsource(
            build_e1_common_probe_ec93_r4_r8_real_adapter_preflight
        )
        tree = ast.parse(textwrap.dedent(source))
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        for forbidden in (
            "run_e1_common_probe_ec93_formation_receipt_adapter",
            "build_e1_common_probe_ec93_fresh_field_adapter",
            "run_e1_common_probe_ec93_probe_receipt_adapter",
            "run_e1_common_probe_real_formation_wrapper",
            "run_e1_common_probe_real_probe_wrapper",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
