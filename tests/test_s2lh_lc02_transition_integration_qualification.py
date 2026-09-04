from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2ld_auditory_partial_cue_runner as runner
from tools import _s2ld_auditory_partial_cue_verifier as verifier
from tools import _s2lg_private_ppb_transition_evaluation as transition


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json"
HISTORICAL_RESULT = ROOT / "reports/s2ld/s2ld-real-auditory-partial-cue-336-20260904-01/result.json"
HISTORICAL_VERIFICATION = ROOT / "reports/s2ld/s2le-real-auditory-partial-cue-20260904-01-verification.json"
QUALIFICATION_ID = "s2lh-lc02-transition-integration-qualification-20260904-01"


def _source_values() -> tuple[tuple[float, ...], tuple[float, ...]]:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != "87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3":
        raise AssertionError("S2-KY source hash differs")
    value = json.loads(raw.decode("ascii"))["measurements"]
    return tuple(value["CANDIDATE_PLUS"]["values"]), tuple(value["CUE_LOW"]["values"][:24])


def _prototypes(source: tuple[float, ...]) -> tuple[tuple[float, ...], ...]:
    first = source
    second = tuple(
        (1.0 - 0.05) * previous + 0.05 * current
        for previous, current in zip(first, source, strict=True)
    )
    third = tuple(
        (1.0 - 0.05) * previous + 0.05 * current
        for previous, current in zip(second, source, strict=True)
    )
    return first, second, third


def _transition_record(
    *,
    events: tuple[str, ...] = transition.EVENT_CHAIN,
    supports: tuple[int, ...] = transition.SUPPORT_CHAIN,
    final: tuple[float, ...] | None = None,
    cue: tuple[float, ...] | None = None,
) -> dict[str, object]:
    source, observed = _source_values()
    prototype = _prototypes(source)[-1] if final is None else final
    return runner._lc02_transition_record(
        ppb_steps=tuple(
            (source, event, support)
            for event, support in zip(events, supports, strict=True)
        ),
        recorded_final_values=prototype,
        recorded_hypothesis_values=prototype[24:],
        observed_cue_values=observed if cue is None else cue,
    )


def _case(case_id: str, transition_record: dict[str, object] | None) -> dict[str, object]:
    expected = runner.EXPECTED_CASES[case_id]
    primary = {
        "decision": expected[0],
        "a_status": expected[1],
        "b_status": expected[2],
        "hypothesis_area": expected[3],
        "hypothesis_values_digest": runner.EXPECTED_HYPOTHESIS_VALUE_DIGESTS.get(case_id),
    }
    return {
        "case_id": case_id,
        "primary": primary,
        "baseline": copy.deepcopy(primary),
        "prototype_transition_evaluation": transition_record,
        "prestate_digest": "a" * 64,
        "poststate_digest": "a" * 64,
        "read_only": True,
    }


class S2LHLC02TransitionIntegrationQualificationTests(unittest.TestCase):
    def test_01_runner_records_exact_lc02_support_and_digests(self) -> None:
        record = _transition_record()
        self.assertEqual(3, record["support_count"])
        self.assertEqual(runner.LC02_FINAL_PROTOTYPE_DIGEST, record["prototype_full_digest"])
        self.assertEqual(
            runner.EXPECTED_HYPOTHESIS_VALUE_DIGESTS["LC02"],
            record["hypothesis_masked_digest"],
        )
        self.assertEqual(transition.INTEGRITY_VALID, record["prototype_transition_integrity"])
        self.assertEqual(transition.FUNCTIONAL_MATCH, record["functional_observed_band_match"])
        self.assertEqual(
            record["integration_digest"],
            runner._digest({key: value for key, value in record.items() if key != "integration_digest"}),
        )

    def test_02_event_and_support_chain_carries_equal_input_order(self) -> None:
        for events, supports in (
            (("MATCHED", "CREATED", "MATCHED"), transition.SUPPORT_CHAIN),
            (transition.EVENT_CHAIN, (1, 3, 2)),
        ):
            with self.subTest(events=events, supports=supports), self.assertRaises(transition.S2LGError):
                _transition_record(events=events, supports=supports)

    def test_03_integrity_and_functional_match_remain_separate(self) -> None:
        source, _ = _source_values()
        changed = list(_prototypes(source)[-1])
        changed[24] += 1e-12
        integrity_failure = _transition_record(final=tuple(changed))
        self.assertEqual(transition.INTEGRITY_INVALID, integrity_failure["prototype_transition_integrity"])
        self.assertEqual(transition.FUNCTIONAL_MATCH, integrity_failure["functional_observed_band_match"])
        functional_failure = _transition_record(cue=(1.0,) * 24)
        self.assertEqual(transition.INTEGRITY_VALID, functional_failure["prototype_transition_integrity"])
        self.assertEqual(transition.FUNCTIONAL_NO_MATCH, functional_failure["functional_observed_band_match"])

    def test_04_runner_evaluation_binds_both_lc02_claims(self) -> None:
        cases = [
            _case(case_id, _transition_record() if case_id == "LC02" else None)
            for case_id in runner.CASE_ORDER
        ]
        result = runner.evaluate_cases(cases)
        self.assertEqual("S2LD_FUNCTION_CONFIRMED", result["status"])
        self.assertIs(result["claims"]["lc02-prototype-transition-integrity"], True)
        self.assertIs(result["claims"]["lc02-functional-observed-band-match"], True)
        changed = copy.deepcopy(cases)
        changed[1]["prototype_transition_evaluation"]["prototype_transition_integrity"] = transition.INTEGRITY_INVALID
        self.assertEqual("S2LD_FUNCTION_FALSIFIED", runner.evaluate_cases(changed)["status"])

    def test_05_verifier_accepts_exact_record_and_rejects_isolated_mutations(self) -> None:
        record = _transition_record()
        issues: list[str] = []
        self.assertEqual((True, True), verifier._verify_lc02_transition(record, issues))
        self.assertEqual([], issues)
        for key, value in (
            ("support_count", 2),
            ("prototype_full_digest", "0" * 64),
            ("hypothesis_masked_digest", "1" * 64),
            ("event_chain", ["MATCHED", "CREATED", "MATCHED"]),
            ("functional_observed_band_match", transition.FUNCTIONAL_NO_MATCH),
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = value
            mutated["integration_digest"] = verifier._digest(
                {name: item for name, item in mutated.items() if name != "integration_digest"}
            )
            mutation_issues: list[str] = []
            integrity, functional = verifier._verify_lc02_transition(mutated, mutation_issues)
            self.assertTrue(mutation_issues)
            self.assertFalse(integrity and functional)

    def test_06_gate_and_historical_evidence_remain_unchanged(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertEqual(
            "827597089a5b2e93c80d12ef50d326bfa79ebc47281770f1b2c6708e9218b06f",
            hashlib.sha256(HISTORICAL_RESULT.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            "2711b2a7ca1f9c480909469d5dde08745556911314683cefb257c8e1a490bdb7",
            hashlib.sha256(HISTORICAL_VERIFICATION.read_bytes()).hexdigest(),
        )
        historical = json.loads(HISTORICAL_VERIFICATION.read_text(encoding="ascii"))
        self.assertEqual("S2LD_FUNCTION_FALSIFIED", historical["functional_status"])
        self.assertEqual("lc02-hypothesis", historical["only_failed_claim"])


if __name__ == "__main__":
    unittest.main()
