"""Eight bounded sequence checks; no complete study fixture or receptor run."""

from __future__ import annotations

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import replace
import copy
import io
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch

from tools import _visual_sequence_memory_probe as sequence


s, b4 = sequence.spatial, sequence.b4


def vector(value):
    return (0.0,) * 8 + (value,) * 18


def four_state():
    values = tuple(vector(value) for value in (0.1, 0.3, 0.5, 0.7))
    entries = tuple(b4._FIFOEntry(f"b4.slot.{i:03d}", i < 4,
                    values[i] if i < 4 else (), i + 1 if i < 4 else None) for i in range(9))
    return b4._B4State(4, entries), values


class SequenceTests(unittest.TestCase):
    def test_01_index_is_derived_from_each_continued_prestate(self):
        state = s.fresh_state()
        first = vector(0.1)
        second = vector(0.3)
        post1, receipt1 = sequence.advance_sequence_b4(state, first)
        post2, receipt2 = sequence.advance_sequence_b4(post1, second)
        self.assertEqual((1, 2), (receipt1["formation_index"], receipt2["formation_index"]))
        self.assertEqual((0, 1, 2), (state.accepted_count, post1.accepted_count, post2.accepted_count))
        self.assertEqual(first, post2.entries[0].values)
        self.assertEqual(second, post2.entries[1].values)
        self.assertEqual(0, state.accepted_count)

    def test_02_order_comes_from_indices_not_container_or_external_ids(self):
        state, values = four_state()
        swapped = (values[0], values[2], values[1], values[3])
        original = sequence.probe_visual_sequence_read_only(state, values)
        changed_layout = b4._B4State(4, tuple(reversed(state.entries)))
        same_after_layout_change = sequence.probe_visual_sequence_read_only(changed_layout, values)
        other = sequence.probe_visual_sequence_read_only(state, swapped)
        self.assertTrue(original["ordered"]["recognized"])
        self.assertTrue(same_after_layout_change["ordered"]["recognized"])
        self.assertFalse(other["ordered"]["recognized"])
        self.assertTrue(other["order_blind"]["recognized"])

    def test_03_missing_duplicate_foreign_or_partial_indices_fail_closed(self):
        state, values = four_state()
        cases = []
        duplicate = list(state.entries)
        duplicate[1] = replace(duplicate[1], formation_index=1)
        cases.append(b4._B4State(4, tuple(duplicate)))
        foreign = list(state.entries)
        foreign[2] = replace(foreign[2], formation_index=7)
        cases.append(b4._B4State(4, tuple(foreign)))
        cases.append(replace(state, accepted_count=3))
        missing = list(state.entries)
        missing[3] = b4._FIFOEntry(missing[3].slot_id, False, (), None)
        cases.append(b4._B4State(4, tuple(missing)))
        for changed in cases:
            with self.subTest(changed=changed.accepted_count):
                with self.assertRaises(s.SpatialError):
                    sequence.probe_visual_sequence_read_only(changed, values)

    def test_04_exact_l1_calibration_and_unique_content_gate(self):
        state, values = four_state()
        boundary = ((0.0,) * 8 + (0.1 + 44/765,) * 18,) + values[1:]
        finding = sequence.probe_visual_sequence_read_only(state, boundary)
        self.assertTrue(finding["ordered"]["recognized"])
        self.assertEqual(44, finding["visual_threshold_numerator"])
        self.assertEqual(765, finding["visual_threshold_denominator"])
        above = ((0.0,) * 8 + (0.1 + 44/765 + 0.0001,) * 18,) + values[1:]
        with self.assertRaises(s.SpatialError):
            sequence.probe_visual_sequence_read_only(state, above)
        ambiguous = (values[0], values[0], values[2], values[3])
        with self.assertRaises(s.SpatialError):
            sequence.probe_visual_sequence_read_only(state, ambiguous)

    def test_05_order_blind_result_is_permutation_invariant(self):
        state, values = four_state()
        for probes in ((values[1], values[3], values[0], values[2]),
                       tuple(reversed(values)), (values[2], values[0], values[3], values[1])):
            with self.subTest(probes=probes[0][8]):
                finding = sequence.probe_visual_sequence_read_only(state, tuple(probes))
                self.assertTrue(finding["order_blind"]["recognized"])
                self.assertEqual(1, finding["order_blind"]["assignment_count"])

    def test_06_both_views_are_read_only_and_return_only_stored_values(self):
        state, values = four_state()
        before = copy.deepcopy(state)
        finding = sequence.probe_visual_sequence_read_only(state, values)
        self.assertEqual(before, state)
        self.assertEqual(finding["prestate"], finding["poststate"])
        self.assertEqual(values, finding["ordered"]["returned"])
        self.assertNotIn("returned", finding["order_blind"])

    def test_07_source_result_chain_and_incomplete_recording_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/"unit"
            journal = s.Journal(directory)
            journal.emit("unit_start", {"owner": "unit"})
            journal.emit("unit", {"owner": "unit"})
            journal.close()
            records = s.read_records(directory)
            self.assertEqual(1, len(list(sequence.calibration.checked_pairs(records))))
            with self.assertRaises(FileExistsError):
                s.Journal(directory)
            records[1]["payload"]["owner"] = "foreign"
            with self.assertRaises(s.SpatialError):
                list(sequence.calibration.checked_pairs(records))
            self.assertEqual("NOT_EVALUABLE", sequence.verify_result(directory)["recording_status"])

    def test_08_sources_and_all_old_attempt_entries_remain_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            raw = b"sequence-source\n"
            (directory/"unit.txt").write_bytes(raw)
            source = {"sources": [{"path": "unit.txt", "sha256": s.raw_hash(raw),
                                    "bytes_base64": "c2VxdWVuY2Utc291cmNlCg=="}]}
            with patch.object(s, "ROOT", directory):
                s.check_sources(source)
                (directory/"unit.txt").write_bytes(b"changed\n")
                with self.assertRaises(s.SpatialError):
                    s.check_sources(source)
        self.assertFalse(sequence.calibration._RUN_RELEASE_ENABLED)
        self.assertFalse(s._RUN_RELEASE_ENABLED)
        self.assertFalse(b4._EXECUTION_RELEASE_ENABLED)


def run_qualification_once():
    directory = sequence.BASE/sequence.QUALIFICATION_ID
    directory.mkdir(exist_ok=False)
    output, captured = io.StringIO(), []
    source = sequence.source_manifest()

    class RecordedResult(unittest.TextTestResult):
        def addSuccess(self, test):
            captured.append({"test": test.id(), "status": "PASS"})
            super().addSuccess(test)

        def addFailure(self, test, error):
            captured.append({"test": test.id(), "status": "FAIL",
                             "traceback": self._exc_info_to_string(error, test)})
            super().addFailure(test, error)

        def addError(self, test, error):
            captured.append({"test": test.id(), "status": "ERROR",
                             "traceback": self._exc_info_to_string(error, test)})
            super().addError(test, error)

    try:
        with ExitStack() as stack:
            advance = stack.enter_context(patch.object(b4, "_advance_b4", wraps=b4._advance_b4))
            guards = {name: stack.enter_context(patch.object(b4, name,
                side_effect=AssertionError("no comparison matrix in sequence qualification")))
                for name in ("advance_s2dr_arm", "probe_s2dr_arm")}
            guards["receptor"] = stack.enter_context(patch.object(s.LocalChannelGridReceptor, "analyze",
                side_effect=AssertionError("no main images in sequence qualification")))
            guards["main_recipe"] = stack.enter_context(patch.object(sequence, "probe_recipe",
                side_effect=AssertionError("no full main sequence in qualification")))
            with redirect_stdout(output), redirect_stderr(output):
                result = unittest.TextTestRunner(stream=output, verbosity=2, failfast=True,
                    resultclass=RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(SequenceTests))
            calls = {name: guard.call_count for name, guard in guards.items()}
            calls["bounded_b4_advances"] = advance.call_count
        s.check_sources(source)
        raw = output.getvalue().encode("utf-8")
        with (directory/"output.txt").open("xb") as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())
        successful = (result.wasSuccessful() and result.testsRun == 8
                      and calls["bounded_b4_advances"] == 2
                      and not any(value for key, value in calls.items() if key != "bounded_b4_advances"))
        report = s.seal("sequence_qualification", {"successful": successful,
            "test_count": result.testsRun, "exit_code": 0 if successful else 1,
            "tests": captured, "guard_calls": calls,
            "output_sha256": s.raw_hash(raw), "source": source})
        s._publish(directory/"result.json", report)
        print(raw.decode(), end="")
        print("qualification_digest=" + report["digest"])
        return 0 if successful else 1
    except BaseException:
        with (directory/"failure.txt").open("x", encoding="utf-8") as stream:
            stream.write(output.getvalue() + traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(run_qualification_once())
