from tools.run_physical_process_preflight import CONTROL_ARMS, build_preflight


def test_preflight_finds_components_without_claiming_physical_acceptance() -> None:
    result = build_preflight()

    assert result["component_preflight_ready"] is True
    assert result["physical_setup_decision"] == "NOT_OBSERVED"
    assert result["ready_for_causal_run"] is False
    assert result["closed_loop_coordinator_present"] is False
    assert result["camera_opened"] is False
    assert result["effector_presented"] is False
    assert result["image_analysis_performed"] is False
    assert result["raw_sensor_payload_retained"] is False


def test_preflight_preregisters_four_distinct_nonadaptive_control_arms() -> None:
    assert tuple(item["arm_id"] for item in CONTROL_ARMS) == (
        "ORIGINAL_EFFECT",
        "BLOCKED_LIGHT_PATH",
        "NEUTRAL_OUTPUT",
        "INTERRUPTED_RETURN",
    )
    assert all("expected_result" not in item for item in CONTROL_ARMS)
    assert all("reward" not in item for item in CONTROL_ARMS)
