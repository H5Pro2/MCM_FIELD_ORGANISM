"""Neutral reduced values only. No NU payloads, materialization files or sensors."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2nu_private_comparison as c
from tools import _s2nu_private_comparison_verification as v
from tools import _s2nu_private_order_evaluation as e
from tools import _s2nu_private_comparison_run as run

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
    proof = c.sealed(dict(status="S2NU_MATERIALIZATION_VALID",run_id=material["run_id"],read_only=True,
        record_digest=material["record_digest"],file_sha256_before=sha,file_sha256_after=sha,
        materialized_sources=30,half_values_checked=1440,verification_calls=1),"verification_digest")
    return plan,material,proof,c.Anchors(plan["execution_digest"],material["record_digest"],proof["verification_digest"])


def fixture(sequences=None):
    sources = [b.bind_source(s,c.digest(f"neutral-source-{s.stream}-{s.window}")) for s in b.specs()]
    plan = b.execution_plan(sources,{"synthetic":True},{"synthetic":"0"*64},{"synthetic":True})
    profiles = plan["profiles"]
    carriers = [f"neutral-band-{i:02d}" for i in range(48)]
    profile = c.sealed(dict(bound_profiles=profiles,config=profiles["raw"]["config"],carriers=carriers,
        bands=[dict(channel_id=x,lower_frequency=123.45678901234567,center_frequency=234.56789012345678,
            upper_frequency=345.67890123456789) for x in carriers],analysis_method="LogSpectralReceptor.analyze",
        projection_method="project_auditory_half_v1",time_semantics="NATIVE_WINDOW_START_DIV_480_NOT_ROLLING_COUNT"),"profile_digest")
    states = []
    for source in sources:
        n = source["ordinal"]
        # Exact metadata roles do not select source data: this is a declared test table.
        table = sequences if sequences is not None else (
            (0.2,0.2,0.2,0.2,0.2),(0.1,0.2,0.3,0.4,0.5),(0.1,0.4,0.2,0.3,0.5),
            (0.1,0.3,0.2,0.4,0.6),(0.1,0.2,0.4,0.2,0.1),(0.1,0.1,0.5,0.6,0.6))
        value = table[(n-1)//5][(n-1)%5]
        raw,half = [value]*48,[value*0.5]*48
        start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
        rawstate = dict(modality_id="auditory",geometry_id=profiles["raw"]["geometry_id"],snapshot_index=index,
            window_start_sample=start,window_end_sample=end,carrier_ids=carriers,energy=raw,contact="active_energy")
        projection = dict(profile_id=profiles["half"]["profile_id"],profile_digest=profiles["half_profile_digest"],
            geometry_id=profiles["half"]["geometry_id"],source_profile_digest=profiles["raw_profile_digest"],
            snapshot_index=index,window_start_tick=start,window_end_tick=end,clock_id="audio.sample",carrier_ids=carriers,values=half)
        states.append(dict(**{k:source[k] for k in ("source_id","ordinal","source_digest","recipe_digest","pcm_sha256","clock_id")},
            payload_hash_checked_before_analysis=True,raw_state=rawstate,projection=projection))
    counts = dict.fromkeys(("generation_attempts","payloads_validated","analyze_attempts","analyze_returns","nj_attempts","nj_returns","completed_sources"),30)
    counts.update(raw_value_count=1440,half_value_count=1440)
    counts.update(dict.fromkeys(("rolling_hops","contact_frame_calls","pcm_payloads_persisted","distance_calls","vector_pair_comparisons",
        "order_criteria_evaluated","memory_calls","field_calls","context_calls","runtime_calls"),0))
    material = dict(schema="s2nu.receptor-nj-materialization.v1",run_id="neutral-reduced-values",status="RECEPTOR_NJ_MATERIALIZATION_COMPLETE",
        execution_digest=plan["execution_digest"],failure=None,profile=profile,states=states,counts=counts,
        source_hashes_before={"synthetic":"0"*64},source_hashes_after={"synthetic":"0"*64},main_gate_after=False,source_gate_after=False,
        seal_digest="0"*64,numpy_loaded=dict(version="neutral",path="neutral",sha256="0"*64),record_values_are_reduced_not_pcm=True)
    return refresh(plan,material)


def view(sequence):
    return c.OrderedView(b.profile_binding()["half_profile_digest"],tuple((float(x),)*48 for x in sequence))


def evaluate_inputs(inputs):
    record = c.compare_all(*inputs)
    proof = v.verify_comparison(record,inputs[3])
    return record,proof,e.evaluate(record,proof,b.evaluation_plan(inputs[0]))


class ComparisonQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for method in ("read_bytes","read_text"):
            original = getattr(Path,method)
            def guarded(path,*args,_original=original,**kwargs):
                if "s2nu-receptor-nj-materialization-" in str(path):
                    raise AssertionError("real NU materialization access forbidden")
                return _original(path,*args,**kwargs)
            guard = patch.object(Path,method,guarded)
            guard.start()
            cls.addClassCleanup(guard.stop)
        guard = patch.object(b,"pcm_window",side_effect=AssertionError("PCM forbidden"))
        guard.start()
        cls.addClassCleanup(guard.stop)
        cls.inputs = fixture()
        cls.record,cls.proof,cls.assessment = evaluate_inputs(cls.inputs)

    def code(self,expected,fn,*args):
        with self.assertRaises(c.S2NUComparisonError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,expected)

    def test_01_complete_full_streams(self):
        self.assertEqual(len(c.bind_inputs(*self.inputs)),30)
        self.assertEqual(len(self.record["primary"]),6)
        self.assertEqual(self.record["primary"],self.record["direct"])
        self.assertEqual(self.proof["work"],dict(halvings=1440,terms=2880,equalities=672,sums=72,order_checks=0))
        self.assertTrue(all(len(r["measurement"]["ordered"]["transitions"]) == 4 for r in self.record["primary"]))

    def test_02_constant(self):
        result = c.ordered_measure(view((0.25,)*5))
        self.assertEqual(result["T"],0.0)
        self.assertTrue(all(x["value"] == 0.0 for r in result["transitions"] for x in r["terms"]))

    def test_03_permutation_same_controls(self):
        controls = self.record["controls"]["primary"]
        self.assertTrue(controls["endpoints_equal"] and controls["multiset_equal"])
        rows = self.record["primary"]
        self.assertLess(rows[1]["measurement"]["ordered"]["T"],rows[2]["measurement"]["ordered"]["T"])

    def test_04_signed_terms_and_historical_sum(self):
        inp = view((0.125,0.25,0.0,0.5,0.25))
        result = c.ordered_measure(inp)
        self.assertEqual([r["terms"][0]["value"] for r in result["transitions"]],[0.125,-0.25,0.5,-0.25])
        for k,row in enumerate(result["transitions"]):
            self.assertEqual(row["step"].hex(),(sum(abs(inp.values[k+1][i]-inp.values[k][i]) for i in range(48))/48).hex())
        self.assertEqual(result["T"].hex(),sum(r["step"] for r in result["transitions"]).hex())

    def test_05_endpoint_boundary(self):
        a,z = view((0.1,0.2,0.3,0.4,0.5)),view((0.1,0.9,0.0,0.8,0.5))
        left = c.EndpointView(a.profile_digest,a.values[0],a.values[4])
        right = c.EndpointView(z.profile_digest,z.values[0],z.values[4])
        self.assertEqual(c.endpoint_measure(left),c.endpoint_measure(right))
        self.assertEqual(set(left.__dataclass_fields__),{"profile_digest","first_values","last_values"})
        self.code("VIEW_TYPE_INVALID",c.endpoint_measure,a)

    def test_06_unordered_metadata_rejected(self):
        inp = view((0.1,0.2,0.2,0.4,0.5))
        payload = dict(profile_digest=inp.profile_digest,values_f64le_sorted=tuple(sorted(struct.pack("<48d",*x) for x in inp.values)))
        valid = c.unordered_from_payload(payload)
        self.assertEqual(set(valid.__dataclass_fields__),set(payload))
        for key in ("source_id","ordinal","window_ordinal","native_windows","snapshot_index","state_digest","clock_id","recipe"):
            with self.subTest(key=key):
                self.code("UNORDERED_METADATA_FORBIDDEN",c.unordered_from_payload,{**payload,key:"leak"})
        self.code("VIEW_TYPE_INVALID",c.unordered_measure,inp)

    def test_07_multiset_multiplicity(self):
        data = struct.pack("<48d",*((0.125,)*48))
        inp = c.UnorderedView(b.profile_binding()["half_profile_digest"],(data,)*5)
        self.assertEqual(c.unordered_measure(inp)["values_f64le_sorted"],[data.hex()]*5)
        self.code("MULTISET_FORM_INVALID",c.UnorderedView,inp.profile_digest,(data,))

    def test_08_primary_conjunction(self):
        self.assertTrue(self.assessment["primary_confirmed"])
        self.assertEqual(self.assessment["order_checks"],5)
        self.assertFalse(self.assessment["learning_binding_proven"])

    def test_09_tie_not_rescued_by_descriptive(self):
        seq = ((0.1,)*5,(0.1,0.2,0.3,0.4,0.5),(0.1,0.2,0.3,0.4,0.5),
            (0.1,0.2,0.3,0.4,0.5),(0.1,0.2,0.3,0.4,0.5),(0.1,0.2,0.3,0.4,0.5))
        _,_,assessment = evaluate_inputs(fixture(seq))
        self.assertEqual(assessment["findings"][0]["order"],"EQ")
        self.assertEqual(assessment["descriptive_passes"],4)
        self.assertFalse(assessment["primary_confirmed"])

    def test_10_inverse_order(self):
        seq = ((0.1,)*5,(0.1,0.4,0.2,0.3,0.5),(0.1,0.2,0.3,0.4,0.5),
            (0.1,)*5,(0.1,)*5,(0.1,)*5)
        _,_,assessment = evaluate_inputs(fixture(seq))
        self.assertEqual(assessment["findings"][0]["order"],"GT")
        self.assertFalse(assessment["primary_confirmed"])

    def test_11_each_control_equality_required(self):
        # Same bag but changed first endpoint; then same endpoints but a changed bag.
        for changed,field in (((0.2,0.4,0.1,0.3,0.5),"endpoints_equal"),((0.1,0.4,0.21,0.3,0.5),"multiset_equal")):
            with self.subTest(field=field):
                seq = ((0.1,)*5,(0.1,0.2,0.3,0.4,0.5),changed,(0.1,)*5,(0.1,)*5,(0.1,)*5)
                _,_,assessment = evaluate_inputs(fixture(seq))
                self.assertTrue(assessment["findings"][0]["strictly_ordered"])
                self.assertFalse(assessment[field])
                self.assertFalse(assessment["primary_confirmed"])

    def test_12_missing_swapped_duplicated_windows(self):
        for change in ("missing","swap","duplicate"):
            with self.subTest(change=change):
                plan,material,_,_ = deepcopy(self.inputs)
                if change == "missing":
                    material["states"].pop()
                elif change == "swap":
                    material["states"][4],material["states"][5] = material["states"][5],material["states"][4]
                else:
                    material["states"][1] = deepcopy(material["states"][0])
                expected = "SOURCE_COUNT_INVALID" if change == "missing" else "SOURCE_BINDING_INVALID"
                self.code(expected,c.bind_inputs,*refresh(plan,material))

    def test_13_time_bindings(self):
        for key,value in (("snapshot_index",11),("window_start_tick",0.0),("clock_id","other")):
            with self.subTest(key=key):
                plan,material,_,_ = deepcopy(self.inputs)
                material["states"][0]["projection"][key] = value
                self.code("TIME_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))

    def test_14_profiles_and_invalid_numeric_inputs(self):
        self.code("VIEW_PROFILE_INVALID",c.OrderedView,"0"*64,view((0.1,)*5).values)
        for value in (float("inf"),float("nan"),-0.1,1.01):
            with self.subTest(value=repr(value)):
                self.code("VALUE_DOMAIN_INVALID",c.validate_values,(value,)+(0.0,)*47,True)
        plan,material,_,_ = deepcopy(self.inputs)
        material["states"][0]["projection"]["profile_digest"] = "0"*64
        self.code("PROFILE_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))

    def test_15_source_and_anchor(self):
        plan,material,proof,a = deepcopy(self.inputs)
        self.code("ANCHOR_BINDING_INVALID",c.bind_inputs,plan,material,proof,c.Anchors("0"*64,a.materialization_digest,a.verification_digest))
        material["states"][0]["pcm_sha256"] = "0"*64
        self.code("SOURCE_BINDING_INVALID",c.bind_inputs,*refresh(plan,material))

    def test_16_output_tamper(self):
        for kind in ("term","metadata","control"):
            with self.subTest(kind=kind):
                record = deepcopy(self.record)
                if kind == "term":
                    record["primary"][0]["measurement"]["ordered"]["transitions"][0]["terms"][0]["value"] = 0.01
                elif kind == "metadata":
                    record["primary"][0]["measurement"]["unordered"]["source_id"] = "leak"
                else:
                    record["controls"]["primary"]["endpoints_equal"] = False
                reseal(record["primary"][0],"stream_digest")
                reseal(record,"comparison_digest")
                self.code("CONTROL_EQUALITY_INVALID" if kind == "control" else "MEASUREMENT_INVALID",v.verify_comparison,record,self.inputs[3])

    def test_17_independent_direct_and_verification(self):
        sources = c.bind_inputs(*self.inputs)[:5]
        views = c.views_for(sources,self.inputs[0]["profiles"]["half_profile_digest"])
        with patch.object(c,"primary_stream",side_effect=AssertionError("primary forbidden")), \
             patch.object(c,"ordered_measure",side_effect=AssertionError("primary forbidden")), \
             patch.object(c,"endpoint_measure",side_effect=AssertionError("primary forbidden")), \
             patch.object(c,"unordered_measure",side_effect=AssertionError("primary forbidden")), \
             patch.object(c,"control_equalities",side_effect=AssertionError("primary forbidden")), \
             patch.object(c,"views_for",side_effect=AssertionError("primary routing forbidden")):
            self.assertEqual(v.direct_stream(*views),self.record["direct"][0]["measurement"])
            self.assertTrue(v.verify_comparison(self.record,self.inputs[3])["baseline_equal"])

    def test_18_complete_artifact_envelope(self):
        # Complete 30-state evidence, not a payload-sized placeholder.
        seq = tuple((0.12345678901234568,0.23456789012345678,0.34567890123456789,
            0.4567890123456789,0.567890123456789)*1 for _ in range(6))
        inputs = fixture(seq)
        record = c.compare_all(*inputs)
        record.pop("comparison_digest")
        record.update(run_id="s2nu-temporal-comparison-20990101-99",code_hashes_before=run.watched(),
            code_hashes_after=run.watched(),main_gate_after=False)
        record = c.sealed(record,"comparison_digest")
        proof = v.verify_comparison(record,inputs[3])
        proof.update(file_sha256_before="0"*64,file_sha256_after="0"*64,verification_calls=1)
        reseal(proof,"verification_digest")
        assessment = e.evaluate(record,proof,b.evaluation_plan(inputs[0]))
        sizes = dict(result_bytes=len(c.canonical(record)),verification_bytes=len(c.canonical(proof)),
            evaluation_bytes=len(c.canonical(assessment)),materialized_states=len(record["inputs"]["materialization"]["states"]))
        self.assertEqual(sizes["materialized_states"],30)
        self.assertLessEqual(sizes["result_bytes"],c.MAX_OUTPUT_BYTES)
        self.assertLessEqual(sizes["verification_bytes"],c.MAX_VERIFICATION_BYTES)
        self.assertLessEqual(sizes["evaluation_bytes"],262144)
        b.publish(run.QUAL_DIR/"neutral-envelope.json",sizes,65536)
        record["oversize"] = "x"*c.MAX_OUTPUT_BYTES
        reseal(record,"comparison_digest")
        self.code("OUTPUT_SIZE_EXCEEDED",v.verify_comparison,record,inputs[3])

    def test_19_closed_gate_atomic_conflict_and_failure(self):
        self.code("MAIN_GATE_CLOSED",run.load_verified_nu)
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2nu-temporal-comparison-20990101-99")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/"neutral.json"
            run.atomic(path,{"ok":True},65536)
            self.code("WRITE_CONFLICT",run.atomic,path,{"ok":False},65536)
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,root/"large.json",{"x":"xx"},1)
            (root/"reports/s2nu").mkdir(parents=True)
            with patch.object(b,"ROOT",root),patch.object(run,"watched",return_value={"neutral":"0"*64}), \
                 patch.object(run,"read",side_effect=c.S2NUComparisonError("NEUTRAL_QUALIFICATION_BINDING_FAILURE")):
                try:
                    run.MAIN_GATE = True
                    out = run.run_main_once("s2nu-temporal-comparison-20990101-99")
                finally:
                    run.MAIN_GATE = False
            proof = run.verify_file_once(out)
            self.assertEqual(proof["status"],"TECHNICAL_FAILURE_RECORDED")
            self.assertFalse(proof["evaluation_allowed"])

    def test_20_verification_required_and_immutability(self):
        record,proof = deepcopy(self.record),deepcopy(self.proof)
        before = c.canonical(record)
        proof["evaluation_allowed"] = False
        reseal(proof,"verification_digest")
        self.code("VERIFICATION_REQUIRED",e.evaluate,record,proof,b.evaluation_plan(self.inputs[0]))
        self.assertEqual(before,c.canonical(record))
        with self.assertRaises(AttributeError):
            view((0.1,)*5).profile_digest = "changed"
        self.assertIs(run.MAIN_GATE,False)
        self.assertIs(b.MAIN_GATE,False)
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_s2nj_private" in n for n in sys.modules))


if __name__ == "__main__":
    unittest.main()
