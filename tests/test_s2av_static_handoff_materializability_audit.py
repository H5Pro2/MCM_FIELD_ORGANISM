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
        "S2AV_STATISCHER_HANDOFF_VERTRAGS_VOLLSTAENDIGKEITS_"
        "NICHTZIRKULARITAETS_KAUSALPARTITIONS_UND_"
        "MATERIALISIERBARKEITSAUDIT_V1.json"
    )
)
BOUND = {
    "s2au_contract": (
        ROOT
        / "docs"
        / (
            "S2AU_STATISCHER_BILDUNG_ZU_SPAETER_READ_ONLY_PROBE_HANDOFF_"
            "FUNKTIONS_PROVENIENZ_STABILISIERUNGS_PARTITIONS_UND_"
            "FALSIFIKATIONSVERTRAG_V1.json"
        )
    ),
    "s2au_document": (
        ROOT
        / "docs"
        / (
            "S2AU_STATISCHER_BILDUNG_ZU_SPAETER_READ_ONLY_PROBE_HANDOFF_"
            "FUNKTIONS_PROVENIENZ_STABILISIERUNGS_PARTITIONS_UND_"
            "FALSIFIKATIONSVERTRAG.md"
        )
    ),
    "s2au_static_validator": (
        ROOT / "tests" / "test_s2au_static_formation_to_later_probe_handoff_contract.py"
    ),
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "active_batch_binder": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "ppb1_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "browser_batch": PACKAGE / "browser_receptor_bridge.py",
    "receptor_time": PACKAGE / "receptor_time_model.py",
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


class S2AVStaticHandoffMaterializabilityAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_completeness_noncircularity_and_partition_pass(self) -> None:
        audit = _audit()
        self.assertEqual("PASS", audit["completeness_audit"]["status"])
        self.assertEqual("PASS", audit["noncircularity_audit"]["status"])
        self.assertEqual("PASS", audit["causal_partition_audit"]["status"])
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_fixture_requires_authentic_three_step_formation_per_modality(
        self,
    ) -> None:
        fixture = _audit()["required_synthetic_fixture_anatomy"]
        self.assertEqual(3, fixture["positive_formation_frames_per_modality"])
        self.assertEqual(
            "ACTUAL_PRIVATE_S2AR_OWNER_AND_CONSUMER_EXECUTION",
            fixture["formation_result_source"],
        )
        self.assertFalse(fixture["manual_forged_bank_or_formation_result_allowed"])
        self.assertEqual(1, fixture["later_probe_frames_per_modality"])

    def test_private_implementation_is_eligible_but_not_authorized(self) -> None:
        audit = _audit()
        gate = audit["implementation_eligibility"]
        self.assertTrue(gate["private_handoff_and_synthetic_tests_materializable"])
        self.assertFalse(gate["implementation_authorized_in_s2av"])
        self.assertEqual(9, len(audit["required_synthetic_test_roles"]))
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
