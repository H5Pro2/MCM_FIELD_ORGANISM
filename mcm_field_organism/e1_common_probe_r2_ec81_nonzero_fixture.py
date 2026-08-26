"""S1-EC81 synthetic nonzero fixture for the EC80 scalar reducer."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    E1CommonProbeN2R2EC79StaticEvaluationContract,
)
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepProbeReceipt,
)
from .e1_common_probe_r2_ec80_scalar_contract import (
    E1CommonProbeR2EC80ScalarReceipt,
    build_e1_common_probe_r2_ec80_scalar_receipt,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC81NonzeroFixtureError(ValueError):
    """Raised when EC81 loses its fixed synthetic nonzero signature."""


S1_EC81_FIXTURE_ID = "e1.common-probe-r2-nonzero-fixture.s1ec81.v1"
S1_EC81_ROLE_LEVELS = (
    ("p0-reset-ab", 0.0, 0.0),
    ("p0-reset-ba", 1.0, 2.0),
    ("e1-active-ab", 2.0, 3.0),
    ("e1-active-ba", 5.0, 7.0),
    ("e1-probe-feedback-ablated-ab", 7.0, 8.0),
    ("e1-probe-feedback-ablated-ba", 11.0, 13.0),
    ("e1-formation-ablated-ab", 13.0, 15.0),
    ("e1-formation-ablated-ba", 18.0, 21.0),
)
S1_EC81_EXPECTED_SCALARS = (
    ("p0-reset-order", 1.0, 2.0),
    ("e1-active-order", 3.0, 4.0),
    ("e1-probe-feedback-ablated-order", 4.0, 5.0),
    ("e1-formation-ablated-order", 5.0, 6.0),
    ("ab-active-vs-probe-feedback-ablated", 5.0, 5.0),
    ("ba-active-vs-probe-feedback-ablated", 6.0, 6.0),
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC81NonzeroFixtureResult:
    fixture_id: str
    source_probe_receipt_digests: tuple[str, ...]
    injected_probe_receipt_digests: tuple[str, ...]
    expected_scalars: tuple[tuple[str, float, float], ...]
    observed_scalars: tuple[tuple[str, float, float], ...]
    all_six_contrasts_exact: bool
    activation_afterimage_separate: bool
    actual_field_steps_executed: int
    persistence_performed: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    scalar_receipt_digest: str
    result_digest: str
    scalar_receipt: E1CommonProbeR2EC80ScalarReceipt

    def __post_init__(self) -> None:
        if (
            self.fixture_id != S1_EC81_FIXTURE_ID
            or len(self.source_probe_receipt_digests) != 8
            or len(self.injected_probe_receipt_digests) != 8
            or self.expected_scalars != S1_EC81_EXPECTED_SCALARS
            or self.observed_scalars != S1_EC81_EXPECTED_SCALARS
            or self.all_six_contrasts_exact is not True
            or self.activation_afterimage_separate is not True
            or self.actual_field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.scalar_receipt_digest != self.scalar_receipt.receipt_digest
        ):
            raise E1CommonProbeR2EC81NonzeroFixtureError(
                "S1-EC81 synthetic nonzero result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"scalar_receipt", "result_digest"}
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeR2EC81NonzeroFixtureError(
                "S1-EC81 result digest changed"
            )


def _inject_nonzero_receipt(
    receipt: E1PositiveStepProbeReceipt,
    activation_level: float,
    afterimage_level: float,
) -> E1PositiveStepProbeReceipt:
    values = {
        name: getattr(receipt, name)
        for name in receipt.__dataclass_fields__
        if name not in {"activation", "afterimage", "receipt_digest"}
    }
    values["activation"] = (activation_level, activation_level / 10.0)
    values["afterimage"] = (afterimage_level, afterimage_level / 10.0)
    return E1PositiveStepProbeReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def run_e1_common_probe_r2_ec81_nonzero_fixture(
    boundary: E1CommonProbeN2R2EC79StaticEvaluationContract,
    probes: tuple[E1PositiveStepProbeReceipt, ...],
) -> E1CommonProbeR2EC81NonzeroFixtureResult:
    """Inject fixed synthetic vectors and audit EC80 without field execution."""

    receipts = tuple(probes)
    levels = dict((role, (activation, afterimage)) for role, activation, afterimage in S1_EC81_ROLE_LEVELS)
    if tuple(item.role_id for item in receipts) != tuple(levels):
        raise E1CommonProbeR2EC81NonzeroFixtureError(
            "S1-EC81 requires all eight ordered source receipts"
        )
    injected = tuple(
        _inject_nonzero_receipt(item, *levels[item.role_id])
        for item in receipts
    )
    synthetic_source_digest = _digest(
        (S1_EC81_FIXTURE_ID, tuple(item.receipt_digest for item in injected))
    )
    scalar = build_e1_common_probe_r2_ec80_scalar_receipt(
        boundary,
        injected,
        source_result_digest=synthetic_source_digest,
    )
    values = {
        "fixture_id": S1_EC81_FIXTURE_ID,
        "source_probe_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "injected_probe_receipt_digests": tuple(item.receipt_digest for item in injected),
        "expected_scalars": S1_EC81_EXPECTED_SCALARS,
        "observed_scalars": scalar.contrast_scalars,
        "all_six_contrasts_exact": scalar.contrast_scalars == S1_EC81_EXPECTED_SCALARS,
        "activation_afterimage_separate": all(
            observed[1:] == expected[1:]
            for observed, expected in zip(
                scalar.contrast_scalars, S1_EC81_EXPECTED_SCALARS, strict=True
            )
        ),
        "actual_field_steps_executed": 0,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "scalar_receipt_digest": scalar.receipt_digest,
    }
    return E1CommonProbeR2EC81NonzeroFixtureResult(
        **values,
        result_digest=_digest(values),
        scalar_receipt=scalar,
    )
