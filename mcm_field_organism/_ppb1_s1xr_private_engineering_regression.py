"""Private S1-XR PPB-1 engineering regression against one static prototype."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    _digest,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from ._ppb1_s1xo_private_numeric_margin_fixture import (
    S1XOModalityNumericFixture,
    build_s1xo_numeric_margin_fixture,
)
from .receptor_contract import ReceptorContactFrame


S1XR_SCHEMA_VERSION = "ppb1.s1xr.private-engineering-regression.v1"
S1XR_CONTRACT_DIGEST = (
    "72eeed148a75a61253099c77f10e359243e287d6c8e8d9517fe4833e29187688"
)
S1XR_PASS = "ENGINEERING_REGRESSION_VALID_EQUIVALENT_TO_STATIC_PROTOTYPE"
S1XR_FAIL = "ENGINEERING_REGRESSION_FAIL"
S1XR_INVALID = "S1XR_INVALID_ENGINEERING_REGRESSION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_EVENTS = ("CREATED", "MATCHED", "MATCHED")


class S1XREngineeringRegressionError(ValueError):
    """One fail-closed private engineering regression violation."""

    def __init__(self, detail: str) -> None:
        self.code = S1XR_INVALID
        self.detail = detail
        super().__init__(f"{self.code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _receipt_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1XR_SCHEMA_VERSION,
            "contract_digest": S1XR_CONTRACT_DIGEST,
            **payload,
        }
    )


@dataclass(frozen=True, slots=True)
class S1XRFormationReceipt:
    modality_id: str
    config_digest: str
    fixture_digest: str
    formed_state_digest: str
    state_identity_digest: str
    ordered_events: tuple[str, ...]
    occupied_slot_count: int
    stabilized_slot_count: int
    support_count: int
    formation_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.modality_id not in {"auditory", "visual"}
            or not all(
                _valid_digest(value)
                for value in (
                    self.config_digest,
                    self.fixture_digest,
                    self.formed_state_digest,
                    self.state_identity_digest,
                )
            )
            or self.ordered_events != _EXPECTED_EVENTS
            or self.occupied_slot_count != 1
            or self.stabilized_slot_count != 1
            or self.support_count != 3
            or self.formation_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1XREngineeringRegressionError("invalid formation receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "config_digest": self.config_digest,
            "fixture_digest": self.fixture_digest,
            "formed_state_digest": self.formed_state_digest,
            "state_identity_digest": self.state_identity_digest,
            "ordered_events": list(self.ordered_events),
            "occupied_slot_count": self.occupied_slot_count,
            "stabilized_slot_count": self.stabilized_slot_count,
            "support_count": self.support_count,
        }


@dataclass(frozen=True, slots=True)
class S1XREngineeringCellReceipt:
    cell_id: str
    role: str
    modality_id: str
    probe_class: str
    config_digest: str
    observed_state_digest: str | None
    state_identity_digest: str | None
    recognized: bool
    distance: float
    state_unchanged: bool
    raw_history_access_used: bool
    matches_fixture: bool
    cell_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.role not in {"candidate", "static-zero-prototype"}
            or self.modality_id not in {"auditory", "visual"}
            or not _valid_digest(self.config_digest)
            or not isinstance(self.recognized, bool)
            or isinstance(self.distance, bool)
            or not isinstance(self.distance, float)
            or not math.isfinite(self.distance)
            or self.distance < 0.0
            or not isinstance(self.state_unchanged, bool)
            or not isinstance(self.raw_history_access_used, bool)
            or not isinstance(self.matches_fixture, bool)
        ):
            raise S1XREngineeringRegressionError("invalid cell receipt anatomy")
        expected_id = (
            f"s1xr.{self.role}.{self.modality_id}.{self.probe_class}"
        )
        if self.cell_id != expected_id or self.raw_history_access_used:
            raise S1XREngineeringRegressionError("invalid cell identity or history role")
        if self.role == "candidate":
            if (
                not _valid_digest(self.observed_state_digest)
                or not _valid_digest(self.state_identity_digest)
                or not self.state_unchanged
            ):
                raise S1XREngineeringRegressionError(
                    "candidate cell is not state-bound and read-only"
                )
        elif self.observed_state_digest is not None or self.state_identity_digest is not None:
            raise S1XREngineeringRegressionError(
                "static baseline received candidate state identity"
            )
        if self.cell_receipt_digest != _receipt_digest(self.payload_without_digest()):
            raise S1XREngineeringRegressionError("cell receipt digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "role": self.role,
            "modality_id": self.modality_id,
            "probe_class": self.probe_class,
            "config_digest": self.config_digest,
            "observed_state_digest": self.observed_state_digest,
            "state_identity_digest": self.state_identity_digest,
            "recognized": self.recognized,
            "distance": self.distance,
            "state_unchanged": self.state_unchanged,
            "raw_history_access_used": self.raw_history_access_used,
            "matches_fixture": self.matches_fixture,
        }


@dataclass(frozen=True, slots=True)
class S1XREngineeringRegressionReceipt:
    fixture_bundle_digest: str
    ordered_formation_receipt_digests: tuple[str, ...]
    ordered_cell_receipt_digests: tuple[str, ...]
    candidate_cell_count: int
    baseline_cell_count: int
    all_candidate_cells_match_fixture: bool
    all_candidate_states_unchanged: bool
    candidate_baseline_equivalent: bool
    decision: str
    regression_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_digest(self.fixture_bundle_digest)
            or len(self.ordered_formation_receipt_digests) != 2
            or len(self.ordered_cell_receipt_digests) != 20
            or not all(
                _valid_digest(value)
                for value in (
                    *self.ordered_formation_receipt_digests,
                    *self.ordered_cell_receipt_digests,
                )
            )
            or self.candidate_cell_count != 10
            or self.baseline_cell_count != 10
            or not isinstance(self.all_candidate_cells_match_fixture, bool)
            or not isinstance(self.all_candidate_states_unchanged, bool)
            or not isinstance(self.candidate_baseline_equivalent, bool)
        ):
            raise S1XREngineeringRegressionError("invalid regression receipt anatomy")
        expected_decision = (
            S1XR_PASS
            if self.all_candidate_cells_match_fixture
            and self.all_candidate_states_unchanged
            and self.candidate_baseline_equivalent
            else S1XR_FAIL
        )
        if (
            self.decision != expected_decision
            or self.regression_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1XREngineeringRegressionError(
                "regression decision or digest mismatch"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "fixture_bundle_digest": self.fixture_bundle_digest,
            "ordered_formation_receipt_digests": list(
                self.ordered_formation_receipt_digests
            ),
            "ordered_cell_receipt_digests": list(
                self.ordered_cell_receipt_digests
            ),
            "candidate_cell_count": self.candidate_cell_count,
            "baseline_cell_count": self.baseline_cell_count,
            "all_candidate_cells_match_fixture": (
                self.all_candidate_cells_match_fixture
            ),
            "all_candidate_states_unchanged": self.all_candidate_states_unchanged,
            "candidate_baseline_equivalent": self.candidate_baseline_equivalent,
            "decision": self.decision,
        }


@dataclass(frozen=True, slots=True)
class S1XREngineeringRegressionResult:
    formation_receipts: tuple[S1XRFormationReceipt, ...]
    cell_receipts: tuple[S1XREngineeringCellReceipt, ...]
    regression_receipt: S1XREngineeringRegressionReceipt

    def __post_init__(self) -> None:
        if (
            tuple(item.modality_id for item in self.formation_receipts)
            != ("auditory", "visual")
            or tuple(
                item.formation_receipt_digest for item in self.formation_receipts
            )
            != self.regression_receipt.ordered_formation_receipt_digests
            or tuple(item.cell_receipt_digest for item in self.cell_receipts)
            != self.regression_receipt.ordered_cell_receipt_digests
        ):
            raise S1XREngineeringRegressionError("result is not atomic")


def _config(fixture: S1XOModalityNumericFixture) -> PPB1BankConfig:
    modality = fixture.modality_id
    carriers = tuple(
        f"carrier.s1xr.{modality}.{index:03d}"
        for index in range(fixture.carrier_count)
    )
    return PPB1BankConfig(
        f"ppb1.s1xr.{modality}",
        modality,
        f"geometry.s1xr.{modality}",
        carriers,
        2,
        fixture.match_threshold,
        0.5,
        3,
        8,
    )


def _frame(
    config: PPB1BankConfig,
    scalar: float,
    role: str,
    start: int,
    end: int,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1xr.{config.modality_id}.{role}",
        f"clock.s1xr.{config.modality_id}",
        start,
        end,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


def _form_state(
    fixture: S1XOModalityNumericFixture,
) -> tuple[PPB1BankConfig, PPB1BankState, S1XRFormationReceipt]:
    config = _config(fixture)
    state = initial_ppb1_bank_state(config)
    events = []
    for index in range(3):
        step = advance_ppb1_bank(
            config,
            state,
            _frame(config, 0.0, f"formation.{index + 1}", index, index + 1),
        )
        state = step.poststate
        events.append(step.readout.event)
    occupied = tuple(slot for slot in state.slots if slot.occupied)
    stabilized = tuple(
        slot
        for slot in occupied
        if slot.support_count is not None
        and slot.support_count >= config.stable_after
    )
    if (
        tuple(events) != _EXPECTED_EVENTS
        or len(occupied) != 1
        or len(stabilized) != 1
        or occupied[0].support_count != 3
        or occupied[0].prototype_values != (0.0,) * fixture.carrier_count
    ):
        raise S1XREngineeringRegressionError("formed state differs from contract")
    identity = _digest(_state_identity_payload(state))
    values = {
        "modality_id": fixture.modality_id,
        "config_digest": config.digest(),
        "fixture_digest": fixture.fixture_digest,
        "formed_state_digest": state.digest(),
        "state_identity_digest": identity,
        "ordered_events": tuple(events),
        "occupied_slot_count": len(occupied),
        "stabilized_slot_count": len(stabilized),
        "support_count": occupied[0].support_count,
    }
    return (
        config,
        state,
        S1XRFormationReceipt(
            **values,
            formation_receipt_digest=_receipt_digest(values),
        ),
    )


def _candidate_cells(
    fixture: S1XOModalityNumericFixture,
    config: PPB1BankConfig,
    state: PPB1BankState,
) -> tuple[S1XREngineeringCellReceipt, ...]:
    cells = []
    before = state.digest()
    identity = _digest(_state_identity_payload(state))
    for probe_class, scalar, expected_recognized, expected_distance in zip(
        fixture.probe_classes,
        fixture.probe_values,
        fixture.expected_recognition,
        fixture.computed_distances,
        strict=True,
    ):
        finding = probe_s1wu_perceptual_state(
            config,
            state,
            _frame(config, scalar, f"probe.{probe_class}", 3, 4),
            f"probe.s1xr.{fixture.modality_id}.{probe_class}",
        )
        after = state.digest()
        matches = (
            finding.recognized == expected_recognized
            and finding.match_distance == expected_distance
        )
        values = {
            "cell_id": f"s1xr.candidate.{fixture.modality_id}.{probe_class}",
            "role": "candidate",
            "modality_id": fixture.modality_id,
            "probe_class": probe_class,
            "config_digest": config.digest(),
            "observed_state_digest": before,
            "state_identity_digest": identity,
            "recognized": finding.recognized,
            "distance": finding.match_distance,
            "state_unchanged": before == after,
            "raw_history_access_used": False,
            "matches_fixture": matches,
        }
        cells.append(
            S1XREngineeringCellReceipt(
                **values,
                cell_receipt_digest=_receipt_digest(values),
            )
        )
    return tuple(cells)


def _baseline_cells(
    fixture: S1XOModalityNumericFixture,
    config: PPB1BankConfig,
) -> tuple[S1XREngineeringCellReceipt, ...]:
    prototype = (0.0,) * fixture.carrier_count
    cells = []
    for probe_class, scalar, expected_recognized, expected_distance in zip(
        fixture.probe_classes,
        fixture.probe_values,
        fixture.expected_recognition,
        fixture.computed_distances,
        strict=True,
    ):
        distance = normalized_mean_l1_distance(
            (scalar,) * fixture.carrier_count,
            prototype,
        )
        recognized = distance <= fixture.match_threshold
        values = {
            "cell_id": (
                f"s1xr.static-zero-prototype.{fixture.modality_id}.{probe_class}"
            ),
            "role": "static-zero-prototype",
            "modality_id": fixture.modality_id,
            "probe_class": probe_class,
            "config_digest": config.digest(),
            "observed_state_digest": None,
            "state_identity_digest": None,
            "recognized": recognized,
            "distance": distance,
            "state_unchanged": True,
            "raw_history_access_used": False,
            "matches_fixture": (
                recognized == expected_recognized
                and distance == expected_distance
            ),
        }
        cells.append(
            S1XREngineeringCellReceipt(
                **values,
                cell_receipt_digest=_receipt_digest(values),
            )
        )
    return tuple(cells)


def run_s1xr_private_engineering_regression() -> S1XREngineeringRegressionResult:
    """Run only the finite private engineering regression."""

    fixture_bundle = build_s1xo_numeric_margin_fixture()
    formed = tuple(_form_state(fixture) for fixture in fixture_bundle.modalities)
    formation_receipts = tuple(item[2] for item in formed)
    candidate_cells = tuple(
        cell
        for fixture, (config, state, _) in zip(
            fixture_bundle.modalities, formed, strict=True
        )
        for cell in _candidate_cells(fixture, config, state)
    )
    baseline_cells = tuple(
        cell
        for fixture, (config, _, _) in zip(
            fixture_bundle.modalities, formed, strict=True
        )
        for cell in _baseline_cells(fixture, config)
    )
    cells = candidate_cells + baseline_cells
    candidate_map = {
        (cell.modality_id, cell.probe_class): cell for cell in candidate_cells
    }
    baseline_map = {
        (cell.modality_id, cell.probe_class): cell for cell in baseline_cells
    }
    equivalent = candidate_map.keys() == baseline_map.keys() and all(
        candidate_map[key].recognized == baseline_map[key].recognized
        and candidate_map[key].distance == baseline_map[key].distance
        for key in candidate_map
    )
    all_matches = all(cell.matches_fixture for cell in candidate_cells)
    all_unchanged = all(cell.state_unchanged for cell in candidate_cells)
    decision = S1XR_PASS if all_matches and all_unchanged and equivalent else S1XR_FAIL
    values = {
        "fixture_bundle_digest": fixture_bundle.bundle_digest,
        "ordered_formation_receipt_digests": tuple(
            item.formation_receipt_digest for item in formation_receipts
        ),
        "ordered_cell_receipt_digests": tuple(
            item.cell_receipt_digest for item in cells
        ),
        "candidate_cell_count": len(candidate_cells),
        "baseline_cell_count": len(baseline_cells),
        "all_candidate_cells_match_fixture": all_matches,
        "all_candidate_states_unchanged": all_unchanged,
        "candidate_baseline_equivalent": equivalent,
        "decision": decision,
    }
    receipt = S1XREngineeringRegressionReceipt(
        **values,
        regression_receipt_digest=_receipt_digest(values),
    )
    return S1XREngineeringRegressionResult(
        formation_receipts,
        cells,
        receipt,
    )
