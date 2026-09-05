from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2ly_private_two_view_projection as projection
from tools import _s2ma_private_arecent_two_view_integration as integration
from tools import _s2mb_private_bstable_two_view as bstable
from tools import _s2mb_private_bstable_two_view_runner as s2mb
from tools import _s2mc_private_learning_lifecycle as subject
from tools import _s2mc_private_learning_lifecycle_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2mc-role-free-lifecycle-qualification-20260905-02"


class S2MCLearningLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = s2mb._load_record(WORKSPACE_ROOT, s2mb.PLAN_BINDING, "plan_digest")
        cls.masks = {
            item["mask_id"]: item for item in cls.plan["mask_root"]["masks"]
        }
        cls.geometry_digest = s2mb._geometry_digest(s2mb.VisualGridConfig(), cls.masks)
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
        cls.memory_digest = subject._digest({"memory": "neutral-state"})

    def _look(
        self,
        mask_id: str,
        tick: int,
        owner: str,
        *,
        source_id: str = "neutral-source",
    ) -> integration.ARecentObservedLookV1:
        mask = self.masks[mask_id]
        view = projection.bind_observed_view(
            self.values,
            mask_id,
            tuple(mask["positions"]),
            mask["mask_digest"],
        )
        payload_digest = hashlib.sha256(source_id.encode("ascii")).hexdigest()
        return integration.ARecentObservedLookV1(
            owner,
            subject._digest({"case": "neutral-case"}),
            subject._digest({"observation": owner}),
            source_id,
            payload_digest,
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

    def _pair(self) -> tuple[integration.ARecentObservedLookV1, integration.ARecentObservedLookV1]:
        return (
            self._look("VIEW_A_96", 1, "neutral-owner-a"),
            self._look("VIEW_B_96", 2, "neutral-owner-b"),
        )

    def _candidate_set(
        self,
        form: tuple[float, ...],
        *,
        radius: float = 0.0,
    ) -> bstable.BStableVisualCandidateSetV1:
        candidate_payload = {
            "schema": bstable.SCHEMA,
            "slot_id": "slot-00",
            "support": 3,
            "slot_digest": "1" * 64,
            "prototype_values_digest": "2" * 64,
            "form_values": list(form),
            "form_values_digest": bstable._digest(list(form)),
            "calibration_id": "neutral-calibration",
            "calibration_radius": radius,
            "calibration_digest": "3" * 64,
        }
        candidate = bstable.BStableVisualCandidateV1(
            "slot-00",
            3,
            "1" * 64,
            "2" * 64,
            form,
            candidate_payload["form_values_digest"],
            "neutral-calibration",
            radius,
            "3" * 64,
            bstable._digest(candidate_payload),
        )
        set_payload = {
            "schema": bstable.SCHEMA,
            "config_digest": "4" * 64,
            "memory_state_digest": self.memory_digest,
            "union_mask_digest": self.masks["UNION_192"]["mask_digest"],
            "union_positions": list(self.masks["UNION_192"]["positions"]),
            "candidate_digests": [candidate.candidate_digest],
            "prestate_digest": self.memory_digest,
            "poststate_digest": self.memory_digest,
        }
        return bstable.BStableVisualCandidateSetV1(
            "4" * 64,
            self.memory_digest,
            self.masks["UNION_192"]["mask_digest"],
            tuple(self.masks["UNION_192"]["positions"]),
            (candidate,),
            self.memory_digest,
            self.memory_digest,
            bstable._digest(set_payload),
        )

    def _decide(self, *, candidates=None, pair=None, direct=False):
        first, second = self._pair() if pair is None else pair
        function = subject.direct_lifecycle_baseline if direct else subject.decide_lifecycle_context
        return function(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
            union_mask_digest=self.masks["UNION_192"]["mask_digest"],
            union_positions=tuple(self.masks["UNION_192"]["positions"]),
            memory_prestate_digest=self.memory_digest,
            memory_poststate_digest=self.memory_digest,
        )

    def test_01_neutral_event_scope_and_gate(self) -> None:
        self.assertEqual((len(runner.EVENT_SPECS), runner.MAX_RESULT_BYTES), (21, 262_144))
        self.assertEqual(sum(item[1] == "COMPLETE_AV_PERCEPTION" for item in runner.EVENT_SPECS), 13)
        self.assertFalse(runner.RUN_ENABLED)
        encoded = json.dumps(runner.EVENT_SPECS).lower()
        self.assertNotIn("target", encoded)
        self.assertNotIn("distractor", encoded)
        self.assertNotIn("pressure", encoded)

    def test_02_valid_empty_inventory_is_absent(self) -> None:
        product = self._decide()
        direct = self._decide(direct=True)
        self.assertEqual(
            (product.status, product.reason, product.evidence_status),
            ("ABSTAINED", "NO_STABLE_CONTEXT", "ABSENT_VALID"),
        )
        self.assertEqual(product.decision_digest, direct.decision_digest)

    def test_03_invalid_pair_is_not_valid_absence(self) -> None:
        first, second = self._pair()
        second = replace(second, source_id="different-source")
        product = self._decide(pair=(first, second))
        direct = self._decide(pair=(first, second), direct=True)
        self.assertEqual(
            (product.reason, product.evidence_status),
            ("PAIR_INCOMPATIBLE_NO_UNION", "PAIR_INVALID"),
        )
        self.assertEqual(product.decision_digest, direct.decision_digest)

    def test_04_single_real_candidate_is_admitted(self) -> None:
        candidates = self._candidate_set(self.form)
        product = self._decide(candidates=candidates)
        direct = self._decide(candidates=candidates, direct=True)
        self.assertEqual((product.status, product.selected_slot_id), ("ADMITTED", "slot-00"))
        self.assertEqual(product.decision_digest, direct.decision_digest)

    def test_05_nonmatching_candidate_is_rejected(self) -> None:
        candidates = self._candidate_set(tuple(1.0 / 144.0 for _ in range(144)))
        product = self._decide(candidates=candidates)
        direct = self._decide(candidates=candidates, direct=True)
        self.assertEqual((product.status, product.reason), ("ABSTAINED", "NO_MODEL_WITHIN_ENVELOPE"))
        self.assertEqual(product.decision_digest, direct.decision_digest)

    def test_06_candidate_state_mismatch_fails_closed(self) -> None:
        candidates = self._candidate_set(self.form)
        with self.assertRaises(subject.S2MCLifecycleError):
            subject.decide_lifecycle_context(
                first=self._pair()[0],
                second=self._pair()[1],
                candidates=candidates,
                geometry_digest=self.geometry_digest,
                view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
                view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
                union_mask_digest=self.masks["UNION_192"]["mask_digest"],
                union_positions=tuple(self.masks["UNION_192"]["positions"]),
                memory_prestate_digest="5" * 64,
                memory_poststate_digest="5" * 64,
            )

    def test_07_memory_mutation_and_missing_field_fail_closed(self) -> None:
        first, second = self._pair()
        with self.assertRaises(subject.S2MCLifecycleError):
            subject.decide_lifecycle_context(
                first=first,
                second=second,
                candidates=None,
                geometry_digest=self.geometry_digest,
                view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
                view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
                union_mask_digest=self.masks["UNION_192"]["mask_digest"],
                union_positions=tuple(self.masks["UNION_192"]["positions"]),
                memory_prestate_digest=self.memory_digest,
                memory_poststate_digest="6" * 64,
            )
        with self.assertRaises(subject.S2MCLifecycleError):
            self._decide(pair=(replace(first, field_contact_digest=None), second))

    def test_08_result_is_immutable_and_bounded(self) -> None:
        result = self._decide(candidates=self._candidate_set(self.form))
        encoded = json.dumps(
            result.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        self.assertLess(len(encoded), 4_096)
        with self.assertRaises(FrozenInstanceError):
            result.status = "ABSTAINED"

    def test_09_pre_contact_accepts_first_visual_field_event(self) -> None:
        prior = s2mb._load_record(
            WORKSPACE_ROOT,
            s2mb.S2LZ_RESULT_BINDING,
            "comparison_digest",
        )
        config = s2mb._build_config()
        sources = s2mb._SourceStream(config=config, plan=self.plan, prior=prior)
        case = self.plan["execution_root"]["cases"][0]
        look, field_input = sources.visual_look(
            source_id="source-005",
            case_plan_digest=case["case_plan_digest"],
            mask=self.masks["VIEW_A_96"],
            geometry_digest=self.geometry_digest,
            look_tick=1,
            field_contact_digest=None,
        )
        pre_contact = runner._initial_pre_contact_field_state(config)
        event = s2mb._field_event(
            ordinal=1,
            event_type="PARTIAL_VISUAL_CUE",
            source_digest=subject._digest({"source": "neutral"}),
            perception_digest=field_input.perception_digest,
            field_input=field_input,
            operation_payload=look,
        )
        result = s2mb.field_runtime.build_s2lo_field_adapter()(pre_contact, event)
        self.assertEqual((pre_contact.phase, pre_contact.step_count), ("PRE_CONTACT", 0))
        self.assertEqual((result.poststate.phase, result.poststate.step_count), ("COMPLETED", 1))
        self.assertIsNone(pre_contact.field.last_distribution)


if __name__ == "__main__":
    unittest.main()
