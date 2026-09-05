from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2ly_private_two_view_projection as projection
from tools import _s2lz_private_open_set_comparison as open_set
from tools import _s2ma_private_arecent_two_view_integration as integration


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2ma-transient-arecent-integration-qualification-20260905-01"


class S2MATransientARecentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        plan = open_set._load_plan(WORKSPACE_ROOT)
        cls.masks = {item["mask_id"]: item for item in plan["mask_root"]["masks"]}
        cls.geometry_digest = integration._digest({"geometry": "neutral-8x12-rgb", "masks": sorted(item["mask_digest"] for item in cls.masks.values())})
        cls.full_values = tuple(
            0.8 if 2 <= index // 36 <= 5 and 4 <= (index % 36) // 3 <= 7 else 0.1
            for index in range(288)
        )
        cls.views = {
            mask_id: projection.bind_observed_view(cls.full_values, mask_id, tuple(cls.masks[mask_id]["positions"]), cls.masks[mask_id]["mask_digest"])
            for mask_id in ("VIEW_A_96", "VIEW_B_96")
        }
        union_values = cls.views["VIEW_A_96"].observed_values + cls.views["VIEW_B_96"].observed_values
        union_view = projection.ObservedVisualViewV1(
            mask_id="UNION_192",
            mask_digest=cls.masks["UNION_192"]["mask_digest"],
            source_values_digest=cls.views["VIEW_A_96"].source_values_digest,
            observed_positions=tuple(cls.masks["UNION_192"]["positions"]),
            observed_values=union_values,
            observed_values_digest=projection._digest(list(union_values)),
        )
        cls.form_values = projection.project_mask_conditioned_form(union_view).values

    def _integrator(self, models: dict[str, tuple[tuple[float, ...], float]] | None = None) -> integration.ARecentTransientTwoViewIntegrator:
        if models is None:
            models = {"model-01": (self.form_values, 0.0), "model-02": (tuple(1.0 / 144.0 for _ in range(144)), 0.0)}
        return integration.ARecentTransientTwoViewIntegrator(
            geometry_digest=self.geometry_digest,
            view_a_mask_digest=self.masks["VIEW_A_96"]["mask_digest"],
            view_b_mask_digest=self.masks["VIEW_B_96"]["mask_digest"],
            union_mask_digest=self.masks["UNION_192"]["mask_digest"],
            union_positions=tuple(self.masks["UNION_192"]["positions"]),
            model_envelopes=models,
        )

    def _look(self, mask_id: str, tick: int, owner: str, field_digest: str | None = None) -> integration.ARecentObservedLookV1:
        view = self.views[mask_id]
        return integration.ARecentObservedLookV1(
            owner_id=owner,
            case_plan_digest=integration._digest({"case": "neutral-case-01"}),
            source_observation_digest=integration._digest({"owner": owner, "tick": tick}),
            source_id="neutral-source-01",
            payload_sha256=hashlib.sha256(b"neutral-payload").hexdigest(),
            geometry_digest=self.geometry_digest,
            tick=tick,
            mask_id=mask_id,
            mask_digest=self.masks[mask_id]["mask_digest"],
            observed_positions=view.observed_positions,
            observed_values=view.observed_values,
            observed_values_digest=view.observed_values_digest,
            source_values_digest=view.source_values_digest,
            field_contact_digest=field_digest,
        )

    def test_01_contract_exposes_only_transient_a_recent_role(self) -> None:
        self.assertEqual((integration.AREA_ROLE, integration.MAX_VIEWS, integration.MAX_TICK_GAP), ("A_RECENT", 2, 1))
        self.assertNotIn("B_STABLE", integration.ARecentTwoViewResultV1.__annotations__)

    def test_02_first_view_is_pending_and_keeps_window_open(self) -> None:
        subject = self._integrator()
        result = subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        self.assertEqual((result.status, result.reason, subject.pending_count), ("PENDING", "WAITING_FOR_SECOND_VIEW", 1))
        self.assertFalse(result.window_discarded)

    def test_03_valid_second_view_admits_and_discards_window(self) -> None:
        subject = self._integrator()
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        result = subject.process(self._look("VIEW_B_96", 11, "neutral-owner-02"))
        self.assertEqual((result.status, result.selected_model_id), ("ADMITTED", "model-01"))
        self.assertTrue(result.window_discarded)
        self.assertEqual(subject.pending_count, 0)
        self.assertFalse(result.retained_for_b_stable)

    def test_04_no_applicable_model_abstains_and_discards(self) -> None:
        subject = self._integrator({"model-01": (tuple(0.0 for _ in range(144)), 0.0)})
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        result = subject.process(self._look("VIEW_B_96", 11, "neutral-owner-02"))
        self.assertEqual((result.status, result.reason), ("ABSTAINED", "NO_MODEL_WITHIN_ENVELOPE"))
        self.assertEqual(subject.pending_count, 0)

    def test_05_multiple_applicable_models_abstain(self) -> None:
        models = {"model-01": (self.form_values, 0.0), "model-02": (self.form_values, 0.0)}
        subject = self._integrator(models)
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        result = subject.process(self._look("VIEW_B_96", 11, "neutral-owner-02"))
        self.assertEqual((result.status, result.reason), ("ABSTAINED", "MULTIPLE_MODELS_WITHIN_ENVELOPE"))

    def test_06_source_change_abstains_and_clears(self) -> None:
        subject = self._integrator()
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        changed = replace(self._look("VIEW_B_96", 11, "neutral-owner-02"), source_id="neutral-source-02", payload_sha256=hashlib.sha256(b"other").hexdigest())
        result = subject.process(changed)
        self.assertEqual((result.status, result.clear_cause, subject.pending_count), ("ABSTAINED", "SOURCE_OR_PAYLOAD_CHANGED", 0))

    def test_07_geometry_or_mask_conflict_abstains_and_clears(self) -> None:
        subject = self._integrator()
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        changed = replace(self._look("VIEW_B_96", 11, "neutral-owner-02"), geometry_digest="f" * 64)
        result = subject.process(changed)
        self.assertEqual((result.status, result.clear_cause, subject.pending_count), ("ABSTAINED", "GEOMETRY_OR_MASK_BINDING_CONFLICT", 0))

    def test_08_expired_or_nonprogressing_window_abstains(self) -> None:
        for tick in (10, 12):
            subject = self._integrator()
            subject.process(self._look("VIEW_A_96", 10, f"neutral-owner-a-{tick}"))
            result = subject.process(self._look("VIEW_B_96", tick, f"neutral-owner-b-{tick}"))
            self.assertEqual((result.status, result.clear_cause, subject.pending_count), ("ABSTAINED", "WINDOW_EXPIRED", 0))

    def test_09_wrong_first_mask_never_opens_a_window(self) -> None:
        subject = self._integrator()
        result = subject.process(self._look("VIEW_B_96", 10, "neutral-owner-01"))
        self.assertEqual((result.status, result.clear_cause, subject.pending_count), ("ABSTAINED", "FIRST_ROLE_NOT_VIEW_A", 0))

    def test_10_event_owner_is_single_use(self) -> None:
        subject = self._integrator()
        look = self._look("VIEW_A_96", 10, "neutral-owner-01")
        subject.process(look)
        with self.assertRaises(integration.S2MAIntegrationError):
            subject.process(look)

    def test_11_existing_field_receipts_are_preserved_on_failure(self) -> None:
        first_field, second_field = "1" * 64, "2" * 64
        subject = self._integrator()
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01", first_field))
        changed = replace(self._look("VIEW_B_96", 11, "neutral-owner-02", second_field), source_id="neutral-source-02")
        result = subject.process(changed)
        self.assertEqual(result.field_contact_digests, (first_field, second_field))
        self.assertEqual(subject.pending_count, 0)

    def test_12_result_is_immutable_and_exactly_matches_direct_open_set_decision(self) -> None:
        subject = self._integrator()
        subject.process(self._look("VIEW_A_96", 10, "neutral-owner-01"))
        result = subject.process(self._look("VIEW_B_96", 11, "neutral-owner-02"))
        direct = open_set._open_set_decision(self.form_values, {"model-01": (self.form_values, 0.0), "model-02": (tuple(1.0 / 144.0 for _ in range(144)), 0.0)})
        self.assertEqual((result.status, result.selected_model_id, result.reason, result.open_set_decision_digest), (direct["status"], direct["selected_model_id"], direct["reason"], direct["decision_digest"]))
        with self.assertRaises(FrozenInstanceError):
            result.status = "ABSTAINED"


if __name__ == "__main__":
    unittest.main()
