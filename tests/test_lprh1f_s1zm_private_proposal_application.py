from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import unittest

from mcm_field_organism._lprh1_s1yn_private_local_handoff import (
    materialize_lprh1_local_handoff,
)
from mcm_field_organism._lprh1f_s1za_private_context_consumer import (
    LPRH1F_BASE_TRANSITION_ID,
    LPRH1F_SCHEMA_VERSION,
    LPRH1FSteeringInput,
    _digest,
    _field_prestate_payload,
    _generic_source_payload,
    _handoff_result_payload,
    _local_values_payload,
    materialize_lprh1f_proposal,
    prepare_lprh1f_base_drive_set,
)
from mcm_field_organism._lprh1f_s1zm_private_proposal_application import (
    LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH,
    LPRH1F_APPLICATION_DUPLICATE_USE,
    LPRH1F_APPLICATION_PROPOSAL_MISMATCH,
    LPRH1F_APPLICATION_SOURCE_LAYER_MISMATCH,
    LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID,
    LPRH1F_DERIVATION_INVALID_TYPE,
    LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID,
    LPRH1FPrivateApplicationError,
    apply_lprh1f_proposal_once,
    derive_lprh1f_drives_for_layer_step,
)
from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
)
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.mcm_neuron import MCMFieldPerception, MCMNeuron
from mcm_field_organism.mcm_neuron_layer import (
    MCMNeuronLayer,
    hold_state_baseline,
)
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
S1ZI = json.loads(
    (
        ROOT
        / "docs/S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG_V1.json"
    ).read_text(encoding="utf-8")
)
S1ZK = json.loads(
    (
        ROOT
        / "docs/S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG_V1.json"
    ).read_text(encoding="utf-8")
)


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_source_bundle():
    source = MCMNeuron(
        neuron_id="neuron.0",
        field_id="field.visual",
        modality_id="visual",
        geometry_id="visual.geometry",
        position=(0,),
        activation=0.0,
        afterimage=0.125,
        perception=MCMFieldPerception(0, None, ()),
    )
    layer = MCMNeuronLayer(
        layer_id="layer.visual",
        neurons=(source,),
        sample_offsets=((-1,), (1,)),
        receptor_dock_ids=("neuron.0",),
    )
    target = MCMFieldStepTime("field.clock", 21, 22, 1000.0)
    contact = TransientLocalReceptorContact(
        snapshot_id="current.0",
        source_clock_id="sensor.clock",
        source_window_start_tick=12,
        source_window_end_tick=13,
        organism_read_time=CommonFieldTime("field.clock", 21, 22),
        value=0.0,
    )
    transient = TransientNeuronDockInput(
        neuron_id="neuron.0",
        dock_id="visual.dock",
        carrier_id="carrier.0",
        step_time=target,
        contacts=(contact,),
    )
    return layer, target, {"neuron.0": 0.0}, {"neuron.0": transient}


def build_handoff(
    arm_id: str,
    execution_id: str,
    target: MCMFieldStepTime,
    transient: TransientNeuronDockInput,
):
    level = arm_id.rsplit(".", 1)[1]
    prototype = -0.5 if level == "low" else 0.5
    recognized = arm_id.startswith("candidate")
    probe_value = prototype if recognized else -prototype
    config = PPB1BankConfig(
        bank_id="visual.bank",
        modality_id="visual",
        geometry_id="visual.geometry",
        carrier_ids=("carrier.0",),
        capacity=1,
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
            PPB1PrototypeSlot(
                "visual.bank.slot.000",
                True,
                (prototype,),
                2,
                2,
            ),
        ),
    )
    probe = ReceptorContactFrame(
        modality_id="visual",
        geometry_id="visual.geometry",
        snapshot_id=f"probe.{arm_id}",
        clock_id="sensor.clock",
        window_start_tick=11,
        window_end_tick=12,
        carrier_ids=("carrier.0",),
        values=(probe_value,),
    )
    finding = probe_s1wu_perceptual_state(
        config,
        state,
        probe,
        f"probe.{execution_id}",
    )
    timed = OrganismTimedReceptorFrame(
        probe,
        CommonFieldTime("field.clock", 20, 21),
    )
    dock = SharedFieldDock(
        "visual.dock",
        ReceptorNeuronDockMap(
            "visual",
            "visual.geometry",
            (("carrier.0", "neuron.0"),),
        ),
    )
    inputs = TransientNeuronInputSet(target, (transient,))
    return materialize_lprh1_local_handoff(
        execution_id,
        config,
        state,
        finding,
        timed,
        target,
        dock,
        inputs,
        (),
    )


def make_steering(
    arm_id: str,
    execution_id: str,
    prepared,
    handoff=None,
):
    prefix = arm_id.rsplit(".", 1)[0]
    source_kind = {
        "candidate": "CANDIDATE",
        "generic": "GENERIC",
        "no-context": "NO_CONTEXT",
        "digest-only": "DIGEST_ONLY",
    }[prefix]
    if arm_id.startswith("candidate"):
        assert handoff is not None and handoff.envelope.context is not None
        local = tuple(
            (
                item.neuron_id,
                item.dock_id,
                item.carrier_id,
                item.prototype_value,
            )
            for item in handoff.envelope.context.local_contexts
        )
    elif arm_id.startswith("generic"):
        value = -0.5 if arm_id.endswith("low") else 0.5
        local = (("neuron.0", "visual.dock", "carrier.0", value),)
    else:
        local = ()
    generic_source_id = {
        "generic.low": "generic.low.source",
        "generic.high": "generic.high.source",
        "digest-only.low": "digest.low.source",
        "digest-only.high": "digest.high.source",
    }.get(arm_id)
    if handoff is not None:
        handoff_digest = _digest(_handoff_result_payload(handoff))
        provenance = handoff_digest
    else:
        handoff_digest = None
        assert generic_source_id is not None
        provenance = _digest(_generic_source_payload(generic_source_id, local))
    values = {
        "execution_id": execution_id,
        "arm_id": arm_id,
        "source_kind": source_kind,
        "target_step_digest": prepared.target_step_digest,
        "field_prestate_digest": prepared.field_prestate_digest,
        "handoff_result": handoff,
        "handoff_result_digest": handoff_digest,
        "generic_source_id": generic_source_id,
        "ordered_local_values": local,
        "source_provenance_digest": provenance,
    }
    payload = {
        "schema_version": LPRH1F_SCHEMA_VERSION,
        "execution_id": execution_id,
        "arm_id": arm_id,
        "source_kind": source_kind,
        "target_step_digest": prepared.target_step_digest,
        "field_prestate_digest": prepared.field_prestate_digest,
        "handoff_result_digest": handoff_digest,
        "generic_source_id": generic_source_id,
        "ordered_local_values": _local_values_payload(local),
        "source_provenance_digest": provenance,
    }
    return LPRH1FSteeringInput(
        **values,
        steering_input_digest=_digest(payload),
    )


def build_proposal(arm_id: str, layer, target, derived, transient):
    execution_id = f"execution.application.{arm_id}"
    prepared = prepare_lprh1f_base_drive_set(
        execution_id,
        layer,
        target,
        _digest(_field_prestate_payload(layer)),
        derived.ordered_drives,
        hold_state_baseline,
        LPRH1F_BASE_TRANSITION_ID,
    )
    handoff = None
    if arm_id.startswith(("candidate", "no-context")):
        handoff = build_handoff(arm_id, execution_id, target, transient)
    steering = make_steering(arm_id, execution_id, prepared, handoff)
    proposal = materialize_lprh1f_proposal(prepared, steering, ())
    return prepared, proposal


class LPRH1FS1ZMPrivateProposalApplicationTests(unittest.TestCase):
    def test_bound_drive_derivation_matches_all_literal_digests(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        derived = derive_lprh1f_drives_for_layer_step(
            layer,
            contacts,
            target,
            transients,
        )
        self.assertEqual(S1ZK["source_layer_digest"], layer.digest())
        self.assertEqual(
            S1ZK["expected_single_derived_drive_digest"],
            derived.ordered_drive_digests[0],
        )
        self.assertEqual(
            S1ZK["drive_input_digests"]["receptor_input_bundle_digest"],
            derived.receptor_input_bundle_digest,
        )
        self.assertIs(derived.ordered_drives[0].previous, layer.neurons[0])
        self.assertEqual(1, derived.derivation_call_count)

    def test_all_eight_arms_match_complete_expected_next_layers(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        transient = transients["neuron.0"]
        derived = derive_lprh1f_drives_for_layer_step(
            layer,
            contacts,
            target,
            transients,
        )
        results = {}
        for arm_id, expected in S1ZI[
            "complete_expected_next_layer_payloads_by_arm"
        ].items():
            prepared, proposal = build_proposal(
                arm_id,
                layer,
                target,
                derived,
                transient,
            )
            result = apply_lprh1f_proposal_once(
                layer,
                derived,
                prepared,
                proposal,
                contacts,
                transients,
                (),
            )
            results[arm_id] = result
            self.assertEqual(canonical_digest(expected), result.next_layer.digest())
            self.assertEqual(expected, {
                "layer_id": result.next_layer.layer_id,
                "sample_offsets": [list(item) for item in result.next_layer.sample_offsets],
                "receptor_dock_ids": list(result.next_layer.docked_neuron_ids),
                "neurons": [item.canonical_payload() for item in result.next_layer.neurons],
            })
            self.assertEqual(1, result.application_receipt.callback_count)
            self.assertEqual(1, len(result.next_consumed_layer_application_ids))

        for left, right in (
            ("candidate.low", "generic.low"),
            ("candidate.high", "generic.high"),
            ("no-context.low", "digest-only.low"),
            ("no-context.high", "digest-only.high"),
        ):
            self.assertEqual(
                results[left].next_layer.digest(),
                results[right].next_layer.digest(),
            )

    def test_duplicate_application_is_rejected_before_a_second_layer_result(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        derived = derive_lprh1f_drives_for_layer_step(layer, contacts, target, transients)
        prepared, proposal = build_proposal(
            "generic.low",
            layer,
            target,
            derived,
            transients["neuron.0"],
        )
        first = apply_lprh1f_proposal_once(
            layer, derived, prepared, proposal, contacts, transients, ()
        )
        with self.assertRaises(LPRH1FPrivateApplicationError) as raised:
            apply_lprh1f_proposal_once(
                layer,
                derived,
                prepared,
                proposal,
                contacts,
                transients,
                first.next_consumed_layer_application_ids,
            )
        self.assertEqual(LPRH1F_APPLICATION_DUPLICATE_USE, raised.exception.code)

    def test_derivation_input_families_fail_closed(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        cases = (
            ((None, contacts, target, transients), LPRH1F_DERIVATION_INVALID_TYPE),
            ((layer, {}, target, transients), LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID),
            ((layer, contacts, target, {}), LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID),
        )
        for args, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(LPRH1FPrivateApplicationError) as raised:
                    derive_lprh1f_drives_for_layer_step(*args)
                self.assertEqual(code, raised.exception.code)

    def test_application_provenance_families_fail_closed(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        derived = derive_lprh1f_drives_for_layer_step(layer, contacts, target, transients)
        prepared_low, proposal_low = build_proposal(
            "generic.low", layer, target, derived, transients["neuron.0"]
        )
        prepared_high, proposal_high = build_proposal(
            "generic.high", layer, target, derived, transients["neuron.0"]
        )
        changed_source = MCMNeuronLayer(
            layer_id=layer.layer_id,
            neurons=(replace(layer.neurons[0], activation=0.1),),
            sample_offsets=layer.sample_offsets,
            receptor_dock_ids=layer.docked_neuron_ids,
        )
        cases = (
            (
                (changed_source, derived, prepared_low, proposal_low, contacts, transients, ()),
                LPRH1F_APPLICATION_SOURCE_LAYER_MISMATCH,
            ),
            (
                (layer, derived, prepared_low, proposal_low, {"neuron.0": 0.1}, transients, ()),
                LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH,
            ),
            (
                (layer, derived, prepared_high, proposal_low, contacts, transients, ()),
                LPRH1F_APPLICATION_PROPOSAL_MISMATCH,
            ),
        )
        for args, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(LPRH1FPrivateApplicationError) as raised:
                    apply_lprh1f_proposal_once(*args)
                self.assertEqual(code, raised.exception.code)

    def test_sources_remain_immutable_and_private_surface_is_unexported(self) -> None:
        layer, target, contacts, transients = build_source_bundle()
        before = (
            layer.digest(),
            repr(target),
            repr(contacts),
            repr(transients),
        )
        derive_lprh1f_drives_for_layer_step(layer, contacts, target, transients)
        after = (
            layer.digest(),
            repr(target),
            repr(contacts),
            repr(transients),
        )
        self.assertEqual(before, after)
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1zm", source)
            self.assertNotIn("lprh1fprivateappliedlayerresult", source)


if __name__ == "__main__":
    unittest.main()
