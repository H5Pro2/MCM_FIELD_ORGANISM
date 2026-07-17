"""Passive Methodik-029 baselines for history-sensitive reentry."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from typing import Callable, Iterable

from .carrier_baselines import run_independent_history, stateless_baseline


class HistorySensitiveReentryProbeError(ValueError):
    """Raised when the preregistered reentry probe is changed or invalid."""


REENTRY_AMPLITUDES = (0.25, 0.5, 1.0)
REENTRY_TAUS = (1.0, 2.0, 4.0)
REENTRY_TRAJECTORY_IDS = ("a", "b", "c", "d")
REENTRY_PAIR_IDS = ("a-d", "b-c")
REENTRY_POSITIONS = {
    "a": (0, 1, 2, None, 3),
    "b": (4, 3, 2, None, 1),
    "c": (0, 1, 2, None, 1),
    "d": (4, 3, 2, None, 3),
}

ReentryObserver = Callable[["HistorySensitiveReentryObservation"], object]


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _contact(position: int | None, amplitude: float) -> tuple[float, ...]:
    return tuple(
        amplitude if position is not None and index == position else 0.0
        for index in range(5)
    )


def _contacts(
    trajectory_id: str,
    amplitude: float,
) -> tuple[tuple[float, ...], ...]:
    return tuple(
        _contact(position, amplitude)
        for position in REENTRY_POSITIONS[trajectory_id]
    )


def _fixed_recurrence(
    contacts: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    state = (0.0,) * 5
    for contact in contacts:
        state = tuple(
            (0.5 * previous) + current
            for previous, current in zip(state, contact, strict=True)
        )
    return state


def _diffuse_once(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        (
            (values[index - 1] if index > 0 else 0.0)
            + (2.0 * values[index])
            + (values[index + 1] if index < len(values) - 1 else 0.0)
        )
        / 4.0
        for index in range(len(values))
    )


def _asymmetry(
    values: tuple[float, ...],
    position: int,
) -> float:
    right = values[position + 1] if position < len(values) - 1 else 0.0
    left = values[position - 1] if position > 0 else 0.0
    return right - left


def _l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(
        abs(left_value - right_value)
        for left_value, right_value in zip(left, right, strict=True)
    )


@dataclass(frozen=True, slots=True)
class HistorySensitiveReentryObservation:
    amplitude: float
    tau: float
    trajectory_id: str
    current_position: int
    contact_history_digest: str
    current_contact: tuple[float, ...]
    previous_contact: tuple[float, ...]
    pre_reentry_afterimage: tuple[float, ...]
    b0_projection: tuple[float, ...]
    b1_afterimage: tuple[float, ...]
    b2_one_step_buffer: tuple[float, ...]
    b3_fixed_recurrence: tuple[float, ...]
    b4_single_diffusion: tuple[float, ...]
    b5_direct_asymmetry: float

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class HistorySensitiveReentryPair:
    amplitude: float
    tau: float
    pair_id: str
    current_contacts_equal: bool
    prior_histories_distinct: bool
    b0_distance: float
    b1_distance: float
    b2_distance: float
    b3_distance: float
    b4_distance: float
    b5_distance: float

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class HistorySensitiveReentryResult:
    observations: tuple[HistorySensitiveReentryObservation, ...]
    pairs: tuple[HistorySensitiveReentryPair, ...]
    all_current_pairs_equal: bool
    all_prior_histories_distinct: bool
    all_trajectory_mirrors_exact: bool
    all_resets_neutral: bool
    b0_collides_all_pairs: bool
    b1_separates_all_pairs: bool
    b2_collides_all_pairs: bool
    b3_separates_all_pairs: bool
    b4_separates_all_pairs: bool
    b5_separates_all_pairs: bool
    b1_covers_required_pair_distinction: bool
    unexplained_function_rest: bool
    writes_back: bool = False
    mechanism_released: bool = False

    def __post_init__(self) -> None:
        if self.writes_back or self.mechanism_released:
            raise HistorySensitiveReentryProbeError(
                "a passive reentry result cannot write back or release a mechanism"
            )
        if len(self.observations) != 36 or len(self.pairs) != 18:
            raise HistorySensitiveReentryProbeError(
                "result must contain every preregistered observation and pair"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "observations": [
                observation.canonical_payload()
                for observation in self.observations
            ],
            "pairs": [pair.canonical_payload() for pair in self.pairs],
            "all_current_pairs_equal": self.all_current_pairs_equal,
            "all_prior_histories_distinct": self.all_prior_histories_distinct,
            "all_trajectory_mirrors_exact": self.all_trajectory_mirrors_exact,
            "all_resets_neutral": self.all_resets_neutral,
            "b0_collides_all_pairs": self.b0_collides_all_pairs,
            "b1_separates_all_pairs": self.b1_separates_all_pairs,
            "b2_collides_all_pairs": self.b2_collides_all_pairs,
            "b3_separates_all_pairs": self.b3_separates_all_pairs,
            "b4_separates_all_pairs": self.b4_separates_all_pairs,
            "b5_separates_all_pairs": self.b5_separates_all_pairs,
            "b1_covers_required_pair_distinction": (
                self.b1_covers_required_pair_distinction
            ),
            "unexplained_function_rest": self.unexplained_function_rest,
            "writes_back": self.writes_back,
            "mechanism_released": self.mechanism_released,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _validated_order(
    values: Iterable[object],
    expected: tuple[object, ...],
    role: str,
) -> tuple[object, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise HistorySensitiveReentryProbeError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _observe(
    *,
    amplitude: float,
    tau: float,
    trajectory_id: str,
) -> HistorySensitiveReentryObservation:
    contacts = _contacts(trajectory_id, amplitude)
    frames = run_independent_history(contacts, dt=1.0, tau=tau)
    current_position = REENTRY_POSITIONS[trajectory_id][-1]
    if current_position is None:
        raise HistorySensitiveReentryProbeError(
            "a reentry trajectory must end in a contact"
        )
    b0 = stateless_baseline(contacts[-1]).activation
    b1 = frames[-1].afterimage
    return HistorySensitiveReentryObservation(
        amplitude=amplitude,
        tau=tau,
        trajectory_id=trajectory_id,
        current_position=current_position,
        contact_history_digest=_digest(contacts),
        current_contact=contacts[-1],
        previous_contact=contacts[-2],
        pre_reentry_afterimage=frames[-2].afterimage,
        b0_projection=b0,
        b1_afterimage=b1,
        b2_one_step_buffer=contacts[-1] + contacts[-2],
        b3_fixed_recurrence=_fixed_recurrence(contacts),
        b4_single_diffusion=_diffuse_once(b1),
        b5_direct_asymmetry=_asymmetry(
            frames[-2].afterimage,
            current_position,
        ),
    )


def _pair(
    left: HistorySensitiveReentryObservation,
    right: HistorySensitiveReentryObservation,
    pair_id: str,
) -> HistorySensitiveReentryPair:
    return HistorySensitiveReentryPair(
        amplitude=left.amplitude,
        tau=left.tau,
        pair_id=pair_id,
        current_contacts_equal=left.current_contact == right.current_contact,
        prior_histories_distinct=(
            left.contact_history_digest != right.contact_history_digest
        ),
        b0_distance=_l1(left.b0_projection, right.b0_projection),
        b1_distance=_l1(left.b1_afterimage, right.b1_afterimage),
        b2_distance=_l1(
            left.b2_one_step_buffer,
            right.b2_one_step_buffer,
        ),
        b3_distance=_l1(
            left.b3_fixed_recurrence,
            right.b3_fixed_recurrence,
        ),
        b4_distance=_l1(
            left.b4_single_diffusion,
            right.b4_single_diffusion,
        ),
        b5_distance=abs(
            left.b5_direct_asymmetry - right.b5_direct_asymmetry
        ),
    )


def _reset_is_neutral(amplitude: float, tau: float) -> bool:
    del amplitude
    contacts = ((0.0,) * 5,) * 5
    frames = run_independent_history(contacts, dt=1.0, tau=tau)
    b0 = stateless_baseline(contacts[-1]).activation
    return (
        b0 == (0.0,) * 5
        and frames[-1].afterimage == (0.0,) * 5
        and contacts[-1] + contacts[-2] == (0.0,) * 10
        and _fixed_recurrence(contacts) == (0.0,) * 5
        and _diffuse_once(frames[-1].afterimage) == (0.0,) * 5
        and _asymmetry(frames[-2].afterimage, 1) == 0.0
        and _asymmetry(frames[-2].afterimage, 3) == 0.0
    )


def run_history_sensitive_reentry_probe(
    *,
    amplitude_order: Iterable[float] = REENTRY_AMPLITUDES,
    tau_order: Iterable[float] = REENTRY_TAUS,
    trajectory_order: Iterable[str] = REENTRY_TRAJECTORY_IDS,
    pair_order: Iterable[str] = REENTRY_PAIR_IDS,
    observer: ReentryObserver | None = None,
) -> HistorySensitiveReentryResult:
    """Execute only the fixed passive baselines from Methodik 029."""

    amplitude_order = _validated_order(
        amplitude_order,
        REENTRY_AMPLITUDES,
        "amplitude_order",
    )
    tau_order = _validated_order(tau_order, REENTRY_TAUS, "tau_order")
    trajectory_order = _validated_order(
        trajectory_order,
        REENTRY_TRAJECTORY_IDS,
        "trajectory_order",
    )
    pair_order = _validated_order(
        pair_order,
        REENTRY_PAIR_IDS,
        "pair_order",
    )

    observations = []
    resets_neutral = True
    for amplitude in amplitude_order:
        for tau in tau_order:
            for trajectory_id in trajectory_order:
                observation = _observe(
                    amplitude=float(amplitude),
                    tau=float(tau),
                    trajectory_id=str(trajectory_id),
                )
                before = observation.digest()
                if observer is not None:
                    observer(observation)
                if observation.digest() != before:
                    raise HistorySensitiveReentryProbeError(
                        "observer changed an immutable reentry observation"
                    )
                observations.append(observation)
            resets_neutral = resets_neutral and _reset_is_neutral(
                float(amplitude),
                float(tau),
            )

    canonical_observations = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.amplitude,
                item.tau,
                item.trajectory_id,
            ),
        )
    )
    by_key = {
        (item.amplitude, item.tau, item.trajectory_id): item
        for item in canonical_observations
    }
    pair_members = {"a-d": ("a", "d"), "b-c": ("b", "c")}
    pairs = []
    for amplitude in REENTRY_AMPLITUDES:
        for tau in REENTRY_TAUS:
            for pair_id in pair_order:
                left_id, right_id = pair_members[str(pair_id)]
                pairs.append(
                    _pair(
                        by_key[(amplitude, tau, left_id)],
                        by_key[(amplitude, tau, right_id)],
                        str(pair_id),
                    )
                )
    canonical_pairs = tuple(
        sorted(
            pairs,
            key=lambda item: (item.amplitude, item.tau, item.pair_id),
        )
    )

    mirrors_exact = all(
        _contacts("a", amplitude)
        == tuple(
            tuple(reversed(contact))
            for contact in _contacts("b", amplitude)
        )
        and _contacts("c", amplitude)
        == tuple(
            tuple(reversed(contact))
            for contact in _contacts("d", amplitude)
        )
        for amplitude in REENTRY_AMPLITUDES
    )
    b1_separates = all(pair.b1_distance > 0.0 for pair in canonical_pairs)
    return HistorySensitiveReentryResult(
        observations=canonical_observations,
        pairs=canonical_pairs,
        all_current_pairs_equal=all(
            pair.current_contacts_equal for pair in canonical_pairs
        ),
        all_prior_histories_distinct=all(
            pair.prior_histories_distinct for pair in canonical_pairs
        ),
        all_trajectory_mirrors_exact=mirrors_exact,
        all_resets_neutral=resets_neutral,
        b0_collides_all_pairs=all(
            pair.b0_distance == 0.0 for pair in canonical_pairs
        ),
        b1_separates_all_pairs=b1_separates,
        b2_collides_all_pairs=all(
            pair.b2_distance == 0.0 for pair in canonical_pairs
        ),
        b3_separates_all_pairs=all(
            pair.b3_distance > 0.0 for pair in canonical_pairs
        ),
        b4_separates_all_pairs=all(
            pair.b4_distance > 0.0 for pair in canonical_pairs
        ),
        b5_separates_all_pairs=all(
            pair.b5_distance > 0.0 for pair in canonical_pairs
        ),
        b1_covers_required_pair_distinction=b1_separates,
        unexplained_function_rest=not b1_separates,
    )


def history_sensitive_reentry_public_roles(
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(HistorySensitiveReentryObservation)),
        tuple(item.name for item in fields(HistorySensitiveReentryPair)),
        tuple(item.name for item in fields(HistorySensitiveReentryResult)),
    )
