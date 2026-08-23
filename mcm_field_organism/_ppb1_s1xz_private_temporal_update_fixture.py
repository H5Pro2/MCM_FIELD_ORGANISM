"""Private immutable S1-XZ fixture for bounded PPB-1 temporal updates."""

from __future__ import annotations

from dataclasses import dataclass
import math

from ._ppb1_reference import _digest, normalized_mean_l1_distance


S1XZ_SCHEMA_VERSION = "ppb1.s1xz.private-temporal-update-fixture.v1"
S1XZ_PREFLIGHT_DIGEST = (
    "1bf316628b75ca6ee11fb05f290713b30b758c7a35b9cb9ede19b3142c577d06"
)
S1XZ_INVALID_FIXTURE = "S1XZ_INVALID_TEMPORAL_UPDATE_FIXTURE"

S1XZ_MODALITY_ORDER = ("auditory", "visual")
S1XZ_HISTORY_ORDER = ("H1", "H2", "H3", "H4", "H5")
S1XZ_VALUE_ROLES = (
    "origin",
    "gradual_1",
    "gradual_2",
    "gradual_3",
    "conflict_b",
    "opposite_c",
    "far_control",
)

_CONFIG = {
    "capacity": 2,
    "update_rate": 0.5,
    "stable_after": 3,
    "expire_after_steps": 8,
}
_MODALITY_SPECS = {
    "auditory": {
        "carrier_count": 12,
        "match_threshold": 0.25,
        "values": (0.0, 0.0625, 0.125, 0.1875, 0.625, -0.625, 1.0),
        "h1_terminal": 0.09375,
        "h2_h5_terminal": 0.1328125,
    },
    "visual": {
        "carrier_count": 72,
        "match_threshold": 0.125,
        "values": (0.0, 0.03125, 0.0625, 0.09375, 0.5, -0.5, 1.0),
        "h1_terminal": 0.046875,
        "h2_h5_terminal": 0.06640625,
    },
}
_HISTORY_ROLES = {
    "H1": {
        "formation": ("origin", "origin", "origin"),
        "update": ("gradual_2", "gradual_2"),
        "probes": ("gradual_2", "conflict_b"),
        "policy": "CONTINUE_SLOT_000_NO_SECOND_SLOT",
        "events": ("CREATED", "MATCHED", "MATCHED", "MATCHED", "MATCHED"),
        "separation_ticks": 4,
    },
    "H2": {
        "formation": ("origin", "origin", "origin"),
        "update": ("gradual_1", "gradual_2", "gradual_3"),
        "probes": ("origin", "gradual_2", "gradual_3", "conflict_b"),
        "policy": "CONTINUE_SLOT_000_THREE_TIMES",
        "events": (
            "CREATED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
        ),
        "separation_ticks": 4,
    },
    "H3": {
        "formation": ("origin", "origin", "origin"),
        "update": ("conflict_b", "conflict_b", "conflict_b"),
        "probes": ("origin", "conflict_b", "opposite_c"),
        "policy": "SEPARATE_ONLY",
        "events": (
            "CREATED",
            "MATCHED",
            "MATCHED",
            "CREATED",
            "MATCHED",
            "MATCHED",
        ),
        "separation_ticks": 4,
    },
    "H4": {
        "formation": (
            "origin",
            "origin",
            "origin",
            "conflict_b",
            "conflict_b",
            "conflict_b",
        ),
        "update": ("opposite_c", "opposite_c", "opposite_c"),
        "probes": ("conflict_b", "origin", "opposite_c", "far_control"),
        "policy": "DETERMINISTIC_LRU_REPLACEMENT_SLOT_000",
        "events": (
            "CREATED",
            "MATCHED",
            "MATCHED",
            "CREATED",
            "MATCHED",
            "MATCHED",
            "REPLACED",
            "MATCHED",
            "MATCHED",
        ),
        "separation_ticks": 4,
    },
    "H5": {
        "formation": ("origin", "origin", "origin"),
        "update": ("gradual_1", "gradual_2", "gradual_3"),
        "probes": ("gradual_3", "origin", "conflict_b"),
        "policy": "READ_ONLY_AFTER_FOUR_TICK_SEPARATION",
        "events": (
            "CREATED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
            "MATCHED",
        ),
        "separation_ticks": 4,
    },
}


class S1XZTemporalUpdateFixtureError(ValueError):
    """One fail-closed S1-XZ fixture violation."""

    def __init__(self, detail: str) -> None:
        self.code = S1XZ_INVALID_FIXTURE
        self.detail = detail
        super().__init__(f"{self.code}: {detail}")


def _payload_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1XZ_SCHEMA_VERSION,
            "preflight_digest": S1XZ_PREFLIGHT_DIGEST,
            **payload,
        }
    )


def _named_values(modality_id: str) -> tuple[tuple[str, float], ...]:
    spec = _MODALITY_SPECS[modality_id]
    return tuple(zip(S1XZ_VALUE_ROLES, spec["values"], strict=True))


def _value_map(modality: S1XZModalityFixture) -> dict[str, float]:
    return dict(modality.named_scalar_values)


def _distance(value: float, prototypes: tuple[float, ...], count: int) -> float:
    return min(
        normalized_mean_l1_distance(
            (value,) * count,
            (prototype,) * count,
        )
        for prototype in prototypes
    )


@dataclass(frozen=True, slots=True)
class S1XZModalityFixture:
    modality_id: str
    carrier_count: int
    match_threshold: float
    capacity: int
    update_rate: float
    stable_after: int
    expire_after_steps: int
    named_scalar_values: tuple[tuple[str, float], ...]
    h1_terminal_candidate_prototype: float
    h2_h5_terminal_candidate_prototype: float
    modality_fixture_digest: str

    def __post_init__(self) -> None:
        spec = _MODALITY_SPECS.get(self.modality_id)
        values = tuple(self.named_scalar_values)
        if (
            spec is None
            or self.carrier_count != spec["carrier_count"]
            or self.match_threshold != spec["match_threshold"]
            or self.capacity != _CONFIG["capacity"]
            or self.update_rate != _CONFIG["update_rate"]
            or self.stable_after != _CONFIG["stable_after"]
            or self.expire_after_steps != _CONFIG["expire_after_steps"]
            or values != _named_values(self.modality_id)
            or self.h1_terminal_candidate_prototype != spec["h1_terminal"]
            or self.h2_h5_terminal_candidate_prototype != spec["h2_h5_terminal"]
            or any(not math.isfinite(value) or abs(value) > 1.0 for _, value in values)
            or self.modality_fixture_digest
            != _payload_digest(self.payload_without_digest())
        ):
            raise S1XZTemporalUpdateFixtureError("invalid modality fixture")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "carrier_count": self.carrier_count,
            "match_threshold": self.match_threshold,
            "capacity": self.capacity,
            "update_rate": self.update_rate,
            "stable_after": self.stable_after,
            "expire_after_steps": self.expire_after_steps,
            "named_scalar_values": [list(item) for item in self.named_scalar_values],
            "h1_terminal_candidate_prototype": self.h1_terminal_candidate_prototype,
            "h2_h5_terminal_candidate_prototype": (
                self.h2_h5_terminal_candidate_prototype
            ),
        }


@dataclass(frozen=True, slots=True)
class S1XZHistoryPlan:
    plan_id: str
    modality_id: str
    history_id: str
    formation_roles: tuple[str, ...]
    update_roles: tuple[str, ...]
    ordered_probe_roles: tuple[str, ...]
    target_policy: str
    expected_candidate_prototypes: tuple[float, ...]
    expected_baseline_prototypes: tuple[float, ...]
    expected_candidate_probe_distances: tuple[float, ...]
    expected_baseline_probe_distances: tuple[float, ...]
    expected_candidate_recognition: tuple[bool, ...]
    expected_baseline_recognition: tuple[bool, ...]
    expected_candidate_events: tuple[str, ...]
    separation_ticks: int
    plan_digest: str

    def __post_init__(self) -> None:
        if self.modality_id not in S1XZ_MODALITY_ORDER or self.history_id not in S1XZ_HISTORY_ORDER:
            raise S1XZTemporalUpdateFixtureError("invalid history identity")
        expected = _expected_history_payload(
            _build_modality_fixture(self.modality_id),
            self.history_id,
        )
        if (
            self.plan_id != f"s1xz.{self.modality_id}.{self.history_id.lower()}"
            or self.payload_without_digest() != expected
            or self.plan_digest != _payload_digest(expected)
        ):
            raise S1XZTemporalUpdateFixtureError("invalid history plan")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "modality_id": self.modality_id,
            "history_id": self.history_id,
            "formation_roles": list(self.formation_roles),
            "update_roles": list(self.update_roles),
            "ordered_probe_roles": list(self.ordered_probe_roles),
            "target_policy": self.target_policy,
            "expected_candidate_prototypes": list(self.expected_candidate_prototypes),
            "expected_baseline_prototypes": list(self.expected_baseline_prototypes),
            "expected_candidate_probe_distances": list(
                self.expected_candidate_probe_distances
            ),
            "expected_baseline_probe_distances": list(
                self.expected_baseline_probe_distances
            ),
            "expected_candidate_recognition": list(
                self.expected_candidate_recognition
            ),
            "expected_baseline_recognition": list(
                self.expected_baseline_recognition
            ),
            "expected_candidate_events": list(self.expected_candidate_events),
            "separation_ticks": self.separation_ticks,
        }


@dataclass(frozen=True, slots=True)
class S1XZTemporalUpdateFixtureBundle:
    modalities: tuple[S1XZModalityFixture, ...]
    history_plans: tuple[S1XZHistoryPlan, ...]
    total_candidate_exposures: int
    total_baseline_formation_exposures: int
    total_baseline_frozen_handoffs: int
    total_paired_probes: int
    retry_count: int
    bundle_digest: str

    def __post_init__(self) -> None:
        expected_order = tuple(
            (modality, history)
            for modality in S1XZ_MODALITY_ORDER
            for history in S1XZ_HISTORY_ORDER
        )
        if (
            tuple(item.modality_id for item in self.modalities) != S1XZ_MODALITY_ORDER
            or tuple((item.modality_id, item.history_id) for item in self.history_plans)
            != expected_order
            or self.total_candidate_exposures != 64
            or self.total_baseline_formation_exposures != 36
            or self.total_baseline_frozen_handoffs != 28
            or self.total_paired_probes != 32
            or self.retry_count != 0
            or self.bundle_digest != _payload_digest(self.payload_without_digest())
        ):
            raise S1XZTemporalUpdateFixtureError("invalid fixture bundle")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "modality_fixture_digests": [
                item.modality_fixture_digest for item in self.modalities
            ],
            "history_plan_digests": [item.plan_digest for item in self.history_plans],
            "total_candidate_exposures": self.total_candidate_exposures,
            "total_baseline_formation_exposures": (
                self.total_baseline_formation_exposures
            ),
            "total_baseline_frozen_handoffs": self.total_baseline_frozen_handoffs,
            "total_paired_probes": self.total_paired_probes,
            "retry_count": self.retry_count,
        }


def _build_modality_fixture(modality_id: str) -> S1XZModalityFixture:
    spec = _MODALITY_SPECS[modality_id]
    values = {
        "modality_id": modality_id,
        "carrier_count": spec["carrier_count"],
        "match_threshold": spec["match_threshold"],
        "capacity": _CONFIG["capacity"],
        "update_rate": _CONFIG["update_rate"],
        "stable_after": _CONFIG["stable_after"],
        "expire_after_steps": _CONFIG["expire_after_steps"],
        "named_scalar_values": _named_values(modality_id),
        "h1_terminal_candidate_prototype": spec["h1_terminal"],
        "h2_h5_terminal_candidate_prototype": spec["h2_h5_terminal"],
    }
    return S1XZModalityFixture(
        **values,
        modality_fixture_digest=_payload_digest(
            {
                **values,
                "named_scalar_values": [list(item) for item in values["named_scalar_values"]],
            }
        ),
    )


def _expected_prototypes(
    modality: S1XZModalityFixture,
    history_id: str,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    values = _value_map(modality)
    if history_id == "H1":
        return (modality.h1_terminal_candidate_prototype,), (values["origin"],)
    if history_id in {"H2", "H5"}:
        return (modality.h2_h5_terminal_candidate_prototype,), (values["origin"],)
    if history_id == "H3":
        return (values["origin"], values["conflict_b"]), (values["origin"],)
    return (
        (values["opposite_c"], values["conflict_b"]),
        (values["origin"], values["conflict_b"]),
    )


def _expected_history_payload(
    modality: S1XZModalityFixture,
    history_id: str,
) -> dict[str, object]:
    roles = _HISTORY_ROLES[history_id]
    values = _value_map(modality)
    candidate_prototypes, baseline_prototypes = _expected_prototypes(
        modality, history_id
    )
    probes = tuple(roles["probes"])
    candidate_distances = tuple(
        _distance(values[role], candidate_prototypes, modality.carrier_count)
        for role in probes
    )
    baseline_distances = tuple(
        _distance(values[role], baseline_prototypes, modality.carrier_count)
        for role in probes
    )
    return {
        "plan_id": f"s1xz.{modality.modality_id}.{history_id.lower()}",
        "modality_id": modality.modality_id,
        "history_id": history_id,
        "formation_roles": list(roles["formation"]),
        "update_roles": list(roles["update"]),
        "ordered_probe_roles": list(probes),
        "target_policy": roles["policy"],
        "expected_candidate_prototypes": list(candidate_prototypes),
        "expected_baseline_prototypes": list(baseline_prototypes),
        "expected_candidate_probe_distances": list(candidate_distances),
        "expected_baseline_probe_distances": list(baseline_distances),
        "expected_candidate_recognition": [
            distance <= modality.match_threshold for distance in candidate_distances
        ],
        "expected_baseline_recognition": [
            distance <= modality.match_threshold for distance in baseline_distances
        ],
        "expected_candidate_events": list(roles["events"]),
        "separation_ticks": roles["separation_ticks"],
    }


def _build_history_plan(
    modality: S1XZModalityFixture,
    history_id: str,
) -> S1XZHistoryPlan:
    payload = _expected_history_payload(modality, history_id)
    return S1XZHistoryPlan(
        plan_id=payload["plan_id"],
        modality_id=payload["modality_id"],
        history_id=payload["history_id"],
        formation_roles=tuple(payload["formation_roles"]),
        update_roles=tuple(payload["update_roles"]),
        ordered_probe_roles=tuple(payload["ordered_probe_roles"]),
        target_policy=payload["target_policy"],
        expected_candidate_prototypes=tuple(
            payload["expected_candidate_prototypes"]
        ),
        expected_baseline_prototypes=tuple(payload["expected_baseline_prototypes"]),
        expected_candidate_probe_distances=tuple(
            payload["expected_candidate_probe_distances"]
        ),
        expected_baseline_probe_distances=tuple(
            payload["expected_baseline_probe_distances"]
        ),
        expected_candidate_recognition=tuple(
            payload["expected_candidate_recognition"]
        ),
        expected_baseline_recognition=tuple(
            payload["expected_baseline_recognition"]
        ),
        expected_candidate_events=tuple(payload["expected_candidate_events"]),
        separation_ticks=payload["separation_ticks"],
        plan_digest=_payload_digest(payload),
    )


def build_s1xz_temporal_update_fixture() -> S1XZTemporalUpdateFixtureBundle:
    """Build only the immutable synthetic fixture; execute no PPB-1 state."""

    modalities = tuple(_build_modality_fixture(item) for item in S1XZ_MODALITY_ORDER)
    plans = tuple(
        _build_history_plan(modality, history_id)
        for modality in modalities
        for history_id in S1XZ_HISTORY_ORDER
    )
    values = {
        "modalities": modalities,
        "history_plans": plans,
        "total_candidate_exposures": 64,
        "total_baseline_formation_exposures": 36,
        "total_baseline_frozen_handoffs": 28,
        "total_paired_probes": 32,
        "retry_count": 0,
    }
    payload = {
        "modality_fixture_digests": [
            item.modality_fixture_digest for item in modalities
        ],
        "history_plan_digests": [item.plan_digest for item in plans],
        "total_candidate_exposures": values["total_candidate_exposures"],
        "total_baseline_formation_exposures": values[
            "total_baseline_formation_exposures"
        ],
        "total_baseline_frozen_handoffs": values[
            "total_baseline_frozen_handoffs"
        ],
        "total_paired_probes": values["total_paired_probes"],
        "retry_count": values["retry_count"],
    }
    return S1XZTemporalUpdateFixtureBundle(
        **values,
        bundle_digest=_payload_digest(payload),
    )
