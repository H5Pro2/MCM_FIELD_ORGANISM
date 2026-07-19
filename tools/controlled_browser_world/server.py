"""Local coordinator for a physical browser-to-camera-and-microphone test world."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
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
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OpenCVVideoFrameSource,
    SoundDeviceInputSource,
    VisualGridConfig,
    VisualWorldPhase,
    build_visual_phase_schedule,
    capture_visual_spatiotemporal_time_window,
    capture_live_audio_video_neutral_session,
    observe_marked_visual_phases,
    observe_visual_phase_local_profiles,
)
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
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


class LiveFieldABAExperimentCoordinator:
    """Coordinate the external A-B-A world with one continuous shared field."""

    def __init__(
        self,
        *,
        camera_device: int,
        audio_device: int | str,
        contract: BrowserWorldContract | None = None,
    ) -> None:
        self.camera_device = camera_device
        self.audio_device = audio_device
        self.contract = contract or replace(
            reference_browser_world_contract(),
            contract_id="browser.world.audiovisual.field-aba.v2",
            start_lead_ns=8_000_000_000,
            phases=(
                BrowserWorldPhase("rest.before", 21_000_000_000, "static", 0.0),
                BrowserWorldPhase("change", 7_000_000_000, "moving", 0.18),
                BrowserWorldPhase("rest.after", 21_000_000_000, "static", 0.0),
            ),
        )
        self.config = VisualGridConfig()
        self._lock = threading.Lock()
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
            self._status = "preparing"
            self._result = None
            self._error = None
        try:
            with OpenCVVideoFrameSource(
                device_index=self.camera_device,
                config=self.config,
                startup_frame_count=self.contract.startup_frame_count,
            ) as camera:
                summary = camera.prepare()
        except Exception:
            with self._lock:
                self._status = "failed"
            raise
        with self._lock:
            self._status = "prepared"
        return {
            "startup_frames": summary.consumed_frames,
            "reported_width": summary.reported_width,
            "reported_height": summary.reported_height,
            "reported_frames_per_second": summary.reported_frames_per_second,
        }

    def start(self) -> dict[str, object]:
        with self._lock:
            if self._status != "prepared":
                raise RuntimeError("camera must be prepared before start")
            now_monotonic = time.monotonic_ns()
            now_epoch = time.time_ns()
            anchor = now_monotonic + self.contract.start_lead_ns
            start_epoch_ns = now_epoch + self.contract.start_lead_ns
            self._status = "scheduled"
            threading.Thread(
                target=self._run,
                args=(anchor,),
                daemon=True,
            ).start()
        return _public_program_payload(
            self.contract,
            start_epoch_ns=start_epoch_ns,
        )

    def _run(self, anchor: int) -> None:
        with self._lock:
            self._status = "running"
        observations = []
        field_states = []
        try:
            second = 1_000_000_000
            if any(
                phase.duration_ns % second != 0
                for phase in self.contract.phases
            ):
                raise RuntimeError(
                    "live field A-B-A phases must contain whole-second windows"
                )
            window_count = self.contract.total_duration_ns // second
            result = capture_live_audio_video_neutral_session(
                camera_device=self.camera_device,
                audio_device=self.audio_device,
                field_config=NeutralLocalFieldSubstrateConfig(1.0),
                afterimage_config=NeutralFastAfterimageConfig(0.5),
                window_seconds=1.0,
                window_count=window_count,
                max_windows=window_count,
                camera_startup_frames=self.contract.startup_frame_count,
                window_observer=observations.append,
                field_state_observer=field_states.append,
                window_anchor_tick=anchor,
            )
            phase_summaries = []
            cursor = 0
            for phase in self.contract.phases:
                count = phase.duration_ns // second
                phase_observations = observations[cursor : cursor + count]
                cursor += count
                phase_summaries.append(
                    {
                        "phase_id": phase.phase_id,
                        "window_count": len(phase_observations),
                        "mean_activation_absolute": sum(
                            item.activation_absolute_mean
                            for item in phase_observations
                        )
                        / len(phase_observations),
                        "mean_afterimage_absolute": sum(
                            item.afterimage_absolute_mean
                            for item in phase_observations
                        )
                        / len(phase_observations),
                        "first_activation_absolute": (
                            phase_observations[0].activation_absolute_mean
                        ),
                        "last_activation_absolute": (
                            phase_observations[-1].activation_absolute_mean
                        ),
                        "first_afterimage_absolute": (
                            phase_observations[0].afterimage_absolute_mean
                        ),
                        "last_afterimage_absolute": (
                            phase_observations[-1].afterimage_absolute_mean
                        ),
                    }
                )
            before, change, after = phase_summaries

            def mean_profile(states, role: str) -> tuple[float, ...]:
                return tuple(
                    sum(float(getattr(state.layer.neurons[index], role)) for state in states)
                    / len(states)
                    for index in range(len(states[0].layer.neurons))
                )

            def mean_l1(left, right) -> float:
                return sum(
                    abs(first - second)
                    for first, second in zip(left, right, strict=True)
                ) / len(left)

            def internal_l1(states, role: str) -> float:
                profile = mean_profile(states, role)
                return sum(
                    mean_l1(
                        tuple(float(getattr(neuron, role)) for neuron in state.layer.neurons),
                        profile,
                    )
                    for state in states
                ) / len(states)

            def distances_to_profile(states, profile, role: str) -> tuple[float, ...]:
                return tuple(
                    mean_l1(
                        tuple(
                            float(getattr(neuron, role))
                            for neuron in state.layer.neurons
                        ),
                        profile,
                    )
                    for state in states
                )

            phase_state_sets = []
            cursor = 0
            for phase in self.contract.phases:
                count = phase.duration_ns // second
                phase_state_sets.append(field_states[cursor : cursor + count])
                cursor += count
            before_states, change_states, after_states = phase_state_sets
            late_before = before_states[-7:]
            late_after = after_states[-7:]
            before_activation = mean_profile(late_before, "activation")
            change_activation = mean_profile(change_states, "activation")
            after_activation = mean_profile(late_after, "activation")
            before_afterimage = mean_profile(late_before, "afterimage")
            change_afterimage = mean_profile(change_states, "afterimage")
            after_afterimage = mean_profile(late_after, "afterimage")
            before_activation_distances = distances_to_profile(
                late_before,
                before_activation,
                "activation",
            )
            change_activation_distances = distances_to_profile(
                change_states,
                before_activation,
                "activation",
            )
            after_activation_distances = distances_to_profile(
                late_after,
                before_activation,
                "activation",
            )
            before_afterimage_distances = distances_to_profile(
                late_before,
                before_afterimage,
                "afterimage",
            )
            change_afterimage_distances = distances_to_profile(
                change_states,
                before_afterimage,
                "afterimage",
            )
            after_afterimage_distances = distances_to_profile(
                late_after,
                before_afterimage,
                "afterimage",
            )

            payload = {
                "contract_digest": self.contract.digest(),
                "window_count": result.field_session.window_count,
                "source_support_count": result.field_session.source_support_count,
                "camera_frame_count": result.camera_capture_frame_count,
                "audio_overflow_count": result.audio_overflow_count,
                "checkpoint_count": result.checkpoint_count,
                "phase_summaries": phase_summaries,
                "contrasts": {
                    "change_minus_before_activation": (
                        change["mean_activation_absolute"]
                        - before["mean_activation_absolute"]
                    ),
                    "after_minus_before_activation": (
                        after["mean_activation_absolute"]
                        - before["mean_activation_absolute"]
                    ),
                    "change_minus_before_afterimage": (
                        change["mean_afterimage_absolute"]
                        - before["mean_afterimage_absolute"]
                    ),
                    "after_minus_before_afterimage": (
                        after["mean_afterimage_absolute"]
                        - before["mean_afterimage_absolute"]
                    ),
                },
                "field_profile_contrasts": {
                    "change_vs_late_before_activation_l1": mean_l1(
                        change_activation,
                        before_activation,
                    ),
                    "late_after_vs_late_before_activation_l1": mean_l1(
                        after_activation,
                        before_activation,
                    ),
                    "late_before_internal_activation_l1": internal_l1(
                        late_before,
                        "activation",
                    ),
                    "late_after_internal_activation_l1": internal_l1(
                        late_after,
                        "activation",
                    ),
                    "change_vs_late_before_afterimage_l1": mean_l1(
                        change_afterimage,
                        before_afterimage,
                    ),
                    "late_after_vs_late_before_afterimage_l1": mean_l1(
                        after_afterimage,
                        before_afterimage,
                    ),
                    "late_before_internal_afterimage_l1": internal_l1(
                        late_before,
                        "afterimage",
                    ),
                    "late_after_internal_afterimage_l1": internal_l1(
                        late_after,
                        "afterimage",
                    ),
                    "late_before_activation_distance_mean": (
                        sum(before_activation_distances)
                        / len(before_activation_distances)
                    ),
                    "change_activation_distance_mean": (
                        sum(change_activation_distances)
                        / len(change_activation_distances)
                    ),
                    "change_activation_distance_max": max(
                        change_activation_distances
                    ),
                    "late_after_activation_distance_mean": (
                        sum(after_activation_distances)
                        / len(after_activation_distances)
                    ),
                    "late_before_afterimage_distance_mean": (
                        sum(before_afterimage_distances)
                        / len(before_afterimage_distances)
                    ),
                    "change_afterimage_distance_mean": (
                        sum(change_afterimage_distances)
                        / len(change_afterimage_distances)
                    ),
                    "change_afterimage_distance_max": max(
                        change_afterimage_distances
                    ),
                    "late_after_afterimage_distance_mean": (
                        sum(after_afterimage_distances)
                        / len(after_afterimage_distances)
                    ),
                },
                "exact_baseline": {
                    "activation_max_error": max(
                        item.exact_baseline_activation_max_error
                        for item in observations
                    ),
                    "afterimage_max_error": max(
                        item.exact_baseline_afterimage_max_error
                        for item in observations
                    ),
                    "matching_digest_count": sum(
                        item.exact_baseline_digest_matches
                        for item in observations
                    ),
                },
                "raw_sensor_payload_retained": False,
                "writes_back": False,
            }
            with self._lock:
                self._result = payload
                self._status = "complete"
        except Exception as exc:
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
                self._status = "failed"


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
        coordinator: ExperimentCoordinator | LiveFieldABAExperimentCoordinator,
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
        choices=("generated", "external-media", "field-aba"),
        default="generated",
    )
    args = parser.parse_args()
    audio_device: int | str = (
        int(args.audio_device) if args.audio_device.isdigit() else args.audio_device
    )
    coordinator = (
        LiveFieldABAExperimentCoordinator(
            camera_device=args.camera_device,
            audio_device=audio_device,
        )
        if args.program == "field-aba"
        else ExperimentCoordinator(
            camera_device=args.camera_device,
            audio_device=audio_device,
            contract=(
                reference_browser_world_contract()
                if args.program == "generated"
                else reference_external_media_observation_contract()
            ),
        )
    )
    server = BrowserWorldServer((args.host, args.port), coordinator)
    print(f"http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
