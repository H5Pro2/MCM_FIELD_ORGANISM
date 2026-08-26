"""S1-EC96 authorized exactly-once in-memory r4/r8 coordinator."""

from __future__ import annotations

from collections.abc import Callable
import ctypes
from dataclasses import dataclass, field
import math
from pathlib import Path
import shutil

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
    E1CommonProbeEC89RefinementObjectHandoff,
)
from .e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91FormationReceipt,
    E1CommonProbeEC91ProbeReceipt,
)
from .e1_common_probe_ec93_r4_r8_real_adapter_preflight import (
    build_e1_common_probe_ec93_fresh_field_adapter,
    run_e1_common_probe_ec93_formation_receipt_adapter,
    run_e1_common_probe_ec93_probe_receipt_adapter,
)
from .e1_common_probe_ec94_final_resource_identity_gate import (
    E1CommonProbeEC94FinalResourceIdentityGate,
)
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_common_probe_r2_ec80_scalar_contract import S1_EC80_CONTRAST_ROLE_PAIRS
from .e1_common_probe_real_binding_contract import E1CommonProbeRealSlotBinding
from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeResolvedSlot,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)
from .shared_mcm_field import SharedMCMField


class E1CommonProbeEC96AuthorizedOnceError(RuntimeError):
    """Raised when EC96 cannot start or complete its single authorized call."""


S1_EC96_AUTHORIZATION_TEXT = (
    "Ich gebe genau einen gemeinsam gebundenen, nicht persistenten r4/r8-Lauf "
    "mit maximal 19.248 Feldschritten frei. Kein Retry und keine "
    "Nachparametrierung. Die Ausfuehrung darf nur starten, wenn die Ressourcen "
    "unmittelbar vor dem ersten Adapteraufruf erneut oberhalb der gebundenen "
    "Mindestgrenzen liegen; sonst fail-closed ohne Teilstart."
)
S1_EC96_RESULT_ID = "e1.common-probe-authorized-r4-r8-once.s1ec96.v1"
S1_EC96_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC96_EC95_GATE_DIGEST = (
    "bc608b5ca68c48757ba99070e0faf763197f970564a181ae1ff7517178a7152c"
)


class E1CommonProbeEC96AuthorizationToken:
    """One-process token consumed immediately before the first adapter call."""

    __slots__ = ("authorization_digest", "source_gate_digest", "_consumed")

    def __init__(self, authorization_text: str, source_gate_digest: str) -> None:
        if authorization_text != S1_EC96_AUTHORIZATION_TEXT:
            raise E1CommonProbeEC96AuthorizedOnceError(
                "S1-EC96 requires the exact explicit owner authorization"
            )
        self.authorization_digest = _digest(authorization_text)
        self.source_gate_digest = source_gate_digest
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def consume(self) -> None:
        if self._consumed:
            raise E1CommonProbeEC96AuthorizedOnceError(
                "S1-EC96 authorization was already consumed; retry forbidden"
            )
        self._consumed = True


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def read_e1_common_probe_ec96_resources() -> E1PilotRealResourceSnapshot:
    """Read Windows memory and current-drive capacity without field activity."""

    status = _MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    try:
        succeeded = ctypes.windll.kernel32.GlobalMemoryStatusEx(  # type: ignore[attr-defined]
            ctypes.byref(status)
        )
    except (AttributeError, OSError) as exc:
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 cannot read the immediate Windows memory snapshot"
        ) from exc
    if not succeeded:
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 immediate Windows memory snapshot failed"
        )
    anchor = Path.cwd().anchor or str(Path.cwd())
    return E1PilotRealResourceSnapshot(
        int(status.available_physical), int(shutil.disk_usage(anchor).free)
    )


FormationAdapter = Callable[
    [
        E1CommonProbeEC89RefinementObjectHandoff,
        E1CommonProbeResolvedSlot,
        SharedMCMField,
        E1LocalEdgePlasticityState,
    ],
    E1CommonProbeEC91FormationReceipt,
]
FreshFieldAdapter = Callable[
    [E1CommonProbeRealSlotBinding, SharedMCMField], E1CommonProbeFreshField
]
ProbeAdapter = Callable[
    [
        E1CommonProbeEC89RefinementObjectHandoff,
        E1CommonProbeResolvedSlot,
        E1CommonProbeFreshField,
        E1CommonProbeEC91FormationReceipt | None,
    ],
    E1CommonProbeEC91ProbeReceipt,
]
ResourceReader = Callable[[], E1PilotRealResourceSnapshot]


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or len(left) != len(right):
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 scalar vectors changed"
        )
    value = max(abs(a - b) for a, b in zip(left, right, strict=True))
    if not math.isfinite(value):
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 scalar result is not finite"
        )
    return value


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC96RefinementResult:
    refinement_id: str
    handoff_digest: str
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    contrast_scalars: tuple[tuple[str, float, float], ...]
    formation_steps: int
    probe_steps: int
    total_steps: int
    all_routes_exact: bool
    all_fresh_fields_identical_and_object_separate: bool
    result_digest: str
    formations: tuple[E1CommonProbeEC91FormationReceipt, ...] = field(
        repr=False, compare=False
    )
    probes: tuple[E1CommonProbeEC91ProbeReceipt, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        expected = {"r4": (3216, 3200, 6416), "r8": (6432, 6400, 12832)}.get(
            self.refinement_id
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "formations", "probes"}
        }
        if (
            expected is None
            or len(self.formations) != 4
            or len(self.probes) != 8
            or self.formation_receipt_digests
            != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests
            != tuple(item.receipt_digest for item in self.probes)
            or tuple(item[0] for item in self.contrast_scalars)
            != tuple(item[0] for item in S1_EC80_CONTRAST_ROLE_PAIRS)
            or any(
                not math.isfinite(value) or value < 0.0
                for _, activation, afterimage in self.contrast_scalars
                for value in (activation, afterimage)
            )
            or (self.formation_steps, self.probe_steps, self.total_steps) != expected
            or self.all_routes_exact is not True
            or self.all_fresh_fields_identical_and_object_separate is not True
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC96AuthorizedOnceError(
                "S1-EC96 refinement result changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC96AtomicResult:
    result_id: str
    source_handoff_set_digest: str
    source_gate_digest: str
    authorization_digest: str
    immediate_resource_digest: str
    immediate_free_memory_bytes: int
    immediate_free_disk_bytes: int
    refinement_ids: tuple[str, ...]
    refinement_result_digests: tuple[str, ...]
    total_field_steps: int
    resource_gate_passed_before_first_adapter: bool
    authorization_consumed: bool
    exactly_once_completed: bool
    atomic_scalar_return: bool
    persistence_performed: bool
    retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    result_digest: str
    refinements: tuple[E1CommonProbeEC96RefinementResult, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "refinements"}
        }
        if (
            self.result_id != S1_EC96_RESULT_ID
            or self.source_handoff_set_digest != S1_EC96_EC89_RESULT_DIGEST
            or self.refinement_ids != ("r4", "r8")
            or self.refinement_result_digests
            != tuple(item.result_digest for item in self.refinements)
            or self.total_field_steps != 19248
            or any(
                value is not True
                for value in (
                    self.resource_gate_passed_before_first_adapter,
                    self.authorization_consumed,
                    self.exactly_once_completed,
                    self.atomic_scalar_return,
                )
            )
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC96AuthorizedOnceError(
                "S1-EC96 atomic result changed or is incomplete"
            )


def run_e1_common_probe_ec96_authorized_r4_r8_once(
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
    gate: E1CommonProbeEC94FinalResourceIdentityGate,
    authorization: E1CommonProbeEC96AuthorizationToken,
    *,
    resource_reader: ResourceReader = read_e1_common_probe_ec96_resources,
    formation_adapter: FormationAdapter = run_e1_common_probe_ec93_formation_receipt_adapter,
    fresh_field_adapter: FreshFieldAdapter = build_e1_common_probe_ec93_fresh_field_adapter,
    probe_adapter: ProbeAdapter = run_e1_common_probe_ec93_probe_receipt_adapter,
) -> E1CommonProbeEC96AtomicResult:
    """Run both refinements once and return only one complete in-memory result."""

    if (
        not isinstance(handoffs, E1CommonProbeEC89R4R8ObjectHandoffSet)
        or handoffs.result_digest != S1_EC96_EC89_RESULT_DIGEST
        or not isinstance(gate, E1CommonProbeEC94FinalResourceIdentityGate)
        or not gate.technical_execution_ready
        or gate.owner_execution_authorized
        or not isinstance(authorization, E1CommonProbeEC96AuthorizationToken)
        or authorization.source_gate_digest != gate.gate_digest
        or authorization.consumed
        or not all(
            callable(item)
            for item in (
                resource_reader,
                formation_adapter,
                fresh_field_adapter,
                probe_adapter,
            )
        )
    ):
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 closed inputs or authorization changed"
        )
    handoffs.__post_init__()
    gate.__post_init__()
    resources = resource_reader()
    resources.__post_init__()
    if (
        resources.free_memory_bytes < S1_EC29_MIN_FREE_MEMORY_BYTES
        or resources.free_disk_bytes < S1_EC29_MIN_FREE_DISK_BYTES
    ):
        raise E1CommonProbeEC96AuthorizedOnceError(
            "S1-EC96 resource gate failed before first adapter; zero-step abort"
        )

    authorization.consume()
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    refinement_results = []
    for handoff in handoffs.handoffs:
        formations = tuple(
            formation_adapter(
                handoff, slot, handoff.initial_field, handoff.initial_state
            )
            for slot in handoff.formation_slots
        )
        if any(
            item.execution_mode != "real-wrapper"
            or item.refinement_id != handoff.refinement_id
            or item.state_role != slot.binding.state_role
            for item, slot in zip(formations, handoff.formation_slots, strict=True)
        ):
            raise E1CommonProbeEC96AuthorizedOnceError(
                "S1-EC96 formation route or mode changed; retry forbidden"
            )
        states = {item.state_role: item for item in formations}
        fresh_fields = []
        probes = []
        for slot in handoff.resolved_slots:
            fresh = fresh_field_adapter(slot.binding, handoff.initial_field)
            state_role = routes[slot.binding.role_id]
            formation = None if state_role is None else states[state_role]
            probe = probe_adapter(handoff, slot, fresh, formation)
            expected_state = None if formation is None else formation.output_state_digest
            if (
                probe.execution_mode != "real-wrapper"
                or probe.refinement_id != handoff.refinement_id
                or probe.role_id != slot.binding.role_id
                or probe.selected_state_role != state_role
                or probe.selected_state_digest != expected_state
                or probe.backreaction_enabled is not slot.binding.backreaction_enabled
            ):
                raise E1CommonProbeEC96AuthorizedOnceError(
                    "S1-EC96 probe route or mode changed; retry forbidden"
                )
            fresh_fields.append(fresh)
            probes.append(probe)
        probe_tuple = tuple(probes)
        by_role = {item.role_id: item for item in probe_tuple}
        scalars = tuple(
            (
                name,
                _linf(by_role[left].activation, by_role[right].activation),
                _linf(by_role[left].afterimage, by_role[right].afterimage),
            )
            for name, left, right in S1_EC80_CONTRAST_ROLE_PAIRS
        )
        formation_steps = sum(item.accounted_field_steps for item in formations)
        probe_steps = sum(item.accounted_field_steps for item in probe_tuple)
        refinement_values = {
            "refinement_id": handoff.refinement_id,
            "handoff_digest": handoff.handoff_digest,
            "formation_receipt_digests": tuple(
                item.receipt_digest for item in formations
            ),
            "probe_receipt_digests": tuple(item.receipt_digest for item in probe_tuple),
            "contrast_scalars": scalars,
            "formation_steps": formation_steps,
            "probe_steps": probe_steps,
            "total_steps": formation_steps + probe_steps,
            "all_routes_exact": len(by_role) == 8,
            "all_fresh_fields_identical_and_object_separate": (
                len({id(item.field) for item in fresh_fields}) == 8
                and all(
                    item.field is not handoff.initial_field
                    and _initial_field_digest(item.field) == handoff.initial_field_digest
                    for item in fresh_fields
                )
            ),
        }
        refinement_results.append(
            E1CommonProbeEC96RefinementResult(
                **refinement_values,
                result_digest=_digest(refinement_values),
                formations=formations,
                probes=probe_tuple,
            )
        )
    refinements = tuple(refinement_results)
    values = {
        "result_id": S1_EC96_RESULT_ID,
        "source_handoff_set_digest": handoffs.result_digest,
        "source_gate_digest": gate.gate_digest,
        "authorization_digest": authorization.authorization_digest,
        "immediate_resource_digest": resources.digest(),
        "immediate_free_memory_bytes": resources.free_memory_bytes,
        "immediate_free_disk_bytes": resources.free_disk_bytes,
        "refinement_ids": tuple(item.refinement_id for item in refinements),
        "refinement_result_digests": tuple(item.result_digest for item in refinements),
        "total_field_steps": sum(item.total_steps for item in refinements),
        "resource_gate_passed_before_first_adapter": True,
        "authorization_consumed": authorization.consumed,
        "exactly_once_completed": True,
        "atomic_scalar_return": len(refinements) == 2,
        "persistence_performed": False,
        "retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC96AtomicResult(
        **values, result_digest=_digest(values), refinements=refinements
    )
