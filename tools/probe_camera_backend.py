"""Probe one OpenCV camera backend in an externally bounded process."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import cv2


def run_single(backend_name: str, device: int) -> None:
    backend = cv2.CAP_DSHOW if backend_name == "dshow" else cv2.CAP_MSMF
    started_at = time.monotonic()
    capture = cv2.VideoCapture(device, backend)
    try:
        opened = bool(capture.isOpened())
        read_ok = False
        shape = None
        if opened:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            capture.set(cv2.CAP_PROP_FPS, 30)
            read_ok, frame = capture.read()
            if read_ok and frame is not None:
                shape = list(frame.shape)
        print(json.dumps({
            "backend": backend_name,
            "device": device,
            "opened": opened,
            "read_ok": bool(read_ok),
            "shape": shape,
            "seconds": round(time.monotonic() - started_at, 3),
        }))
    finally:
        capture.release()


def run_supervised(timeout: float) -> None:
    script = str(Path(__file__).resolve())
    for backend_name in ("dshow", "msmf"):
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    script,
                    "--backend",
                    backend_name,
                    "--device",
                    "0",
                ],
                capture_output=True,
                check=False,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            print(json.dumps({
                "backend": backend_name,
                "device": 0,
                "timeout": True,
                "seconds": timeout,
            }))
            continue
        if completed.stdout.strip():
            print(completed.stdout.strip())
        elif completed.stderr.strip():
            print(json.dumps({
                "backend": backend_name,
                "device": 0,
                "error": completed.stderr.strip(),
                "exit_code": completed.returncode,
            }))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("dshow", "msmf"))
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--supervise", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    if args.supervise:
        run_supervised(args.timeout)
        return
    if args.backend is None:
        parser.error("--backend is required without --supervise")
    run_single(args.backend, args.device)


if __name__ == "__main__":
    main()
