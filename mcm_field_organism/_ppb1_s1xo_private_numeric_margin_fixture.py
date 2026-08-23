"""Private S1-XO numeric margin fixtures for PPB-1 engineering tests."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import _digest, normalized_mean_l1_distance


S1XO_SCHEMA_VERSION = "ppb1.s1xo.private-numeric-margin-fixture.v1"
S1XO_CONTRACT_DIGEST = (
    "cff21269c4981ffe7439de49e3eee35bd71528ed464f6f75937d1e9a192628b6"
)
S1XO_INVALID_FIXTURE = "S1XO_INVALID_FIXTURE"

S1XO_PROBE_CLASSES = (
    "exact-positive",
    "near-positive",
    "margin-positive",
    "margin-negative",
    "distinct-negative",
)
S1XO_EXPECTED_MASK = (True, True, True, False, False)
S1XO_MODALITY_SPECS = {
    "auditory": {
        "carrier_count": 12,
        "threshold": 0.25,
        "probe_values": (0.0, 0.125, 0.1875, 0.3125, 0.625),
        "minimum_margin": 0.0625,
    },
    "visual": {
        "carrier_count": 72,
        "threshold": 0.125,
        "probe_values": (0.0, 0.0625, 0.09375, 0.15625, 0.5),
        "minimum_margin": 0.03125,
    },
}

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1XONumericFixtureError(ValueError):
    """One fail-closed S1-XO fixture contract violation."""

    def __init__(self, detail: str) -> None:
        self.code = S1XO_INVALID_FIXTURE
        self.detail = detail
        super().__init__(f"{self.code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _finite_float(value: object, role: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, float)
        or not math.isfinite(value)
    ):
        raise S1XONumericFixtureError(f"{role} must be one finite float")
    return value


@dataclass(frozen=True, slots=True)
class S1XOModalityNumericFixture:
    modality_id: str
    carrier_count: int
    match_threshold: float
    minimum_threshold_separation: float
    probe_classes: tuple[str, ...]
    probe_values: tuple[float, ...]
    expected_recognition: tuple[bool, ...]
    computed_distances: tuple[float, ...]
    fixture_digest: str

    def __post_init__(self) -> None:
        spec = S1XO_MODALITY_SPECS.get(self.modality_id)
        if spec is None:
            raise S1XONumericFixtureError("unknown modality")
        if (
            isinstance(self.carrier_count, bool)
            or not isinstance(self.carrier_count, int)
            or self.carrier_count != spec["carrier_count"]
            or self.probe_classes != S1XO_PROBE_CLASSES
            or self.expected_recognition != S1XO_EXPECTED_MASK
            or self.probe_values != spec["probe_values"]
        ):
            raise S1XONumericFixtureError("fixture identity or inventory mismatch")
        threshold = _finite_float(self.match_threshold, "match_threshold")
        minimum_margin = _finite_float(
            self.minimum_threshold_separation,
            "minimum_threshold_separation",
        )
        if threshold != spec["threshold"] or minimum_margin != spec["minimum_margin"]:
            raise S1XONumericFixtureError("threshold or margin mismatch")
        if len(self.computed_distances) != len(S1XO_PROBE_CLASSES):
            raise S1XONumericFixtureError("distance inventory mismatch")

        prototype = (0.0,) * self.carrier_count
        for index, (value, distance, expected) in enumerate(
            zip(
                self.probe_values,
                self.computed_distances,
                self.expected_recognition,
                strict=True,
            )
        ):
            scalar = _finite_float(value, f"probe_values[{index}]")
            measured = _finite_float(distance, f"computed_distances[{index}]")
            recomputed = normalized_mean_l1_distance(
                (scalar,) * self.carrier_count,
                prototype,
            )
            if measured != recomputed or measured != scalar:
                raise S1XONumericFixtureError("distance is not production-metric exact")
            if (measured <= threshold) is not expected:
                raise S1XONumericFixtureError(
                    "computed class side differs from contract"
                )
            if index in {2, 3} and abs(measured - threshold) < minimum_margin:
                raise S1XONumericFixtureError("margin probe is too close to threshold")
            if measured == threshold:
                raise S1XONumericFixtureError("behavioral probe equals threshold")
        if self.fixture_digest != _digest(self.payload_without_digest()):
            raise S1XONumericFixtureError("fixture digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XO_SCHEMA_VERSION,
            "contract_digest": S1XO_CONTRACT_DIGEST,
            "modality_id": self.modality_id,
            "carrier_count": self.carrier_count,
            "match_threshold": self.match_threshold,
            "minimum_threshold_separation": self.minimum_threshold_separation,
            "probe_classes": list(self.probe_classes),
            "probe_values": list(self.probe_values),
            "expected_recognition": list(self.expected_recognition),
            "computed_distances": list(self.computed_distances),
        }


@dataclass(frozen=True, slots=True)
class S1XOThresholdOperatorCase:
    modality_id: str
    position: str
    threshold: float
    distance: float
    expected_recognized: bool
    case_digest: str

    def __post_init__(self) -> None:
        spec = S1XO_MODALITY_SPECS.get(self.modality_id)
        if spec is None or self.position not in {"below", "equal", "above"}:
            raise S1XONumericFixtureError("invalid operator case identity")
        threshold = _finite_float(self.threshold, "threshold")
        distance = _finite_float(self.distance, "distance")
        expected_distance = {
            "below": math.nextafter(threshold, -math.inf),
            "equal": threshold,
            "above": math.nextafter(threshold, math.inf),
        }[self.position]
        if (
            threshold != spec["threshold"]
            or distance != expected_distance
            or self.expected_recognized is not (distance <= threshold)
        ):
            raise S1XONumericFixtureError("operator case does not bind <= semantics")
        if self.case_digest != _digest(self.payload_without_digest()):
            raise S1XONumericFixtureError("operator case digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XO_SCHEMA_VERSION,
            "contract_digest": S1XO_CONTRACT_DIGEST,
            "modality_id": self.modality_id,
            "position": self.position,
            "threshold": self.threshold,
            "distance": self.distance,
            "expected_recognized": self.expected_recognized,
        }


@dataclass(frozen=True, slots=True)
class S1XONumericMarginFixtureBundle:
    modalities: tuple[S1XOModalityNumericFixture, ...]
    threshold_operator_cases: tuple[S1XOThresholdOperatorCase, ...]
    bundle_digest: str

    def __post_init__(self) -> None:
        if (
            tuple(item.modality_id for item in self.modalities)
            != ("auditory", "visual")
            or tuple(
                (item.modality_id, item.position)
                for item in self.threshold_operator_cases
            )
            != tuple(
                (modality, position)
                for modality in ("auditory", "visual")
                for position in ("below", "equal", "above")
            )
            or not _valid_digest(self.bundle_digest)
            or self.bundle_digest != _digest(self.payload_without_digest())
        ):
            raise S1XONumericFixtureError("bundle inventory or digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XO_SCHEMA_VERSION,
            "contract_digest": S1XO_CONTRACT_DIGEST,
            "modality_fixture_digests": [
                item.fixture_digest for item in self.modalities
            ],
            "threshold_operator_case_digests": [
                item.case_digest for item in self.threshold_operator_cases
            ],
        }


def build_s1xo_numeric_margin_fixture() -> S1XONumericMarginFixtureBundle:
    """Build and validate only the two private margin fixtures."""

    modalities = []
    operator_cases = []
    for modality_id, spec in S1XO_MODALITY_SPECS.items():
        carrier_count = spec["carrier_count"]
        threshold = spec["threshold"]
        probe_values = spec["probe_values"]
        prototype = (0.0,) * carrier_count
        distances = tuple(
            normalized_mean_l1_distance((value,) * carrier_count, prototype)
            for value in probe_values
        )
        values = {
            "modality_id": modality_id,
            "carrier_count": carrier_count,
            "match_threshold": threshold,
            "minimum_threshold_separation": spec["minimum_margin"],
            "probe_classes": S1XO_PROBE_CLASSES,
            "probe_values": probe_values,
            "expected_recognition": S1XO_EXPECTED_MASK,
            "computed_distances": distances,
        }
        modalities.append(
            S1XOModalityNumericFixture(
                **values,
                fixture_digest=_digest(
                    {
                        "schema_version": S1XO_SCHEMA_VERSION,
                        "contract_digest": S1XO_CONTRACT_DIGEST,
                        **{
                            key: list(value)
                            if isinstance(value, tuple)
                            else value
                            for key, value in values.items()
                        },
                    }
                ),
            )
        )
        for position, distance in (
            ("below", math.nextafter(threshold, -math.inf)),
            ("equal", threshold),
            ("above", math.nextafter(threshold, math.inf)),
        ):
            case_values = {
                "modality_id": modality_id,
                "position": position,
                "threshold": threshold,
                "distance": distance,
                "expected_recognized": distance <= threshold,
            }
            operator_cases.append(
                S1XOThresholdOperatorCase(
                    **case_values,
                    case_digest=_digest(
                        {
                            "schema_version": S1XO_SCHEMA_VERSION,
                            "contract_digest": S1XO_CONTRACT_DIGEST,
                            **case_values,
                        }
                    ),
                )
            )
    payload = {
        "schema_version": S1XO_SCHEMA_VERSION,
        "contract_digest": S1XO_CONTRACT_DIGEST,
        "modality_fixture_digests": [item.fixture_digest for item in modalities],
        "threshold_operator_case_digests": [
            item.case_digest for item in operator_cases
        ],
    }
    return S1XONumericMarginFixtureBundle(
        tuple(modalities),
        tuple(operator_cases),
        _digest(payload),
    )
