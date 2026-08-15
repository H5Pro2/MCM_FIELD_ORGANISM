from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    CameraAcquisitionControls,
    OpenCVVideoFrameSource,
    VisualGridConfig,
)


PREVIEW_SECONDS = 30.0
STARTUP_FRAME_COUNT = 30
WINDOW_TITLE = "Lauf 125 - camera setup acceptance"

CHECKLIST = (
    "effector source is outside the camera image",
    "left and right light channels are optically separated",
    "each channel illuminates one passive matte target",
    "both targets are fully visible and spatially separated",
    "no source, channel opening, or reflection is visible",
    "camera position and targets remain fixed",
    "exposure, white balance, and focus locks were accepted",
    "ambient light and channel geometry remain fixed",
    "left/right physical provenance is documented externally",
    "external stop and neutral output remain reachable",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Show one bounded raw-camera preview for human acceptance of the "
            "physical target setup. No image is stored or analysed."
        )
    )
    parser.add_argument(
        "--camera-device",
        type=int,
        required=True,
        help="Explicit non-negative OpenCV camera device index.",
    )
    args = parser.parse_args(argv)
    if args.camera_device < 0:
        parser.error("--camera-device must be non-negative")
    return args


def decision_from_key(key: int) -> str:
    if key in (ord("a"), ord("A")):
        return "HUMAN_ACCEPTED"
    if key in (ord("r"), ord("R"), 27):
        return "HUMAN_REJECTED"
    return "NO_DECISION"


def run_preview(camera_device: int) -> dict[str, object]:
    import cv2  # type: ignore[import-not-found]

    config = VisualGridConfig()
    controls = CameraAcquisitionControls(True, True, True)
    decision = "NO_DECISION"
    preview_frames = 0
    startup_summary = None
    started = time.monotonic()

    print("Human checklist (A=accept all, R/Esc=reject):")
    for index, item in enumerate(CHECKLIST, start=1):
        print(f"{index}. {item}")

    try:
        with OpenCVVideoFrameSource(
            device_index=camera_device,
            config=config,
            startup_frame_count=STARTUP_FRAME_COUNT,
            acquisition_controls=controls,
        ) as source:
            startup_summary = source.prepare()
            while time.monotonic() - started < PREVIEW_SECONDS:
                frame = source.read_frame()
                preview_frames += 1
                cv2.imshow(WINDOW_TITLE, frame)
                decision = decision_from_key(cv2.waitKey(1) & 0xFF)
                if decision != "NO_DECISION":
                    break
    finally:
        cv2.destroyAllWindows()

    summary = None
    if startup_summary is not None:
        summary = {
            "device_index": startup_summary.device_index,
            "consumed_frames": startup_summary.consumed_frames,
            "reported_width": startup_summary.reported_width,
            "reported_height": startup_summary.reported_height,
            "reported_frames_per_second": startup_summary.reported_frames_per_second,
            "observed_frames_per_second": startup_summary.observed_frames_per_second,
            "accepted_manual_controls": list(
                startup_summary.accepted_manual_controls
            ),
        }

    return {
        "run_number": 125,
        "purpose": "physical_setup_human_acceptance",
        "decision": decision,
        "camera_device": camera_device,
        "preview_frames": preview_frames,
        "preview_limit_seconds": PREVIEW_SECONDS,
        "startup": summary,
        "image_analysis_performed": False,
        "image_file_written": False,
        "field_snapshot_loaded": False,
        "effector_presented": False,
        "receptor_state_created": False,
        "field_advance_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_preview(args.camera_device)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "HUMAN_ACCEPTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
