"""Private S1-XF miniature runner and digest-bound technical receipts."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import (
    PPB1BankState,
    _digest,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from ._ppb1_s1xc_fixture_registry import (
    S1XC_SYSTEM_IDS,
    S1XCBaselinePrestate,
    S1XCModalityFixture,
    _frame_digest,
    materialize_s1xc_fixture_registry,
    probe_s1xc_baseline_read_only,
)


S1XF_SCHEMA_VERSION = "ppb1.s1xf.private-miniature-runner.v1"
S1XF_CONTRACT_DIGEST = (
    "eb501a103ec40dc9234e946553afb554279089ed2381a03011daa91f9db7731c"
)
S1XF_MINI_PROBE_CLASSES = ("exact-positive", "distinct-negative")
S1XF_TECHNICAL_RUNNER_PASS = "MINIATURE_RUNNER_AND_RECEIPTS_VALID"
S1XF_INVALID_FORMATION = "S1XF_INVALID_FORMATION"
S1XF_INVALID_RECEIPT = "S1XF_INVALID_RECEIPT"
S1XF_INVALID_RUN = "S1XF_INVALID_RUN"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1XFError(ValueError):
    """One fail-closed S1-XF runner or receipt violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S1XFFormationReceipt:
    modality_id: str
    config_digest: str
    template_state_digest: str
    formed_state_digest: str
    formed_state_identity_digest: str
    formation_history_digest: str
    ordered_frame_digests: tuple[str, ...]
    ordered_event_sequence: tuple[str, ...]
    ordered_step_readout_digests: tuple[str, ...]
    template_match: bool
    formation_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.modality_id not in {"auditory", "visual"}
            or len(self.ordered_frame_digests) != 3
            or len(self.ordered_step_readout_digests) != 3
            or self.ordered_event_sequence != ("CREATED", "MATCHED", "MATCHED")
            or not self.template_match
        ):
            raise S1XFError(S1XF_INVALID_RECEIPT, "invalid formation receipt")
        for value in (
            self.config_digest,
            self.template_state_digest,
            self.formed_state_digest,
            self.formed_state_identity_digest,
            self.formation_history_digest,
            *self.ordered_frame_digests,
            *self.ordered_step_readout_digests,
        ):
            if not _valid_digest(value):
                raise S1XFError(
                    S1XF_INVALID_RECEIPT, "formation receipt digest role is invalid"
                )
        if (
            self.template_state_digest != self.formed_state_digest
            or self.formation_receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1XFError(
                S1XF_INVALID_RECEIPT, "formation receipt is not template-bound"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XF_SCHEMA_VERSION,
            "contract_digest": S1XF_CONTRACT_DIGEST,
            "modality_id": self.modality_id,
            "config_digest": self.config_digest,
            "template_state_digest": self.template_state_digest,
            "formed_state_digest": self.formed_state_digest,
            "formed_state_identity_digest": self.formed_state_identity_digest,
            "formation_history_digest": self.formation_history_digest,
            "ordered_frame_digests": list(self.ordered_frame_digests),
            "ordered_event_sequence": list(self.ordered_event_sequence),
            "ordered_step_readout_digests": list(
                self.ordered_step_readout_digests
            ),
            "template_match": self.template_match,
        }


@dataclass(frozen=True, slots=True)
class S1XFCellReceipt:
    cell_id: str
    system_id: str
    modality_id: str
    probe_class: str
    finding_digest: str
    recognized: bool
    nearest_distance: float | None
    observed_state_present: bool
    observed_state_digest_before: str | None
    observed_state_digest_after: str | None
    state_identity_digest: str | None
    state_provenance_digest: str | None
    storage_role_count: int
    stored_scalar_value_count: int
    raw_history_access_used: bool
    state_unchanged: bool
    matches_miniature_expectation: bool
    cell_receipt_digest: str

    def __post_init__(self) -> None:
        expected_id = f"s1xf-mini.{self.modality_id}.{self.system_id}.{self.probe_class}"
        if (
            self.cell_id != expected_id
            or self.system_id not in S1XC_SYSTEM_IDS
            or self.modality_id not in {"auditory", "visual"}
            or self.probe_class not in S1XF_MINI_PROBE_CLASSES
            or not _valid_digest(self.finding_digest)
            or not isinstance(self.recognized, bool)
            or not isinstance(self.observed_state_present, bool)
            or not isinstance(self.raw_history_access_used, bool)
            or not self.state_unchanged
            or not self.matches_miniature_expectation
        ):
            raise S1XFError(S1XF_INVALID_RECEIPT, "invalid miniature cell receipt")
        if self.nearest_distance is not None and (
            not math.isfinite(self.nearest_distance)
            or self.nearest_distance < 0.0
            or self.nearest_distance > 2.0
        ):
            raise S1XFError(S1XF_INVALID_RECEIPT, "invalid miniature distance")
        for count in (self.storage_role_count, self.stored_scalar_value_count):
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise S1XFError(S1XF_INVALID_RECEIPT, "invalid storage count")
        optional_digests = (
            self.observed_state_digest_before,
            self.observed_state_digest_after,
            self.state_identity_digest,
            self.state_provenance_digest,
        )
        if any(value is not None and not _valid_digest(value) for value in optional_digests):
            raise S1XFError(S1XF_INVALID_RECEIPT, "invalid optional digest role")
        if self.observed_state_present:
            if (
                self.observed_state_digest_before is None
                or self.observed_state_digest_after
                != self.observed_state_digest_before
            ):
                raise S1XFError(
                    S1XF_INVALID_RECEIPT, "observed state must remain unchanged"
                )
        elif any(value is not None for value in optional_digests):
            raise S1XFError(
                S1XF_INVALID_RECEIPT, "absent state requires canonical null roles"
            )
        if self.system_id == "ppb1":
            if self.state_identity_digest is None or self.raw_history_access_used:
                raise S1XFError(
                    S1XF_INVALID_RECEIPT, "candidate identity or history role invalid"
                )
        elif self.state_identity_digest is not None:
            raise S1XFError(
                S1XF_INVALID_RECEIPT, "baseline received candidate identity"
            )
        if self.system_id == "no-memory" and (
            self.observed_state_present
            or self.recognized
            or self.nearest_distance is not None
            or self.storage_role_count != 0
            or self.stored_scalar_value_count != 0
            or self.raw_history_access_used
        ):
            raise S1XFError(
                S1XF_INVALID_RECEIPT, "no-memory receipt roles are not canonical"
            )
        if self.cell_receipt_digest != _digest(self.payload_without_digest()):
            raise S1XFError(S1XF_INVALID_RECEIPT, "cell receipt digest mismatch")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XF_SCHEMA_VERSION,
            "contract_digest": S1XF_CONTRACT_DIGEST,
            "cell_id": self.cell_id,
            "system_id": self.system_id,
            "modality_id": self.modality_id,
            "probe_class": self.probe_class,
            "finding_digest": self.finding_digest,
            "recognized": self.recognized,
            "nearest_distance": self.nearest_distance,
            "observed_state_present": self.observed_state_present,
            "observed_state_digest_before": self.observed_state_digest_before,
            "observed_state_digest_after": self.observed_state_digest_after,
            "state_identity_digest": self.state_identity_digest,
            "state_provenance_digest": self.state_provenance_digest,
            "storage_role_count": self.storage_role_count,
            "stored_scalar_value_count": self.stored_scalar_value_count,
            "raw_history_access_used": self.raw_history_access_used,
            "state_unchanged": self.state_unchanged,
            "matches_miniature_expectation": self.matches_miniature_expectation,
        }


@dataclass(frozen=True, slots=True)
class S1XFMatrixReceipt:
    materialization_digest: str
    ordered_formation_receipt_digests: tuple[str, ...]
    ordered_cell_receipt_digests: tuple[str, ...]
    initial_state_call_count: int
    formation_advance_call_count: int
    candidate_probe_call_count: int
    baseline_probe_call_count: int
    miniature_cell_count: int
    registered_matrix_cell_count: int
    technical_runner_decision: str
    matrix_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_digest(self.materialization_digest)
            or len(self.ordered_formation_receipt_digests) != 2
            or len(self.ordered_cell_receipt_digests) != 24
            or any(
                not _valid_digest(value)
                for value in (
                    *self.ordered_formation_receipt_digests,
                    *self.ordered_cell_receipt_digests,
                )
            )
            or self.initial_state_call_count != 2
            or self.formation_advance_call_count != 6
            or self.candidate_probe_call_count != 4
            or self.baseline_probe_call_count != 20
            or self.miniature_cell_count != 24
            or self.registered_matrix_cell_count != 0
            or self.technical_runner_decision != S1XF_TECHNICAL_RUNNER_PASS
            or self.matrix_receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1XFError(S1XF_INVALID_RECEIPT, "invalid miniature matrix receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1XF_SCHEMA_VERSION,
            "contract_digest": S1XF_CONTRACT_DIGEST,
            "materialization_digest": self.materialization_digest,
            "ordered_formation_receipt_digests": list(
                self.ordered_formation_receipt_digests
            ),
            "ordered_cell_receipt_digests": list(
                self.ordered_cell_receipt_digests
            ),
            "initial_state_call_count": self.initial_state_call_count,
            "formation_advance_call_count": self.formation_advance_call_count,
            "candidate_probe_call_count": self.candidate_probe_call_count,
            "baseline_probe_call_count": self.baseline_probe_call_count,
            "miniature_cell_count": self.miniature_cell_count,
            "registered_matrix_cell_count": self.registered_matrix_cell_count,
            "technical_runner_decision": self.technical_runner_decision,
        }


@dataclass(frozen=True, slots=True)
class S1XFRunResult:
    formation_receipts: tuple[S1XFFormationReceipt, ...]
    cell_receipts: tuple[S1XFCellReceipt, ...]
    matrix_receipt: S1XFMatrixReceipt

    def __post_init__(self) -> None:
        expected_cell_ids = tuple(
            f"s1xf-mini.{modality}.{system}.{probe}"
            for modality in ("auditory", "visual")
            for system in S1XC_SYSTEM_IDS
            for probe in S1XF_MINI_PROBE_CLASSES
        )
        if (
            tuple(item.modality_id for item in self.formation_receipts)
            != ("auditory", "visual")
            or tuple(item.cell_id for item in self.cell_receipts)
            != expected_cell_ids
            or tuple(
                item.formation_receipt_digest for item in self.formation_receipts
            )
            != self.matrix_receipt.ordered_formation_receipt_digests
            or tuple(item.cell_receipt_digest for item in self.cell_receipts)
            != self.matrix_receipt.ordered_cell_receipt_digests
        ):
            raise S1XFError(S1XF_INVALID_RUN, "run result is not atomic")


def _receipt_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1XF_SCHEMA_VERSION,
            "contract_digest": S1XF_CONTRACT_DIGEST,
            **payload,
        }
    )


def _form_candidate(
    fixture: S1XCModalityFixture,
) -> tuple[PPB1BankState, S1XFFormationReceipt]:
    state = initial_ppb1_bank_state(fixture.config)
    events = []
    readout_digests = []
    for frame in fixture.formation_frames:
        result = advance_ppb1_bank(fixture.config, state, frame)
        state = result.poststate
        events.append(result.readout.event)
        readout_digests.append(result.readout.digest())

    identity_digest = _digest(_state_identity_payload(state))
    if (
        tuple(events) != ("CREATED", "MATCHED", "MATCHED")
        or state != fixture.candidate_prestate
        or state.digest() != fixture.candidate_prestate.digest()
        or identity_digest != fixture.candidate_state_identity_digest
    ):
        raise S1XFError(
            S1XF_INVALID_FORMATION,
            "executed candidate formation does not match the bound template",
        )
    values = {
        "modality_id": fixture.config.modality_id,
        "config_digest": fixture.config.digest(),
        "template_state_digest": fixture.candidate_prestate.digest(),
        "formed_state_digest": state.digest(),
        "formed_state_identity_digest": identity_digest,
        "formation_history_digest": fixture.formation_history_digest,
        "ordered_frame_digests": tuple(
            _frame_digest(frame) for frame in fixture.formation_frames
        ),
        "ordered_event_sequence": tuple(events),
        "ordered_step_readout_digests": tuple(readout_digests),
        "template_match": True,
    }
    return state, S1XFFormationReceipt(
        **values,
        formation_receipt_digest=_receipt_digest(values),
    )


def _candidate_cell(
    fixture: S1XCModalityFixture,
    formed_state: PPB1BankState,
    probe_class: str,
    frame_index: int,
) -> S1XFCellReceipt:
    frame = fixture.probe_frames[frame_index]
    before = formed_state.digest()
    identity = _digest(_state_identity_payload(formed_state))
    finding = probe_s1wu_perceptual_state(
        fixture.config,
        formed_state,
        frame,
        f"probe.s1xf-mini.{fixture.config.modality_id}.ppb1.{probe_class}",
    )
    after = formed_state.digest()
    expected_recognized = probe_class == "exact-positive"
    expected_distance = 0.0 if expected_recognized else frame.values[0]
    values = {
        "cell_id": f"s1xf-mini.{fixture.config.modality_id}.ppb1.{probe_class}",
        "system_id": "ppb1",
        "modality_id": fixture.config.modality_id,
        "probe_class": probe_class,
        "finding_digest": finding.finding_digest,
        "recognized": finding.recognized,
        "nearest_distance": finding.match_distance,
        "observed_state_present": True,
        "observed_state_digest_before": before,
        "observed_state_digest_after": after,
        "state_identity_digest": identity,
        "state_provenance_digest": fixture.formation_history_digest,
        "storage_role_count": 1,
        "stored_scalar_value_count": len(fixture.config.carrier_ids),
        "raw_history_access_used": False,
        "state_unchanged": before == after,
        "matches_miniature_expectation": (
            finding.recognized == expected_recognized
            and finding.match_distance == expected_distance
        ),
    }
    return S1XFCellReceipt(
        **values,
        cell_receipt_digest=_receipt_digest(values),
    )


def _baseline_cell(
    fixture: S1XCModalityFixture,
    system_id: str,
    prestate: S1XCBaselinePrestate | None,
    probe_class: str,
    frame_index: int,
) -> S1XFCellReceipt:
    frame = fixture.probe_frames[frame_index]
    before = None if prestate is None else prestate.digest()
    finding = probe_s1xc_baseline_read_only(
        system_id, fixture.config, prestate, frame, probe_class
    )
    after = None if prestate is None else prestate.digest()
    expected_recognized = False if system_id == "no-memory" else probe_class == "exact-positive"
    expected_distance = (
        None
        if system_id == "no-memory"
        else 0.0 if probe_class == "exact-positive" else frame.values[0]
    )
    values = {
        "cell_id": f"s1xf-mini.{fixture.config.modality_id}.{system_id}.{probe_class}",
        "system_id": system_id,
        "modality_id": fixture.config.modality_id,
        "probe_class": probe_class,
        "finding_digest": finding.finding_digest,
        "recognized": finding.recognized,
        "nearest_distance": finding.match_distance,
        "observed_state_present": prestate is not None,
        "observed_state_digest_before": before,
        "observed_state_digest_after": after,
        "state_identity_digest": None,
        "state_provenance_digest": (
            None if prestate is None else fixture.formation_history_digest
        ),
        "storage_role_count": 0 if prestate is None else 1,
        "stored_scalar_value_count": finding.stored_scalar_value_count,
        "raw_history_access_used": finding.raw_history_access_used,
        "state_unchanged": before == after,
        "matches_miniature_expectation": (
            finding.recognized == expected_recognized
            and finding.match_distance == expected_distance
        ),
    }
    return S1XFCellReceipt(
        **values,
        cell_receipt_digest=_receipt_digest(values),
    )


def run_s1xf_miniature_contract() -> S1XFRunResult:
    """Run the fixed 24-cell substitute matrix after six real formation steps."""

    materialized = materialize_s1xc_fixture_registry()
    formed = []
    formation_receipts = []
    for fixture in materialized.modalities:
        state, receipt = _form_candidate(fixture)
        formed.append(state)
        formation_receipts.append(receipt)

    baseline_by_role = {
        (item.modality_id, item.system_id): item
        for item in materialized.baseline_prestates
    }
    cell_receipts = []
    probe_indices = (0, 4)
    for fixture, formed_state in zip(materialized.modalities, formed, strict=True):
        for system_id in S1XC_SYSTEM_IDS:
            for probe_class, frame_index in zip(
                S1XF_MINI_PROBE_CLASSES, probe_indices, strict=True
            ):
                if system_id == "ppb1":
                    receipt = _candidate_cell(
                        fixture, formed_state, probe_class, frame_index
                    )
                else:
                    receipt = _baseline_cell(
                        fixture,
                        system_id,
                        baseline_by_role.get(
                            (fixture.config.modality_id, system_id)
                        ),
                        probe_class,
                        frame_index,
                    )
                cell_receipts.append(receipt)

    if len(cell_receipts) != 24 or len({item.cell_id for item in cell_receipts}) != 24:
        raise S1XFError(S1XF_INVALID_RUN, "miniature receipt set is incomplete")
    values = {
        "materialization_digest": materialized.materialization_digest,
        "ordered_formation_receipt_digests": tuple(
            item.formation_receipt_digest for item in formation_receipts
        ),
        "ordered_cell_receipt_digests": tuple(
            item.cell_receipt_digest for item in cell_receipts
        ),
        "initial_state_call_count": 2,
        "formation_advance_call_count": 6,
        "candidate_probe_call_count": 4,
        "baseline_probe_call_count": 20,
        "miniature_cell_count": 24,
        "registered_matrix_cell_count": 0,
        "technical_runner_decision": S1XF_TECHNICAL_RUNNER_PASS,
    }
    matrix = S1XFMatrixReceipt(
        **values,
        matrix_receipt_digest=_receipt_digest(values),
    )
    return S1XFRunResult(
        tuple(formation_receipts), tuple(cell_receipts), matrix
    )
