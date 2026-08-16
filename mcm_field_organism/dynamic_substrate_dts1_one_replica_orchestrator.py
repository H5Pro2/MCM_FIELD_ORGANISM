"""Private pure runner for the single S1-KC technical exemplar."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Mapping

from .dynamic_substrate_dts1_common_interval_materializer import (
    DTS1CommonIntervalPrivateState,
    _field_payload,
    canonical_dts1_common_interval_envelope_fixtures,
    materialize_dts1_common_interval,
)
from .dynamic_substrate_dts1_private_baseline_adapters import (
    DTS1PrivateBaselineAdapterContext,
    S1_JW_CONFIGURATION_DIGESTS,
    advance_dts1_private_baseline,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_REPLICA_RECORDS,
    S1_JX_SEQUENCE_RECORDS,
)
from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    build_dts1_s1jz_finite_orchestrator_api_contract,
)
from .dynamic_substrate_s1kb_fresh_private_digest_correction import (
    S1_KB_CORRECTED_S1JZ_DIGEST,
    build_dts1_s1kb_fresh_private_digest_correction,
)
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer, PeriodicSamplingAxis
from .receptor_contract import ReceptorNeuronDockMap
from .shared_mcm_field import SharedFieldDock, SharedMCMField


class DTS1OneReplicaOrchestratorError(ValueError):
    """Raised atomically when the one permitted replica cannot complete."""


S1_KC_RUNNER_INPUT_SCHEMA_ID = "mcm.s1jz.one-replica-runner-input.v1"
S1_KC_CHECKPOINT_SCHEMA_ID = "mcm.s1jz.replica-checkpoint.v1"
S1_KC_OUTPUT_SCHEMA_ID = "mcm.s1jz.complete-replica-output.v1"
S1_KC_EXEMPLAR_REPLICA_ID = "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2"
S1_KC_IMPLEMENTATION_ID = "dynamic-substrate.one-replica-runner.s1kc.v1"
S1_KC_SOURCE_S1KB_DIGEST = (
    "b4099484095dbdb5b4d5fbdfd047c5f953e34d31d92e50381f36f8e874c0fd27"
)
S1_KC_EXEMPLAR_OUTPUT_DIGEST = (
    "bb098fbc3ce5d5da4c72b6b3da69ca789960e81e8299ca2a93621a66e4eea201"
)
S1_KC_DECISION = (
    "ONE_B1_P_IE_R2_REPLICA_RUNNER_IMPLEMENTED_TWO_BIT_IDENTICAL_TECHNICAL_REPEATS"
)
S1_KF_OUTPUT_SCHEMA_ID = "mcm.s1jz.complete-replica-output.v2"
S1_KF_COMPARISON_SCHEMA_ID = "mcm.s1ke.refinement-comparison-content.v1"
S1_KF_SOURCE_S1KE_DIGEST = (
    "1d9f500f74d895de52c5635b70aaf710a112f88cca1dc5f0cf8853393e831328"
)
S1_KF_IMPLEMENTATION_ID = "dynamic-substrate.dual-digest-r2-runner.s1kf.v1"
S1_KF_EXEMPLAR_OUTPUT_DIGEST = (
    "07325bb2d4c739483d7eea2dbe7110e8f5efe315a31946f937988f7dabc2882a"
)
S1_KF_EXEMPLAR_COMPARISON_DIGEST = (
    "276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589"
)
S1_KF_DECISION = (
    "R2_RUNNER_DUAL_PROVENANCE_AND_REFINEMENT_COMPARISON_DIGESTS_IMPLEMENTED_TWO_BIT_IDENTICAL_REPEATS"
)
S1_KH_SOURCE_S1KG_DIGEST = (
    "57305167b1d07803ac1d895d729c6b3f6b850561e766ab6e1d8028a0a00c3512"
)
S1_KH_TARGET_REPLICA_IDS = (
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KH_ALLOWED_REPLICA_IDS = (S1_KC_EXEMPLAR_REPLICA_ID,) + S1_KH_TARGET_REPLICA_IDS
S1_KH_IMPLEMENTATION_ID = "dynamic-substrate.b1-pie-r4-r8-extension.s1kh.v1"
S1_KH_TARGET_OUTPUT_DIGESTS = (
    "fe590916fb6608e91f8f1661859b3ef556ae81c835fa28ecf15484bec291d1f7",
    "047716609ea3aa9289eb376e2cd975bb9b28188eac925b4756b904a293c6f986",
)
S1_KH_DECISION = (
    "B1_P_IE_R4_R8_IMPLEMENTED_EIGHT_INTERVALS_COMPARISON_IDENTICAL_THREE_REFINEMENT_SET_ACCEPTED"
)
S1_KK_SOURCE_S1KJ_DIGEST = (
    "5f02c7ed2de53b713d19dbed514fd35d328a79c09663e119afc939da8949791d"
)
S1_KK_TARGET_REPLICA_IDS = (
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r2",
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KK_ALLOWED_REPLICA_IDS = S1_KH_ALLOWED_REPLICA_IDS + S1_KK_TARGET_REPLICA_IDS
S1_KK_IMPLEMENTATION_ID = "dynamic-substrate.b2-pie-three-refinement.s1kk.v1"
S1_KK_TARGET_OUTPUT_DIGESTS = (
    "881fc449aa7bcad3af2a2a9db3733020514f18842735488eebeb8331be3a71ff",
    "86c612c31fd18015079301828e0255c8d7deca9f6de3432b0a676bdbb8421de0",
    "3e86ef71ae7291d0578952bbc9b8ddcdfda44793b0e1a8d883fe6b1a3ad74648",
)
S1_KK_TARGET_COMPARISON_DIGEST = (
    "9b0b211b8f6459ec7c4be616c871c882be378af4ae6ea131a469e810dd9c29ae"
)
S1_KK_DECISION = (
    "B2_PIE_R2_R4_R8_IMPLEMENTED_TWELVE_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED"
)
S1_KN_SOURCE_S1KM_DIGEST = (
    "c54b795f54dae25d76717ad974dd329493f5993ac9613a4922f24c2d930a9af1"
)
S1_KN_IMPLEMENTATION_ID = (
    "dynamic-substrate.b1-checkpoint-replica-identity-correction.s1kn.v1"
)
S1_KN_CORRECTED_OUTPUT_DIGESTS = (
    "deb5611740ed7bdeccd13cfd2cea77ed3f6c1b7147e8c58e6d812c955b1e8790",
    "fdb9cb500337b7d9285d23c0b0d8f357db1c446cde5d5437a6fff11db7757a1f",
)
S1_KN_DECISION = (
    "B1_R4_R8_CHECKPOINT_IDENTITIES_CORRECTED_EIGHT_INTERVALS_COMPARISON_PRESERVED"
)
_REPLICA_BY_ID = {
    row[0]: row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KK_ALLOWED_REPLICA_IDS
}
_SEQUENCE_BY_KEY = {row[0]: row for row in S1_JX_SEQUENCE_RECORDS}


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _canonicalize(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DTS1OneReplicaOrchestratorError(
                "canonical output contains a non-finite number"
            )
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise DTS1OneReplicaOrchestratorError(
                "canonical output mapping keys must be strings"
            )
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    raise DTS1OneReplicaOrchestratorError(
        "canonical output contains a non-value object"
    )


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonicalize(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1OneReplicaRunnerInput:
    schema_id: str
    replica_id: str

    def __post_init__(self) -> None:
        if (
            self.schema_id != S1_KC_RUNNER_INPUT_SCHEMA_ID
            or self.replica_id not in S1_KK_ALLOWED_REPLICA_IDS
        ):
            raise DTS1OneReplicaOrchestratorError(
                "runner input is not the single registered S1-KC exemplar"
            )


@dataclass(frozen=True, slots=True)
class DTS1ReplicaCheckpoint:
    schema_id: str
    replica_id: str
    sequence_key: str
    sequence_digest: str
    ordinal: int
    interval_digest: str
    node_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    complete_field_digest: str
    private_state_digest: str
    adapter_output_digest: str

    def __post_init__(self) -> None:
        if self.schema_id != S1_KC_CHECKPOINT_SCHEMA_ID:
            raise DTS1OneReplicaOrchestratorError(
                "checkpoint schema differs from S1-JZ"
            )
        if self.replica_id not in S1_KK_ALLOWED_REPLICA_IDS:
            raise DTS1OneReplicaOrchestratorError("checkpoint replica differs")
        node_ids = tuple(self.node_ids)
        activation = tuple(self.activation)
        afterimage = tuple(self.afterimage)
        if (
            node_ids != ("node-a", "node-b")
            or len(activation) != 2
            or len(afterimage) != 2
            or any(not math.isfinite(value) for value in activation + afterimage)
            or any(
                not _is_digest(value)
                for value in (
                    self.sequence_digest,
                    self.interval_digest,
                    self.complete_field_digest,
                    self.private_state_digest,
                    self.adapter_output_digest,
                )
            )
        ):
            raise DTS1OneReplicaOrchestratorError(
                "checkpoint content is incomplete or non-canonical"
            )
        object.__setattr__(self, "node_ids", node_ids)
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "afterimage", afterimage)

    def canonical_payload(self) -> dict[str, object]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class DTS1OneReplicaOutput:
    schema_id: str
    replica_id: str
    model_role: str
    profile_block: str
    refinement: int
    sequence_digests: tuple[str, ...]
    checkpoints: tuple[DTS1ReplicaCheckpoint, ...]
    signed_components: tuple[float, ...]
    adapter_diagnostics: tuple[tuple[str, int, tuple[tuple[str, object], ...]], ...]
    refinement_comparison_digest: str
    output_digest: str

    def _comparison_payload(self) -> dict[str, object]:
        checkpoints = []
        for checkpoint in self.checkpoints:
            payload = checkpoint.canonical_payload()
            payload.pop("replica_id")
            checkpoints.append(payload)
        return {
            "schema_id": S1_KF_COMPARISON_SCHEMA_ID,
            "source_output_schema_id": self.schema_id,
            "model_role": self.model_role,
            "profile_block": self.profile_block,
            "sequence_digests": self.sequence_digests,
            "checkpoints": tuple(checkpoints),
            "signed_components": self.signed_components,
            "adapter_diagnostics": self.adapter_diagnostics,
        }

    def _payload(self, *, include_digest: bool) -> dict[str, object]:
        payload = {
            "schema_id": self.schema_id,
            "replica_id": self.replica_id,
            "model_role": self.model_role,
            "profile_block": self.profile_block,
            "refinement": self.refinement,
            "sequence_digests": self.sequence_digests,
            "checkpoints": tuple(
                checkpoint.canonical_payload() for checkpoint in self.checkpoints
            ),
            "signed_components": self.signed_components,
            "adapter_diagnostics": self.adapter_diagnostics,
            "refinement_comparison_digest": self.refinement_comparison_digest,
        }
        if include_digest:
            payload["output_digest"] = self.output_digest
        return payload

    def __post_init__(self) -> None:
        if (
            any(not isinstance(item, DTS1ReplicaCheckpoint) for item in self.checkpoints)
            or any(not isinstance(row, tuple) or len(row) != 3 for row in self.adapter_diagnostics)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "complete replica output contains invalid records"
            )
        checkpoint_signature = tuple(
            (item.sequence_key, item.sequence_digest, item.ordinal)
            for item in self.checkpoints
        )
        replica = _REPLICA_BY_ID.get(self.replica_id)
        if replica is None:
            raise DTS1OneReplicaOrchestratorError(
                "complete replica output identity is not registered"
            )
        expected_checkpoints = tuple(
            (key, _SEQUENCE_BY_KEY[key][4], ordinal)
            for key in replica[5]
            for ordinal in _SEQUENCE_BY_KEY[key][5]
        )
        if (
            self.schema_id != S1_KF_OUTPUT_SCHEMA_ID
            or self.model_role != replica[1]
            or self.profile_block != replica[3]
            or self.refinement != replica[4]
            or self.sequence_digests != replica[6]
            or len(self.checkpoints) != 4
            or len(self.signed_components) != 8
            or len(self.adapter_diagnostics) != 4
            or checkpoint_signature != expected_checkpoints
            or any(
                checkpoint.replica_id != self.replica_id
                for checkpoint in self.checkpoints
            )
            or tuple((row[0], row[1]) for row in self.adapter_diagnostics)
            != tuple((key, ordinal) for key, _digest_value, ordinal in expected_checkpoints)
            or any(not math.isfinite(value) for value in self.signed_components)
            or self.refinement_comparison_digest != _digest(self._comparison_payload())
            or self.output_digest != _digest(self._payload(include_digest=False))
        ):
            raise DTS1OneReplicaOrchestratorError(
                "complete replica output differs from the S1-JZ schema"
            )

    def canonical_payload(self) -> dict[str, object]:
        return self._payload(include_digest=True)


def _fresh_field_projection(field: SharedMCMField) -> tuple[tuple[str, object], ...]:
    neuron_rows = tuple(
        (
            ("node_id", neuron.neuron_id),
            ("position", neuron.position),
            ("activation", neuron.activation),
            ("afterimage", neuron.afterimage),
            ("perception_tick", neuron.perception.tick),
            ("receptor_contact", neuron.perception.receptor_contact),
            ("local_samples", neuron.perception.local_samples),
        )
        for neuron in field.layer.neurons
    )
    dock = field.docks[0]
    return (
        ("schema_id", "mcm.s1jz.fresh-field.v1"),
        ("field_id", field.field_id),
        ("layer_id", field.layer.layer_id),
        ("geometry_id", field.geometry_id),
        ("modality_id", field.layer.neurons[0].modality_id),
        ("sample_offsets", field.layer.sample_offsets),
        ("periodic_axes", tuple(axis.canonical_payload() for axis in field.layer.periodic_axes)),
        ("neurons", neuron_rows),
        ("dock", (
            ("dock_id", dock.dock_id),
            ("receptor_geometry_id", dock.dock_map.receptor_geometry_id),
            ("pairs", dock.dock_map.pairs),
        )),
        ("last_distribution", None),
        ("substrate", None),
        ("development", None),
    )


def _build_fresh_two_node_state(
    model_role: str,
) -> tuple[SharedMCMField, DTS1CommonIntervalPrivateState]:
    contract = build_dts1_s1jz_finite_orchestrator_api_contract()
    if contract.contract_digest != S1_KB_CORRECTED_S1JZ_DIGEST:
        raise DTS1OneReplicaOrchestratorError("corrected S1-JZ contract differs")
    records = tuple(
        row
        for row in contract.fresh_state_records
        if row[0] == model_role and row[1] == "TWO_NODE_OPEN_LINE"
    )
    if len(records) != 1:
        raise DTS1OneReplicaOrchestratorError("fresh exemplar state is not unique")
    record = records[0]
    payload = dict(record[5])
    neurons = tuple(
        MCMNeuron(
            neuron_id=values["node_id"],
            field_id=payload["field_id"],
            modality_id=payload["modality_id"],
            geometry_id=payload["geometry_id"],
            position=values["position"],
            activation=values["activation"],
            afterimage=values["afterimage"],
            perception=MCMFieldPerception(
                values["perception_tick"],
                values["receptor_contact"],
                values["local_samples"],
            ),
        )
        for values in (dict(row) for row in payload["neurons"])
    )
    layer = MCMNeuronLayer(
        payload["layer_id"],
        neurons,
        payload["sample_offsets"],
        tuple(PeriodicSamplingAxis(**dict(row)) for row in payload["periodic_axes"]),
        record[2],
    )
    dock_values = dict(payload["dock"])
    dock = SharedFieldDock(
        dock_values["dock_id"],
        ReceptorNeuronDockMap(
            payload["modality_id"],
            dock_values["receptor_geometry_id"],
            dock_values["pairs"],
        ),
    )
    field = SharedMCMField(layer, (dock,))
    private_state = DTS1CommonIntervalPrivateState(model_role, record[7])
    if (
        _fresh_field_projection(field) != record[5]
        or _digest(record[5]) != record[6]
        or _digest(private_state.canonical_payload()) != record[8]
    ):
        raise DTS1OneReplicaOrchestratorError(
            "fresh exemplar state does not roundtrip exactly"
        )
    return field, private_state


def _build_fresh_b1_two_node_state(
) -> tuple[SharedMCMField, DTS1CommonIntervalPrivateState]:
    return _build_fresh_two_node_state("B1")


def _checkpoint(
    replica_id, sequence_key, fixture, output
) -> DTS1ReplicaCheckpoint:
    neurons = tuple(
        sorted(output.complete_field.layer.neurons, key=lambda item: item.position)
    )
    return DTS1ReplicaCheckpoint(
        S1_KC_CHECKPOINT_SCHEMA_ID,
        replica_id,
        sequence_key,
        fixture.sequence_digest,
        fixture.ordinal,
        fixture.interval_digest,
        tuple(item.neuron_id for item in neurons),
        tuple(item.activation for item in neurons),
        tuple(item.afterimage for item in neurons),
        _digest(_field_payload(output.complete_field)),
        _digest(output.next_private_state.canonical_payload()),
        output.output_digest,
    )


def run_dts1_one_replica(
    runner_input: DTS1OneReplicaRunnerInput,
) -> DTS1OneReplicaOutput:
    """Run one registered B1/B2 P_IE replica or publish one atomic error."""

    try:
        if not isinstance(runner_input, DTS1OneReplicaRunnerInput):
            raise DTS1OneReplicaOrchestratorError(
                "runner requires one complete registered input"
            )
        replica = _REPLICA_BY_ID.get(runner_input.replica_id)
        expected_long_role = {
            "B1": "B1_FIXED_PRERELEASE_ADAPTER",
            "B2": "B2_S2_LINEAR_INTEGRATOR",
        }
        if replica is None or replica[1] not in expected_long_role or replica[1:9] != (
            replica[1],
            expected_long_role[replica[1]],
            "P_IE_CAUSAL_TWO_SUBSTEP",
            replica[4],
            ("P_IE_F_HIGH", "P_IE_R_HIGH"),
            replica[6],
            4,
            4,
        ):
            raise DTS1OneReplicaOrchestratorError("registered exemplar differs")
        fixtures = canonical_dts1_common_interval_envelope_fixtures()
        checkpoints = []
        diagnostics = []
        for sequence_key in replica[5]:
            sequence = _SEQUENCE_BY_KEY[sequence_key]
            sequence_fixtures = tuple(
                item for item in fixtures if item.sequence_digest == sequence[4]
            )
            if (
                len(sequence_fixtures) != sequence[3]
                or tuple(item.interval_digest for item in sequence_fixtures) != sequence[6]
            ):
                raise DTS1OneReplicaOrchestratorError("sequence registry differs")
            if replica[1] == "B1":
                field, private_state = _build_fresh_b1_two_node_state()
            else:
                field, private_state = _build_fresh_two_node_state(replica[1])
            prior_envelope_digest = None
            prior_output_digest = None
            for fixture in sequence_fixtures:
                materialized = materialize_dts1_common_interval(
                    fixture,
                    replica[1],
                    field,
                    private_state,
                    prior_envelope_digest,
                    prior_output_digest,
                )
                context = DTS1PrivateBaselineAdapterContext(
                    replica[1],
                    private_state,
                    S1_JW_CONFIGURATION_DIGESTS[replica[1]],
                    replica[4],
                )
                output = advance_dts1_private_baseline(
                    materialized.model_invocation, context
                )
                field = output.complete_field
                private_state = output.next_private_state
                prior_envelope_digest = fixture.interval_digest
                prior_output_digest = output.output_digest
                diagnostics.append((sequence_key, fixture.ordinal, output.diagnostics))
                if fixture.checkpoint_after_interval:
                    checkpoints.append(
                        _checkpoint(
                            runner_input.replica_id, sequence_key, fixture, output
                        )
                    )
        checkpoint_by_key = {
            (checkpoint.sequence_key, checkpoint.ordinal): checkpoint
            for checkpoint in checkpoints
        }
        component_rows = tuple(
            row
            for row in build_dts1_s1jz_finite_orchestrator_api_contract().component_index_records
            if row[0] == "P_IE_CAUSAL_TWO_SUBSTEP"
        )
        signed_components = []
        for row in component_rows:
            left = checkpoint_by_key[(row[2], row[3])]
            right = checkpoint_by_key[(row[4], row[5])]
            node_index = left.node_ids.index(row[7])
            left_values = left.activation if row[6] == "activation" else left.afterimage
            right_values = right.activation if row[6] == "activation" else right.afterimage
            signed_components.append(left_values[node_index] - right_values[node_index])
        values = {
            "schema_id": S1_KF_OUTPUT_SCHEMA_ID,
            "replica_id": runner_input.replica_id,
            "model_role": replica[1],
            "profile_block": replica[3],
            "refinement": replica[4],
            "sequence_digests": replica[6],
            "checkpoints": tuple(checkpoints),
            "signed_components": tuple(signed_components),
            "adapter_diagnostics": tuple(diagnostics),
        }
        comparison_payload = {
            "schema_id": S1_KF_COMPARISON_SCHEMA_ID,
            "source_output_schema_id": values["schema_id"],
            "model_role": values["model_role"],
            "profile_block": values["profile_block"],
            "sequence_digests": values["sequence_digests"],
            "checkpoints": tuple(
                {
                    key: value
                    for key, value in item.canonical_payload().items()
                    if key != "replica_id"
                }
                for item in values["checkpoints"]
            ),
            "signed_components": values["signed_components"],
            "adapter_diagnostics": values["adapter_diagnostics"],
        }
        values["refinement_comparison_digest"] = _digest(comparison_payload)
        return DTS1OneReplicaOutput(
            **values,
            output_digest=_digest({
                **values,
                "checkpoints": tuple(
                    item.canonical_payload() for item in values["checkpoints"]
                ),
            }),
        )
    except DTS1OneReplicaOrchestratorError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise DTS1OneReplicaOrchestratorError(str(exc)) from exc


def run_dts1_b1_pie_r4_r8_extension(
) -> tuple[DTS1OneReplicaOutput, DTS1OneReplicaOutput]:
    """Run the exact S1-KG pair once and publish only a complete accepted pair."""

    try:
        outputs = tuple(
            run_dts1_one_replica(
                DTS1OneReplicaRunnerInput(S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id)
            )
            for replica_id in S1_KH_TARGET_REPLICA_IDS
        )
        if (
            tuple(output.replica_id for output in outputs) != S1_KH_TARGET_REPLICA_IDS
            or any(
                output.refinement_comparison_digest
                != S1_KF_EXEMPLAR_COMPARISON_DIGEST
                for output in outputs
            )
            or len({output.output_digest for output in outputs}) != 2
        ):
            raise DTS1OneReplicaOrchestratorError(
                "r4/r8 outputs fail the atomic S1-KG acceptance rules"
            )
        return outputs
    except DTS1OneReplicaOrchestratorError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise DTS1OneReplicaOrchestratorError(str(exc)) from exc


def run_dts1_s1kn_corrected_b1_pie_pair(
) -> tuple[DTS1OneReplicaOutput, DTS1OneReplicaOutput]:
    """Run and accept only the corrected S1-KM B1 r4/r8 pair."""

    outputs = run_dts1_b1_pie_r4_r8_extension()
    if (
        tuple(output.output_digest for output in outputs)
        != S1_KN_CORRECTED_OUTPUT_DIGESTS
        or any(
            tuple(checkpoint.replica_id for checkpoint in output.checkpoints)
            != (output.replica_id,) * 4
            for output in outputs
        )
    ):
        raise DTS1OneReplicaOrchestratorError(
            "corrected B1 pair differs from the S1-KM identity contract"
        )
    return outputs


def run_dts1_b2_pie_three_refinement(
) -> tuple[DTS1OneReplicaOutput, DTS1OneReplicaOutput, DTS1OneReplicaOutput]:
    """Run the exact S1-KJ B2 set once and publish only an accepted triple."""

    try:
        outputs = tuple(
            run_dts1_one_replica(
                DTS1OneReplicaRunnerInput(S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id)
            )
            for replica_id in S1_KK_TARGET_REPLICA_IDS
        )
        if (
            tuple(output.replica_id for output in outputs)
            != S1_KK_TARGET_REPLICA_IDS
            or any(output.model_role != "B2" for output in outputs)
            or len({output.refinement_comparison_digest for output in outputs}) != 1
            or len({output.output_digest for output in outputs}) != 3
        ):
            raise DTS1OneReplicaOrchestratorError(
                "B2 r2/r4/r8 outputs fail the atomic S1-KJ acceptance rules"
            )
        return outputs
    except DTS1OneReplicaOrchestratorError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise DTS1OneReplicaOrchestratorError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DTS1S1KCImplementationReceipt:
    implementation_id: str
    source_s1kb_digest: str
    exemplar_replica_id: str
    repeat_output_digests: tuple[str, str]
    technical_repeat_count: int
    interval_calls_per_repeat: int
    total_interval_calls: int
    checkpoint_count_per_repeat: int
    signed_component_count: int
    fresh_state_factory_implemented: bool
    private_pure_runner_implemented: bool
    other_replicas_executed: int
    complete_matrix_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_KC_IMPLEMENTATION_ID
            or self.source_s1kb_digest != S1_KC_SOURCE_S1KB_DIGEST
            or self.exemplar_replica_id != S1_KC_EXEMPLAR_REPLICA_ID
            or self.repeat_output_digests
            != (S1_KC_EXEMPLAR_OUTPUT_DIGEST,) * 2
            or self.technical_repeat_count != 2
            or self.interval_calls_per_repeat != 4
            or self.total_interval_calls != 8
            or self.checkpoint_count_per_repeat != 4
            or self.signed_component_count != 8
            or self.fresh_state_factory_implemented is not True
            or self.private_pure_runner_implemented is not True
            or self.other_replicas_executed != 0
            or self.complete_matrix_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.decision != S1_KC_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "S1-KC implementation receipt was weakened"
            )


def build_dts1_s1kc_implementation_receipt() -> DTS1S1KCImplementationReceipt:
    """Return the two-repeat acceptance record without executing the runner."""

    source = build_dts1_s1kb_fresh_private_digest_correction()
    values = {
        "implementation_id": S1_KC_IMPLEMENTATION_ID,
        "source_s1kb_digest": source.audit_digest,
        "exemplar_replica_id": S1_KC_EXEMPLAR_REPLICA_ID,
        "repeat_output_digests": (S1_KC_EXEMPLAR_OUTPUT_DIGEST,) * 2,
        "technical_repeat_count": 2,
        "interval_calls_per_repeat": 4,
        "total_interval_calls": 8,
        "checkpoint_count_per_repeat": 4,
        "signed_component_count": 8,
        "fresh_state_factory_implemented": True,
        "private_pure_runner_implemented": True,
        "other_replicas_executed": 0,
        "complete_matrix_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "decision": S1_KC_DECISION,
    }
    return DTS1S1KCImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class DTS1S1KFImplementationReceipt:
    implementation_id: str
    source_s1ke_digest: str
    exemplar_replica_id: str
    output_schema_id: str
    comparison_schema_id: str
    repeat_output_digests: tuple[str, str]
    repeat_comparison_digests: tuple[str, str]
    technical_repeat_count: int
    interval_calls_per_repeat: int
    total_interval_calls: int
    dual_digest_output_implemented: bool
    complete_provenance_digest_identity_bearing: bool
    comparison_digest_identity_neutral: bool
    r4_r8_runner_implemented: bool
    r4_r8_replicas_executed: int
    complete_matrix_cases_executed: int
    runtime_integration_present: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_KF_IMPLEMENTATION_ID
            or self.source_s1ke_digest != S1_KF_SOURCE_S1KE_DIGEST
            or self.exemplar_replica_id != S1_KC_EXEMPLAR_REPLICA_ID
            or self.output_schema_id != S1_KF_OUTPUT_SCHEMA_ID
            or self.comparison_schema_id != S1_KF_COMPARISON_SCHEMA_ID
            or self.repeat_output_digests != (S1_KF_EXEMPLAR_OUTPUT_DIGEST,) * 2
            or self.repeat_comparison_digests
            != (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2
            or self.technical_repeat_count != 2
            or self.interval_calls_per_repeat != 4
            or self.total_interval_calls != 8
            or self.dual_digest_output_implemented is not True
            or self.complete_provenance_digest_identity_bearing is not True
            or self.comparison_digest_identity_neutral is not True
            or self.r4_r8_runner_implemented is not False
            or self.r4_r8_replicas_executed != 0
            or self.complete_matrix_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.decision != S1_KF_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "S1-KF implementation receipt was weakened"
            )


def build_dts1_s1kf_implementation_receipt() -> DTS1S1KFImplementationReceipt:
    """Return the dual-digest r2 acceptance record without running a replica."""

    from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
        build_dts1_s1ke_dual_refinement_digest_contract,
    )

    source = build_dts1_s1ke_dual_refinement_digest_contract()
    values = {
        "implementation_id": S1_KF_IMPLEMENTATION_ID,
        "source_s1ke_digest": source.contract_digest,
        "exemplar_replica_id": S1_KC_EXEMPLAR_REPLICA_ID,
        "output_schema_id": S1_KF_OUTPUT_SCHEMA_ID,
        "comparison_schema_id": S1_KF_COMPARISON_SCHEMA_ID,
        "repeat_output_digests": (S1_KF_EXEMPLAR_OUTPUT_DIGEST,) * 2,
        "repeat_comparison_digests": (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2,
        "technical_repeat_count": 2,
        "interval_calls_per_repeat": 4,
        "total_interval_calls": 8,
        "dual_digest_output_implemented": True,
        "complete_provenance_digest_identity_bearing": True,
        "comparison_digest_identity_neutral": True,
        "r4_r8_runner_implemented": False,
        "r4_r8_replicas_executed": 0,
        "complete_matrix_cases_executed": 0,
        "runtime_integration_present": False,
        "decision": S1_KF_DECISION,
    }
    return DTS1S1KFImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class DTS1S1KHImplementationReceipt:
    implementation_id: str
    source_s1kg_digest: str
    target_replica_ids: tuple[str, str]
    target_output_digests: tuple[str, str]
    target_comparison_digests: tuple[str, str]
    bound_r2_output_digest: str
    bound_r2_comparison_digest: str
    target_replica_count: int
    interval_calls_per_target: int
    total_new_interval_calls: int
    runner_registry_extended: bool
    atomic_pair_acceptance_implemented: bool
    three_refinement_comparison_set_accepted: bool
    complete_provenance_digests_all_distinct: bool
    matrix_case_output_published: bool
    other_roles_executed: int
    runtime_integration_present: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_KH_IMPLEMENTATION_ID
            or self.source_s1kg_digest != S1_KH_SOURCE_S1KG_DIGEST
            or self.target_replica_ids != S1_KH_TARGET_REPLICA_IDS
            or self.target_output_digests != S1_KH_TARGET_OUTPUT_DIGESTS
            or self.target_comparison_digests
            != (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2
            or self.bound_r2_output_digest != S1_KF_EXEMPLAR_OUTPUT_DIGEST
            or self.bound_r2_comparison_digest != S1_KF_EXEMPLAR_COMPARISON_DIGEST
            or self.target_replica_count != 2
            or self.interval_calls_per_target != 4
            or self.total_new_interval_calls != 8
            or self.runner_registry_extended is not True
            or self.atomic_pair_acceptance_implemented is not True
            or self.three_refinement_comparison_set_accepted is not True
            or self.complete_provenance_digests_all_distinct is not True
            or self.matrix_case_output_published is not False
            or self.other_roles_executed != 0
            or self.runtime_integration_present is not False
            or self.decision != S1_KH_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "S1-KH implementation receipt was weakened"
            )


def build_dts1_s1kh_implementation_receipt() -> DTS1S1KHImplementationReceipt:
    """Return the accepted r4/r8 record without running either replica."""

    from .dynamic_substrate_s1kg_b1_pie_refinement_extension_contract import (
        build_dts1_s1kg_b1_pie_refinement_extension_contract,
    )

    source = build_dts1_s1kg_b1_pie_refinement_extension_contract()
    provenance_digests = (S1_KF_EXEMPLAR_OUTPUT_DIGEST,) + S1_KH_TARGET_OUTPUT_DIGESTS
    values = {
        "implementation_id": S1_KH_IMPLEMENTATION_ID,
        "source_s1kg_digest": source.contract_digest,
        "target_replica_ids": S1_KH_TARGET_REPLICA_IDS,
        "target_output_digests": S1_KH_TARGET_OUTPUT_DIGESTS,
        "target_comparison_digests": (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2,
        "bound_r2_output_digest": S1_KF_EXEMPLAR_OUTPUT_DIGEST,
        "bound_r2_comparison_digest": S1_KF_EXEMPLAR_COMPARISON_DIGEST,
        "target_replica_count": 2,
        "interval_calls_per_target": 4,
        "total_new_interval_calls": 8,
        "runner_registry_extended": True,
        "atomic_pair_acceptance_implemented": True,
        "three_refinement_comparison_set_accepted": True,
        "complete_provenance_digests_all_distinct": len(set(provenance_digests)) == 3,
        "matrix_case_output_published": False,
        "other_roles_executed": 0,
        "runtime_integration_present": False,
        "decision": S1_KH_DECISION,
    }
    return DTS1S1KHImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class DTS1S1KKImplementationReceipt:
    implementation_id: str
    source_s1kj_digest: str
    target_replica_ids: tuple[str, str, str]
    target_output_digests: tuple[str, str, str]
    target_comparison_digests: tuple[str, str, str]
    target_replica_count: int
    interval_calls_per_target: int
    total_new_interval_calls: int
    runner_registry_extended: bool
    corrected_b2_fresh_state_used: bool
    sequence_local_complete_l_carry_implemented: bool
    atomic_triple_acceptance_implemented: bool
    three_refinement_comparison_set_accepted: bool
    complete_provenance_digests_all_distinct: bool
    case_output_composed: bool
    matrix_case_output_published: bool
    other_roles_or_profiles_executed: int
    runtime_integration_present: bool
    baseline_or_candidate_judgment_present: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_KK_IMPLEMENTATION_ID
            or self.source_s1kj_digest != S1_KK_SOURCE_S1KJ_DIGEST
            or self.target_replica_ids != S1_KK_TARGET_REPLICA_IDS
            or self.target_output_digests != S1_KK_TARGET_OUTPUT_DIGESTS
            or self.target_comparison_digests
            != (S1_KK_TARGET_COMPARISON_DIGEST,) * 3
            or self.target_replica_count != 3
            or self.interval_calls_per_target != 4
            or self.total_new_interval_calls != 12
            or self.runner_registry_extended is not True
            or self.corrected_b2_fresh_state_used is not True
            or self.sequence_local_complete_l_carry_implemented is not True
            or self.atomic_triple_acceptance_implemented is not True
            or self.three_refinement_comparison_set_accepted is not True
            or self.complete_provenance_digests_all_distinct is not True
            or self.case_output_composed is not False
            or self.matrix_case_output_published is not False
            or self.other_roles_or_profiles_executed != 0
            or self.runtime_integration_present is not False
            or self.baseline_or_candidate_judgment_present is not False
            or self.decision != S1_KK_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "S1-KK implementation receipt was weakened"
            )


def build_dts1_s1kk_implementation_receipt() -> DTS1S1KKImplementationReceipt:
    """Return the accepted B2 triple record without running a replica."""

    from .dynamic_substrate_s1kj_b2_pie_case_selection_contract import (
        build_dts1_s1kj_b2_pie_case_selection_contract,
    )

    source = build_dts1_s1kj_b2_pie_case_selection_contract()
    values = {
        "implementation_id": S1_KK_IMPLEMENTATION_ID,
        "source_s1kj_digest": source.contract_digest,
        "target_replica_ids": S1_KK_TARGET_REPLICA_IDS,
        "target_output_digests": S1_KK_TARGET_OUTPUT_DIGESTS,
        "target_comparison_digests": (S1_KK_TARGET_COMPARISON_DIGEST,) * 3,
        "target_replica_count": 3,
        "interval_calls_per_target": 4,
        "total_new_interval_calls": 12,
        "runner_registry_extended": True,
        "corrected_b2_fresh_state_used": True,
        "sequence_local_complete_l_carry_implemented": True,
        "atomic_triple_acceptance_implemented": True,
        "three_refinement_comparison_set_accepted": True,
        "complete_provenance_digests_all_distinct": (
            len(set(S1_KK_TARGET_OUTPUT_DIGESTS)) == 3
        ),
        "case_output_composed": False,
        "matrix_case_output_published": False,
        "other_roles_or_profiles_executed": 0,
        "runtime_integration_present": False,
        "baseline_or_candidate_judgment_present": False,
        "decision": S1_KK_DECISION,
    }
    return DTS1S1KKImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )


@dataclass(frozen=True, slots=True)
class DTS1S1KNImplementationReceipt:
    implementation_id: str
    source_s1km_digest: str
    target_replica_ids: tuple[str, str]
    historical_output_digests: tuple[str, str]
    corrected_output_digests: tuple[str, str]
    corrected_comparison_digests: tuple[str, str]
    target_replica_count: int
    interval_calls_per_target: int
    total_new_interval_calls: int
    checkpoint_parent_identity_implemented: bool
    fail_closed_output_validation_implemented: bool
    atomic_corrected_pair_accepted: bool
    numeric_comparison_content_preserved: bool
    corrected_provenance_digests_distinct: bool
    historical_records_rewritten: bool
    b1_r2_or_b2_replicas_executed: int
    case_output_composed: bool
    matrix_case_output_published: bool
    baseline_or_candidate_judgment_present: bool
    runtime_integration_present: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_KN_IMPLEMENTATION_ID
            or self.source_s1km_digest != S1_KN_SOURCE_S1KM_DIGEST
            or self.target_replica_ids != S1_KH_TARGET_REPLICA_IDS
            or self.historical_output_digests != S1_KH_TARGET_OUTPUT_DIGESTS
            or self.corrected_output_digests != S1_KN_CORRECTED_OUTPUT_DIGESTS
            or self.corrected_comparison_digests
            != (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2
            or self.target_replica_count != 2
            or self.interval_calls_per_target != 4
            or self.total_new_interval_calls != 8
            or self.checkpoint_parent_identity_implemented is not True
            or self.fail_closed_output_validation_implemented is not True
            or self.atomic_corrected_pair_accepted is not True
            or self.numeric_comparison_content_preserved is not True
            or self.corrected_provenance_digests_distinct is not True
            or self.historical_records_rewritten is not False
            or self.b1_r2_or_b2_replicas_executed != 0
            or self.case_output_composed is not False
            or self.matrix_case_output_published is not False
            or self.baseline_or_candidate_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_KN_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1OneReplicaOrchestratorError(
                "S1-KN implementation receipt was weakened"
            )


def build_dts1_s1kn_implementation_receipt() -> DTS1S1KNImplementationReceipt:
    """Return the corrected pair record without executing either replica."""

    from .dynamic_substrate_s1km_checkpoint_identity_correction_contract import (
        build_dts1_s1km_checkpoint_identity_correction_contract,
    )

    source = build_dts1_s1km_checkpoint_identity_correction_contract()
    all_provenance = S1_KH_TARGET_OUTPUT_DIGESTS + S1_KN_CORRECTED_OUTPUT_DIGESTS
    values = {
        "implementation_id": S1_KN_IMPLEMENTATION_ID,
        "source_s1km_digest": source.contract_digest,
        "target_replica_ids": S1_KH_TARGET_REPLICA_IDS,
        "historical_output_digests": S1_KH_TARGET_OUTPUT_DIGESTS,
        "corrected_output_digests": S1_KN_CORRECTED_OUTPUT_DIGESTS,
        "corrected_comparison_digests": (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2,
        "target_replica_count": 2,
        "interval_calls_per_target": 4,
        "total_new_interval_calls": 8,
        "checkpoint_parent_identity_implemented": True,
        "fail_closed_output_validation_implemented": True,
        "atomic_corrected_pair_accepted": True,
        "numeric_comparison_content_preserved": True,
        "corrected_provenance_digests_distinct": len(set(all_provenance)) == 4,
        "historical_records_rewritten": False,
        "b1_r2_or_b2_replicas_executed": 0,
        "case_output_composed": False,
        "matrix_case_output_published": False,
        "baseline_or_candidate_judgment_present": False,
        "runtime_integration_present": False,
        "decision": S1_KN_DECISION,
    }
    return DTS1S1KNImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )
