from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_chain_composition import (
    E1ConfirmationChainCompositionError,
    compose_synthetic_e1_confirmation_chain,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)
from mcm_field_organism.e1_refined_world_formation_contract import (
    S1_DS_REQUIRED_CONTROLS,
)
from tests.test_e1_confirmation_seven_arm_probe import _inputs, _run


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _chain_inputs():
    corridor, formation, source, plans = _inputs()
    probes = tuple(
        _run(corridor, formed, source, plan)
        for formed, plan in zip(
            formation.refinements,
            plans.plans,
            strict=True,
        )
    )
    contract = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)
    return contract, formation, probes


class E1ConfirmationChainCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.formation, cls.probes = _chain_inputs()

    def test_composition_builds_ordered_r2_r4_r8_result(self) -> None:
        result = compose_synthetic_e1_confirmation_chain(
            self.contract,
            self.formation,
            self.probes,
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            item.refinement_id for item in result.refinements
        ))
        self.assertEqual(13, len(result.metrics))
        self.assertEqual(11, len(result.controls))
        self.assertIn(result.technical_decision, {
            "TECHNICALLY_INVALID",
            "NO_CONFIRMED_REFINED_EFFECT",
            "CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
            "NUMERICALLY_UNDECIDABLE",
        })

    def test_all_synthetic_chain_controls_are_exact(self) -> None:
        result = compose_synthetic_e1_confirmation_chain(
            self.contract,
            self.formation,
            self.probes,
        )
        metrics = dict(result.metrics)

        self.assertTrue(all(dict(result.controls).values()))
        for role in (
            "identity_residual",
            "formation_ablation_residual",
            "probe_ablation_residual",
            "fixed_adapter_residual",
            "resource_budget_error",
        ):
            self.assertEqual(0.0, metrics[role])
        self.assertEqual(
            S1_DS_REQUIRED_CONTROLS,
            tuple(role for role, _ in result.controls),
        )

    def test_current_synthetic_fixture_is_bound_without_a_claim(self) -> None:
        result = compose_synthetic_e1_confirmation_chain(
            self.contract,
            self.formation,
            self.probes,
        )

        self.assertEqual("NUMERICALLY_UNDECIDABLE", result.technical_decision)
        self.assertEqual(
            "ff98c96b2ccecd0a23e1ba02ce1bf8827d672aae72953b9e04d18c9062ad510c",
            result.result_digest,
        )
        self.assertEqual(0.0, result.refinements[-1].d_probe_s)
        self.assertEqual(0.0, result.refinements[-1].d_probe_h)

    def test_mismatched_probe_order_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationChainCompositionError,
            "matching ordered",
        ):
            compose_synthetic_e1_confirmation_chain(
                self.contract,
                self.formation,
                tuple(reversed(self.probes)),
            )

    def test_changed_probe_source_inventory_fails_closed(self) -> None:
        changed = copy.deepcopy(self.probes[0])
        object.__setattr__(changed, "probe_source_digest", "0" * 64)

        with self.assertRaisesRegex(
            E1ConfirmationChainCompositionError,
            "source or plan inventory",
        ):
            compose_synthetic_e1_confirmation_chain(
                self.contract,
                self.formation,
                (changed, self.probes[1], self.probes[2]),
            )

    def test_composition_is_repeatable_and_keeps_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = compose_synthetic_e1_confirmation_chain(
            self.contract,
            self.formation,
            self.probes,
        )
        second = compose_synthetic_e1_confirmation_chain(
            self.contract,
            self.formation,
            self.probes,
        )

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_composition_has_no_runtime_persistence_and_remains_private(self) -> None:
        source = inspect.getsource(compose_synthetic_e1_confirmation_chain)
        for forbidden in (
            "run_e1_asynchronous_field",
            "run_synthetic_e1_confirmation_seven_arm_probe",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1ConfirmationChainCompositionError",
            "compose_synthetic_e1_confirmation_chain",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
