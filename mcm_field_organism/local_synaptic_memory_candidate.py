"""Passive two-timescale local memory candidate outside the organism runtime."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Iterable, Mapping

from .shared_mcm_field import SharedMCMField


class LocalSynapticMemoryCandidateError(ValueError):
    """Raised when the passive candidate violates its bounded local contract."""


def _unit_interval(value: object, role: str, *, allow_zero: bool) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise LocalSynapticMemoryCandidateError(f"{role} must be numeric") from exc
    minimum = 0.0 if allow_zero else 0.0
    if (
        not math.isfinite(result)
        or result < minimum
        or result > 1.0
        or (not allow_zero and result == 0.0)
    ):
        interval = "0..1" if allow_zero else "greater than 0 and at most 1"
        raise LocalSynapticMemoryCandidateError(f"{role} must be {interval}")
    return result


@dataclass(frozen=True, slots=True)
class LocalSynapticMemoryConfig:
    flexible_rate: float
    stabilization_rate: float
    release_rate: float
    local_budget: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "flexible_rate",
            _unit_interval(self.flexible_rate, "flexible_rate", allow_zero=False),
        )
        object.__setattr__(
            self,
            "stabilization_rate",
            _unit_interval(
                self.stabilization_rate,
                "stabilization_rate",
                allow_zero=False,
            ),
        )
        object.__setattr__(
            self,
            "release_rate",
            _unit_interval(self.release_rate, "release_rate", allow_zero=False),
        )
        object.__setattr__(
            self,
            "local_budget",
            _unit_interval(self.local_budget, "local_budget", allow_zero=False),
        )


@dataclass(frozen=True, slots=True)
class LocalSynapticRelationState:
    relation_id: str
    source_neuron_id: str
    target_neuron_id: str
    flexible: float
    stabilized: float

    def __post_init__(self) -> None:
        for role in ("relation_id", "source_neuron_id", "target_neuron_id"):
            value = getattr(self, role)
            if not isinstance(value, str) or not value:
                raise LocalSynapticMemoryCandidateError(
                    f"{role} must be a non-empty technical identity"
                )
        if self.source_neuron_id == self.target_neuron_id:
            raise LocalSynapticMemoryCandidateError(
                "local memory relation cannot connect a neuron to itself"
            )
        for role in ("flexible", "stabilized"):
            try:
                value = float(getattr(self, role))
            except (TypeError, ValueError) as exc:
                raise LocalSynapticMemoryCandidateError(
                    f"{role} must be numeric"
                ) from exc
            if not math.isfinite(value) or abs(value) > 1.0:
                raise LocalSynapticMemoryCandidateError(
                    f"{role} must stay within -1..1"
                )
            object.__setattr__(self, role, value)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "relation_id": self.relation_id,
            "source_neuron_id": self.source_neuron_id,
            "target_neuron_id": self.target_neuron_id,
            "flexible": self.flexible,
            "stabilized": self.stabilized,
        }


@dataclass(frozen=True, slots=True)
class LocalSynapticMemoryState:
    tick: int
    relations: tuple[LocalSynapticRelationState, ...]

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int) or self.tick < 0:
            raise LocalSynapticMemoryCandidateError(
                "memory tick must be a non-negative integer"
            )
        relations = tuple(self.relations)
        if any(
            not isinstance(relation, LocalSynapticRelationState)
            for relation in relations
        ):
            raise LocalSynapticMemoryCandidateError(
                "relations must contain local synaptic relation states"
            )
        relation_ids = [relation.relation_id for relation in relations]
        if len(set(relation_ids)) != len(relation_ids):
            raise LocalSynapticMemoryCandidateError(
                "local relation identities must be unique"
            )
        object.__setattr__(
            self,
            "relations",
            tuple(sorted(relations, key=lambda item: item.relation_id)),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "relations": [
                relation.canonical_payload() for relation in self.relations
            ],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def local_relation_evidence(
    field: SharedMCMField,
) -> dict[str, tuple[str, str, float]]:
    """Read local coactivity after every neuron completed the same field tick."""

    if not isinstance(field, SharedMCMField):
        raise LocalSynapticMemoryCandidateError(
            "local relation evidence requires one shared MCM field"
        )
    evidence: dict[str, tuple[str, str, float]] = {}
    neuron_by_id = {
        neuron.neuron_id: neuron for neuron in field.layer.neurons
    }
    for target in field.layer.neurons:
        for sample in target.perception.local_samples:
            prefix = "sample."
            if not sample.sample_id.startswith(prefix):
                raise LocalSynapticMemoryCandidateError(
                    "field sample identity cannot resolve its local source"
                )
            source_id = sample.sample_id[len(prefix) :]
            source = neuron_by_id.get(source_id)
            if source is None:
                raise LocalSynapticMemoryCandidateError(
                    "field sample references an unknown local source"
                )
            relation_id = f"relation.{source_id}.to.{target.neuron_id}"
            value = max(-1.0, min(1.0, target.activation * source.activation))
            evidence[relation_id] = (
                source_id,
                target.neuron_id,
                value,
            )
    return dict(sorted(evidence.items()))


def initialize_local_synaptic_memory(
    evidence: Mapping[str, tuple[str, str, float]],
) -> LocalSynapticMemoryState:
    relations = []
    for relation_id, item in sorted(dict(evidence).items()):
        if not isinstance(item, tuple) or len(item) != 3:
            raise LocalSynapticMemoryCandidateError(
                "evidence values must contain source, target, and local coactivity"
            )
        source_id, target_id, value = item
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise LocalSynapticMemoryCandidateError(
                "local coactivity must be numeric"
            ) from exc
        if not math.isfinite(numeric) or abs(numeric) > 1.0:
            raise LocalSynapticMemoryCandidateError(
                "local coactivity must stay within -1..1"
            )
        relations.append(
            LocalSynapticRelationState(
                relation_id,
                source_id,
                target_id,
                0.0,
                0.0,
            )
        )
    return LocalSynapticMemoryState(0, tuple(relations))


def advance_local_synaptic_memory(
    state: LocalSynapticMemoryState,
    evidence: Mapping[str, tuple[str, str, float]],
    config: LocalSynapticMemoryConfig,
) -> LocalSynapticMemoryState:
    """Advance flexible and stabilized local efficacy without runtime writeback."""

    if not isinstance(state, LocalSynapticMemoryState):
        raise LocalSynapticMemoryCandidateError(
            "candidate advance requires one completed memory state"
        )
    if not isinstance(config, LocalSynapticMemoryConfig):
        raise LocalSynapticMemoryCandidateError(
            "candidate advance requires one explicit configuration"
        )
    evidence_in = dict(evidence)
    if set(evidence_in) != {relation.relation_id for relation in state.relations}:
        raise LocalSynapticMemoryCandidateError(
            "candidate topology must remain fixed during one passive comparison"
        )

    proposals: list[LocalSynapticRelationState] = []
    for relation in state.relations:
        source_id, target_id, raw_value = evidence_in[relation.relation_id]
        if (
            source_id != relation.source_neuron_id
            or target_id != relation.target_neuron_id
        ):
            raise LocalSynapticMemoryCandidateError(
                "candidate relation identities must not be remapped"
            )
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise LocalSynapticMemoryCandidateError(
                "local coactivity must be numeric"
            ) from exc
        if not math.isfinite(value) or abs(value) > 1.0:
            raise LocalSynapticMemoryCandidateError(
                "local coactivity must stay within -1..1"
            )

        flexible = relation.flexible + config.flexible_rate * (
            value - relation.flexible
        )
        stabilized = (
            relation.stabilized
            + config.stabilization_rate
            * flexible
            * (1.0 - abs(relation.stabilized))
            - config.release_rate
            * (1.0 - abs(value))
            * relation.stabilized
        )
        proposals.append(
            LocalSynapticRelationState(
                relation.relation_id,
                source_id,
                target_id,
                max(-1.0, min(1.0, flexible)),
                max(-1.0, min(1.0, stabilized)),
            )
        )

    by_target: dict[str, list[int]] = {}
    for index, relation in enumerate(proposals):
        by_target.setdefault(relation.target_neuron_id, []).append(index)
    bounded = list(proposals)
    for indices in by_target.values():
        total = sum(abs(proposals[index].stabilized) for index in indices)
        if total <= config.local_budget:
            continue
        scale = config.local_budget / total
        for index in indices:
            relation = proposals[index]
            bounded[index] = LocalSynapticRelationState(
                relation.relation_id,
                relation.source_neuron_id,
                relation.target_neuron_id,
                relation.flexible,
                relation.stabilized * scale,
            )
    return LocalSynapticMemoryState(state.tick + 1, tuple(bounded))


def local_synaptic_memory_candidate_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            LocalSynapticMemoryConfig,
            LocalSynapticRelationState,
            LocalSynapticMemoryState,
        )
        for item in fields(cls)
    )
