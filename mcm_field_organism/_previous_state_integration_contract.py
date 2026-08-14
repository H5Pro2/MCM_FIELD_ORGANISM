"""Private, execution-locked contract between fixation and minimal runner."""

from __future__ import annotations

from dataclasses import dataclass

from ._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    _LockedRunnerManifest,
)
from ._runtime_fixation_structure import _FixedDigestBundle, _FixedDigestEntry


_STAGE_KINDS = (
    "measurement",
    "contact",
    "contact",
    "contact",
    "measurement",
    "operator_boundary",
    "measurement",
    "contact",
    "measurement",
)
_MEASUREMENT_IDS = ("M0", "M1", "M2", "M3")


@dataclass(frozen=True, slots=True)
class _IntegrationStage:
    kind: str
    stage_id: str
    digest_gate: _FixedDigestEntry | None = None


@dataclass(frozen=True, slots=True)
class _ArmIntegrationContract:
    run_id: str
    arm_id: str
    history_id: str
    previous_state_operator: str | None
    freshness_token: str
    stages: tuple[_IntegrationStage, ...]

    def __post_init__(self) -> None:
        if tuple(stage.kind for stage in self.stages) != _STAGE_KINDS:
            raise PreviousStateMinimalRunnerError("integration stage order changed")
        measurements = tuple(
            stage.stage_id for stage in self.stages if stage.kind == "measurement"
        )
        if measurements != _MEASUREMENT_IDS:
            raise PreviousStateMinimalRunnerError("integration measurements changed")
        operator = self.stages[5]
        if operator.stage_id != (self.previous_state_operator or "none"):
            raise PreviousStateMinimalRunnerError("integration operator boundary changed")
        for stage in self.stages:
            if (stage.kind == "contact") != (stage.digest_gate is not None):
                raise PreviousStateMinimalRunnerError("integration digest gate changed")


@dataclass(frozen=True, slots=True)
class _PrivateIntegrationContract:
    arms: tuple[_ArmIntegrationContract, ...]
    execution_locked: bool = True
    field_execution_allowed: bool = False
    hook_execution_allowed: bool = False
    effect_measurement_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.execution_locked or any(
            (
                self.field_execution_allowed,
                self.hook_execution_allowed,
                self.effect_measurement_allowed,
            )
        ):
            raise PreviousStateMinimalRunnerError("integration contract must remain locked")
        if len(self.arms) != 24:
            raise PreviousStateMinimalRunnerError("integration arm count changed")
        run_ids = tuple(arm.run_id for arm in self.arms)
        freshness_tokens = tuple(arm.freshness_token for arm in self.arms)
        if len(set(run_ids)) != 24 or freshness_tokens != run_ids:
            raise PreviousStateMinimalRunnerError("integration freshness contract changed")


@dataclass(frozen=True, slots=True)
class _StaticContactObservation:
    run_id: str
    freshness_token: str
    contact_id: str
    receptor_distribution_digest: str
    generator_digest: str
    boundary_digest: str


def _contact_stages(
    contact_ids: tuple[str, ...],
    digest_by_contact: dict[str, _FixedDigestEntry],
    operator: str | None,
) -> tuple[_IntegrationStage, ...]:
    first, second, third, current = contact_ids
    return (
        _IntegrationStage("measurement", "M0"),
        _IntegrationStage("contact", first, digest_by_contact[first]),
        _IntegrationStage("contact", second, digest_by_contact[second]),
        _IntegrationStage("contact", third, digest_by_contact[third]),
        _IntegrationStage("measurement", "M1"),
        _IntegrationStage("operator_boundary", operator or "none"),
        _IntegrationStage("measurement", "M2"),
        _IntegrationStage("contact", current, digest_by_contact[current]),
        _IntegrationStage("measurement", "M3"),
    )


def _build_private_integration_contract(
    bundle: _FixedDigestBundle,
    manifest: _LockedRunnerManifest,
) -> _PrivateIntegrationContract:
    if not isinstance(bundle, _FixedDigestBundle) or not isinstance(
        manifest, _LockedRunnerManifest
    ):
        raise PreviousStateMinimalRunnerError("private integration contract invalid")
    try:
        _FixedDigestBundle(
            entries=bundle.entries,
            schema_version=bundle.schema_version,
            source_digests=bundle.source_digests,
            static_contract=bundle.static_contract,
        )
    except Exception:
        raise PreviousStateMinimalRunnerError(
            "private integration contract invalid"
        ) from None
    if not manifest.execution_locked or any(
        (
            manifest.field_construction_allowed,
            manifest.receptor_distribution_allowed,
            manifest.integrator_execution_allowed,
            manifest.effect_measurement_allowed,
        )
    ):
        raise PreviousStateMinimalRunnerError("private integration contract invalid")

    digest_by_contact = {entry.contact_id: entry for entry in bundle.entries}
    expected_contacts = tuple(
        contact.snapshot_id
        for contact in (*manifest.input_a, *manifest.input_b, *manifest.input_c)
    )
    if tuple(digest_by_contact) != expected_contacts:
        raise PreviousStateMinimalRunnerError("private integration contract invalid")

    histories = {
        "A": tuple(contact.snapshot_id for contact in manifest.input_a),
        "B": tuple(contact.snapshot_id for contact in manifest.input_b),
    }
    current = tuple(contact.snapshot_id for contact in manifest.input_c)
    if len(current) != 1:
        raise PreviousStateMinimalRunnerError("private integration contract invalid")

    arms = tuple(
        _ArmIntegrationContract(
            run_id=arm.run_id,
            arm_id=arm.arm_id,
            history_id=arm.history_id,
            previous_state_operator=arm.previous_state_operator,
            freshness_token=arm.run_id,
            stages=_contact_stages(
                (*histories[arm.history_id], current[0]),
                digest_by_contact,
                arm.previous_state_operator,
            ),
        )
        for arm in manifest.arms
    )
    return _PrivateIntegrationContract(arms=arms)


def _verify_static_contact_observations(
    contract: _PrivateIntegrationContract,
    observations: tuple[_StaticContactObservation, ...],
) -> None:
    """Verify only static order, freshness and digest gates; expose no result."""

    if not isinstance(contract, _PrivateIntegrationContract):
        raise PreviousStateMinimalRunnerError("static integration verification failed")
    expected = tuple(
        (arm, stage)
        for arm in contract.arms
        for stage in arm.stages
        if stage.kind == "contact"
    )
    if len(observations) != len(expected):
        raise PreviousStateMinimalRunnerError("static integration verification failed")
    seen_freshness: dict[str, str] = {}
    try:
        for observation, (arm, stage) in zip(observations, expected, strict=True):
            gate = stage.digest_gate
            if not isinstance(observation, _StaticContactObservation) or gate is None:
                raise ValueError
            previous = seen_freshness.setdefault(arm.run_id, observation.freshness_token)
            if previous != observation.freshness_token:
                raise ValueError
            if (
                observation.run_id != arm.run_id
                or observation.freshness_token != arm.freshness_token
                or observation.contact_id != stage.stage_id
                or observation.receptor_distribution_digest
                != gate.receptor_distribution_digest
                or observation.generator_digest != gate.generator_digest
                or observation.boundary_digest != gate.boundary_digest
            ):
                raise ValueError
    except Exception:
        raise PreviousStateMinimalRunnerError(
            "static integration verification failed"
        ) from None
