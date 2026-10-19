import copy
import contextlib
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from tools import _s2ty_record as record
from tools import _s2ty_run_envelope as run
from tools import _s2ty_source_time_binding as binding
from tools import _s2ty_event_control as control
from tools import _s2ty_audio_materialization as audio


OWNERS = {"adapter": "neutral-adapter-owner", "direct": "neutral-direct-owner"}


def prepared():
    manifest = binding.source_manifest()
    return manifest, run.neutral_inputs(manifest)


def materialized_prepared():
    payload = np.zeros(4800, dtype="<f4").tobytes()
    manifest = copy.deepcopy(binding.source_manifest())
    manifest["source_reused"] = False
    for item in manifest["events"]:
        if "endpoint" in item:
            item["endpoint"]["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
    manifest = binding.reseal_manifest(manifest)
    def supplier(ordinal, endpoint):
        return payload
    return manifest, supplier


class Tests(unittest.TestCase):
    def test_complete_neutral_chain_has_distinct_owners_and_independent_verification(self):
        manifest, inputs = prepared()
        envelope = run.run_once(run_id="s2ty-neutral-chain-01", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual(envelope["status"], "COMPLETE")
        self.assertEqual(envelope["preflight"]["checked_endpoints"], 22)
        self.assertEqual(run.verify_envelope(envelope), {"status": "VERIFIED", "events": 26})
        self.assertEqual(envelope["budget"]["actual"]["branches"]["success"]["contributions"]["record"], len(record.canonical(envelope)))

    def test_source_failure_stops_before_event_control_with_endpoint_progress(self):
        manifest, inputs = prepared()
        inputs[5]["payload_sha256"] = "0" * 64
        envelope = run.run_once(run_id="s2ty-neutral-source-error", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual(envelope["status"], "NOT_EVALUABLE")
        self.assertEqual(envelope["failure"]["code"], "PAYLOAD_HASH_INVALID")
        self.assertIsNone(envelope["record"])
        self.assertEqual(envelope["failure"]["progress"]["arms"], {"adapter": 0, "direct": 0})
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_SOURCE_FAILURE")
        self.assertEqual(envelope["budget"]["actual"]["branches"]["failure"]["contributions"]["record"], len(record.canonical(envelope)))

    def test_swapped_endpoint_and_invented_source_failure_are_rejected(self):
        manifest, inputs = prepared()
        inputs[0]["payload_sha256"] = inputs[1]["payload_sha256"]
        envelope = run.run_once(run_id="s2ty-neutral-swapped-endpoint", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual(envelope["failure"]["code"], "PAYLOAD_HASH_INVALID")
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_SOURCE_FAILURE")
        envelope["failure"]["code"] = "PROFILE_INVALID"
        with self.assertRaises(run.S2TYRunError) as raised:
            run.verify_envelope(envelope)
        self.assertEqual(raised.exception.code, "FAILURE_INVALID")

    def test_time_failure_stops_before_event_control(self):
        manifest, inputs = prepared()
        manifest["events"][4]["runtime_time"] = 3
        envelope = run.run_once(run_id="s2ty-neutral-time-error", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual((envelope["status"], envelope["failure"]["code"]), ("NOT_EVALUABLE", "RUNTIME_TIME_INVALID"))
        self.assertEqual(envelope["failure"]["progress"]["arms"], {"adapter": 0, "direct": 0})
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_SOURCE_FAILURE")

    def test_code_binding_and_distinct_owners_are_required(self):
        manifest, inputs = prepared()
        with self.assertRaises(run.S2TYRunError) as code_error:
            run.run_once(run_id="s2ty-neutral-code-error", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes={})
        self.assertEqual(code_error.exception.code, "CODE_BINDING_INVALID")
        with self.assertRaises(run.S2TYRunError) as owner_error:
            run.run_once(run_id="s2ty-neutral-owner-error", manifest=manifest, supplied_events=inputs, owners={"adapter": "same", "direct": "same"}, expected_code_hashes=run.code_hashes())
        self.assertEqual(owner_error.exception.code, "RUN_BINDING_INVALID")

    def test_envelope_manipulation_is_rejected(self):
        manifest, inputs = prepared()
        envelope = run.run_once(run_id="s2ty-neutral-manipulation", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        mutations = (
            ("time", lambda document: document["source_manifest"]["events"][0].update(runtime_time=99), "RUNTIME_TIME_INVALID"),
            ("record-owner", lambda document: document["record"].update(owner={"adapter": "wrong", "direct": "wrong"}), "RUN_BINDING_INVALID"),
            ("handoff-value", lambda document: document["handoffs"][0].update(half_values_digest="0" * 64), "HANDOFF_VALUES_INVALID"),
            ("segment", lambda document: document["record"]["inputs"][0].update(segment="other"), "INNER_EVENT_BINDING_INVALID"),
            ("formation-hint", lambda document: document["record"]["inputs"][0].update(kind="HINT"), "INNER_EVENT_BINDING_INVALID"),
            ("early-close", lambda document: document["record"]["inputs"][3].update(kind="CLOSE"), "INNER_EVENT_BINDING_INVALID"),
            ("success-status", lambda document: document["record"].update(status="NOT_EVALUABLE"), "RUN_BINDING_INVALID"),
        )
        for name, mutate, code in mutations:
            with self.subTest(name=name):
                document = copy.deepcopy(envelope)
                mutate(document)
                with self.assertRaises(run.S2TYRunError) as raised:
                    run.verify_envelope(document)
                self.assertEqual(raised.exception.code, code)

    def test_control_failure_after_direct_arm_progress_uses_failure_verifier(self):
        original = control.tw.ExactConfirmationStore

        class DirectFailureStore(original):
            instances = []

            def __init__(self, *args):
                super().__init__(*args)
                DirectFailureStore.instances.append(self)

            def form(self, frame):
                result = super().form(frame)
                if self is DirectFailureStore.instances[1]:
                    raise RuntimeError("direct-after-change")
                return result

        manifest, inputs = prepared()
        with patch.object(control.tw, "ExactConfirmationStore", DirectFailureStore):
            envelope = run.run_once(run_id="s2ty-neutral-control-error", manifest=manifest, supplied_events=inputs, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual(envelope["status"], "NOT_EVALUABLE")
        self.assertEqual(envelope["record"]["result"]["failure"]["progress"]["arms"]["direct"]["returned_steps"], 0)
        self.assertTrue(envelope["record"]["result"]["failure"]["progress"]["arms"]["direct"]["changed_without_return"])
        self.assertEqual(run.verify_envelope(envelope), {"status": "VERIFIED_CONTROL_FAILURE", "completed": 0})
        envelope["record"]["status"] = "COMPLETE"
        with self.assertRaises(run.S2TYRunError) as raised:
            run.verify_envelope(envelope)
        self.assertEqual(raised.exception.code, "RUN_BINDING_INVALID")

    def test_materialized_neutral_chain_records_hash_receptor_and_nj_calls(self):
        manifest, supplier = materialized_prepared()
        with contextlib.ExitStack() as stack:
            hash_spy = stack.enter_context(patch.object(audio, "_pcm_sha256", wraps=audio._pcm_sha256))
            analyze_spy = stack.enter_context(patch.object(audio.LogSpectralReceptor, "analyze", autospec=True, wraps=audio.LogSpectralReceptor.analyze))
            nj_spy = stack.enter_context(patch.object(audio.nj, "project_auditory_half_v1", wraps=audio.nj.project_auditory_half_v1))
            envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized", manifest=manifest, payload_supplier=supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual(envelope["status"], "COMPLETE")
        self.assertEqual(envelope["materialization"]["counts"], {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22})
        self.assertEqual((hash_spy.call_count, analyze_spy.call_count, nj_spy.call_count), (22, 22, 22))
        self.assertLessEqual(envelope["budget"]["actual"]["branches"]["success"]["contributions"]["record"], envelope["budget"]["reserves"]["record"])
        observation_path = os.environ.get("S2TY_FORMAL_OBSERVATION_PATH")
        if observation_path is not None:
            Path(observation_path).write_text(json.dumps({
                "counts": envelope["materialization"]["counts"],
                "native_payload_bytes": envelope["budget"]["actual"]["native_payload_bytes"],
                "materializer_workspace": envelope["budget"]["actual"]["materializer_workspace"],
                "success_branch": envelope["budget"]["actual"]["branches"]["success"],
                "record_reserve_bytes": envelope["budget"]["reserves"]["record"],
            }, sort_keys=True, separators=(",", ":")), encoding="ascii")
        self.assertEqual(run.verify_envelope(envelope), {"status": "VERIFIED", "events": 26})

    def test_materialized_hash_receptor_and_nj_failures_stop_before_memory(self):
        manifest, supplier = materialized_prepared()
        envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-hash", manifest=manifest, payload_supplier=lambda ordinal, endpoint: b"x" * 19200, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual((envelope["failure"]["code"], envelope["failure"]["phase"]), ("PCM_HASH_INVALID", "PCM"))
        self.assertEqual(envelope["materialization"]["counts"], {"pcm_hashes": 1, "audio_analyses": 0, "nj_projections": 0})
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_MATERIALIZATION_FAILURE")
        for name, target, code, phase in (
            ("receptor", "analyze", "RuntimeError", "RECEPTOR"),
            ("nj", "project_auditory_half_v1", "RuntimeError", "NJ"),
        ):
            with self.subTest(name=name):
                if target == "analyze":
                    context = patch.object(audio.LogSpectralReceptor, target, side_effect=RuntimeError("neutral-" + name))
                else:
                    context = patch.object(audio.nj, target, side_effect=RuntimeError("neutral-" + name))
                with context:
                    envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-" + name, manifest=manifest, payload_supplier=supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
                self.assertEqual((envelope["failure"]["code"], envelope["failure"]["phase"]), (code, phase))
                self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_MATERIALIZATION_FAILURE")

    def test_materialization_failure_counts_follow_direct_call_steps_not_phase(self):
        manifest, supplier = materialized_prepared()
        cases = (
            ("not-bytes", lambda: (lambda ordinal, endpoint: "not-bytes"), None, ("PCM_FORM_INVALID", "PCM", "NONE", {"pcm_hashes": 0, "audio_analyses": 0, "nj_projections": 0})),
            ("before-analyze", lambda: supplier, patch.object(audio.np, "frombuffer", side_effect=RuntimeError("neutral-before-analyze")), ("RuntimeError", "RECEPTOR", "HASH", {"pcm_hashes": 1, "audio_analyses": 0, "nj_projections": 0})),
            ("before-nj", lambda: supplier, patch.object(audio, "AuditoryReceptorState", side_effect=RuntimeError("neutral-before-nj")), ("RuntimeError", "NJ", "ANALYZE", {"pcm_hashes": 1, "audio_analyses": 1, "nj_projections": 0})),
        )
        for name, make_supplier, context, expected in cases:
            with self.subTest(name=name):
                with contextlib.ExitStack() as stack:
                    if context is not None:
                        stack.enter_context(context)
                    envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-step-" + name, manifest=manifest, payload_supplier=make_supplier(), owners=OWNERS, expected_code_hashes=run.code_hashes())
                self.assertEqual((envelope["failure"]["code"], envelope["failure"]["phase"], envelope["materialization"]["reached_step"], envelope["materialization"]["counts"]), expected)
                self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_MATERIALIZATION_FAILURE")

    def test_materialized_source_failure_keeps_prior_receipts_and_direct_counts(self):
        manifest, supplier = materialized_prepared()
        calls = 0

        def failing_supplier(ordinal, endpoint):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("neutral-source-unavailable")
            return supplier(ordinal, endpoint)

        envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-source", manifest=manifest, payload_supplier=failing_supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual((envelope["failure"]["code"], envelope["failure"]["phase"]), ("OSError", "SOURCE_BINDING"))
        self.assertEqual(envelope["materialization"]["counts"], {"pcm_hashes": 2, "audio_analyses": 2, "nj_projections": 2})
        self.assertEqual(len(envelope["materialization"]["receipts"]), 2)
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_MATERIALIZATION_FAILURE")

    def test_materialized_manifest_failure_is_verified_without_revalidation_escape(self):
        manifest, supplier = materialized_prepared()
        manifest["events"][0]["runtime_time"] = 77
        envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-manifest", manifest=manifest, payload_supplier=supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertEqual((envelope["failure"]["code"], envelope["failure"]["phase"]), ("RUNTIME_TIME_INVALID", "SOURCE_BINDING"))
        self.assertEqual(run.verify_envelope(envelope), {"status": "VERIFIED_MATERIALIZATION_MANIFEST_FAILURE", "attempted": None})

    def test_materialized_control_failure_uses_record_failure_verifier(self):
        original = control.tw.ExactConfirmationStore

        class DirectFailureStore(original):
            instances = []

            def __init__(self, *args):
                super().__init__(*args)
                DirectFailureStore.instances.append(self)

            def form(self, frame):
                result = super().form(frame)
                if self is DirectFailureStore.instances[1]:
                    raise RuntimeError("materialized-direct-after-change")
                return result

        manifest, supplier = materialized_prepared()
        with patch.object(control.tw, "ExactConfirmationStore", DirectFailureStore):
            envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-control", manifest=manifest, payload_supplier=supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
        self.assertIsNotNone(envelope["record"])
        self.assertEqual(envelope["materialization"]["counts"], {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22})
        self.assertEqual(run.verify_envelope(envelope)["status"], "VERIFIED_CONTROL_FAILURE")

    def test_materialization_receipt_digest_bindings_reject_manipulation(self):
        manifest, supplier = materialized_prepared()
        envelope = run.run_materialized_once(run_id="s2ty-neutral-materialized-receipt", manifest=manifest, payload_supplier=supplier, owners=OWNERS, expected_code_hashes=run.code_hashes())
        mutations = (
            ("raw", lambda receipt: receipt.update(raw_state_digest="0" * 64)),
            ("projection", lambda receipt: receipt.update(projection_digest="0" * 64)),
            ("values", lambda receipt: receipt["half_values_hex"].__setitem__(0, 0.5.hex())),
            ("profile", lambda receipt: receipt["projection_binding"].update(profile_digest="0" * 64)),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                document = copy.deepcopy(envelope)
                mutate(document["materialization"]["receipts"][0])
                with self.assertRaises(run.S2TYRunError) as raised:
                    run.verify_envelope(document)
                self.assertEqual(raised.exception.code, "MATERIALIZATION_RECEIPT_INVALID")
