from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_formation_runner import (
    run_synthetic_e1_confirmation_formation,
)
from mcm_field_organism.e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from mcm_field_organism.e1_confirmation_seven_arm_probe import (
    E1ConfirmationSevenArmProbeError,
    run_synthetic_e1_confirmation_seven_arm_probe,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
from tests.test_e1_a0_av_history_producer import contract, field, source


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _probe_sequences():
    histories = source().history_ab
    return tuple(
        ReceptorTimeSequence(
            item.modality_id,
            item.geometry_id,
            item.clock_id,
            (item.frames[0],),
        )
        for item in histories
    )


def _inputs():
    corridor = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)
    permutation = source()
    history_ab = build_e1_confirmation_refinement_plans(
        corridor,
        permutation.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    history_ba = build_e1_confirmation_refinement_plans(
        corridor,
        permutation.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    initial = field()
    formation = run_synthetic_e1_confirmation_formation(
        corridor,
        permutation,
        history_ab,
        history_ba,
        initial,
        build_neutral_e1_state(initial.layer, contract()),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )
    probe = _probe_sequences()
    probe_plans = build_e1_confirmation_refinement_plans(
        corridor,
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    return corridor, formation, probe, probe_plans


def _run(corridor, formed, probe, plan):
    return run_synthetic_e1_confirmation_seven_arm_probe(
        corridor,
        formed,
        field,
        probe,
        plan,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class E1ConfirmationSevenArmProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corridor, cls.formation, cls.probe, cls.plans = _inputs()

    def test_all_r2_r4_r8_probes_preserve_exact_controls(self) -> None:
        results = tuple(
            _run(self.corridor, formed, self.probe, plan)
            for formed, plan in zip(
                self.formation.refinements,
                self.plans.plans,
                strict=True,
            )
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            item.refinement_id for item in results
        ))
        for result in results:
            self.assertEqual(7, len(result.field_digests))
            self.assertEqual(0.0, result.probe_ablation_residual)
            self.assertEqual(0.0, result.fixed_adapter_residual)
            self.assertEqual(
                result.pre_probe_ab_state_digest,
                result.post_probe_ab_state_digest,
            )
            self.assertEqual(
                result.pre_probe_ba_state_digest,
                result.post_probe_ba_state_digest,
            )
            self.assertTrue(result.supports_assigned_once)

    def test_probe_is_repeatable(self) -> None:
        first = _run(
            self.corridor,
            self.formation.refinements[0],
            self.probe,
            self.plans.plans[0],
        )
        second = _run(
            self.corridor,
            self.formation.refinements[0],
            self.probe,
            self.plans.plans[0],
        )

        self.assertEqual(first, second)

    def test_nonseparate_fields_fail_before_probe(self) -> None:
        shared = field()
        with self.assertRaisesRegex(
            E1ConfirmationSevenArmProbeError,
            "object-separated",
        ):
            run_synthetic_e1_confirmation_seven_arm_probe(
                self.corridor,
                self.formation.refinements[0],
                lambda: shared,
                self.probe,
                self.plans.plans[0],
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_mismatched_refinement_fails_before_probe(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationSevenArmProbeError,
            "do not match",
        ):
            _run(
                self.corridor,
                self.formation.refinements[0],
                self.probe,
                self.plans.plans[1],
            )

    def test_canonical_probe_source_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationSevenArmProbeError,
            "rejects the canonical",
        ):
            _run(
                self.corridor,
                self.formation.refinements[0],
                _fixed_probe_sequences(),
                self.plans.plans[0],
            )

    def test_changed_contract_is_rejected(self) -> None:
        changed = copy.deepcopy(self.corridor)
        object.__setattr__(changed, "corridor_status", "CHANGED")
        with self.assertRaisesRegex(
            E1ConfirmationSevenArmProbeError,
            "current S1-EB contract",
        ):
            _run(
                changed,
                self.formation.refinements[0],
                self.probe,
                self.plans.plans[0],
            )

    def test_probe_keeps_registered_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        _run(
            self.corridor,
            self.formation.refinements[0],
            self.probe,
            self.plans.plans[0],
        )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_probe_has_no_decision_persistence_and_remains_private(self) -> None:
        source_text = inspect.getsource(
            run_synthetic_e1_confirmation_seven_arm_probe
        )
        for forbidden in (
            "build_e1_confirmation_chain_result",
            "technical_decision",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source_text)
        for role in (
            "E1ConfirmationProbeResult",
            "run_synthetic_e1_confirmation_seven_arm_probe",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
