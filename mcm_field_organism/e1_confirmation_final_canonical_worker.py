"""Private S1-EB31 final canonical one-shot worker and guarded launcher."""

from __future__ import annotations

import argparse
import copy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from .e1_confirmation_canonical_dataflow_contract import (
    prepare_e1_confirmation_canonical_dataflow_contract,
)
from .e1_confirmation_canonical_formation_adapter import (
    produce_e1_confirmation_canonical_formation,
)
from .e1_confirmation_canonical_gate_transition_contract import (
    prepare_e1_confirmation_canonical_gate_transition_contract,
)
from .e1_confirmation_canonical_probe_adapter import (
    run_e1_confirmation_canonical_seven_arm_probe,
)
from .e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from .e1_confirmation_canonical_report_handoff import (
    prepare_e1_confirmation_canonical_report_handoff,
)
from .e1_confirmation_canonical_result_compositor import (
    compose_e1_confirmation_canonical_result,
)
from .e1_confirmation_canonical_result_handoff import (
    prepare_e1_confirmation_canonical_result_handoff,
)
from .e1_confirmation_canonical_worker_binding import (
    bind_e1_confirmation_canonical_worker_functions,
)
from .e1_confirmation_chain_contract import S1_EB4_REPORT_FIELDS
from .e1_confirmation_final_go_no_go_audit import (
    audit_e1_confirmation_final_go_no_go,
)
from .e1_confirmation_one_shot_worker import _prepare_worker_inputs
from .e1_confirmation_released_worker_audit import (
    audit_e1_confirmation_released_worker_contract,
)
from .e1_confirmation_resource_guard import (
    E1ConfirmationGuardedProcessResult,
    E1ConfirmationResourceGuardBinding,
    run_guarded_synthetic_process,
)
from .e1_confirmation_same_session_preflight import (
    prepare_e1_confirmation_same_session_preflight,
    require_fresh_e1_confirmation_preflight,
)


class E1ConfirmationFinalCanonicalWorkerError(RuntimeError):
    """Raised when the final one-shot cannot preserve its release contract."""


S1_EB30_AUDIT_DIGEST = (
    "1bd5bdb972a12e3ac114715451381481a4a8d03a477b585d60d82eb33a3974f8"
)


def _exclusive_marker(path: Path, payload: dict[str, object]) -> None:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise E1ConfirmationFinalCanonicalWorkerError(
            f"S1-EB31 one-shot marker already exists: {path.name}"
        ) from exc


def _atomic_publish(target: Path, payload: dict[str, object]) -> bytes:
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
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".tmp.", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if json.loads(temporary.read_text(encoding="ascii")) != json.loads(
            encoded
        ):
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 temporary report verification failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 canonical report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 published report differs from its payload"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def _released_copy(value, **opened_gates):
    released = copy.deepcopy(value)
    for role, state in opened_gates.items():
        if state is not True or getattr(released, role) is not False:
            raise E1ConfirmationFinalCanonicalWorkerError(
                f"S1-EB31 invalid gate transition: {role}"
            )
        object.__setattr__(released, role, True)
    return released


def _prepare_final_chain():
    binding, chain, release, authorization, guard = _prepare_worker_inputs()
    released = audit_e1_confirmation_released_worker_contract(
        binding, chain, release, authorization, guard
    )
    function_binding = bind_e1_confirmation_canonical_worker_functions(
        released
    )
    dataflow = prepare_e1_confirmation_canonical_dataflow_contract(
        function_binding
    )
    transitions = prepare_e1_confirmation_canonical_gate_transition_contract(
        dataflow
    )
    final_audit = audit_e1_confirmation_final_go_no_go(released, transitions)
    if final_audit.audit_digest != S1_EB30_AUDIT_DIGEST:
        raise E1ConfirmationFinalCanonicalWorkerError(
            "S1-EB31 final GO audit changed"
        )
    return (
        binding,
        chain,
        release,
        authorization,
        guard,
        final_audit,
    )


def _canonical_report(chain, result) -> dict[str, object]:
    report = {
        "execution_id": chain.execution_id,
        "confirmation_contract_digest": chain.confirmation_contract_digest,
        "canonical_preflight_digest": chain.canonical_preflight_digest,
        "implementation_digests": chain.implementation_digests,
        "source_digests": (
            chain.history_ab_digest,
            chain.history_ba_digest,
            chain.permutation_digest,
            chain.probe_digest,
        ),
        "plan_digests": (
            chain.ab_plan_digest,
            chain.ba_plan_digest,
            chain.probe_plan_digest,
        ),
        "refinement_result_digests": tuple(
            (item.refinement_id, item.digest()) for item in result.refinements
        ),
        "result_digest": result.result_digest,
        "technical_decision": result.technical_decision,
        "metrics": result.metrics,
        "controls": result.controls,
        "result": asdict(result),
    }
    if tuple(report) != S1_EB4_REPORT_FIELDS:
        raise E1ConfirmationFinalCanonicalWorkerError(
            "S1-EB31 canonical report field order changed"
        )
    return report


def execute_final_canonical_worker_in_child() -> dict[str, object]:
    """Consume the authorization by starting the canonical chain once."""

    binding, chain, release, authorization, guard, final_audit = (
        _prepare_final_chain()
    )
    targets = tuple(Path(value) for value in chain._target_path_values())
    if any(path.exists() for path in targets):
        raise E1ConfirmationFinalCanonicalWorkerError(
            "S1-EB31 canonical one-shot target is already used"
        )
    report_path, attempt_path, lock_path = targets
    preflight = prepare_e1_confirmation_same_session_preflight(
        binding, chain, release, authorization, guard
    )
    require_fresh_e1_confirmation_preflight(preflight)
    _exclusive_marker(
        lock_path,
        {
            "execution_id": chain.execution_id,
            "final_audit_digest": final_audit.audit_digest,
            "preflight_digest": preflight.preflight_digest,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt_path,
            {
                "execution_id": chain.execution_id,
                "final_audit_digest": final_audit.audit_digest,
                "preflight_digest": preflight.preflight_digest,
                "failure_policy": "retain-attempt-marker-no-automatic-retry",
            },
        )
        attempt_created = True

        formation = produce_e1_confirmation_canonical_formation(
            binding, chain
        )
        probe_handoff = prepare_e1_confirmation_canonical_probe_handoff(
            binding, chain, formation
        )
        released_probe_handoff = _released_copy(
            probe_handoff, probe_execution_permitted=True
        )
        probes = run_e1_confirmation_canonical_seven_arm_probe(
            binding, chain, formation, released_probe_handoff
        )
        if tuple(item.refinement_id for item in probes) != ("r2", "r4", "r8"):
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 probe results are not ordered r2/r4/r8"
            )
        result_handoff = prepare_e1_confirmation_canonical_result_handoff(
            binding, chain, formation, probe_handoff, probes
        )
        released_result_handoff = _released_copy(
            result_handoff, result_composition_permitted=True
        )
        result = compose_e1_confirmation_canonical_result(
            binding,
            chain,
            formation,
            probe_handoff,
            released_result_handoff,
            probes,
        )
        report_handoff = prepare_e1_confirmation_canonical_report_handoff(
            binding, chain, result_handoff, result
        )
        released_report_handoff = _released_copy(
            report_handoff,
            execution_permitted=True,
            persistence_permitted=True,
        )
        if (
            released_report_handoff.retry_permitted is not False
            or released_report_handoff.claims_permitted is not False
            or released_report_handoff.result_digest != result.result_digest
        ):
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 report release boundary changed"
            )
        report = _canonical_report(chain, result)
        encoded = _atomic_publish(report_path, report)
        report_sha256 = hashlib.sha256(encoded).hexdigest()
        if (
            hashlib.sha256(report_path.read_bytes()).hexdigest()
            != report_sha256
            or json.loads(report_path.read_text(encoding="ascii"))
            != json.loads(encoded)
        ):
            raise E1ConfirmationFinalCanonicalWorkerError(
                "S1-EB31 final report reread failed"
            )
        attempt_path.unlink()
        return {
            "status": "CANONICAL_ONE_SHOT_COMPLETE",
            "execution_id": chain.execution_id,
            "report_path": str(report_path.resolve()),
            "report_sha256": report_sha256,
            "result_digest": result.result_digest,
            "technical_decision": result.technical_decision,
            "preflight_digest": preflight.preflight_digest,
            "final_audit_digest": final_audit.audit_digest,
            "retry_permitted": False,
            "claims_permitted": False,
        }
    finally:
        lock_path.unlink(missing_ok=True)
        if not attempt_created:
            attempt_path.unlink(missing_ok=True)


def launch_final_canonical_worker_once(
    guard: E1ConfirmationResourceGuardBinding,
) -> E1ConfirmationGuardedProcessResult:
    """Launch the final child exactly once under the bound resource guard."""

    if (
        not isinstance(guard, E1ConfirmationResourceGuardBinding)
        or guard.max_wall_seconds != 1_800
        or guard.max_peak_rss_bytes != 4 * 1024**3
        or guard.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationFinalCanonicalWorkerError(
            "S1-EB31 resource guard changed"
        )
    return run_guarded_synthetic_process(
        (
            sys.executable,
            "-m",
            "mcm_field_organism.e1_confirmation_final_canonical_worker",
            "--execute-canonical-once",
        ),
        Path(__file__).parents[1],
        max_wall_seconds=guard.max_wall_seconds,
        max_peak_rss_bytes=guard.max_peak_rss_bytes,
    )


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--execute-canonical-once", action="store_true")
    args = parser.parse_args(argv)
    if not args.execute_canonical_once:
        raise E1ConfirmationFinalCanonicalWorkerError(
            "S1-EB31 explicit canonical one-shot flag is required"
        )
    receipt = execute_final_canonical_worker_in_child()
    print(
        json.dumps(
            receipt,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
