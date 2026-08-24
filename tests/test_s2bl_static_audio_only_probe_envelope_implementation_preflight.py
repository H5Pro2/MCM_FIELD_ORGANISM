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
    / "S2BL_AVPC1_AUDIO_ONLY_PROBENHUELLE_STATISCHER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
)
BOUND = {
    "s2bk_contract": (
        ROOT / "docs" / "S2BK_AVPC1_PRIVATER_AUDIO_ONLY_PROBENHUELLENVERTRAG_V1.json"
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "state_lifecycle": PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
    "receptor_contract": PACKAGE / "receptor_contract.py",
    "browser_receptor_bridge": PACKAGE / "browser_receptor_bridge.py",
    "browser_world_contract": PACKAGE / "browser_world_contract.py",
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


class S2BLStaticAudioOnlyImplementationPreflightTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_exactly_three_private_types_and_functions_are_bound(self) -> None:
        audit = _audit()
        self.assertEqual(3, len(audit["required_new_private_types"]))
        self.assertEqual(3, len(audit["required_private_functions"]))
        self.assertTrue(audit["target_module"]["private_module"])
        self.assertFalse(audit["target_module"]["public_export_allowed"])

    def test_visual_information_cannot_leave_source_validation(self) -> None:
        boundary = _audit()["source_visual_independence_boundary"]
        self.assertFalse(
            boundary["returned_source_binding_contains_visual_content_or_digest"]
        )
        self.assertFalse(
            boundary["returned_envelope_contains_visual_content_or_digest"]
        )
        self.assertFalse(boundary["matcher_can_receive_parent_batch_or_visual_data"])

    def test_preflight_passes_without_execution(self) -> None:
        audit = _audit()
        self.assertEqual(10, audit["checked_role_count"])
        self.assertEqual(10, audit["passed_role_count"])
        self.assertEqual(0, audit["open_blocker_count"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertTrue(
            audit["implementation_authorization"][
                "private_module_and_synthetic_contract_tests_ready"
            ]
        )


if __name__ == "__main__":
    unittest.main()
