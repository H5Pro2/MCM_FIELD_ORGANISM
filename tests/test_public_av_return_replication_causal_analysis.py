from __future__ import annotations

import unittest

from mcm_field_organism.public_av_return_replication_causal_analysis import (
    analyze_public_av_return_replication_causal_contrasts,
    public_av_return_replication_causal_analysis_public_roles,
)
from mcm_field_organism.public_av_return_replication_execution import (
    PublicAVReturnReplicationArmResult,
    PublicAVReturnReplicationExecution,
)


IDS = (
    "return.continued.full_state", "return.fresh_stage_two",
    "control.activation_only_carry", "control.afterimage_only_carry",
    "control.stage_two_order_permuted", "control.stage_two_sequence_withheld",
)
ACT = (
    (0.0, .017293651956615398, 0.0, .017293651956615398, .012491996276939484, .021061313972438742),
    (.017293651956615398, 0.0, .017293651956615398, 0.0, .010251972869725621, .011481558846333728),
    (0.0, .017293651956615398, 0.0, .017293651956615398, .012491996276939484, .021061313972438742),
    (.017293651956615398, 0.0, .017293651956615398, 0.0, .010251972869725621, .011481558846333728),
    (.012491996276939484, .010251972869725621, .012491996276939484, .010251972869725621, 0.0, .011078336010613223),
    (.021061313972438742, .011481558846333728, .021061313972438742, .011481558846333728, .011078336010613223, 0.0),
)
AFTER = (
    (0.0, .017580295681599252, .003527301811182163, .014223839182877845, .009650827900181767, .0017208269679413624),
    (.017580295681599252, 0.0, .014223839182877824, .0035273018111821545, .02718958763859674, .01733642864552728),
    (.003527301811182163, .014223839182877824, 0.0, .010867382684156419, .013139919076486147, .003112589462649456),
    (.014223839182877845, .0035273018111821545, .010867382684156419, 0.0, .023833131139875334, .013979972146805875),
    (.009650827900181767, .02718958763859674, .013139919076486147, .023833131139875334, 0.0, .010326414905583232),
    (.0017208269679413624, .01733642864552728, .003112589462649456, .013979972146805875, .010326414905583232, 0.0),
)


def documented_execution() -> PublicAVReturnReplicationExecution:
    arms = tuple(PublicAVReturnReplicationArmResult(
        arm_id, 56, 0 if index == 5 else 56, "same-stage-one", None, None,
        f"snapshot-{index}", f"layer-{index}", (float(index),), (float(index),),
        "withheld_contact_free" if index == 5 else "audited_reduced_sequence", None,
    ) for index, arm_id in enumerate(IDS))
    equality = tuple(tuple(i == j for j in range(6)) for i in range(6))
    return PublicAVReturnReplicationExecution(
        "public.av.nasa-earthrise.return-replication.execution.v1", "runner", "preflight",
        "source", "public.media.pts_ns", 500_000_000, 100_000_000, arms,
        ACT, AFTER, equality, equality,
    )


class PublicAVReturnReplicationCausalAnalysisTests(unittest.TestCase):
    def test_four_preregistered_primary_contrasts_are_reported(self) -> None:
        analysis = analyze_public_av_return_replication_causal_contrasts(documented_execution())
        self.assertEqual(4, len(analysis.primary_contrasts))
        self.assertTrue(analysis.all_stage_one_snapshots_equal)

    def test_full_and_fresh_differ_in_both_components(self) -> None:
        item = analyze_public_av_return_replication_causal_contrasts(documented_execution()).primary_contrasts[0]
        self.assertTrue(item.activation_technically_distinct)
        self.assertTrue(item.afterimage_technically_distinct)

    def test_component_auxiliaries_preserve_activation_equality_but_not_digest_equality(self) -> None:
        analysis = analyze_public_av_return_replication_causal_contrasts(documented_execution())
        for item in analysis.component_auxiliary_contrasts:
            self.assertEqual(0.0, item.activation_linf)
            self.assertGreater(item.afterimage_linf, 0.0)
            self.assertTrue(item.field_digest_technically_distinct)

    def test_permutation_and_withheld_primary_contrasts_are_technically_distinct(self) -> None:
        analysis = analyze_public_av_return_replication_causal_contrasts(documented_execution())
        for item in analysis.primary_contrasts[2:]:
            self.assertTrue(item.activation_technically_distinct)
            self.assertTrue(item.afterimage_technically_distinct)
            self.assertTrue(item.field_digest_technically_distinct)

    def test_no_threshold_or_claim_role_is_added(self) -> None:
        analysis = analyze_public_av_return_replication_causal_contrasts(documented_execution())
        self.assertFalse(analysis.thresholds_defined)
        self.assertFalse(analysis.causal_mechanism_proven)
        forbidden = {"memory_score", "organization_score", "meaning", "reward", "target_topology"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_causal_analysis_public_roles()))


if __name__ == "__main__":
    unittest.main()
