from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "mcm_field_organism"
ARTIFACT = (
    ROOT
    / "docs"
    / (
        "S2BC_STATISCHER_QUELLGEBUNDENER_BASELINE_MATERIALISIERBARKEITS_"
        "NICHTZIRKULARITAETS_UND_INFORMATIONSFLUSS_PREFLIGHT_V1.json"
    )
)
BOUND = {
    "s2bb_contract": (
        ROOT
        / "docs"
        / (
            "S2BB_QUELLGEBUNDENER_AKTIVER_STATISCHER_PROTOTYPBASELINE_"
            "RECEIPT_UND_COMPARATOR_MATERIALISIERUNGSVERTRAG_V1.json"
        )
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
}


def _audit() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2BCStaticBaselineMaterializabilityPreflightTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_all_roles_pass_with_no_implementation_blocker(self) -> None:
        audit = _audit()
        self.assertEqual(12, audit["checked_role_count"])
        self.assertEqual(audit["checked_role_count"], audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual([], audit["open_implementation_blockers"])

    def test_baseline_input_boundary_excludes_candidate_state(self) -> None:
        audit = _audit()
        formation = next(
            item
            for item in audit["exact_private_function_boundaries"]
            if item["function_role"] == "FORM_BASELINE"
        )
        self.assertEqual(
            [
                "PPB1ActiveReceptorBatchEnvelope",
                "PPB1ReceptorProfileBinding",
            ],
            formation["allowed_inputs"],
        )
        self.assertIn("PPB1BankState", formation["forbidden_inputs"])
        self.assertFalse(
            audit["noncircularity_audit"]["circular_information_path_present"]
        )

    def test_no_implementation_execution_or_claim_is_present(self) -> None:
        audit = _audit()
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertTrue(
            audit["implementation_readiness"][
                "implementation_may_be_separately_authorized"
            ]
        )
        self.assertFalse(
            audit["implementation_readiness"][
                "execution_may_be_separately_authorized"
            ]
        )


if __name__ == "__main__":
    unittest.main()
