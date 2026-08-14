from __future__ import annotations

import argparse
import json
import time


DEFAULT_DURATION_SECONDS = 15.0
WINDOW_TITLE = "OpenCV keyboard focus probe"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open one neutral OpenCV window and report whether A, R, or Esc "
            "is received. No camera, image analysis, or project runtime is used."
        )
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=DEFAULT_DURATION_SECONDS,
        help="Positive window lifetime in seconds.",
    )
    args = parser.parse_args(argv)
    if args.duration_seconds <= 0:
        parser.error("--duration-seconds must be positive")
    return args


def key_event_from_key(key: int) -> str:
    if key in (ord("a"), ord("A")):
        return "KEY_A_RECEIVED"
    if key in (ord("r"), ord("R")):
        return "KEY_R_RECEIVED"
    if key == 27:
        return "KEY_ESCAPE_RECEIVED"
    return "NO_KEY_RECEIVED"


def run_probe(duration_seconds: float) -> dict[str, object]:
    import cv2  # type: ignore[import-not-found]
    import numpy as np

    canvas = np.full((240, 640, 3), 32, dtype=np.uint8)
    cv2.putText(
        canvas,
        "Focus this window, then press A, R, or Esc",
        (24, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (230, 230, 230),
        1,
        cv2.LINE_AA,
    )

    event = "NO_KEY_RECEIVED"
    wait_iterations = 0
    started = time.monotonic()
    try:
        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.imshow(WINDOW_TITLE, canvas)
        while time.monotonic() - started < duration_seconds:
            wait_iterations += 1
            event = key_event_from_key(cv2.waitKey(10) & 0xFF)
            if event != "NO_KEY_RECEIVED":
                break
            if cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        cv2.destroyAllWindows()

    return {
        "purpose": "opencv_keyboard_focus_probe",
        "event": event,
        "duration_limit_seconds": duration_seconds,
        "elapsed_seconds": time.monotonic() - started,
        "wait_iterations": wait_iterations,
        "camera_opened": False,
        "image_analysis_performed": False,
        "image_file_written": False,
        "setup_decision_created": False,
        "effector_presented": False,
        "receptor_state_created": False,
        "field_snapshot_loaded": False,
        "field_advance_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_probe(args.duration_seconds)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["event"] != "NO_KEY_RECEIVED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
