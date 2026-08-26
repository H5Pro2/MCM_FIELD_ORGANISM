from __future__ import annotations

from dataclasses import replace

import pytest

from mcm_field_organism.simulated_return_causal_probe import (
    run_simulated_return_causal_probe,
    run_simulated_two_step_causal_probe,
)


def test_all_four_return_arms_are_measured_from_fresh_states() -> None:
    result = run_simulated_return_causal_probe()

    assert result.case_count == 14
    assert result.observation_count == 56
    assert result.neutral_world_difference_count == 14
    assert result.interrupted_world_equality_count == 14
    assert result.interrupted_field_difference_count == 14
    assert result.swapped_world_equality_count == 14


def test_channel_swap_reports_fixed_points_instead_of_forcing_a_difference() -> None:
    result = run_simulated_return_causal_probe()

    assert result.swapped_receptor_difference_count == 12
    assert result.swapped_field_difference_count == 12
    assert result.all_afterimages_zero
    assert result.deterministic_reproduction


def test_probe_cannot_claim_a_field_to_effector_connection() -> None:
    result = run_simulated_return_causal_probe()

    assert not result.connects_field_to_effector
    with pytest.raises(ValueError):
        replace(result, connects_field_to_effector=True)


def test_two_step_probe_applies_the_same_second_world_contact() -> None:
    result = run_simulated_two_step_causal_probe()

    assert result.case_count == 14
    assert result.observation_count == 42
    assert result.second_worlds_equal_count == 14
    assert result.second_fast_states_equal_count == 28
    assert result.all_second_activations_match_contact
    assert result.all_second_afterimages_zero


def test_two_step_layer_differences_are_accounted_for_by_first_state_samples() -> None:
    result = run_simulated_two_step_causal_probe()

    assert result.interrupted_layer_difference_count == 14
    assert result.swapped_layer_difference_count == 12
    assert result.all_local_samples_match_first_state
    assert result.deterministic_reproduction
    assert not result.connects_field_to_effector
