"""Private one-shot S1-UK synthetic ACM-1H comparison matrix."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from ._acm1h_field_runtime import (
    _advance_with_generator,
    _field_digest,
    advance_acm1h_four_node_field,
    advance_acm1h_off_four_node_field,
    build_acm1h_field_carry,
)
from ._acm1h_reference import (
    ACM1H_EDGES,
    ACM1H_NODE_IDS,
    ACM1H_PARAMETER_CANDIDATES,
    ACM1HConfigRecord,
    ACM1HPrestateRecord,
    acm1h_edge_inventory_digest,
    run_acm1h_reference,
)
from .e1_coupled_fast_field import advance_e1_coupled_fast_shared_field
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    advance_e1_local_edge_plasticity,
    build_neutral_e1_state,
)
from .field_step_time import MCMFieldStepTime
from .four_node_fresh_factory import build_four_node_public_fresh_field
from .four_node_fresh_manifest import load_four_node_fresh_manifest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock


S1UK_SCHEMA_ID = "mcm.s1uk.acm1h-33-path-result.v1"
S1UK_OUTCOMES = (
    "ACM1H_TECHNICAL_RELATIONAL_RESIDUAL",
    "EXPLAINED_BY_BASELINE",
    "COMPARISON_METHOD_INVALID",
)
HISTORIES = {
    "G": ((1.0, 0.5, 0.0, 0.0), (0.0, 0.5, 1.0, 1.0)),
    "O": ((1.0, 0.5, 1.0, 1.0), (0.0, 0.5, 0.0, 0.0)),
}
PROBE_S = (1.0, 0.5, 0.0, 0.0)
SUBSTRATE = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE = NeutralFastAfterimageConfig(0.5)


class S1UKMatrixError(ValueError):
    """Raised when the bound private matrix cannot be executed exactly once."""


def _digest(payload: object) -> str:
    raw = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def s1uk_path_plan() -> tuple[dict[str, object], ...]:
    """Return the immutable 33-path plan without executing a field step."""

    paths: list[dict[str, object]] = []
    for gamma_z, beta in ACM1H_PARAMETER_CANDIDATES:
        config_id = _config_id(gamma_z, beta)
        for history in ("G", "O", "Z0"):
            paths.append({"family": "ACM1H", "history": history, "config": config_id})
    for gamma_z, beta in ACM1H_PARAMETER_CANDIDATES:
        config_id = _config_id(gamma_z, beta)
        for history in ("G", "O"):
            paths.append({"family": "CGR1", "history": history, "config": config_id})
    paths.append({"family": "ACM_OFF", "history": "NONE", "config": "NONE"})
    paths.extend(
        {"family": "E1", "history": history, "config": "BOUND"}
        for history in ("G", "O")
    )
    return tuple(
        {"path_id": f"S1UK-{index:02d}", **path}
        for index, path in enumerate(paths, start=1)
    )


def _field_with_activations(field: Any, values: tuple[float, ...]):
    neurons = tuple(
        replace(neuron, activation=value, afterimage=0.0)
        for neuron, value in zip(field.layer.neurons, values, strict=True)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _distribution() -> Any:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.s1rf.technical-control.4n",
            "technical-control",
            "mcm.s1rf.receptor.4n",
        )
    )
    frame = ReceptorContactFrame(
        modality_id="technical-control",
        geometry_id="mcm.s1rf.receptor.4n",
        snapshot_id="s1uk.synthetic.zero-probe",
        clock_id="s1uk.synthetic.source",
        window_start_tick=0,
        window_end_tick=10,
        carrier_ids=("carrier-a", "carrier-b", "carrier-c", "carrier-d"),
        values=(0.0, 0.0, 0.0, 0.0),
    )
    return distributor.distribute(
        (frame,), CommonFieldTime("s1uk.synthetic.field", 0, 10)
    )


def _step() -> MCMFieldStepTime:
    return MCMFieldStepTime("s1uk.synthetic.field", 0, 10, 10.0)


def _prestate(
    values: tuple[float, ...], states: tuple[float, float]
) -> ACM1HPrestateRecord:
    return ACM1HPrestateRecord(
        "mcm.s1rf.field.4n",
        "mcm.s1rf.geometry.4n",
        ACM1H_NODE_IDS,
        values,
        (1.0, 1.0, 1.0),
        states,
        acm1h_edge_inventory_digest(),
        "s1uk.synthetic.field",
        0,
        10,
    )


def _formed_acm_state(config: ACM1HConfigRecord, history: str) -> tuple[float, float]:
    states = (0.0, 0.0)
    for values in HISTORIES[history]:
        decision = run_acm1h_reference(config, _prestate(values, states), _step())
        if decision.status != "COMPLETED":
            raise S1UKMatrixError(f"ACM state formation failed: {decision.error_code}")
        states = tuple(item.z_next for item in decision.motif_proposals)  # type: ignore[assignment]
    return states


def _values(field: Any, role: str) -> list[float]:
    return [float(getattr(neuron, role)) for neuron in field.layer.neurons]


def _record(
    path: dict[str, object], field_in: Any, field_out: Any, **extra: object
) -> dict[str, object]:
    return {
        **path,
        "input_field_digest": _field_digest(field_in),
        "S": _values(field_out, "activation"),
        "H": _values(field_out, "afterimage"),
        "output_field_digest": _field_digest(field_out),
        **extra,
    }


def _run_acm(path: dict[str, object], field: Any) -> dict[str, object]:
    gamma_z, beta = _config_values(str(path["config"]))
    config = ACM1HConfigRecord(gamma_z, beta)
    history = str(path["history"])
    states = (0.0, 0.0) if history == "Z0" else _formed_acm_state(config, history)
    decision = run_acm1h_reference(config, _prestate(PROBE_S, states), _step())
    if decision.status != "COMPLETED" or decision.composition is None:
        raise S1UKMatrixError("ACM probe proposal failed")
    carry = build_acm1h_field_carry(field, config, motif_states=states)
    result = advance_acm1h_four_node_field(
        carry, config, _distribution(), _step(), SUBSTRATE, AFTERIMAGE
    )
    return _record(
        path,
        field,
        result.field,
        state_marker=list(states),
        state_digest=carry.private_state_digest,
        edge_rates=list(decision.composition.composed_rates_per_second),
        z_next=[result.private_state.z_left, result.private_state.z_right],
        carry_role="PRIVATE_ACM1H",
    )


def _config_values(config_id: str) -> tuple[float, float]:
    left, right = config_id.split("_b", maxsplit=1)
    return float(left[1:]), float(right)


def _config_id(gamma_z: float, beta: float) -> str:
    return f"g{gamma_z:g}_b{beta:g}"


def _cgr_proposal(
    gamma_z: float, beta: float, states: tuple[float, float]
) -> tuple[tuple[float, ...], tuple[float, float], tuple[tuple[float, ...], ...]]:
    flows = (0.5, 0.5, 0.0)
    factors: list[float] = []
    next_states: list[float] = []
    for z_pre, first, second in ((states[0], flows[0], flows[1]), (states[1], flows[1], flows[2])):
        participation = min(abs(first), abs(second))
        if participation == 0.0:
            factors.append(1.0)
            next_states.append(z_pre)
        else:
            parity = 1.0 if first * second > 0.0 else -1.0
            theta = 1.0 - math.exp(-gamma_z * participation)
            factors.append(1.0 + beta * parity * z_pre)
            next_states.append((1.0 - theta) * z_pre + theta * parity)
    rates = (factors[0], factors[0] * factors[1], factors[1])
    generator = [[0.0] * 4 for _ in range(4)]
    for index, rate in enumerate(rates):
        generator[index][index + 1] += rate
        generator[index + 1][index] += rate
        generator[index][index] -= rate
        generator[index + 1][index + 1] -= rate
    return rates, (next_states[0], next_states[1]), tuple(tuple(row) for row in generator)


def _run_cgr(path: dict[str, object], field: Any) -> dict[str, object]:
    gamma_z, beta = _config_values(str(path["config"]))
    states = _formed_acm_state(ACM1HConfigRecord(gamma_z, beta), str(path["history"]))
    rates, next_states, generator = _cgr_proposal(gamma_z, beta, states)
    result = _advance_with_generator(
        field, _distribution(), _step(), SUBSTRATE, AFTERIMAGE, None, generator
    )
    return _record(
        path,
        field,
        result,
        state_marker=list(states),
        state_digest=_digest({"family": "CGR1", "states": states}),
        edge_rates=list(rates),
        z_next=list(next_states),
        carry_role="PRIVATE_CGR1_CONTROL",
    )


def _formed_e1_state(field: Any, history: str):
    contract = E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 1.5, 0.25, 0.5)
    state = build_neutral_e1_state(field.layer, contract)
    for values in HISTORIES[history]:
        state = advance_e1_local_edge_plasticity(
            _field_with_activations(field, values).layer, state, 1.0
        )
    return state


def _run_e1(path: dict[str, object], field: Any) -> dict[str, object]:
    state = _formed_e1_state(field, str(path["history"]))
    result = advance_e1_coupled_fast_shared_field(
        field,
        state,
        _distribution(),
        _step(),
        SUBSTRATE,
        AFTERIMAGE,
        backreaction_enabled=True,
    )
    bindings = [item.binding for item in state.edge_bindings]
    return _record(
        path,
        field,
        result.field,
        state_marker=bindings,
        state_digest=_digest({"family": "E1", "bindings": bindings}),
        edge_rates=[item.rate_per_second for item in result.applied_adapter.edge_rates],
        z_next=None,
        bindings=bindings,
        carry_role="PRIVATE_E1_BASELINE",
    )


def _run_off(path: dict[str, object], field: Any) -> dict[str, object]:
    result = advance_acm1h_off_four_node_field(
        field, _distribution(), _step(), SUBSTRATE, AFTERIMAGE
    )
    return _record(
        path,
        field,
        result,
        state_marker="STATELESS",
        state_digest=None,
        edge_rates=[1.0, 1.0, 1.0],
        z_next=None,
        carry_role="ACM_OFF",
    )


def _checks(records: list[dict[str, object]]) -> dict[str, bool]:
    by_key = {
        (row["family"], row["history"], row["config"]): row for row in records
    }
    off = by_key[("ACM_OFF", "NONE", "NONE")]
    c0 = all(
        by_key[("ACM1H", "Z0", _config_id(g, b))]["output_field_digest"]
        == off["output_field_digest"]
        for g, b in ACM1H_PARAMETER_CANDIDATES
    )
    c1 = all(
        by_key[("ACM1H", "G", _config_id(g, b))]["output_field_digest"]
        != by_key[("ACM1H", "O", _config_id(g, b))]["output_field_digest"]
        for g, b in ACM1H_PARAMETER_CANDIDATES
    )
    e1_g, e1_o = by_key[("E1", "G", "BOUND")], by_key[("E1", "O", "BOUND")]
    c3 = all(e1_g[key] == e1_o[key] for key in ("state_marker", "edge_rates", "output_field_digest"))
    c4 = all(
        all(
            by_key[("ACM1H", history, _config_id(g, b))][key]
            == by_key[("CGR1", history, _config_id(g, b))][key]
            for key in ("edge_rates", "S", "H", "output_field_digest", "z_next")
        )
        for g, b in ACM1H_PARAMETER_CANDIDATES
        for history in ("G", "O")
    )
    return {
        "C0_Z0_EQUALS_OFF": c0,
        "C1_G_DIFFERS_FROM_O": c1,
        "C2_STATE_SWAP_AND_ZERO_REMOVAL": c1 and c0,
        "C3_E1_G_EQUALS_O": c3,
        "C4_CGR1_EXACTLY_REPRODUCES_ACM1H": c4,
        "C5_ALL_SIX_CONFIGS_PRESENT": len({row["config"] for row in records if row["family"] == "ACM1H"}) == 6,
        "IDENTICAL_PROBE_PRESTATE": len({row["input_field_digest"] for row in records}) == 1,
        "EXACT_PATH_COUNT": len(records) == 33,
    }


def execute_s1uk_matrix_once(manifest_path: Path, output_path: Path) -> dict[str, object]:
    """Execute and seal the bound synthetic matrix; refuse any second execution."""

    if output_path.exists():
        raise S1UKMatrixError("sealed S1-UK result already exists; execution refused")
    plan = s1uk_path_plan()
    if len(plan) != 33:
        raise S1UKMatrixError("bound plan does not contain exactly 33 paths")
    manifest = load_four_node_fresh_manifest(manifest_path)
    probe = _field_with_activations(build_four_node_public_fresh_field(manifest), PROBE_S)
    records = []
    for path in plan:
        family = path["family"]
        if family == "ACM1H":
            records.append(_run_acm(path, probe))
        elif family == "CGR1":
            records.append(_run_cgr(path, probe))
        elif family == "ACM_OFF":
            records.append(_run_off(path, probe))
        elif family == "E1":
            records.append(_run_e1(path, probe))
        else:
            raise S1UKMatrixError(f"unknown path family: {family}")
    checks = _checks(records)
    structural = (
        checks["C0_Z0_EQUALS_OFF"]
        and checks["C3_E1_G_EQUALS_O"]
        and checks["C5_ALL_SIX_CONFIGS_PRESENT"]
        and checks["IDENTICAL_PROBE_PRESTATE"]
        and checks["EXACT_PATH_COUNT"]
    )
    if not structural:
        outcome = S1UK_OUTCOMES[2]
    elif checks["C4_CGR1_EXACTLY_REPRODUCES_ACM1H"]:
        outcome = S1UK_OUTCOMES[1]
    elif checks["C1_G_DIFFERS_FROM_O"]:
        outcome = S1UK_OUTCOMES[0]
    else:
        outcome = S1UK_OUTCOMES[1]
    payload: dict[str, object] = {
        "schema_id": S1UK_SCHEMA_ID,
        "scope": "PRIVATE_SYNTHETIC_33_PATH_MATRIX",
        "path_count": len(records),
        "probe_S": list(PROBE_S),
        "probe_H": [0.0] * 4,
        "checks": checks,
        "outcome": outcome,
        "records": records,
    }
    payload["result_digest"] = _digest(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
