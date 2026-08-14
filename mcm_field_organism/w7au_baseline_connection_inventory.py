"""Static W7-AU inventory of existing W7-L baseline connection gaps."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7AUBaselineConnectionInventoryError(ValueError):
    """Raised when the static baseline inventory is changed inconsistently."""


_AUDIT_ID = "w7au.w7l-baseline-connection-inventory.v1"
_W7AT_EVALUATION_DIGEST = (
    "b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c"
)
_STATUSES = (
    "SEVEN_PATH_MATERIALIZED_NOT_TERMINALLY_BOUND",
    "DERIVATIVE_ONLY_NO_TRAJECTORY_CONSUMER",
    "INTERVENTION_ONLY_NO_TRAJECTORY_CONSUMER",
)
_ROWS = (
    (
        "LEAK",
        "leak",
        "observer",
        "w7n.advance_w7n_local_baseline",
        "observer-output",
        _STATUSES[0],
        False,
        "bind-existing-w7ac-result-and-lifecycle-profile",
    ),
    (
        "SAT",
        "sat",
        "observer",
        "w7n.advance_w7n_local_baseline",
        "observer-output",
        _STATUSES[0],
        False,
        "bind-existing-w7ac-result-and-lifecycle-profile",
    ),
    (
        "NORM",
        "norm",
        "observer",
        "w7n.advance_w7n_local_baseline",
        "observer-output",
        _STATUSES[0],
        False,
        "bind-existing-w7ac-result-and-lifecycle-profile",
    ),
    (
        "LIN",
        "lin",
        "coupling",
        "w7n.compute_w7n_coupling_baseline",
        "field-sh",
        _STATUSES[1],
        True,
        "build-r124-seven-path-field-trajectory-consumer",
    ),
    (
        "F3",
        "f3",
        "coupling",
        "w7n.compute_w7n_coupling_baseline",
        "field-sh",
        _STATUSES[1],
        True,
        "build-r124-seven-path-field-trajectory-consumer",
    ),
    (
        "CONST-V",
        "const-v",
        "coupling",
        "w7n.compute_w7n_coupling_baseline",
        "field-sh",
        _STATUSES[1],
        True,
        "build-r124-seven-path-field-trajectory-consumer-first",
    ),
    (
        "MOB",
        "mob",
        "coupling",
        "w7n.compute_w7n_coupling_baseline",
        "field-sh",
        _STATUSES[1],
        True,
        "build-r124-seven-path-field-trajectory-consumer",
    ),
    (
        "ETA0",
        "eta0",
        "cap-intervention",
        "w7m.ablate_w7m_eta",
        "field-sh",
        _STATUSES[2],
        True,
        "build-parameterized-cap-r124-trajectory-consumer",
    ),
    (
        "KAPPA0",
        "kappa0",
        "cap-intervention",
        "w7m.ablate_w7m_kappa",
        "field-sh",
        _STATUSES[2],
        True,
        "build-parameterized-cap-r124-trajectory-consumer",
    ),
    (
        "SIGN",
        "sign",
        "cap-intervention",
        "w7m.invert_w7m_kappa",
        "field-sh",
        _STATUSES[2],
        True,
        "build-parameterized-cap-r124-trajectory-consumer",
    ),
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class W7AUBaselineConnection:
    """Static implementation and connection status for one W7-L baseline."""

    baseline_id: str
    model_id: str
    family: str
    equation_provider: str
    measurement_surface: str
    connection_status: str
    requires_new_integration: bool
    missing_boundary: str
    equation_implemented: bool
    registered_by_w7m: bool
    current_w7at_comparable: bool
    connection_digest: str

    def __post_init__(self) -> None:
        row = (
            self.baseline_id,
            self.model_id,
            self.family,
            self.equation_provider,
            self.measurement_surface,
            self.connection_status,
            self.requires_new_integration,
            self.missing_boundary,
        )
        if (
            row not in _ROWS
            or self.connection_status not in _STATUSES
            or self.equation_implemented is not True
            or self.registered_by_w7m is not True
            or self.current_w7at_comparable is not False
            or self.connection_digest
            != _digest(
                {
                    "row": row,
                    "equation_implemented": True,
                    "registered_by_w7m": True,
                    "current_w7at_comparable": False,
                }
            )
        ):
            raise W7AUBaselineConnectionInventoryError(
                "W7-AU baseline connection differs"
            )


def _audit_payload(
    connections: tuple[W7AUBaselineConnection, ...],
) -> dict[str, object]:
    return {
        "audit_id": _AUDIT_ID,
        "w7at_evaluation_digest": _W7AT_EVALUATION_DIGEST,
        "connection_digests": tuple(
            item.connection_digest for item in connections
        ),
        "equation_implementation_count": 10,
        "terminally_comparable_count": 0,
        "reuse_without_new_integration": ("LEAK", "SAT", "NORM"),
        "field_trajectory_gap": ("LIN", "F3", "CONST-V", "MOB"),
        "cap_intervention_trajectory_gap": ("ETA0", "KAPPA0", "SIGN"),
        "primary_narrow_baseline": "CONST-V",
        "accept_result_values": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AUBaselineConnectionInventory:
    """Complete static audit of all ten missing W7-L result connections."""

    audit_id: str
    w7at_evaluation_digest: str
    connections: tuple[W7AUBaselineConnection, ...]
    equation_implementation_count: int
    terminally_comparable_count: int
    reuse_without_new_integration: tuple[str, ...]
    field_trajectory_gap: tuple[str, ...]
    cap_intervention_trajectory_gap: tuple[str, ...]
    primary_narrow_baseline: str
    accept_result_values: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    audit_digest: str

    def __post_init__(self) -> None:
        connections = tuple(self.connections)
        if (
            self.audit_id != _AUDIT_ID
            or self.w7at_evaluation_digest != _W7AT_EVALUATION_DIGEST
            or tuple(
                (
                    item.baseline_id,
                    item.model_id,
                    item.family,
                    item.equation_provider,
                    item.measurement_surface,
                    item.connection_status,
                    item.requires_new_integration,
                    item.missing_boundary,
                )
                for item in connections
            )
            != _ROWS
            or self.equation_implementation_count != 10
            or self.terminally_comparable_count != 0
            or tuple(self.reuse_without_new_integration)
            != ("LEAK", "SAT", "NORM")
            or tuple(self.field_trajectory_gap)
            != ("LIN", "F3", "CONST-V", "MOB")
            or tuple(self.cap_intervention_trajectory_gap)
            != ("ETA0", "KAPPA0", "SIGN")
            or self.primary_narrow_baseline != "CONST-V"
            or self.accept_result_values is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.audit_digest != _digest(_audit_payload(connections))
        ):
            raise W7AUBaselineConnectionInventoryError(
                "W7-AU baseline inventory differs"
            )
        object.__setattr__(self, "connections", connections)


def build_w7au_baseline_connection_inventory(
) -> W7AUBaselineConnectionInventory:
    """Build the static inventory without reading or executing result values."""

    connections = []
    for row in _ROWS:
        payload = {
            "row": row,
            "equation_implemented": True,
            "registered_by_w7m": True,
            "current_w7at_comparable": False,
        }
        connections.append(
            W7AUBaselineConnection(
                *row,
                True,
                True,
                False,
                _digest(payload),
            )
        )
    connections_out = tuple(connections)
    return W7AUBaselineConnectionInventory(
        _AUDIT_ID,
        _W7AT_EVALUATION_DIGEST,
        connections_out,
        10,
        0,
        ("LEAK", "SAT", "NORM"),
        ("LIN", "F3", "CONST-V", "MOB"),
        ("ETA0", "KAPPA0", "SIGN"),
        "CONST-V",
        False,
        False,
        False,
        _digest(_audit_payload(connections_out)),
    )
