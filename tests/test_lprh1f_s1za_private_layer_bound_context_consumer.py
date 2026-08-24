from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import unittest

from mcm_field_organism._lprh1_s1yn_private_local_handoff import (
    materialize_lprh1_local_handoff,
)
from mcm_field_organism._lprh1f_s1za_private_context_consumer import (
    LPRH1F_ATOMIC_RESULT_REQUIRED,
    LPRH1F_DUPLICATE_FIELD_USE,
    LPRH1F_LOCAL_MAPPING_MISMATCH,
    LPRH1F_PROVENANCE_MISMATCH,
    LPRH1F_BASE_TRANSITION_ID,
    LPRH1F_SCHEMA_VERSION,
    LPRH1FConsumerError,
    LPRH1FSteeringInput,
    _digest,
    _field_prestate_payload,
    _generic_source_payload,
    _handoff_result_payload,
    _local_values_payload,
    materialize_lprh1f_proposal,
    prepare_lprh1f_base_drive_set,
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
    MCMNeuronDrive,
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


def build_handoff(
    prototype_value: float,
    *,
    execution_id: str,
    recognized: bool = True,
):
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
                (prototype_value,),
                2,
                2,
            ),
        ),
    )
    probe_value = prototype_value if recognized else -prototype_value
    probe = ReceptorContactFrame(
        modality_id="visual",
        geometry_id="visual.geometry",
        snapshot_id="probe.001",
        clock_id="sensor.clock",
        window_start_tick=11,
        window_end_tick=12,
        carrier_ids=config.carrier_ids,
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
    target = MCMFieldStepTime("field.clock", 21, 22, 1000.0)
    dock = SharedFieldDock(
        "visual.dock",
        ReceptorNeuronDockMap(
            "visual",
            "visual.geometry",
            (("carrier.0", "neuron.0"),),
        ),
    )
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
    inputs = TransientNeuronInputSet(target, (transient,))
    result = materialize_lprh1_local_handoff(
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
    return result, target, transient


def build_layer_and_drives(
    target: MCMFieldStepTime,
    transients: tuple[TransientNeuronDockInput | None, ...],
):
    neurons = tuple(
        MCMNeuron(
            neuron_id=f"neuron.{index}",
            field_id="field.visual",
            modality_id="visual",
            geometry_id="visual.geometry",
            position=(index,),
            activation=0.0 if index == 0 else 0.2,
            afterimage=0.125 if index == 0 else -0.125,
            perception=MCMFieldPerception(0, None, ()),
        )
        for index in range(len(transients))
    )
    layer = MCMNeuronLayer(
        layer_id="layer.visual",
        neurons=neurons,
        sample_offsets=((-1,), (1,)),
        receptor_dock_ids=(),
    )
    drives = tuple(
        MCMNeuronDrive(
            previous=neuron,
            perception=MCMFieldPerception(1, None, ()),
            step_time=target,
            transient_receptor_input=transient,
        )
        for neuron, transient in zip(layer.neurons, transients, strict=True)
    )
    return layer, drives


def prepare(execution_id: str, layer, target, drives):
    return prepare_lprh1f_base_drive_set(
        execution_id,
        layer,
        target,
        _digest(_field_prestate_payload(layer)),
        drives,
        hold_state_baseline,
        LPRH1F_BASE_TRANSITION_ID,
    )


def make_steering(
    execution_id: str,
    arm_id: str,
    prepared,
    *,
    handoff=None,
    local_values=(),
):
    source_kind = {
        "candidate": "CANDIDATE",
        "generic": "GENERIC",
        "no-context": "NO_CONTEXT",
        "digest-only": "DIGEST_ONLY",
    }[arm_id.rsplit(".", 1)[0]]
    generic_source_id = {
        "generic.low": "generic.low.source",
        "generic.high": "generic.high.source",
        "digest-only.low": "digest.low.source",
        "digest-only.high": "digest.high.source",
    }.get(arm_id)
    local = tuple(local_values)
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


class LPRH1FS1ZAPrivateLayerBoundContextConsumerTests(unittest.TestCase):
    def test_low_and_high_candidate_midpoints_are_exact(self) -> None:
        for level, prototype, expected in (
            ("low", -0.5, -0.25),
            ("high", 0.5, 0.25),
        ):
            execution = f"execution.synthetic.{level}"
            handoff, target, transient = build_handoff(
                prototype,
                execution_id=execution,
            )
            layer, drives = build_layer_and_drives(target, (transient,))
            prepared = prepare(execution, layer, target, drives)
            context = handoff.envelope.context
            assert context is not None
            local = tuple(
                (item.neuron_id, item.dock_id, item.carrier_id, item.prototype_value)
                for item in context.local_contexts
            )
            steering = make_steering(
                execution,
                f"candidate.{level}",
                prepared,
                handoff=handoff,
                local_values=local,
            )
            result = materialize_lprh1f_proposal(prepared, steering, ())
            output = result.proposal_set.ordered_outputs[0]
            self.assertEqual(expected, output.output_activation)
            self.assertEqual(0.125, output.output_afterimage)
            self.assertEqual(prototype, output.steering_value)

    def test_generic_equal_value_is_numerically_identical_to_candidate(self) -> None:
        execution = "execution.synthetic.low"
        handoff, target, transient = build_handoff(-0.5, execution_id=execution)
        layer, drives = build_layer_and_drives(target, (transient,))
        prepared = prepare(execution, layer, target, drives)
        context = handoff.envelope.context
        assert context is not None
        local = tuple(
            (item.neuron_id, item.dock_id, item.carrier_id, item.prototype_value)
            for item in context.local_contexts
        )
        candidate = materialize_lprh1f_proposal(
            prepared,
            make_steering(
                execution,
                "candidate.low",
                prepared,
                handoff=handoff,
                local_values=local,
            ),
            (),
        )
        generic = materialize_lprh1f_proposal(
            prepared,
            make_steering(
                execution,
                "generic.low",
                prepared,
                local_values=local,
            ),
            (),
        )
        candidate_values = tuple(
            (item.output_activation, item.output_afterimage)
            for item in candidate.proposal_set.ordered_outputs
        )
        generic_values = tuple(
            (item.output_activation, item.output_afterimage)
            for item in generic.proposal_set.ordered_outputs
        )
        self.assertEqual(candidate_values, generic_values)
        self.assertNotEqual(candidate.field_use_id, generic.field_use_id)

    def test_no_context_and_digest_only_copy_every_base_output(self) -> None:
        execution = "execution.synthetic.none"
        handoff, target, transient = build_handoff(
            0.5,
            execution_id=execution,
            recognized=False,
        )
        layer, drives = build_layer_and_drives(target, (transient,))
        prepared = prepare(execution, layer, target, drives)
        for arm, source in (
            ("no-context.low", handoff),
            ("no-context.high", handoff),
            ("digest-only.low", None),
            ("digest-only.high", None),
        ):
            steering = make_steering(
                execution,
                arm,
                prepared,
                handoff=source,
            )
            result = materialize_lprh1f_proposal(prepared, steering, ())
            output = result.proposal_set.ordered_outputs[0]
            self.assertIsNone(output.steering_value)
            self.assertEqual(output.base_activation, output.output_activation)
            self.assertEqual(output.base_afterimage, output.output_afterimage)

    def test_source_layer_prestate_and_drive_order_are_enforced(self) -> None:
        target = MCMFieldStepTime("field.clock", 21, 22, 1000.0)
        layer, drives = build_layer_and_drives(target, (None, None))
        prepared = prepare("execution.synthetic.order", layer, target, drives)
        self.assertEqual(layer.digest(), prepared.source_layer_digest)
        self.assertEqual(
            _digest(_field_prestate_payload(layer)),
            prepared.field_prestate_digest,
        )
        with self.assertRaises(LPRH1FConsumerError) as raised:
            prepare("execution.synthetic.order", layer, target, tuple(reversed(drives)))
        self.assertEqual(LPRH1F_PROVENANCE_MISMATCH, raised.exception.code)

        cloned_neurons = tuple(replace(neuron) for neuron in layer.neurons)
        cloned_layer = replace(layer, neurons=cloned_neurons)
        with self.assertRaises(LPRH1FConsumerError) as raised:
            prepare("execution.synthetic.order", cloned_layer, target, drives)
        self.assertEqual(LPRH1F_PROVENANCE_MISMATCH, raised.exception.code)

    def test_transition_registry_and_preparation_are_bound(self) -> None:
        target = MCMFieldStepTime("field.clock", 21, 22, 1000.0)
        layer, drives = build_layer_and_drives(target, (None, None))
        prepared = prepare("execution.synthetic.registry", layer, target, drives)
        self.assertEqual(2, prepared.base_transition_call_count)
        self.assertEqual(
            tuple(drive.previous.activation for drive in drives),
            tuple(item.base_output.activation for item in prepared.ordered_prepared_drives),
        )

        call_count = 0

        def unregistered(drive):
            nonlocal call_count
            call_count += 1
            return hold_state_baseline(drive)

        with self.assertRaises(LPRH1FConsumerError) as raised:
            prepare_lprh1f_base_drive_set(
                "execution.synthetic.registry",
                layer,
                target,
                _digest(_field_prestate_payload(layer)),
                drives,
                unregistered,
                LPRH1F_BASE_TRANSITION_ID,
            )
        self.assertEqual(LPRH1F_PROVENANCE_MISMATCH, raised.exception.code)
        self.assertEqual(0, call_count)

    def test_source_branch_and_local_mapping_fail_closed(self) -> None:
        execution = "execution.synthetic.mapping"
        handoff, target, transient = build_handoff(-0.5, execution_id=execution)
        layer, drives = build_layer_and_drives(target, (transient,))
        prepared = prepare(execution, layer, target, drives)
        wrong_local = (("neuron.0", "other.dock", "carrier.0", -0.5),)
        steering = make_steering(
            execution,
            "generic.low",
            prepared,
            local_values=wrong_local,
        )
        with self.assertRaises(LPRH1FConsumerError) as raised:
            materialize_lprh1f_proposal(prepared, steering, ())
        self.assertEqual(LPRH1F_LOCAL_MAPPING_MISMATCH, raised.exception.code)

        context = handoff.envelope.context
        assert context is not None
        with self.assertRaises(LPRH1FConsumerError) as raised:
            make_steering(
                execution,
                "candidate.low",
                prepared,
                handoff=handoff,
                local_values=(("neuron.0", "visual.dock", "carrier.0", 0.5),),
            )
        self.assertEqual(LPRH1F_ATOMIC_RESULT_REQUIRED, raised.exception.code)

    def test_duplicate_field_use_preserves_prior_ledger(self) -> None:
        execution = "execution.synthetic.duplicate"
        handoff, target, transient = build_handoff(0.5, execution_id=execution)
        layer, drives = build_layer_and_drives(target, (transient,))
        prepared = prepare(execution, layer, target, drives)
        context = handoff.envelope.context
        assert context is not None
        local = tuple(
            (item.neuron_id, item.dock_id, item.carrier_id, item.prototype_value)
            for item in context.local_contexts
        )
        steering = make_steering(
            execution,
            "candidate.high",
            prepared,
            handoff=handoff,
            local_values=local,
        )
        first = materialize_lprh1f_proposal(prepared, steering, ())
        prior = first.consumed_field_use_ids_after
        with self.assertRaises(LPRH1FConsumerError) as raised:
            materialize_lprh1f_proposal(prepared, steering, prior)
        self.assertEqual(LPRH1F_DUPLICATE_FIELD_USE, raised.exception.code)
        self.assertEqual((first.field_use_id,), prior)

    def test_digests_counters_and_public_surfaces_remain_private(self) -> None:
        execution = "execution.synthetic.boundary"
        handoff, target, transient = build_handoff(0.5, execution_id=execution)
        layer, drives = build_layer_and_drives(target, (transient,))
        prepared = prepare(execution, layer, target, drives)
        source_digest_before = hashlib.sha256(
            repr((layer, drives, handoff)).encode()
        ).hexdigest()
        context = handoff.envelope.context
        assert context is not None
        local = tuple(
            (item.neuron_id, item.dock_id, item.carrier_id, item.prototype_value)
            for item in context.local_contexts
        )
        result = materialize_lprh1f_proposal(
            prepared,
            make_steering(
                execution,
                "candidate.high",
                prepared,
                handoff=handoff,
                local_values=local,
            ),
            (),
        )
        self.assertEqual((1, 1, 0, 0, 0, 0), (
            result.consumer_call_count,
            result.mapped_steering_call_count,
            result.consumer_base_transition_call_count,
            result.partial_output_count,
            result.retry_count,
            result.field_step_count,
        ))
        self.assertEqual(64, len(result.result_digest))
        source_digest_after = hashlib.sha256(
            repr((layer, drives, handoff)).encode()
        ).hexdigest()
        self.assertEqual(source_digest_before, source_digest_after)
        with self.assertRaises(LPRH1FConsumerError) as raised:
            replace(
                result.proposal_set.ordered_outputs[0],
                output_activation=0.75,
            )
        self.assertEqual(LPRH1F_ATOMIC_RESULT_REQUIRED, raised.exception.code)
        with self.assertRaises(LPRH1FConsumerError) as raised:
            replace(result, field_use_id="0" * 64)
        self.assertEqual(LPRH1F_ATOMIC_RESULT_REQUIRED, raised.exception.code)
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
            "mcm_field_organism/shared_mcm_field.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1za", source)
            self.assertNotIn("lprh1f", source)


if __name__ == "__main__":
    unittest.main()
