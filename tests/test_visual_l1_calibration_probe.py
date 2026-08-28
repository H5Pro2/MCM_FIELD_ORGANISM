"""Eight small qualification tests; no confirmation images or bank formations."""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import io
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch

from tools import _visual_l1_calibration_probe as calibration


s = calibration.spatial


def sample_records():
    original = [0.0] * 8 + [0.3] * 18
    frame = {"values": [0.31] * 18}
    image = s.seal("unit_image", {"frame": frame})
    state = s.empty_payload()
    state["accepted_count"] = 1
    state["entries"][0].update(occupied=True, values=original, formation_index=1)
    formation = s.seal("unit_formation", {"poststate": state, "offered": original, "owner": "unit.owner"})
    offered = [0.0] * 8 + frame["values"]
    distances = calibration.recorded_distances(offered, original)
    payload = {"rule": "L1-KAL", "owner": "unit.owner", "input_digest": image["digest"],
        "formation_digest": formation["digest"], "offered": offered,
        "prestate": copy.deepcopy(state), "poststate": copy.deepcopy(state),
        "state_digest": s.b4._digest(state), "visual_threshold": float(calibration.CALIBRATED),
        "auditory_threshold": 0.2, "distances": distances, "recognized": True,
        "selected": [max(distances), sum(distances), -1, "b4.slot.000", original, *distances],
        "returned": original, "score": s.score(True, True, original, original),
        "costs": calibration.PROBE_COSTS}
    return payload, image, formation


class CalibrationTests(unittest.TestCase):
    def test_01_development_only_exact_fraction_and_fail_closed(self):
        rows = [{"distances": [0.0, 8/255], "score": {"expected_recognized": True}} for _ in range(12)]
        rows += [{"distances": [0.0, 128/765], "score": {"expected_recognized": False}} for _ in range(12)]
        with patch.object(calibration, "recipe", side_effect=AssertionError("no confirmation access")):
            finding = calibration.calibration_from_development(rows)
        self.assertEqual(44/765, finding["visual_threshold"])
        self.assertFalse(finding["confirmation_used"])
        rows[0]["distances"][1] = 0.3
        with self.assertRaises(s.SpatialError):
            calibration.calibration_from_development(rows)

    def test_02_exact_threshold_and_inclusive_boundary(self):
        stored = (0.0,) * 26
        slots = (("unit.slot", stored, 1),)
        boundary = (0.0,) * 8 + (44/765,) * 18
        self.assertIsNotNone(calibration.calibrated_probe(slots, boundary, 44/765))
        above = (0.0,) * 8 + (44/765 + 0.0001,) * 18
        self.assertIsNone(calibration.calibrated_probe(slots, above, 44/765))
        for threshold in (0.0575, 0.05751634, float("nan")):
            with self.assertRaises(s.SpatialError):
                calibration.calibrated_probe(slots, boundary, threshold)

    def test_03_old_rule_parity_including_ties_and_auditory_limit(self):
        stored = (0.0,) * 26
        slots = (("unit.b", stored, 1), ("unit.c", stored, 2), ("unit.a", stored, 2))
        for auditory, visual in ((0.0, 0.0), (0.2, 0.2), (0.0, 0.25), (0.3, 0.0)):
            values = (auditory,) * 8 + (visual,) * 18
            self.assertEqual(s.b4._probe_joint_slots(slots, values),
                             calibration.calibrated_probe(slots, values, 0.2))
        self.assertEqual("unit.a", calibration.calibrated_probe(slots, stored, 0.2)[3])

    def test_04_readonly_inputs_and_stored_not_probe_return(self):
        stored = (0.0,) * 8 + (0.3,) * 18
        values = (0.0,) * 8 + (0.31,) * 18
        slots = (("unit.slot", stored, 1),)
        before = copy.deepcopy((slots, values))
        for threshold in (0.2, 44/765):
            selected = calibration.calibrated_probe(slots, values, threshold)
            self.assertEqual(stored, selected[4])
            self.assertNotEqual(values, selected[4])
        self.assertEqual(before, (slots, values))

    def test_05_record_binding_mutations_and_operator_free_validation(self):
        payload, image, formation = sample_records()
        with patch.object(s.b4, "_probe_joint_slots", side_effect=AssertionError("record only")), \
             patch.object(calibration, "calibrated_probe", side_effect=AssertionError("record only")):
            calibration.validate_probe(payload, image, formation, "L1-KAL", True)
            for key, value in (("owner", "foreign"), ("input_digest", "foreign"),
                               ("formation_digest", "foreign"), ("visual_threshold", 0.0575),
                               ("state_digest", "foreign"), ("distances", [0.0, 0.7])):
                changed = copy.deepcopy(payload)
                changed[key] = value
                with self.assertRaises(s.SpatialError):
                    calibration.validate_probe(changed, image, formation, "L1-KAL", True)
            changed = copy.deepcopy(payload)
            changed["poststate"]["entries"][0]["values"][8] = 0.4
            with self.assertRaises(s.SpatialError):
                calibration.validate_probe(changed, image, formation, "L1-KAL", True)

    def test_06_false_decisions_and_wrong_return_remain_recorded(self):
        payload, image, formation = sample_records()
        payload["score"] = s.score(False, True, payload["returned"], formation["payload"]["offered"])
        calibration.validate_probe(payload, image, formation, "L1-KAL", False)
        self.assertEqual("FALSE_EQUIVALENCE", payload["score"]["classification"])
        self.assertEqual("FALSE_REJECTION", s.score(True, False, None, (0.0,) * 26)["classification"])
        payload["returned"] = [0.0] * 26
        payload["score"] = s.score(True, True, payload["returned"], formation["payload"]["offered"])
        calibration.validate_probe(payload, image, formation, "L1-KAL", True)
        self.assertEqual("WRONG_RETURNED_VALUES", payload["score"]["classification"])

    def test_07_corrupt_incomplete_and_reused_recording_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "unit"
            journal = s.Journal(directory)
            journal.emit("unit_start", {"owner": "unit"})
            journal.emit("unit", {"owner": "unit"})
            journal.close()
            records = s.read_records(directory)
            self.assertEqual(1, len(list(calibration.checked_pairs(records))))
            with self.assertRaises(FileExistsError):
                s.Journal(directory)
            with self.assertRaises(s.SpatialError):
                list(calibration.checked_pairs(records[:1]))
            records[1]["payload"]["owner"] = "foreign"
            with self.assertRaises(s.SpatialError):
                list(calibration.checked_pairs(records))
            self.assertEqual("NOT_EVALUABLE", calibration.verify_result(directory)["recording_status"])

    def test_08_source_binding_and_closed_legacy_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            raw = b"unit-source\n"
            (directory / "unit.txt").write_bytes(raw)
            source = {"sources": [{"path": "unit.txt", "sha256": s.raw_hash(raw),
                                    "bytes_base64": "dW5pdC1zb3VyY2UK"}]}
            with patch.object(s, "ROOT", directory):
                s.check_sources(source)
                (directory / "unit.txt").write_bytes(b"changed\n")
                with self.assertRaises(s.SpatialError):
                    s.check_sources(source)
        self.assertFalse(s._RUN_RELEASE_ENABLED)
        self.assertFalse(s.b4._EXECUTION_RELEASE_ENABLED)
        from tools import _tspm1_functional_study as functional
        self.assertFalse(functional._FUNCTIONAL_STUDY_RELEASE_ENABLED)


def run_qualification_once():
    directory = calibration.BASE / calibration.QUALIFICATION_ID
    directory.mkdir(exist_ok=False)
    output, captured = io.StringIO(), []
    source = calibration.source_manifest()

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
            guards = {name: stack.enter_context(patch.object(s.b4, name,
                side_effect=AssertionError("no formation or matrix in qualification")))
                for name in ("_advance_b4", "advance_s2dr_arm", "probe_s2dr_arm")}
            guards["receptor"] = stack.enter_context(patch.object(s.LocalChannelGridReceptor, "analyze",
                side_effect=AssertionError("no confirmation images in qualification")))
            guards["recipe"] = stack.enter_context(patch.object(calibration, "recipe",
                side_effect=AssertionError("no confirmation recipe in qualification")))
            with redirect_stdout(output), redirect_stderr(output):
                result = unittest.TextTestRunner(stream=output, verbosity=2, failfast=True,
                    resultclass=RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(CalibrationTests))
            calls = {name: guard.call_count for name, guard in guards.items()}
        s.check_sources(source)
        raw = output.getvalue().encode("utf-8")
        with (directory / "output.txt").open("xb") as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())
        successful = result.wasSuccessful() and result.testsRun == 8 and not any(calls.values())
        report = s.seal("calibration_qualification", {"successful": successful,
            "test_count": result.testsRun, "exit_code": 0 if successful else 1,
            "tests": captured, "guard_calls": calls, "output_sha256": s.raw_hash(raw), "source": source})
        s._publish(directory / "result.json", report)
        print(raw.decode(), end="")
        print("qualification_digest=" + report["digest"])
        return 0 if successful else 1
    except BaseException:
        with (directory / "failure.txt").open("x", encoding="utf-8") as stream:
            stream.write(output.getvalue() + traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(run_qualification_once())
