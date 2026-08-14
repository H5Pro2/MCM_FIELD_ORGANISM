from __future__ import annotations

from mcm_field_organism.layer_payload_difference_probe import run_layer_payload_difference_probe


def test_distance_zero_layer_differences_are_openly_localized() -> None:
    result = run_layer_payload_difference_probe()

    assert len(result.comparisons) == 12
    assert result.differences_localized
    assert result.distance_zero_difference_paths
    assert result.distance_one_difference_paths == ()
    assert all(item.activation_equal for item in result.comparisons)
    assert all(item.afterimage_equal for item in result.comparisons)
    assert all(not item.layer_digest_equal for item in result.comparisons if item.gap == 0)
    assert all(item.layer_digest_equal for item in result.comparisons if item.gap == 1)
