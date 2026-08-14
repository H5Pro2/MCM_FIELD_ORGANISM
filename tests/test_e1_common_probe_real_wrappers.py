from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_real_wrappers import (
    audit_e1_common_probe_real_wrappers,
    build_e1_common_probe_fresh_field,
    resolve_e1_common_probe_real_slot,
    run_e1_common_probe_real_formation_wrapper,
    run_e1_common_probe_real_probe_wrapper,
)


class E1CommonProbeRealWrappersTests(unittest.TestCase):
    def test_all_private_wrappers_are_statically_present(self) -> None:
        result = audit_e1_common_probe_real_wrappers()
        self.assertTrue(result.wrappers_implemented)
        self.assertTrue(result.small_fixture_permitted)
        self.assertFalse(result.full_matrix_execution_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_wrapper_signatures_remain_narrow(self) -> None:
        self.assertEqual(5, len(inspect.signature(resolve_e1_common_probe_real_slot).parameters))
        self.assertEqual(3, len(inspect.signature(run_e1_common_probe_real_formation_wrapper).parameters))
        self.assertEqual(2, len(inspect.signature(build_e1_common_probe_fresh_field).parameters))
        self.assertEqual(3, len(inspect.signature(run_e1_common_probe_real_probe_wrapper).parameters))

    def test_audit_does_not_invoke_any_wrapper(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_real_wrappers)
        for name in (
            "resolve_e1_common_probe_real_slot(",
            "run_e1_common_probe_real_formation_wrapper(",
            "build_e1_common_probe_fresh_field(",
            "run_e1_common_probe_real_probe_wrapper(",
        ):
            self.assertNotIn(name, source)


if __name__ == "__main__":
    unittest.main()
