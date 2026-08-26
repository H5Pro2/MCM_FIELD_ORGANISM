from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from mcm_field_organism.e1_confirmation_full_published_run_contract import (
    S1_EC16_POLICY_DIGEST,
    S1_EC16_REQUIRED_GATES,
    S1_EC16_TRANSITIONS,
    audit_full_formation_published_run_contract,
    prepare_full_formation_published_run_contract,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationFullPublishedRunContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        with TemporaryDirectory() as directory:
            run = prepare_e1_confirmation_synthetic_run_contract(
                descriptor, Path(directory)
            )
            bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
                run, UPSTREAM
            )
            cls.preflight = preflight_prepared_full_formation_resources(bundle)

    def test_contract_binds_all_upstream_policies_and_transitions(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_published_run_contract(
                self.preflight, Path(directory)
            )
            audit = audit_full_formation_published_run_contract(
                contract, self.preflight
            )

            self.assertEqual(S1_EC16_POLICY_DIGEST, contract.policy_digest)
            self.assertEqual(S1_EC16_TRANSITIONS, contract.transitions)
            self.assertEqual(S1_EC16_REQUIRED_GATES, contract.required_gates)
            self.assertTrue(audit.ready_for_synthetic_composition)
            self.assertFalse(audit.execution_authorized)

    def test_policy_is_path_independent_but_run_contract_is_path_bound(self) -> None:
        contracts = []
        for _ in range(2):
            with TemporaryDirectory() as directory:
                contracts.append(
                    prepare_full_formation_published_run_contract(
                        self.preflight, Path(directory)
                    )
                )

        self.assertEqual(contracts[0].policy_digest, contracts[1].policy_digest)
        self.assertNotEqual(contracts[0].digest(), contracts[1].digest())

    def test_static_audit_creates_no_marker_report_or_field_execution(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_published_run_contract(
                self.preflight, Path(directory)
            )
            audit_full_formation_published_run_contract(contract, self.preflight)

            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())

    def test_contract_and_audit_sources_contain_no_execution_or_publication(self) -> None:
        source = inspect.getsource(prepare_full_formation_published_run_contract)
        source += inspect.getsource(audit_full_formation_published_run_contract)

        for forbidden in (
            "_run_arm",
            "run_small_five_arm_formation_in_memory",
            "execute_prepared_full_formation_lifecycle",
            "publish_full_formation_handoff_fixture_once",
            "_exclusive_marker",
            "_atomic_publish",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1ec13_and_terminal_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_published_run_contract(
                self.preflight, Path(directory)
            )
            audit_full_formation_published_run_contract(contract, self.preflight)
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
