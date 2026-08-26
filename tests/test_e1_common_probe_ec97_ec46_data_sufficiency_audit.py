from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from mcm_field_organism.e1_common_probe_ec97_ec46_data_sufficiency_audit import (
    E1CommonProbeEC97EC46DataSufficiencyAuditError,
    S1_EC97_REQUIRED_VECTOR_INPUTS,
    audit_e1_common_probe_ec97_ec46_data_sufficiency,
)


class E1CommonProbeEC97EC46DataSufficiencyAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.contract = build_e1_common_probe_acceptance_contract()

    def test_scalars_exist_but_all_required_vectors_are_missing(self) -> None:
        result = audit_e1_common_probe_ec97_ec46_data_sufficiency(
            self.root, self.contract
        )
        self.assertEqual(("r2", "r4", "r8"), tuple(x[0] for x in result.available_active_scalars))
        self.assertEqual((), result.available_vector_inputs)
        self.assertEqual(S1_EC97_REQUIRED_VECTOR_INPUTS, result.missing_vector_inputs)
        self.assertFalse(result.exact_coarse_distance_computable)
        self.assertFalse(result.exact_fine_distance_computable)
        self.assertFalse(result.ec46_decision_computable)
        self.assertEqual("STOP_EC46_RAW_ORDER_VECTORS_NOT_RETAINED", result.decision)

    def test_scalar_norm_differences_cannot_be_enabled_as_substitute(self) -> None:
        result = audit_e1_common_probe_ec97_ec46_data_sufficiency(
            self.root, self.contract
        )
        with self.assertRaises(E1CommonProbeEC97EC46DataSufficiencyAuditError):
            replace(
                result,
                scalar_norm_differences_are_valid_vector_distance_substitutes=True,
            )

    def test_audit_has_no_decider_field_or_write_call(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec97_ec46_data_sufficiency
        )
        for forbidden in (
            "decide_common_probe_evidence(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
