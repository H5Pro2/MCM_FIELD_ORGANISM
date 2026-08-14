from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from mcm_field_organism.e1_confirmation_canonical_result_compositor import (
    E1ConfirmationCanonicalResultCompositorError,
    _compose_bound_result_core,
    compose_e1_confirmation_canonical_result,
)
from mcm_field_organism.e1_confirmation_canonical_result_handoff import (
    prepare_e1_confirmation_canonical_result_handoff,
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
        binding,
        chain,
        formation,
        probe_handoff,
        probes,
    )
    return binding, chain, formation, probe_handoff, result_handoff, probes


class E1ConfirmationCanonicalResultCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.binding,
            cls.chain,
            cls.formation,
            cls.probe_handoff,
            cls.result_handoff,
            cls.probes,
        ) = _inputs()

    def test_synthetic_bound_core_builds_complete_result(self) -> None:
        result = _compose_bound_result_core(
            self.chain, self.formation, self.probes
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            item.refinement_id for item in result.refinements
        ))
        self.assertEqual(13, len(result.metrics))
        self.assertEqual(11, len(result.controls))
        self.assertTrue(all(dict(result.controls).values()))

    def test_synthetic_bound_core_matches_existing_result_logic(self) -> None:
        result = _compose_bound_result_core(
            self.chain, self.formation, self.probes
        )

        self.assertEqual("NUMERICALLY_UNDECIDABLE", result.technical_decision)
        self.assertEqual(
            "ff98c96b2ccecd0a23e1ba02ce1bf8827d672aae72953b9e04d18c9062ad510c",
            result.result_digest,
        )
        self.assertEqual(0.0, result.refinements[-1].d_probe_s)
        self.assertEqual(0.0, result.refinements[-1].d_probe_h)

    def test_synthetic_bound_core_is_repeatable(self) -> None:
        first = _compose_bound_result_core(
            self.chain, self.formation, self.probes
        )
        second = _compose_bound_result_core(
            self.chain, self.formation, self.probes
        )

        self.assertEqual(first, second)

    def test_invalid_probe_inventory_fails_closed(self) -> None:
        with self.assertRaises(E1ConfirmationCanonicalResultCompositorError):
            _compose_bound_result_core(
                self.chain, self.formation, self.probes[:2]
            )

    def test_canonical_entrypoint_stops_before_composition(self) -> None:
        with patch(
            "mcm_field_organism.e1_confirmation_canonical_result_compositor."
            "_compose_bound_result_core",
            side_effect=AssertionError("result composed"),
        ):
            with self.assertRaisesRegex(
                E1ConfirmationCanonicalResultCompositorError,
                "remains locked",
            ):
                compose_e1_confirmation_canonical_result(
                    self.binding,
                    self.chain,
                    self.formation,
                    self.probe_handoff,
                    self.result_handoff,
                    self.probes,
                )

    def test_compositor_has_no_runtime_or_persistence_path(self) -> None:
        source = inspect.getsource(compose_e1_confirmation_canonical_result)
        for forbidden in (
            "run_e1_confirmation_canonical_seven_arm_probe",
            "run_e1_asynchronous_field",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_compositor_keeps_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        _compose_bound_result_core(self.chain, self.formation, self.probes)

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalResultCompositorError",
            "compose_e1_confirmation_canonical_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
