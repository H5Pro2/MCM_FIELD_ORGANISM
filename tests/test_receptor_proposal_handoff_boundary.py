from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import current_api
from mcm_field_organism import neutral_asynchronous_field_runtime
from mcm_field_organism import receptor_proposal_handoff
from mcm_field_organism import receptor_proposal_handoff_audit
from mcm_field_organism import transient_dock_trajectory


class ReceptorProposalHandoffBoundaryTests(unittest.TestCase):
    def test_legacy_root_current_and_runtime_roles_keep_identity(self) -> None:
        roles = (
            receptor_proposal_handoff.ReceptorProposalHandoffError,
            receptor_proposal_handoff.ReceptorProposalCompletionGroup,
            receptor_proposal_handoff.ReceptorProposalBatch,
            receptor_proposal_handoff.ReceptorProposalHandoff,
            receptor_proposal_handoff.handoff_receptor_completion_groups,
        )
        for role in roles:
            with self.subTest(role=role.__name__):
                self.assertIs(
                    role,
                    getattr(receptor_proposal_handoff_audit, role.__name__),
                )
                self.assertIs(role, getattr(root_api, role.__name__))
                self.assertIs(role, getattr(current_api, role.__name__))

        self.assertIs(
            receptor_proposal_handoff.ReceptorProposalHandoff,
            neutral_asynchronous_field_runtime.ReceptorProposalHandoff,
        )
        self.assertIs(
            receptor_proposal_handoff.ReceptorProposalBatch,
            transient_dock_trajectory.ReceptorProposalBatch,
        )

    def test_operational_boundary_does_not_expose_audit_roles(self) -> None:
        self.assertFalse(
            hasattr(receptor_proposal_handoff, "ProposalSegmentationComparison")
        )
        self.assertFalse(
            hasattr(receptor_proposal_handoff, "run_receptor_proposal_handoff_audit")
        )
        self.assertFalse(
            hasattr(
                receptor_proposal_handoff,
                "receptor_proposal_handoff_audit_public_roles",
            )
        )


if __name__ == "__main__":
    unittest.main()
