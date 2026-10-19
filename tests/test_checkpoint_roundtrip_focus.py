"""Four independent read-only controls; no replay, processes or payload analysis."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import unittest

from tools import _memory_checkpoint as c

OLD=c.b.ROOT/"reports/memory-checkpoint-qualification-20260912-02"


class RoundtripControls(unittest.TestCase):
    def setUp(self):
        # A fresh evidence copy for each independent control, no shared mutation.
        self.value=c.read_checkpoint(OLD/"checkpoint.json")
        self.manifest=c.b.decode_manifest(self.value["manifest"])
        self.code=json.loads((OLD/"preregistration.json").read_bytes())["code_digest"]

    def test_native_types(self):
        state,config=c.validate(self.value,self.manifest,self.code)
        self.assertIs(type(state),c.r.ng.stream.PerceptionStreamStateV1)
        self.assertIs(type(state.memory_state),c.r.memory.S2JVCompositeStateV1)
        self.assertIs(type(state.field_state),c.r.ng.field.S2LOFieldStateV1)
        c.r.memory._validate_state(config,state.memory_state)

    def test_memory_canonical_roundtrip(self):
        state,_=c.validate(self.value,self.manifest,self.code)
        encoded=c.b.state_wire.encode(asdict(state.memory_state))
        stored=self.value["prefix"]["states"][state.memory_state_digest]
        self.assertEqual(c.b.canonical(encoded),c.b.canonical(stored))
        decoded=c.b.state_wire.decode(encoded)
        self.assertEqual(c.b.canonical(decoded),c.b.canonical(asdict(state.memory_state)))
        self.assertEqual(encoded["native_sha256"],stored["native_sha256"])

    def test_field_canonical_roundtrip(self):
        state,_=c.validate(self.value,self.manifest,self.code)
        snapshot=state.field_state.field.snapshot()
        self.assertEqual(c.b.canonical(snapshot.canonical_payload()),c.b.canonical(self.value["field"]))
        restored=c.restore_shared_mcm_field(c.SharedMCMFieldSnapshot.from_json(snapshot.to_json()))
        self.assertEqual(restored.snapshot().to_json(),snapshot.to_json())
        self.assertEqual(snapshot.digest(),self.value["field_wrapper"]["field_component_digest"])

    def test_evidence_unchanged(self):
        before=deepcopy(self.value)
        native,_=c.validate(self.value,self.manifest,self.code)
        c.b.state_wire.decode(c.b.state_wire.encode(asdict(native.memory_state)))
        c.restore_shared_mcm_field(native.field_state.field.snapshot())
        self.assertEqual(self.value,before)
        self.assertEqual(c.b.canonical(self.value),c.b.canonical(before))
