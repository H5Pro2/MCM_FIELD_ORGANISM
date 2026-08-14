from __future__ import annotations

import pytest

from mcm_field_organism.contact_reproduction_probe import run_contact_reproduction


@pytest.mark.parametrize(
    ("research_id", "combination_count", "unequal_layer_count"),
    (("032", 5, 0), ("033", 25, 4), ("034", 11, 0), ("035", 75, 12), ("036", 70, 11), ("037", 70, 11), ("038", 220, 37), ("039", 370, 49)),
)
def test_contact_study_reproduces_against_fresh_null_baselines(research_id: str, combination_count: int, unequal_layer_count: int) -> None:
    result = run_contact_reproduction(research_id)

    assert result.combination_count == combination_count
    assert result.max_activation_error == 0.0
    assert result.max_afterimage_error == 0.0
    assert result.unequal_layer_digest_count == unequal_layer_count
    assert result.all_probe_activations_expected
    assert result.all_afterimages_zero
    assert result.deterministic_reproduction
