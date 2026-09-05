from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2jx_default_live_memory_fixtures as fixtures
from tools import _s2ly_private_two_view_projection as projection
from tools import _s2ma_private_arecent_two_view_integration as integration
from tools import _s2mb_private_bstable_two_view as subject
from tools import _s2mb_private_bstable_two_view_runner as runner
from tools import _s2jw_profiled_memory_coordinator as coordinator


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2mb-bstable-two-view-qualification-20260905-01"


class S2MBBStableTwoViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = runner._load_record(WORKSPACE_ROOT, runner.PLAN_BINDING, "plan_digest")
        cls.masks = {item["mask_id"]: item for item in cls.plan["mask_root"]["masks"]}
        cls.geometry_digest = runner._geometry_digest(runner.VisualGridConfig(), cls.masks)
        cls.values = tuple(
            0.8 if 2 <= index // 36 <= 5 and 4 <= (index % 36) // 3 <= 7 else 0.1
            for index in range(288)
        )
        union = cls.masks["UNION_192"]
        union_view = projection.bind_observed_view(
            cls.values,
            "UNION_192",
            tuple(union["positions"]),
            union["mask_digest"],
        )
        cls.form = projection.project_mask_conditioned_form(union_view).values
        cls.config = runner._build_config()
        state = coordinator.initial_s2jv_composite_state(cls.config)
        fixture_stream = fixtures.S2JXFixtureStream(cls.config.profile)
        first_values = None
        for ordinal in range(4):
            pair = fixture_stream.materialize("X", ordinal)
            if first_values is None:
                first_values = tuple(pair.visual.timed_frame.frame.values)
            bound = coordinator.bind_s2jv_coordinator_input(config=cls.config, source=pair)
            owner = coordinator.S2JVFormationOwner(
                f"s2mb-neutral-owner-{ordinal:03d}",
                f"s2mb-neutral-auth-{ordinal:03d}",
                f"s2mb-neutral-consume-{ordinal:03d}",
                cls.config.config_digest,
                state.state_digest,
                bound.input_digest,
            )
            state = coordinator.advance_s2jv_atomic(
                config=cls.config,
                prestate=state,
                source=bound,
                owner=owner,
            ).poststate
        assert first_values is not None
        cls.memory_state = state
        cls.memory_values = first_values

    def _candidate(self, slot_id: str, form: tuple[float, ...]) -> subject.BStableVisualCandidateV1:
        payload = {
            "schema": subject.SCHEMA,
            "slot_id": slot_id,
            "support": 3,
            "slot_digest": "1" * 64,
            "prototype_values_digest": "2" * 64,
            "form_values": list(form),
            "form_values_digest": subject._digest(list(form)),
            "calibration_id": f"calibration-{slot_id}",
            "calibration_radius": 0.0,
            "calibration_digest": "3" * 64,
        }
        return subject.BStableVisualCandidateV1(
            slot_id,
            3,
            "1" * 64,
            "2" * 64,
            form,
            payload["form_values_digest"],
            payload["calibration_id"],
            0.0,
            "3" * 64,
            subject._digest(payload),
        )

    def _candidate_set(self, forms: tuple[tuple[float, ...], ...]) -> subject.BStableVisualCandidateSetV1:
        candidates = tuple(self._candidate(f"slot-{index:02d}", form) for index, form in enumerate(forms))
        payload = {
            "schema": subject.SCHEMA,
            "config_digest": "4" * 64,
            "memory_state_digest": "5" * 64,
            "union_mask_digest": self.masks["UNION_192"]["mask_digest"],
            "union_positions": list(self.masks["UNION_192"]["positions"]),
            "candidate_digests": [item.candidate_digest for item in candidates],
            "prestate_digest": "5" * 64,
            "poststate_digest": "5" * 64,
        }
        return subject.BStableVisualCandidateSetV1(
            "4" * 64,
            "5" * 64,
            self.masks["UNION_192"]["mask_digest"],
            tuple(self.masks["UNION_192"]["positions"]),
            candidates,
            "5" * 64,
            "5" * 64,
            subject._digest(payload),
        )

    def _look(self, mask_id: str, tick: int, owner: str) -> integration.ARecentObservedLookV1:
        mask = self.masks[mask_id]
        view = projection.bind_observed_view(
            self.values,
            mask_id,
            tuple(mask["positions"]),
            mask["mask_digest"],
        )
        return integration.ARecentObservedLookV1(
            owner,
            subject._digest({"case": "neutral-case"}),
            subject._digest({"owner": owner}),
            "neutral-source",
            hashlib.sha256(b"neutral-source").hexdigest(),
            self.geometry_digest,
            tick,
            mask_id,
            mask["mask_digest"],
            view.observed_positions,
            view.observed_values,
            view.observed_values_digest,
            view.source_values_digest,
            subject._digest({"field": owner}),
        )

    def _pair(self):
        return (
            self._look("VIEW_A_96", 10, "neutral-owner-a"),
            self._look("VIEW_B_96", 11, "neutral-owner-b"),
        )

    def test_01_scope_and_main_gate_are_fixed(self) -> None:
        self.assertEqual((len(runner.FORMATION_SOURCES), integration.MAX_VIEWS), (21, 2))
        self.assertFalse(runner.RUN_ENABLED)

    def test_02_real_stable_slot_projection_is_read_only(self) -> None:
        slot = next(item for item in self.memory_state.tspm_state.visual_ppb1_state.slots if item.occupied)
        expected = runner._repeat_prototype(self.memory_values, 2)
        binding = subject.BStableCalibrationBindingV1(
            slot.slot_id,
            "neutral-calibration",
            0.0,
            subject._digest({"calibration": "neutral"}),
            subject._digest(list(expected)),
        )
        before = self.memory_state.state_digest
        result = subject.bind_visual_bstable_candidates(
            config=self.config,
            state=self.memory_state,
            bindings=(binding,),
            union_mask_digest=self.masks["UNION_192"]["mask_digest"],
            union_positions=tuple(self.masks["UNION_192"]["positions"]),
        )
        self.assertEqual((len(result.candidates), result.candidates[0].support), (1, 3))
        self.assertEqual((before, result.prestate_digest, result.poststate_digest), (before, before, before))

    def test_03_wrong_prototype_transition_binding_fails_closed(self) -> None:
        slot = next(item for item in self.memory_state.tspm_state.visual_ppb1_state.slots if item.occupied)
        binding = subject.BStableCalibrationBindingV1(
            slot.slot_id,
            "neutral-calibration",
            0.0,
            "6" * 64,
            "7" * 64,
        )
        with self.assertRaises(subject.S2MBBStableError):
            subject.bind_visual_bstable_candidates(
                config=self.config,
                state=self.memory_state,
                bindings=(binding,),
                union_mask_digest=self.masks["UNION_192"]["mask_digest"],
                union_positions=tuple(self.masks["UNION_192"]["positions"]),
            )

    def test_04_missing_slot_binding_fails_closed(self) -> None:
        with self.assertRaises(subject.S2MBBStableError):
            subject.bind_visual_bstable_candidates(
                config=self.config,
                state=self.memory_state,
                bindings=(),
                union_mask_digest=self.masks["UNION_192"]["mask_digest"],
                union_positions=tuple(self.masks["UNION_192"]["positions"]),
            )

    def test_05_unique_real_candidate_form_is_admitted(self) -> None:
        candidates = self._candidate_set((self.form, tuple(1.0 / 144.0 for _ in range(144))))
        first, second = self._pair()
        direct = subject.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
        )
        self.assertEqual((direct["status"], direct["selected_model_id"]), ("ADMITTED", "slot-00"))

    def test_06_no_candidate_within_envelope_abstains(self) -> None:
        candidates = self._candidate_set((tuple(1.0 / 144.0 for _ in range(144)),))
        first, second = self._pair()
        direct = subject.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
        )
        self.assertEqual((direct["status"], direct["reason"]), ("ABSTAINED", "NO_MODEL_WITHIN_ENVELOPE"))

    def test_07_multiple_real_candidates_abstain(self) -> None:
        candidates = self._candidate_set((self.form, self.form))
        first, second = self._pair()
        direct = subject.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
        )
        self.assertEqual((direct["status"], direct["reason"]), ("ABSTAINED", "MULTIPLE_MODELS_WITHIN_ENVELOPE"))

    def test_08_source_conflict_abstains_and_preserves_field_receipts(self) -> None:
        candidates = self._candidate_set((self.form,))
        first, second = self._pair()
        second = replace(second, source_id="changed-source")
        direct = subject.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
        )
        self.assertEqual((direct["status"], direct["reason"]), ("ABSTAINED", "PAIR_INCOMPATIBLE_NO_UNION"))
        self.assertEqual((first.field_contact_digest, second.field_contact_digest), (subject._digest({"field": "neutral-owner-a"}), subject._digest({"field": "neutral-owner-b"})))

    def test_09_product_and_independent_baseline_are_digest_equal(self) -> None:
        candidates = self._candidate_set((self.form, tuple(1.0 / 144.0 for _ in range(144))))
        first, second = self._pair()
        product = integration.ARecentTransientTwoViewIntegrator(
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
            union_mask_digest=self.masks["UNION_192"]["mask_digest"],
            union_positions=tuple(self.masks["UNION_192"]["positions"]),
            model_envelopes=candidates.model_envelopes(),
        )
        product.process(first)
        actual = product.process(second)
        direct = subject.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
        )
        self.assertEqual(actual.open_set_decision_digest, direct["decision_digest"])

    def test_10_outputs_are_immutable_and_bounded(self) -> None:
        candidates = self._candidate_set((self.form,))
        encoded = json.dumps(candidates.payload_without_digest(), sort_keys=True, separators=(",", ":")).encode("ascii")
        self.assertLess(len(encoded), 32_768)
        with self.assertRaises(FrozenInstanceError):
            candidates.memory_state_digest = "0" * 64
        with self.assertRaises(subject.S2MBBStableError):
            replace(candidates.candidates[0], form_values_digest="0" * 64)


if __name__ == "__main__":
    unittest.main()
