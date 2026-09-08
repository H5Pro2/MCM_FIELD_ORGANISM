"""Neutral reduced values only. No NT payloads, materialization files or sensors."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2nt_private_comparison as c
from tools import _s2nt_private_comparison_verification as v
from tools import _s2nt_private_order_evaluation as e
from tools import _s2nt_private_comparison_run as run

b = c.b


def reseal(value,key):
    value.pop(key,None)
    value[key] = c.digest(value)
    return value


def bytes_digest(values):
    return hashlib.sha256(struct.pack("<48d",*values)).hexdigest()


def refresh(plan,material):
    for row in material["states"]:
        rawstate,p = row["raw_state"],row["projection"]
        raw,half = rawstate["energy"],p["values"]
        row["raw_state_digest"] = p["source_state_digest"] = c.digest(rawstate)
        row["raw_values_digest"] = p["source_values_digest"] = c.digest(raw)
        row["raw_values_hex"] = [x.hex() for x in raw]
        row["half_values_hex"] = [x.hex() for x in half]
        row["raw_values_f64le_sha256"] = bytes_digest(raw)
        row["half_values_f64le_sha256"] = bytes_digest(half)
        row["raw_subnormal_band_indices"] = [i for i,x in enumerate(raw) if 0 < x < sys.float_info.min]
        p["subnormal_band_indices"] = [i for i,x in enumerate(half) if 0 < x < sys.float_info.min]
        p["underflow_band_indices"] = [i for i,(x,z) in enumerate(zip(raw,half)) if x > 0 and z == 0]
        reseal(p,"projection_digest")
        reseal(row,"materialized_state_digest")
    reseal(material,"record_digest")
    sha = hashlib.sha256(c.canonical(material)).hexdigest()
    proof = c.sealed(dict(status="S2NT_MATERIALIZATION_VALID",run_id=material["run_id"],read_only=True,
        record_digest=material["record_digest"],file_sha256_before=sha,file_sha256_after=sha,
        materialized_sources=14,half_values_checked=672,verification_calls=1),"verification_digest")
    return plan,material,proof,c.Anchors(plan["execution_digest"],material["record_digest"],proof["verification_digest"])


def fixture():
    sources = [b.bind_source(s,c.digest(f"neutral-source-{s.ordinal}")) for s in b.source_specs()]
    plan = b.execution_plan(sources,{"synthetic":True},{"synthetic":"0"*64},{"synthetic":True})
    profiles = plan["profiles"]
    carriers = [f"neutral-band-{i:02d}" for i in range(48)]
    profile = c.sealed(dict(bound_profiles=profiles,config=profiles["raw"]["config"],carriers=carriers),"profile_digest")
    states = []
    for source in sources:
        n = source["ordinal"]
        # Exact metadata roles do not select source data: this is a declared test table.
        value = (0.125,0.25,0.125,0.125,0.15,0.3,0.35,0.25,0.2,0.275,0.4,0.45,0.5,0.6)[n-1]
        raw,half = [value]*48,[value*0.5]*48
        start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
        rawstate = dict(modality_id="auditory",geometry_id=profiles["raw"]["geometry_id"],snapshot_index=index,
            window_start_sample=start,window_end_sample=end,carrier_ids=carriers,energy=raw,contact="active_energy")
        projection = dict(profile_id=profiles["half"]["profile_id"],profile_digest=profiles["half_profile_digest"],
            geometry_id=profiles["half"]["geometry_id"],source_profile_digest=profiles["raw_profile_digest"],
            snapshot_index=index,window_start_tick=start,window_end_tick=end,clock_id="audio.sample",carrier_ids=carriers,values=half)
        states.append(dict(**{k:source[k] for k in ("source_id","ordinal","source_digest","recipe_digest","pcm_sha256","clock_id")},
            payload_hash_checked_before_analysis=True,raw_state=rawstate,projection=projection))
    counts = dict.fromkeys(("generation_attempts","payloads_validated","analyze_attempts","analyze_returns","nj_attempts","nj_returns","completed_sources"),14)
    counts.update(raw_value_count=672,half_value_count=672)
    counts.update(dict.fromkeys(("rolling_hops","contact_frame_calls","pcm_payloads_persisted","distance_calls","vector_pair_comparisons",
        "order_criteria_evaluated","memory_calls","field_calls","context_calls","runtime_calls"),0))
    material = dict(schema="s2nt.receptor-nj-materialization.v1",run_id="neutral-reduced-values",status="RECEPTOR_NJ_MATERIALIZATION_COMPLETE",
        execution_digest=plan["execution_digest"],failure=None,profile=profile,states=states,counts=counts,
        source_hashes_before={"synthetic":"0"*64},source_hashes_after={"synthetic":"0"*64},main_gate_after=False,source_gate_after=False)
    return refresh(plan,material)


class ComparisonQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = fixture()
        cls.record = c.compare_all(*cls.inputs)
        cls.proof = v.verify_comparison(cls.record,cls.inputs[3])

    def code(self,expected,fn,*args):
        with self.assertRaises(c.S2NTComparisonError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,expected)

    def test_01_complete_binding(self):
        sources = c.bind_inputs(*self.inputs)
        self.assertEqual(len(sources),14)
        self.assertEqual(len(self.record["primary"]),25)
        self.assertEqual(len(self.record["direct"]),25)
        self.assertEqual(self.proof["work"],dict(halvings=672,terms=2400,equalities=2400,sums=50,order_checks=0))

    def test_02_anchor_and_digest(self):
        plan,material,proof,anchors = deepcopy(self.inputs)
        self.code("ANCHOR_BINDING_INVALID",c.bind_inputs,plan,material,proof,c.Anchors("0"*64,anchors.materialization_digest,anchors.verification_digest))
        material["run_id"] = "tampered"
        self.code("DIGEST_INVALID",c.bind_inputs,plan,material,proof,anchors)

    def test_03_source_binding(self):
        plan,material,_,_ = deepcopy(self.inputs)
        material["states"][0]["pcm_sha256"] = "0"*64
        self.code("SOURCE_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))

    def test_04_time_binding(self):
        for key,value in (("snapshot_index",11),("window_start_tick",0.0),("clock_id","foreign")):
            with self.subTest(key=key):
                plan,material,_,_ = deepcopy(self.inputs)
                material["states"][0]["projection"][key] = value
                self.code("TIME_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))

    def test_05_profile_and_domains(self):
        plan,material,_,_ = deepcopy(self.inputs)
        material["states"][0]["projection"]["profile_digest"] = "0"*64
        self.code("PROFILE_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))
        for value in (float("inf"),float("nan"),-0.1,1.01):
            with self.subTest(value=repr(value)):
                self.code("VALUE_DOMAIN_INVALID",c.validate_values,(value,)+(0.0,)*47,True)

    def test_06_pairs_complete_ordered(self):
        for change in ("missing","swap","duplicate"):
            with self.subTest(change=change):
                plan = deepcopy(self.inputs[0])
                if change == "missing":
                    plan["pairs"].pop()
                elif change == "swap":
                    plan["pairs"][0],plan["pairs"][1] = plan["pairs"][1],plan["pairs"][0]
                else:
                    plan["pairs"][1] = deepcopy(plan["pairs"][0])
                self.code("PAIR_BINDING_INVALID",c.validate_pairs,plan)

    def test_07_historical_sum(self):
        values = (1.0,)+(2.0**-53,)*47
        q = c.BoundSource("q","1"*64,values,values)
        r = c.BoundSource("r","2"*64,(0.0,)*48,(0.0,)*48)
        row = c.compare_pair(dict(pair_id="neutral",source_id="q",reference_id="r"),q,r)
        self.assertEqual(row["mean"].hex(),(sum(abs(q.half[i]-r.half[i]) for i in range(48))/48).hex())
        self.assertEqual(row["terms"],[dict(original_index=i,value=x) for i,x in enumerate(values)])

    def test_08_independent_direct(self):
        sources = c.bind_inputs(*self.inputs)
        pair = self.inputs[0]["pairs"][0]
        with patch.object(c,"compare_pair",side_effect=AssertionError("productive helper forbidden")):
            row = v.direct_pair(pair,sources[2],sources[0])
        self.assertEqual(row["terms"],self.record["primary"][0]["terms"])
        self.assertEqual(row["mean"].hex(),self.record["primary"][0]["mean"].hex())

    def test_09_strict_tie_inverted(self):
        for left,right,expected in ((0.1,0.2,"LT"),(0.2,0.2,"EQ"),(0.3,0.2,"GT")):
            with self.subTest(order=expected):
                self.assertEqual(e.strict_order(left,right),expected)
        assessment = e.evaluate(self.record,self.proof,b.evaluation_plan(self.inputs[0]))
        self.assertEqual(len(assessment["order_findings"]),24)
        for row in assessment["order_findings"]:
            self.assertEqual(row["separated"],row["left_distance"] < row["right_distance"])

    def test_10_nominal_variant_not_evidence(self):
        result = e.evaluate(self.record,self.proof,b.evaluation_plan(self.inputs[0]))
        nominal = next(x for x in result["variants"] if x["source_id"] == "nt-a04")
        self.assertTrue(nominal["nominal_variant_without_half_change"])
        self.assertFalse(result["actual_variant_coverage"])
        self.assertFalse(result["bounded_separation_confirmed"])
        self.assertEqual(len(result["exact_controls"]),2)
        self.assertEqual(len(result["variants"]),4)
        self.assertEqual([x["N"] for x in result["groups"]],[8,4,12])
        self.assertEqual([x["right_subtype"] for x in result["subgroups"]],["ADDITION","REPLACEMENT","INDEPENDENT_CONTROL","REFERENCE"])

    def test_11_raw_half_collision_separate(self):
        plan,material,_,_ = deepcopy(self.inputs)
        for index in (0,5):
            material["states"][index]["raw_state"]["energy"] = [0.0]*48
            material["states"][index]["projection"]["values"] = [0.0]*48
        material["states"][0]["raw_state"]["contact"] = "active_zero"
        material["states"][5]["raw_state"]["energy"][47] = float.fromhex("0x0.0000000000001p-1022")
        inputs = refresh(plan,material)
        record = c.compare_all(*inputs)
        proof = v.verify_comparison(record,inputs[3])
        result = e.evaluate(record,proof,b.evaluation_plan(plan))
        collision = next(x for x in result["pair_collisions"] if x["pair_id"] == "d06-01")
        self.assertTrue(collision["half_only_collision"])
        self.assertFalse(collision["raw_equal"])
        self.assertTrue(collision["different_prescribed_whole_assignment"])
        self.assertTrue(result["missing_l1_order_is_not_universal_information_loss"])

    def test_12_equality_tamper(self):
        record = deepcopy(self.record)
        record["primary"][0]["raw_equal"] = False
        reseal(record["primary"][0],"pair_digest")
        self.code("EQUALITY_INVALID",v.verify_comparison,reseal(record,"comparison_digest"),self.inputs[3])

    def test_13_forward_halving(self):
        plan,material,_,_ = deepcopy(self.inputs)
        material["states"][0]["projection"]["values"][0] = 0.2
        inputs = refresh(plan,material)
        record = c.compare_all(*inputs)
        self.code("HALVING_INVALID",v.verify_comparison,record,inputs[3])

    def test_14_term_tamper(self):
        for key,value,expected in (("original_index",47,"TERM_INDEX_INVALID"),("value",0.01,"TERM_VALUE_INVALID")):
            with self.subTest(key=key):
                record = deepcopy(self.record)
                record["primary"][0]["terms"][0][key] = value
                reseal(record["primary"][0],"pair_digest")
                self.code(expected,v.verify_comparison,reseal(record,"comparison_digest"),self.inputs[3])

    def test_15_baseline_tamper_and_evaluation_gate(self):
        record = deepcopy(self.record)
        record["direct"][0]["mean"] = 0.1
        reseal(record["direct"][0],"pair_digest")
        self.code("SUM_ARITHMETIC_INVALID",v.verify_comparison,reseal(record,"comparison_digest"),self.inputs[3])
        proof = deepcopy(self.proof)
        proof["evaluation_allowed"] = False
        self.code("VERIFICATION_REQUIRED",e.evaluate,self.record,reseal(proof,"verification_digest"),b.evaluation_plan(self.inputs[0]))

    def test_16_envelope_and_atomic_limits(self):
        # The complete neutral envelope includes all 14 source receipts and 50 term tables.
        record = deepcopy(self.record)
        hashes = run.watched()
        record.update(run_id="s2nt-diagnostic-comparison-neutral",code_hashes_before=hashes,code_hashes_after=hashes,main_gate_after=False)
        reseal(record,"comparison_digest")
        self.assertLess(len(c.canonical(record)),c.MAX_OUTPUT_BYTES)
        oversized = deepcopy(record)
        oversized["oversized"] = "x"*c.MAX_OUTPUT_BYTES
        self.code("OUTPUT_SIZE_EXCEEDED",v.verify_comparison,reseal(oversized,"comparison_digest"),self.inputs[3])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"result.json"
            run.atomic(path,record,c.MAX_OUTPUT_BYTES)
            self.assertEqual(path.read_bytes(),c.canonical(record))
            self.code("WRITE_CONFLICT",run.atomic,path,record,c.MAX_OUTPUT_BYTES)
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,Path(directory)/"large.json",oversized,c.MAX_OUTPUT_BYTES)

    def test_17_immutability(self):
        before = c.digest(dict(inputs=self.inputs[:3],record=self.record,proof=self.proof))
        inputs = deepcopy(self.inputs)
        record = c.compare_all(*inputs)
        proof = v.verify_comparison(record,inputs[3])
        e.evaluate(record,proof,b.evaluation_plan(inputs[0]))
        self.assertEqual(before,c.digest(dict(inputs=self.inputs[:3],record=self.record,proof=self.proof)))
        self.assertEqual(inputs,self.inputs)
        self.assertEqual(record,self.record)

    def test_18_real_loader_closed(self):
        self.assertIs(run.MAIN_GATE,False)
        self.assertIs(b.MAIN_GATE,False)
        with patch.object(run,"read",side_effect=AssertionError("real reads forbidden")) as reader:
            self.code("MAIN_GATE_CLOSED",run.load_verified_nt)
            reader.assert_not_called()
        self.assertFalse(any(name.startswith("mcm_field_organism") or "_s2nj_private" in name for name in sys.modules))


if __name__ == "__main__":
    unittest.main()
