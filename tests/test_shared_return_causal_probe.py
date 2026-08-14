from dataclasses import replace

import pytest

from mcm_field_organism.shared_return_causal_probe import (
    run_shared_return_causal_probe,
)


def test_shared_probe_applies_one_identical_second_world_contact() -> None:
    result = run_shared_return_causal_probe()

    assert result.case_count == 14
    assert result.observation_count == 42
    assert result.second_worlds_equal_count == 14
    assert result.second_fast_states_equal_count == 28
    assert result.all_second_activations_match_contact
    assert result.all_second_afterimages_zero


def test_shared_probe_accounts_for_first_state_in_local_samples() -> None:
    result = run_shared_return_causal_probe()

    assert result.interrupted_layer_difference_count == 14
    assert result.swapped_layer_difference_count == 12
    assert result.all_local_samples_match_first_state
    assert result.deterministic_reproduction


def test_shared_snapshot_differences_are_reported_without_effector_claim() -> None:
    result = run_shared_return_causal_probe()

    assert result.interrupted_snapshot_difference_count == 14
    assert result.swapped_snapshot_difference_count == 12
    assert not result.connects_field_to_effector
    with pytest.raises(ValueError):
        replace(result, connects_field_to_effector=True)
