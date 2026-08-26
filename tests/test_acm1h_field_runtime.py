from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._acm1h_field_runtime import (
    ACM1HFieldCarry,
    ACM1HFieldRuntimeError,
    ACM1HPrivateState,
    _field_digest,
    advance_acm1h_four_node_field,
    advance_acm1h_off_four_node_field,
    build_acm1h_field_carry,
)
from mcm_field_organism._acm1h_reference import (
    ACM1HConfigRecord,
    ACM1HDecisionRecord,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.four_node_fresh_factory import (
    build_four_node_public_fresh_field,
)
from mcm_field_organism.four_node_fresh_manifest import (
    load_four_node_fresh_manifest,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_distributor import (
    ReceptorDistributor,
    ReceptorDock,
)
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = load_four_node_fresh_manifest(
    ROOT / "reports" / "s1rk_four_node_fresh_manifest.json"
)
SUBSTRATE = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE = NeutralFastAfterimageConfig(0.5)
CONFIG = ACM1HConfigRecord(0.5, 0.5)


def _distribution(
    start: int,
    end: int,
    values: tuple[float, float, float, float],
):
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.s1rf.technical-control.4n",
            "technical-control",
            "mcm.s1rf.receptor.4n",
        )
    )
    frame = ReceptorContactFrame(
        modality_id="technical-control",
        geometry_id="mcm.s1rf.receptor.4n",
        snapshot_id=f"acm1h.synthetic.{start}.{end}",
        clock_id="acm1h.source",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=("carrier-a", "carrier-b", "carrier-c", "carrier-d"),
        values=values,
    )
    return distributor.distribute(
        (frame,), CommonFieldTime("acm1h.field", start, end)
    )


def _step(start: int, end: int) -> MCMFieldStepTime:
    return MCMFieldStepTime("acm1h.field", start, end, 10.0)


def _prepared_field():
    fresh = build_four_node_public_fresh_field(MANIFEST)
    return advance_neutral_fast_shared_field(
        fresh,
        _distribution(0, 10, (0.9, 0.2, -0.3, -0.8)),
        _step(0, 10),
        SUBSTRATE,
        AFTERIMAGE,
    )


class ACM1HFieldRuntimeTests(unittest.TestCase):
    def test_private_carry_binds_unchanged_completed_field(self) -> None:
        field = _prepared_field()
        before = _field_digest(field)
        carry = build_acm1h_field_carry(
            field, CONFIG, motif_states=(0.5, -0.25)
        )

        self.assertIsInstance(carry, ACM1HFieldCarry)
        self.assertIs(carry.field, field)
        self.assertEqual(before, carry.field_digest)
        self.assertEqual(field.layer.tick, carry.private_state.field_tick)
        self.assertEqual(10, carry.private_state.field_time_endpoint)
        self.assertEqual((0.5, -0.25), (
            carry.private_state.z_left,
            carry.private_state.z_right,
        ))

    def test_one_active_step_commits_field_and_both_z_siblings(self) -> None:
        field = _prepared_field()
        carry = build_acm1h_field_carry(
            field, CONFIG, motif_states=(0.5, -0.25)
        )
        distribution = _distribution(10, 20, (0.1, 0.1, 0.1, 0.1))

        result = advance_acm1h_four_node_field(
            carry,
            CONFIG,
            distribution,
            _step(10, 20),
            SUBSTRATE,
            AFTERIMAGE,
        )
        neutral = advance_neutral_fast_shared_field(
            field,
            distribution,
            _step(10, 20),
            SUBSTRATE,
            AFTERIMAGE,
        )

        self.assertEqual(2, result.field.layer.tick)
        self.assertEqual(20, result.private_state.field_time_endpoint)
        self.assertNotEqual(
            (carry.private_state.z_left, carry.private_state.z_right),
            (result.private_state.z_left, result.private_state.z_right),
        )
        self.assertNotEqual(
            carry.private_state.z_left, result.private_state.z_left
        )
        self.assertNotEqual(
            carry.private_state.z_right, result.private_state.z_right
        )
        self.assertNotEqual(carry.private_state_digest, result.private_state_digest)
        self.assertNotEqual(carry.field_digest, result.field_digest)
        self.assertNotEqual(_field_digest(neutral), result.field_digest)

    def test_successor_carry_is_valid_input_for_exactly_one_next_step(self) -> None:
        first = advance_acm1h_four_node_field(
            build_acm1h_field_carry(
                _prepared_field(), CONFIG, motif_states=(0.25, 0.25)
            ),
            CONFIG,
            _distribution(10, 20, (0.2, -0.1, 0.4, -0.2)),
            _step(10, 20),
            SUBSTRATE,
            AFTERIMAGE,
        )
        second = advance_acm1h_four_node_field(
            first,
            CONFIG,
            _distribution(20, 30, (-0.2, 0.4, -0.1, 0.2)),
            _step(20, 30),
            SUBSTRATE,
            AFTERIMAGE,
        )
        self.assertEqual(3, second.field.layer.tick)
        self.assertEqual(30, second.private_state.field_time_endpoint)

    def test_acm_off_is_bit_exact_neutral_and_creates_no_private_state(self) -> None:
        field = build_four_node_public_fresh_field(MANIFEST)
        distribution = _distribution(0, 10, (0.8, -0.4, 0.2, 0.1))
        expected = advance_neutral_fast_shared_field(
            field,
            distribution,
            _step(0, 10),
            SUBSTRATE,
            AFTERIMAGE,
        )
        with patch(
            "mcm_field_organism._acm1h_field_runtime.run_acm1h_reference"
        ) as reference:
            actual = advance_acm1h_off_four_node_field(
                field,
                distribution,
                _step(0, 10),
                SUBSTRATE,
                AFTERIMAGE,
            )

        reference.assert_not_called()
        self.assertNotIsInstance(actual, ACM1HFieldCarry)
        self.assertEqual(expected, actual)
        self.assertEqual(_field_digest(expected), _field_digest(actual))

    def test_configuration_or_time_mismatch_fails_without_successor(self) -> None:
        carry = build_acm1h_field_carry(_prepared_field(), CONFIG)
        before = (carry.field_digest, carry.private_state_digest, carry.carry_digest)
        with self.assertRaisesRegex(
            ACM1HFieldRuntimeError, "configuration differs"
        ):
            advance_acm1h_four_node_field(
                carry,
                ACM1HConfigRecord(1.0, 0.5),
                _distribution(10, 20, (0.0, 0.0, 0.0, 0.0)),
                _step(10, 20),
                SUBSTRATE,
                AFTERIMAGE,
            )
        with self.assertRaisesRegex(
            ACM1HFieldRuntimeError, "does not start at the carry endpoint"
        ):
            advance_acm1h_four_node_field(
                carry,
                CONFIG,
                _distribution(20, 30, (0.0, 0.0, 0.0, 0.0)),
                _step(20, 30),
                SUBSTRATE,
                AFTERIMAGE,
            )
        self.assertEqual(
            before,
            (carry.field_digest, carry.private_state_digest, carry.carry_digest),
        )

    def test_failed_reference_proposal_publishes_no_partial_carry(self) -> None:
        carry = build_acm1h_field_carry(_prepared_field(), CONFIG)
        failed = ACM1HDecisionRecord(
            "FAILED", "SYNTHETIC_FAILURE", None, None, None, (), None
        )
        with patch(
            "mcm_field_organism._acm1h_field_runtime.run_acm1h_reference",
            return_value=failed,
        ), self.assertRaisesRegex(ACM1HFieldRuntimeError, "SYNTHETIC_FAILURE"):
            advance_acm1h_four_node_field(
                carry,
                CONFIG,
                _distribution(10, 20, (0.0, 0.0, 0.0, 0.0)),
                _step(10, 20),
                SUBSTRATE,
                AFTERIMAGE,
            )
        self.assertEqual(1, carry.field.layer.tick)

    def test_distribution_interval_is_rejected_before_reference_proposal(self) -> None:
        carry = build_acm1h_field_carry(_prepared_field(), CONFIG)
        with patch(
            "mcm_field_organism._acm1h_field_runtime.run_acm1h_reference"
        ) as reference, self.assertRaisesRegex(
            ACM1HFieldRuntimeError, "field step must match"
        ):
            advance_acm1h_four_node_field(
                carry,
                CONFIG,
                _distribution(10, 20, (0.0, 0.0, 0.0, 0.0)),
                MCMFieldStepTime("acm1h.field", 10, 21, 10.0),
                SUBSTRATE,
                AFTERIMAGE,
            )
        reference.assert_not_called()

    def test_records_are_immutable_private_and_snapshot_free(self) -> None:
        carry = build_acm1h_field_carry(_prepared_field(), CONFIG)
        with self.assertRaises(FrozenInstanceError):
            carry.private_state.z_left = 0.0  # type: ignore[misc]
        self.assertNotIn("acm", SharedMCMFieldSnapshot.__dataclass_fields__)
        for role in (
            "ACM1HFieldCarry",
            "ACM1HPrivateState",
            "build_acm1h_field_carry",
            "advance_acm1h_four_node_field",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))
        self.assertIsInstance(carry.private_state, ACM1HPrivateState)


if __name__ == "__main__":
    unittest.main()
