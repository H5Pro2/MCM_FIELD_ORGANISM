from __future__ import annotations

import ast
import copy
from pathlib import Path
import tempfile
import unittest

from tools import _s2kp_real_context_admission_336_fixtures as fixtures
from tools import _s2kp_real_context_admission_336_runner as runner
from tools import _s2kp_real_context_admission_336_verifier as verifier
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile


ROOT = Path(__file__).resolve().parents[1]


def _digest(label: str) -> str:
    return runner._digest({"neutral": label})


def _semantic(case_id: str) -> dict[str, object]:
    decision, a_status, b_status, count, area = runner.EXPECTED_CASES[case_id]
    return {
        "decision": decision,
        "a_status": a_status,
        "b_status": b_status,
        "public_candidate_count": count,
        "hypothesis_area": area,
        "hypothesis_values_digest": _digest(f"values-{case_id}") if area else None,
        "hypothesis_provenance_count": 2 if case_id == "R1" else 1 if area else 0,
    }


def _neutral_record() -> dict[str, object]:
    formations: list[dict[str, object]] = []
    for history_id, length in zip(("h00", "h01", "h02"), (15, 14, 2), strict=True):
        prestate = _digest(f"{history_id}-state-0")
        for ordinal in range(1, length + 1):
            poststate = _digest(f"{history_id}-state-{ordinal}")
            formations.append(
                {
                    "history_id": history_id,
                    "ordinal": ordinal,
                    "recipe_id": "N",
                    "source": {"pairing_digest": _digest(f"{history_id}-pair-{ordinal}")},
                    "input_digest": _digest(f"{history_id}-input-{ordinal}"),
                    "prestate_digest": prestate,
                    "poststate_digest": poststate,
                    "receipt_digest": _digest(f"{history_id}-receipt-{ordinal}"),
                    "result_digest": _digest(f"{history_id}-result-{ordinal}"),
                    "owner_status": "CONSUMED",
                    "b4_event": "B4_APPENDED",
                }
            )
            prestate = poststate
    cases: list[dict[str, object]] = []
    for case_id in runner.CASE_ORDER:
        state_digest = _digest(f"state-{case_id}")
        retrieval_source = _digest(f"retrieval-source-{case_id}")
        context_digest = _digest(f"context-{case_id}")
        semantic = _semantic(case_id)
        cases.append(
            {
                "case_id": case_id,
                "history_id": "h00",
                "context_bundle_digest": context_digest,
                "retrieval_source_digest": retrieval_source,
                "retrieval": {
                    "source": {"pairing_digest": retrieval_source},
                    "memory_probe_digest": _digest(f"memory-probe-{case_id}"),
                    "finding_digest": _digest(f"finding-{case_id}"),
                    "validated_finding_digest": _digest(f"validated-{case_id}"),
                    "context_bundle_digest": context_digest,
                    "prestate_digest": state_digest,
                    "poststate_digest": state_digest,
                },
                "masked_source": {"pairing_digest": _digest(f"masked-source-{case_id}")},
                "masked_probe_digest": _digest(f"masked-probe-{case_id}"),
                "primary_result_digest": _digest(f"primary-{case_id}"),
                "baseline_result_digest": _digest(f"baseline-{case_id}"),
                "primary": semantic,
                "baseline": copy.deepcopy(semantic),
                "prestate_digest": state_digest,
                "poststate_digest": state_digest,
                "read_only": True,
            }
        )
    payload = {
        "schema": runner.S2KP_RESULT_SCHEMA,
        "run_id": "s2kp-neutral-qualification-record",
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": runner.source_hashes(ROOT),
        "config_digest": _digest("config"),
        "plan": {
            "history_ids": ["h00", "h01", "h02"],
            "history_lengths": [15, 14, 2],
            "formation_count": 31,
            "full_probe_count": 5,
            "masked_probe_count": 6,
            "admission_call_count": 12,
            "maximum_functional_operations": 96,
            "context_fill": False,
            "field_effect": False,
            "automatic_mask_detection": False,
        },
        "formations": formations,
        "cases": cases,
        "functional_evaluation": runner.evaluate_case_evidence(cases),
        "raw_payload_retained": False,
    }
    return runner._sealed_result(payload)


def _write_record(root: Path, record: dict[str, object]) -> Path:
    directory = root / "s2kp-neutral-record"
    directory.mkdir()
    runner._atomic_write(directory / "result.json", record)
    return directory.resolve()


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    return runner._sealed_result(payload)


class S2KPRealContextAdmission336QualificationTests(unittest.TestCase):
    def test_01_bound_plan_is_three_fresh_histories_and_six_cases(self) -> None:
        self.assertEqual((15, 14, 2), tuple(len(value) for value in fixtures.HISTORIES.values()))
        self.assertEqual(31, fixtures.FORMATION_COUNT)
        self.assertEqual((5, 6, 12, 96), (
            fixtures.FULL_PROBE_COUNT,
            fixtures.MASKED_PROBE_COUNT,
            runner.ADMISSION_CALL_COUNT,
            runner.MAX_FUNCTIONAL_OPERATIONS,
        ))
        self.assertEqual(("R1", "R2", "R3", "R4", "R5", "R6"), fixtures.CASE_ORDER)

    def test_02_real_byte_block_fixtures_produce_bound_receptor_values(self) -> None:
        stream = fixtures.S2KPFixtureStream(build_s2jw_default_live_profile(), "n01")
        observed = {}
        for recipe in ("B0", "A0", "C0", "C1"):
            pair, source = stream.materialize(recipe)
            observed[recipe] = tuple(pair.visual.timed_frame.frame.values)
            self.assertEqual(recipe, source.recipe_id)
        self.assertEqual((0.0,) * 288, observed["B0"])
        self.assertEqual(observed["B0"], observed["C0"])
        self.assertEqual(1.0 / 255.0, observed["A0"][32])
        self.assertEqual(2.0 / 255.0, observed["C1"][32])
        self.assertEqual(1, sum(value != 0.0 for value in observed["A0"]))
        self.assertEqual(1, sum(value != 0.0 for value in observed["C1"]))

    def test_03_mask_source_is_real_strictly_later_and_d9_conflict_is_visible(self) -> None:
        stream = fixtures.S2KPFixtureStream(build_s2jw_default_live_profile(), "n02")
        pair, earlier = stream.materialize("D9")
        later_pair, later = stream.materialize("D9_VISIBLE_MISMATCH")
        fixtures.assert_strictly_later(earlier, later)
        first = tuple(pair.visual.timed_frame.frame.values)
        changed = tuple(later_pair.visual.timed_frame.frame.values)
        self.assertEqual(0.0, first[0])
        self.assertEqual(1.0, changed[0])
        self.assertEqual(first[1:], changed[1:])
        masked = fixtures.masked_visual_values(later_pair)
        self.assertTrue(all(masked[index] is not None for index in range(32)))
        self.assertTrue(all(masked[index] is None for index in range(32, 288)))

    def test_04_neutral_real_pipeline_uses_full_probe_and_is_read_only(self) -> None:
        result = runner._neutral_pipeline_once()
        self.assertEqual("R1", result["case_id"])
        self.assertEqual("ADMIT_SINGLE_CONTEXT", result["primary"]["decision"])
        self.assertEqual("A_RECENT", result["primary"]["hypothesis_area"])
        self.assertEqual(result["primary"], result["baseline"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["prestate_digest"], result["poststate_digest"])

    def test_05_main_gate_is_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(runner.S2KPRunnerError, "gate is closed"):
                runner.run_main_once(Path(temporary).resolve(), ROOT, runner.AUTHORIZED_RUN_ID)

    def test_06_atomic_result_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "result.json"
            runner._atomic_write(path, {"neutral": True})
            with self.assertRaises(runner.S2KPRunnerError):
                runner._atomic_write(path, {"neutral": False})

    def test_07_verifier_accepts_one_complete_neutral_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write_record(Path(temporary), _neutral_record())
            finding = verifier.verify_s2kp_result(directory, ROOT)
        self.assertEqual(("RECORDING_COMPLETE", "S2KP_FUNCTION_CONFIRMED", ()), (
            finding.status,
            finding.functional_status,
            finding.issues,
        ))

    def test_08_verifier_rejects_record_digest_mutation(self) -> None:
        record = _neutral_record()
        record["record_digest"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            finding = verifier.verify_s2kp_result(_write_record(Path(temporary), record), ROOT)
        self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_09_verifier_rejects_missing_and_additional_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing = root / "missing"
            missing.mkdir()
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2kp_result(missing.resolve(), ROOT).status)
            directory = _write_record(root, _neutral_record())
            (directory / "extra.json").write_text("{}", encoding="ascii")
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2kp_result(directory, ROOT).status)

    def test_10_chain_and_full_retrieval_mutations_fail_closed(self) -> None:
        mutations = []
        chain = _neutral_record()
        chain["formations"][1]["prestate_digest"] = _digest("foreign-state")
        mutations.append(chain)
        retrieval = _neutral_record()
        retrieval["cases"][0]["retrieval"]["context_bundle_digest"] = _digest("foreign-context")
        mutations.append(retrieval)
        for ordinal, record in enumerate(mutations):
            with self.subTest(ordinal=ordinal), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2kp_result(
                    _write_record(Path(temporary), _reseal(record)),
                    ROOT,
                )
                self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_11_complete_semantic_deviation_is_functionally_falsified(self) -> None:
        record = _neutral_record()
        record["cases"][0]["primary"]["decision"] = "ABSTAIN_NO_CONTEXT"
        record["cases"][0]["baseline"]["decision"] = "ABSTAIN_NO_CONTEXT"
        record["functional_evaluation"] = runner.evaluate_case_evidence(record["cases"])
        with tempfile.TemporaryDirectory() as temporary:
            finding = verifier.verify_s2kp_result(
                _write_record(Path(temporary), _reseal(record)),
                ROOT,
            )
        self.assertEqual(("RECORDING_COMPLETE", "S2KP_FUNCTION_FALSIFIED"), (
            finding.status,
            finding.functional_status,
        ))

    def test_12_raw_data_source_mutation_and_public_exports_are_excluded(self) -> None:
        record = _neutral_record()
        record["raw_payload"] = [0, 1]
        first_source = runner.SOURCE_PATHS[0]
        record["source_hashes"][first_source] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            finding = verifier.verify_s2kp_result(
                _write_record(Path(temporary), _reseal(record)),
                ROOT,
            )
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertGreaterEqual(len(finding.issues), 2)

        for relative in (
            "tools/_s2kp_real_context_admission_336_fixtures.py",
            "tools/_s2kp_real_context_admission_336_runner.py",
            "tools/_s2kp_real_context_admission_336_verifier.py",
        ):
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
                elif isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
            self.assertFalse(any("field_engine" in item for item in imports), imports)
        self.assertEqual((), fixtures.__all__)
        self.assertEqual((), runner.__all__)
        self.assertEqual((), verifier.__all__)


if __name__ == "__main__":
    unittest.main()
