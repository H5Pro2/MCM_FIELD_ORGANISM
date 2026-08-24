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
    / "S2BP_AVPC1_BEGRENZTE_RELATION_STATISCHER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
)
BOUND = {
    "s2bo_contract": (
        ROOT
        / "docs"
        / (
            "S2BO_AVPC1_BEGRENZTER_RELATIONSZUSTANDS_KAPAZITAETS_SUPPORT_"
            "KONFLIKT_RECEIPT_UND_BASELINE_VERTRAG_V1.json"
        )
    ),
    "s2bn_closure_audit": (
        ROOT
        / "docs"
        / "S2BN_AVPC1_AUDIO_ONLY_IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT_V1.json"
    ),
    "audio_only_envelope": PACKAGE / "_avpc1_audio_only_probe_envelope.py",
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "state_lifecycle": PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "receptor_time_alignment": PACKAGE / "receptor_time_alignment.py",
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
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


class S2BPStaticAVPC1BoundedRelationPreflightTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_type_function_and_transition_inventory_is_exact(self) -> None:
        audit = _audit()
        self.assertEqual(6, len(audit["new_private_types"]))
        self.assertEqual(4, len(audit["new_private_functions"]))
        transition = audit["transition_totality"]
        self.assertEqual(9, transition["ordered_case_count"])
        self.assertEqual(3, transition["accepted_cases"])
        self.assertEqual(6, transition["rejected_cases"])

    def test_prototype_identity_gate_and_probe_are_fail_closed(self) -> None:
        audit = _audit()
        gate = audit["prototype_identity_uniqueness_gate"]
        probe = audit["read_only_probe_materialization"]
        self.assertTrue(
            gate[
                "stabilized_auditory_prototype_digests_must_be_unique_within_frozen_bank"
            ]
        )
        self.assertTrue(
            gate[
                "stabilized_visual_prototype_digests_must_be_unique_within_frozen_bank"
            ]
        )
        self.assertFalse(probe["current_visual_input_allowed"])
        self.assertFalse(probe["calls_existing_s1wu_probe_in_relation_kernel"])

    def test_strongest_baseline_uses_same_budget_and_kernel(self) -> None:
        baseline = _audit()["baseline_architecture"]
        self.assertTrue(
            baseline[
                "candidate_and_strongest_baseline_use_same_generic_transition_kernel"
            ]
        )
        self.assertTrue(
            baseline["candidate_and_baseline_state_instances_are_separate"]
        )
        self.assertTrue(
            baseline[
                "capacity_support_exposure_conflict_and_full_policies_equal"
            ]
        )

    def test_preflight_passes_without_execution(self) -> None:
        audit = _audit()
        self.assertEqual(
            (9, 9, 0, 0),
            (
                audit["checked_role_count"],
                audit["passed_role_count"],
                audit["blocked_role_count"],
                audit["open_blocker_count"],
            ),
        )
        self.assertTrue(
            all(value == 0 for value in audit["execution"].values())
        )
        self.assertFalse(
            audit["implementation_authorization"][
                "authorized_without_separate_next_step"
            ]
        )


if __name__ == "__main__":
    unittest.main()
