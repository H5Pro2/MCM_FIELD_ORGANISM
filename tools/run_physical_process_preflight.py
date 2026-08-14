from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    OpenCVVideoFrameSource,
    prepare_independent_visual_target_plan,
    project_visual_mcm_effector_surface,
)
from tools.run_live_process_decoupling_probe import run_process_decoupled
from tools.run_physical_setup_acceptance import run_preview


CONTROL_ARMS = (
    {
        "arm_id": "ORIGINAL_EFFECT",
        "effector_input": "completed_non_neutral_field_snapshot",
        "optical_path": "open_to_passive_targets",
        "camera_return": "enabled_after_fixed_wait",
    },
    {
        "arm_id": "BLOCKED_LIGHT_PATH",
        "effector_input": "same_completed_non_neutral_field_snapshot",
        "optical_path": "physically_blocked_before_passive_targets",
        "camera_return": "enabled_after_fixed_wait",
    },
    {
        "arm_id": "NEUTRAL_OUTPUT",
        "effector_input": "completed_neutral_field_snapshot",
        "optical_path": "open_to_passive_targets",
        "camera_return": "enabled_after_fixed_wait",
    },
    {
        "arm_id": "INTERRUPTED_RETURN",
        "effector_input": "same_completed_non_neutral_field_snapshot",
        "optical_path": "open_to_passive_targets",
        "camera_return": "disabled_for_test_window",
    },
)


def build_preflight() -> dict[str, object]:
    files = {
        "physical_contract": ROOT
        / "docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md",
        "causal_contract": ROOT
        / "docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md",
        "human_acceptance_tool": ROOT / "tools/run_physical_setup_acceptance.py",
        "independent_target_presenter": ROOT
        / "tools/present_independent_visual_targets.py",
        "process_runtime": ROOT / "tools/run_live_process_decoupling_probe.py",
        "runtime_evidence": ROOT
        / "docs/forschung/070_PROZESS_ENTKOPPELTE_120S_LANGZEITSTABILITAET_LAUF_172.md",
    }
    file_checks = {name: path.is_file() for name, path in files.items()}
    interface_checks = {
        "raw_camera_source_callable": callable(OpenCVVideoFrameSource),
        "human_preview_callable": callable(run_preview),
        "field_surface_projection_callable": callable(
            project_visual_mcm_effector_surface
        ),
        "independent_target_plan_callable": callable(
            prepare_independent_visual_target_plan
        ),
        "process_runtime_callable": callable(run_process_decoupled),
    }
    component_ready = all(file_checks.values()) and all(interface_checks.values())
    return {
        "workflow_run": 173,
        "purpose": "physical_process_path_preflight",
        "file_checks": file_checks,
        "interface_checks": interface_checks,
        "control_arms": CONTROL_ARMS,
        "control_arm_ids_unique": len(
            {item["arm_id"] for item in CONTROL_ARMS}
        )
        == len(CONTROL_ARMS),
        "component_preflight_ready": component_ready,
        "physical_setup_decision": "NOT_OBSERVED",
        "camera_excludes_effector_confirmed": False,
        "passive_targets_confirmed": False,
        "optical_separation_confirmed": False,
        "closed_loop_orchestrator_present": False,
        "ready_for_causal_run": False,
        "image_analysis_performed": False,
        "image_file_written": False,
        "camera_opened": False,
        "effector_presented": False,
        "receptor_state_created": False,
        "field_advance_performed": False,
        "raw_sensor_payload_retained": False,
        "result_preprogrammed": False,
    }


def main() -> int:
    result = build_preflight()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["component_preflight_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
