"""New display checks only; synthetic records, no historical processing replay."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools import _s2oe_history_view as v


def sealed(value, key):
    return dict(value, **{key: v.sha(v.canonical(value))})


def fixture():
    specs, rows, inputs, scans, transitions, receipts = [], [], [], [], [], []
    births = [None] * 24
    for ordinal in range(1, 5):
        formation = ordinal in (1, 3)
        spec = dict(ordinal=ordinal, event_id=f"neutral-view-{ordinal}", pass_number=1, window_number=ordinal)
        specs.append(spec)
        generation = None
        if formation:
            births = [ordinal] + [None] * 23
            generation = dict(event=ordinal, births=births, actions=["CREATED" if ordinal == 1 else "REPLACED"] + ["FREE"]*23)
            transitions.append(dict(event=ordinal, generations=generation))
        cue = dict(cue_digest=f"cue-{ordinal}", visible_positions=[0, 2], values=[0.25, None, 0.75])
        event = dict(spec, event_type="FORMATION" if formation else "PARTIAL_VISUAL_CUE", event_digest=f"event-{ordinal}")
        step = dict(event_digest=event["event_digest"], scan_receipt_digest=None if formation else f"scan-{ordinal}",
            context_status="NOT_REQUESTED" if formation else "ABSTAIN_INTERNAL_AMBIGUITY", hypothesis=None,
            perception_status="RECORDED", memory_status="COMMITTED" if formation else "READ_ONLY_UNCHANGED", error_codes=[])
        rows.append(dict(step=step, memory="state", post=dict(memory_state_digest="state"),
                         generations=generation, current_births=list(births)))
        inputs.append(dict(event=event, operation=cue, field=dict(start_tick=ordinal, end_tick=ordinal+1)))
        receipts.append(dict(ordinal=ordinal, frame_pts=ordinal))
        if not formation:
            banks = []
            for role, count in (("B4_RECENT", 9), ("TSPM_FAST", 3), ("B_STABLE_VISUAL", 4)):
                records = [dict(bank_role=role, slot_id=f"slot.{i:03d}", slot_digest=f"slot-{i}",
                           observed_match=role == "B4_RECENT" and i == 0) for i in range(count)]
                banks.append(dict(bank_role=role, records=records))
            scans.append(dict(ordinal=ordinal, role="PRIMARY", value=dict(result_digest=f"scan-{ordinal}",
                state_digest="state", prestate_digest="state", poststate_digest="state", config_digest="profile",
                decision=step["context_status"], hypothesis=None, cue_digest=cue["cue_digest"],
                schema="neutral-visual", a_recent=dict(status="A_RECENT_INTERNAL_AMBIGUITY"), bank_scans=banks)))
    common = sealed(dict(manifest=dict(run_id="neutral", events=specs, source=dict(video_time_base=[1, 30000]))), "common_digest")
    core = dict(run_id="neutral", record_digest="core", config_digest="profile", rows=rows, inputs=inputs, scans=scans, states=dict(state={}))
    record = dict(run_id="neutral", record_digest="record", status="RECORDING_COMPLETE", manifest={"$oc_common":"manifest"},
                  execution=core, media=dict(receipts=receipts))
    proof = sealed(dict(status="RECORDING_COMPLETE", evaluation_allowed=True, read_only=True,
                   record_digest="record", native=dict(record_digest="core", transitions=transitions)), "verification_digest")
    return dict(wire=dict(record=record, common_sha256=v.sha(v.canonical(common))), common=common,
                proof=proof, session=dict(common_sha256=v.sha(v.canonical(common)), session=dict(run_id="neutral")))


class DisplayChecks(unittest.TestCase):
    def bad(self, data, code):
        with self.assertRaises(v.DisplayError) as caught:
            v.project(**data)
        self.assertEqual(caught.exception.code, code)

    def test_01_assignment(self):
        result = v.project(**fixture())
        self.assertEqual(result["events"][1]["components"], [dict(index=0, value=.25), dict(index=2, value=.75)])

    def test_02_ambiguity(self):
        result = v.project(**fixture())["events"][1]
        self.assertEqual(result["context"], "ABSTAIN_INTERNAL_AMBIGUITY")
        self.assertFalse(result["hypothesis"])
        self.assertEqual(len(result["candidates"]), 1)

    def test_03_missing_positions(self):
        data = fixture()
        del data["wire"]["record"]["execution"]["inputs"][1]["operation"]["visible_positions"]
        self.assertEqual(v.project(**data)["events"][1]["components"], [])

    def test_04_replacement(self):
        result = v.project(**fixture())
        self.assertEqual([result["events"][i]["candidates"][0]["generation"] for i in (1, 3)], [1, 3])
        self.assertTrue(all(result["events"][i]["candidates"][0]["historical"] for i in (1, 3)))

    def test_05_run_reference(self):
        data = fixture(); data["wire"]["record"]["run_id"] = "foreign"
        self.bad(data, "RUN_BINDING_INVALID")

    def test_06_event_reference(self):
        data = fixture(); data["wire"]["record"]["execution"]["inputs"][1]["event"]["event_id"] = "foreign"
        self.bad(data, "EVENT_BINDING_INVALID")

    def test_07_scan_reference(self):
        data = fixture(); data["wire"]["record"]["execution"]["scans"][0]["value"]["state_digest"] = "foreign"
        self.bad(data, "SCAN_REFERENCE_INVALID")

    def test_08_generation_reference(self):
        data = fixture(); data["wire"]["record"]["execution"]["rows"][3]["current_births"][0] = 1
        self.bad(data, "GENERATION_REFERENCE_INVALID")

    def test_09_detached(self):
        data = fixture(); before = copy.deepcopy(data)
        result = v.project(**data); result["events"][1]["components"][0]["value"] = 123
        self.assertEqual(data, before)

    def test_10_file_pins(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); (path/"x").write_bytes(b"correct")
            ref = dict(path="x", bytes=7, sha256=v.sha(b"correct"))
            self.assertEqual(v.read_bound(path, ref), b"correct")
            (path/"x").write_bytes(b"changed")
            with self.assertRaises(v.DisplayError) as caught: v.read_bound(path, ref)
            self.assertEqual(caught.exception.code, "REFERENCE_HASH_INVALID")
            (path/"x").unlink()
            with self.assertRaises(v.DisplayError) as caught: v.read_bound(path, ref)
            self.assertEqual(caught.exception.code, "REFERENCE_MISSING")

    def test_11_missing_scan(self):
        data = fixture(); data["wire"]["record"]["execution"]["scans"] = []
        self.bad(data, "SCAN_REFERENCE_MISSING")

    def test_12_browser(self):
        data = fixture()
        result = v.project(**data)
        with tempfile.TemporaryDirectory() as name:
            path = Path(name)
            (path/"view.html").write_bytes(v.page(Path("tools/s2oe_player.html").read_bytes(), result))
            # Independent expectations from source fixtures, not the production projector/renderer.
            expected = [dict(event=x["event"]["event_id"], context=row["step"]["context_status"],
                state=row["memory"], birth=row["current_births"][0])
                for x, row in zip(data["wire"]["record"]["execution"]["inputs"],
                                  data["wire"]["record"]["execution"]["rows"], strict=True)]
            (path/"expected.json").write_text(json.dumps(expected), encoding="utf-8")
            proc = subprocess.run([os.environ["MCM_NODE"], "tests/s2oe_history_browser.cjs", str(path)],
                                  capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("BROWSER_OK", proc.stdout)
            print(proc.stdout.strip())

    def test_13_audio_binding(self):
        data = fixture(); core = data["wire"]["record"]["execution"]
        old = core["scans"][0]["value"]
        old["bank_scans"][2] = dict(bank_role="B_STABLE_AUDITORY", records=[dict(
            bank_role="B_STABLE_AUDITORY", slot_id=f"slot.{i:03d}", slot_digest=f"b-{i}",
            observed_match=False, match_threshold=.01) for i in range(8)])
        for bank in old["bank_scans"][:2]:
            for candidate in bank["records"]: candidate["match_threshold"] = .1
        core["scans"][0]["value"] = dict(arm_digest="scan-2", rule="ALL_BANDS_24", evidence=old)
        cue = core["inputs"][1]["operation"]
        core["inputs"][1]["operation"] = dict(cue=cue, band_plan=dict(observed_bands=[0, 2]))
        result = v.project(**data)["events"][1]
        self.assertEqual(result["rules"][0]["rule"], "ALL_BANDS_24")
        self.assertEqual(result["rules"][2]["threshold"], .01)

    def test_14_output_limit(self):
        with self.assertRaises(v.DisplayError) as caught:
            v.page(b"<script>" + b" "*65536, {})
        self.assertEqual(caught.exception.code, "HTML_LIMIT")

    def test_15_hypothesis(self):
        data = fixture(); core = data["wire"]["record"]["execution"]
        core["rows"][1]["step"].update(context_status="ADMIT_SINGLE_CONTEXT", hypothesis=dict(trace="bound"))
        core["scans"][0]["value"].update(decision="ADMIT_SINGLE_CONTEXT", hypothesis=dict(trace="bound"))
        self.assertTrue(v.project(**data)["events"][1]["hypothesis"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
