from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import cv2
import numpy as np

from mcm_field_organism.browser_payload_runtime import (
    bind_browser_payload_runtime,
)
from mcm_field_organism.browser_payload_timing_pair import (
    BrowserPayloadTimingInvariantDiagnostics,
    BrowserPayloadTimingPairError,
    browser_payload_timing_audio_sample_supports,
    browser_payload_timing_diagnostics_json_value,
    browser_payload_timing_pair_contracts,
    browser_payload_timing_pair_json_value,
    browser_payload_timing_pair_public_roles,
    browser_payload_timing_receptor_bridge,
    browser_payload_timing_visual_signatures,
    run_browser_payload_canonical_timing_pair,
    run_browser_payload_timing_pair,
)
from mcm_field_organism.browser_payload_smoke import (
    browser_payload_smoke_world_contract,
)
from mcm_field_organism.controlled_av_source_pair_diagnostic import (
    ControlledAVSourcePairDiagnosticError,
    controlled_av_source_pair_diagnostic_json_value,
    controlled_av_source_pair_diagnostic_public_roles,
    run_controlled_av_canonical_source_pair_diagnostic,
    run_controlled_av_source_pair_diagnostic,
)


ASSETS = Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"
CANONICAL_ASSETS = (
    Path(__file__).parents[1] / "tools" / "controlled_av_canonical_audio_world"
)


def bound_runtime(root: Path):
    installation = root / "browsers"
    installation.mkdir()
    executable = installation / "headless.exe"
    executable.write_bytes(b"bound-headless-shell")
    requirements = root / "requirements-browser.txt"
    requirements.write_text("playwright==1.62.0\n", encoding="utf-8")
    manifest = root / "browsers.json"
    manifest.write_text(
        json.dumps(
            {
                "browsers": [
                    {
                        "name": "chromium-headless-shell",
                        "revision": "1234",
                        "browserVersion": "151.0.7922.34",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return (
        bind_browser_payload_runtime(
            package_version="1.62.0",
            requirements_path=requirements,
            manifest_path=manifest,
            executable_path=executable,
            installation_root=installation,
        ),
        executable,
    )


def png_payload(value: int) -> bytes:
    rgb = np.full((80, 120, 3), value, dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not ok:
        raise AssertionError("test PNG encoding failed")
    return encoded.tobytes()


class FakeRequest:
    def __init__(self, url: str) -> None:
        self.url = url


class FakeRoute:
    def __init__(self) -> None:
        self.continued = False

    def continue_(self) -> None:
        self.continued = True

    def abort(self, error_code: str = "blockedbyclient") -> None:
        raise AssertionError(f"unexpected blocked request: {error_code}")


class FakePage:
    def __init__(
        self,
        *,
        audio_scale: float = 1.0,
        bad_audio_index: int | None = None,
        canonical_audio: bool = False,
    ) -> None:
        self.url = "about:blank"
        self.audio_scale = audio_scale
        self.bad_audio_index = bad_audio_index
        self.canonical_audio = canonical_audio
        self.route_handler = None
        self.world = None
        self.source = None
        self.visual_index = 0
        self.audio_released = False
        self.closed = False

    def route(self, url: str, handler: object) -> None:
        self.route_handler = handler

    def goto(self, url: str, **kwargs: object) -> None:
        self.url = url
        root = Path(url.removeprefix("file:///"))
        if root.drive == "":
            root = Path("/" + str(root))
        root = root.parent
        for name in ("index.html", "styles.css", "world.js"):
            route = FakeRoute()
            self.route_handler(route, FakeRequest((root / name).as_uri()))
            if not route.continued:
                raise AssertionError("local request was not continued")

    def evaluate(self, expression: str, arg: object | None = None):
        if "configureWorld" in expression:
            self.world = arg["world"]
            self.source = arg["source"]
            return None
        if "renderVisualFrame" in expression:
            self.visual_index = int(arg)
            return None
        if "renderAudio" in expression:
            return 9600
        if "readAudioChunk" in expression:
            index = int(arg)
            if self.bad_audio_index == index:
                return [0.0] * 79
            phases = self.world["phases"]
            sample_rate = self.source["audio_sample_rate"]
            hop_size = self.source["audio_hop_size"]
            frequency = self.world["tone_frequency_hz"]
            phase_samples = 2400
            values = []
            for sample in range(index * hop_size, (index + 1) * hop_size):
                phase_index = min(sample // phase_samples, len(phases) - 1)
                gain = phases[phase_index]["tone_gain"] * self.audio_scale
                wave_index = (
                    sample - phase_index * phase_samples
                    if self.canonical_audio and gain != 0.0
                    else sample
                )
                values.append(
                    gain
                    * math.sin(2.0 * math.pi * frequency * wave_index / sample_rate)
                )
            return values
        if "releaseAudio" in expression:
            self.audio_released = True
            return None
        raise AssertionError(f"unexpected evaluate expression: {expression}")

    def locator(self, selector: str):
        if selector != "canvas#world":
            raise AssertionError(selector)
        return self

    def screenshot(self, **kwargs: object) -> bytes:
        return png_payload(32 + (self.visual_index % 9) * 20)

    def close(self) -> None:
        self.closed = True


class FakeContext:
    def __init__(self, page: FakePage) -> None:
        self.page = page
        self.closed = False

    def new_page(self) -> FakePage:
        return self.page

    def close(self) -> None:
        self.closed = True


class FakeBrowser:
    def __init__(self, engine_version: str, page: FakePage) -> None:
        self.version = engine_version
        self.context = FakeContext(page)
        self.closed = False

    def new_context(self, **kwargs: object) -> FakeContext:
        return self.context

    def close(self) -> None:
        self.closed = True


class FakeChromium:
    def __init__(self, browser: FakeBrowser) -> None:
        self.browser = browser

    def launch(self, **kwargs: object) -> FakeBrowser:
        return self.browser


class FakePlaywrightManager:
    def __init__(
        self,
        engine_version: str,
        *,
        audio_scale: float = 1.0,
        bad_audio_index: int | None = None,
        canonical_audio: bool = False,
    ) -> None:
        self.page = FakePage(
            audio_scale=audio_scale,
            bad_audio_index=bad_audio_index,
            canonical_audio=canonical_audio,
        )
        self.browser = FakeBrowser(engine_version, self.page)
        self.chromium = FakeChromium(self.browser)
        self.exited = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.exited = True


def manager_factory(managers: list[FakePlaywrightManager]):
    pending = iter(managers)

    def factory() -> FakePlaywrightManager:
        return next(pending)

    return factory


class BrowserPayloadTimingPairTests(unittest.TestCase):
    def test_console_tool_imports_outside_workspace_without_starting_pair(self) -> None:
        tool = ASSETS.parent / "run_browser_payload_timing_pair.py"
        with TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import runpy,sys; runpy.run_path(sys.argv[1], "
                    "run_name='browser_payload_timing_pair_import_test')",
                    str(tool),
                ],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)

    def test_canonical_field_pair_tool_is_separate_and_loop_free(self) -> None:
        tool = ASSETS.parent / "run_browser_payload_canonical_timing_pair.py"
        with TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import runpy,sys; runpy.run_path(sys.argv[1], "
                    "run_name='canonical_field_pair_import_test')",
                    str(tool),
                ],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        source = tool.read_text(encoding="ascii")
        self.assertIn("controlled_av_canonical_audio_world", source)
        self.assertIn("run_browser_payload_canonical_timing_pair", source)
        self.assertNotIn("run_browser_payload_timing_pair(", source)
        for forbidden in ("for ", "while ", "reports/", "reports\\", "z4a_"):
            self.assertNotIn(forbidden, source)

    def test_source_diagnostic_tool_imports_without_starting_browser(self) -> None:
        tool = ASSETS.parent / "run_controlled_av_source_pair_diagnostic.py"
        with TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import runpy,sys; runpy.run_path(sys.argv[1], "
                    "run_name='controlled_av_source_diagnostic_import_test')",
                    str(tool),
                ],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        source = tool.read_text(encoding="ascii")
        for forbidden in ("for ", "while ", "reports/", "reports\\", "z4a_"):
            self.assertNotIn(forbidden, source)

    def test_canonical_source_diagnostic_tool_is_separate_and_loop_free(self) -> None:
        tool = ASSETS.parent / "run_controlled_av_canonical_source_pair_diagnostic.py"
        with TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import runpy,sys; runpy.run_path(sys.argv[1], "
                    "run_name='canonical_source_diagnostic_import_test')",
                    str(tool),
                ],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        source = tool.read_text(encoding="ascii")
        self.assertIn("controlled_av_canonical_audio_world", source)
        self.assertIn("run_controlled_av_canonical_source_pair_diagnostic", source)
        self.assertNotIn("run_controlled_av_source_pair_diagnostic(", source)
        for forbidden in ("for ", "while ", "reports/", "reports\\", "z4a_"):
            self.assertNotIn(forbidden, source)

    def test_contracts_bind_one_shift_without_changing_old_smoke(self) -> None:
        a0, c0 = browser_payload_timing_pair_contracts()
        self.assertEqual((1_200_000_000, 1_200_000_000), (
            a0.total_duration_ns,
            c0.total_duration_ns,
        ))
        self.assertEqual((0.0, 0.2, 0.0, 0.0), tuple(
            phase.tone_gain for phase in a0.phases
        ))
        self.assertEqual((0.0, 0.0, 0.2, 0.0), tuple(
            phase.tone_gain for phase in c0.phases
        ))
        self.assertEqual((36, 120), (
            browser_payload_timing_receptor_bridge(a0).expected_visual_frame_count,
            browser_payload_timing_receptor_bridge(a0).expected_audio_chunk_count,
        ))
        self.assertEqual(
            "8d896d7e55fd56c4193f3f25570a1c560fc5e1035f96f16e3f0640f8a06f7261",
            browser_payload_smoke_world_contract().digest(),
        )

    def test_static_visual_inputs_match_and_audio_support_shifts_exactly(self) -> None:
        visual_a0, visual_c0 = browser_payload_timing_visual_signatures()
        support_a0, support_c0 = browser_payload_timing_audio_sample_supports()
        self.assertEqual(visual_a0, visual_c0)
        self.assertEqual((2400, 4800), support_a0)
        self.assertEqual((4800, 7200), support_c0)
        self.assertEqual(support_a0[1] - support_a0[0], support_c0[1] - support_c0[0])
        self.assertEqual(132.0, 440.0 * 0.3)

    def test_synthetic_energy_is_equal_but_one_boundary_sample_is_detectable(self) -> None:
        sample_rate = 8000
        samples = np.arange(9600, dtype=np.float64)
        wave = np.sin(2.0 * math.pi * 440.0 * samples / sample_rate).astype(
            np.float32
        )

        def energy(start: int, end: int) -> float:
            signal = np.zeros(9600, dtype=np.float32)
            signal[start:end] = (0.2 * wave[start:end]).astype(np.float32)
            return math.fsum(float(value) * float(value) for value in signal)

        a0 = energy(2400, 4800)
        c0 = energy(4800, 7200)
        missing_boundary = energy(4800, 7199)
        self.assertLessEqual(abs(a0 - c0) / max(a0, c0), 1e-12)
        self.assertGreater(
            abs(a0 - missing_boundary) / max(a0, missing_boundary),
            1e-12,
        )

    def test_fake_pair_reaches_scalar_comparison_and_closes_both_arms(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version),
            ]
            receipt = run_browser_payload_timing_pair(
                binding,
                asset_directory=ASSETS,
                playwright_factory=manager_factory(managers),
                runtime_validator=lambda _: None,
            )

        self.assertTrue(receipt.visual_sequence_exact_match)
        self.assertLessEqual(
            receipt.audio_total_energy_relative_error,
            receipt.energy_relative_tolerance,
        )
        self.assertGreater(receipt.activation_final_l1, 0.0)
        self.assertGreater(receipt.activation_final_linf, 0.0)
        self.assertEqual(0.0, receipt.afterimage_final_linf)
        self.assertEqual(
            "TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED",
            receipt.technical_decision,
        )
        self.assertTrue(receipt.all_input_invariants_hold)
        self.assertTrue(receipt.all_lifecycle_boundaries_closed)
        self.assertTrue(all(manager.page.audio_released for manager in managers))
        self.assertTrue(all(manager.page.closed for manager in managers))
        self.assertTrue(all(manager.browser.context.closed for manager in managers))
        self.assertTrue(all(manager.browser.closed for manager in managers))
        self.assertTrue(all(manager.exited for manager in managers))
        encoded = json.dumps(browser_payload_timing_pair_json_value(receipt)).lower()
        for forbidden in ("raw_png", "raw_pcm", "receptor_values", "field_values"):
            self.assertNotIn(forbidden, encoded)

    def test_canonical_fake_pair_reaches_same_scalar_field_boundary(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version, canonical_audio=True),
                FakePlaywrightManager(binding.engine_version, canonical_audio=True),
            ]
            receipt = run_browser_payload_canonical_timing_pair(
                binding,
                asset_directory=CANONICAL_ASSETS,
                playwright_factory=manager_factory(managers),
                runtime_validator=lambda _: None,
            )

        self.assertEqual(
            "browser.payload.canonical-timing-pair.v1",
            receipt.pair_id,
        )
        self.assertTrue(receipt.visual_sequence_exact_match)
        self.assertLessEqual(
            receipt.audio_total_energy_relative_error,
            receipt.energy_relative_tolerance,
        )
        self.assertGreater(receipt.activation_final_l1, 0.0)
        self.assertGreater(receipt.activation_final_linf, 0.0)
        self.assertEqual(0.0, receipt.afterimage_final_linf)
        self.assertEqual(
            "TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED",
            receipt.technical_decision,
        )
        self.assertTrue(receipt.all_input_invariants_hold)
        self.assertTrue(receipt.all_lifecycle_boundaries_closed)
        self.assertTrue(all(manager.page.audio_released for manager in managers))
        self.assertTrue(all(manager.page.closed for manager in managers))
        self.assertTrue(all(manager.browser.context.closed for manager in managers))
        self.assertTrue(all(manager.browser.closed for manager in managers))
        self.assertTrue(all(manager.exited for manager in managers))

    def test_canonical_pair_rejects_historical_assets_before_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            called = False

            def factory():
                nonlocal called
                called = True
                raise AssertionError("factory must not run for historical assets")

            with self.assertRaisesRegex(
                BrowserPayloadTimingPairError,
                "assets differ from binding",
            ):
                run_browser_payload_canonical_timing_pair(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=factory,
                    runtime_validator=lambda _: None,
                )

        self.assertFalse(called)

    def test_source_diagnostic_matches_fair_fake_pair_without_field_handoff(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version),
            ]
            receipt = run_controlled_av_source_pair_diagnostic(
                binding,
                asset_directory=ASSETS,
                playwright_factory=manager_factory(managers),
                runtime_validator=lambda _: None,
            )

        self.assertEqual("SOURCE_INVARIANTS_MATCH", receipt.diagnostic_decision)
        self.assertEqual((), receipt.failed_invariant_roles)
        self.assertTrue(receipt.visual_sequence_exact_match)
        self.assertFalse(receipt.field_handoff_performed)
        self.assertFalse(receipt.raw_payloads_retained)
        self.assertTrue(all(manager.browser.closed for manager in managers))

    def test_canonical_source_assets_bind_one_local_segment_without_oscillator(self) -> None:
        expected = {
            "index.html": "0ceecd1e9e346ce262e8e0cb41efe52fe2f3e42e00c1d6298fdf23becc451d3b",
            "styles.css": "f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594",
            "world.js": "7e903402e16f3f11423116ab3112d452c3815fb6006ed18537963fd887c956bb",
        }
        observed = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in CANONICAL_ASSETS.iterdir()
            if path.is_file()
        }
        self.assertEqual(expected, observed)
        source = (CANONICAL_ASSETS / "world.js").read_text(encoding="ascii")
        for required in (
            "activeStart + localIndex",
            "tone_frequency_hz * localIndex",
            "OfflineAudioContext",
            "createBufferSource",
        ):
            self.assertIn(required, source)
        for forbidden in ("createOscillator", "getUserMedia", "fetch(", "WebSocket"):
            self.assertNotIn(forbidden, source)

    def test_canonical_source_pair_matches_under_fakes_without_field_handoff(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version),
            ]
            receipt = run_controlled_av_canonical_source_pair_diagnostic(
                binding,
                asset_directory=CANONICAL_ASSETS,
                playwright_factory=manager_factory(managers),
                runtime_validator=lambda _: None,
            )

        self.assertEqual(
            "controlled.av.canonical-source-pair.diagnostic.v1",
            receipt.diagnostic_id,
        )
        self.assertEqual("SOURCE_INVARIANTS_MATCH", receipt.diagnostic_decision)
        self.assertEqual((), receipt.failed_invariant_roles)
        self.assertTrue(receipt.visual_sequence_exact_match)
        self.assertLessEqual(
            receipt.audio_total_energy_relative_error,
            receipt.energy_relative_tolerance,
        )
        self.assertFalse(receipt.field_handoff_performed)
        self.assertTrue(all(manager.browser.closed for manager in managers))

    def test_source_diagnostic_returns_energy_role_for_unfair_fake_pair(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version, audio_scale=0.5),
            ]
            receipt = run_controlled_av_source_pair_diagnostic(
                binding,
                asset_directory=ASSETS,
                playwright_factory=manager_factory(managers),
                runtime_validator=lambda _: None,
            )

        self.assertEqual("SOURCE_INVARIANTS_DIFFER", receipt.diagnostic_decision)
        self.assertEqual(("audio_total_energy",), receipt.failed_invariant_roles)
        self.assertGreater(
            receipt.audio_total_energy_relative_error,
            receipt.energy_relative_tolerance,
        )
        encoded = json.dumps(
            controlled_av_source_pair_diagnostic_json_value(receipt)
        ).lower()
        for forbidden in ("raw_png", "raw_pcm", "field_snapshot", "activation"):
            self.assertNotIn(forbidden, encoded)

    def test_source_diagnostic_failure_closes_second_fake_arm(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version, bad_audio_index=4),
            ]
            with self.assertRaisesRegex(ValueError, "audio chunk"):
                run_controlled_av_source_pair_diagnostic(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=manager_factory(managers),
                    runtime_validator=lambda _: None,
                )

        self.assertTrue(all(manager.page.audio_released for manager in managers))
        self.assertTrue(all(manager.page.closed for manager in managers))
        self.assertTrue(all(manager.browser.context.closed for manager in managers))
        self.assertTrue(all(manager.browser.closed for manager in managers))
        self.assertTrue(all(manager.exited for manager in managers))

    def test_source_diagnostic_module_has_no_field_handoff_or_closed_path(self) -> None:
        roles = set(controlled_av_source_pair_diagnostic_public_roles())
        self.assertTrue(
            {"field_snapshot", "activation", "afterimage", "raw_pcm"}.isdisjoint(
                roles
            )
        )
        source = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "controlled_av_source_pair_diagnostic.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_audio_video_receptor_sequences",
            "NeutralLocalFieldSubstrateConfig",
            "z4a_",
            "reports/",
            "reports\\",
        ):
            self.assertNotIn(forbidden, source)

    def test_source_diagnostic_runtime_drift_stops_before_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binding, executable = bound_runtime(Path(directory))
            executable.write_bytes(b"drift")
            called = False

            def factory():
                nonlocal called
                called = True
                raise AssertionError("factory must not be called after drift")

            with self.assertRaisesRegex(
                ControlledAVSourcePairDiagnosticError,
                "size changed",
            ):
                run_controlled_av_source_pair_diagnostic(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=factory,
                    runtime_validator=lambda _: None,
                )
        self.assertFalse(called)

    def test_energy_mismatch_rejects_pair_after_closing_both_arms(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version, audio_scale=0.5),
            ]
            with self.assertRaisesRegex(
                BrowserPayloadTimingPairError,
                "input invariants failed: audio_total_energy",
            ) as raised:
                run_browser_payload_timing_pair(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=manager_factory(managers),
                    runtime_validator=lambda _: None,
                )

        diagnostics = raised.exception.diagnostics
        self.assertIsInstance(diagnostics, BrowserPayloadTimingInvariantDiagnostics)
        self.assertEqual(("audio_total_energy",), diagnostics.failed_invariant_roles)
        self.assertGreater(
            diagnostics.audio_total_energy_relative_error,
            diagnostics.energy_relative_tolerance,
        )
        encoded = json.dumps(
            browser_payload_timing_diagnostics_json_value(diagnostics)
        ).lower()
        self.assertNotIn("samples", encoded)
        self.assertTrue(all(manager.browser.closed for manager in managers))
        self.assertTrue(all(manager.exited for manager in managers))

    def test_second_arm_capture_failure_closes_every_created_resource(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            managers = [
                FakePlaywrightManager(binding.engine_version),
                FakePlaywrightManager(binding.engine_version, bad_audio_index=3),
            ]
            with self.assertRaisesRegex(ValueError, "audio chunk"):
                run_browser_payload_timing_pair(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=manager_factory(managers),
                    runtime_validator=lambda _: None,
                )

        self.assertTrue(all(manager.page.audio_released for manager in managers))
        self.assertTrue(all(manager.page.closed for manager in managers))
        self.assertTrue(all(manager.browser.context.closed for manager in managers))
        self.assertTrue(all(manager.browser.closed for manager in managers))
        self.assertTrue(all(manager.exited for manager in managers))

    def test_runtime_drift_stops_before_fake_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binding, executable = bound_runtime(Path(directory))
            executable.write_bytes(b"drift")
            called = False

            def factory():
                nonlocal called
                called = True
                raise AssertionError("factory must not be called after drift")

            with self.assertRaisesRegex(
                BrowserPayloadTimingPairError,
                "size changed",
            ):
                run_browser_payload_timing_pair(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=factory,
                    runtime_validator=lambda _: None,
                )
        self.assertFalse(called)

    def test_public_roles_and_module_have_no_raw_or_closed_path(self) -> None:
        roles = set(browser_payload_timing_pair_public_roles())
        self.assertTrue(
            {"raw_png", "raw_pcm", "receptor_values", "field_values"}.isdisjoint(
                roles
            )
        )
        source = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "browser_payload_timing_pair.py"
        ).read_text(encoding="ascii")
        for forbidden in ("z4a_", "reports/", "reports\\"):
            self.assertNotIn(forbidden, source)
        tool = (
            Path(__file__).parents[1]
            / "tools"
            / "run_browser_payload_timing_pair.py"
        ).read_text(encoding="ascii")
        for forbidden in ("z4a_", "reports/", "reports\\", "for ", "while "):
            self.assertNotIn(forbidden, tool)


if __name__ == "__main__":
    unittest.main()
