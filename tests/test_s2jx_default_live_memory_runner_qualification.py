"""Neutral technical qualification for the private S2-JX run boundary."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools import _s2jx_default_live_memory_result_verifier as verifier
from tools import _s2jx_default_live_memory_runner as runner
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits


ROOT = Path(__file__).resolve().parents[1]


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _neutral_pairs():
    profile = build_s2jw_default_live_profile()
    visual_receptor = LocalChannelGridReceptor(VisualGridConfig())
    hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    pairs = []
    for block, (fill, period) in enumerate(((64, 320), (192, 200))):
        image = np.full((1080, 1920, 3), fill, dtype=np.uint8)
        half = period // 2
        window = tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))
        auditory_state = None
        for hop in range(10):
            auditory_state = hearing.push(window[hop * 480 : (hop + 1) * 480])
        assert auditory_state is not None
        visual_state = visual_receptor.analyze(image, frame_index=3 * block + 2)
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(
                "s2jx-neutral-clock",
                block * 100_000_000 + 90_000_000,
                (block + 1) * 100_000_000,
            ),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                "s2jx-neutral-clock",
                ((3 * block + 2) * 1_000_000_000) // 30,
                (block + 1) * 100_000_000,
            ),
        )
        plan = pairing.build_s2jv_pairing_plan(
            pair_id=f"s2jx-neutral-pair-{block}",
            source_contract_id="s2jx-neutral-source",
            profile=profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=_sha256(np.asarray(window, dtype="<f4").tobytes()),
            visual_payload_digest=_sha256(image.tobytes(order="C")),
        )
        pairs.append(
            pairing.bind_s2jv_default_live_pair(
                pairing_plan=plan,
                profile=profile,
                auditory=auditory,
                visual=visual,
            )
        )
    return profile, tuple(pairs)


def _probe(label: str, final_digest: str) -> dict[str, object]:
    result: dict[str, object] = {
        "evaluation_label": label,
        "probe_digest": "1" * 64,
        "finding_digest": "2" * 64,
        "native_tspm_finding_digest": "3" * 64,
        "prestate_digest": final_digest,
        "poststate_digest": final_digest,
        "b4_selected": None,
        "fast_selected": None,
        "auditory_slow_selected": None,
        "visual_slow_selected": None,
        "auditory_slow_observations": [],
        "visual_slow_observations": [],
        "ledger_digest": "4" * 64,
    }
    if label == "D9":
        result["b4_selected"] = {
            "slot_id": "neutral-b4",
            "formation_index": 15,
            "auditory_distance": 0.0,
            "visual_distance": 0.0,
            "mechanical_match": True,
            "evidence_digest": "5" * 64,
        }
    elif label == "X":
        for key, modality in (
            ("auditory_slow_selected", "auditory"),
            ("visual_slow_selected", "visual"),
        ):
            result[key] = {
                "modality_id": modality,
                "slot_id": f"neutral-{modality}",
                "support": 3,
                "stable": True,
                "native_distance": 0.0,
                "mechanical_match": True,
                "evidence_digest": "6" * 64,
            }
    return result


def _complete_record() -> dict[str, object]:
    chain = runner._OperationChain([])
    for role in verifier.EXPECTED_OPERATION_ROLES:
        chain.append(role, {"neutral_evidence_digest": "7" * 64})
    final_digest = "8" * 64
    probes = [_probe(label, final_digest) for label in ("D9", "X", "Y")]
    payload = {
        "schema": runner.S2JX_RESULT_SCHEMA,
        "run_id": "s2jx-neutral-qualification-run",
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": runner.source_hashes(ROOT),
        "profile_binding_digest": "9" * 64,
        "fixture_recipe_digest": verifier.FIXTURE_RECIPE_DIGEST,
        "plan": {
            "formation_sequence": list(verifier.FORMATION_SEQUENCE),
            "probe_sequence": list(verifier.PROBE_SEQUENCE),
            "formation_count": 15,
            "probe_count": 3,
            "top_level_operation_count": 72,
            "total_l1_terms": 43_680,
            "raw_payload_retained": False,
            "field_read": False,
            "context_selection": False,
            "compression_336_to_26": False,
        },
        "operations": chain.records,
        "formation_evidence": [
            {
                "evaluation_label": label,
                "formation_index": index,
                "pairing_digest": "a" * 64,
                "input_digest": "b" * 64,
                "receipt_digest": "c" * 64,
                "state": {"generation": index, "state_digest": "d" * 64},
            }
            for index, label in enumerate(verifier.FORMATION_SEQUENCE, 1)
        ],
        "final_state": {"generation": 15, "state_digest": final_digest},
        "probe_evidence": probes,
        "functional_evaluation": runner.evaluate_probe_evidence(probes),
        "last_operation_digest": chain.previous_digest,
    }
    return runner._sealed_result(payload)


def _write_record(root: Path, record: dict[str, object]) -> Path:
    directory = root / str(record["run_id"])
    directory.mkdir()
    runner._atomic_write(directory / "result.json", record)
    return directory


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = deepcopy(record)
    payload.pop("record_digest", None)
    return runner._sealed_result(payload)


class S2JXRunnerQualificationTests(unittest.TestCase):
    def test_01_main_gate_is_closed(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(runner.S2JXRunnerError):
                runner.run_main_once(Path(temporary).resolve(), ROOT, runner.AUTHORIZED_RUN_ID)

    def test_02_bound_counts_and_sequences_are_exact(self) -> None:
        self.assertEqual((15, 3, 72, 43_680), (
            runner.FORMATION_COUNT,
            runner.PROBE_COUNT,
            runner.TOP_LEVEL_OPERATION_COUNT,
            runner.TOTAL_L1_TERMS,
        ))
        self.assertEqual(15, len(verifier.FORMATION_SEQUENCE))
        self.assertEqual(("D9", "X", "Y"), verifier.PROBE_SEQUENCE)

    def test_03_neutral_receptor_pair_has_exact_default_live_dimensions(self) -> None:
        profile, pairs = _neutral_pairs()
        self.assertEqual((48, 288, 336), (
            len(pairs[0].auditory.timed_frame.frame.values),
            len(pairs[0].visual.timed_frame.frame.values),
            profile.av_dimension,
        ))

    def test_04_neutral_atomic_step_and_probe_are_read_only(self) -> None:
        profile, pairs = _neutral_pairs()
        limits = build_s2jv_ledger_limits(profile)
        config = coordinator.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=limits,
        )
        state = coordinator.initial_s2jv_composite_state(config)
        source = coordinator.bind_s2jv_coordinator_input(config=config, source=pairs[0])
        owner = coordinator.S2JVFormationOwner(
            "s2jx-neutral-owner",
            "s2jx-neutral-authorization",
            "s2jx-neutral-consumption",
            config.config_digest,
            state.state_digest,
            source.input_digest,
        )
        state = coordinator.advance_s2jv_atomic(
            config=config, prestate=state, source=source, owner=owner
        ).poststate
        probe = coordinator.bind_s2jv_probe(config=config, source=pairs[1])
        finding = read_only.probe_s2jv_composite_read_only(
            config=config, state=state, probe=probe
        )
        self.assertEqual((state.state_digest, state.state_digest), (
            finding.prestate_digest,
            finding.poststate_digest,
        ))

    def test_05_operation_registry_is_complete_and_chained(self) -> None:
        record = _complete_record()
        operations = record["operations"]
        self.assertEqual(72, len(operations))
        self.assertEqual("s2jx-op-072", operations[-1]["operation_id"])
        self.assertEqual(operations[-1]["operation_digest"], record["last_operation_digest"])

    def test_06_atomic_record_is_independently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), _complete_record())
            finding = verifier.verify_s2jx_result(directory.resolve(), ROOT)
        self.assertEqual(("RECORDING_COMPLETE", "S2JX_FUNCTION_CONFIRMED"), (
            finding.status,
            finding.functional_status,
        ))

    def test_07_complete_functional_deviation_is_falsified_not_technical(self) -> None:
        record = _complete_record()
        record["probe_evidence"][0]["b4_selected"] = None
        record["functional_evaluation"] = runner.evaluate_probe_evidence(record["probe_evidence"])
        record = _reseal(record)
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jx_result(directory.resolve(), ROOT)
        self.assertEqual(("RECORDING_COMPLETE", "S2JX_FUNCTION_FALSIFIED"), (
            finding.status,
            finding.functional_status,
        ))

    def test_08_record_digest_mutation_is_rejected(self) -> None:
        record = _complete_record()
        record["record_digest"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jx_result(directory.resolve(), ROOT)
        self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_09_operation_reordering_is_rejected_even_when_resealed(self) -> None:
        record = _complete_record()
        record["operations"][0]["role"] = "TSPM_ARM"
        record = _reseal(record)
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jx_result(directory.resolve(), ROOT)
        self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_10_missing_or_additional_artifact_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing = root / "s2jx-neutral-missing"
            missing.mkdir()
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2jx_result(missing.resolve(), ROOT).status)
            directory = _write_record(root, _complete_record())
            (directory / "extra.json").write_text("{}", encoding="ascii")
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2jx_result(directory.resolve(), ROOT).status)

    def test_11_result_path_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), _complete_record())
            with self.assertRaises(runner.S2JXRunnerError):
                runner._atomic_write(directory / "result.json", _complete_record())

    def test_12_raw_payload_or_source_mutation_is_rejected(self) -> None:
        record = _complete_record()
        record["raw_payload"] = "forbidden"
        record["source_hashes"][runner.SOURCE_PATHS[0]] = "0" * 64
        record = _reseal(record)
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), record)
            finding = verifier.verify_s2jx_result(directory.resolve(), ROOT)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertGreaterEqual(len(finding.issues), 2)


if __name__ == "__main__":
    unittest.main()

