"""Local coordinator for a physical browser-to-camera-and-microphone test world."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import threading
import time
from typing import Any
from urllib.parse import urlparse

from mcm_field_organism import (
    AuditoryProbeConfig,
    BroadbandHearingPath,
    LogSpectralConfig,
    LogSpectralReceptor,
    OpenCVVideoFrameSource,
    SoundDeviceInputSource,
    VisualGridConfig,
    VisualWorldPhase,
    build_visual_phase_schedule,
    capture_visual_spatiotemporal_time_window,
    observe_marked_visual_phases,
    observe_visual_phase_local_profiles,
)
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    reference_browser_world_contract,
)
from mcm_field_organism.external_media_observation_contract import (
    ExternalMediaObservationContract,
    reference_external_media_observation_contract,
)


ASSET_ROOT = Path(__file__).resolve().parent
ObservationContract = BrowserWorldContract | ExternalMediaObservationContract


def _phase_id_at(tick: int, schedule: tuple[Any, ...]) -> str | None:
    for phase in schedule:
        if phase.window_start_tick <= tick < phase.window_end_tick:
            return phase.phase_id
    return None


def _public_program_payload(
    contract: ObservationContract,
    *,
    start_epoch_ns: int,
) -> dict[str, object]:
    phases = []
    for phase in contract.phases:
        item: dict[str, object] = {
            "phase_id": phase.phase_id,
            "duration_ms": phase.duration_ns / 1_000_000,
        }
        if isinstance(contract, BrowserWorldContract):
            item["visual_mode"] = phase.visual_mode
            item["tone_gain"] = phase.tone_gain
        else:
            item["media_contact"] = phase.media_contact
        phases.append(item)

    payload: dict[str, object] = {
        "contract_id": contract.contract_id,
        "contract_digest": contract.digest(),
        "start_epoch_ms": start_epoch_ns / 1_000_000,
        "phases": phases,
    }
    if isinstance(contract, BrowserWorldContract):
        payload["movement_cycles"] = contract.movement_cycles
        payload["tone_frequency_hz"] = contract.tone_frequency_hz
    return payload


class ExperimentCoordinator:
    def __init__(
        self,
        *,
        camera_device: int,
        audio_device: int | str,
        contract: ObservationContract | None = None,
    ) -> None:
        self.camera_device = camera_device
        self.audio_device = audio_device
        self.contract = contract or reference_browser_world_contract()
        self.config = VisualGridConfig()
        self._lock = threading.Lock()
        self._camera: OpenCVVideoFrameSource | None = None
        self._status = "idle"
        self._result: dict[str, object] | None = None
        self._error: str | None = None

    def status_payload(self) -> dict[str, object]:
        with self._lock:
            return {
                "status": self._status,
                "error": self._error,
                "result": self._result,
                "contract_digest": self.contract.digest(),
            }

    def prepare(self) -> dict[str, object]:
        with self._lock:
            if self._status not in {"idle", "complete", "failed"}:
                raise RuntimeError(f"cannot prepare while status is {self._status}")
            stale_camera = self._camera
            self._camera = None
            self._status = "preparing"
            self._result = None
            self._error = None

        if stale_camera is not None:
            stale_camera.__exit__(None, None, None)

        camera = OpenCVVideoFrameSource(
            device_index=self.camera_device,
            config=self.config,
            startup_frame_count=self.contract.startup_frame_count,
        )
        try:
            camera.__enter__()
            summary = camera.prepare()
        except Exception:
            camera.__exit__(None, None, None)
            with self._lock:
                self._status = "failed"
            raise

        with self._lock:
            self._camera = camera
            self._status = "prepared"
        return {
            "startup_frames": summary.consumed_frames,
            "reported_width": summary.reported_width,
            "reported_height": summary.reported_height,
            "reported_frames_per_second": summary.reported_frames_per_second,
        }

    def start(self) -> dict[str, object]:
        with self._lock:
            if self._status != "prepared" or self._camera is None:
                raise RuntimeError("camera must be prepared before start")
            now_monotonic = time.monotonic_ns()
            now_epoch = time.time_ns()
            anchor = now_monotonic + self.contract.start_lead_ns
            start_epoch_ns = now_epoch + self.contract.start_lead_ns
            self._status = "scheduled"
            camera = self._camera
            worker = threading.Thread(
                target=self._run,
                args=(camera, anchor),
                daemon=True,
            )
            worker.start()

        return _public_program_payload(
            self.contract,
            start_epoch_ns=start_epoch_ns,
        )

    def _run(self, camera: OpenCVVideoFrameSource, anchor: int) -> None:
        contract = self.contract
        schedule = build_visual_phase_schedule(
            clock_id="organism.monotonic_ns",
            anchor_tick=anchor,
            phases=tuple(
                VisualWorldPhase(phase.phase_id, phase.duration_ns)
                for phase in contract.phases
            ),
        )
        with self._lock:
            self._status = "running"

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                video_future = executor.submit(
                    self._capture_video,
                    camera,
                    anchor,
                    schedule,
                )
                audio_future = executor.submit(
                    self._capture_audio,
                    anchor,
                    schedule,
                    contract,
                )
                video_result = video_future.result()
                audio_result = audio_future.result()
            result = {
                "contract_digest": contract.digest(),
                "visual": video_result,
                "auditory": audio_result,
            }
            with self._lock:
                self._result = result
                self._status = "complete"
        except Exception as exc:
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
                self._status = "failed"
        finally:
            camera.__exit__(None, None, None)
            with self._lock:
                self._camera = None

    def _capture_video(
        self,
        camera: OpenCVVideoFrameSource,
        anchor: int,
        schedule: tuple[Any, ...],
    ) -> dict[str, object]:
        remaining = (anchor - time.monotonic_ns()) / 1_000_000_000
        if remaining > 0:
            time.sleep(remaining)
        probe = capture_visual_spatiotemporal_time_window(
            camera,
            self.config,
            window_start_tick=anchor,
            window_end_tick=schedule[-1].window_end_tick,
            clock=time.monotonic_ns,
            clock_id="organism.monotonic_ns",
            max_frame_count=max(
                300,
                math.ceil(
                    self.contract.total_duration_ns
                    / 1_000_000_000
                    * self.config.frames_per_second
                    * 1.25
                ),
            ),
        )
        marked = observe_marked_visual_phases(
            probe,
            clock_id="organism.monotonic_ns",
            phases=schedule,
        )
        profiles = observe_visual_phase_local_profiles(probe, marked)
        return {
            "captured_frames": len(probe.ticks),
            "boundary_frames": marked.boundary_frame_count,
            "outside_schedule_frames": marked.outside_schedule_frame_count,
            "global_summaries": [
                {
                    "phase_id": item.phase_id,
                    "frame_count": item.frame_count,
                    "mean_absolute_receptor_change": (
                        item.mean_absolute_receptor_change
                    ),
                    "mean_absolute_local_activation_difference": (
                        item.mean_absolute_local_activation_difference
                    ),
                }
                for item in marked.summaries
            ],
            "local_profiles": [
                {
                    "phase_id": profile.phase_id,
                    "neuron_count": len(profile.values),
                }
                for profile in profiles
            ],
        }

    def _capture_audio(
        self,
        anchor: int,
        schedule: tuple[Any, ...],
        contract: ObservationContract,
    ) -> dict[str, object]:
        source_config = AuditoryProbeConfig(sample_rate=48000, frame_size=480)
        receptor_config = LogSpectralConfig()
        path = BroadbandHearingPath(LogSpectralReceptor(receptor_config))
        totals = {
            phase.phase_id: {
                "state_count": 0,
                "total_energy": 0.0,
                "active_state_count": 0,
            }
            for phase in contract.phases
        }

        with SoundDeviceInputSource(
            device=self.audio_device,
            config=source_config,
        ) as source:
            while time.monotonic_ns() < anchor:
                source.read_frame()
            while True:
                start = time.monotonic_ns()
                if start >= schedule[-1].window_end_tick:
                    break
                samples = source.read_frame()
                end = time.monotonic_ns()
                state = path.push(samples)
                if state is None:
                    continue
                phase_id = _phase_id_at((start + end) // 2, schedule)
                if phase_id is None:
                    continue
                bucket = totals[phase_id]
                energy = sum(state.energy)
                bucket["state_count"] += 1
                bucket["total_energy"] += energy
                bucket["active_state_count"] += int(energy != 0.0)

            overflow_count = source.overflow_count

        summaries = []
        for phase in contract.phases:
            bucket = totals[phase.phase_id]
            count = int(bucket["state_count"])
            summaries.append(
                {
                    "phase_id": phase.phase_id,
                    "state_count": count,
                    "mean_total_receptor_energy": (
                        float(bucket["total_energy"]) / count if count else 0.0
                    ),
                    "active_state_count": int(bucket["active_state_count"]),
                }
            )
        return {
            "band_count": receptor_config.band_count,
            "overflow_count": overflow_count,
            "phase_summaries": summaries,
        }


class BrowserWorldHandler(BaseHTTPRequestHandler):
    server_version = "MCMControlledBrowserWorld/1"

    @property
    def coordinator(self) -> ExperimentCoordinator:
        return self.server.coordinator  # type: ignore[attr-defined]

    def _json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _asset(self, name: str, content_type: str) -> None:
        path = ASSET_ROOT / name
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._asset("index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            self._asset("styles.css", "text/css; charset=utf-8")
        elif path == "/stimulus.js":
            self._asset("stimulus.js", "text/javascript; charset=utf-8")
        elif path == "/api/status":
            self._json(self.coordinator.status_payload())
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/prepare":
                self._json(self.coordinator.prepare())
            elif path == "/api/start":
                self._json(self.coordinator.start())
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._json(
                {"error": f"{type(exc).__name__}: {exc}"},
                HTTPStatus.CONFLICT,
            )

    def log_message(self, format: str, *args: object) -> None:
        return


class BrowserWorldServer(ThreadingHTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        coordinator: ExperimentCoordinator,
    ) -> None:
        super().__init__(address, BrowserWorldHandler)
        self.coordinator = coordinator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--camera-device", type=int, default=0)
    parser.add_argument("--audio-device", required=True)
    parser.add_argument(
        "--program",
        choices=("generated", "external-media"),
        default="generated",
    )
    args = parser.parse_args()
    audio_device: int | str = (
        int(args.audio_device) if args.audio_device.isdigit() else args.audio_device
    )
    coordinator = ExperimentCoordinator(
        camera_device=args.camera_device,
        audio_device=audio_device,
        contract=(
            reference_browser_world_contract()
            if args.program == "generated"
            else reference_external_media_observation_contract()
        ),
    )
    server = BrowserWorldServer((args.host, args.port), coordinator)
    print(f"http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
