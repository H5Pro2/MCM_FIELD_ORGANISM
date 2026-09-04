from __future__ import annotations

from dataclasses import FrozenInstanceError
import ast
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2lg_private_ppb_transition_evaluation as subject


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json"
QUALIFICATION_ID = "s2lg-ppb-transition-qualification-20260904-01"


def _source_values() -> tuple[tuple[float, ...], tuple[float, ...]]:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != "87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3":
        raise AssertionError("S2-KY source hash differs")
    value = json.loads(raw.decode("ascii"))
    return (
        tuple(value["measurements"]["CANDIDATE_PLUS"]["values"]),
        tuple(value["measurements"]["CUE_LOW"]["values"][:24]),
    )


def _prototypes(p: tuple[float, ...]) -> tuple[tuple[float, ...], ...]:
    one = tuple((1.0 - 0.05) * old + 0.05 * current for old, current in zip(p, p, strict=True))
    two = tuple((1.0 - 0.05) * old + 0.05 * current for old, current in zip(one, p, strict=True))
    return p, one, two


def _run(
    *,
    events: tuple[str, ...] = subject.EVENT_CHAIN,
    supports: tuple[int, ...] = subject.SUPPORT_CHAIN,
    recorded: tuple[float, ...] | None = None,
    hypothesis: tuple[float, ...] | None = None,
    cue: tuple[float, ...] | None = None,
):
    p, low = _source_values()
    final = _prototypes(p)[-1]
    return subject.derive_and_evaluate_lc02(
        ppb_inputs=(p, p, p),
        event_chain=events,
        support_chain=supports,
        recorded_final_values=final if recorded is None else recorded,
        recorded_hypothesis_values=final[24:] if hypothesis is None else hypothesis,
        observed_cue_values=low if cue is None else cue,
    )


class S2LGPrivatePPBTransitionEvaluationTests(unittest.TestCase):
    def test_01_exact_binary64_chain_and_source_boundary(self) -> None:
        result = _run()
        self.assertEqual(subject.EVENT_CHAIN, tuple(step.event for step in result.steps))
        self.assertEqual(subject.SUPPORT_CHAIN, tuple(step.support for step in result.steps))
        self.assertEqual((0, 10, 10), tuple(step.changed_position_count_from_input for step in result.steps))
        source = (ROOT / "tools/_s2lg_private_ppb_transition_evaluation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports.update(node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        self.assertFalse(any(name.startswith(("mcm_field_organism", "tools._s2")) for name in imports))
        self.assertIn("(1.0 - UPDATE_RATE) * previous_value + UPDATE_RATE * current_value", source)

    def test_02_all_full_and_masked_digests_match_contract(self) -> None:
        result = _run()
        self.assertEqual(subject.STEP_FULL_DIGESTS, tuple(step.prototype_full_digest for step in result.steps))
        self.assertEqual(subject.STEP_MASKED_DIGESTS, tuple(step.prototype_masked_digest for step in result.steps))
        self.assertEqual(subject.STEP_FULL_DIGESTS[-1], result.derived_final_full_digest)
        self.assertEqual(subject.STEP_MASKED_DIGESTS[-1], result.derived_final_masked_digest)

    def test_03_event_and_support_order_carry_identity_for_equal_inputs(self) -> None:
        for events, supports in (
            (("MATCHED", "CREATED", "MATCHED"), subject.SUPPORT_CHAIN),
            (subject.EVENT_CHAIN, (1, 3, 2)),
            (subject.EVENT_CHAIN, (1, 2, 2)),
        ):
            with self.subTest(events=events, supports=supports), self.assertRaises(subject.S2LGError):
                _run(events=events, supports=supports)

    def test_04_changed_input_or_update_order_fails_closed(self) -> None:
        p, low = _source_values()
        changed = list(p)
        changed[0] += 1e-12
        with self.assertRaises(subject.S2LGError):
            subject.derive_and_evaluate_lc02(
                ppb_inputs=(p, tuple(changed), p),
                event_chain=subject.EVENT_CHAIN,
                support_chain=subject.SUPPORT_CHAIN,
                recorded_final_values=_prototypes(p)[-1],
                recorded_hypothesis_values=_prototypes(p)[-1][24:],
                observed_cue_values=low,
            )
        self.assertEqual(0.05, subject.UPDATE_RATE)

    def test_05_integrity_and_functional_match_are_independent(self) -> None:
        p, _ = _source_values()
        final = _prototypes(p)[-1]
        changed = list(final)
        changed[24] += 1e-12
        result = _run(recorded=tuple(changed), hypothesis=tuple(changed[24:]))
        self.assertEqual(subject.INTEGRITY_INVALID, result.transition_integrity_status)
        self.assertEqual(subject.FUNCTIONAL_MATCH, result.functional_match_status)
        far_cue = (1.0,) * 24
        no_match = _run(cue=far_cue)
        self.assertEqual(subject.INTEGRITY_VALID, no_match.transition_integrity_status)
        self.assertEqual(subject.FUNCTIONAL_NO_MATCH, no_match.functional_match_status)

    def test_06_lc02_final_binding_is_exact_immutable_and_not_original_p(self) -> None:
        result = _run()
        self.assertEqual(subject.INTEGRITY_VALID, result.transition_integrity_status)
        self.assertEqual(subject.FUNCTIONAL_MATCH, result.functional_match_status)
        self.assertEqual("8408f2f4452b64cd8bf53847b91de8d8a34d29f64191c344cf8684726974191e", result.recorded_hypothesis_masked_digest)
        self.assertNotEqual("1622004a498c487579e941a9b99193eded1a966420f916140251e21933ee1ba9", result.recorded_hypothesis_masked_digest)
        with self.assertRaises(FrozenInstanceError):
            result.transition_integrity_status = subject.INTEGRITY_INVALID  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
