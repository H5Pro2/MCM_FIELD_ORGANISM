"""Small adapter checks and the five authorized existing regressions, not a study replay."""

from __future__ import annotations

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch

from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools import _visual_spatial_memory_probe as spatial


REGRESSIONS = (
    "tests.test_finite_video_path.FiniteVisualReceptorTests.test_local_channel_contact_stays_in_its_cell_and_channel",
    "tests.test_finite_video_path.FiniteVisualReceptorTests.test_equal_global_means_at_different_places_remain_distinct",
    "tests.test_finite_video_path.FiniteVisualReceptorTests.test_state_is_immutable_and_has_no_raw_or_semantic_roles",
    "tests.test_finite_video_path.FiniteVisualReceptorTests.test_invalid_frame_and_geometry_domains_are_rejected",
    "tests.test_ppb1_receptor_profiles.PPB1ReceptorProfileBindingTests.test_all_four_profiles_bind_exact_existing_geometry",
)


def sample_frame():
    return ReceptorContactFrame("visual", spatial.CONFIG.geometry_id, "unit.source", "unit.clock",
                                0, 1, spatial.CONFIG.carrier_ids, tuple(i / 32 for i in range(18)))


class SpatialAdapterTests(unittest.TestCase):
    def test_01_positional_transfer_and_explicit_ablation(self):
        frame = sample_frame()
        self.assertEqual((0.0,) * 8 + frame.values, spatial.frame_to_b4(frame, "B4_SPATIAL"))
        pooled = spatial.frame_to_b4(frame, "B4_NO_LOCATION")
        self.assertEqual(pooled[8:11] * 6, pooled[8:])
        self.assertEqual(frame.values, sample_frame().values)

    def test_02_foreign_geometry_order_and_values_fail_closed(self):
        frame = sample_frame()
        for changed in (replace(frame, geometry_id="unit.foreign"),
                        replace(frame, carrier_ids=tuple(reversed(frame.carrier_ids)))):
            with self.subTest(frame=changed.snapshot_id):
                with self.assertRaises(spatial.SpatialError):
                    spatial.frame_to_b4(changed, "B4_SPATIAL")
        for values in ((0.0,) * 17, (float("nan"),) * 18, (2.0,) * 18):
            with self.assertRaises(spatial.SpatialError):
                spatial.project_values(values, "B4_SPATIAL")
        with self.assertRaises(spatial.SpatialError):
            spatial.frame_to_b4({}, "B4_SPATIAL")

    def test_03_source_ids_cannot_supply_recognition(self):
        frame = sample_frame()
        changed = replace(frame, snapshot_id="unit.other", clock_id="unit.other.clock",
                          window_start_tick=7, window_end_tick=8)
        for condition in spatial.CONDITIONS:
            self.assertEqual(spatial.frame_to_b4(frame, condition), spatial.frame_to_b4(changed, condition))

    def test_04_storage_validation_rejects_wrong_values_and_metadata(self):
        offered = (0.25,) * 26
        payload = spatial.empty_payload()
        payload["accepted_count"] = 1
        payload["entries"][0].update(occupied=True, values=list(offered), formation_index=1)
        spatial.validate_storage(payload, offered)
        payload["entries"][0]["values"][8] = 0.5
        with self.assertRaises(spatial.SpatialError):
            spatial.validate_storage(payload, offered)
        payload["entries"][0]["values"][8] = 0.25
        payload["entries"][1]["formation_index"] = 1
        with self.assertRaises(spatial.SpatialError):
            spatial.validate_storage(payload, offered)

    def test_05_false_equivalence_is_a_result_not_an_exception(self):
        original = (0.25,) * 26
        self.assertEqual("FALSE_EQUIVALENCE", spatial.score(False, True, original, original)["classification"])
        self.assertEqual("FALSE_REJECTION", spatial.score(True, False, None, original)["classification"])
        self.assertEqual("WRONG_RETURNED_VALUES", spatial.score(True, True, (0.5,) * 26, original)["classification"])

    def test_06_incomplete_corrupt_and_reused_recording_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "unit.recording"
            log = spatial.Journal(directory)
            log.emit("unit", {"value": 1})
            log.close()
            self.assertEqual("NOT_EVALUABLE", spatial.verify_result(directory)["recording_status"])
            with self.assertRaises(FileExistsError):
                spatial.Journal(directory)
            path = directory / "record.json"
            spatial._write_new(path, spatial.seal("unit", {"value": 1}))
            self.assertEqual(1, spatial.read_sealed(path, "unit")["payload"]["value"])
            path.write_bytes(path.read_bytes().replace(b'"value":1', b'"value":2'))
            with self.assertRaises(spatial.SpatialError):
                spatial.read_sealed(path, "unit")


def run_qualification_once():
    directory = spatial.BASE / spatial.QUALIFICATION_ID
    directory.mkdir(exist_ok=False)
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(SpatialAdapterTests),
        unittest.defaultTestLoader.loadTestsFromNames(REGRESSIONS),
    ])
    source = spatial.source_manifest()
    output = io.StringIO()
    captured = []

    class RecordedResult(unittest.TextTestResult):
        def addSuccess(self, test):
            captured.append({"test": test.id(), "status": "PASS"})
            super().addSuccess(test)

        def addFailure(self, test, error):
            captured.append({"test": test.id(), "status": "FAIL", "traceback": self._exc_info_to_string(error, test)})
            super().addFailure(test, error)

        def addError(self, test, error):
            captured.append({"test": test.id(), "status": "ERROR", "traceback": self._exc_info_to_string(error, test)})
            super().addError(test, error)

    try:
        with ExitStack() as stack:
            guards = {name: stack.enter_context(patch.object(spatial.b4, name,
                side_effect=AssertionError("No B4 or matrix execution in qualification")))
                for name in ("_advance_b4", "_probe_joint_slots", "advance_s2dr_arm", "probe_s2dr_arm")}
            with redirect_stdout(output), redirect_stderr(output):
                result = unittest.TextTestRunner(stream=output, verbosity=2, failfast=True,
                    resultclass=RecordedResult).run(suite)
            calls = {name: guard.call_count for name, guard in guards.items()}
        spatial.check_sources(source)
        raw = output.getvalue().encode("utf-8")
        with (directory / "output.txt").open("xb") as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())
        successful = result.wasSuccessful() and result.testsRun == 11 and not any(calls.values())
        report = spatial.seal("qualification", {"successful": successful,
            "test_count": result.testsRun, "exit_code": 0 if successful else 1,
            "tests": captured, "blocked_operator_calls": calls,
            "output_sha256": spatial.raw_hash(raw), "source": source})
        spatial._publish(directory / "result.json", report)
        print(raw.decode(), end="")
        print("qualification_digest=" + report["digest"])
        return 0 if successful else 1
    except BaseException:
        with (directory / "failure.txt").open("x", encoding="utf-8") as stream:
            stream.write(output.getvalue() + traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(run_qualification_once())
