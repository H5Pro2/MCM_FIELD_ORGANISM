import hashlib, json, math, struct
from pathlib import Path
root=Path.cwd()
base=root/"reports/s2nc/s2nc-source-panel-preseal-20260906-01"
path=root/"reports/s2nc/s2nc-receptor-materialization-20260906-01/result.json"
def canonical(v):
    return json.dumps(v,allow_nan=False,ensure_ascii=True,sort_keys=True,separators=(",",":")).encode("ascii")
def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()
def read(p,key):
    raw=p.read_bytes()
    r=json.loads(raw)
    assert raw==canonical(r)+b"\n",str(p)
    assert r[key]==digest({k:v for k,v in r.items() if k!=key}),str(p)
    return r
before=hashlib.sha256(path.read_bytes()).hexdigest()
r=read(path,"record_digest")
ex=read(base/"execution-plan.json","execution_digest")
seal=read(base/"seal.json","seal_digest")
assert r["schema"]=="s2nc.receptor-materialization.v1"
assert r["run_id"]=="s2nc-receptor-materialization-20260906-01"
assert r["technical_status"]=="RECEPTOR_MATERIALIZATION_COMPLETE" and r["failure"] is None
assert r["execution_digest"]==ex["execution_digest"]==seal["execution_digest"]
assert r["seal_digest"]==seal["seal_digest"]=="ac2ec3e0441fb463c2a1a80d8cb296bbc4934f7555899c5750aa32a0ea56679b"
assert r["python_version"]==seal["python_version"]
assert r["sources_unchanged"] is True
for p,h in r["input_hashes"].items():
    assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
for p,h in seal["source_hashes"].items():
    assert r["input_hashes"][p]==h
assert r["input_hashes"]["reports/s2nc/seal_inventory.py"]==seal["script_sha256"]
profile=r["receptor_profile"]
assert profile["profile_digest"]==digest({k:v for k,v in profile.items() if k!="profile_digest"})
assert profile["config"]==ex["receptor_profile"]==dict(sample_rate=48000,window_size=4800,hop_size=480,min_frequency=50.0,max_frequency=18000.0,band_count=48)
assert profile["method"]=="LogSpectralReceptor.analyze"
assert profile["receptor_source_sha256"]==seal["source_hashes"]["mcm_field_organism/log_spectral_receptor.py"]
assert len(profile["channel_ids"])==len(set(profile["channel_ids"]))==len(profile["bands"])==48
assert profile["channel_ids"]==[b["channel_id"] for b in profile["bands"]]
assert all(math.isfinite(b[k]) for b in profile["bands"] for k in ("lower_frequency","center_frequency","upper_frequency"))
assert all(a["center_frequency"]<b["center_frequency"] for a,b in zip(profile["bands"],profile["bands"][1:]))
assert r["counts"]==dict(analyze_attempt_count=23,analyze_return_count=23,completed_analyses=23,receptor_values=1104,distance_calculations=0,rule_calls=0,memory_calls=0,context_calls=0,field_calls=0,runtime_calls=0,pcm_payloads_persisted=0)
assert len(r["states"])==23
state_keys={"source_id","ordinal","recipe_digest","pcm_sha256","sample_count","clock_id","window_start_sample","window_end_sample","time_semantics","execution_digest","profile_digest","values","values_digest","values_f64le_sha256","materialized_state_digest"}
for n,(s,source) in enumerate(zip(r["states"],ex["sources"],strict=True),1):
    assert set(s)==state_keys
    assert s["ordinal"]==n and s["source_id"]==f"s{n:03d}"
    for k in ("source_id","ordinal","recipe_digest","pcm_sha256","sample_count","clock_id","window_start_sample","window_end_sample"):
        assert s[k]==source[k],(n,k)
    assert s["clock_id"]=="s2nc-source-sample-clock"
    assert (s["window_start_sample"],s["window_end_sample"])==((n-1)*4800,n*4800)
    assert s["time_semantics"]=="DECLARED_PCM_SOURCE_WINDOW_NOT_RECEPTOR_TIMESTAMP"
    assert s["execution_digest"]==ex["execution_digest"] and s["profile_digest"]==profile["profile_digest"]
    values=s["values"]
    assert len(values)==48 and all(type(x) is float and math.isfinite(x) and 0.0<=x<=1.0 for x in values)
    assert s["values_digest"]==digest(values)
    assert s["values_f64le_sha256"]==hashlib.sha256(struct.pack("<48d",*values)).hexdigest()
    assert s["materialized_state_digest"]==digest({k:v for k,v in s.items() if k!="materialized_state_digest"})
assert hashlib.sha256(path.read_bytes()).hexdigest()==before
v={"verification_status":"MATERIALIZATION_EVIDENCE_VALID","run_id":r["run_id"],"record_digest":r["record_digest"],"result_file_sha256":before,"state_count":23,"value_count":1104,"read_only":True,"receptor_repetitions":0,"distance_calculations":0,"source_hashes_unchanged":True,"result_unchanged":True}
v["verification_digest"]=digest(v)
print(json.dumps(v,sort_keys=True))
