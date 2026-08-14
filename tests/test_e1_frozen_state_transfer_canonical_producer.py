from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_canonical_producer import (
    E1FrozenStateTransferCanonicalProducerError,
    _proposal_steps,
    _technical_status,
    prepare_e1_frozen_state_transfer_canonical_plan,
    produce_e1_frozen_state_transfer,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_PROBE_DIGEST,
)
from mcm_field_organism.e1_frozen_state_transfer_one_shot_contract import (
    S1_DM_PARTITIONS,
)


HISTORY = Path("reports/e1_a0_av_history_s1di_once_v1.json")
TARGETS = tuple(
    Path("reports") / name
    for name in (
        "e1_frozen_state_transfer_s1dn_once_v1.json",
        "e1_frozen_state_transfer_s1dn_once_v1.attempt.json",
        "e1_frozen_state_transfer_s1dn_once_v1.lock",
    )
)


class E1FrozenStateTransferCanonicalProducerTests(unittest.TestCase):
    def test_preflight_binds_published_states_probe_and_geometry(self) -> None:
        plan = prepare_e1_frozen_state_transfer_canonical_plan(HISTORY)

        self.assertEqual(S1_DK_PROBE_DIGEST, plan.probe_digest)
        self.assertEqual(
            "6cc885c3b6cb41efcdb48cea0aecb02f980f582115e505534679beb3c427b8e6",
            plan.geometry_digest,
        )
        self.assertEqual(
            "26a53d5a379ecefb7d707df0336c0f7da1b70d0cd8484e7b6221add9a65b4ce1",
            plan.initial_field_digest,
        )
        self.assertEqual((110, 84, 145), (
            plan.source_support_count,
            plan.field_node_count,
            plan.edge_count,
        ))
        self.assertEqual(S1_DM_PARTITIONS, plan.partitions)
        self.assertEqual(S1_DK_ARMS, plan.arms)
        self.assertFalse(plan.execution_permitted)

    def test_preflight_does_not_advance_a_field_or_create_project_paths(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        plan = prepare_e1_frozen_state_transfer_canonical_plan(HISTORY)
        after = tuple(path.exists() for path in TARGETS)

        self.assertEqual(before, after)
        self.assertEqual((True, False, False), after)
        source = inspect.getsource(prepare_e1_frozen_state_transfer_canonical_plan)
        for forbidden in (
            "_partition_run",
            "advance_neutral_fast_shared_field_transient",
            "advance_frozen_e1_fast_shared_field_transient",
            "execute_e1_frozen_state_transfer_one_shot",
        ):
            self.assertNotIn(forbidden, source)
        self.assertFalse(plan.execution_permitted)

    def test_changed_history_evidence_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            changed = json.loads(HISTORY.read_text(encoding="ascii"))
            changed["d_state"] = 0.0
            path = Path(directory) / "changed.json"
            path.write_text(
                json.dumps(changed, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaises(ValueError):
                prepare_e1_frozen_state_transfer_canonical_plan(path)

    def test_preflight_plan_cannot_release_execution(self) -> None:
        plan = prepare_e1_frozen_state_transfer_canonical_plan(HISTORY)

        with self.assertRaisesRegex(
            E1FrozenStateTransferCanonicalProducerError,
            "cannot release",
        ):
            replace(plan, execution_permitted=True)

    def test_proposal_partitions_are_exact_and_contiguous(self) -> None:
        coarse = _proposal_steps("coarse", (0, 1_000_000))
        split = _proposal_steps("split", (0, 500_000, 1_000_000))

        self.assertEqual(1, len(coarse))
        self.assertEqual(2, len(split))
        self.assertEqual(coarse[0].start_tick, split[0].start_tick)
        self.assertEqual(coarse[-1].end_tick, split[-1].end_tick)
        self.assertEqual(split[0].end_tick, split[1].start_tick)
        with self.assertRaisesRegex(
            E1FrozenStateTransferCanonicalProducerError,
            "partition changed",
        ):
            _proposal_steps("split", (0, 400_000, 1_000_000))

    def test_technical_status_boundary_is_deterministic(self) -> None:
        self.assertEqual(
            "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
            _technical_status(0.2, 0.01),
        )
        self.assertEqual(
            "NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
            _technical_status(0.0, 0.0),
        )
        self.assertEqual("TECHNICALLY_UNDECIDABLE", _technical_status(0.01, 0.02))

    def test_canonical_producer_wiring_is_present_but_remains_private(self) -> None:
        source = inspect.getsource(produce_e1_frozen_state_transfer)
        for required in (
            "prepare_e1_frozen_state_transfer_canonical_plan",
            "_partition_run",
            "d_probe_partition",
            "E1FrozenStateTransferExecutionResult",
        ):
            self.assertIn(required, source)
        self.assertNotIn("produce_e1_a0_av_histories", source)
        for role in (
            "E1FrozenStateTransferCanonicalPlan",
            "prepare_e1_frozen_state_transfer_canonical_plan",
            "produce_e1_frozen_state_transfer",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
