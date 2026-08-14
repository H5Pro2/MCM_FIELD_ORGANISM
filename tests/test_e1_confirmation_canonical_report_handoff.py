from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from mcm_field_organism.e1_confirmation_canonical_report_handoff import (
    E1ConfirmationCanonicalReportHandoffError,
    prepare_e1_confirmation_canonical_report_handoff,
)
from mcm_field_organism.e1_confirmation_canonical_result_compositor import (
    _compose_bound_result_core,
)
from mcm_field_organism.e1_confirmation_canonical_result_handoff import (
    prepare_e1_confirmation_canonical_result_handoff,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    S1_EB4_REPORT_FIELDS,
)
from tests.test_e1_confirmation_canonical_probe_handoff import (
    _inputs_with_substituted_formation,
)
from tests.test_e1_confirmation_canonical_result_handoff import (
    _canonicalized_probe_results,
)


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _inputs():
    binding, chain, formation = _inputs_with_substituted_formation()
    probe_handoff = prepare_e1_confirmation_canonical_probe_handoff(
        binding, chain, formation
    )
    probes = _canonicalized_probe_results(binding, probe_handoff)
    result_handoff = prepare_e1_confirmation_canonical_result_handoff(
        binding, chain, formation, probe_handoff, probes
    )
    result = _compose_bound_result_core(chain, formation, probes)
    return binding, chain, result_handoff, result


class E1ConfirmationCanonicalReportHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.result_handoff, cls.result = _inputs()

    def test_handoff_binds_complete_report_surface(self) -> None:
        handoff = prepare_e1_confirmation_canonical_report_handoff(
            self.binding, self.chain, self.result_handoff, self.result
        )

        self.assertEqual(S1_EB4_REPORT_FIELDS, handoff.report_fields)
        self.assertEqual(4, len(handoff.source_digests))
        self.assertEqual(3, len(handoff.plan_digests))
        self.assertEqual(("r2", "r4", "r8"), tuple(
            role for role, _ in handoff.refinement_result_digests
        ))
        self.assertEqual(self.result.result_digest, handoff.result_digest)

    def test_registered_targets_are_exact_distinct_and_free(self) -> None:
        handoff = prepare_e1_confirmation_canonical_report_handoff(
            self.binding, self.chain, self.result_handoff, self.result
        )
        targets = (
            Path(handoff.report_path),
            Path(handoff.attempt_path),
            Path(handoff.lock_path),
        )

        self.assertEqual(
            tuple(item.resolve() for item in TARGETS),
            tuple(item.resolve() for item in targets),
        )
        self.assertEqual(3, len(set(targets)))
        self.assertTrue(all(not item.exists() for item in targets))

    def test_result_state_and_probe_digests_are_bound(self) -> None:
        handoff = prepare_e1_confirmation_canonical_report_handoff(
            self.binding, self.chain, self.result_handoff, self.result
        )

        self.assertEqual(
            self.result_handoff.handoff_digest,
            handoff.result_handoff_digest,
        )
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE", handoff.technical_decision
        )

    def test_invalid_result_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalReportHandoffError,
            "matching result",
        ):
            prepare_e1_confirmation_canonical_report_handoff(
                self.binding, self.chain, self.result_handoff, object()
            )

    def test_handoff_is_repeatable_and_release_roles_stay_closed(self) -> None:
        args = (self.binding, self.chain, self.result_handoff, self.result)
        first = prepare_e1_confirmation_canonical_report_handoff(*args)
        second = prepare_e1_confirmation_canonical_report_handoff(*args)

        self.assertEqual(first, second)
        for role in (
            "execution_permitted",
            "persistence_permitted",
            "retry_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(first, role))

    def test_handoff_has_no_executor_or_file_write_call(self) -> None:
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_report_handoff
        )
        for forbidden in (
            "execute_synthetic_e1_confirmation_once",
            "execute_e1_confirmation_canonical_once(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_handoff_keeps_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        prepare_e1_confirmation_canonical_report_handoff(
            self.binding, self.chain, self.result_handoff, self.result
        )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalReportHandoff",
            "prepare_e1_confirmation_canonical_report_handoff",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
