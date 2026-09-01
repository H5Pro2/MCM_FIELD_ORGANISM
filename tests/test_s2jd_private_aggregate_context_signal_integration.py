"""Focused S2-JD integration qualification without a five-status main run."""

from __future__ import annotations

import hashlib
import json
import unittest

import numpy as np

from mcm_field_organism._ppb1_reference import PPB1BankConfig, initial_ppb1_bank_state
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2fu_private_fixtures as p_fixtures
from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2hq_private_byte_block_conflict_fixture as q_fixtures
from tools import _s2ic_private_direct_two_area_conflict_baseline as baseline
from tools import _s2ic_private_two_area_conflict_contract as contract
from tools import _s2ic_private_two_area_conflict_signal as signal
from tools import _s2ig_private_fixture_registry as old_fixtures
from tools import _s2jb_private_receptor_aggregate_equivalence as aggregate
from tools import _s2jd_private_aggregate_context_binding as binding


QUALIFICATION_ID = "s2jd-aggregate-context-integration-20260901-03"


def _digest(label: str) -> str:
    return hashlib.sha256(
        json.dumps(
            {"neutral": label},
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def _image(blocks: tuple[int, ...]) -> np.ndarray:
    cells = np.asarray(blocks, dtype=np.uint8).reshape(2, 3, 3)
    frame = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
    frame.setflags(write=False)
    return frame


def _p1_blocks() -> tuple[int, ...]:
    values = p_fixtures.PATTERN_BY_ID["P1"].visual_cell_values
    return tuple(value for value in values for _ in range(3))


def _masked_probe(values: tuple[float, ...], suffix: str) -> probe_contract.MaskedVisualProbe:
    masked = tuple(
        values[index] if index in probe_contract.VISIBLE_POSITIONS else None
        for index in range(18)
    )
    return probe_contract.MaskedVisualProbe.build(masked, _digest(f"probe-{suffix}"))


def _component(
    area: str,
    values: tuple[float, ...],
    lineage: aggregate.PPBAggregateLineageV1 | None,
) -> context.PerceptualContextComponent:
    if area == "A_RECENT":
        role = "AV_JOINT"
        component_values = (0.0,) * 8 + values
        source_id = "s2jd.a.slot"
        support = stable = selected = None
        formation = 1
        distances = (0.0, 0.0)
    else:
        if lineage is None:
            raise AssertionError("B component requires lineage")
        role = "VISUAL"
        component_values = values
        source_id = f"{lineage.bank_id}.{lineage.slot_id}"
        support = lineage.final_support
        stable = lineage.stabilized
        selected = 3
        formation = None
        distances = (0.0,)
    source_digest = _digest(f"{area}-source")
    payload = {
        "schema": context.S2GB_SCHEMA,
        "component_role": role,
        "values": list(component_values),
        "source_id": source_id,
        "source_digest": source_digest,
        "values_digest": context._digest(list(component_values)),
        "native_distances": list(distances),
        "functional_distances": list(distances),
        "support_count": support,
        "stable": stable,
        "last_selected_step": selected,
        "formation_index": formation,
    }
    return context.PerceptualContextComponent(
        role,
        component_values,
        source_id,
        source_digest,
        payload["values_digest"],
        distances,
        distances,
        support,
        stable,
        selected,
        formation,
        context._digest(payload),
    )


def _role_finding(
    area: str,
    values: tuple[float, ...] | None,
    lineage: aggregate.PPBAggregateLineageV1 | None,
) -> context.PerceptualContextRoleFinding:
    role = "B4_RECENT" if area == "A_RECENT" else "TSPM_SLOW"
    if values is None:
        reason = "NO_OCCUPIED_SOURCE" if area == "A_RECENT" else "NO_STABLE_SLOW_MATCH"
        payload = {
            "schema": context.S2GB_SCHEMA,
            "role": role,
            "status": "ABSENT_VALID",
            "candidate_digest": None,
            "absence_reason": reason,
        }
        return context.PerceptualContextRoleFinding(
            role, "ABSENT_VALID", None, reason, context._digest(payload)
        )
    component = _component(area, values, lineage)
    relation = "JOINT_SOURCE_VALUES" if area == "A_RECENT" else "CROSS_MODAL_RELATION_NOT_REPRESENTED"
    candidate_payload = {
        "schema": context.S2GB_SCHEMA,
        "role": role,
        "component_digests": [component.component_digest],
        "cross_modal_relation": relation,
    }
    candidate = context.PerceptualContextCandidate(
        role, (component,), relation, context._digest(candidate_payload)
    )
    status = "AVAILABLE_COMPLETE" if area == "A_RECENT" else "AVAILABLE_PARTIAL"
    finding_payload = {
        "schema": context.S2GB_SCHEMA,
        "role": role,
        "status": status,
        "candidate_digest": candidate.candidate_digest,
        "absence_reason": None,
    }
    return context.PerceptualContextRoleFinding(
        role, status, candidate, None, context._digest(finding_payload)
    )


def _absent_fast() -> context.PerceptualContextRoleFinding:
    payload = {
        "schema": context.S2GB_SCHEMA,
        "role": "TSPM_FAST",
        "status": "ABSENT_VALID",
        "candidate_digest": None,
        "absence_reason": "NO_OCCUPIED_SOURCE",
    }
    return context.PerceptualContextRoleFinding(
        "TSPM_FAST", "ABSENT_VALID", None, "NO_OCCUPIED_SOURCE", context._digest(payload)
    )


def _sequence() -> context.B4ShortSequenceFinding:
    payload = {
        "schema": context.S2GB_SCHEMA,
        "status": "NOT_REQUESTED",
        "reference_digests": [],
        "observed_b4_state_digest": _digest("b4-state"),
        "source_evidence_digest": _digest("sequence-absence"),
    }
    return context.B4ShortSequenceFinding(
        "NOT_REQUESTED",
        (),
        payload["observed_b4_state_digest"],
        payload["source_evidence_digest"],
        context._digest(payload),
    )


def _bundle(
    a_values: tuple[float, ...] | None,
    b_values: tuple[float, ...] | None,
    b_lineage: aggregate.PPBAggregateLineageV1 | None,
    probe: probe_contract.MaskedVisualProbe,
) -> two_area.TwoAreaContextBundle:
    a_role = _role_finding("A_RECENT", a_values, None)
    b_role = _role_finding("B_STABLE", b_values, b_lineage)
    fast = _absent_fast()
    sequence = _sequence()
    a_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "area": "A_RECENT",
        "recent_content_finding_digest": a_role.finding_digest,
        "fast_internal_finding_digest": fast.finding_digest,
        "short_sequence_finding_digest": sequence.finding_digest,
    }
    area_a = two_area.AreaARecentFinding(
        "A_RECENT", a_role, fast, sequence, two_area._digest(a_payload)
    )
    b_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "area": "B_STABLE",
        "stable_content_finding_digest": b_role.finding_digest,
    }
    area_b = two_area.AreaBStableFinding(
        "B_STABLE", b_role, two_area._digest(b_payload)
    )
    candidates = tuple(
        item.candidate for item in (a_role, b_role) if item.candidate is not None
    )
    components = tuple(item for candidate in candidates for item in candidate.components)
    ledger_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "validated_bundle_count": 1,
        "validated_role_count": 3,
        "candidate_reference_count": len(candidates),
        "component_reference_count": len(components),
        "value_reference_count": sum(len(item.values) for item in components),
        "sequence_reference_count": 0,
        "area_projection_count": 2,
        "digest_operation_count": 4,
        "source_ledger_digest": _digest("source-ledger"),
    }
    ledger = two_area.TwoAreaContextResourceLedger(
        1,
        3,
        len(candidates),
        len(components),
        sum(len(item.values) for item in components),
        0,
        2,
        4,
        ledger_payload["source_ledger_digest"],
        two_area._digest(ledger_payload),
    )
    state = _digest("composite-state")
    output_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "contract_digest": two_area.S2GH_CONTRACT_DIGEST,
        "source_bundle_digest": _digest("source-bundle"),
        "binding_digest": _digest("bundle-binding"),
        "config_digest": _digest("config"),
        "composite_state_digest": state,
        "probe_digest": probe.probe_digest,
        "source_digest": _digest("bundle-source"),
        "area_finding_digests": [area_a.finding_digest, area_b.finding_digest],
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": state,
        "poststate_digest": state,
        "automatic_selection": None,
    }
    return two_area.TwoAreaContextBundle(
        two_area.S2GH_CONTRACT_DIGEST,
        output_payload["source_bundle_digest"],
        output_payload["binding_digest"],
        output_payload["config_digest"],
        state,
        probe.probe_digest,
        output_payload["source_digest"],
        (area_a, area_b),
        ledger,
        state,
        state,
        None,
        two_area._digest(output_payload),
    )


class S2JDAggregateContextSignalIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receptor = LocalChannelGridReceptor(VisualGridConfig(120, 80, 3, 2, 30.0))
        cls.frame_index = 0

    def _analyze(self, blocks: tuple[int, ...]):
        state, codes = aggregate.analyze_uint8_frame_with_aggregate_codes(
            _image(blocks), self.receptor, frame_index=type(self).frame_index
        )
        type(self).frame_index += 1
        return state, codes

    def _stable(self, blocks: tuple[int, ...], suffix: str):
        config = PPB1BankConfig(
            f"s2jd.visual.{suffix}",
            "visual",
            self.receptor.config.geometry_id,
            self.receptor.config.carrier_ids,
            4,
            0.01,
            0.05,
            3,
            64,
        )
        state = initial_ppb1_bank_state(config)
        lineages = ()
        sources = []
        result = None
        for _ in range(3):
            receptor_state, codes = self._analyze(blocks)
            sources.append(codes)
            result, lineages = aggregate.advance_visual_ppb_with_aggregate_lineage(
                config,
                state,
                from_visual_receptor_state(receptor_state),
                codes,
                lineages,
            )
            state = result.poststate
        self.assertIsNotNone(result)
        self.assertEqual(1, len(lineages))
        self.assertEqual(3, lineages[0].final_support)
        return tuple(result.readout.prototype_values), lineages[0], tuple(sources)

    def _case(
        self,
        *,
        suffix: str,
        a_blocks: tuple[int, ...] | None,
        b_blocks: tuple[int, ...] | None,
        probe_blocks: tuple[int, ...],
    ):
        probe_state, probe_codes = self._analyze(probe_blocks)
        probe = _masked_probe(tuple(probe_state.channel_values), suffix)
        if a_blocks is None:
            a_values = a_codes = None
        else:
            a_state, a_codes = self._analyze(a_blocks)
            a_values = tuple(a_state.channel_values)
        if b_blocks is None:
            b_values = b_lineage = b_sources = None
        else:
            b_values, b_lineage, b_sources = self._stable(b_blocks, suffix)
        bundle = _bundle(a_values, b_values, b_lineage, probe)
        return probe, probe_codes, a_codes, b_lineage, b_sources, bundle

    def _invoke(self, function_role: str, case, suffix: str):
        probe, probe_codes, a_codes, b_lineage, b_sources, bundle = case
        signal_input = contract.TwoAreaConflictSignalInput.build(
            f"s2jd-{function_role.lower().replace('_', '-')}-{suffix}",
            function_role,
            probe,
            bundle,
        )
        owner = contract.TwoAreaConflictSignalOwner(
            contract.TwoAreaConflictOwnerPrestate.build(
                f"s2jd-owner-{function_role.lower().replace('_', '-')}-{suffix}",
                signal_input,
            )
        )
        evidence = binding.build_aggregate_visibility_binding(
            probe,
            bundle,
            signal_input,
            probe_codes=probe_codes,
            a_codes=a_codes,
            b_lineage=b_lineage,
            b_source_code_inventories=b_sources,
        )
        if function_role == "SIGNAL":
            commit = signal.form_two_area_conflict_signal_with_aggregate_evidence(
                probe, bundle, signal_input, owner, evidence
            )
        else:
            commit = baseline.form_direct_two_area_conflict_baseline_with_aggregate_evidence(
                probe, bundle, signal_input, owner, evidence
            )
        return commit, owner, evidence

    def _assert_pair(self, case, expected: str, suffix: str) -> None:
        before = (
            case[-1].bundle_digest,
            case[-1].prestate_digest,
            case[-1].poststate_digest,
        )
        signal_commit, signal_owner, _ = self._invoke("SIGNAL", case, f"{suffix}-signal")
        baseline_commit, baseline_owner, _ = self._invoke(
            "DIRECT_BASELINE", case, f"{suffix}-baseline"
        )
        self.assertEqual(expected, signal_commit.result.status)
        self.assertEqual(expected, baseline_commit.result.status)
        self.assertEqual(
            signal_commit.result.applicable_areas,
            baseline_commit.result.applicable_areas,
        )
        self.assertEqual("CONSUMED", signal_owner.state)
        self.assertEqual("CONSUMED", baseline_owner.state)
        self.assertEqual(
            before,
            (
                case[-1].bundle_digest,
                case[-1].prestate_digest,
                case[-1].poststate_digest,
            ),
        )

    def test_01_c01_rounding_drift_is_prospectively_consistent(self) -> None:
        case = self._case(
            suffix="c01",
            a_blocks=_p1_blocks(),
            b_blocks=_p1_blocks(),
            probe_blocks=_p1_blocks(),
        )
        probe_values = tuple(case[0].values[index] for index in probe_contract.VISIBLE_POSITIONS)
        b_values = tuple(
            case[-1].area_findings[1].stable_content.candidate.components[0].values[index]
            for index in probe_contract.VISIBLE_POSITIONS
        )
        self.assertNotEqual(probe_values, b_values)
        self._assert_pair(case, "CONSISTENT", "c01")

    def test_02_c05_rounding_drift_keeps_b_as_single_source(self) -> None:
        case = self._case(
            suffix="c05",
            a_blocks=None,
            b_blocks=_p1_blocks(),
            probe_blocks=_p1_blocks(),
        )
        self._assert_pair(case, "SINGLE_SOURCE", "c05")

    def test_03_c07_real_one_step_difference_remains_visible(self) -> None:
        case = self._case(
            suffix="c07",
            a_blocks=q_fixtures.V0.block_values,
            b_blocks=q_fixtures.V1.block_values,
            probe_blocks=old_fixtures.Z_VISUAL_BLOCKS["z0"],
        )
        self._assert_pair(case, "NO_APPLICABLE_CONTEXT", "c07")

    def test_04_c08_real_one_step_difference_remains_visible(self) -> None:
        case = self._case(
            suffix="c08",
            a_blocks=q_fixtures.V1.block_values,
            b_blocks=q_fixtures.V0.block_values,
            probe_blocks=old_fixtures.Z_VISUAL_BLOCKS["z1"],
        )
        self._assert_pair(case, "NO_APPLICABLE_CONTEXT", "c08")

    def test_05_adjacent_aggregate_sums_are_not_equal(self) -> None:
        candidate_state, candidate_codes = self._analyze(_p1_blocks())
        adjacent = _image(_p1_blocks()).copy()
        adjacent[0, 0, 0] = 211
        adjacent.setflags(write=False)
        probe_state, probe_codes = aggregate.analyze_uint8_frame_with_aggregate_codes(
            adjacent, self.receptor, frame_index=type(self).frame_index
        )
        type(self).frame_index += 1
        self.assertEqual(1, probe_codes[0].byte_sum - candidate_codes[0].byte_sum)
        probe = _masked_probe(tuple(probe_state.channel_values), "adjacent")
        bundle = _bundle(tuple(candidate_state.channel_values), None, None, probe)
        case = (probe, probe_codes, candidate_codes, None, None, bundle)
        self._assert_pair(case, "NO_APPLICABLE_CONTEXT", "adjacent")

    def test_06_missing_b_lineage_fails_before_signal(self) -> None:
        case = self._case(
            suffix="missing",
            a_blocks=None,
            b_blocks=_p1_blocks(),
            probe_blocks=_p1_blocks(),
        )
        probe, probe_codes, _, _, b_sources, bundle = case
        signal_input = contract.TwoAreaConflictSignalInput.build(
            "s2jd-signal-missing-lineage", "SIGNAL", probe, bundle
        )
        with self.assertRaises(binding.S2JDBindingError):
            binding.build_aggregate_visibility_binding(
                probe,
                bundle,
                signal_input,
                probe_codes=probe_codes,
                a_codes=None,
                b_lineage=None,
                b_source_code_inventories=b_sources,
            )

    def test_07_mixed_b_source_chain_fails_closed(self) -> None:
        case = self._case(
            suffix="mixed",
            a_blocks=None,
            b_blocks=_p1_blocks(),
            probe_blocks=_p1_blocks(),
        )
        probe, probe_codes, _, lineage, b_sources, bundle = case
        _, foreign_codes = self._analyze(q_fixtures.V0.block_values)
        mixed_sources = (b_sources[0], foreign_codes, b_sources[2])
        signal_input = contract.TwoAreaConflictSignalInput.build(
            "s2jd-signal-mixed-lineage", "SIGNAL", probe, bundle
        )
        with self.assertRaises(binding.S2JDBindingError):
            binding.build_aggregate_visibility_binding(
                probe,
                bundle,
                signal_input,
                probe_codes=probe_codes,
                a_codes=None,
                b_lineage=lineage,
                b_source_code_inventories=mixed_sources,
            )

    def test_08_inputs_are_immutable_and_no_aggregate_state_is_exposed(self) -> None:
        case = self._case(
            suffix="readonly",
            a_blocks=_p1_blocks(),
            b_blocks=_p1_blocks(),
            probe_blocks=_p1_blocks(),
        )
        before = (
            case[0].probe_digest,
            case[-1].bundle_digest,
            case[3].lineage_digest,
            tuple(item.evidence_digest for item in case[1]),
        )
        commit, _, evidence = self._invoke("SIGNAL", case, "readonly")
        self.assertEqual("CONSISTENT", commit.result.status)
        self.assertFalse(hasattr(commit.result, "aggregate_codes"))
        self.assertFalse(hasattr(commit.result, "best_memory"))
        self.assertEqual(
            before,
            (
                case[0].probe_digest,
                case[-1].bundle_digest,
                case[3].lineage_digest,
                tuple(item.evidence_digest for item in case[1]),
            ),
        )
        self.assertEqual(evidence.bundle_digest, case[-1].bundle_digest)


if __name__ == "__main__":
    unittest.main()
