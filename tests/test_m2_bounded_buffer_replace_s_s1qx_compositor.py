from __future__ import annotations

from dataclasses import fields, replace
import ast
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.m2_bounded_buffer_replace_s_compositor import (
    CAPACITY_RECORDS,
    COMPLETED,
    CONTRACT_ID,
    CURRENT_FALLBACK_ID,
    FAILURE_CODES,
    MODE_IDS,
    NOT_APPLICABLE,
    NOT_COMPUTABLE,
    OUTPUT_ROLES,
    PHASES,
    RECORD_SCHEMA_ID,
    REPLAY_PHASES,
    SOURCE_S1QV_DIGEST,
    STATUSES,
    M2BoundedBufferCompositorError,
    M2BoundedBufferConfiguration,
    M2BoundedBufferReplaceSReceipt,
    M2BoundedBufferReplaceSResult,
    M2BoundedBufferState,
    M2EvidenceRecord,
    advance_m2_bounded_buffer_replace_s,
    build_empty_m2_buffer,
    build_registered_m2_configuration,
    s1qv_registration_payload,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from mcm_field_organism.shared_mcm_field import SharedMCMField
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from tests.m2_bounded_buffer_replace_s_s1qx_fixtures import (
    POSITION_IDS,
    RECORD_IDS,
    REGISTERED_VALUES,
    M2BoundedBufferFixture,
    build_field,
    build_sync_fixture,
    build_transient_fixture,
)


MODULE = "mcm_field_organism.m2_bounded_buffer_replace_s_compositor"


def _run(
    fixture: M2BoundedBufferFixture, **overrides
) -> M2BoundedBufferReplaceSResult:
    values = {
        "field": fixture.field,
        "distribution": fixture.distribution,
        "interval_input": fixture.interval_input,
        "neutral_substrate_config": fixture.substrate_config,
        "fast_afterimage_config": fixture.afterimage_config,
        "m2_configuration": fixture.m2_configuration,
        "m2_prestate": fixture.m2_prestate,
    }
    values.update(overrides)
    return advance_m2_bounded_buffer_replace_s(**values)


def _proposal(fixture: M2BoundedBufferFixture) -> SharedMCMField:
    if isinstance(fixture.interval_input, MCMFieldStepTime):
        return advance_neutral_fast_shared_field(
            fixture.field,
            fixture.distribution,
            fixture.interval_input,
            fixture.substrate_config,
            fixture.afterimage_config,
        )
    return advance_neutral_fast_shared_field_transient(
        fixture.field,
        fixture.distribution,
        fixture.interval_input,
        fixture.substrate_config,
        fixture.afterimage_config,
    )


def _s(field: SharedMCMField) -> tuple[float, ...]:
    return tuple(item.activation for item in field.layer.neurons)


def _h(field: SharedMCMField) -> tuple[float, ...]:
    return tuple(item.afterimage for item in field.layer.neurons)


def _run_sequence(mode_id: str):
    field = build_field()
    configuration = build_registered_m2_configuration(mode_id)
    state = build_empty_m2_buffer(configuration, field)
    fixtures = []
    proposals = []
    results = []
    for index, values in enumerate(REGISTERED_VALUES):
        fixture = build_sync_fixture(
            mode_id,
            field=field,
            m2_configuration=configuration,
            m2_prestate=state,
            start_tick=index * 10,
            values=values,
        )
        proposal = _proposal(fixture)
        result = _run(fixture)
        fixtures.append(fixture)
        proposals.append(proposal)
        results.append(result)
        if result.receipt.status != COMPLETED:
            raise AssertionError(result.receipt.failure_codes)
        field = result.field
        state = result.next_m2_state
    return tuple(fixtures), tuple(proposals), tuple(results)


def _failure_code(result: M2BoundedBufferReplaceSResult) -> str:
    if result.receipt.status != NOT_COMPUTABLE:
        raise AssertionError("expected NOT_COMPUTABLE result")
    return result.receipt.failure_codes[0]


class M2BoundedBufferReplaceSS1QXCompositorTests(unittest.TestCase):
    def test_01_module_type_status_phase_and_error_surface(self) -> None:
        self.assertEqual("m2-bounded-buffer-replace-s/s1qw.v1", CONTRACT_ID)
        self.assertEqual((COMPLETED, NOT_COMPUTABLE), STATUSES)
        self.assertEqual(18, len(FAILURE_CODES))
        self.assertEqual(18, len(set(FAILURE_CODES)))
        self.assertEqual(12, len(PHASES))
        self.assertEqual(("DELAY", "REPLAY"), MODE_IDS)
        self.assertEqual(("CAPTURE", "EMIT", "EXHAUSTED"), REPLAY_PHASES)
        self.assertEqual(5, len(OUTPUT_ROLES))
        self.assertEqual(
            ("field", "next_m2_state", "receipt"),
            tuple(item.name for item in fields(M2BoundedBufferReplaceSResult)),
        )
        self.assertEqual(
            "receipt_digest", fields(M2BoundedBufferReplaceSReceipt)[-1].name
        )

    def test_02_exact_s1qv_mode_configurations_and_digest(self) -> None:
        encoded = json.dumps(
            s1qv_registration_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(SOURCE_S1QV_DIGEST, hashlib.sha256(encoded).hexdigest())
        delay = build_registered_m2_configuration("DELAY")
        replay = build_registered_m2_configuration("REPLAY")
        self.assertEqual(CAPACITY_RECORDS, delay.capacity_records)
        self.assertEqual(CAPACITY_RECORDS, replay.capacity_records)
        self.assertEqual(RECORD_SCHEMA_ID, delay.record_schema_id)
        self.assertEqual(CURRENT_FALLBACK_ID, replay.current_fallback_id)
        self.assertEqual(
            replace(delay, mode_id="REPLAY"),
            replay,
        )

    def test_03_deterministic_distinct_mode_fresh_states(self) -> None:
        field = build_field()
        delay_config = build_registered_m2_configuration("DELAY")
        replay_config = build_registered_m2_configuration("REPLAY")
        delay_a = build_empty_m2_buffer(delay_config, field)
        delay_b = build_empty_m2_buffer(delay_config, field)
        replay = build_empty_m2_buffer(replay_config, field)
        self.assertEqual(delay_a, delay_b)
        self.assertIsNot(delay_a, delay_b)
        self.assertEqual((), delay_a.records)
        self.assertEqual(NOT_APPLICABLE, delay_a.replay_phase)
        self.assertEqual("CAPTURE", replay.replay_phase)
        self.assertNotEqual(delay_a.mode_id, replay.mode_id)

    def test_04_canonical_record_payload_digest_and_no_raw_roles(self) -> None:
        result = _run(build_sync_fixture("DELAY"))
        record = result.next_m2_state.records[0]
        self.assertIsInstance(record, M2EvidenceRecord)
        encoded = json.dumps(
            record.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(record.record_digest, hashlib.sha256(encoded).hexdigest())
        self.assertEqual(
            (
                "s_evidence",
                "input_field_digest",
                "geometry_digest",
                "neuron_order",
                "distribution_digest",
                "interval_digest",
                "a1_proposal_digest",
                "record_digest",
            ),
            tuple(item.name for item in fields(M2EvidenceRecord)),
        )
        for forbidden in ("raw", "contact", "afterimage", "field", "arm"):
            self.assertFalse(hasattr(record, forbidden))

    def test_05_sync_delay_warmup_p0_p1(self) -> None:
        _, proposals, results = _run_sequence("DELAY")
        self.assertEqual(
            ("CURRENT_A1_WARMUP", "CURRENT_A1_WARMUP"),
            tuple(item.receipt.output_role for item in results[:2]),
        )
        self.assertEqual(_s(proposals[0]), _s(results[0].field))
        self.assertEqual(_s(proposals[1]), _s(results[1].field))
        self.assertEqual((1, 2), tuple(len(item.next_m2_state.records) for item in results[:2]))

    def test_06_sync_delay_rolls_p2_to_p4(self) -> None:
        _, proposals, results = _run_sequence("DELAY")
        expected = (_s(proposals[0]), _s(proposals[1]), _s(proposals[2]))
        self.assertEqual(
            ("DELAY_OLDEST_RECORD",) * 3,
            tuple(item.receipt.output_role for item in results[2:]),
        )
        self.assertEqual(expected, tuple(_s(item.field) for item in results[2:]))
        self.assertTrue(all(len(item.next_m2_state.records) == 2 for item in results[2:]))

    def test_07_sync_replay_captures_p0_p1(self) -> None:
        _, proposals, results = _run_sequence("REPLAY")
        self.assertEqual(
            ("CURRENT_A1_CAPTURE", "CURRENT_A1_CAPTURE"),
            tuple(item.receipt.output_role for item in results[:2]),
        )
        self.assertEqual(("CAPTURE", "EMIT"), tuple(item.next_m2_state.replay_phase for item in results[:2]))
        self.assertEqual(_s(proposals[0]), _s(results[0].field))
        self.assertEqual(_s(proposals[1]), _s(results[1].field))

    def test_08_sync_replay_emits_p2_p3_in_order(self) -> None:
        _, proposals, results = _run_sequence("REPLAY")
        self.assertEqual(
            ("REPLAY_PREFIX_RECORD", "REPLAY_PREFIX_RECORD"),
            tuple(item.receipt.output_role for item in results[2:4]),
        )
        self.assertEqual((_s(proposals[0]), _s(proposals[1])), tuple(_s(item.field) for item in results[2:4]))
        self.assertEqual((0, 1), tuple(item.receipt.selection_position for item in results[2:4]))

    def test_09_sync_replay_is_exhausted_at_p4(self) -> None:
        _, proposals, results = _run_sequence("REPLAY")
        result = results[4]
        self.assertEqual("CURRENT_A1_EXHAUSTED", result.receipt.output_role)
        self.assertEqual("EXHAUSTED", result.next_m2_state.replay_phase)
        self.assertEqual(2, result.next_m2_state.replay_cursor)
        self.assertEqual(_s(proposals[4]), _s(result.field))
        self.assertIsNone(result.receipt.source_record_digest)

    def test_10_valid_single_transient_delay_step(self) -> None:
        fixture = build_transient_fixture("DELAY")
        proposal = _proposal(fixture)
        result = _run(fixture)
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertEqual("transient", result.receipt.interval_kind)
        self.assertEqual("CURRENT_A1_WARMUP", result.receipt.output_role)
        self.assertEqual(_s(proposal), _s(result.field))

    def test_11_valid_single_transient_replay_step(self) -> None:
        fixture = build_transient_fixture("REPLAY")
        proposal = _proposal(fixture)
        result = _run(fixture)
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertEqual("transient", result.receipt.interval_kind)
        self.assertEqual("CURRENT_A1_CAPTURE", result.receipt.output_role)
        self.assertEqual(_s(proposal), _s(result.field))

    def test_12_exact_s1qv_output_roles_and_source_schedule(self) -> None:
        _, _, delay = _run_sequence("DELAY")
        _, _, replay = _run_sequence("REPLAY")
        delay_current = tuple(item.receipt.current_record_digest for item in delay)
        replay_current = tuple(item.receipt.current_record_digest for item in replay)
        self.assertEqual(delay_current, replay_current)
        self.assertEqual(
            (None, None, delay_current[0], delay_current[1], delay_current[2]),
            tuple(item.receipt.source_record_digest for item in delay),
        )
        self.assertEqual(
            (None, None, replay_current[0], replay_current[1], None),
            tuple(item.receipt.source_record_digest for item in replay),
        )
        self.assertEqual(POSITION_IDS, tuple(f"P{i}" for i in range(5)))
        self.assertEqual(RECORD_IDS, ("A", "B", "C", "D", "E"))

    def test_13_exact_delay_buffer_and_replay_phase_cursor_sequences(self) -> None:
        _, _, delay = _run_sequence("DELAY")
        _, _, replay = _run_sequence("REPLAY")
        ids = tuple(item.receipt.current_record_digest for item in delay)
        self.assertEqual(
            ((ids[0],), (ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[3]), (ids[3], ids[4])),
            tuple(tuple(record.record_digest for record in item.next_m2_state.records) for item in delay),
        )
        self.assertEqual(
            ("CAPTURE", "EMIT", "EMIT", "EXHAUSTED", "EXHAUSTED"),
            tuple(item.next_m2_state.replay_phase for item in replay),
        )
        self.assertEqual((0, 0, 1, 2, 2), tuple(item.next_m2_state.replay_cursor for item in replay))

    def test_14_fields_match_through_p3_and_first_diverge_at_p4(self) -> None:
        _, _, delay = _run_sequence("DELAY")
        _, _, replay = _run_sequence("REPLAY")
        for index in range(4):
            self.assertEqual(delay[index].field, replay[index].field)
        self.assertNotEqual(_s(delay[4].field), _s(replay[4].field))
        self.assertEqual(_h(delay[4].field), _h(replay[4].field))
        self.assertEqual(delay[4].field.last_distribution, replay[4].field.last_distribution)

    def test_15_record_digests_and_required_s_distinctions_hold(self) -> None:
        _, proposals, results = _run_sequence("DELAY")
        digests = tuple(item.receipt.current_record_digest for item in results)
        self.assertEqual(5, len(set(digests)))
        self.assertNotEqual(_s(proposals[0]), _s(proposals[1]))
        self.assertNotEqual(_s(proposals[2]), _s(proposals[4]))

    def test_16_signed_s_is_replaced_from_exact_current_or_historical_source(self) -> None:
        _, delay_proposals, delay = _run_sequence("DELAY")
        _, replay_proposals, replay = _run_sequence("REPLAY")
        delay_expected = tuple(_s(delay_proposals[index]) for index in (0, 1, 0, 1, 2))
        replay_expected = tuple(_s(replay_proposals[index]) for index in (0, 1, 0, 1, 4))
        self.assertEqual(delay_expected, tuple(_s(item.field) for item in delay))
        self.assertEqual(replay_expected, tuple(_s(item.field) for item in replay))
        self.assertTrue(all(item.receipt.s_replacement_confirmed for item in (*delay, *replay)))

    def test_17_current_a1_h_provenance_and_one_time_advance_are_preserved(self) -> None:
        for mode in MODE_IDS:
            fixtures, proposals, results = _run_sequence(mode)
            for fixture, proposal, result in zip(fixtures, proposals, results, strict=True):
                self.assertEqual(proposal.docks, result.field.docks)
                self.assertEqual(proposal.last_distribution, result.field.last_distribution)
                self.assertEqual(_h(proposal), _h(result.field))
                self.assertEqual(fixture.field.layer.tick + 1, result.field.layer.tick)
                self.assertEqual(1, result.receipt.field_time_advance_count)
                self.assertTrue(result.receipt.h_identity_confirmed)

    def test_18_carry_result_state_and_receipt_digests_are_deterministic(self) -> None:
        _, _, first_delay = _run_sequence("DELAY")
        _, _, second_delay = _run_sequence("DELAY")
        _, _, first_replay = _run_sequence("REPLAY")
        _, _, second_replay = _run_sequence("REPLAY")
        self.assertEqual(first_delay, second_delay)
        self.assertEqual(first_replay, second_replay)
        for sequence in (first_delay, first_replay):
            for previous, current in zip(sequence, sequence[1:]):
                self.assertEqual(previous.receipt.final_field_digest, current.receipt.input_field_digest)
                self.assertEqual(previous.receipt.m2_next_state_digest, current.receipt.m2_prestate_digest)

    def test_19_common_geometry_permutation_has_no_list_position_semantics(self) -> None:
        original_fixture = build_sync_fixture("DELAY")
        original = _run(original_fixture)
        reversed_field = SharedMCMField(
            replace(
                original_fixture.field.layer,
                neurons=tuple(reversed(original_fixture.field.layer.neurons)),
            ),
            original_fixture.field.docks,
        )
        permuted_fixture = build_sync_fixture("DELAY", field=reversed_field)
        permuted = _run(permuted_fixture)
        original_by_id = {item.neuron_id: item.activation for item in original.field.layer.neurons}
        permuted_by_id = {item.neuron_id: item.activation for item in permuted.field.layer.neurons}
        self.assertEqual(set(original_by_id), set(permuted_by_id))
        for neuron_id in original_by_id:
            self.assertAlmostEqual(original_by_id[neuron_id], permuted_by_id[neuron_id], places=12)

    def test_20_arm_isolation_mode_identity_and_no_cross_state_read(self) -> None:
        field = build_field()
        delay_config = build_registered_m2_configuration("DELAY")
        replay_config = build_registered_m2_configuration("REPLAY")
        delay_a = build_empty_m2_buffer(delay_config, field)
        delay_b = build_empty_m2_buffer(delay_config, field)
        replay = build_empty_m2_buffer(replay_config, field)
        self.assertEqual(delay_a, delay_b)
        self.assertIsNot(delay_a, delay_b)
        mismatch = _run(
            build_sync_fixture(
                "REPLAY",
                field=field,
                m2_configuration=replay_config,
                m2_prestate=delay_a,
            )
        )
        self.assertEqual("QW_M2_PRESTATE_INVALID", _failure_code(mismatch))
        valid = _run(build_sync_fixture("REPLAY", field=field, m2_prestate=replay))
        self.assertEqual("REPLAY", valid.next_m2_state.mode_id)

    def test_21_private_import_export_side_effect_and_closed_branch_boundaries(self) -> None:
        root = Path(__file__).parents[1] / "mcm_field_organism"
        source = (root / "m2_bounded_buffer_replace_s_compositor.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        forbidden = (
            "local_synaptic_memory_candidate",
            "passive_synaptic_memory_comparison",
            "dynamic_substrate",
            "runner",
            "orchestrator",
            "current_api",
        )
        self.assertFalse(any(fragment in module for module in imported for fragment in forbidden))
        self.assertIn("local_state_replace_s_compositor_core", source)
        self.assertFalse(hasattr(current_api, "advance_m2_bounded_buffer_replace_s"))
        self.assertFalse(hasattr(mcm_field_organism, "advance_m2_bounded_buffer_replace_s"))

    def test_22_mutation_classes_01_to_06_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture("DELAY")
        invalid_configuration = replace(fixture.m2_configuration, capacity_records=3)
        invalid_state = replace(fixture.m2_prestate, replay_phase="CAPTURE")
        foreign_field = build_field(2)
        foreign_state = build_empty_m2_buffer(fixture.m2_configuration, foreign_field)
        cases = (
            (_run(fixture, field=object()), "QW_INPUT_TYPE_INVALID"),
            (_run(fixture, field=build_w7m_capacity_function_matrix_adapter().initial_field), "QW_FIELD_ROLE_INVALID"),
            (_run(fixture, interval_input=MCMFieldStepTime("organism.test", 0, 9, 10.0)), "QW_DISTRIBUTION_OR_INTERVAL_INVALID"),
            (_run(fixture, m2_configuration=invalid_configuration), "QW_CONFIGURATION_INVALID"),
            (_run(fixture, m2_prestate=invalid_state), "QW_M2_PRESTATE_INVALID"),
            (_run(fixture, m2_prestate=foreign_state), "QW_GEOMETRY_OR_ORDER_MISMATCH"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_23_mutation_classes_07_to_12_fail_with_exact_codes(self) -> None:
        delay = build_sync_fixture("DELAY")
        replay = build_sync_fixture("REPLAY")
        with patch(f"{MODULE}.advance_neutral_fast_shared_field", side_effect=NeutralLocalFieldSubstrateError("controlled")):
            a1_failure = _run(delay)
        with patch(f"{MODULE}._a1_proposal_valid", return_value=False):
            a1_invalid = _run(delay)
        with patch(f"{MODULE}._build_record", side_effect=M2BoundedBufferCompositorError("controlled")):
            record_failure = _run(delay)
        with patch(f"{MODULE}._record_valid", return_value=False):
            record_invalid = _run(delay)
        with patch(f"{MODULE}._advance_delay", side_effect=M2BoundedBufferCompositorError("controlled")):
            delay_invalid = _run(delay)
        with patch(f"{MODULE}._advance_replay", side_effect=M2BoundedBufferCompositorError("controlled")):
            replay_invalid = _run(replay)
        cases = (
            (a1_failure, "QW_A1_ADVANCE_FAILED"),
            (a1_invalid, "QW_A1_PROPOSAL_INVALID"),
            (record_failure, "QW_RECORD_MATERIALIZATION_FAILED"),
            (record_invalid, "QW_RECORD_INVALID"),
            (delay_invalid, "QW_DELAY_TRANSITION_INVALID"),
            (replay_invalid, "QW_REPLAY_TRANSITION_INVALID"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_24_mutation_classes_13_to_18_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture("DELAY")
        with patch(f"{MODULE}._selection_valid", return_value=False):
            selection = _run(fixture)
        with patch(f"{MODULE}._materialize_replace_s", side_effect=ValueError("controlled")):
            replacement = _run(fixture)
        with patch(f"{MODULE}._final_identity_valid", return_value=False):
            identity = _run(fixture)
        with patch(f"{MODULE}._field_time_advance_count", return_value=2):
            time_count = _run(fixture)
        with patch(f"{MODULE}._next_state_valid", return_value=False):
            next_state = _run(fixture)
        with patch(f"{MODULE}._atomic_output_valid", return_value=False):
            atomic = _run(fixture)
        cases = (
            (selection, "QW_SOURCE_SELECTION_INVALID"),
            (replacement, "QW_S_REPLACEMENT_FAILED"),
            (identity, "QW_H_OR_PROVENANCE_CHANGED"),
            (time_count, "QW_FIELD_TIME_CARDINALITY_FAILED"),
            (next_state, "QW_NEXT_STATE_INVALID"),
            (atomic, "QW_ATOMIC_OUTPUT_FAILED"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_25_not_computable_is_atomic_without_partial_output(self) -> None:
        fixture = build_sync_fixture("DELAY")
        failures = (
            _run(fixture, field=object()),
            _run(fixture, m2_prestate=replace(fixture.m2_prestate, replay_cursor=1)),
        )
        for result in failures:
            self.assertEqual(NOT_COMPUTABLE, result.field)
            self.assertEqual(NOT_COMPUTABLE, result.next_m2_state)
            self.assertEqual(NOT_COMPUTABLE, result.receipt.status)
            self.assertTrue(result.receipt.failure_codes)


if __name__ == "__main__":
    unittest.main()
