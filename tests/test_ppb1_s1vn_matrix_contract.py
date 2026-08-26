from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from mcm_field_organism._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_EXPECTED_BASELINE_CALLS,
    S1VN_EXPECTED_CASE_COUNT,
    S1VN_EXPECTED_PPB_CALLS,
    S1VN_EXPECTED_TOTAL_CALLS,
    S1VN_FAMILY_IDS,
    S1VN_FIXTURE_IDS,
    S1VN_MATRIX_EXECUTION_BLOCKED,
    S1VN_PARAMETER_IDS,
    S1VNMatrixError,
    advance_s1vn_baseline,
    build_s1vn_fixture,
    execute_s1vn_matrix,
    initial_s1vn_baseline_state,
    prepare_s1vn_matrix_runner,
    run_s1vn_miniature_contract,
    s1vn_config,
    s1vn_fixture_call_count,
    s1vn_matrix_plan,
    s1vn_parameter_records,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


def contract_frames(config) -> tuple[ReceptorContactFrame, ...]:
    return tuple(
        ReceptorContactFrame(
            config.modality_id,
            config.geometry_id,
            f"s1vn.contract.{config.modality_id}.{index:02d}",
            f"s1vn.contract.{config.modality_id}.clock",
            index - 1,
            index,
            config.carrier_ids,
            (value,) * len(config.carrier_ids),
        )
        for index, value in enumerate((0.2, 0.2, 0.8), start=1)
    )


class PPB1S1VNMatrixContractTests(unittest.TestCase):
    def test_parameter_records_are_exact_and_deterministic(self) -> None:
        first = s1vn_parameter_records()
        second = s1vn_parameter_records()
        self.assertEqual(S1VN_PARAMETER_IDS, tuple(first))
        self.assertEqual(first, second)
        self.assertEqual((8, 4, 512, 128), (
            first["P0"].auditory.capacity,
            first["P0"].visual.capacity,
            first["P0"].auditory.expire_after_steps,
            first["P0"].visual.expire_after_steps,
        ))
        self.assertEqual((32, 16, 2048, 512), (
            first["P2"].auditory.capacity,
            first["P2"].visual.capacity,
            first["P2"].auditory.expire_after_steps,
            first["P2"].visual.expire_after_steps,
        ))

    def test_plan_has_exactly_384_unique_paths(self) -> None:
        plan = s1vn_matrix_plan()
        self.assertEqual(S1VN_EXPECTED_CASE_COUNT, len(plan))
        self.assertEqual(len(plan), len({path.path_id for path in plan}))
        self.assertEqual(48, sum(path.family_id == "PPB1" for path in plan))
        for baseline_id in S1VN_BASELINE_IDS:
            self.assertEqual(48, sum(path.family_id == baseline_id for path in plan))

    def test_plan_cross_product_is_complete(self) -> None:
        plan = s1vn_matrix_plan()
        observed = {
            (path.family_id, path.parameter_id, path.modality_id, path.fixture_id)
            for path in plan
        }
        expected = {
            (family, parameter, modality, fixture)
            for family in S1VN_FAMILY_IDS
            for parameter in S1VN_PARAMETER_IDS
            for modality in ("auditory", "visual")
            for fixture in S1VN_FIXTURE_IDS
        }
        self.assertEqual(expected, observed)

    def test_runner_preparation_binds_exact_call_budget_without_execution(self) -> None:
        receipt = prepare_s1vn_matrix_runner()
        self.assertEqual(S1VN_EXPECTED_CASE_COUNT, receipt.case_count)
        self.assertEqual(S1VN_EXPECTED_PPB_CALLS, receipt.ppb_call_count)
        self.assertEqual(S1VN_EXPECTED_BASELINE_CALLS, receipt.baseline_call_count)
        self.assertEqual(S1VN_EXPECTED_TOTAL_CALLS, receipt.total_call_count)
        self.assertFalse(receipt.execution_authorized)
        self.assertEqual(0, receipt.accepted_call_count)
        self.assertEqual(64, len(receipt.plan_digest))

    def test_plan_and_preparation_are_deterministic(self) -> None:
        self.assertEqual(s1vn_matrix_plan(), s1vn_matrix_plan())
        self.assertEqual(prepare_s1vn_matrix_runner(), prepare_s1vn_matrix_runner())

    def test_fixture_lengths_match_all_six_configs(self) -> None:
        for parameter_id in S1VN_PARAMETER_IDS:
            for modality_id in ("auditory", "visual"):
                config = s1vn_config(parameter_id, modality_id)
                for fixture_id in S1VN_FIXTURE_IDS:
                    fixture = build_s1vn_fixture(config, fixture_id)
                    self.assertEqual(
                        s1vn_fixture_call_count(config, fixture_id), len(fixture)
                    )

    def test_fixture_values_are_dimensioned_bounded_and_clock_ordered(self) -> None:
        for modality_id in ("auditory", "visual"):
            config = s1vn_config("P0", modality_id)
            for fixture_id in S1VN_FIXTURE_IDS:
                fixture = build_s1vn_fixture(config, fixture_id)
                self.assertEqual(
                    tuple(range(1, len(fixture) + 1)),
                    tuple(frame.window_end_tick for frame in fixture),
                )
                for frame in fixture:
                    self.assertEqual(len(config.carrier_ids), len(frame.values))
                    self.assertTrue(all(0.0 <= value <= 1.0 for value in frame.values))

    def test_repetition_separation_and_conflict_anatomies_are_exact(self) -> None:
        config = s1vn_config("P0", "auditory")
        f01 = build_s1vn_fixture(config, "F01")
        self.assertEqual(1, len({frame.values for frame in f01}))
        f03 = build_s1vn_fixture(config, "F03")
        self.assertEqual(f03[0].values, f03[-2].values)
        self.assertEqual(f03[1].values, f03[-1].values)
        f04 = build_s1vn_fixture(config, "F04")
        self.assertEqual((0.2, 0.8, 0.5), tuple(frame.values[0] for frame in f04))

    def test_fill_vectors_exceed_each_bound_match_threshold(self) -> None:
        for parameter_id in S1VN_PARAMETER_IDS:
            for modality_id in ("auditory", "visual"):
                config = s1vn_config(parameter_id, modality_id)
                fixture = build_s1vn_fixture(config, "F06")
                fills = fixture[: config.capacity + 1]
                for index, left in enumerate(fills):
                    for right in fills[index + 1 :]:
                        self.assertGreater(
                            normalized_mean_l1_distance(left.values, right.values),
                            config.match_threshold,
                        )

    def test_expiry_histories_keep_filler_away_from_low_probe(self) -> None:
        config = s1vn_config("P0", "visual")
        for fixture_id in ("F07", "F08"):
            fixture = build_s1vn_fixture(config, fixture_id)
            self.assertEqual(fixture[0].values, fixture[-1].values)
            self.assertTrue(all(
                frame.values != fixture[0].values for frame in fixture[1:-1]
            ))

    def test_all_seven_baselines_advance_deterministically(self) -> None:
        config = s1vn_config("P0", "auditory")
        vectors = tuple(frame.values for frame in contract_frames(config))
        for adapter_id in S1VN_BASELINE_IDS:
            first = initial_s1vn_baseline_state(adapter_id, config)
            second = initial_s1vn_baseline_state(adapter_id, config)
            first_events = []
            second_events = []
            for vector in vectors:
                first_result = advance_s1vn_baseline(adapter_id, config, first, vector)
                second_result = advance_s1vn_baseline(adapter_id, config, second, vector)
                first, second = first_result.poststate, second_result.poststate
                first_events.append(first_result.readout.event)
                second_events.append(second_result.readout.event)
            self.assertEqual(first, second)
            self.assertEqual(first_events, second_events)

    def test_window_mean_and_exponential_trace_are_not_duplicate_adapters(self) -> None:
        config = s1vn_config("P0", "auditory")
        vectors = tuple(frame.values for frame in contract_frames(config))
        states = {}
        for adapter_id in ("B02", "B04"):
            state = initial_s1vn_baseline_state(adapter_id, config)
            for vector in vectors:
                state = advance_s1vn_baseline(
                    adapter_id, config, state, vector
                ).poststate
            states[adapter_id] = state
        self.assertNotEqual(states["B02"].trace, states["B04"].trace)

    def test_window_mean_counts_window_and_separate_trace_storage(self) -> None:
        config = s1vn_config("P0", "auditory")
        state = initial_s1vn_baseline_state("B02", config)
        vector = (0.2,) * len(config.carrier_ids)
        result = advance_s1vn_baseline("B02", config, state, vector)
        self.assertEqual(2 * len(vector), result.readout.logical_value_count)

    def test_bounded_histories_never_exceed_config_capacity(self) -> None:
        config = s1vn_config("P0", "auditory")
        vector = (0.2,) * len(config.carrier_ids)
        for adapter_id in ("B01", "B02", "B03"):
            state = initial_s1vn_baseline_state(adapter_id, config)
            for _ in range(config.capacity + 5):
                state = advance_s1vn_baseline(
                    adapter_id, config, state, vector
                ).poststate
            self.assertLessEqual(len(state.history), config.capacity)

    def test_ppb_and_baseline_miniature_wiring_accepts_only_contract_frames(self) -> None:
        config = s1vn_config("P0", "auditory")
        frames = contract_frames(config)
        for family_id in ("PPB1",) + S1VN_BASELINE_IDS:
            receipt = run_s1vn_miniature_contract(family_id, config, frames)
            self.assertEqual(3, receipt.accepted_call_count)
            self.assertEqual(3, len(receipt.events))
            self.assertEqual(3, len(receipt.observations))
            self.assertEqual(64, len(receipt.input_history_digest))
            self.assertEqual(64, len(receipt.final_state_digest))
            self.assertEqual(64, len(receipt.digest()))
        registered = build_s1vn_fixture(config, "F04")
        with self.assertRaises(S1VNMatrixError):
            run_s1vn_miniature_contract("PPB1", config, registered)

    def test_matrix_execution_is_unconditionally_blocked(self) -> None:
        with self.assertRaises(S1VNMatrixError) as caught:
            execute_s1vn_matrix()
        self.assertEqual(S1VN_MATRIX_EXECUTION_BLOCKED, caught.exception.code)

    def test_miniature_ppb_receipt_carries_bound_measurement_roles(self) -> None:
        config = s1vn_config("P0", "auditory")
        receipt = run_s1vn_miniature_contract(
            "PPB1", config, contract_frames(config)
        )
        self.assertEqual(("CREATED", "MATCHED", "CREATED"), receipt.events)
        first, second, third = receipt.observations
        self.assertEqual((1, 1, 2), (
            first.occupied_slot_count,
            second.occupied_slot_count,
            third.occupied_slot_count,
        ))
        self.assertEqual(0.0, first.selected_state_displacement)
        self.assertEqual(0.0, second.selected_state_displacement)
        self.assertEqual(0.0, third.selected_state_displacement)
        self.assertIsNotNone(second.selected_slot_id)

    def test_s1vn_roles_remain_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in (
            "s1vn_matrix_plan",
            "prepare_s1vn_matrix_runner",
            "execute_s1vn_matrix",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_s1vn_module_does_not_import_field_or_media_runtime(self) -> None:
        source = (ROOT / "mcm_field_organism" / "_ppb1_s1vn_matrix.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "shared_mcm_field",
            "neutral_local_field_substrate",
            "audio_video_neutral_field_runtime",
            "public_av_receptor_run",
            "live_audio_video_field",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
