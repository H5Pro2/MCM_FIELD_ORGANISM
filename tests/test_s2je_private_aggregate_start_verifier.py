"""Focused one-shot qualification of the S2-JE START-binding verifier."""

from __future__ import annotations

import unittest

from tools import _s2ig_private_result_verifier as verifier


QUALIFICATION_ID = "s2je-aggregate-start-verifier-20260901-01"


def _digest(label: str) -> str:
    return verifier._digest({"s2je_neutral": label})


def _valid_case(case_id: str) -> tuple[str, dict[str, str], dict[str, str], dict[str, str]]:
    dual = _digest(f"{case_id}-dual")
    signal = _digest(f"{case_id}-signal")
    baseline = _digest(f"{case_id}-baseline")
    signal_start = {
        "dual_probe_binding_digest": dual,
        "aggregate_visibility_binding_digest": signal,
    }
    baseline_start = {
        "dual_probe_binding_digest": dual,
        "aggregate_visibility_binding_digest": baseline,
    }
    evidence = {
        "aggregate_visibility_binding_pair_digest": verifier._digest(
            (signal, baseline)
        )
    }
    return dual, signal_start, baseline_start, evidence


def _errors(
    case_id: str,
    dual: object,
    signal_start: object,
    baseline_start: object,
    evidence: object,
) -> list[str]:
    errors: list[str] = []
    verifier._validate_s2je_aggregate_start_pair(
        case_id=case_id,
        dual_probe_binding_digest=dual,
        signal_start_input=signal_start,
        baseline_start_input=baseline_start,
        case_evidence=evidence,
        errors=errors,
    )
    return errors


class S2JEPrivateAggregateStartVerifierTests(unittest.TestCase):
    def test_01_all_sixteen_ordered_arm_bindings_are_accepted(self) -> None:
        for index in range(1, 9):
            case_id = f"c{index:02d}"
            self.assertEqual([], _errors(case_id, *_valid_case(case_id)))

    def test_02_missing_dual_binding_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c01")
        signal.pop("dual_probe_binding_digest")
        self.assertEqual(
            ["aggregate START binding shape differs: c01"],
            _errors("c01", dual, signal, baseline, evidence),
        )

    def test_03_missing_aggregate_binding_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c02")
        baseline.pop("aggregate_visibility_binding_digest")
        self.assertEqual(
            ["aggregate START binding shape differs: c02"],
            _errors("c02", dual, signal, baseline, evidence),
        )

    def test_04_additional_start_binding_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c03")
        signal["unexpected"] = _digest("unexpected")
        self.assertEqual(
            ["aggregate START binding shape differs: c03"],
            _errors("c03", dual, signal, baseline, evidence),
        )

    def test_05_invalid_aggregate_digest_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c04")
        signal["aggregate_visibility_binding_digest"] = "not-a-digest"
        self.assertEqual(
            ["aggregate START role binding differs: c04"],
            _errors("c04", dual, signal, baseline, evidence),
        )

    def test_06_swapped_arm_bindings_are_rejected_by_ordered_pair(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c05")
        signal_digest = signal["aggregate_visibility_binding_digest"]
        signal["aggregate_visibility_binding_digest"] = baseline[
            "aggregate_visibility_binding_digest"
        ]
        baseline["aggregate_visibility_binding_digest"] = signal_digest
        self.assertEqual(
            ["aggregate START pair digest differs: c05"],
            _errors("c05", dual, signal, baseline, evidence),
        )

    def test_07_wrong_pair_digest_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c06")
        evidence["aggregate_visibility_binding_pair_digest"] = _digest("wrong")
        self.assertEqual(
            ["aggregate START pair digest differs: c06"],
            _errors("c06", dual, signal, baseline, evidence),
        )

    def test_08_duplicate_role_binding_is_rejected(self) -> None:
        dual, signal, baseline, evidence = _valid_case("c07")
        baseline["aggregate_visibility_binding_digest"] = signal[
            "aggregate_visibility_binding_digest"
        ]
        evidence["aggregate_visibility_binding_pair_digest"] = verifier._digest(
            (
                signal["aggregate_visibility_binding_digest"],
                baseline["aggregate_visibility_binding_digest"],
            )
        )
        self.assertEqual(
            ["aggregate START role binding differs: c07"],
            _errors("c07", dual, signal, baseline, evidence),
        )


if __name__ == "__main__":
    unittest.main()
