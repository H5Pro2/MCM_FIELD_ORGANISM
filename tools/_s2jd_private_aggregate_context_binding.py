"""Private prospective aggregate provenance for S2-IC visible-value checks."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jb_private_receptor_aggregate_equivalence as aggregate


S2JD_SCHEMA = "s2jd.private.aggregate-context-binding.v1"
AVAILABLE = "AVAILABLE"
ABSENT_VALID = "ABSENT_VALID"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2JDBindingError(ValueError):
    """One fail-closed aggregate provenance violation."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2JDBindingError(message)


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _code_value(code: aggregate.ReceptorAggregateCodeV1) -> float:
    return (float(code.byte_sum) / float(code.sample_count)) / 255.0


def _prototype_digest(values: tuple[float, ...]) -> str:
    return aggregate._digest(
        {"schema": aggregate.S2JB_SCHEMA, "prototype_values": list(values)}
    )


def aggregate_digests_equivalent(first: object, second: object) -> str:
    """Apply the qualified integer aggregate identity rule to two bound digests."""

    _require(_valid_digest(first) and _valid_digest(second), "aggregate digest differs")
    return (
        aggregate.SAME_RECEPTOR_AGGREGATE
        if first == second
        else aggregate.DIFFERENT_RECEPTOR_AGGREGATE
    )


@dataclass(frozen=True, slots=True)
class AreaAggregateEvidenceV1:
    area: str
    status: str
    candidate_digest: str | None
    component_digest: str | None
    component_source_digest: str | None
    ordered_carrier_ids: tuple[str, ...]
    ordered_aggregate_code_digests: tuple[str, ...]
    lineage_digest: str | None
    lineage_source_chain_digest: str | None
    evidence_digest: str
    schema: str = S2JD_SCHEMA

    def __post_init__(self) -> None:
        _require(self.schema == S2JD_SCHEMA, "area evidence schema differs")
        _require(self.area in signal_contract.AREAS, "area evidence role differs")
        _require(self.status in (AVAILABLE, ABSENT_VALID), "area evidence status differs")
        if self.status == AVAILABLE:
            _require(
                all(
                    _valid_digest(value)
                    for value in (
                        self.candidate_digest,
                        self.component_digest,
                        self.component_source_digest,
                    )
                ),
                "available area binding differs",
            )
            _require(
                type(self.ordered_carrier_ids) is tuple
                and len(self.ordered_carrier_ids) == aggregate.VISUAL_DIMENSION
                and len(set(self.ordered_carrier_ids)) == len(self.ordered_carrier_ids),
                "ordered carrier inventory differs",
            )
            _require(
                type(self.ordered_aggregate_code_digests) is tuple
                and len(self.ordered_aggregate_code_digests) == aggregate.VISUAL_DIMENSION
                and all(_valid_digest(value) for value in self.ordered_aggregate_code_digests),
                "ordered aggregate inventory differs",
            )
            _require(
                (
                    self.area == "A_RECENT"
                    and self.lineage_digest is None
                    and self.lineage_source_chain_digest is None
                )
                or (
                    self.area == "B_STABLE"
                    and _valid_digest(self.lineage_digest)
                    and _valid_digest(self.lineage_source_chain_digest)
                ),
                "area lineage role differs",
            )
        else:
            _require(
                self.candidate_digest is None
                and self.component_digest is None
                and self.component_source_digest is None
                and self.ordered_carrier_ids == ()
                and self.ordered_aggregate_code_digests == ()
                and self.lineage_digest is None
                and self.lineage_source_chain_digest is None,
                "valid absence carries aggregate candidate evidence",
            )
        _require(
            _valid_digest(self.evidence_digest)
            and self.evidence_digest == _digest(self.payload_without_digest()),
            "area evidence digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "area": self.area,
            "status": self.status,
            "candidate_digest": self.candidate_digest,
            "component_digest": self.component_digest,
            "component_source_digest": self.component_source_digest,
            "ordered_carrier_ids": list(self.ordered_carrier_ids),
            "ordered_aggregate_code_digests": list(
                self.ordered_aggregate_code_digests
            ),
            "lineage_digest": self.lineage_digest,
            "lineage_source_chain_digest": self.lineage_source_chain_digest,
        }


@dataclass(frozen=True, slots=True)
class AggregateVisibilityBindingV1:
    signal_input_digest: str
    probe_digest: str
    bundle_digest: str
    composite_state_digest: str
    probe_frame_evidence_digest: str
    probe_ordered_carrier_ids: tuple[str, ...]
    probe_ordered_aggregate_code_digests: tuple[str, ...]
    a_evidence: AreaAggregateEvidenceV1
    b_evidence: AreaAggregateEvidenceV1
    binding_digest: str
    schema: str = S2JD_SCHEMA

    def __post_init__(self) -> None:
        _require(self.schema == S2JD_SCHEMA, "binding schema differs")
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.signal_input_digest,
                    self.probe_digest,
                    self.bundle_digest,
                    self.composite_state_digest,
                    self.probe_frame_evidence_digest,
                )
            ),
            "binding digest role differs",
        )
        _require(
            type(self.probe_ordered_carrier_ids) is tuple
            and len(self.probe_ordered_carrier_ids) == aggregate.VISUAL_DIMENSION
            and len(set(self.probe_ordered_carrier_ids))
            == len(self.probe_ordered_carrier_ids),
            "probe carrier inventory differs",
        )
        _require(
            type(self.probe_ordered_aggregate_code_digests) is tuple
            and len(self.probe_ordered_aggregate_code_digests)
            == aggregate.VISUAL_DIMENSION
            and all(
                _valid_digest(value)
                for value in self.probe_ordered_aggregate_code_digests
            ),
            "probe aggregate inventory differs",
        )
        _require(
            type(self.a_evidence) is AreaAggregateEvidenceV1
            and type(self.b_evidence) is AreaAggregateEvidenceV1,
            "area evidence type differs",
        )
        self.a_evidence.__post_init__()
        self.b_evidence.__post_init__()
        _require(
            self.a_evidence.area == "A_RECENT"
            and self.b_evidence.area == "B_STABLE",
            "area evidence order differs",
        )
        for evidence in (self.a_evidence, self.b_evidence):
            if evidence.status == AVAILABLE:
                _require(
                    evidence.ordered_carrier_ids == self.probe_ordered_carrier_ids,
                    "probe and candidate carrier roles differ",
                )
        _require(
            _valid_digest(self.binding_digest)
            and self.binding_digest == _digest(self.payload_without_digest()),
            "aggregate binding digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "signal_input_digest": self.signal_input_digest,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_frame_evidence_digest": self.probe_frame_evidence_digest,
            "probe_ordered_carrier_ids": list(self.probe_ordered_carrier_ids),
            "probe_ordered_aggregate_code_digests": list(
                self.probe_ordered_aggregate_code_digests
            ),
            "a_evidence_digest": self.a_evidence.evidence_digest,
            "b_evidence_digest": self.b_evidence.evidence_digest,
        }


def _absence(area: str) -> AreaAggregateEvidenceV1:
    payload = {
        "schema": S2JD_SCHEMA,
        "area": area,
        "status": ABSENT_VALID,
        "candidate_digest": None,
        "component_digest": None,
        "component_source_digest": None,
        "ordered_carrier_ids": [],
        "ordered_aggregate_code_digests": [],
        "lineage_digest": None,
        "lineage_source_chain_digest": None,
    }
    return AreaAggregateEvidenceV1(
        area, ABSENT_VALID, None, None, None, (), (), None, None, _digest(payload)
    )


def _available(
    area: str,
    candidate: context.PerceptualContextCandidate,
    component: context.PerceptualContextComponent,
    carrier_ids: tuple[str, ...],
    code_digests: tuple[str, ...],
    lineage_digest: str | None,
    lineage_source_chain_digest: str | None,
) -> AreaAggregateEvidenceV1:
    payload = {
        "schema": S2JD_SCHEMA,
        "area": area,
        "status": AVAILABLE,
        "candidate_digest": candidate.candidate_digest,
        "component_digest": component.component_digest,
        "component_source_digest": component.source_digest,
        "ordered_carrier_ids": list(carrier_ids),
        "ordered_aggregate_code_digests": list(code_digests),
        "lineage_digest": lineage_digest,
        "lineage_source_chain_digest": lineage_source_chain_digest,
    }
    return AreaAggregateEvidenceV1(
        area,
        AVAILABLE,
        candidate.candidate_digest,
        component.component_digest,
        component.source_digest,
        carrier_ids,
        code_digests,
        lineage_digest,
        lineage_source_chain_digest,
        _digest(payload),
    )


def _validated_codes(codes: object) -> tuple[aggregate.ReceptorAggregateCodeV1, ...]:
    aggregate.aggregate_frame_evidence_digest(codes)
    _require(type(codes) is tuple, "aggregate code tuple differs")
    return tuple(codes)


def _visual_component(
    bundle: two_area.TwoAreaContextBundle,
    area: str,
) -> tuple[
    context.PerceptualContextRoleFinding,
    context.PerceptualContextCandidate | None,
    context.PerceptualContextComponent | None,
]:
    if area == "A_RECENT":
        finding = bundle.area_findings[0].recent_content
        if finding.status == "ABSENT_VALID":
            return finding, None, None
        _require(
            finding.status == "AVAILABLE_COMPLETE"
            and finding.candidate is not None
            and finding.candidate.role == "B4_RECENT"
            and len(finding.candidate.components) == 1,
            "A_RECENT anatomy differs",
        )
        component = finding.candidate.components[0]
        _require(
            component.component_role == "AV_JOINT" and len(component.values) == 26,
            "A_RECENT visual component differs",
        )
        return finding, finding.candidate, component
    finding = bundle.area_findings[1].stable_content
    if finding.status == "ABSENT_VALID":
        return finding, None, None
    _require(
        finding.status in ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL")
        and finding.candidate is not None
        and finding.candidate.role == "TSPM_SLOW",
        "B_STABLE anatomy differs",
    )
    components = tuple(
        item for item in finding.candidate.components if item.component_role == "VISUAL"
    )
    _require(len(components) == 1 and components[0].stable is True, "B_STABLE visual component differs")
    return finding, finding.candidate, components[0]


def build_aggregate_visibility_binding(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    *,
    probe_codes: tuple[aggregate.ReceptorAggregateCodeV1, ...],
    a_codes: tuple[aggregate.ReceptorAggregateCodeV1, ...] | None,
    b_lineage: aggregate.PPBAggregateLineageV1 | None,
    b_source_code_inventories: tuple[
        tuple[aggregate.ReceptorAggregateCodeV1, ...], ...
    ]
    | None,
) -> AggregateVisibilityBindingV1:
    """Bind prospective aggregate provenance without adding a memory area."""

    _require(type(probe) is probe_contract.MaskedVisualProbe, "probe type differs")
    _require(type(bundle) is two_area.TwoAreaContextBundle, "bundle type differs")
    _require(
        type(signal_input) is signal_contract.TwoAreaConflictSignalInput,
        "signal input type differs",
    )
    _require(
        signal_input.probe_digest == probe.probe_digest
        and signal_input.bundle_digest == bundle.bundle_digest
        and signal_input.composite_state_digest
        == bundle.prestate_digest
        == bundle.poststate_digest,
        "signal source binding differs",
    )
    probe_inventory = _validated_codes(probe_codes)
    for position in probe_contract.VISIBLE_POSITIONS:
        _require(
            probe.values[position] == _code_value(probe_inventory[position]),
            "probe float does not match prospective aggregate source",
        )
    ordered_carriers = tuple(item.carrier_id for item in probe_inventory)
    probe_digests = tuple(item.aggregate_code_digest for item in probe_inventory)

    _, a_candidate, a_component = _visual_component(bundle, "A_RECENT")
    if a_candidate is None:
        _require(a_codes is None, "absent A_RECENT received aggregate evidence")
        a_evidence = _absence("A_RECENT")
    else:
        _require(a_component is not None and a_codes is not None, "A_RECENT aggregate evidence missing")
        a_inventory = _validated_codes(a_codes)
        a_visual = tuple(a_component.values[8:])
        _require(
            a_visual == tuple(_code_value(item) for item in a_inventory),
            "A_RECENT values do not match their aggregate source",
        )
        a_evidence = _available(
            "A_RECENT",
            a_candidate,
            a_component,
            tuple(item.carrier_id for item in a_inventory),
            tuple(item.aggregate_code_digest for item in a_inventory),
            None,
            None,
        )

    _, b_candidate, b_component = _visual_component(bundle, "B_STABLE")
    if b_candidate is None:
        _require(
            b_lineage is None and b_source_code_inventories is None,
            "absent B_STABLE received aggregate evidence",
        )
        b_evidence = _absence("B_STABLE")
    else:
        _require(
            b_component is not None
            and type(b_lineage) is aggregate.PPBAggregateLineageV1,
            "B_STABLE aggregate lineage missing",
        )
        b_lineage.__post_init__()
        _require(
            type(b_source_code_inventories) is tuple
            and len(b_source_code_inventories)
            == len(b_lineage.ordered_source_aggregate_evidence_digests),
            "B_STABLE aggregate source chain missing",
        )
        source_inventories = tuple(
            _validated_codes(items) for items in b_source_code_inventories
        )
        source_evidence_digests = tuple(
            aggregate.aggregate_frame_evidence_digest(items)
            for items in source_inventories
        )
        source_code_digests = tuple(
            tuple(item.aggregate_code_digest for item in items)
            for items in source_inventories
        )
        _require(
            b_lineage.stabilized
            and b_lineage.final_support == b_component.support_count
            and b_lineage.final_prototype_digest
            == _prototype_digest(tuple(b_component.values))
            and b_component.source_id == f"{b_lineage.bank_id}.{b_lineage.slot_id}",
            "B_STABLE lineage does not bind the selected prototype",
        )
        _require(
            source_evidence_digests
            == b_lineage.ordered_source_aggregate_evidence_digests
            and all(
                item == b_lineage.homogeneous_aggregate_code_digests
                for item in source_code_digests
            ),
            "B_STABLE aggregate source chain is mixed or reordered",
        )
        source_chain_digest = _digest(
            {
                "schema": "s2jd.private.aggregate-source-chain.v1",
                "lineage_digest": b_lineage.lineage_digest,
                "ordered_source_aggregate_evidence_digests": list(
                    source_evidence_digests
                ),
                "ordered_code_digest_sets": [list(items) for items in source_code_digests],
            }
        )
        b_evidence = _available(
            "B_STABLE",
            b_candidate,
            b_component,
            tuple(b_lineage.carrier_ids),
            tuple(b_lineage.homogeneous_aggregate_code_digests),
            b_lineage.lineage_digest,
            source_chain_digest,
        )

    payload = {
        "schema": S2JD_SCHEMA,
        "signal_input_digest": signal_input.input_digest,
        "probe_digest": probe.probe_digest,
        "bundle_digest": bundle.bundle_digest,
        "composite_state_digest": bundle.composite_state_digest,
        "probe_frame_evidence_digest": aggregate.aggregate_frame_evidence_digest(
            probe_inventory
        ),
        "probe_ordered_carrier_ids": list(ordered_carriers),
        "probe_ordered_aggregate_code_digests": list(probe_digests),
        "a_evidence_digest": a_evidence.evidence_digest,
        "b_evidence_digest": b_evidence.evidence_digest,
    }
    return AggregateVisibilityBindingV1(
        signal_input.input_digest,
        probe.probe_digest,
        bundle.bundle_digest,
        bundle.composite_state_digest,
        payload["probe_frame_evidence_digest"],
        ordered_carriers,
        probe_digests,
        a_evidence,
        b_evidence,
        _digest(payload),
    )


def validate_aggregate_visibility_binding(
    binding: object,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
) -> AggregateVisibilityBindingV1:
    _require(
        type(binding) is AggregateVisibilityBindingV1,
        "exact aggregate visibility binding required",
    )
    binding.__post_init__()
    _require(
        binding.signal_input_digest == signal_input.input_digest
        and binding.probe_digest == probe.probe_digest
        and binding.bundle_digest == bundle.bundle_digest
        and binding.composite_state_digest
        == bundle.composite_state_digest
        == bundle.prestate_digest
        == bundle.poststate_digest,
        "aggregate visibility source binding differs",
    )
    _, a_candidate, a_component = _visual_component(bundle, "A_RECENT")
    _, b_candidate, b_component = _visual_component(bundle, "B_STABLE")
    for evidence, candidate, component in (
        (binding.a_evidence, a_candidate, a_component),
        (binding.b_evidence, b_candidate, b_component),
    ):
        if candidate is None:
            _require(evidence.status == ABSENT_VALID, "absence evidence differs")
        else:
            _require(
                evidence.status == AVAILABLE
                and component is not None
                and evidence.candidate_digest == candidate.candidate_digest
                and evidence.component_digest == component.component_digest
                and evidence.component_source_digest == component.source_digest,
                "candidate aggregate binding differs",
            )
    return binding


__all__: tuple[str, ...] = ()
