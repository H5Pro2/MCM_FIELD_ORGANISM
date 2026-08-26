"""Cell-wise four-arm adapter for the preregistered S1-T ledgers."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .s1r_phase_separation_matrix import S1R_DOSE_COUNTS, S1R_SOURCE_FORMS
from .s1u_f3_component_observer import (
    S1UComponentLedgerResult,
    run_s1u_component_cell,
    run_s1u_component_late_interval,
)


class S1VFourCurveComponentMatrixError(ValueError):
    """Raised when one S1-V ledger leaves the preregistered inventory."""


S1V_MODELS = ("f3", "linear-coupled-field", "kappa-null", "eta-null")
S1V_REFINEMENTS = (2, 4)
S1V_EARLY_CUMULATIVE_ENDS = (0.025, 0.05, 0.1, 0.2)
S1V_LATE_INTERVALS = ((0.2, 0.4), (0.4, 0.8), (0.8, 1.6))


@dataclass(frozen=True, slots=True)
class S1VLedgerCellContract:
    ledger_id: str
    dose_count: int
    source_form: str
    ledger_role: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True, slots=True)
class S1VLedgerCellMeasurement:
    cell: S1VLedgerCellContract
    model_id: str
    refinement: int
    ledger: S1UComponentLedgerResult
    classification_allowed: bool = False
    runtime_writeback_allowed: bool = False
    memory_claim_allowed: bool = False
    field_time_claim_allowed: bool = False


def _form_id(source_form: str) -> str:
    return "repeated" if source_form == "repeated-supports" else "continuous"


def _time_id(value: float) -> str:
    return format(value, ".3f").replace(".", "p")


def s1v_ledger_inventory() -> tuple[S1VLedgerCellContract, ...]:
    values = []
    for dose in S1R_DOSE_COUNTS:
        for source_form in S1R_SOURCE_FORMS:
            for end in S1V_EARLY_CUMULATIVE_ENDS:
                values.append(
                    S1VLedgerCellContract(
                        (
                            f"s1v.d{dose}.{_form_id(source_form)}."
                            f"cumulative-{_time_id(end)}"
                        ),
                        dose,
                        source_form,
                        "early-cumulative",
                        0.0,
                        end,
                    )
                )
            for start, end in S1V_LATE_INTERVALS:
                values.append(
                    S1VLedgerCellContract(
                        (
                            f"s1v.d{dose}.{_form_id(source_form)}."
                            f"interval-{_time_id(start)}-{_time_id(end)}"
                        ),
                        dose,
                        source_form,
                        "late-interval",
                        start,
                        end,
                    )
                )
    return tuple(values)


def _validated_cell(
    dose_count: int,
    source_form: str,
    ledger_role: str,
    start_seconds: float,
    end_seconds: float,
) -> S1VLedgerCellContract:
    for cell in s1v_ledger_inventory():
        if (
            cell.dose_count == dose_count
            and cell.source_form == source_form
            and cell.ledger_role == ledger_role
            and cell.start_seconds == start_seconds
            and cell.end_seconds == end_seconds
        ):
            return cell
    raise S1VFourCurveComponentMatrixError(
        "S1-V ledger cell is outside the preregistered inventory"
    )


def run_s1v_ledger_cell(
    model_id: str,
    dose_count: int,
    source_form: str,
    ledger_role: str,
    start_seconds: float,
    end_seconds: float,
    refinement: int,
) -> S1VLedgerCellMeasurement:
    """Run one fixed ledger cell without classifying the four curves."""

    if model_id not in S1V_MODELS:
        raise S1VFourCurveComponentMatrixError("S1-V model is not bound")
    if refinement not in S1V_REFINEMENTS:
        raise S1VFourCurveComponentMatrixError(
            "S1-V refinement must be 2 or 4"
        )
    cell = _validated_cell(
        dose_count,
        source_form,
        ledger_role,
        start_seconds,
        end_seconds,
    )
    if ledger_role == "early-cumulative":
        ledger = run_s1u_component_cell(
            model_id,
            dose_count,
            source_form,
            end_seconds,
            refinement,
        )
    else:
        ledger = run_s1u_component_late_interval(
            model_id,
            dose_count,
            source_form,
            start_seconds,
            end_seconds,
            refinement,
        )
    return S1VLedgerCellMeasurement(
        cell=cell,
        model_id=model_id,
        refinement=refinement,
        ledger=ledger,
    )


def s1v_four_curve_component_matrix_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (S1VLedgerCellContract, S1VLedgerCellMeasurement)
        for item in fields(cls)
    )
