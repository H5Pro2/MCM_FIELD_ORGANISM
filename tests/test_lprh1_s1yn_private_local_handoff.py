from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import unittest

from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    S1WU_CONTRACT_DIGEST,
    S1WU_PREFLIGHT_DIGEST,
    S1WU_SCHEMA_VERSION,
    S1WUReadOnlyPerceptualFinding,
    _prototype_digest,
    probe_s1wu_perceptual_state,
)
from mcm_field_organism._lprh1_s1yn_private_local_handoff import (
    LPRH1_CAUSAL_TIME_MISMATCH,
    LPRH1_DUPLICATE_HANDOFF,
    LPRH1_LOCAL_MAPPING_MISMATCH,
    LPRH1_PROVENANCE_MISMATCH,
    LPRH1_SLOT_NOT_STABLE,
    LPRH1HandoffError,
    materialize_lprh1_local_handoff,
)
from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
    _digest,
    _input_projection,
)
from mcm_field_organism._ppb1_s1wq_perceptual_state_lifecycle import (
    _state_identity_payload,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorNeuronDockMap,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from mcm_field_organism.shared_mcm_field import SharedFieldDock
from mcm_field_organism.transient_neuron_input import (
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    TransientNeuronInputSet,
)


ROOT = Path(__file__).resolve().parents[1]


def build_fixture(probe_values: tuple[float, float] = (0.21, -0.19)):
    config = PPB1BankConfig(
        bank_id="visual.bank",
        modality_id="visual",
        geometry_id="visual.geometry",
        carrier_ids=("carrier.0", "carrier.1"),
        capacity=2,
        match_threshold=0.1,
        update_rate=0.5,
        stable_after=2,
        expire_after_steps=4,
    )
    state = PPB1BankState(
        bank_id=config.bank_id,
        config_digest=config.digest(),
        accepted_step_count=2,
        source_clock_id="sensor.clock",
        last_source_window_end_tick=10,
        slots=(
            PPB1PrototypeSlot("visual.bank.slot.000", True, (0.2, -0.2), 2, 2),
            PPB1PrototypeSlot.free("visual.bank.slot.001"),
        ),
    )
    probe = ReceptorContactFrame(
        modality_id="visual",
        geometry_id="visual.geometry",
        snapshot_id="probe.001",
        clock_id="sensor.clock",
        window_start_tick=11,
        window_end_tick=12,
        carrier_ids=config.carrier_ids,
        values=probe_values,
    )
    finding = probe_s1wu_perceptual_state(config, state, probe, "probe.read.001")
    timed = OrganismTimedReceptorFrame(probe, CommonFieldTime("field.clock", 20, 21))
    target = MCMFieldStepTime("field.clock", 21, 22, 1000.0)
    dock = SharedFieldDock(
        "visual.dock",
        ReceptorNeuronDockMap(
            "visual",
            "visual.geometry",
            (("carrier.0", "neuron.0"), ("carrier.1", "neuron.1")),
        ),
    )
    inputs = TransientNeuronInputSet(
        target,
        tuple(
            TransientNeuronDockInput(
                neuron_id=f"neuron.{index}",
                dock_id="visual.dock",
                carrier_id=f"carrier.{index}",
                step_time=target,
                contacts=(
                    TransientLocalReceptorContact(
                        snapshot_id=f"current.{index}",
                        source_clock_id="sensor.clock",
                        source_window_start_tick=12,
                        source_window_end_tick=13,
                        organism_read_time=CommonFieldTime("field.clock", 21, 22),
                        value=0.1 * (index + 1),
                    ),
                ),
            )
            for index in range(2)
        ),
    )
    return config, state, finding, timed, target, dock, inputs


def materialize(fixture, consumed=()):
    return materialize_lprh1_local_handoff(
        "execution.synthetic.001", *fixture, consumed
    )


class LPRH1S1YNPrivateLocalHandoffTests(unittest.TestCase):
    def test_positive_context_copies_exact_stable_prototype_locally(self) -> None:
        fixture = build_fixture()
        result = materialize(fixture)
        context = result.envelope.context
        self.assertIsNotNone(context)
        assert context is not None
        self.assertIsNone(result.envelope.no_context_receipt)
        self.assertEqual("CONTEXT", result.receipt.result_role)
        self.assertEqual((0.2, -0.2), context.prototype_values)
        self.assertEqual(("carrier.0", "carrier.1"), context.carrier_ids)
        self.assertEqual(("neuron.0", "neuron.1"), tuple(item.neuron_id for item in context.local_contexts))
        self.assertEqual(("visual.dock", "visual.dock"), tuple(item.dock_id for item in context.local_contexts))
        self.assertEqual(1, result.receipt.extraction_attempt_count)
        self.assertEqual((0, 0, 0, 0, 0), (
            result.receipt.retry_count,
            result.receipt.partial_output_count,
            result.receipt.state_call_count,
            result.receipt.probe_call_count,
            result.receipt.field_call_count,
        ))

    def test_unrecognized_probe_returns_only_explicit_no_context(self) -> None:
        fixture = build_fixture((-1.0, -1.0))
        result = materialize(fixture)
        self.assertIsNone(result.envelope.context)
        self.assertIsNotNone(result.envelope.no_context_receipt)
        assert result.envelope.no_context_receipt is not None
        self.assertEqual("UNRECOGNIZED", result.envelope.no_context_receipt.reason)
        self.assertEqual("NO_CONTEXT", result.receipt.result_role)
        self.assertNotEqual(result.receipt.receipt_id, result.envelope.no_context_receipt.receipt_id)

    def test_state_provenance_mismatch_fails_closed(self) -> None:
        fixture = list(build_fixture())
        state = fixture[1]
        fixture[1] = replace(
            state,
            accepted_step_count=3,
            slots=(
                replace(state.slots[0], last_selected_step=3),
                state.slots[1],
            ),
        )
        with self.assertRaises(LPRH1HandoffError) as raised:
            materialize(tuple(fixture))
        self.assertEqual(LPRH1_PROVENANCE_MISMATCH, raised.exception.code)

    def test_nonadjacent_target_time_fails_before_mapping(self) -> None:
        fixture = list(build_fixture())
        wrong_target = MCMFieldStepTime("field.clock", 22, 23, 1000.0)
        fixture[4] = wrong_target
        with self.assertRaises(LPRH1HandoffError) as raised:
            materialize(tuple(fixture))
        self.assertEqual(LPRH1_CAUSAL_TIME_MISMATCH, raised.exception.code)

    def test_dock_geometry_mismatch_fails_closed(self) -> None:
        fixture = list(build_fixture())
        fixture[5] = SharedFieldDock(
            "visual.dock",
            ReceptorNeuronDockMap(
                "visual",
                "other.geometry",
                (("carrier.0", "neuron.0"), ("carrier.1", "neuron.1")),
            ),
        )
        with self.assertRaises(LPRH1HandoffError) as raised:
            materialize(tuple(fixture))
        self.assertEqual(LPRH1_LOCAL_MAPPING_MISMATCH, raised.exception.code)

    def test_recognized_but_unstable_slot_fails_closed(self) -> None:
        fixture = list(build_fixture())
        config, stable_state, prior_finding, timed = fixture[:4]
        unstable_state = replace(
            stable_state,
            slots=(
                replace(stable_state.slots[0], support_count=1),
                stable_state.slots[1],
            ),
        )
        values = {
            "probe_id": prior_finding.probe_id,
            "bank_id": config.bank_id,
            "modality_id": config.modality_id,
            "bank_config_digest": config.digest(),
            "observed_bank_state_digest": unstable_state.digest(),
            "state_identity_digest": _digest(_state_identity_payload(unstable_state)),
            "probe_input_digest": _digest(_input_projection(timed.frame)),
            "eligible_slot_count": 1,
            "recognized": True,
            "selected_slot_id": unstable_state.slots[0].slot_id,
            "match_distance": 0.01,
            "selected_prototype_digest": _prototype_digest(unstable_state.slots[0].prototype_values),
        }
        finding_payload = {
            "schema_version": S1WU_SCHEMA_VERSION,
            "contract_digest": S1WU_CONTRACT_DIGEST,
            "preflight_digest": S1WU_PREFLIGHT_DIGEST,
            **values,
        }
        fixture[1] = unstable_state
        fixture[2] = S1WUReadOnlyPerceptualFinding(
            **values,
            finding_digest=_digest(finding_payload),
        )
        with self.assertRaises(LPRH1HandoffError) as raised:
            materialize(tuple(fixture))
        self.assertEqual(LPRH1_SLOT_NOT_STABLE, raised.exception.code)

    def test_duplicate_handoff_is_rejected_without_ledger_change(self) -> None:
        fixture = build_fixture()
        first = materialize(fixture)
        prior = first.next_consumed_handoff_ids
        with self.assertRaises(LPRH1HandoffError) as raised:
            materialize(fixture, prior)
        self.assertEqual(LPRH1_DUPLICATE_HANDOFF, raised.exception.code)
        self.assertEqual(1, len(prior))

    def test_sources_and_receptor_input_are_unchanged(self) -> None:
        fixture = build_fixture()
        before = tuple(
            hashlib.sha256(repr(value).encode("utf-8")).hexdigest()
            for value in fixture
        )
        result = materialize(fixture)
        after = tuple(
            hashlib.sha256(repr(value).encode("utf-8")).hexdigest()
            for value in fixture
        )
        self.assertEqual(before, after)
        self.assertIs(result.envelope.receptor_input_set, fixture[-1])
        self.assertEqual(result.next_consumed_handoff_ids, result.receipt.consumed_handoff_ids_after)

    def test_private_module_is_absent_from_public_surfaces(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yn", source)
            self.assertNotIn("lprh", source)


if __name__ == "__main__":
    unittest.main()
