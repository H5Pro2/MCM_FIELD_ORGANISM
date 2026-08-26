from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ln_b3_pih_resource_anatomy_contract import (
    DTS1S1LNResourceAnatomyContractError,
    S1_LN_CASE_ID,
    S1_LN_DECISION,
    S1_LN_EDGE_BALANCE_RULES,
    S1_LN_EDGE_ROLES,
    S1_LN_FORBIDDEN_CLAIMS,
    S1_LN_FORBIDDEN_STATES,
    S1_LN_GLOBAL_BALANCE_RULES,
    S1_LN_LOCAL_LEDGERS,
    S1_LN_NODE_CAPACITIES,
    S1_LN_ROLE_DEFINITIONS,
    S1_LN_SOURCE_S1HI_CONTRACT_DIGEST,
    S1_LN_STRUCTURAL_DISTINCTIONS,
    S1_LN_GEOMETRY,
    build_dts1_s1ln_b3_pih_resource_anatomy_contract,
    _derive_local_ledgers,
    _almost_zero,
)
from mcm_field_organism.dynamic_substrate_s1hh_function_falsification_contract import (
    S1_HH_CANDIDATE_ID,
    S1_HH_DECISION,
)
from mcm_field_organism.dynamic_substrate_s1lm_b3_pih_case_selection_contract import (
    S1_LM_TARGET_CASE_RECORD,
    S1_LM_SEQUENCE_RECORD,
    S1_LM_TARGET_REPLICA_IDS,
    build_dts1_s1lm_b3_pih_case_selection_contract,
    S1_LM_CASE_ID,
    S1_LM_DECISION,
    S1_LM_SEQUENCE_KEY,
)


class DTS1S1LNResourceAnatomyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1ln_b3_pih_resource_anatomy_contract()

    def test_s1_ln_builds_from_s1lm_and_s1hi_binding(self) -> None:
        s1lm = build_dts1_s1lm_b3_pih_case_selection_contract()
        self.assertEqual(S1_LM_CASE_ID, S1_LN_CASE_ID)
        self.assertEqual("B3", self.contract.candidate_baseline)
        self.assertEqual("P_IH_ATTENUATION", self.contract.candidate_profile)
        self.assertEqual(S1_LM_SEQUENCE_KEY, self.contract.source_s1lm_sequence_key)
        self.assertEqual(s1lm.contract_digest, self.contract.source_s1lm_contract_digest)
        self.assertEqual(self.contract.source_s1hi_contract_digest, S1_LN_SOURCE_S1HI_CONTRACT_DIGEST)
        self.assertEqual(S1_LM_DECISION, self.contract.source_s1lm_decision)
        self.assertEqual(S1_LM_TARGET_CASE_RECORD, self.contract.reference_case_record)
        self.assertEqual(S1_LM_SEQUENCE_RECORD, self.contract.reference_sequence)
        self.assertEqual(S1_LM_TARGET_REPLICA_IDS, self.contract.reference_replica_ids)
        self.assertEqual(self.contract.decision, S1_LN_DECISION)

    def test_binds_local_roles_and_identity_as_derived_ledger(self) -> None:
        self.assertEqual((("node-a", 0.5), ("node-b", 0.5)), S1_LN_NODE_CAPACITIES)
        self.assertEqual((("node-a", "node-b", 0.2, 0.1),), S1_LN_EDGE_ROLES)
        ledgers = S1_LN_LOCAL_LEDGERS
        self.assertEqual(2, len(ledgers))
        ledgers_by_node = {node: ledger for node, *ledger in ledgers}
        node_a = ledgers_by_node["node-a"]
        node_b = ledgers_by_node["node-b"]
        self.assertAlmostEqual(0.5, node_a[0], places=12)
        self.assertAlmostEqual(0.35, node_a[1], places=12)
        self.assertAlmostEqual(0.1, node_a[2], places=12)
        self.assertAlmostEqual(0.05, node_a[3], places=12)
        self.assertAlmostEqual(0.5, node_b[0], places=12)
        self.assertAlmostEqual(0.35, node_b[1], places=12)
        self.assertAlmostEqual(0.1, node_b[2], places=12)
        self.assertAlmostEqual(0.05, node_b[3], places=12)
        self.assertTrue(_almost_zero(self.contract.global_balance_gap(), tolerance=1e-12))

    def test_global_and_local_conservation_rules_are_declared(self) -> None:
        self.assertEqual(
            (
                "edge roles are stored as conductive-bound and refractory per canonical edge",
                "each endpoint gets half of incident conductive-bound and half of incident refractory",
                "free is derived per node as capacity minus half-share incident roles",
                "role accounting is per-edge and per-endpoint explicit",
            ),
            S1_LN_EDGE_BALANCE_RULES,
        )
        self.assertEqual(
            (
                "global capacity = sum(node capacities)",
                "global accounted = sum(derived free + all stored edge roles)",
                "global residual must be zero",
            ),
            S1_LN_GLOBAL_BALANCE_RULES,
        )
        self.assertEqual(
            (
                "free: node-local residual capacity after incident edge roles",
                "conductive-bound: explicit edge role that can alter local coupling",
                "refractory: explicit edge role not immediately available for engagement",
            ),
            S1_LN_ROLE_DEFINITIONS,
        )

    def test_bindings_reject_dynamic_and_execution_paths(self) -> None:
        self.assertEqual(
            ("fixed-adapter", "gain", "fast-afterimage", "integrator", "replay"),
            tuple(name for name, _ in self.contract.structural_distinctions),
        )
        self.assertFalse(self.contract.equation_selected)
        self.assertFalse(self.contract.parameters_selected)
        self.assertFalse(self.contract.runtime_implemented)
        self.assertFalse(self.contract.field_coupling_selected)
        self.assertFalse(self.contract.dynamic_functional_effect_selected)
        self.assertFalse(self.contract.execution_permitted)
        self.assertFalse(self.contract.claims_permitted)
        self.assertEqual(0, self.contract.field_steps_executed)

    def test_forbidden_claims_states_and_resources(self) -> None:
        self.assertIn("memory", self.contract.forbidden_claims)
        self.assertIn("consciousness", self.contract.forbidden_claims)
        self.assertIn("feeling", self.contract.forbidden_claims)
        self.assertIn("fixed-adapter", tuple(name for name, _ in self.contract.structural_distinctions))
        self.assertIn("empty-or-duplicate-node-inventory", S1_LN_FORBIDDEN_STATES)

    def test_can_derive_ledger_and_reject_invalid_anatomy(self) -> None:
        self.assertEqual(
            _derive_local_ledgers(S1_LN_NODE_CAPACITIES, S1_LN_EDGE_ROLES),
            S1_LN_LOCAL_LEDGERS,
        )
        with self.assertRaises(DTS1S1LNResourceAnatomyContractError):
            _derive_local_ledgers((("a", -0.2), ("b", 0.2)), (("a", "b", 0.0, 0.0)))
        with self.assertRaises(DTS1S1LNResourceAnatomyContractError):
            _derive_local_ledgers((("a", 1.0),), (("a", "a", 0.0, 0.0),))
        with self.assertRaises(DTS1S1LNResourceAnatomyContractError):
            _derive_local_ledgers(
                (("a", 0.2), ("b", 0.2)),
                (("a", "b", 1.0, 0.0),),
            )

    def test_is_deterministic_tamper_evident_and_no_runtime_invocation(self) -> None:
        first = build_dts1_s1ln_b3_pih_resource_anatomy_contract()
        second = build_dts1_s1ln_b3_pih_resource_anatomy_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LNResourceAnatomyContractError):
            replace(first, claims_permitted=True)
        source = inspect.getsource(build_dts1_s1ln_b3_pih_resource_anatomy_contract)
        for forbidden in (
            "run_",
            "execute_",
            "start_",
            "adapter_",
            "runner",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_metadata_links_back_to_s1hh_candidate(self) -> None:
        self.assertEqual(S1_HH_CANDIDATE_ID, self.contract.candidate_id)
        self.assertEqual(S1_HH_DECISION, S1_HH_DECISION)
        self.assertEqual(S1_LN_GEOMETRY, self.contract.candidate_geometry)
        self.assertEqual(
            "B3_PIH_C10_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION",
            self.contract.source_s1lm_decision,
        )
        self.assertEqual(S1_LN_FORBIDDEN_CLAIMS, self.contract.forbidden_claims)
        self.assertEqual(S1_LN_STRUCTURAL_DISTINCTIONS, self.contract.structural_distinctions)

    def test_dataclass_field_set_is_minimal_and_static(self) -> None:
        dataclass_names = tuple(f.name for f in fields(self.contract.__class__))
        self.assertIn("contract_id", dataclass_names)
        self.assertIn("node_capacity_records", dataclass_names)
        self.assertIn("edge_resource_roles", dataclass_names)
        self.assertIn("contract_digest", dataclass_names)


if __name__ == "__main__":
    unittest.main()
