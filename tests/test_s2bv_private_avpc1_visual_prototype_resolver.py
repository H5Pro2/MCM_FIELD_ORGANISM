from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism import current_api
from mcm_field_organism._avpc1_bounded_relation import (
    AVPC1_RELATION_CONTRACT_DIGEST,
    AVPC1_RELATION_PREFLIGHT_DIGEST,
    AVPC1_RELATION_SCHEMA_VERSION,
    AVPC1BoundedRelationState,
    AVPC1ReadOnlyRelationFinding,
    _digest as _relation_digest,
    advance_avpc1_bounded_relation_state,
)
from mcm_field_organism._avpc1_visual_prototype_resolver import (
    AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
    AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH,
    AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE,
    AVPC1VisualPrototypeResolverError,
    resolve_avpc1_visual_prototype_state,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_s1wq_perceptual_state_lifecycle import (
    _state_identity_payload,
)
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    _prototype_digest,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tests.test_s2bq_private_avpc1_bounded_relation import (
    _Fixture,
    _advance_all,
    _parameters,
)


ROOT = Path(__file__).resolve().parents[1]


def _stable_fixture():
    fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
    state, _ = _advance_all(
        fixture,
        fixture.state("candidate.resolver.table"),
    )
    finding = fixture.audio_only_probe(-0.5, state)
    return fixture, state, finding


def _rebuild_relation_state(
    state: AVPC1BoundedRelationState,
    **updates,
) -> AVPC1BoundedRelationState:
    values = {
        name: getattr(state, name)
        for name in state.__dataclass_fields__
        if name != "state_digest"
    }
    values.update(updates)
    digest_values = {
        key: value
        for key, value in values.items()
        if key != "relation_partition"
    }
    digest_values["auditory_prototype_inventory"] = list(
        digest_values["auditory_prototype_inventory"]
    )
    digest_values["visual_prototype_inventory"] = list(
        digest_values["visual_prototype_inventory"]
    )
    digest_values["consumed_exposure_receipt_digests"] = list(
        digest_values["consumed_exposure_receipt_digests"]
    )
    digest_values["slots"] = [slot.payload() for slot in digest_values["slots"]]
    payload = {
        "schema_version": AVPC1_RELATION_SCHEMA_VERSION,
        "contract_digest": AVPC1_RELATION_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_RELATION_PREFLIGHT_DIGEST,
        **digest_values,
    }
    return AVPC1BoundedRelationState(
        **values,
        state_digest=_relation_digest(payload),
    )


def _rebuild_finding(
    finding: AVPC1ReadOnlyRelationFinding,
    **updates,
) -> AVPC1ReadOnlyRelationFinding:
    values = {
        name: getattr(finding, name)
        for name in finding.__dataclass_fields__
        if name != "finding_digest"
    }
    values.update(updates)
    payload = {"schema_version": AVPC1_RELATION_SCHEMA_VERSION, **values}
    return AVPC1ReadOnlyRelationFinding(
        **values,
        finding_digest=_relation_digest(payload),
    )


def _rebind_visual_bank(state, finding, visual_bank_state):
    identity = _relation_digest(_state_identity_payload(visual_bank_state))
    rebound_state = _rebuild_relation_state(
        state,
        visual_bank_state_identity_digest=identity,
        visual_bank_state_digest=visual_bank_state.digest(),
    )
    rebound_finding = _rebuild_finding(
        finding,
        observed_relation_state_digest=rebound_state.state_digest,
        frozen_visual_bank_state_digest=visual_bank_state.digest(),
    )
    return rebound_state, rebound_finding


class S2BVPrivateAVPC1VisualPrototypeResolverTests(unittest.TestCase):
    def test_valid_match_resolves_exact_stable_visual_values_and_support(self) -> None:
        fixture, state, finding = _stable_fixture()
        output = resolve_avpc1_visual_prototype_state(
            "resolver.synthetic.visual.v1",
            finding,
            state,
            fixture.profile,
            fixture.visual_state,
        )
        expected = next(
            slot
            for slot in fixture.visual_state.slots
            if slot.occupied
            and _prototype_digest(slot.prototype_values)
            == finding.visual_prototype_identity_digest
        )
        self.assertEqual("visual", output.modality_id)
        self.assertEqual(expected.slot_id, output.visual_prototype_slot_id)
        self.assertEqual(expected.prototype_values, output.prototype_values)
        self.assertEqual(expected.support_count, output.support_count)
        self.assertEqual(
            finding.visual_prototype_identity_digest,
            output.visual_prototype_identity_digest,
        )

    def test_output_binds_sources_is_frozen_and_self_validating(self) -> None:
        fixture, state, finding = _stable_fixture()
        before = (
            finding.finding_digest,
            state.state_digest,
            fixture.profile.digest(),
            fixture.visual_state.digest(),
        )
        output = resolve_avpc1_visual_prototype_state(
            "resolver.synthetic.visual.v1",
            finding,
            state,
            fixture.profile,
            fixture.visual_state,
        )
        self.assertEqual(finding.finding_digest, output.relation_finding_digest)
        self.assertEqual(state.state_digest, output.observed_relation_state_digest)
        self.assertEqual(fixture.profile.digest(), output.profile_binding_digest)
        self.assertEqual(fixture.visual_state.digest(), output.visual_bank_state_digest)
        self.assertEqual(before, (
            finding.finding_digest,
            state.state_digest,
            fixture.profile.digest(),
            fixture.visual_state.digest(),
        ))
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            output.support_count = 4  # type: ignore[misc]

    def test_no_match_and_conflict_findings_fail_closed(self) -> None:
        pending_fixture = _Fixture(((-0.5, 0.5),))
        pending_state = pending_fixture.state("candidate.pending.resolver.table")
        pending_state = advance_avpc1_bounded_relation_state(
            "transition.pending.resolver.1",
            pending_state,
            pending_fixture.receipt(0, pending_state),
        ).state
        no_match = pending_fixture.audio_only_probe(-0.5, pending_state)
        conflict_fixture = _Fixture(((-0.5, -0.5), (-0.5, 0.5)))
        conflict_state, _ = _advance_all(
            conflict_fixture,
            conflict_fixture.state("candidate.conflict.resolver.table"),
        )
        conflict = conflict_fixture.audio_only_probe(-0.5, conflict_state)
        for fixture, state, finding in (
            (pending_fixture, pending_state, no_match),
            (conflict_fixture, conflict_state, conflict),
        ):
            with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
                resolve_avpc1_visual_prototype_state(
                    "resolver.synthetic.visual.v1",
                    finding,
                    state,
                    fixture.profile,
                    fixture.visual_state,
                )
            self.assertEqual(
                AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH,
                caught.exception.code,
            )

    def test_relation_state_and_target_substitution_fail_closed(self) -> None:
        fixture, state, finding = _stable_fixture()
        foreign_state = _rebuild_relation_state(
            state,
            relation_table_id="candidate.foreign.resolver.table",
            state_identity_digest=_relation_digest({
                "schema_version": AVPC1_RELATION_SCHEMA_VERSION,
                "relation_table_id": "candidate.foreign.resolver.table",
                "slot_ids": [
                    "avpc1.relation.slot.000",
                    "avpc1.relation.slot.001",
                ],
                "relation_slot_capacity": 2,
                "support_required": 2,
                "exposure_budget": 4,
            }),
        )
        with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
            resolve_avpc1_visual_prototype_state(
                "resolver.synthetic.visual.v1",
                finding,
                foreign_state,
                fixture.profile,
                fixture.visual_state,
            )
        self.assertEqual(AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH, caught.exception.code)

        other_target = state.visual_prototype_inventory[0]
        changed_finding = _rebuild_finding(
            finding,
            visual_prototype_identity_digest=other_target,
        )
        with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
            resolve_avpc1_visual_prototype_state(
                "resolver.synthetic.visual.v1",
                changed_finding,
                state,
                fixture.profile,
                fixture.visual_state,
            )
        self.assertEqual(AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH, caught.exception.code)

    def test_profile_and_visual_bank_substitution_fail_closed(self) -> None:
        fixture, state, finding = _stable_fixture()
        controlled = bind_ppb1_receptor_profile("controlled", _parameters())
        with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
            resolve_avpc1_visual_prototype_state(
                "resolver.synthetic.visual.v1",
                finding,
                state,
                controlled,
                fixture.visual_state,
            )
        self.assertEqual(AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH, caught.exception.code)

        changed_visual = replace(
            fixture.visual_state,
            accepted_step_count=4,
        )
        with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
            resolve_avpc1_visual_prototype_state(
                "resolver.synthetic.visual.v1",
                finding,
                state,
                fixture.profile,
                changed_visual,
            )
        self.assertEqual(AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH, caught.exception.code)

    def test_absent_duplicated_and_unstable_targets_fail_closed(self) -> None:
        fixture, state, finding = _stable_fixture()
        target = finding.visual_prototype_identity_digest
        target_index = next(
            index
            for index, slot in enumerate(fixture.visual_state.slots)
            if slot.occupied
            and _relation_digest({
                "normalized_prototype_values": list(slot.prototype_values)
            }) == target
        )
        target_slot = fixture.visual_state.slots[target_index]
        variants = []

        absent_slots = list(fixture.visual_state.slots)
        absent_slots[target_index] = replace(
            target_slot,
            prototype_values=tuple(0.25 for _ in target_slot.prototype_values),
        )
        variants.append(replace(fixture.visual_state, slots=tuple(absent_slots)))

        duplicate_slots = list(fixture.visual_state.slots)
        duplicate_slots[1] = replace(
            duplicate_slots[1],
            prototype_values=target_slot.prototype_values,
        )
        variants.append(replace(fixture.visual_state, slots=tuple(duplicate_slots)))

        unstable_slots = list(fixture.visual_state.slots)
        unstable_slots[target_index] = replace(target_slot, support_count=2)
        variants.append(replace(fixture.visual_state, slots=tuple(unstable_slots)))

        for visual_state in variants:
            rebound_state, rebound_finding = _rebind_visual_bank(
                state,
                finding,
                visual_state,
            )
            with self.assertRaises(AVPC1VisualPrototypeResolverError) as caught:
                resolve_avpc1_visual_prototype_state(
                    "resolver.synthetic.visual.v1",
                    rebound_finding,
                    rebound_state,
                    fixture.profile,
                    visual_state,
                )
            self.assertEqual(
                AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE,
                caught.exception.code,
            )

    def test_resolution_preserves_all_input_digests(self) -> None:
        fixture, state, finding = _stable_fixture()
        before = (
            finding.finding_digest,
            state.state_digest,
            fixture.profile.digest(),
            fixture.profile.visual_config.digest(),
            fixture.visual_state.digest(),
        )
        resolve_avpc1_visual_prototype_state(
            "resolver.synthetic.visual.v1",
            finding,
            state,
            fixture.profile,
            fixture.visual_state,
        )
        self.assertEqual(before, (
            finding.finding_digest,
            state.state_digest,
            fixture.profile.digest(),
            fixture.profile.visual_config.digest(),
            fixture.visual_state.digest(),
        ))

    def test_private_module_has_no_update_public_field_or_filesystem_path(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_avpc1_visual_prototype_resolver.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_ppb1_bank",
            "advance_s1wq_perceptual_state",
            "normalized_mean_l1_distance",
            "SharedMCMField",
            "MCMNeuronDrive",
            "current_api",
            "root_lazy_exports",
            "live_audio",
            "live_video",
            "open(",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(any("avpc1" in name.lower() for name in public_names))


if __name__ == "__main__":
    unittest.main()
