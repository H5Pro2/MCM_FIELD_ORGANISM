from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    prepare_e1_formation_s1fi_inputs,
)
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import (
    build_e1_formation_s1fj_synthetic_inventory,
)
from mcm_field_organism.e1_formation_s1fp_common_probe_contract import (
    audit_e1_formation_s1fp_common_probe_contract,
)
from mcm_field_organism.e1_formation_s1fq_synthetic_common_probe_coordinator import (
    coordinate_e1_formation_s1fq_synthetically,
)
from mcm_field_organism.e1_formation_s1fr_static_resource_matrix_audit import (
    audit_e1_formation_s1fr_static_resources_and_matrix,
)
from mcm_field_organism.e1_formation_s1fs_fresh_chain_one_shot_contract import (
    prepare_e1_formation_s1fs_fresh_chain_one_shot_contract,
)
from mcm_field_organism.e1_formation_s1ft_synthetic_fresh_chain_preflight import (
    E1FormationS1FTSyntheticFreshChainPreflightError,
    build_e1_formation_s1ft_synthetic_resource_snapshot,
    prepare_e1_formation_s1ft_synthetic_objects,
    preflight_e1_formation_s1ft_synthetically,
)


class E1FormationS1FTSyntheticFreshChainPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.probe_contract = audit_e1_formation_s1fp_common_probe_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        inventory = build_e1_formation_s1fj_synthetic_inventory(cls.inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(
            cls.probe_contract, inventory
        )
        cls.audit = audit_e1_formation_s1fr_static_resources_and_matrix(
            cls.probe_contract, integration
        )
        cls.contract = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            cls.audit
        )
        cls.chain, cls.schema = prepare_e1_formation_s1ft_synthetic_objects(
            cls.contract, cls.audit, cls.probe_contract, cls.inputs
        )

    def test_complete_synthetic_preflight_passes_without_execution(self) -> None:
        resources = build_e1_formation_s1ft_synthetic_resource_snapshot()
        result = preflight_e1_formation_s1ft_synthetically(
            self.contract, self.audit, self.chain, resources, self.schema
        )
        self.assertTrue(result.synthetic_preflight_passed)
        self.assertEqual((6, 30), (
            result.formation_input_count,
            result.probe_slot_count,
        ))
        self.assertEqual((45, 28_000), (
            result.planned_field_call_count,
            result.planned_field_steps,
        ))
        self.assertFalse(result.real_runner_implemented)
        self.assertFalse(result.execution_permitted)
        self.assertEqual(0, self.schema.field_steps_executed)

    def test_low_synthetic_memory_fails_closed(self) -> None:
        resources = build_e1_formation_s1ft_synthetic_resource_snapshot(
            3 * 1024**3
        )
        result = preflight_e1_formation_s1ft_synthetically(
            self.contract, self.audit, self.chain, resources, self.schema
        )
        self.assertFalse(result.synthetic_preflight_passed)
        self.assertEqual(
            "SYNTHETIC_FRESH_CHAIN_PREFLIGHT_FAILED_CLOSED",
            result.decision,
        )
        self.assertFalse(result.execution_permitted)

    def test_probe_slot_or_return_schema_tampering_is_rejected(self) -> None:
        with self.assertRaises(E1FormationS1FTSyntheticFreshChainPreflightError):
            replace(self.chain, probe_slots=self.chain.probe_slots[:-1])
        with self.assertRaises(E1FormationS1FTSyntheticFreshChainPreflightError):
            replace(self.schema, observed_values_present=True)

    def test_preflight_is_deterministic_and_tamper_evident(self) -> None:
        resources = build_e1_formation_s1ft_synthetic_resource_snapshot()
        first = preflight_e1_formation_s1ft_synthetically(
            self.contract, self.audit, self.chain, resources, self.schema
        )
        second = preflight_e1_formation_s1ft_synthetically(
            self.contract, self.audit, self.chain, resources, self.schema
        )
        self.assertEqual(first.preflight_digest, second.preflight_digest)
        with self.assertRaises(E1FormationS1FTSyntheticFreshChainPreflightError):
            replace(first, execution_permitted=True)

    def test_preflight_calls_no_field_runner_resource_reader_or_writer(self) -> None:
        source = inspect.getsource(preflight_e1_formation_s1ft_synthetically)
        for forbidden in (
            "run_e1_formation_s1fl_once(",
            "run_small_five_arm_formation_in_memory(",
            "read_e1_formation_s1fi_resource_snapshot(",
            "advance_neutral_fast_shared_field_transient(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
