"""Single-use neutral connection coverage for the S2-SP PPB lifecycle V2.

This module is intentionally separate from the already consumed OA adapter
qualification.  It uses only temporary neutral payloads and never reads the
OA presealed corpus.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2nl_private_half_profile_binding as half_profile
from tools import _s2ob_private_caller_binding as oa
from tools import _s2sp_oa_materialization_adapter as adapter
from tools import _s2sp_private_memory_compare as core


ARMS = {
    "HISTORICAL": coordinator.tspm1.PPB_UPDATE_HISTORICAL,
    "IDENTITY_PRESERVING_V1": coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING,
}
FORMATION_ROLES = ("A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C", "D", "D", "D", "D", "E", "E")
CUE_ORDINALS = (14, 20)
EVENT_COUNT = 20


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _pixels(role: str, *, cue: bool) -> bytes:
    palette = {"A": 32, "B": 80, "C": 128, "D": 176, "E": 224}
    image = np.full((1080, 1920, 3), palette[role], dtype=np.uint8)
    if cue:
        cells = image.reshape(8, 135, 12, 160, 3)
        for index in range(32, 288):
            cell, channel = divmod(index, 3)
            row, column = divmod(cell, 12)
            cells[row, :, column, :, channel] = 0
    return image.tobytes()


def _pcm(role: str) -> bytes:
    level = {"A": 0.03125, "B": 0.0625, "C": 0.09375, "D": 0.125, "E": 0.15625}[role]
    return np.full(4800, level, dtype="<f4").tobytes()


def _payload(root: Path, source_id: str, suffix: str, raw: bytes) -> oa.Payload:
    path = root / f"{source_id}.{suffix}"
    path.write_bytes(raw)
    return oa.Payload(source_id, path.relative_to(oa.ROOT).as_posix(), _sha(raw), len(raw))


def _visible_cue_values(item: object) -> tuple[tuple[float, ...], tuple[int, ...]]:
    if type(item) is not oa.Input:
        raise AssertionError("cue input type differs")
    operation = item.event.operation_payload
    if type(operation) is not oa.r.ng.visual.MaskedMemoryCue336V1:
        raise AssertionError("direct visual cue type differs")
    values = operation.values
    result = tuple(0.0 if value is None else value for value in values)
    if len(result) != 288 or operation.visible_positions != tuple(range(32)):
        raise AssertionError("neutral cue form differs")
    return result, operation.visible_positions


def _validate_formation_handoff(value: object, prestate: object, result: object) -> None:
    if type(value) is not adapter.S2SPOAMaterializedPairV1:
        raise AssertionError("formation adapter type differs")
    if type(value.pair) is not coordinator.S2JVBoundAVPairV1:
        raise AssertionError("formation pair type differs")
    if type(prestate) is not coordinator.S2JVCompositeStateV1:
        raise AssertionError("formation prestate type differs")
    if type(result) is not coordinator.S2JVFormationResultV1:
        raise AssertionError("formation result type differs")
    readout = result.visual_ppb1_readout
    if readout is not None and type(readout) is not coordinator.tspm1.PPB1Readout:
        raise AssertionError("PPB readout type differs")


def _direct_exact_baseline(
    state: object, cue_values: tuple[float, ...], visible_positions: tuple[int, ...],
    *, candidate_rows: dict[str, tuple[tuple[str, tuple[float, ...]], ...]] | None = None,
) -> dict[str, tuple[str, ...]]:
    """Independent exact comparison; it does not use the productive scan helper."""
    if type(state) is not coordinator.S2JVCompositeStateV1:
        raise AssertionError("baseline state type differs")
    if (type(cue_values) is not tuple or len(cue_values) != 288
            or type(visible_positions) is not tuple or visible_positions != tuple(range(32))):
        raise AssertionError("baseline sight binding differs")
    if not all(type(index) is int and 0 <= index < 288 for index in visible_positions):
        raise AssertionError("baseline sight index differs")
    candidates = core._candidate_rows(state) if candidate_rows is None else candidate_rows
    return {
        bank: tuple(candidate_id for candidate_id, values in rows
                    if type(values) is tuple and len(values) == 288
                    and all(values[index] == cue_values[index] for index in visible_positions))
        for bank, rows in candidates.items()
    }


def _verify(record: dict[str, object]) -> dict[str, object]:
    if record["counts"] != {"events_per_arm": 20, "formations_per_arm": 18, "cues_per_arm": 2,
                            "shared_audio": 18, "shared_visual": 20}:
        raise AssertionError("V2 envelope count differs")
    inputs = None
    for arm_name, arm in record["arms"].items():
        if arm["mode"] != ARMS[arm_name] or len(arm["events"]) != EVENT_COUNT:
            raise AssertionError("arm binding differs")
        current_inputs = tuple(event["input_digest"] for event in arm["events"])
        if inputs is None:
            inputs = current_inputs
        elif inputs != current_inputs:
            raise AssertionError("arms do not share materialized inputs")
        for event in arm["events"]:
            if event["kind"] == "FORMATION":
                evidence = dict(event["transition"])
                observed = evidence.pop("transition_evidence_digest")
                if observed != core.digest(evidence):
                    raise AssertionError("transition evidence digest differs")
                readout = evidence["visual_ppb_readout"]
                if readout is not None and readout["readout_digest"] != event["readout_digest"]:
                    raise AssertionError("native PPB readout differs")
            else:
                if event["prestate_digest"] != event["poststate_digest"]:
                    raise AssertionError("read-only cue changed memory")
                observed = {row["bank"]: tuple(row["exact_baseline_candidate_ids"]) for row in event["scan"]["banks"]}
                if event["direct_baseline"] != observed:
                    raise AssertionError("independent cue baseline differs")
    return {"status": "VERIFIED", "record_digest": record["record_digest"]}


def _evaluate(record: dict[str, object]) -> dict[str, object]:
    """Evaluate lifecycle prerequisites without treating them as technical gates."""
    results = {}
    for arm_name, arm in record["arms"].items():
        formations = [event for event in arm["events"] if event["kind"] == "FORMATION"]
        first_target = next((event["transition"]["visual_ppb_readout"] for event in formations[:4]
                             if event["transition"]["visual_ppb_readout"] is not None), None)
        cue14 = next(event for event in arm["events"] if event["ordinal"] == 14)
        cue20 = next(event for event in arm["events"] if event["ordinal"] == 20)
        b4_fast = [row for row in cue14["scan"]["banks"] if row["bank"] in ("B4", "FAST")]
        a_absent = all(not row["exact_baseline_candidate_ids"] for row in b4_fast)
        replaced = first_target is not None and any(
            event["transition"]["visual_ppb_readout"] is not None
            and event["transition"]["visual_ppb_readout"]["slot_id"] == first_target["slot_id"]
            and event["transition"]["visual_ppb_readout"]["event"] == "REPLACED"
            for event in formations[4:]
        )
        results[arm_name] = {
            "cue14": "READY" if a_absent and first_target is not None else "PRÜFBEDINGUNG_NICHT_ERREICHT",
            "cue20": "READY" if replaced else "PRÜFBEDINGUNG_NICHT_ERREICHT",
            "cue14_scan_digest": cue14["scan"]["comparison_digest"],
            "cue20_scan_digest": cue20["scan"]["comparison_digest"],
        }
    return results


class S2SPPpbLifecycleV2ConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="s2sp-v2-neutral-", dir=oa.ROOT / "reports")
        root = Path(cls.temp.name)
        events = []
        role_index = 0
        for ordinal in range(1, EVENT_COUNT + 1):
            cue = ordinal in CUE_ORDINALS
            role = "A" if cue else FORMATION_ROLES[role_index]
            if not cue:
                role_index += 1
            event_id = f"s2sp-v2-q{ordinal:02d}"
            rgb = _payload(root, f"s2sp-v2-rgb-{ordinal:02d}", "rgb", _pixels(role, cue=cue))
            if cue:
                events.append(oa.Event(event_id, ordinal, oa.V, **oa.expected_times(ordinal, oa.V), pcm=None, rgb=rgb))
            else:
                pcm = _payload(root, f"s2sp-v2-pcm-{ordinal:02d}", "pcm", _pcm(role))
                events.append(oa.Event(event_id, ordinal, oa.AV, **oa.expected_times(ordinal, oa.AV), pcm=pcm, rgb=rgb))
        cls.manifest = oa.build_manifest("s2sp-v2-neutral", tuple(events), "1" * 64)
        cls._static_preflight(tuple(events))
        cls.record = cls._run_neutral(tuple(events))
        cls.verification = _verify(cls.record)
        cls.evaluation = _evaluate(cls.record)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    @classmethod
    def _run_neutral(cls, events: tuple[oa.Event, ...]) -> dict[str, object]:
        materializer = oa.Materializer(cls.manifest, track_reads=True)
        config = half_profile.build_config()
        states = {arm: coordinator.initial_s2jv_composite_state(config) for arm in ARMS}
        rows = {arm: [] for arm in ARMS}
        for event in events:
            if event.kind == oa.AV:
                value = adapter.materialize_next(materializer, event)
                adapter.validate_half_profile_pair(value)
                for arm, mode in ARMS.items():
                    prestate = states[arm]
                    result = core.form(config=config, state=prestate, pair=value.pair, event_id=event.event_id,
                                       run_id=f"s2sp-v2-neutral-{arm.lower()}", ppb_update_mode=mode)
                    _validate_formation_handoff(value, prestate, result)
                    transition = core.transition_evidence(prestate=prestate, result=result)
                    readout = transition["visual_ppb_readout"]
                    rows[arm].append({
                        "ordinal": event.ordinal, "kind": "FORMATION", "input_digest": value.evidence_digest,
                        "prestate_digest": prestate.state_digest, "poststate_digest": result.poststate.state_digest,
                        "transition": transition, "readout_digest": None if readout is None else readout["readout_digest"],
                    })
                    states[arm] = result.poststate
            else:
                item = materializer.next(event)
                cue_values, visible_positions = _visible_cue_values(item)
                input_digest = oa.digest(list(cue_values))
                for arm in ARMS:
                    prestate = states[arm]
                    scan = core.compare_state(state=prestate, cue_values=cue_values)
                    baseline = _direct_exact_baseline(prestate, cue_values, visible_positions)
                    rows[arm].append({
                        "ordinal": event.ordinal, "kind": "CUE", "input_digest": input_digest,
                        "prestate_digest": prestate.state_digest, "poststate_digest": prestate.state_digest,
                        "cue_values": cue_values, "visible_positions": visible_positions,
                        "scan": scan, "direct_baseline": baseline,
                    })
        counts = materializer.counts
        record = {
            "schema": "s2sp.ppb-lifecycle-v2-neutral.v1",
            "counts": {"events_per_arm": 20, "formations_per_arm": 18, "cues_per_arm": 2,
                       "shared_audio": counts["audio"], "shared_visual": counts["visual"]},
            "read_account": materializer.read_account,
            "arms": {arm: {"mode": mode, "events": rows[arm]} for arm, mode in ARMS.items()},
        }
        record["record_digest"] = core.digest(record)
        return record

    @staticmethod
    def _static_preflight(events: tuple[oa.Event, ...]) -> None:
        if len(events) != EVENT_COUNT or sum(event.kind == oa.AV for event in events) != 18:
            raise AssertionError("neutral event envelope differs")
        if tuple(event.ordinal for event in events) != tuple(range(1, EVENT_COUNT + 1)):
            raise AssertionError("neutral event order differs")
        if tuple(event.ordinal for event in events if event.kind == oa.V) != CUE_ORDINALS:
            raise AssertionError("neutral cue order differs")
        for event in events:
            if event.kind == oa.AV and (event.pcm is None or event.rgb is None):
                raise AssertionError("formation payload form differs")
            if event.kind == oa.V and (event.pcm is not None or event.rgb is None):
                raise AssertionError("cue payload form differs")

    def test_complete_neutral_envelope_and_separate_arms(self) -> None:
        self.assertEqual(self.record["counts"], {"events_per_arm": 20, "formations_per_arm": 18, "cues_per_arm": 2,
                                                  "shared_audio": 18, "shared_visual": 20})
        self.assertEqual(self.record["read_account"]["read_operations"], 38)
        self.assertEqual(len(self.record["arms"]["HISTORICAL"]["events"]), EVENT_COUNT)
        self.assertNotEqual(id(self.record["arms"]["HISTORICAL"]), id(self.record["arms"]["IDENTITY_PRESERVING_V1"]))

    def test_native_lifecycle_readouts_are_bound(self) -> None:
        for arm in ARMS:
            formations = [row for row in self.record["arms"][arm]["events"] if row["kind"] == "FORMATION"]
            self.assertEqual(len(formations), 18)
            self.assertTrue(any(row["readout_digest"] is not None for row in formations))
            for row in formations:
                self.assertEqual(row["transition"]["formation_generation_after"], row["transition"]["formation_generation_before"] + 1)

    def test_independent_verification_and_read_only_cues(self) -> None:
        self.assertEqual(self.verification["status"], "VERIFIED")
        for arm in ARMS:
            cues = [row for row in self.record["arms"][arm]["events"] if row["kind"] == "CUE"]
            self.assertEqual([row["ordinal"] for row in cues], list(CUE_ORDINALS))
            self.assertTrue(all(row["prestate_digest"] == row["poststate_digest"] for row in cues))

    def test_negative_lifecycle_evaluation_is_not_a_technical_failure(self) -> None:
        self.assertEqual(set(self.evaluation), set(ARMS))
        allowed = {"READY", "PRÜFBEDINGUNG_NICHT_ERREICHT"}
        for arm in ARMS:
            self.assertIn(self.evaluation[arm]["cue14"], allowed)
            self.assertIn(self.evaluation[arm]["cue20"], allowed)

    def test_full_envelope_fits_the_existing_receipt_limit(self) -> None:
        verification_bytes = len(core.canonical(self.verification))
        evaluation_bytes = len(core.canonical(self.evaluation))
        record_bytes = len(core.canonical(self.record))
        self.assertLessEqual(record_bytes + verification_bytes + evaluation_bytes, 262_144)

    def test_hidden_values_do_not_change_the_visible_baseline(self) -> None:
        cue = (0.25,) * 288
        candidate = cue[:32] + (0.75,) * 256
        state = coordinator.initial_s2jv_composite_state(half_profile.build_config())
        candidates = {"B4": (("candidate", candidate),), "FAST": (), "VISUAL_SLOW": ()}
        self.assertEqual(_direct_exact_baseline(state, cue, tuple(range(32)), candidate_rows=candidates)["B4"],
                         ("candidate",))

    def test_visible_difference_rejects_the_exact_baseline(self) -> None:
        cue = (0.25,) * 288
        candidate = (0.5,) + cue[1:]
        state = coordinator.initial_s2jv_composite_state(half_profile.build_config())
        candidates = {"B4": (("candidate", candidate),), "FAST": (), "VISUAL_SLOW": ()}
        self.assertEqual(_direct_exact_baseline(state, cue, tuple(range(32)), candidate_rows=candidates)["B4"], ())

    def test_invalid_visible_binding_is_rejected(self) -> None:
        state = coordinator.initial_s2jv_composite_state(half_profile.build_config())
        with self.assertRaisesRegex(AssertionError, "baseline sight binding differs"):
            _direct_exact_baseline(state, (0.0,) * 288, tuple(range(31)))


if __name__ == "__main__":
    unittest.main()
