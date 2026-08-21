"""Pure four-node fresh-bundle to model-input assembly."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re

from .four_node_fresh_factory import (
    FourNodeFixedAdapterState,
    FourNodeFreshBundle,
    FourNodeIntegratorState,
    FourNodeM4FreshState,
    FourNodePrivateFreshState,
    FourNodeSubstrateFreshState,
)
from .m1_parallel_leak_replace_s_compositor import M1ParallelLeakBankState
from .m2_bounded_buffer_replace_s_compositor import M2BoundedBufferState
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .w7n_capacity_function_baselines import W7NLocalBaselineState


class FourNodeModelInputAssemblyError(ValueError):
    """Raised before an invalid model-input assembly can be published."""


PUBLIC_FIELD_IDENTITY = "PUBLIC_FIELD_IDENTITY"
NATIVE_SUBSTRATE_COPY = "NATIVE_SUBSTRATE_COPY"

_ROLE_SURFACES = {
    "A0_CURRENT_CONTACT": "neutral.current-contact",
    "A1_FAST_SH": "neutral.fast-sh",
    "A2_B1_FIXED_ADAPTER": "four-node.fixed-adapter",
    "A2_B2_INTEGRATOR": "four-node.integrator",
    "A2_B3_LOCAL_LEAKY": "mcm-f3.local-leaky",
    "A2_B4_LINEAR_COUPLED": "mcm-f3.linear-coupled",
    "A2_B5_F3_FULL": "mcm-f3.full",
    "A2_B6_CONST_V": "mcm-f3.const-v",
    "A3_NORM": "replace-s.norm",
    "M1_PARALLEL_LEAK": "replace-s.parallel-leak",
    "M2_DELAY": "replace-s.bounded-buffer.delay",
    "M2_REPLAY": "replace-s.bounded-buffer.replay",
    "M4_DTS1_T1": "dts1.t1-coupled-fast-field",
    "M5_DIRECT": "replace-s.direct-leak",
}
_SUBSTRATE_ROLES = frozenset(
    {
        "A2_B3_LOCAL_LEAKY",
        "A2_B4_LINEAR_COUPLED",
        "A2_B5_F3_FULL",
        "A2_B6_CONST_V",
    }
)
_STATELESS_MARKERS = {
    "A0_CURRENT_CONTACT": "STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ",
    "A1_FAST_SH": "FIELD_ONLY:A1_FAST_SH:S1RJ",
}
_PRIVATE_DIGESTS = {
    "A2_B1_FIXED_ADAPTER": "8a55ecf2cac9e4d3268eeb125cb7a6bcd2a4e79e005fbf79a381569fe30911ce",
    "A2_B2_INTEGRATOR": "cf1f3b36b7e47645df478c0e6099db79d199df95ef9cb0fa9f0288904928be05",
    "A2_B3_LOCAL_LEAKY": "89924659b50b545c17bd1734a4440764db29063f8d328719f5863d6ed230e12b",
    "A2_B4_LINEAR_COUPLED": "8d2a656d81d72e430d9c66611b92efc371866b65aefd530c079c67ffaa01b52e",
    "A2_B5_F3_FULL": "bd23b8ea5811d21c9a3abddf8622183d54b9cfb5a2aa3f0ebec8a2d5c92b3d89",
    "A2_B6_CONST_V": "2c7899a846853d1683aa2a0421ffda2f7cbd8951399c008a20932c0ca67edfc0",
    "A3_NORM": "f52e3304538891ed7f9b9eb7ca8d3bbfc79bbf8284ac506f6496ad7052ab2ab4",
    "M1_PARALLEL_LEAK": "c84829037970255ca0e16417cae9001938a5a50843cc416325c0a9f44963afc5",
    "M2_DELAY": "97ff90b67e001ba3346173f8a1df7620a5b2895022df14947f34142595f03ea0",
    "M2_REPLAY": "5fc1d98b534e5a6fbe13afe6913e86011ceed7b2b1f94be7c9abb375aaa08be7",
    "M4_DTS1_T1": "c673984c64f88074d276f4430e92a4b9242f1118d47eaa85d4a776f405169b2f",
    "M5_DIRECT": "7eed04ea4fbc72d8c7370ee96ee2a509b9384bc9ec19be54cc533b8f89434edc",
}
_NODE_IDENTITIES = (
    ("node-a", (0,)),
    ("node-b", (1,)),
    ("node-c", (2,)),
    ("node-d", (3,)),
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _fail(code: str, detail: str) -> None:
    raise FourNodeModelInputAssemblyError(f"{code}: {detail}")


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not (-float("inf") < value < float("inf")):
            _fail("MODEL_INPUT_DIGEST_INVALID", "canonical number must be finite")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            _fail("MODEL_INPUT_DIGEST_INVALID", "canonical keys must be strings")
        return {key: _canonical(value[key]) for key in sorted(value)}
    _fail("MODEL_INPUT_DIGEST_INVALID", "canonical payload contains an object")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        _canonical(payload),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _field_shell_payload(field: SharedMCMField) -> dict[str, object]:
    return {
        "field_id": field.field_id,
        "geometry_id": field.geometry_id,
        "layer_id": field.layer.layer_id,
        "sample_offsets": field.layer.sample_offsets,
        "periodic_axes": tuple(
            (item.axis, item.period) for item in field.layer.periodic_axes
        ),
        "docks": tuple(
            (
                dock.dock_id,
                dock.dock_map.modality_id,
                dock.dock_map.receptor_geometry_id,
                dock.dock_map.pairs,
            )
            for dock in field.docks
        ),
        "last_distribution": field.last_distribution,
        "nodes": tuple(
            (
                neuron.neuron_id,
                neuron.position,
                neuron.modality_id,
                neuron.activation,
                neuron.afterimage,
                neuron.tick,
                neuron.perception.tick,
                neuron.perception.receptor_contact,
                tuple(
                    (sample.position, sample.activation, sample.afterimage)
                    for sample in neuron.perception.local_samples
                ),
            )
            for neuron in field.layer.neurons
        ),
    }


def _validate_public_fresh_field(field: object) -> SharedMCMField:
    if not isinstance(field, SharedMCMField):
        _fail("MODEL_INPUT_PUBLIC_FIELD_INVALID", "shared field required")
    if (
        field.field_id != "mcm.s1rf.field.4n"
        or field.geometry_id != "mcm.s1rf.geometry.4n"
        or field.layer.layer_id != "mcm.s1rf.layer.4n"
        or field.layer.sample_offsets != ((-1,), (1,))
        or field.layer.periodic_axes != ()
        or field.last_distribution is not None
        or field.substrate is not None
        or field.development is not None
    ):
        _fail("MODEL_INPUT_PUBLIC_FIELD_INVALID", "fresh field shell differs")
    if tuple((item.neuron_id, item.position) for item in field.layer.neurons) != _NODE_IDENTITIES:
        _fail("MODEL_INPUT_PUBLIC_FIELD_INVALID", "node identity or order differs")
    for neuron in field.layer.neurons:
        if (
            neuron.modality_id != "technical-control"
            or neuron.activation != 0.0
            or neuron.afterimage != 0.0
            or neuron.tick != 0
            or neuron.perception.tick != 0
            or neuron.perception.receptor_contact != 0.0
            or neuron.perception.local_samples != ()
        ):
            _fail("MODEL_INPUT_PUBLIC_FIELD_INVALID", "node fresh value differs")
    expected_dock = (
        "dock.s1rf.technical-control.4n",
        "technical-control",
        "mcm.s1rf.receptor.4n",
        (
            ("carrier-a", "node-a"),
            ("carrier-b", "node-b"),
            ("carrier-c", "node-c"),
            ("carrier-d", "node-d"),
        ),
    )
    actual_docks = tuple(
        (
            dock.dock_id,
            dock.dock_map.modality_id,
            dock.dock_map.receptor_geometry_id,
            dock.dock_map.pairs,
        )
        for dock in field.docks
    )
    if actual_docks != (expected_dock,):
        _fail("MODEL_INPUT_PUBLIC_FIELD_INVALID", "dock identity differs")
    return field


def _validate_private_state(
    bundle: FourNodeFreshBundle,
) -> FourNodePrivateFreshState | None:
    role = bundle.model_role
    private = bundle.private_state_or_none
    if role in _STATELESS_MARKERS:
        if (
            private is not None
            or bundle.registered_private_digest_or_none is not None
            or bundle.stateless_marker_or_none != _STATELESS_MARKERS[role]
        ):
            _fail("MODEL_INPUT_ROLE_STATE_INVALID", "stateless role differs")
        return None
    if (
        not isinstance(private, FourNodePrivateFreshState)
        or private.model_role != role
        or bundle.stateless_marker_or_none is not None
        or not isinstance(bundle.registered_private_digest_or_none, str)
        or not _SHA256.fullmatch(bundle.registered_private_digest_or_none)
        or bundle.registered_private_digest_or_none != _PRIVATE_DIGESTS.get(role)
        or not isinstance(private.configuration_binding, str)
        or not private.configuration_binding
    ):
        _fail("MODEL_INPUT_ROLE_STATE_INVALID", "stateful role differs")

    state = private.native_state
    valid = False
    if role == "A2_B1_FIXED_ADAPTER":
        valid = isinstance(state, FourNodeFixedAdapterState)
    elif role == "A2_B2_INTEGRATOR":
        valid = isinstance(state, FourNodeIntegratorState)
    elif role in _SUBSTRATE_ROLES:
        valid = isinstance(state, FourNodeSubstrateFreshState)
    elif role == "A3_NORM":
        valid = isinstance(state, W7NLocalBaselineState) and state.model_id == "norm"
    elif role == "M1_PARALLEL_LEAK":
        valid = isinstance(state, M1ParallelLeakBankState)
    elif role in {"M2_DELAY", "M2_REPLAY"}:
        expected_mode = "DELAY" if role == "M2_DELAY" else "REPLAY"
        valid = isinstance(state, M2BoundedBufferState) and state.mode_id == expected_mode
    elif role == "M4_DTS1_T1":
        valid = (
            isinstance(state, FourNodeM4FreshState)
            and state.candidate_sidecar_digest_or_none is None
        )
    elif role == "M5_DIRECT":
        valid = isinstance(state, W7NLocalBaselineState) and state.model_id == "leak"
    if not valid:
        _fail("MODEL_INPUT_ROLE_STATE_INVALID", "native state type differs")
    return private


def _assembly_payload(
    *,
    model_role: str,
    adapter_surface_id: str,
    public_field: SharedMCMField,
    model_field: SharedMCMField,
    private: FourNodePrivateFreshState | None,
    registered_private_digest: str | None,
    embedding_mode: str,
) -> dict[str, object]:
    substrate_digest = (
        None if model_field.substrate is None else model_field.substrate.digest()
    )
    return {
        "schema_id": "mcm.s1rv.four-node-model-input-assembly.v1",
        "model_role": model_role,
        "adapter_surface_id": adapter_surface_id,
        "field_embedding_mode": embedding_mode,
        "public_field_shell": _field_shell_payload(public_field),
        "model_field_shell": _field_shell_payload(model_field),
        "model_substrate_digest_or_none": substrate_digest,
        "private_state_type_or_none": (
            None if private is None else type(private.native_state).__name__
        ),
        "configuration_binding_or_none": (
            None if private is None else private.configuration_binding
        ),
        "registered_private_digest_or_none": registered_private_digest,
        "registered_edge_inventory_digest_or_none": (
            None if private is None else private.registered_edge_inventory_digest_or_none
        ),
        "native_edge_inventory_digest_or_none": (
            None if private is None else private.native_edge_inventory_digest_or_none
        ),
        "registered_geometry_digest_or_none": (
            None if private is None else private.registered_geometry_digest_or_none
        ),
        "native_geometry_digest_or_none": (
            None if private is None else private.native_geometry_digest_or_none
        ),
    }


@dataclass(frozen=True, slots=True)
class FourNodeModelInputAssembly:
    model_role: str
    adapter_surface_id: str
    public_fresh_field: SharedMCMField
    model_input_field: SharedMCMField
    native_private_state_or_none: object | None
    configuration_binding_or_none: str | None
    registered_private_digest_or_none: str | None
    registered_edge_inventory_digest_or_none: str | None
    native_edge_inventory_digest_or_none: str | None
    registered_geometry_digest_or_none: str | None
    native_geometry_digest_or_none: str | None
    field_embedding_mode: str
    assembly_digest: str

    def __post_init__(self) -> None:
        public = _validate_public_fresh_field(self.public_fresh_field)
        if not isinstance(self.model_input_field, SharedMCMField):
            _fail("MODEL_INPUT_FIELD_INVALID", "model field is invalid")
        if self.model_role not in _ROLE_SURFACES:
            _fail("MODEL_INPUT_ROLE_INVALID", "model role is unknown")
        if self.adapter_surface_id != _ROLE_SURFACES[self.model_role]:
            _fail("MODEL_INPUT_SURFACE_INVALID", "adapter surface differs")
        if _field_shell_payload(public) != _field_shell_payload(self.model_input_field):
            _fail("MODEL_INPUT_FIELD_IDENTITY_MISMATCH", "field shell differs")

        substrate_role = self.model_role in _SUBSTRATE_ROLES
        if substrate_role:
            if (
                self.field_embedding_mode != NATIVE_SUBSTRATE_COPY
                or self.model_input_field is public
                or self.model_input_field.substrate is None
                or not isinstance(self.native_private_state_or_none, FourNodeSubstrateFreshState)
                or self.model_input_field.substrate
                is not self.native_private_state_or_none.substrate
            ):
                _fail("MODEL_INPUT_SUBSTRATE_EMBEDDING_INVALID", "B3-B6 embedding differs")
        elif (
            self.field_embedding_mode != PUBLIC_FIELD_IDENTITY
            or self.model_input_field is not public
            or self.model_input_field.substrate is not None
        ):
            _fail("MODEL_INPUT_FIELD_IDENTITY_MISMATCH", "public field identity differs")
        if self.model_input_field.development is not None:
            _fail("MODEL_INPUT_FIELD_IDENTITY_MISMATCH", "development must remain absent")

        private = None
        if self.native_private_state_or_none is not None:
            if not isinstance(self.configuration_binding_or_none, str) or not self.configuration_binding_or_none:
                _fail("MODEL_INPUT_ROLE_STATE_INVALID", "configuration binding is absent")
            private = FourNodePrivateFreshState(
                model_role=self.model_role,
                configuration_binding=self.configuration_binding_or_none,
                native_state=self.native_private_state_or_none,
                registered_state_payload={},
                registered_edge_inventory_digest_or_none=self.registered_edge_inventory_digest_or_none,
                native_edge_inventory_digest_or_none=self.native_edge_inventory_digest_or_none,
                registered_geometry_digest_or_none=self.registered_geometry_digest_or_none,
                native_geometry_digest_or_none=self.native_geometry_digest_or_none,
            )
        elif self.configuration_binding_or_none is not None:
            _fail("MODEL_INPUT_ROLE_STATE_INVALID", "stateless role has configuration")
        payload = _assembly_payload(
            model_role=self.model_role,
            adapter_surface_id=self.adapter_surface_id,
            public_field=public,
            model_field=self.model_input_field,
            private=private,
            registered_private_digest=self.registered_private_digest_or_none,
            embedding_mode=self.field_embedding_mode,
        )
        if not _SHA256.fullmatch(self.assembly_digest) or self.assembly_digest != _digest(payload):
            _fail("MODEL_INPUT_DIGEST_INVALID", "assembly digest differs")


def assemble_four_node_model_input(
    bundle: FourNodeFreshBundle,
) -> FourNodeModelInputAssembly:
    """Assemble one fresh model input without invoking or advancing a model."""

    if not isinstance(bundle, FourNodeFreshBundle):
        _fail("MODEL_INPUT_BUNDLE_INVALID", "validated fresh bundle required")
    if bundle.model_role not in _ROLE_SURFACES:
        _fail("MODEL_INPUT_ROLE_INVALID", "model role is unknown")
    public = _validate_public_fresh_field(bundle.public_field)
    private = _validate_private_state(bundle)
    if bundle.model_role in _SUBSTRATE_ROLES:
        state = private.native_state
        if not isinstance(state, FourNodeSubstrateFreshState):
            _fail("MODEL_INPUT_SUBSTRATE_EMBEDDING_INVALID", "substrate wrapper required")
        try:
            model_field = replace(public, substrate=state.substrate)
        except (TypeError, ValueError, SharedMCMFieldError) as exc:
            _fail("MODEL_INPUT_SUBSTRATE_EMBEDDING_INVALID", str(exc))
        embedding_mode = NATIVE_SUBSTRATE_COPY
    else:
        model_field = public
        embedding_mode = PUBLIC_FIELD_IDENTITY

    payload = _assembly_payload(
        model_role=bundle.model_role,
        adapter_surface_id=_ROLE_SURFACES[bundle.model_role],
        public_field=public,
        model_field=model_field,
        private=private,
        registered_private_digest=bundle.registered_private_digest_or_none,
        embedding_mode=embedding_mode,
    )
    return FourNodeModelInputAssembly(
        model_role=bundle.model_role,
        adapter_surface_id=_ROLE_SURFACES[bundle.model_role],
        public_fresh_field=public,
        model_input_field=model_field,
        native_private_state_or_none=(None if private is None else private.native_state),
        configuration_binding_or_none=(
            None if private is None else private.configuration_binding
        ),
        registered_private_digest_or_none=bundle.registered_private_digest_or_none,
        registered_edge_inventory_digest_or_none=(
            None if private is None else private.registered_edge_inventory_digest_or_none
        ),
        native_edge_inventory_digest_or_none=(
            None if private is None else private.native_edge_inventory_digest_or_none
        ),
        registered_geometry_digest_or_none=(
            None if private is None else private.registered_geometry_digest_or_none
        ),
        native_geometry_digest_or_none=(
            None if private is None else private.native_geometry_digest_or_none
        ),
        field_embedding_mode=embedding_mode,
        assembly_digest=_digest(payload),
    )
