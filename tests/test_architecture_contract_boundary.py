from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import architecture_contract
from mcm_field_organism import architecture_readiness
from mcm_field_organism import current_api
from mcm_field_organism import receptor_process_contract


class ArchitectureContractBoundaryTests(unittest.TestCase):
    def test_legacy_root_current_and_process_contract_keep_identity(self) -> None:
        roles = (
            architecture_contract.EvidenceLevel,
            architecture_contract.RuntimePermission,
        )
        for role in roles:
            with self.subTest(role=role.__name__):
                self.assertIs(role, getattr(architecture_readiness, role.__name__))
                self.assertIs(role, getattr(root_api, role.__name__))
                self.assertIs(role, getattr(current_api, role.__name__))
                self.assertIs(
                    role,
                    getattr(receptor_process_contract, role.__name__),
                )

    def test_contract_boundary_does_not_expose_architecture_plan(self) -> None:
        forbidden = (
            "ArchitectureBoundary",
            "ArchitectureReadinessPlan",
            "BoundaryKind",
            "reference_architecture_plan",
        )
        for name in forbidden:
            with self.subTest(role=name):
                self.assertFalse(hasattr(architecture_contract, name))


if __name__ == "__main__":
    unittest.main()
