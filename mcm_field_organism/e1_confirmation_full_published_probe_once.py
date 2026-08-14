"""Private S1-EC23 exactly-once probe of persistent S1-EC19 states."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Callable

from .e1_confirmation_full_formation_handoff import (
    E1PreparedFullFormationResult,
    load_full_formation_handoff_payload,
)
from .e1_confirmation_full_probe_release_audit import (
    E1FullProbeReleaseDecision,
    E1FullProbeResourceSnapshot,
    S1_EC22_ATTEMPT_NAME,
    S1_EC22_LOCK_NAME,
    S1_EC22_MAX_REPORT_BYTES,
    S1_EC22_MAX_RUNTIME_SECONDS,
    S1_EC22_RELEASE_TARGET_ID,
    S1_EC22_REPORT_NAME,
)
from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    _atomic_publish,
    _exclusive_marker,
)
from .e1_confirmation_prepared_formation_consumer import _typed_values_from_bundle
from .e1_confirmation_published_probe_fixture_consumer import (
    E1PublishedProbeFixtureRefinementResult,
    _refinement_residual,
    _run_refinement_fixture,
)
from .e1_confirmation_published_probe_handoff_audit import (
    E1PublishedProbeHandoffAudit,
    S1_EC20_REFINEMENTS,
)
from .e1_frozen_state_transfer import _state_payload
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullPublishedProbeOnceError(RuntimeError):
    """Raised when the S1-EC23 persistent full probe fails closed."""


S1_EC23_SCHEMA_ID = "e1.full-published-probe.s1ec23.once.v1"
S1_EC23_FAILURE_POLICY = "retain-attempt-marker-no-automatic-retry"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FullPublishedProbeRawResult:
    source_report_sha256: str
    source_formation_result_digest: str
    probe_source_digest: str
    probe_plan_set_digest: str
    source_state_digests_before: tuple[tuple[str, str], ...]
    source_state_digests_after: tuple[tuple[str, str], ...]
    refinements: tuple[E1PublishedProbeFixtureRefinementResult, ...]
    r2_r4_probe_residual: float
    r4_r8_probe_residual: float
    convergence_nonincreasing: bool
    all_registered_controls_passed: bool
    persistent_states_consumed: bool
    registered_probe_consumed: bool
    result_decision_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        numeric = (self.r2_r4_probe_residual, self.r4_r8_probe_residual)
        if (
            any(
                not _valid_digest(value)
                for value in (
                    self.source_report_sha256,
                    self.source_formation_result_digest,
                    self.probe_source_digest,
                    self.probe_plan_set_digest,
                    self.result_digest,
                )
            )
            or tuple(item.refinement_id for item in refinements)
            != S1_EC20_REFINEMENTS
            or self.source_state_digests_before != self.source_state_digests_after
            or len(self.source_state_digests_before) != 15
            or any(
                not role or not _valid_digest(value)
                for role, value in self.source_state_digests_before
            )
            or any(not math.isfinite(value) or value < 0.0 for value in numeric)
            or self.convergence_nonincreasing
            is not (self.r4_r8_probe_residual <= self.r2_r4_probe_residual)
            or self.all_registered_controls_passed is not True
            or self.persistent_states_consumed is not True
            or self.registered_probe_consumed is not True
            or self.result_decision_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 raw result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"refinements", "result_digest"}
        }
        payload["refinement_result_digests"] = tuple(
            item.result_digest for item in refinements
        )
        if self.result_digest != _digest(payload):
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 raw result digest changed"
            )
        object.__setattr__(self, "refinements", refinements)


def _state_digests(formation: E1PreparedFullFormationResult):
    return tuple(
        (
            f"{refinement.refinement_id}:{arm.arm_id}",
            _digest(_state_payload(arm.output_state)),
        )
        for refinement in formation.refinements
        for arm in refinement.arms
    )


def run_full_persistent_probe(
    handoff: E1PublishedProbeHandoffAudit,
    bundle: E1PreparedExecutionBundle,
    formation: E1PreparedFullFormationResult,
    runtime_guard: Callable[[], None],
) -> E1FullPublishedProbeRawResult:
    """Run registered plans against loaded frozen states without deciding."""

    if not callable(runtime_guard):
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 requires one runtime guard"
        )
    values = _typed_values_from_bundle(bundle)
    before = _state_digests(formation)
    if before != handoff.all_state_digests:
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 loaded state inventory changed"
        )
    results = tuple(
        _run_refinement_fixture(
            refinement,
            plan,
            values.initial_field,
            runtime_guard=runtime_guard,
        )
        for refinement, plan in zip(
            formation.refinements,
            values.probe_plans.plans,
            strict=True,
        )
    )
    after = _state_digests(formation)
    r2_r4 = _refinement_residual(results[0], results[1])
    r4_r8 = _refinement_residual(results[1], results[2])
    payload = {
        "source_report_sha256": handoff.report_sha256,
        "source_formation_result_digest": formation.result_digest,
        "probe_source_digest": handoff.probe_source_digest,
        "probe_plan_set_digest": handoff.probe_plan_set_digest,
        "source_state_digests_before": before,
        "source_state_digests_after": after,
        "r2_r4_probe_residual": r2_r4,
        "r4_r8_probe_residual": r4_r8,
        "convergence_nonincreasing": r4_r8 <= r2_r4,
        "all_registered_controls_passed": all(
            item.probe_ablation_residual == 0.0
            and item.fixed_adapter_residual == 0.0
            and item.frozen_state_change == 0.0
            and item.initial_fields_identical_and_separate
            and item.supports_assigned_once
            for item in results
        ),
        "persistent_states_consumed": True,
        "registered_probe_consumed": True,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    digest_payload = dict(payload)
    digest_payload["refinement_result_digests"] = tuple(
        item.result_digest for item in results
    )
    return E1FullPublishedProbeRawResult(
        **payload,
        refinements=results,
        result_digest=_digest(digest_payload),
    )


def _raw_payload(result: E1FullPublishedProbeRawResult) -> dict[str, object]:
    payload = asdict(result)
    return payload


def load_full_published_probe_raw_result(
    payload: object,
) -> E1FullPublishedProbeRawResult:
    """Typed-reload S1-EC23 raw metrics without a research decision."""

    if not isinstance(payload, dict):
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 raw payload is invalid"
        )
    try:
        refinements = tuple(
            E1PublishedProbeFixtureRefinementResult(
                refinement_id=item["refinement_id"],
                field_digests=tuple(tuple(value) for value in item["field_digests"]),
                ab_active_s=tuple(item["ab_active_s"]),
                ba_active_s=tuple(item["ba_active_s"]),
                ab_active_h=tuple(item["ab_active_h"]),
                ba_active_h=tuple(item["ba_active_h"]),
                active_s_linf=item["active_s_linf"],
                active_h_linf=item["active_h_linf"],
                probe_ablation_residual=item["probe_ablation_residual"],
                fixed_adapter_residual=item["fixed_adapter_residual"],
                frozen_state_change=item["frozen_state_change"],
                initial_fields_identical_and_separate=item[
                    "initial_fields_identical_and_separate"
                ],
                supports_assigned_once=item["supports_assigned_once"],
                result_digest=item["result_digest"],
            )
            for item in payload["refinements"]
        )
        return E1FullPublishedProbeRawResult(
            source_report_sha256=payload["source_report_sha256"],
            source_formation_result_digest=payload[
                "source_formation_result_digest"
            ],
            probe_source_digest=payload["probe_source_digest"],
            probe_plan_set_digest=payload["probe_plan_set_digest"],
            source_state_digests_before=tuple(
                tuple(item) for item in payload["source_state_digests_before"]
            ),
            source_state_digests_after=tuple(
                tuple(item) for item in payload["source_state_digests_after"]
            ),
            refinements=refinements,
            r2_r4_probe_residual=payload["r2_r4_probe_residual"],
            r4_r8_probe_residual=payload["r4_r8_probe_residual"],
            convergence_nonincreasing=payload["convergence_nonincreasing"],
            all_registered_controls_passed=payload[
                "all_registered_controls_passed"
            ],
            persistent_states_consumed=payload["persistent_states_consumed"],
            registered_probe_consumed=payload["registered_probe_consumed"],
            result_decision_permitted=payload["result_decision_permitted"],
            claims_permitted=payload["claims_permitted"],
            result_digest=payload["result_digest"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 raw payload cannot be reconstructed"
        ) from exc


ProbeRunner = Callable[
    [E1PublishedProbeHandoffAudit, E1PreparedExecutionBundle,
     E1PreparedFullFormationResult, Callable[[], None]],
    E1FullPublishedProbeRawResult,
]


@dataclass(frozen=True, slots=True)
class E1FullPublishedProbeReceipt:
    execution_id: str
    release_decision_digest: str
    raw_result_digest: str
    report_path: str
    report_sha256: str
    report_bytes: int
    runtime_seconds: float
    final_reread_verified: bool
    typed_reload_verified: bool
    attempt_removed_after_verification: bool
    lock_released: bool
    result_decision_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != S1_EC22_RELEASE_TARGET_ID
            or not _valid_digest(self.release_decision_digest)
            or not _valid_digest(self.raw_result_digest)
            or Path(self.report_path).name != S1_EC22_REPORT_NAME
            or not _valid_digest(self.report_sha256)
            or not 0 < self.report_bytes <= S1_EC22_MAX_REPORT_BYTES
            or not 0.0 <= self.runtime_seconds <= S1_EC22_MAX_RUNTIME_SECONDS
            or self.final_reread_verified is not True
            or self.typed_reload_verified is not True
            or self.attempt_removed_after_verification is not True
            or self.lock_released is not True
            or self.result_decision_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 receipt changed"
            )


def execute_full_published_probe_once(
    release: E1FullProbeReleaseDecision,
    snapshot: E1FullProbeResourceSnapshot,
    handoff: E1PublishedProbeHandoffAudit,
    bundle: E1PreparedExecutionBundle,
    source_report_path: Path,
    directory: Path,
    *,
    owner_authorized: bool,
    probe_runner: ProbeRunner = run_full_persistent_probe,
) -> E1FullPublishedProbeReceipt:
    """Run and publish raw full-probe metrics exactly once."""

    release.__post_init__()
    snapshot.__post_init__()
    handoff.__post_init__()
    bundle.__post_init__()
    if (
        release.decision != "FREIGABE"
        or owner_authorized is not True
        or not callable(probe_runner)
        or release.handoff_audit_digest != handoff.audit_digest
        or release.resource_snapshot_digest != snapshot.digest()
    ):
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 is not authorized or aligned"
        )
    source = Path(source_report_path).resolve()
    root = Path(directory).resolve()
    report = root / S1_EC22_REPORT_NAME
    attempt = root / S1_EC22_ATTEMPT_NAME
    lock = root / S1_EC22_LOCK_NAME
    if (
        root != Path(snapshot.proposed_directory).resolve()
        or root == Path("reports").resolve()
        or any(path.exists() for path in (report, attempt, lock))
        or not source.is_file()
        or hashlib.sha256(source.read_bytes()).hexdigest()
        != snapshot.s1ec19_report_sha256
    ):
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 source or target paths changed"
        )
    root.mkdir(parents=False, exist_ok=True)
    source_payload = json.loads(source.read_text(encoding="ascii"))
    formation = load_full_formation_handoff_payload(source_payload["payload"])
    if formation.result_digest != handoff.formation_result_digest:
        raise E1ConfirmationFullPublishedProbeOnceError(
            "S1-EC23 source formation changed"
        )

    started = time.monotonic()

    def runtime_guard() -> None:
        if time.monotonic() - started > S1_EC22_MAX_RUNTIME_SECONDS:
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 runtime cap exceeded"
            )

    _exclusive_marker(
        lock,
        {
            "execution_id": S1_EC22_RELEASE_TARGET_ID,
            "release_decision_digest": release.decision_digest,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": S1_EC22_RELEASE_TARGET_ID,
                "release_decision_digest": release.decision_digest,
                "failure_policy": S1_EC23_FAILURE_POLICY,
            },
        )
        attempt_created = True
        raw = probe_runner(handoff, bundle, formation, runtime_guard)
        if not isinstance(raw, E1FullPublishedProbeRawResult):
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 runner returned no typed raw result"
            )
        raw.__post_init__()
        runtime_guard()
        payload = {
            "schema_id": S1_EC23_SCHEMA_ID,
            "execution_id": S1_EC22_RELEASE_TARGET_ID,
            "release_policy_digest": release.policy_digest,
            "release_decision_digest": release.decision_digest,
            "resource_snapshot": asdict(snapshot),
            "resource_snapshot_digest": snapshot.digest(),
            "handoff_audit_digest": handoff.audit_digest,
            "raw_result_digest": raw.result_digest,
            "raw_result": _raw_payload(raw),
            "runtime_seconds": time.monotonic() - started,
            "owner_authorized": True,
            "result_decision_permitted": False,
            "claims_permitted": False,
        }
        encoded = (
            json.dumps(
                payload,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=False,
            )
            + "\n"
        ).encode("ascii")
        if len(encoded) > S1_EC22_MAX_REPORT_BYTES:
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 report size cap exceeded"
            )
        published = _atomic_publish(report, payload)
        if published != encoded:
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 publication encoding changed"
            )
        report_sha256 = hashlib.sha256(published).hexdigest()
        reread = report.read_bytes()
        decoded = json.loads(reread.decode("ascii"))
        if (
            hashlib.sha256(reread).hexdigest() != report_sha256
            or decoded["raw_result_digest"] != raw.result_digest
        ):
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 final reread failed"
            )
        loaded = load_full_published_probe_raw_result(decoded["raw_result"])
        if loaded.result_digest != raw.result_digest:
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 typed reload changed raw metrics"
            )
        if hashlib.sha256(source.read_bytes()).hexdigest() != handoff.report_sha256:
            raise E1ConfirmationFullPublishedProbeOnceError(
                "S1-EC23 changed the protected source report"
            )
        runtime_seconds = time.monotonic() - started
        runtime_guard()
        attempt.unlink()
        return E1FullPublishedProbeReceipt(
            execution_id=S1_EC22_RELEASE_TARGET_ID,
            release_decision_digest=release.decision_digest,
            raw_result_digest=raw.result_digest,
            report_path=str(report),
            report_sha256=report_sha256,
            report_bytes=len(published),
            runtime_seconds=runtime_seconds,
            final_reread_verified=True,
            typed_reload_verified=True,
            attempt_removed_after_verification=True,
            lock_released=True,
            result_decision_permitted=False,
            claims_permitted=False,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
